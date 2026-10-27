import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_api_documents_and_index():
    base = ROOT / "docs/api"
    index = (base / "README.md").read_text()
    names = [
        "ENTITIES.md",
        "SERVICES.md",
        "EVENTS.md",
        "ERRORS.md",
        "VERSIONING.md",
        "SECURITY.md",
        "VOICE_ASSISTANTS.md",
        "AUTOMATION_EXAMPLES.md",
        "REST.md",
        "WEBSOCKET.md",
    ]
    for name in names:
        assert (base / name).exists()
        assert name in index


def test_every_service_is_documented():
    yaml = (ROOT / "custom_components/btdoor_security_plus/services.yaml").read_text()
    docs = (ROOT / "docs/api/SERVICES.md").read_text()
    for name in re.findall(r"^([a-z][a-z0-9_]+):\s*$", yaml, re.M):
        assert f"`{name}`" in docs


def test_voice_assistant_boundaries():
    text = (ROOT / "docs/api/VOICE_ASSISTANTS.md").read_text()
    for marker in ("Alexa", "Alexa+", "Google Assistant", "Home Assistant exposure configuration"):
        assert marker in text
    assert "does not implement a private Alexa or Google transport" in text


def test_api_adrs_present():
    for n in range(54, 57):
        assert list((ROOT / "docs/adr").glob(f"ADR-{n:04d}-*.md"))
