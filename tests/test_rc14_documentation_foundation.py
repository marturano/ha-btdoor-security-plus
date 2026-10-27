import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.1.0-rc.15"


def test_version_and_pcp():
    manifest = json.loads(
        (ROOT / "custom_components/btdoor_security_plus/manifest.json").read_text()
    )
    assert manifest["version"] == VERSION
    required = [
        "PROJECT_MANIFEST.md",
        "docs/repository/REPOSITORY_POLICY.md",
        "handoff/00_PROJECT_EXECUTION_CONTRACT.md",
        "handoff/01_PROJECT_MEMORY.md",
        "handoff/HANDOFF_INDEX.md",
        "handoff/16_RECOVERY_PROMPT.md",
        "docs/release/RELEASE_CHECKLIST.md",
        "docs/release/DOCUMENTATION_CHANGELOG.md",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), rel


def test_canonical_validation_and_roadmap():
    assert not (ROOT / "docs/archive").exists()
    for rel in [
        "docs/validation/VALIDATION_MAINTENANCE_POLICY.md",
        "docs/validation/VALIDATION_REGISTER.md",
        "docs/validation/VALIDATION_REPORT_1.1.0-rc.15.md",
    ]:
        assert (ROOT / rel).is_file(), rel
    assert "4.4 — Documentation Platform" in (ROOT / "docs/roadmap/ROADMAP_4X.md").read_text()


def test_localized_release_parity():
    manifest = yaml.safe_load((ROOT / "docs/document_manifest.yaml").read_text())
    for locale in manifest["supported_locales"]:
        assert (ROOT / "docs" / locale / "release" / "1.1.0-rc.14.md").is_file()
        assert (ROOT / "docs" / locale / "release" / "1.1.0-rc.15.md").is_file()
