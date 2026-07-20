"""Tests for the alpha.25 modular diagnostic framework."""
from __future__ import annotations

import asyncio

from custom_components.btdoor_security_plus.diagnostic_framework import DiagnosticEngine, HealthEngine
from custom_components.btdoor_security_plus.diagnostic_framework.providers import StaticResultProvider


def test_provider_collection_and_health_are_independent() -> None:
    async def run():
        engine = DiagnosticEngine([
            StaticResultProvider("sip", 70, {"ok": True, "registered": True}),
            StaticResultProvider("media", 30, {"ok": False, "error": "not ready"}),
        ])
        results = await engine.async_collect()
        health = HealthEngine.aggregate(results)
        return results, health

    results, health = asyncio.run(run())
    assert results["sip"].healthy is True
    assert results["media"].healthy is False
    assert health["score"] == 70
    assert health["status"] == "degraded"
    assert "media" in health["issues"]


def test_provider_payload_does_not_require_home_assistant_runtime() -> None:
    async def run():
        provider = StaticResultProvider("tls", 15, {"ok": True, "tls_version": "TLSv1.3"})
        return await provider.async_collect()

    result = asyncio.run(run())
    assert result.as_dict()["details"]["tls_version"] == "TLSv1.3"
    assert result.score == 100
