"""BTDoor Security+ integration."""

from __future__ import annotations

import asyncio

from datetime import UTC, datetime, timedelta
import logging
from pathlib import Path
import shutil
import json
from typing import TYPE_CHECKING, Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.storage import Store
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    ATTR_ENTRY_ID,
    CERTIFICATE_RENEW_BEFORE,
    CONF_CA_CHAIN_PATH,
    CONF_CERTIFICATE_NOT_AFTER,
    CONF_CLIENT_CERT_PATH,
    CONF_CLIENT_KEY_PATH,
    CONF_DEVICE_NAME,
    CONF_EMAIL,
    CONF_GATEWAY_ID,
    CONF_GATEWAY_NAME,
    CONF_ID_DEVICE,
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_PLANT_NAME,
    CONF_PORT,
    CONF_SERVER,
    CONF_SIP_ACCOUNT,
    CONF_SIP_PASSWORD,
    CONF_VERIFY_SERVER,
    CONF_DEBUG_MODE,
    CONF_DEVELOPER_MODE,
    DEFAULT_DEBUG_MODE,
    DEFAULT_DEVELOPER_MODE,
    DEFAULT_DEVICE_NAME,
    DEFAULT_PORT,
    DEFAULT_SERVER,
    DEFAULT_VERIFY_SERVER,
    DOMAIN,
    INTEGRATION_VERSION,
    EVENT_BUS,
    PLATFORMS,
    SERVICE_OPEN_GATE,
    SERVICE_RESET_STATISTICS,
    SERVICE_TEST_CONNECTION,
    SERVICE_REJECT_CALL,
    SERVICE_DEVELOPER_TEST,
    SERVICE_GENERATE_SUPPORT_REPORT,
    SERVICE_CLEAN_DEBUG_ENVIRONMENT,
    SERVICE_EXPORT_DEBUG_BUNDLE,
    SERVICE_CLEAR_CALL_JOURNAL,
    SERVICE_EXPORT_CALL_JOURNAL,
    SERVICE_REBUILD_CALL_JOURNAL,
    ATTR_TEST,
    ATTR_INCLUDE_LOGS,
    STORAGE_VERSION,
)
if TYPE_CHECKING:
    from .runtime import BTDoorRuntimeData
    from .sip_client import BticinoSipClient


_LOGGER = logging.getLogger(__name__)

type BticinoConfigEntry = ConfigEntry[Any]

SERVICE_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTRY_ID): cv.string})

DEVELOPER_TEST_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTRY_ID): cv.string,
    vol.Optional(ATTR_TEST, default="all"): vol.In(["all", "cloud", "tls", "sip", "certificates", "sdp", "dialog"]),
})
SUPPORT_REPORT_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTRY_ID): cv.string,
    vol.Optional(ATTR_INCLUDE_LOGS, default=True): cv.boolean,
})


def _client_from_entry(entry: ConfigEntry, debug=None):
    from .sip_client import BticinoSipClient

    data = entry.data
    return BticinoSipClient(
        sip_account=data[CONF_SIP_ACCOUNT],
        sip_password=data[CONF_SIP_PASSWORD],
        gateway_id=data[CONF_GATEWAY_ID],
        client_cert_path=data[CONF_CLIENT_CERT_PATH],
        client_key_path=data[CONF_CLIENT_KEY_PATH],
        server=data.get(CONF_SERVER, DEFAULT_SERVER),
        port=data.get(CONF_PORT, DEFAULT_PORT),
        verify_server=data.get(CONF_VERIFY_SERVER, DEFAULT_VERIFY_SERVER),
        debug_recorder=debug,
    )



def _service_entries(hass: HomeAssistant, call: ServiceCall):
    requested_entry = call.data.get(ATTR_ENTRY_ID)
    entries = hass.config_entries.async_entries(DOMAIN)
    if requested_entry:
        entries = [item for item in entries if item.entry_id == requested_entry]
    if not entries:
        raise HomeAssistantError("No matching BTDoor Security+ configuration")
    return entries

async def async_setup_entry(hass: HomeAssistant, entry: BticinoConfigEntry) -> bool:
    """Set up BTDoor Security+ from a config entry."""
    # Import integration subsystems only when the config entry is set up.
    # Keeping the package import lightweight avoids expensive crypto, SIP,
    # media and diagnostics module imports in Home Assistant's event loop.
    from .call_journal import CallJournal
    from .cloud import BticinoCloudAuthenticationError, BticinoCloudConnectionError, BticinoCloudError
    from .developer import DeveloperModeDisabledError, DeveloperTools
    from .device_model import async_register_devices
    from .event_bus import RuntimeEvent, RuntimeEventBus, RuntimeEventType, RuntimeSource, map_client_event
    from .runtime import BTDoorRuntimeData
    from .runtime_state import BTDoorRuntimeAPI
    from .sip_client import BticinoSipError
    from .support_debug import SupportDebugRecorder

    if entry.title != "Bticino DS+ Suite":
        hass.config_entries.async_update_entry(entry, title="Bticino DS+ Suite")

    await _async_migrate_certificate_storage(hass, entry)
    await _async_migrate_debug_storage(hass, entry)
    debug = SupportDebugRecorder(
        Path(hass.config.path("custom_components", DOMAIN, "logs", entry.entry_id)),
        str(entry.options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE)),
    )
    await debug.async_start()
    debug.record("integration", "setup_entry", version=INTEGRATION_VERSION, entry_title=entry.title)
    await _async_renew_certificate_if_needed(hass, entry)
    client = _client_from_entry(entry, debug)
    store: Store[dict[str, object]] = Store(
        hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}"
    )
    client.restore_state(await store.async_load())

    cert_path = Path(str(entry.data.get(CONF_CLIENT_CERT_PATH, ""))).expanduser()
    key_path = Path(str(entry.data.get(CONF_CLIENT_KEY_PATH, ""))).expanduser()
    certificate_files_ready = await asyncio.to_thread(
        lambda: cert_path.is_file() and key_path.is_file()
    )

    if certificate_files_ready:
        ir.async_delete_issue(hass, DOMAIN, f"missing_certificate_{entry.entry_id}")
        try:
            await client.async_start()
        except BticinoSipError as err:
            raise ConfigEntryNotReady(
                f"Unable to establish BTicino SIP session: {err}"
            ) from err
    else:
        ir.async_create_issue(
            hass, DOMAIN, f"missing_certificate_{entry.entry_id}",
            is_fixable=False, severity=ir.IssueSeverity.WARNING,
            translation_key="missing_certificate",
            translation_placeholders={"entry_title": entry.title},
        )
        # Legacy/manual entries can exist before milestone 2 provisioning.
        # Load the entry without retry noise so the user can open Reconfigure
        # and complete the first cloud-based setup. Entities remain unavailable
        # until certificate provisioning has completed.
        _LOGGER.warning(
            "BTicino SIP certificate or private key is missing for %s. "
            "The integration will remain unregistered until Reconfigure is "
            "completed with valid MyHomeWeb credentials. Certificate: %s; key: %s",
            entry.title,
            cert_path,
            key_path,
        )

    event_store: Store[dict[str, object]] = Store(
        hass, 1, f"{DOMAIN}.{entry.entry_id}.runtime_events"
    )
    runtime_event_bus = RuntimeEventBus(event_store)
    await runtime_event_bus.async_load()
    journal_store: Store[dict[str, object]] = Store(
        hass, 1, f"{DOMAIN}.{entry.entry_id}.call_journal"
    )
    call_journal = CallJournal(journal_store)
    await call_journal.async_load()
    call_journal.attach(runtime_event_bus)

    entry.runtime_data = BTDoorRuntimeData(
        client=client, store=store, debug=debug, event_bus=runtime_event_bus,
        call_journal=call_journal,
        language=str(hass.config.language or "en"),
    )
    entry.runtime_data.developer = DeveloperTools(
        hass, entry, entry.runtime_data,
        bool(entry.options.get(CONF_DEVELOPER_MODE, DEFAULT_DEVELOPER_MODE)),
    )
    entry.runtime_data.api = BTDoorRuntimeAPI(entry, entry.runtime_data)
    await async_register_devices(hass, entry)

    def _handle_client_event(event_type: str, data: dict[str, object]) -> None:
        debug.record("home_assistant", "event", event_type=event_type, data=data)
        runtime_event_bus.publish(map_client_event(event_type, data))
        if event_type == "gate_opened":
            entry.runtime_data.last_open = datetime.now(UTC)
        entry.runtime_data.last_result = str(data.get("status", event_type))
        entry.runtime_data.store.async_delay_save(client.export_state, 1.0)
        hass.bus.async_fire(
            EVENT_BUS,
            {
                "entry_id": entry.entry_id,
                "gateway_id": str(entry.data.get(CONF_GATEWAY_ID, "")),
                "device_name": str(entry.data.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME)),
                "event_type": event_type,
                **data,
            },
        )

    entry.runtime_data.event_unsub = client.add_listener(_handle_client_event)
    runtime_event_bus.publish(
        RuntimeEvent(
            event_type=RuntimeEventType.INTEGRATION_STARTED,
            source=RuntimeSource.INTEGRATION,
            payload={"entry_id": entry.entry_id, "version": INTEGRATION_VERSION},
        )
    )
    # The initial REGISTER can complete before Home Assistant listeners are
    # attached. Publish a state-synchronization event so the event history
    # always reflects the live SIP and Cloud state immediately after setup.
    if client.registered:
        runtime_event_bus.publish(
            RuntimeEvent(
                event_type=RuntimeEventType.SIP_REGISTERED,
                source=RuntimeSource.SIP,
                payload={
                    "entry_id": entry.entry_id,
                    "status": client.last_status,
                    "server": client.server,
                    "port": client.port,
                    "synchronized": True,
                },
            )
        )
    runtime_event_bus.publish(
        RuntimeEvent(
            event_type=RuntimeEventType.CLOUD_CONNECTED,
            source=RuntimeSource.CLOUD,
            payload={
                "entry_id": entry.entry_id,
                "authenticated": True,
                "gateway_id": str(entry.data.get(CONF_GATEWAY_ID, "")),
                "synchronized": True,
            },
        )
    )

    async def _scheduled_renewal(_now: datetime) -> None:
        if await _async_renew_certificate_if_needed(hass, entry):
            await hass.config_entries.async_reload(entry.entry_id)

    entry.runtime_data.renewal_unsub = async_track_time_interval(
        hass, _scheduled_renewal, timedelta(days=1)
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_open_gate(call: ServiceCall) -> None:
        requested_entry = call.data.get(ATTR_ENTRY_ID)
        entries = hass.config_entries.async_entries(DOMAIN)
        if requested_entry:
            entries = [item for item in entries if item.entry_id == requested_entry]
        if not entries:
            raise HomeAssistantError("No matching BTDoor Security+ configuration")

        for config_entry in entries:
            runtime = config_entry.runtime_data
            try:
                result = await runtime.client.async_open_gate()
            except BticinoSipError as err:
                runtime.last_result = str(err)
                raise HomeAssistantError(
                    f"BTicino gate opening failed: {err}"
                ) from err
            runtime.last_open = datetime.now(UTC)
            runtime.last_result = result.status

    async def handle_reset_statistics(call: ServiceCall) -> None:
        requested_entry = call.data.get(ATTR_ENTRY_ID)
        entries = hass.config_entries.async_entries(DOMAIN)
        if requested_entry:
            entries = [item for item in entries if item.entry_id == requested_entry]
        if not entries:
            raise HomeAssistantError("No matching BTDoor Security+ configuration")
        for config_entry in entries:
            config_entry.runtime_data.client.reset_statistics()
            await config_entry.runtime_data.store.async_save(
                config_entry.runtime_data.client.export_state()
            )


    async def handle_test_connection(call: ServiceCall) -> None:
        requested_entry = call.data.get(ATTR_ENTRY_ID)
        entries = hass.config_entries.async_entries(DOMAIN)
        if requested_entry:
            entries = [item for item in entries if item.entry_id == requested_entry]
        if not entries:
            raise HomeAssistantError("No matching BTDoor Security+ configuration")
        for config_entry in entries:
            runtime = config_entry.runtime_data
            started = asyncio.get_running_loop().time()
            try:
                result = await runtime.client.async_test_connection()
            except BticinoSipError as err:
                runtime.last_result = str(err)
                runtime.client._notify("connection_test_failed", error=str(err))
                raise HomeAssistantError(f"BTicino SIP connection test failed: {err}") from err
            duration = max(0.0, asyncio.get_running_loop().time() - started)
            runtime.last_result = result.status
            runtime.client._notify(
                "connection_test_succeeded",
                status=result.status,
                code=result.code,
                duration_seconds=duration,
            )


    async def handle_reject_call(call: ServiceCall) -> None:
        requested_entry = call.data.get(ATTR_ENTRY_ID)
        entries = hass.config_entries.async_entries(DOMAIN)
        if requested_entry:
            entries = [item for item in entries if item.entry_id == requested_entry]
        if not entries:
            raise HomeAssistantError("No matching BTDoor Security+ configuration")
        for config_entry in entries:
            try:
                await config_entry.runtime_data.client.async_reject_call()
            except BticinoSipError as err:
                raise HomeAssistantError(f"BTicino call rejection failed: {err}") from err

    async def handle_developer_test(call: ServiceCall):
        entries = _service_entries(hass, call)
        output = {}
        for config_entry in entries:
            try:
                output[config_entry.entry_id] = await config_entry.runtime_data.developer.async_run_tests(str(call.data.get(ATTR_TEST, "all")))
            except DeveloperModeDisabledError as err:
                raise HomeAssistantError(str(err)) from err
        return output

    async def handle_generate_support_report(call: ServiceCall):
        entries = _service_entries(hass, call)
        output = {}
        for config_entry in entries:
            try:
                output[config_entry.entry_id] = await config_entry.runtime_data.developer.async_generate_support_report(bool(call.data.get(ATTR_INCLUDE_LOGS, True)))
            except DeveloperModeDisabledError as err:
                raise HomeAssistantError(str(err)) from err
        return output

    async def handle_clear_call_journal(call: ServiceCall):
        output = {}
        for config_entry in _service_entries(hass, call):
            await config_entry.runtime_data.call_journal.async_clear()
            output[config_entry.entry_id] = {"cleared": True}
        return output

    async def handle_export_call_journal(call: ServiceCall):
        output = {}
        export_dir = Path(hass.config.path("www", DOMAIN))
        await hass.async_add_executor_job(export_dir.mkdir, parents=True, exist_ok=True)
        for config_entry in _service_entries(hass, call):
            path = export_dir / f"call-journal-{config_entry.entry_id}.json"
            payload = json.dumps(config_entry.runtime_data.call_journal.export_state(), indent=2, ensure_ascii=False)
            await hass.async_add_executor_job(path.write_text, payload, "utf-8")
            output[config_entry.entry_id] = {"path": str(path), "url": f"/local/{DOMAIN}/{path.name}"}
        return output

    async def handle_rebuild_call_journal(call: ServiceCall):
        output = {}
        for config_entry in _service_entries(hass, call):
            events = [RuntimeEvent.from_dict(item) for item in config_entry.runtime_data.event_bus.history]
            await config_entry.runtime_data.call_journal.async_rebuild(events)
            output[config_entry.entry_id] = config_entry.runtime_data.call_journal.metrics
        return output

    if not hass.services.has_service(DOMAIN, SERVICE_OPEN_GATE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_OPEN_GATE,
            handle_open_gate,
            schema=SERVICE_SCHEMA,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_RESET_STATISTICS):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RESET_STATISTICS,
            handle_reset_statistics,
            schema=SERVICE_SCHEMA,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_TEST_CONNECTION):
        hass.services.async_register(
            DOMAIN,
            SERVICE_TEST_CONNECTION,
            handle_test_connection,
            schema=SERVICE_SCHEMA,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_REJECT_CALL):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REJECT_CALL,
            handle_reject_call,
            schema=SERVICE_SCHEMA,
        )

    async def handle_clean_debug_environment(call: ServiceCall):
        output = {}
        for config_entry in _service_entries(hass, call):
            developer = config_entry.runtime_data.developer
            if developer is None:
                raise HomeAssistantError("Developer tools are unavailable")
            output[config_entry.entry_id] = await developer.async_clean_debug_environment()
        return output

    if not hass.services.has_service(DOMAIN, SERVICE_DEVELOPER_TEST):
        hass.services.async_register(DOMAIN, SERVICE_DEVELOPER_TEST, handle_developer_test, schema=DEVELOPER_TEST_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
    if not hass.services.has_service(DOMAIN, SERVICE_GENERATE_SUPPORT_REPORT):
        hass.services.async_register(DOMAIN, SERVICE_GENERATE_SUPPORT_REPORT, handle_generate_support_report, schema=SUPPORT_REPORT_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
    if not hass.services.has_service(DOMAIN, SERVICE_EXPORT_DEBUG_BUNDLE):
        hass.services.async_register(DOMAIN, SERVICE_EXPORT_DEBUG_BUNDLE, handle_generate_support_report, schema=SUPPORT_REPORT_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
    if not hass.services.has_service(DOMAIN, SERVICE_CLEAN_DEBUG_ENVIRONMENT):
        hass.services.async_register(DOMAIN, SERVICE_CLEAN_DEBUG_ENVIRONMENT, handle_clean_debug_environment, schema=SERVICE_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
    if not hass.services.has_service(DOMAIN, SERVICE_CLEAR_CALL_JOURNAL):
        hass.services.async_register(DOMAIN, SERVICE_CLEAR_CALL_JOURNAL, handle_clear_call_journal, schema=SERVICE_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
    if not hass.services.has_service(DOMAIN, SERVICE_EXPORT_CALL_JOURNAL):
        hass.services.async_register(DOMAIN, SERVICE_EXPORT_CALL_JOURNAL, handle_export_call_journal, schema=SERVICE_SCHEMA, supports_response=SupportsResponse.OPTIONAL)
    if not hass.services.has_service(DOMAIN, SERVICE_REBUILD_CALL_JOURNAL):
        hass.services.async_register(DOMAIN, SERVICE_REBUILD_CALL_JOURNAL, handle_rebuild_call_journal, schema=SERVICE_SCHEMA, supports_response=SupportsResponse.OPTIONAL)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BticinoConfigEntry) -> bool:
    """Unload a config entry."""
    from .event_bus import RuntimeEvent, RuntimeEventType, RuntimeSource

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        if entry.runtime_data.event_bus is not None:
            entry.runtime_data.event_bus.publish(
                RuntimeEvent(
                    event_type=RuntimeEventType.INTEGRATION_STOPPED,
                    source=RuntimeSource.INTEGRATION,
                    payload={"entry_id": entry.entry_id},
                )
            )
        if entry.runtime_data.renewal_unsub is not None:
            entry.runtime_data.renewal_unsub()
        if entry.runtime_data.event_unsub is not None:
            entry.runtime_data.event_unsub()
        await entry.runtime_data.store.async_save(
            entry.runtime_data.client.export_state()
        )
        await entry.runtime_data.client.async_stop()
        if entry.runtime_data.debug is not None:
            await entry.runtime_data.debug.async_stop()
    if unloaded and len(hass.config_entries.async_entries(DOMAIN)) <= 1:
        hass.services.async_remove(DOMAIN, SERVICE_OPEN_GATE)
        hass.services.async_remove(DOMAIN, SERVICE_RESET_STATISTICS)
        hass.services.async_remove(DOMAIN, SERVICE_TEST_CONNECTION)
        hass.services.async_remove(DOMAIN, SERVICE_REJECT_CALL)
        hass.services.async_remove(DOMAIN, SERVICE_DEVELOPER_TEST)
        hass.services.async_remove(DOMAIN, SERVICE_GENERATE_SUPPORT_REPORT)
        hass.services.async_remove(DOMAIN, SERVICE_EXPORT_DEBUG_BUNDLE)
        hass.services.async_remove(DOMAIN, SERVICE_CLEAN_DEBUG_ENVIRONMENT)
    return unloaded


async def _async_migrate_debug_storage(hass: HomeAssistant, entry: BticinoConfigEntry) -> None:
    """Move legacy logs and support reports inside the integration folder."""
    destination_root = Path(hass.config.path("custom_components", DOMAIN))
    legacy_root = Path(hass.config.path(DOMAIN))

    def _migrate() -> None:
        for folder in ("logs", "support"):
            source = legacy_root / folder / entry.entry_id
            destination = destination_root / folder / entry.entry_id
            destination.mkdir(parents=True, exist_ok=True)
            if not source.exists():
                continue
            for item in source.iterdir():
                target = destination / item.name
                if target.exists():
                    continue
                if item.is_dir():
                    shutil.copytree(item, target)
                else:
                    shutil.copy2(item, target)

    await asyncio.to_thread(_migrate)


def _certificate_storage_dir(hass: HomeAssistant, gateway_id: str) -> Path:
    """Return the requested certificate directory inside the integration."""
    return Path(
        hass.config.path("custom_components", DOMAIN, "certificate", str(gateway_id))
    )


def _copy_certificate_material(
    source_dir: Path, destination_dir: Path
) -> dict[str, str]:
    """Copy existing certificate material to the integration certificate folder."""
    destination_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, str] = {}
    names = {
        "client-cert.pem": CONF_CLIENT_CERT_PATH,
        "client-key.pem": CONF_CLIENT_KEY_PATH,
        "ca-chain.pem": CONF_CA_CHAIN_PATH,
    }
    for filename, config_key in names.items():
        source = source_dir / filename
        destination = destination_dir / filename
        if source.is_file() and source.resolve() != destination.resolve():
            shutil.copy2(source, destination)
        if destination.is_file():
            if filename == "client-key.pem":
                destination.chmod(0o600)
            result[config_key] = str(destination)
    fullchain = source_dir / "client-fullchain.pem"
    if fullchain.is_file():
        target = destination_dir / fullchain.name
        if fullchain.resolve() != target.resolve():
            shutil.copy2(fullchain, target)
    return result


async def _async_migrate_certificate_storage(
    hass: HomeAssistant, entry: BticinoConfigEntry
) -> None:
    """Move legacy certificate files into custom_components/.../certificate."""
    data = dict(entry.data)
    gateway_id = str(data.get(CONF_GATEWAY_ID, ""))
    if not gateway_id:
        return
    destination = _certificate_storage_dir(hass, gateway_id)
    current_cert = Path(str(data.get(CONF_CLIENT_CERT_PATH, ""))).expanduser()
    current_key = Path(str(data.get(CONF_CLIENT_KEY_PATH, ""))).expanduser()
    already_migrated = await asyncio.to_thread(
        lambda: (
            current_cert.parent == destination
            and current_key.parent == destination
            and current_cert.is_file()
            and current_key.is_file()
        )
    )
    if already_migrated:
        return
    source_dirs = []
    for item in (current_cert, current_key):
        if str(item) and item.parent not in source_dirs:
            source_dirs.append(item.parent)
    source_dirs.append(Path(hass.config.path("btdoor_security_plus", gateway_id)))
    # One-time migration sources from all former domains.  The alpha.20 domain
    # rename moved the integration package but existing certificate material
    # may still live below the previous custom-component directory.
    source_dirs.extend(
        [
            Path(hass.config.path("btdoor_entry_plus", gateway_id)),
            Path(
                hass.config.path(
                    "custom_components", "btdoor_entry_plus", "certificate", gateway_id
                )
            ),
            Path(hass.config.path("bticino_door_entry", gateway_id)),
            Path(
                hass.config.path(
                    "custom_components", "bticino_door_entry", "certificate", gateway_id
                )
            ),
        ]
    )
    updates: dict[str, str] = {}
    for source_dir in source_dirs:
        if await asyncio.to_thread(source_dir.is_dir):
            updates.update(
                await asyncio.to_thread(
                    _copy_certificate_material, source_dir, destination
                )
            )
        if CONF_CLIENT_CERT_PATH in updates and CONF_CLIENT_KEY_PATH in updates:
            break
    if updates:
        data.update(updates)
        hass.config_entries.async_update_entry(entry, data=data)
        _LOGGER.info(
            "Migrated BTicino certificate material to %s", destination
        )


async def _async_renew_certificate_if_needed(
    hass: HomeAssistant, entry: BticinoConfigEntry
) -> bool:
    """Renew the client certificate when missing or near expiry."""
    from .cloud import (
        BticinoCloudAuthenticationError,
        BticinoCloudClient,
        BticinoCloudConnectionError,
        BticinoCloudError,
        PlantGateway,
        certificate_expiry,
    )

    data = dict(entry.data)
    email = data.get(CONF_EMAIL)
    password = data.get(CONF_PASSWORD)
    if not email or not password:
        return False

    expiry = await asyncio.to_thread(
        certificate_expiry, data.get(CONF_CLIENT_CERT_PATH, "")
    )
    now = datetime.now(UTC)
    if expiry is not None and expiry - now > CERTIFICATE_RENEW_BEFORE:
        return False
    if expiry is not None:
        hass.bus.async_fire(
            EVENT_BUS,
            {
                "entry_id": entry.entry_id,
                "gateway_id": str(data.get(CONF_GATEWAY_ID, "")),
                "event_type": "certificate_expiring",
                "certificate_not_after": expiry.isoformat(),
                "days_remaining": max(0, (expiry - now).days),
            },
        )

    selection = PlantGateway(
        plant_id=str(data.get(CONF_PLANT_ID, "")),
        plant_name=str(data.get(CONF_PLANT_NAME, "")),
        gateway_id=str(data[CONF_GATEWAY_ID]),
        gateway_name=str(data.get(CONF_GATEWAY_NAME, "")),
    )
    storage_dir = hass.config.path("custom_components", DOMAIN, "certificate", selection.gateway_id)
    cloud = BticinoCloudClient(
        async_get_clientsession(hass),
        email=str(email),
        password=str(password),
    )
    try:
        await cloud.async_login()
        provisioned = await cloud.async_provision(
            selection=selection,
            device_name=str(data.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME)),
            id_device=str(data.get(CONF_ID_DEVICE, "")),
            storage_dir=Path(storage_dir),
        )
    except BticinoCloudAuthenticationError as err:
        raise ConfigEntryAuthFailed("BTicino cloud credentials rejected") from err
    except BticinoCloudConnectionError as err:
        cert_path = Path(str(data.get(CONF_CLIENT_CERT_PATH, ""))).expanduser()
        key_path = Path(str(data.get(CONF_CLIENT_KEY_PATH, ""))).expanduser()
        if await asyncio.to_thread(lambda: cert_path.is_file() and key_path.is_file()):
            _LOGGER.warning(
                "Unable to check or renew the BTicino certificate because the "
                "cloud connection was interrupted. Continuing with the existing "
                "certificate: %s",
                err,
            )
            return False
        raise ConfigEntryNotReady(
            f"Unable to provision BTicino certificate: {err}"
        ) from err
    except BticinoCloudError as err:
        cert_path = Path(str(data.get(CONF_CLIENT_CERT_PATH, ""))).expanduser()
        key_path = Path(str(data.get(CONF_CLIENT_KEY_PATH, ""))).expanduser()
        if await asyncio.to_thread(lambda: cert_path.is_file() and key_path.is_file()):
            _LOGGER.warning(
                "Unable to renew the BTicino certificate. Continuing with the "
                "existing certificate: %s",
                err,
            )
            return False
        raise ConfigEntryNotReady(f"Unable to renew BTicino certificate: {err}") from err

    data.update(
        {
            CONF_SIP_ACCOUNT: provisioned.sip_account,
            CONF_SIP_PASSWORD: provisioned.sip_password,
            CONF_CLIENT_CERT_PATH: provisioned.client_cert_path,
            CONF_CLIENT_KEY_PATH: provisioned.client_key_path,
            CONF_CERTIFICATE_NOT_AFTER: provisioned.certificate_not_after,
            CONF_ID_DEVICE: provisioned.id_device,
        }
    )
    hass.config_entries.async_update_entry(entry, data=data)
    hass.bus.async_fire(
        EVENT_BUS,
        {
            "entry_id": entry.entry_id,
            "gateway_id": str(data.get(CONF_GATEWAY_ID, "")),
            "event_type": "certificate_renewed",
            "certificate_not_after": provisioned.certificate_not_after,
        },
    )
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate alpha v1 manual entries to the v2 schema."""
    if entry.version == 1:
        data = dict(entry.data)
        data.setdefault(CONF_DEVICE_NAME, entry.title or DEFAULT_DEVICE_NAME)
        hass.config_entries.async_update_entry(
            entry, data=data, version=2, minor_version=0
        )
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload after an entry update."""
    await hass.config_entries.async_reload(entry.entry_id)
