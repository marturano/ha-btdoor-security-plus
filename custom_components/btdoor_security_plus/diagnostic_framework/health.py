"""Weighted health aggregation."""
from __future__ import annotations

from .models import DiagnosticResult


class HealthEngine:
    """Calculate health without cascading provider failures."""

    @staticmethod
    def aggregate(results: dict[str, DiagnosticResult]) -> dict[str, object]:
        total_weight = sum(max(result.weight, 0) for result in results.values()) or 1
        earned = sum(
            max(result.weight, 0) * max(0, min(result.score, 100)) / 100
            for result in results.values()
        )
        score = round(earned * 100 / total_weight)
        status = "healthy" if score >= 95 else "degraded" if score >= 70 else "unhealthy"
        issues = {
            name: result.issues
            for name, result in results.items()
            if not result.healthy or result.issues
        }
        return {
            "score": score,
            "status": status,
            "healthy": status == "healthy",
            "provider_count": len(results),
            "issues": issues,
            "providers": {name: result.as_dict() for name, result in results.items()},
        }
