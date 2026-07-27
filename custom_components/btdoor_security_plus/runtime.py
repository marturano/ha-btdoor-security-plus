"""Runtime data for BTDoor Security+."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.helpers.storage import Store

from .event_bus import RuntimeEventBus
from .call_journal import CallJournal
from .sip_client import BticinoSipClient
from .support_debug import SupportDebugRecorder
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .developer import DeveloperTools
    from .runtime_state import BTDoorRuntimeAPI


@dataclass(slots=True)
class BTDoorRuntimeData:
    """Per-entry runtime data."""

    client: BticinoSipClient
    store: Store[dict[str, Any]]
    last_open: datetime | None = None
    last_result: str | None = None
    renewal_unsub: Callable[[], None] | None = None
    event_unsub: Callable[[], None] | None = None
    debug: SupportDebugRecorder | None = None
    developer: "DeveloperTools | None" = None
    last_developer_test_at: datetime | None = None
    last_developer_test_result: str | None = None
    last_support_report_at: datetime | None = None
    last_support_report_path: str | None = None
    last_support_bundle_path: str | None = None
    api: "BTDoorRuntimeAPI | None" = None
    event_bus: RuntimeEventBus | None = None
    call_journal: CallJournal | None = None
    language: str = "en"
    availability_state: bool | None = None
