"""Constants for BTDoor Security+."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "btdoor_security_plus"
INTEGRATION_VERSION = "6.0.0"
PLATFORMS = ["switch", "button", "binary_sensor", "sensor", "event"]

CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_PLANT_ID = "plant_id"
CONF_PLANT_NAME = "plant_name"
CONF_GATEWAY_NAME = "gateway_name"
CONF_ID_DEVICE = "id_device"
CONF_CERTIFICATE_NOT_AFTER = "certificate_not_after"
CONF_CA_CHAIN_PATH = "ca_chain_path"
CONF_SIP_ACCOUNT = "sip_account"
CONF_SIP_PASSWORD = "sip_password"
CONF_GATEWAY_ID = "gateway_id"
CONF_DEVICE_NAME = "device_name"
CONF_CLIENT_CERT_PATH = "client_cert_path"
CONF_CLIENT_KEY_PATH = "client_key_path"
CONF_SERVER = "server"
CONF_PORT = "port"
CONF_VERIFY_SERVER = "verify_server"

DEFAULT_DEVICE_NAME = "HomeAssistant-BTicino-DoorEntry"
DEFAULT_SERVER = "sipserver.bs.iotleg.com"
DEFAULT_PORT = 5228
DEFAULT_EXPIRES = 5_184_000
DEFAULT_VERIFY_SERVER = False
DEFAULT_OPEN_COMMAND = "*8*19*20##"
USER_AGENT = "VctLinphoneService/1.17.3"
CERTIFICATE_RENEW_BEFORE = timedelta(days=30)

SERVICE_OPEN_GATE = "open_gate"
SERVICE_RESET_STATISTICS = "reset_statistics"
SERVICE_TEST_CONNECTION = "test_connection"
SERVICE_REJECT_CALL = "reject_call"
ATTR_ENTRY_ID = "entry_id"

EVENT_BUS = "btdoor_security_plus_event"

CALL_TIMEOUT_SECONDS = 45
STORAGE_VERSION = 1

CONF_DEBUG_MODE = "debug_mode"
DEBUG_MODE_OFF = "off"
DEBUG_MODE_SUPPORT = "support"
DEBUG_MODE_DEEP = "deep"
DEFAULT_DEBUG_MODE = DEBUG_MODE_OFF
DEBUG_LOG_MAX_BYTES = 5_000_000
DEBUG_LOG_BACKUP_COUNT = 5
DEBUG_RECENT_RECORDS = 250

CONF_DEVELOPER_MODE = "developer_mode"
DEFAULT_DEVELOPER_MODE = False

CONF_SHOW_CLOUD_STATUS = "show_cloud_status"
CONF_SHOW_SIP_MONITOR = "show_sip_monitor"
CONF_SHOW_CALL_MONITOR = "show_call_monitor"
CONF_SHOW_MEDIA_MONITOR = "show_media_monitor"
CONF_SHOW_ADVANCED_DIAGNOSTICS = "show_advanced_diagnostics"
DEFAULT_SHOW_CLOUD_STATUS = True
DEFAULT_SHOW_SIP_MONITOR = True
DEFAULT_SHOW_CALL_MONITOR = True
DEFAULT_SHOW_MEDIA_MONITOR = True
DEFAULT_SHOW_ADVANCED_DIAGNOSTICS = True
SERVICE_DEVELOPER_TEST = "developer_test"
SERVICE_GENERATE_SUPPORT_REPORT = "generate_support_report"
SERVICE_EXPORT_DEBUG_BUNDLE = "export_debug_bundle"
ATTR_TEST = "test"
ATTR_INCLUDE_LOGS = "include_logs"

SUPPORT_REPORT_RETENTION = 20
SERVICE_CLEAN_DEBUG_ENVIRONMENT = "clean_debug_environment"

SERVICE_CLEAR_CALL_JOURNAL = "clear_call_journal"
SERVICE_EXPORT_CALL_JOURNAL = "export_call_journal"
SERVICE_REBUILD_CALL_JOURNAL = "rebuild_call_journal"
