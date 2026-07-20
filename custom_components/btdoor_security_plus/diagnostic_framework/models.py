"""Diagnostic framework models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DiagnosticResult:
    """Normalized diagnostic provider result."""

    name: str
    healthy: bool
    score: int
    weight: int
    details: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "healthy": self.healthy,
            "score": self.score,
            "weight": self.weight,
            "issues": list(self.issues),
            "details": self.details,
        }
