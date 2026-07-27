"""Diagnostics for BTDoor Security+."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import BticinoConfigEntry
from .support_models import sanitize_support_data


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: BticinoConfigEntry
) -> dict[str, Any]:
    """Return redacted config-entry diagnostics."""
    client = entry.runtime_data.client
    return sanitize_support_data({
        "entry": dict(entry.data),
        "support_debug": {
            "mode": entry.options.get("debug_mode", "off"),
            "log_path": str(entry.runtime_data.debug.log_path) if entry.runtime_data.debug else None,
            "dropped_records": entry.runtime_data.debug.dropped_records if entry.runtime_data.debug else 0,
            "recent_records": entry.runtime_data.debug.recent() if entry.runtime_data.debug else [],
        },
        "runtime": {
            "registered": client.registered,
            "server": client.server,
            "port": client.port,
            "target_uri": client.target_uri,
            "last_sip_status": client.last_status,
            "last_open": entry.runtime_data.last_open,
            "last_result": entry.runtime_data.last_result,
            "ringing": client.ringing,
            "call_state": client.call_state,
            "last_caller": client.last_caller,
            "last_caller_identity": {
                "uri": client.last_caller_uri,
                "domain": client.last_caller_domain,
                "display_name": client.last_caller_display_name,
            },
            "last_call_id": client.last_call_id,
            "call_started_at": client.call_started_at,
            "call_ended_at": client.call_ended_at,
            "last_call_duration": client.last_call_duration,
            "call_count": client.call_count,
            "missed_call_count": client.missed_call_count,
            "last_message": client.last_message,
            "last_message_at": client.last_message_at,
            "message_count": client.message_count,
            "message_count_scope": "incoming_sip_message_requests_only",
            "last_event_type": client.last_event_type,
            "last_event_at": client.last_event_at,
            "connected_at": client.connected_at,
            "last_keepalive_at": client.last_keepalive_at,
            "reconnect_count": client.reconnect_count,
            "reconnect_count_scope": "successful_reconnections_after_real_disconnect",
            "last_error": client.last_error,
            "last_command_duration": client.last_command_duration,
            "last_command_at": client.last_command_at,
            "dialog_state": client.dialog_state,
            "last_sip_method": client.last_sip_method,
            "last_sdp_offer": client.last_sdp_offer,
            "last_info_body": client.last_info_body,
            "last_notify_event": client.last_notify_event,
            "last_refer_to": client.last_refer_to,
            "media_runtime": client.media_runtime,
            "media_instrumentation": client.media_instrumentation,
            "sip_dispatcher": client.sip_dispatcher_diagnostics,
        },
    })
