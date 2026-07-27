"""Formalized, weighted and explainable Health Score aggregation."""
from __future__ import annotations

from .models import DiagnosticResult

HEALTH_SCORE_MODEL_VERSION = 2
HEALTHY_THRESHOLD = 95
DEGRADED_THRESHOLD = 70


def _severity_for_score(score: int, *, timed_out: bool = False) -> str:
    if timed_out or score < DEGRADED_THRESHOLD:
        return "critical"
    if score < HEALTHY_THRESHOLD:
        return "warning"
    return "info"


class HealthEngine:
    """Calculate health without cascading provider failures."""

    @staticmethod
    def aggregate(results: dict[str, DiagnosticResult]) -> dict[str, object]:
        total_weight = sum(max(result.weight, 0) for result in results.values()) or 1
        provider_rows: dict[str, dict[str, object]] = {}
        earned_total = 0.0

        for name, result in results.items():
            result.score = max(0, min(int(result.score), 100))
            if not result.severity or result.severity == "info":
                result.severity = _severity_for_score(result.score, timed_out=result.timed_out)
            if not result.explanation:
                result.explanation = (
                    "Provider passed without deductions."
                    if result.score == 100
                    else f"Provider retained {result.score}% of its weighted points."
                )
            row = result.as_dict()
            earned_total += float(row["points"]["earned"])
            provider_rows[name] = row

        score = round(earned_total * 100 / total_weight)
        status = (
            "healthy"
            if score >= HEALTHY_THRESHOLD
            else "degraded"
            if score >= DEGRADED_THRESHOLD
            else "unhealthy"
        )
        issues = {
            name: row["issues"]
            for name, row in provider_rows.items()
            if not row["healthy"] or row["issues"]
        }
        deductions = {
            name: row["points"]["deducted"]
            for name, row in provider_rows.items()
            if float(row["points"]["deducted"]) > 0
        }
        return {
            "model_version": HEALTH_SCORE_MODEL_VERSION,
            "formula": "round(sum(weight * bounded_score / 100) * 100 / sum(weight))",
            "thresholds": {
                "healthy_min": HEALTHY_THRESHOLD,
                "degraded_min": DEGRADED_THRESHOLD,
                "unhealthy_max": DEGRADED_THRESHOLD - 1,
            },
            "score": score,
            "status": status,
            "healthy": status == "healthy",
            "provider_count": len(results),
            "points": {
                "maximum": total_weight,
                "earned": round(earned_total, 2),
                "deducted": round(total_weight - earned_total, 2),
            },
            "deductions_by_provider": deductions,
            "issues": issues,
            "providers": provider_rows,
        }
