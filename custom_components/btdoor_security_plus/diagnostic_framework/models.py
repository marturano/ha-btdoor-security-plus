"""Diagnostic framework models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DiagnosticResult:
    """Normalized diagnostic provider result.

    Timing, timeout and explanation fields are additive so schema-3 readers that
    only consume the original fields remain compatible.
    """

    name: str
    healthy: bool
    score: int
    weight: int
    details: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    severity: str = "info"
    explanation: str = ""
    duration_ms: float | None = None
    timeout_seconds: float | None = None
    timed_out: bool = False

    def as_dict(self) -> dict[str, Any]:
        bounded_score = max(0, min(int(self.score), 100))
        bounded_weight = max(int(self.weight), 0)
        earned_points = round(bounded_weight * bounded_score / 100, 2)
        return {
            "provider": self.name,
            "healthy": self.healthy,
            "score": bounded_score,
            "weight": bounded_weight,
            "severity": self.severity,
            "explanation": self.explanation,
            "issues": list(self.issues),
            "timing": {
                "duration_ms": self.duration_ms,
                "timeout_seconds": self.timeout_seconds,
                "timed_out": self.timed_out,
            },
            "points": {
                "maximum": bounded_weight,
                "earned": earned_points,
                "deducted": round(bounded_weight - earned_points, 2),
            },
            "details": self.details,
        }
