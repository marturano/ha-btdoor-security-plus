"""Diagnostic and call sensors for BTDoor Security+."""
from __future__ import annotations

from datetime import UTC, datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import BticinoConfigEntry
from .entity import BticinoDoorEntryEntity, BticinoSipClientEntity
from .device_model import DeviceKind
from .entity_metrics import last_call_summary, last_completed_session, runtime_health
from .analysis import build_runtime_summary
from .visibility import visibility_for_entry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BticinoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up BTDoor Security+ sensors."""
    entities = [
            BticinoLastSipStatusSensor(entry),
            BticinoLastOpenSensor(entry),
            BticinoLastEventSensor(entry),
            BticinoLastCallerSensor(entry),
            BticinoLastMessageSensor(entry),
            BticinoCallStateSensor(entry),
            BticinoLastCallDurationSensor(entry),
            BticinoCallCountSensor(entry),
            BticinoLastCallStartedSensor(entry),
            BticinoLastCallEndedSensor(entry),
            BticinoMissedCallCountSensor(entry),
            BticinoMessageCountSensor(entry),
            BticinoLastMessageTimeSensor(entry),
            BticinoLastEventTimeSensor(entry),
            BticinoReconnectCountSensor(entry),
            BticinoLastErrorSensor(entry),
            BticinoConnectionUptimeSensor(entry),
            BticinoLastCommandDurationSensor(entry),
            BticinoLastCommandTimeSensor(entry),
            BticinoConnectionQualitySensor(entry),
            BticinoDialogStateSensor(entry),
            BticinoLastSipMethodSensor(entry),
            BticinoLastSdpOfferSensor(entry),
            BticinoSdpSummarySensor(entry),
            BticinoAudioOfferSensor(entry),
            BticinoVideoOfferSensor(entry),
            BticinoMediaPreparationSensor(entry),
            BticinoSelectedAudioCodecSensor(entry),
            BticinoSelectedVideoCodecSensor(entry),
            BticinoSrtpSuiteSensor(entry),
            BTDoorLastCallSummarySensor(entry),
            BTDoorLastMediaCloseReasonSensor(entry),
            BTDoorRetainedMediaSessionsSensor(entry),
            BTDoorCloudStateSensor(entry),
            BTDoorCloudEndpointSensor(entry),
            BTDoorCloudLastErrorSensor(entry),
            BTDoorDialogCallIdSensor(entry),
            BTDoorCallJournalLastCallSensor(entry),
            BTDoorCallJournalCountSensor(entry),
            BTDoorCallJournalMissedCountSensor(entry),
            BTDoorCallJournalAverageDurationSensor(entry),
            BTDoorCallJournalAnsweredTodaySensor(entry),
            BTDoorCallJournalMissedTodaySensor(entry),
            *(
                [
                    BticinoLastDeveloperTestSensor(entry),
                    BticinoLastSupportReportSensor(entry),
                    BTDoorRuntimeHealthSensor(entry),
                    BTDoorRuntimeScoreSensor(entry),
                    BTDoorOperationsSummarySensor(entry),
                    BTDoorDeveloperRuntimeInspectorSensor(entry),
                    BTDoorDeveloperEventMonitorSensor(entry),
                    BTDoorDeveloperEventMetricsSensor(entry),
                ]
                if bool(entry.options.get("developer_mode", False))
                else []
            ),
    ]
    async_add_entities(visibility_for_entry(entry).filter_entities(entities))

class _ListeningEntity(BticinoDoorEntryEntity):
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self._entry.runtime_data.client.add_listener(
                lambda _event, _data: self.async_write_ha_state()
            )
        )


class _SipListeningEntity(BticinoSipClientEntity):
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self._entry.runtime_data.client.add_listener(
                lambda _event, _data: self.async_write_ha_state()
            )
        )


class BticinoLastSipStatusSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.SIP
    _attr_translation_key = "last_sip_status"
    _attr_icon = "mdi:message-text-fast"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_sip_status"
    @property
    def native_value(self): return self._entry.runtime_data.client.last_status


class BticinoLastOpenSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.GATEWAY
    _attr_translation_key = "last_gate_open"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_gate_open"
    @property
    def native_value(self): return self._entry.runtime_data.last_open


class BticinoLastEventSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.GATEWAY
    _attr_translation_key = "last_event"
    _attr_icon = "mdi:timeline-clock"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_event"
    @property
    def native_value(self): return self._entry.runtime_data.client.last_event_type


class BticinoLastCallerSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "last_caller"
    _attr_icon = "mdi:account-voice"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_caller"
    @property
    def native_value(self):
        return self._entry.runtime_data.client.last_caller

    @property
    def extra_state_attributes(self):
        client = self._entry.runtime_data.client
        return {
            key: value
            for key, value in {
                "sip_uri": client.last_caller_uri,
                "sip_domain": client.last_caller_domain,
                "sip_tag": client.last_caller_tag,
                "display_name": client.last_caller_display_name,
                "raw_header": client.last_caller_raw,
                "call_id": client.last_call_id,
                "call_state": client.call_state,
                "last_method": client.last_sip_method,
            }.items()
            if value is not None
        }


class BticinoLastMessageSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.GATEWAY
    _attr_translation_key = "last_message"
    _attr_icon = "mdi:message-text"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_message"
    @property
    def native_value(self): return self._entry.runtime_data.client.last_message


class BticinoCallStateSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "call_state"
    _attr_icon = "mdi:phone-in-talk"
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_call_state"
    @property
    def native_value(self): return self._entry.runtime_data.client.call_state
    @property
    def extra_state_attributes(self):
        client = self._entry.runtime_data.client
        return {"caller": client.last_caller, "call_id": client.last_call_id}


class BticinoLastCallDurationSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "last_call_duration"
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:timer-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_call_duration"
    @property
    def native_value(self):
        value = self._entry.runtime_data.client.last_call_duration
        return round(value, 1) if value is not None else None


class BticinoCallCountSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "call_count"
    _attr_icon = "mdi:counter"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_call_count"
    @property
    def native_value(self): return self._entry.runtime_data.client.call_count


class BticinoLastCallStartedSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "last_call_started"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_call_started"
    @property
    def native_value(self): return self._entry.runtime_data.client.call_started_at


class BticinoLastCallEndedSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "last_call_ended"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_call_ended"
    @property
    def native_value(self): return self._entry.runtime_data.client.call_ended_at


class BticinoMissedCallCountSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "missed_call_count"
    _attr_icon = "mdi:phone-missed"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_missed_call_count"
    @property
    def native_value(self): return self._entry.runtime_data.client.missed_call_count


class BticinoMessageCountSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.GATEWAY
    _attr_translation_key = "message_count"
    _attr_icon = "mdi:message-badge"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_message_count"
    @property
    def native_value(self): return self._entry.runtime_data.client.message_count


class BticinoLastMessageTimeSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.GATEWAY
    _attr_translation_key = "last_message_time"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_message_time"
    @property
    def native_value(self): return self._entry.runtime_data.client.last_message_at


class BticinoLastEventTimeSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.GATEWAY
    _attr_translation_key = "last_event_time"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_event_time"
    @property
    def native_value(self): return self._entry.runtime_data.client.last_event_at


class BticinoReconnectCountSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.SIP
    _attr_translation_key = "reconnect_count"
    _attr_icon = "mdi:connection"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_reconnect_count"
    @property
    def native_value(self): return self._entry.runtime_data.client.reconnect_count


class BticinoLastErrorSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.SIP
    _attr_translation_key = "last_error"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_error"
    @property
    def native_value(self): return self._entry.runtime_data.client.last_error


class BticinoConnectionUptimeSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.SIP
    _attr_translation_key = "connection_uptime"
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:timer-sand"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_connection_uptime"
    @property
    def native_value(self):
        value = self._entry.runtime_data.client.connected_at
        return round((datetime.now(UTC)-value).total_seconds()) if value else None


class BticinoLastCommandDurationSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.SIP
    _attr_translation_key = "last_command_duration"
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:speedometer"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_command_duration"
    @property
    def native_value(self):
        value=self._entry.runtime_data.client.last_command_duration
        return round(value, 3) if value is not None else None


class BticinoLastCommandTimeSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.SIP
    _attr_translation_key = "last_command_time"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_last_command_time"
    @property
    def native_value(self): return self._entry.runtime_data.client.last_command_at


class BticinoConnectionQualitySensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.SIP
    _attr_translation_key = "connection_quality"
    _attr_icon = "mdi:signal"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_connection_quality"

    @property
    def native_value(self):
        client = self._entry.runtime_data.client
        if not client.registered:
            return "offline"
        if client.last_error:
            return "poor"
        duration = client.last_command_duration
        if duration is None:
            return "good"
        if duration <= 0.75:
            return "excellent"
        if duration <= 1.5:
            return "good"
        if duration <= 3.0:
            return "average"
        return "poor"

    @property
    def extra_state_attributes(self):
        client = self._entry.runtime_data.client
        return {
            "registered": client.registered,
            "last_command_duration": client.last_command_duration,
            "reconnect_count": client.reconnect_count,
            "last_error": client.last_error,
        }


class BticinoDialogStateSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "dialog_state"
    _attr_icon = "mdi:phone-sync"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_dialog_state"

    @property
    def native_value(self):
        return self._entry.runtime_data.client.dialog_state


class BticinoLastSipMethodSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "last_sip_method"
    _attr_icon = "mdi:protocol"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_last_sip_method"

    @property
    def native_value(self):
        return self._entry.runtime_data.client.last_sip_method


class BticinoLastSdpOfferSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "last_sdp_offer"
    _attr_icon = "mdi:file-document-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_last_sdp_offer"

    @property
    def native_value(self):
        value = self._entry.runtime_data.client.last_sdp_offer
        if not value:
            return None
        return value[:255]

    @property
    def extra_state_attributes(self):
        return {"sdp": self._entry.runtime_data.client.last_sdp_offer}


class BticinoSdpSummarySensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.MEDIA
    _attr_translation_key = "sdp_summary"
    _attr_icon = "mdi:transit-connection-variant"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_sdp_summary"

    @property
    def native_value(self):
        return self._entry.runtime_data.client.last_sdp_summary


class BticinoAudioOfferSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.MEDIA
    _attr_translation_key = "audio_offer"
    _attr_icon = "mdi:waveform"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_audio_offer"

    @property
    def native_value(self):
        client = self._entry.runtime_data.client
        if client.sdp_audio_port is None:
            return None
        return f"{client.sdp_audio_address or '-'}:{client.sdp_audio_port}"

    @property
    def extra_state_attributes(self):
        client = self._entry.runtime_data.client
        return {
            "address": client.sdp_audio_address,
            "port": client.sdp_audio_port,
            "direction": client.sdp_audio_direction,
            "codecs": list(client.sdp_audio_codecs),
        }


class BticinoVideoOfferSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.MEDIA
    _attr_translation_key = "video_offer"
    _attr_icon = "mdi:video-wireless-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_video_offer"

    @property
    def native_value(self):
        client = self._entry.runtime_data.client
        if client.sdp_video_port is None:
            return None
        return f"{client.sdp_video_address or '-'}:{client.sdp_video_port}"

    @property
    def extra_state_attributes(self):
        client = self._entry.runtime_data.client
        return {
            "address": client.sdp_video_address,
            "port": client.sdp_video_port,
            "direction": client.sdp_video_direction,
            "codecs": list(client.sdp_video_codecs),
        }


class BticinoMediaPreparationSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.MEDIA
    _attr_translation_key = "media_preparation"
    _attr_icon = "mdi:multimedia"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_media_preparation"

    @property
    def native_value(self):
        client = self._entry.runtime_data.client
        return client.media_runtime_state

    @property
    def extra_state_attributes(self):
        return self._entry.runtime_data.client.media_runtime


class BticinoSelectedAudioCodecSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.MEDIA
    _attr_translation_key = "selected_audio_codec"
    _attr_icon = "mdi:waveform"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_selected_audio_codec"

    @property
    def native_value(self):
        plan = self._entry.runtime_data.client.media_plan
        return plan.get("audio", {}).get("codec") if plan else None

    @property
    def extra_state_attributes(self):
        plan = self._entry.runtime_data.client.media_plan
        return dict(plan.get("audio", {})) if plan else {}


class BticinoSelectedVideoCodecSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.MEDIA
    _attr_translation_key = "selected_video_codec"
    _attr_icon = "mdi:video-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_selected_video_codec"

    @property
    def native_value(self):
        plan = self._entry.runtime_data.client.media_plan
        return plan.get("video", {}).get("codec") if plan else None

    @property
    def extra_state_attributes(self):
        plan = self._entry.runtime_data.client.media_plan
        return dict(plan.get("video", {})) if plan else {}


class BticinoSrtpSuiteSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.MEDIA
    _attr_translation_key = "srtp_suite"
    _attr_icon = "mdi:shield-lock-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_srtp_suite"

    @property
    def native_value(self):
        plan = self._entry.runtime_data.client.media_plan
        return plan.get("srtp", {}).get("suite") if plan else None

    @property
    def extra_state_attributes(self):
        plan = self._entry.runtime_data.client.media_plan
        return dict(plan.get("srtp", {})) if plan else {}


class BticinoLastDeveloperTestSensor(BticinoDoorEntryEntity, SensorEntity):
    _device_kind = DeviceKind.DIAGNOSTICS
    _attr_translation_key = "last_developer_test"
    _attr_icon = "mdi:flask-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_last_developer_test"

    @property
    def native_value(self):
        return self._entry.runtime_data.last_developer_test_result

    @property
    def extra_state_attributes(self):
        value = self._entry.runtime_data.last_developer_test_at
        return {"tested_at": value.isoformat() if value else None}


class BticinoLastSupportReportSensor(BticinoDoorEntryEntity, SensorEntity):
    _device_kind = DeviceKind.DIAGNOSTICS
    _attr_translation_key = "last_support_report"
    _attr_icon = "mdi:file-document-check-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_last_support_report"

    @property
    def native_value(self):
        value = self._entry.runtime_data.last_support_report_at
        return value.isoformat() if value else None

    @property
    def extra_state_attributes(self):
        runtime = self._entry.runtime_data
        return {
            "report_path": runtime.last_support_report_path,
            "bundle_path": runtime.last_support_bundle_path,
        }


class _DeveloperEventEntity(BticinoDoorEntryEntity):
    """Base class for developer entities refreshed by the runtime Event Bus."""

    _device_kind = DeviceKind.DIAGNOSTICS
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        bus = self._entry.runtime_data.event_bus
        if bus is not None:
            self.async_on_remove(bus.subscribe(lambda _event: self.async_write_ha_state()))


class BTDoorDeveloperRuntimeInspectorSensor(_DeveloperEventEntity, SensorEntity):
    """Expose a compact, immutable runtime snapshot in Developer Mode."""

    _attr_translation_key = "developer_runtime_inspector"
    _attr_icon = "mdi:state-machine"

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_developer_runtime_inspector"

    @property
    def native_value(self):
        api = self._entry.runtime_data.api
        if api is None:
            return "unavailable"
        snapshot = api.snapshot()
        if not snapshot.sip.registered:
            return "sip_unregistered"
        if not snapshot.cloud.connected:
            return "cloud_disconnected"
        return "healthy"

    @property
    def extra_state_attributes(self):
        api = self._entry.runtime_data.api
        if api is None:
            return {}
        snapshot = api.snapshot()
        snapshot_data = snapshot.as_dict()
        return {
            "gateway": snapshot_data["gateway"],
            "cloud": snapshot_data["cloud"],
            "sip": snapshot_data["sip"],
            "dialog": snapshot_data["dialog"],
            "media": snapshot_data["media"],
            "diagnostics": snapshot_data["diagnostics"],
        }


class BTDoorDeveloperEventMonitorSensor(_DeveloperEventEntity, SensorEntity):
    """Expose the last canonical runtime event and a small sanitized timeline."""

    _attr_translation_key = "developer_event_monitor"
    _attr_icon = "mdi:timeline-text-outline"

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_developer_event_monitor"

    @property
    def native_value(self):
        bus = self._entry.runtime_data.event_bus
        last = bus.metrics.get("last_event") if bus is not None else None
        return last.get("type", "none") if isinstance(last, dict) else "none"

    @property
    def extra_state_attributes(self):
        bus = self._entry.runtime_data.event_bus
        if bus is None:
            return {}
        timeline = []
        for item in bus.history[-20:]:
            timeline.append({
                "timestamp": item.get("timestamp"),
                "type": item.get("type"),
                "source": item.get("source"),
            })
        return {"retained_events": len(bus.history), "timeline": timeline}


class BTDoorDeveloperEventMetricsSensor(_DeveloperEventEntity, SensorEntity):
    """Expose Event Bus counters for developer dashboards."""

    _attr_translation_key = "developer_event_metrics"
    _attr_icon = "mdi:chart-box-outline"

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_developer_event_metrics"

    @property
    def native_value(self):
        bus = self._entry.runtime_data.event_bus
        return int(bus.metrics.get("retained_events", 0)) if bus is not None else 0

    @property
    def extra_state_attributes(self):
        bus = self._entry.runtime_data.event_bus
        return dict(bus.metrics) if bus is not None else {}


class BTDoorLastCallSummarySensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "last_call_summary"
    _attr_icon = "mdi:phone-log"

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_last_call_summary"

    @property
    def native_value(self):
        api = self._entry.runtime_data.api
        if api is None:
            return last_call_summary(self._entry.runtime_data.client)[0]
        media = api.media()
        dialog = api.dialog()
        reason = (media.close_reason or dialog.call_state or "unknown").lower()
        return {"cancel": "missed", "bye": "completed"}.get(reason, reason)

    @property
    def extra_state_attributes(self):
        api = self._entry.runtime_data.api
        if api is None:
            return last_call_summary(self._entry.runtime_data.client)[1]
        media = api.media()
        dialog = api.dialog()
        return {
            key: value
            for key, value in {
                "caller": dialog.caller,
                "call_id": dialog.call_id,
                "duration_seconds": media.duration_seconds,
                "close_reason": media.close_reason,
                "audio_codec": media.audio_codec,
                "video_codec": media.video_codec,
                "started_at": media.started_at or dialog.started_at,
                "closed_at": media.closed_at or dialog.ended_at,
            }.items()
            if value is not None
        }


class BTDoorLastMediaCloseReasonSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.MEDIA
    _attr_translation_key = "last_media_close_reason"
    _attr_icon = "mdi:phone-hangup"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_last_media_close_reason"

    @property
    def native_value(self):
        api = self._entry.runtime_data.api
        return api.media().close_reason if api is not None else last_completed_session(self._entry.runtime_data.client).get("closed_reason")


class BTDoorRuntimeHealthSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIAGNOSTICS
    _attr_translation_key = "runtime_health"
    _attr_icon = "mdi:heart-pulse"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_runtime_health"

    @property
    def native_value(self):
        api = self._entry.runtime_data.api
        return api.diagnostics().status if api is not None else runtime_health(self._entry.runtime_data.client)[0]

    @property
    def extra_state_attributes(self):
        api = self._entry.runtime_data.api
        if api is None:
            status, score, details = runtime_health(self._entry.runtime_data.client)
            return {"score": score, **details}
        state = api.diagnostics()
        return {
            "score": state.score,
            "registered": state.sip_registered,
            "dialog_state": state.dialog_state,
            "media_state": state.media_state,
            "last_error": state.last_error,
            "issues": list(state.issues),
        }


class BTDoorRuntimeScoreSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIAGNOSTICS
    _attr_translation_key = "runtime_score"
    _attr_icon = "mdi:gauge"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = "%"

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_runtime_score"

    @property
    def native_value(self):
        api = self._entry.runtime_data.api
        return api.diagnostics().score if api is not None else runtime_health(self._entry.runtime_data.client)[1]


class BTDoorRetainedMediaSessionsSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.MEDIA
    _attr_translation_key = "retained_media_sessions"
    _attr_icon = "mdi:history"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_retained_media_sessions"

    @property
    def native_value(self):
        api = self._entry.runtime_data.api
        return api.media().retained_sessions if api is not None else self._entry.runtime_data.client.media_session_metrics.get("retained_sessions", 0)

    @property
    def extra_state_attributes(self):
        return dict(self._entry.runtime_data.client.media_session_metrics)


class BTDoorCloudStateSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.CLOUD
    _attr_translation_key = "cloud_state"
    _attr_icon = "mdi:cloud-check"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_cloud_state"

    @property
    def native_value(self):
        return self._entry.runtime_data.api.cloud().status

    @property
    def extra_state_attributes(self):
        state = self._entry.runtime_data.api.cloud()
        return {
            "connected": state.connected,
            "authenticated": state.authenticated,
            "certificate_ready": state.certificate_ready,
            "last_request": state.last_request,
            "last_response": state.last_response,
        }


class BTDoorCloudEndpointSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.CLOUD
    _attr_translation_key = "cloud_endpoint"
    _attr_icon = "mdi:cloud-tags"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_cloud_endpoint"

    @property
    def native_value(self):
        return self._entry.runtime_data.api.cloud().endpoint


class BTDoorCloudLastErrorSensor(_SipListeningEntity, SensorEntity):
    _device_kind = DeviceKind.CLOUD
    _attr_translation_key = "cloud_last_error"
    _attr_icon = "mdi:cloud-alert"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_cloud_last_error"

    @property
    def native_value(self):
        return self._entry.runtime_data.api.cloud().last_error


class BTDoorDialogCallIdSensor(_ListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "dialog_call_id"
    _attr_icon = "mdi:identifier"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_dialog_call_id"

    @property
    def native_value(self):
        return self._entry.runtime_data.api.dialog().call_id


class BTDoorOperationsSummarySensor(_SipListeningEntity, SensorEntity):
    """Expose the complete Operations Center snapshot as one stable entity."""

    _device_kind = DeviceKind.DIAGNOSTICS
    _attr_translation_key = "operations_summary"
    _attr_icon = "mdi:view-dashboard-variant-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry):
        super().__init__(entry)
        self._attr_unique_id = f"{entry.unique_id}_operations_summary"

    @property
    def native_value(self):
        return build_runtime_summary(self._entry.runtime_data.api).overall_status

    @property
    def extra_state_attributes(self):
        return build_runtime_summary(self._entry.runtime_data.api).as_dict()


class _EventBusListeningEntity(BticinoDoorEntryEntity):
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        bus = self._entry.runtime_data.event_bus
        if bus is not None:
            self.async_on_remove(bus.subscribe(lambda _event: self.async_write_ha_state()))


class BTDoorCallJournalLastCallSensor(_EventBusListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "call_journal_last_call"
    _attr_icon = "mdi:book-clock-outline"
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_call_journal_last_call"
    @property
    def native_value(self):
        record = self._entry.runtime_data.call_journal.last_record if self._entry.runtime_data.call_journal else None
        return record.get("result") if record else None
    @property
    def extra_state_attributes(self):
        record = self._entry.runtime_data.call_journal.last_record if self._entry.runtime_data.call_journal else None
        return record or {}


class BTDoorCallJournalCountSensor(_EventBusListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "call_journal_count"
    _attr_icon = "mdi:book-open-page-variant-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_call_journal_count"
    @property
    def native_value(self):
        journal = self._entry.runtime_data.call_journal
        return len(journal.records) if journal else 0


class BTDoorCallJournalMissedCountSensor(_EventBusListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "call_journal_missed_count"
    _attr_icon = "mdi:phone-missed-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_call_journal_missed_count"
    @property
    def native_value(self):
        journal = self._entry.runtime_data.call_journal
        if not journal:
            return 0
        return int(journal.metrics.get("calls_by_result", {}).get("missed", 0))


class BTDoorCallJournalAverageDurationSensor(_EventBusListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "call_journal_average_duration"
    _attr_icon = "mdi:timer-outline"
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_call_journal_average_duration"
    @property
    def native_value(self):
        journal = self._entry.runtime_data.call_journal
        return journal.metrics.get("average_duration_seconds") if journal else None

class BTDoorCallJournalAnsweredTodaySensor(_EventBusListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "call_journal_answered_today"
    _attr_icon = "mdi:phone-check-outline"
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_call_journal_answered_today"
    @property
    def native_value(self):
        journal = self._entry.runtime_data.call_journal
        return int(journal.metrics.get("answered_today", 0)) if journal else 0

class BTDoorCallJournalMissedTodaySensor(_EventBusListeningEntity, SensorEntity):
    _device_kind = DeviceKind.DIALOG
    _attr_translation_key = "call_journal_missed_today"
    _attr_icon = "mdi:phone-missed-outline"
    def __init__(self, entry):
        super().__init__(entry); self._attr_unique_id=f"{entry.unique_id}_call_journal_missed_today"
    @property
    def native_value(self):
        journal = self._entry.runtime_data.call_journal
        return int(journal.metrics.get("missed_today", 0)) if journal else 0
