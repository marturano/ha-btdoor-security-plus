"""Regression tests for the formalized Health Score v2 model."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = "btdoor_health_test"
BASE = ROOT / "custom_components" / "btdoor_security_plus" / "diagnostic_framework"

pkg = types.ModuleType(PKG)
pkg.__path__ = [str(BASE)]
sys.modules.setdefault(PKG, pkg)


def load(name: str):
    spec = importlib.util.spec_from_file_location(f"{PKG}.{name}", BASE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module


models = load("models")
provider_contract = load("provider")
engine_mod = load("engine")
health_mod = load("health")
DiagnosticResult = models.DiagnosticResult
DiagnosticEngine = engine_mod.DiagnosticEngine
HealthEngine = health_mod.HealthEngine


def test_weighted_score_is_reproducible_and_explained() -> None:
    results = {
        "sip": DiagnosticResult("sip", True, 100, 20),
        "cloud": DiagnosticResult("cloud", False, 50, 10, issues=["offline"]),
    }
    health = HealthEngine.aggregate(results)
    assert health["model_version"] == 2
    assert health["score"] == 83
    assert health["status"] == "degraded"
    assert health["points"] == {"maximum": 30, "earned": 25.0, "deducted": 5.0}
    assert health["deductions_by_provider"] == {"cloud": 5.0}
    assert health["providers"]["cloud"]["severity"] == "critical"


def test_provider_result_contains_timing_and_points() -> None:
    row = DiagnosticResult("sip", True, 80, 20, duration_ms=12.5, timeout_seconds=3).as_dict()
    assert row["timing"] == {"duration_ms": 12.5, "timeout_seconds": 3, "timed_out": False}
    assert row["points"] == {"maximum": 20, "earned": 16.0, "deducted": 4.0}


def test_timeout_isolated_and_reported() -> None:
    class SlowProvider:
        name = "slow"
        weight = 10
        timeout_seconds = 0.1

        async def async_collect(self):
            await asyncio.sleep(0.2)
            return DiagnosticResult(self.name, True, 100, self.weight)

    result = asyncio.run(DiagnosticEngine([SlowProvider()]).async_collect())["slow"]
    assert result.timed_out is True
    assert result.score == 0
    assert result.severity == "critical"
    assert result.issues == ["provider_timeout"]
    assert result.duration_ms is not None
