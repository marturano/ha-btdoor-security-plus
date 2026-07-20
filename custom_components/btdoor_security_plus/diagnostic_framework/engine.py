"""Diagnostic provider orchestration."""
from __future__ import annotations

import asyncio
from typing import Iterable

from .models import DiagnosticResult
from .provider import DiagnosticProvider


class DiagnosticEngine:
    """Collect providers independently so one failure cannot hide the others."""

    def __init__(self, providers: Iterable[DiagnosticProvider]) -> None:
        self._providers = tuple(providers)

    async def async_collect(self) -> dict[str, DiagnosticResult]:
        async def collect(provider: DiagnosticProvider) -> DiagnosticResult:
            try:
                return await provider.async_collect()
            except Exception as err:  # diagnostics must aggregate failures
                return DiagnosticResult(
                    name=provider.name,
                    healthy=False,
                    score=0,
                    weight=provider.weight,
                    issues=[type(err).__name__],
                    details={"error": str(err)},
                )

        results = await asyncio.gather(*(collect(provider) for provider in self._providers))
        return {result.name: result for result in results}
