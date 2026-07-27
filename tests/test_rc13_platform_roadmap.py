from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_rc13_version_and_roadmaps():
    manifest = json.loads((ROOT / "custom_components/btdoor_security_plus/manifest.json").read_text())
    assert manifest["version"] == "1.1.0-rc.15"
    expected = {
        "ROADMAP_1X.md": ["1.9 — AI Vision & Recognition", "1.10 — Core Consolidation & Migration"],
        "ROADMAP_2X.md": ["2.0 — Ecosystem Foundation", "2.7 — MyHOME Platform"],
        "ROADMAP_3X.md": ["3.0 — SDK Foundation", "3.1 — Extension Framework"],
    }
    for name, markers in expected.items():
        text = (ROOT / "docs" / "roadmap" / name).read_text()
        for marker in markers:
            assert marker in text


def test_platform_governance_documents_exist():
    required = [
        "PROJECT_VISION.md", "ARCHITECTURE_PRINCIPLES.md",
        "docs/architecture/ECOSYSTEM_MODEL.md", "docs/architecture/AI_PIPELINE.md",
        "docs/ai/VISION.md", "docs/sdk/SDK_STRATEGY.md",
        "docs/security/SECURITY_BASELINE.md", "docs/benchmarks/BASELINES.md",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), rel
