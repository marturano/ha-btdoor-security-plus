"""Diagnostic provider orchestration."""
from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Iterable

from .models import DiagnosticResult
from .provider import DiagnosticProvider

DEFAULT_PROVIDER_TIMEOUT_SECONDS = 10.0


class DiagnosticEngine:
    """Collect providers independently so one failure cannot hide the others."""

    def __init__(
        self,
        providers: Iterable[DiagnosticProvider],
        *,
        default_timeout_seconds: float = DEFAULT_PROVIDER_TIMEOUT_SECONDS,
    ) -> None:
        self._providers = tuple(providers)
        self._default_timeout_seconds = max(float(default_timeout_seconds), 0.1)

    async def async_collect(self) -> dict[str, DiagnosticResult]:
        async def collect(provider: DiagnosticProvider) -> DiagnosticResult:
            timeout = max(
                float(getattr(provider, "timeout_seconds", self._default_timeout_seconds)),
                0.1,
            )
            started = perf_counter()
            try:
                result = await asyncio.wait_for(provider.async_collect(), timeout=timeout)
                result.duration_ms = round((perf_counter() - started) * 1000, 2)
                result.timeout_seconds = timeout
                result.timed_out = False
                return result
            except asyncio.TimeoutError:
                return DiagnosticResult(
                    name=provider.name,
                    healthy=False,
                    score=0,
                    weight=provider.weight,
                    severity="critical",
                    explanation=f"Provider exceeded the {timeout:g}s diagnostic timeout.",
                    issues=["provider_timeout"],
                    details={"error": "provider_timeout"},
                    duration_ms=round((perf_counter() - started) * 1000, 2),
                    timeout_seconds=timeout,
                    timed_out=True,
                )
            except Exception as err:  # diagnostics must aggregate failures
                return DiagnosticResult(
                    name=provider.name,
                    healthy=False,
                    score=0,
                    weight=provider.weight,
                    severity="critical",
                    explanation="Provider collection failed; other providers were preserved.",
                    issues=[type(err).__name__],
                    details={"error": str(err)},
                    duration_ms=round((perf_counter() - started) * 1000, 2),
                    timeout_seconds=timeout,
                    timed_out=False,
                )

        results = await asyncio.gather(*(collect(provider) for provider in self._providers))
        return {result.name: result for result in results}
