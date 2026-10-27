"""BTDoor Security+ integration."""

from __future__ import annotations

import asyncio
import logging
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTR_ENTRY_ID as ATTR_ENTRY_ID,
)
from .const import (
    ATTR_INCLUDE_LOGS as ATTR_INCLUDE_LOGS,
)
from .const import (
    ATTR_REASON as ATTR_REASON,
)
from .const import (
    ATTR_SOURCE as ATTR_SOURCE,
)
from .const import (
    ATTR_TEST as ATTR_TEST,
)
from .const import (
    CERTIFICATE_RENEW_BEFORE,
    CONF_CA_CHAIN_PATH,
    CONF_CERTIFICATE_NOT_AFTER,
    CONF_CLIENT_CERT_PATH,
    CONF_CLIENT_KEY_PATH,
    CONF_DEBUG_MODE,
    CONF_DEVELOPER_MODE,
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
    DEFAULT_DEBUG_MODE,
    DEFAULT_DEVELOPER_MODE,
    DEFAULT_DEVICE_NAME,
    DEFAULT_PORT,
    DEFAULT_SERVER,
    DEFAULT_VERIFY_SERVER,
    DOMAIN,
    EVENT_BUS,
    INTEGRATION_VERSION,
    PLATFORMS,
    STORAGE_VERSION,
)
from .const import (
    SERVICE_CLEAN_DEBUG_ENVIRONMENT as SERVICE_CLEAN_DEBUG_ENVIRONMENT,
)
from .const import (
    SERVICE_CLEAR_CALL_JOURNAL as SERVICE_CLEAR_CALL_JOURNAL,
)
from .const import (
    SERVICE_DEVELOPER_TEST as SERVICE_DEVELOPER_TEST,
)
from .const import (
    SERVICE_EXPORT_CALL_JOURNAL as SERVICE_EXPORT_CALL_JOURNAL,
)
from .const import (
    SERVICE_EXPORT_DEBUG_BUNDLE as SERVICE_EXPORT_DEBUG_BUNDLE,
)
from .const import (
    SERVICE_GENERATE_SUPPORT_REPORT as SERVICE_GENERATE_SUPPORT_REPORT,
)
from .const import (
    SERVICE_OPEN_GATE as SERVICE_OPEN_GATE,
)
from .const import (
    SERVICE_REBUILD_CALL_JOURNAL as SERVICE_REBUILD_CALL_JOURNAL,
)
from .const import (
    SERVICE_REJECT_CALL as SERVICE_REJECT_CALL,
)
from .const import (
    SERVICE_RESET_STATISTICS as SERVICE_RESET_STATISTICS,
)
from .const import (
    SERVICE_TEST_CONNECTION as SERVICE_TEST_CONNECTION,
)

if TYPE_CHECKING:
    from .runtime import BTDoorRuntimeData


_LOGGER = logging.getLogger(__name__)

type BticinoConfigEntry = ConfigEntry[Any]


def _log_availability_transition(
    runtime: BTDoorRuntimeData, available: bool, entry_title: str
) -> None:
    """Log an availability transition once per actual state change."""
    previous = runtime.availability_state
    if previous is available:
        return
    runtime.availability_state = available
    if available:
        if previous is False:
            _LOGGER.info("BTDoor Security+ %s recovered and is available again", entry_title)
        return
    _LOGGER.warning("BTDoor Security+ %s became unavailable", entry_title)


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


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up integration-wide services, intents, and Assist sentences."""
    from .sentence_manager import async_install_sentences
    from .services import async_register_services
    from .voice import async_register_voice_intents

    sentence_result = await async_install_sentences(hass)
    _LOGGER.info("Assist sentences synchronized: %s", sentence_result)
    sentence_issue_id = "assist_sentences_restart_required"
    sentences_changed = bool(sentence_result["installed"] or sentence_result["updated"])
    # During a normal Home Assistant startup Conversation can load the files in
    # the same boot, so requesting an additional restart is misleading. Only
    # raise the repair when sentences change while HA is already running (for
    # example after a config-entry reload or a manual integration reload).
    if sentences_changed and hass.state is CoreState.running:
        ir.async_create_issue(
            hass,
            DOMAIN,
            sentence_issue_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="assist_sentences_restart_required",
        )
    else:
        ir.async_delete_issue(hass, DOMAIN, sentence_issue_id)
    async_register_voice_intents(hass)
    await async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: BticinoConfigEntry) -> bool:
    """Set up BTDoor Security+ from a config entry."""
    # Import integration subsystems only when the config entry is set up.
    # Keeping the package import lightweight avoids expensive crypto, SIP,
    # media and diagnostics module imports in Home Assistant's event loop.
    from .call_journal import CallJournal
    from .developer import DeveloperTools
    from .event_bus import (
        RuntimeEvent,
        RuntimeEventBus,
        RuntimeEventType,
        RuntimeSource,
        map_client_event,
    )
    from .managers import async_register_devices
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
    try:
        await _async_renew_certificate_if_needed(hass, entry)
    except BaseException:
        await debug.async_stop()
        raise
    client = _client_from_entry(entry, debug)
    store: Store[dict[str, object]] = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
    client.restore_state(await store.async_load())

    cert_path = await asyncio.to_thread(
        Path(str(entry.data.get(CONF_CLIENT_CERT_PATH, ""))).expanduser
    )
    key_path = await asyncio.to_thread(
        Path(str(entry.data.get(CONF_CLIENT_KEY_PATH, ""))).expanduser
    )
    certificate_files_ready = await asyncio.to_thread(
        lambda: cert_path.is_file() and key_path.is_file()
    )

    if certificate_files_ready:
        ir.async_delete_issue(hass, DOMAIN, f"missing_certificate_{entry.entry_id}")
        try:
            await client.async_start()
        except BticinoSipError as err:
            await client.async_stop()
            await debug.async_stop()
            raise ConfigEntryNotReady(f"Unable to establish BTicino SIP session: {err}") from err
    else:
        ir.async_create_issue(
            hass,
            DOMAIN,
            f"missing_certificate_{entry.entry_id}",
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
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
        client=client,
        store=store,
        debug=debug,
        event_bus=runtime_event_bus,
        call_journal=call_journal,
        language=str(hass.config.language or "en"),
    )
    entry.runtime_data.developer = DeveloperTools(
        hass,
        entry,
        entry.runtime_data,
        bool(entry.options.get(CONF_DEVELOPER_MODE, DEFAULT_DEVELOPER_MODE)),
    )
    entry.runtime_data.api = BTDoorRuntimeAPI(entry, entry.runtime_data)
    _log_availability_transition(entry.runtime_data, client.registered, entry.title)
    try:
        await async_register_devices(hass, entry)
        _async_remove_legacy_gate_entities(hass, entry)
    except BaseException:
        await _async_cleanup_runtime(entry.runtime_data)
        raise

    def _handle_client_event(event_type: str, data: dict[str, object]) -> None:
        debug.record("home_assistant", "event", event_type=event_type, data=data)
        mapped_event = map_client_event(event_type, data)
        runtime_event_bus.publish(mapped_event)
        if mapped_event.event_type is RuntimeEventType.SIP_REGISTERED:
            _log_availability_transition(entry.runtime_data, True, entry.title)
        elif mapped_event.event_type is RuntimeEventType.SIP_UNREGISTERED:
            _log_availability_transition(entry.runtime_data, False, entry.title)
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
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except BaseException:
        await _async_cleanup_runtime(entry.runtime_data)
        raise

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


def _async_remove_legacy_gate_entities(hass: HomeAssistant, entry: BticinoConfigEntry) -> None:
    """Remove retired gate entities from the entity registry."""
    if not entry.unique_id:
        return
    registry = er.async_get(hass)
    legacy = (
        ("switch", f"{entry.unique_id}_open_gate_switch"),
        ("cover", f"{entry.unique_id}_gate_cover"),
    )
    for platform, unique_id in legacy:
        entity_id = registry.async_get_entity_id(platform, DOMAIN, unique_id)
        if entity_id is not None:
            registry.async_remove(entity_id)
            _LOGGER.info("Removed retired BTDoor gate entity: %s", entity_id)


async def _async_cleanup_runtime(runtime: BTDoorRuntimeData) -> None:
    """Release resources allocated during setup or normal unload."""
    if runtime.renewal_unsub is not None:
        runtime.renewal_unsub()
        runtime.renewal_unsub = None
    if runtime.event_unsub is not None:
        runtime.event_unsub()
        runtime.event_unsub = None
    await runtime.client.async_stop()
    if runtime.debug is not None:
        await runtime.debug.async_stop()


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
        await entry.runtime_data.store.async_save(entry.runtime_data.client.export_state())
        await _async_cleanup_runtime(entry.runtime_data)
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
    return Path(hass.config.path("custom_components", DOMAIN, "certificate", str(gateway_id)))


def _copy_certificate_material(source_dir: Path, destination_dir: Path) -> dict[str, str]:
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
    current_cert = await asyncio.to_thread(
        Path(str(data.get(CONF_CLIENT_CERT_PATH, ""))).expanduser
    )
    current_key = await asyncio.to_thread(Path(str(data.get(CONF_CLIENT_KEY_PATH, ""))).expanduser)
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
                await asyncio.to_thread(_copy_certificate_material, source_dir, destination)
            )
        if CONF_CLIENT_CERT_PATH in updates and CONF_CLIENT_KEY_PATH in updates:
            break
    if updates:
        data.update(updates)
        hass.config_entries.async_update_entry(entry, data=data)
        _LOGGER.info("Migrated BTicino certificate material to %s", destination)


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

    expiry = await asyncio.to_thread(certificate_expiry, data.get(CONF_CLIENT_CERT_PATH, ""))
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
        cert_path = await asyncio.to_thread(
            Path(str(data.get(CONF_CLIENT_CERT_PATH, ""))).expanduser
        )
        key_path = await asyncio.to_thread(Path(str(data.get(CONF_CLIENT_KEY_PATH, ""))).expanduser)
        if await asyncio.to_thread(lambda: cert_path.is_file() and key_path.is_file()):
            _LOGGER.warning(
                "Unable to check or renew the BTicino certificate because the "
                "cloud connection was interrupted. Continuing with the existing "
                "certificate: %s",
                err,
            )
            return False
        raise ConfigEntryNotReady(f"Unable to provision BTicino certificate: {err}") from err
    except BticinoCloudError as err:
        cert_path = await asyncio.to_thread(
            Path(str(data.get(CONF_CLIENT_CERT_PATH, ""))).expanduser
        )
        key_path = await asyncio.to_thread(Path(str(data.get(CONF_CLIENT_KEY_PATH, ""))).expanduser)
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
        hass.config_entries.async_update_entry(entry, data=data, version=2, minor_version=0)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload after an entry update."""
    await hass.config_entries.async_reload(entry.entry_id)
