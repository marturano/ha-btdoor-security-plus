"""Adapter for existing developer test results."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from ..models import DiagnosticResult


class TestResultProvider:
    """Expose an existing async test through the provider contract."""

    def __init__(
        self,
        name: str,
        weight: int,
        collector: Callable[[], Awaitable[dict[str, Any]]],
    ) -> None:
        self.name = name
        self.weight = weight
        self._collector = collector

    async def async_collect(self) -> DiagnosticResult:
        details = await self._collector()
        explicit = details.get("healthy")
        healthy = bool(explicit) if explicit is not None else True
        score = int(details.get("score", 100 if healthy else 0))
        issues = [str(issue) for issue in details.get("issues", [])]
        return DiagnosticResult(
            name=self.name,
            healthy=healthy,
            score=score,
            weight=self.weight,
            details=details,
            issues=issues,
        )


class StaticResultProvider:
    """Normalize an already collected developer test result."""

    def __init__(self, name: str, weight: int, result: dict[str, Any]) -> None:
        self.name = name
        self.weight = weight
        self._result = result

    async def async_collect(self) -> DiagnosticResult:
        payload = dict(self._result)
        ok = bool(payload.pop("ok", False))
        error = payload.get("error")
        issues = [str(error)] if error else []
        score = int(payload.get("score", 100 if ok else 0))
        return DiagnosticResult(
            name=self.name,
            healthy=ok,
            score=score,
            weight=self.weight,
            details=payload,
            issues=issues,
        )
