"""Global services for BTDoor Security+."""
from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from time import monotonic

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv, entity_registry as er

from .const import (
    ATTR_ENTRY_ID, ATTR_INCLUDE_LOGS, ATTR_REASON, ATTR_SOURCE, ATTR_TEST,
    CONF_GATEWAY_ID, DOMAIN, EVENT_BUS,
    SERVICE_CLEAN_DEBUG_ENVIRONMENT, SERVICE_CLEAR_CALL_JOURNAL,
    SERVICE_DEVELOPER_TEST, SERVICE_EXPORT_CALL_JOURNAL,
    SERVICE_EXPORT_DEBUG_BUNDLE, SERVICE_GENERATE_SUPPORT_REPORT,
    SERVICE_OPEN_GATE, SERVICE_REBUILD_CALL_JOURNAL, SERVICE_REJECT_CALL,
    SERVICE_RESET_STATISTICS, SERVICE_TEST_CONNECTION,
)

OPEN_GATE_TIMEOUT = 20.0
ATTR_ENTITY_ID = "entity_id"

SERVICE_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTRY_ID): cv.string})
OPEN_GATE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTRY_ID): cv.string,
    vol.Optional(ATTR_ENTITY_ID): vol.Any(cv.entity_id, [cv.entity_id]),
    vol.Optional(ATTR_REASON, default="Home Assistant service action"): cv.string,
    vol.Optional(ATTR_SOURCE, default="service"): cv.string,
})
DEVELOPER_TEST_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTRY_ID): cv.string,
    vol.Optional(ATTR_TEST, default="all"): vol.In(["all", "cloud", "tls", "sip", "certificates", "sdp", "dialog"]),
})
SUPPORT_REPORT_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTRY_ID): cv.string,
    vol.Optional(ATTR_INCLUDE_LOGS, default=True): cv.boolean,
})

REGISTERED_SERVICES = (
    SERVICE_OPEN_GATE, SERVICE_RESET_STATISTICS, SERVICE_TEST_CONNECTION,
    SERVICE_REJECT_CALL, SERVICE_DEVELOPER_TEST, SERVICE_GENERATE_SUPPORT_REPORT,
    SERVICE_EXPORT_DEBUG_BUNDLE, SERVICE_CLEAN_DEBUG_ENVIRONMENT,
    SERVICE_CLEAR_CALL_JOURNAL, SERVICE_EXPORT_CALL_JOURNAL,
    SERVICE_REBUILD_CALL_JOURNAL,
)


def _loaded_entries(hass: HomeAssistant):
    return [e for e in hass.config_entries.async_entries(DOMAIN) if getattr(e, "runtime_data", None) is not None]


def _service_entries(hass: HomeAssistant, call: ServiceCall, *, require_single: bool = False):
    entries = _loaded_entries(hass)
    requested = call.data.get(ATTR_ENTRY_ID)
    entity_ids = call.data.get(ATTR_ENTITY_ID)
    if entity_ids:
        entity_ids = [entity_ids] if isinstance(entity_ids, str) else entity_ids
        registry = er.async_get(hass)
        entry_ids = {item.config_entry_id for entity_id in entity_ids if (item := registry.async_get(entity_id)) and item.config_entry_id}
        entries = [entry for entry in entries if entry.entry_id in entry_ids]
    elif requested:
        entries = [entry for entry in entries if entry.entry_id == requested]
    if not entries:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="no_matching_config")
    if require_single and len(entries) != 1:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="multiple_gates")
    return entries


async def async_register_services(hass: HomeAssistant) -> None:
    """Register global services once, without closing over a config entry."""
    if hass.services.has_service(DOMAIN, SERVICE_OPEN_GATE):
        return

    from .developer import DeveloperModeDisabledError
    from .event_bus import RuntimeEvent
    from .sip_client import BticinoSipError

    async def open_gate(call: ServiceCall):
        entry = _service_entries(hass, call, require_single=True)[0]
        runtime = entry.runtime_data
        reason = str(call.data.get(ATTR_REASON, "Home Assistant service action"))
        source = str(call.data.get(ATTR_SOURCE, "service"))
        requested_at = datetime.now(UTC)
        request_id = f"{entry.entry_id}-{requested_at.timestamp():.6f}"
        base = {
            "entry_id": entry.entry_id,
            "gateway_id": str(entry.data.get(CONF_GATEWAY_ID, "")),
            "request_id": request_id,
            "reason": reason,
            "source": source,
            "requested_at": requested_at.isoformat(),
        }
        runtime.debug.record("home_assistant", "gate_open_requested", **base, user_id=getattr(call.context, "user_id", None))
        hass.bus.async_fire(EVENT_BUS, {**base, "event_type": "gate_open_requested"}, context=call.context)
        started = monotonic()
        try:
            async with asyncio.timeout(OPEN_GATE_TIMEOUT):
                result = await runtime.client.async_open_gate()
        except (BticinoSipError, TimeoutError) as err:
            duration_ms = round((monotonic() - started) * 1000)
            runtime.last_result = str(err)
            failure = {**base, "event_type": "gate_open_failed", "success": False, "status": "timeout" if isinstance(err, TimeoutError) else "error", "code": None, "duration_ms": duration_ms, "error": str(err)}
            runtime.debug.record("home_assistant", "gate_open_failed", **failure)
            hass.bus.async_fire(EVENT_BUS, failure, context=call.context)
            return {entry.entry_id: failure}
        duration_ms = round((monotonic() - started) * 1000)
        runtime.last_open = datetime.now(UTC)
        runtime.last_result = result.status
        success = {**base, "event_type": "gate_open_succeeded", "success": True, "status": result.status, "code": result.code, "duration_ms": duration_ms}
        runtime.debug.record("home_assistant", "gate_open_succeeded", **success)
        hass.bus.async_fire(EVENT_BUS, success, context=call.context)
        return {entry.entry_id: success}

    async def reset_statistics(call: ServiceCall):
        for entry in _service_entries(hass, call):
            entry.runtime_data.client.reset_statistics()
            await entry.runtime_data.store.async_save(entry.runtime_data.client.export_state())

    async def test_connection(call: ServiceCall):
        for entry in _service_entries(hass, call):
            try:
                await entry.runtime_data.client.async_test_connection()
            except BticinoSipError as err:
                raise HomeAssistantError(translation_domain=DOMAIN, translation_key="sip_connection_test_failed", translation_placeholders={"error": str(err)}) from err

    async def reject_call(call: ServiceCall):
        for entry in _service_entries(hass, call):
            try:
                await entry.runtime_data.client.async_reject_call()
            except BticinoSipError as err:
                raise HomeAssistantError(translation_domain=DOMAIN, translation_key="call_rejection_failed", translation_placeholders={"error": str(err)}) from err

    async def developer_test(call: ServiceCall):
        output = {}
        for entry in _service_entries(hass, call):
            try:
                output[entry.entry_id] = await entry.runtime_data.developer.async_run_tests(str(call.data.get(ATTR_TEST, "all")))
            except DeveloperModeDisabledError as err:
                raise HomeAssistantError(translation_domain=DOMAIN, translation_key="developer_mode_disabled", translation_placeholders={"error": str(err)}) from err
        return output

    async def support_report(call: ServiceCall):
        output = {}
        for entry in _service_entries(hass, call):
            try:
                output[entry.entry_id] = await entry.runtime_data.developer.async_generate_support_report(bool(call.data.get(ATTR_INCLUDE_LOGS, True)))
            except DeveloperModeDisabledError as err:
                raise HomeAssistantError(translation_domain=DOMAIN, translation_key="developer_mode_disabled", translation_placeholders={"error": str(err)}) from err
        return output

    async def clean_debug(call: ServiceCall):
        return {entry.entry_id: await entry.runtime_data.developer.async_clean_debug_environment() for entry in _service_entries(hass, call)}

    async def clear_journal(call: ServiceCall):
        output = {}
        for entry in _service_entries(hass, call):
            await entry.runtime_data.call_journal.async_clear(); output[entry.entry_id] = {"cleared": True}
        return output

    async def export_journal(call: ServiceCall):
        output = {}
        export_dir = Path(hass.config.path(DOMAIN, "exports"))
        await hass.async_add_executor_job(partial(export_dir.mkdir, parents=True, exist_ok=True, mode=0o700))
        for entry in _service_entries(hass, call):
            path = export_dir / f"call-journal-{entry.entry_id}.json"
            payload = json.dumps(entry.runtime_data.call_journal.export_state(), indent=2, ensure_ascii=False)
            await hass.async_add_executor_job(path.write_text, payload, "utf-8")
            await hass.async_add_executor_job(path.chmod, 0o600)
            output[entry.entry_id] = {"path": str(path), "private": True}
        return output

    async def rebuild_journal(call: ServiceCall):
        output = {}
        for entry in _service_entries(hass, call):
            events = [RuntimeEvent.from_dict(item) for item in entry.runtime_data.event_bus.history]
            await entry.runtime_data.call_journal.async_rebuild(events)
            output[entry.entry_id] = entry.runtime_data.call_journal.metrics
        return output

    registrations = {
        SERVICE_OPEN_GATE: (open_gate, OPEN_GATE_SCHEMA, SupportsResponse.OPTIONAL),
        SERVICE_RESET_STATISTICS: (reset_statistics, SERVICE_SCHEMA, SupportsResponse.NONE),
        SERVICE_TEST_CONNECTION: (test_connection, SERVICE_SCHEMA, SupportsResponse.NONE),
        SERVICE_REJECT_CALL: (reject_call, SERVICE_SCHEMA, SupportsResponse.NONE),
        SERVICE_DEVELOPER_TEST: (developer_test, DEVELOPER_TEST_SCHEMA, SupportsResponse.OPTIONAL),
        SERVICE_GENERATE_SUPPORT_REPORT: (support_report, SUPPORT_REPORT_SCHEMA, SupportsResponse.OPTIONAL),
        SERVICE_EXPORT_DEBUG_BUNDLE: (support_report, SUPPORT_REPORT_SCHEMA, SupportsResponse.OPTIONAL),
        SERVICE_CLEAN_DEBUG_ENVIRONMENT: (clean_debug, SERVICE_SCHEMA, SupportsResponse.OPTIONAL),
        SERVICE_CLEAR_CALL_JOURNAL: (clear_journal, SERVICE_SCHEMA, SupportsResponse.OPTIONAL),
        SERVICE_EXPORT_CALL_JOURNAL: (export_journal, SERVICE_SCHEMA, SupportsResponse.OPTIONAL),
        SERVICE_REBUILD_CALL_JOURNAL: (rebuild_journal, SERVICE_SCHEMA, SupportsResponse.OPTIONAL),
    }
    for name, (handler, schema, response) in registrations.items():
        hass.services.async_register(DOMAIN, name, handler, schema=schema, supports_response=response)


def async_unregister_services(hass: HomeAssistant) -> None:
    """Remove every integration service symmetrically."""
    for service in REGISTERED_SERVICES:
        if hass.services.has_service(DOMAIN, service):
            hass.services.async_remove(DOMAIN, service)
