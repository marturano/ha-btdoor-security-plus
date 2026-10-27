import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_rc9_version_alignment():
    manifest = json.loads(
        (ROOT / "custom_components/btdoor_security_plus/manifest.json").read_text()
    )
    const = (ROOT / "custom_components/btdoor_security_plus/const.py").read_text()
    assert manifest["version"] == "1.1.0-rc.15"
    assert 'INTEGRATION_VERSION = "1.1.0-rc.15"' in const


def test_canonical_history_and_required_documents():
    project = yaml.safe_load((ROOT / "PROJECT_MANIFEST.yaml").read_text())
    assert project["canonical_history"]["milestones"] == ["1.0 Foundation", "1.1 Core Stable"]
    for rel in project["continuity_documents"]:
        assert (ROOT / rel).exists(), rel


def test_active_docs_have_no_stale_markers():
    manifest = yaml.safe_load((ROOT / "docs/document_manifest.yaml").read_text())
    for locale in manifest["supported_locales"]:
        for rel in manifest["required_user_documents"]:
            text = (ROOT / "docs" / locale / rel).read_text()
            for marker in manifest["forbidden_active_markers"]:
                assert marker not in text


def test_architecture_and_adr_governance_present():
    for rel in [
        "docs/architecture/SYSTEM_ARCHITECTURE.md",
        "docs/architecture/LIFECYCLE_AND_ISOLATION.md",
        "docs/architecture/DEVICE_ENTITY_MODEL.md",
        "docs/architecture/GATE_AND_VOICE_BRIDGE.md",
        "docs/architecture/DIAGNOSTICS_AND_SUPPORT.md",
        "docs/adr/ADR-0026-canonical-product-history.md",
        "docs/adr/ADR-0030-identity-stability.md",
        "docs/engineering/REPOSITORY_CLEANUP_AUDIT_2026-07-22.md",
    ]:
        assert (ROOT / rel).exists(), rel
