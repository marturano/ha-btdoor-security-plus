"""Diagnostic provider protocol."""
from __future__ import annotations

from typing import Protocol

from .models import DiagnosticResult


class DiagnosticProvider(Protocol):
    """Contract implemented by all diagnostic providers."""

    name: str
    weight: int

    async def async_collect(self) -> DiagnosticResult:
        """Collect a normalized diagnostic result."""
