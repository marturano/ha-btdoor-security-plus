from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_rc8_continuity_documents_exist() -> None:
    required = [
        "PROJECT_MANIFEST.yaml",
        "docs/roadmap/ROADMAP.md",
        "docs/project/CORE_STABLE_1.1_MILESTONE.md",
        "docs/project/DECISIONS_AND_CONSTRAINTS.md",
        "docs/project/FEATURE_AND_VALIDATION_MATRIX.md",
        "handoff/HANDOFF_INDEX.md",
        "docs/index.md",
        "docs/adr/ADR-0025-active-roadmap-and-handoff.md",
        "docs/release/1.1.0-rc.13.md",
        "docs/validation/VALIDATION_REPORT_1.1.0-rc.15.md",
    ]
    assert all((ROOT / path).is_file() for path in required)


def test_rc8_roadmap_order_and_names() -> None:
    roadmap_1x = (ROOT / "docs/roadmap/ROADMAP_1X.md").read_text()
    milestones = [
        "1.1 — Core Stable",
        "1.2 — Universal Door Security Bridge",
        "1.3 — Advanced Media Foundation",
        "1.4 — Audio & Call Control",
        "1.5 — Voicemail Center",
        "1.6 — Multimedia Timeline",
        "1.7 — BTicino / Netatmo Security Cameras",
        "1.8 — Smart Notifications",
        "1.9 — AI Vision & Recognition",
        "1.10 — Core Consolidation & Migration",
    ]
    positions = [roadmap_1x.index(item) for item in milestones]
    assert positions == sorted(positions)
    roadmap_2x = (ROOT / "docs/roadmap/ROADMAP_2X.md").read_text()
    roadmap_3x = (ROOT / "docs/roadmap/ROADMAP_3X.md").read_text()
    assert "2.0 — Ecosystem Foundation" in roadmap_2x
    assert "3.0 — SDK Foundation" in roadmap_3x


def test_handoff_preserves_entity_contract() -> None:
    content = "\n".join(path.read_text(errors="ignore") for path in (ROOT / "handoff").glob("*.md"))
    assert "button.apri_cancello" in content
    assert "switch.apri_cancello_alexa" in content
    assert "Alexa" in content
