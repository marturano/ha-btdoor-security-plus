"""Support bundle layout helpers."""
from __future__ import annotations

from typing import Any

from .models import DiagnosticResult


class BundleLayoutBuilder:
    """Build stable provider paths for Support Bundle schema 3."""

    @staticmethod
    def provider_payloads(results: dict[str, DiagnosticResult]) -> dict[str, dict[str, Any]]:
        return {
            f"diagnostics/providers/{name}.json": result.as_dict()
            for name, result in results.items()
        }
