"""Device-neutral adapter API for BTDoor Security+."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DeviceCapabilities:
    """Capabilities exposed by an adapter."""

    answer: bool = False
    reject: bool = False
    unlock: bool = False
    auxiliary: bool = False
    snapshot: bool = False
    stream: bool = False


class DeviceAdapter(ABC):
    """Abstract contract implemented by every supported device family."""

    @property
    @abstractmethod
    def capabilities(self) -> DeviceCapabilities:
        """Return supported operations."""

    @abstractmethod
    async def async_connect(self) -> None:
        """Connect and initialize the adapter."""

    @abstractmethod
    async def async_disconnect(self) -> None:
        """Disconnect and release adapter resources."""

    async def async_answer(self) -> None:
        raise NotImplementedError("Answer is not supported by this adapter")

    async def async_reject(self) -> None:
        raise NotImplementedError("Reject is not supported by this adapter")

    async def async_unlock(self) -> None:
        raise NotImplementedError("Unlock is not supported by this adapter")

    async def async_aux(self) -> None:
        raise NotImplementedError("Auxiliary command is not supported by this adapter")

    async def async_snapshot(self) -> bytes:
        raise NotImplementedError("Snapshot is not supported by this adapter")

    async def async_stream(self) -> Any:
        raise NotImplementedError("Streaming is not supported by this adapter")

    @abstractmethod
    def diagnostics(self) -> dict[str, Any]:
        """Return redacted adapter diagnostics."""
