"""Stable internal API consumed by entities, diagnostics and services."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from .models import (
    CloudState,
    DiagnosticsState,
    DialogState,
    GatewayState,
    MediaState,
    RuntimeSnapshot,
    SipState,
)
from .provider import RuntimeStateProvider


class BTDoorRuntimeAPIProtocol(Protocol):
    def gateway(self) -> GatewayState: ...
    def cloud(self) -> CloudState: ...
    def sip(self) -> SipState: ...
    def dialog(self) -> DialogState: ...
    def media(self) -> MediaState: ...
    def diagnostics(self) -> DiagnosticsState: ...
    def devices(self) -> dict[str, Any]: ...
    def snapshot(self) -> RuntimeSnapshot: ...
    async def async_generate_support_bundle(self, include_logs: bool = True) -> Path: ...


class BTDoorRuntimeAPI(RuntimeStateProvider):
    """Default API implementation backed by one config entry runtime."""

    async def async_generate_support_bundle(self, include_logs: bool = True) -> Path:
        developer = getattr(self._runtime, "developer", None)
        if developer is None:
            raise RuntimeError("Developer tools are not initialized")
        result: Any = await developer.async_generate_support_report(include_logs=include_logs)
        return Path(str(result["bundle_path"]))
