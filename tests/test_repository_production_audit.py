from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/audit/production_audit.py"

spec = importlib.util.spec_from_file_location("production_audit", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_production_audit_passes_repository():
    payload = module.audit()
    assert payload["status"] == "PASS"
    assert all(payload["checks"].values())


def test_production_audit_never_grants_publication():
    payload = module.audit()
    assert payload["release_context"]["publication_approval"] == "NOT_GRANTED"


def test_required_documentation_exists():
    for path in [
        "docs/production-audit/README.md",
        "docs/production-audit/PRODUCTION_AUDIT_POLICY.md",
        "docs/adr/ADR-0063-repository-production-audit.md",
        "handoff/36_REPOSITORY_PRODUCTION_AUDIT_STATUS.md",
    ]:
        assert (ROOT / path).is_file(), path
