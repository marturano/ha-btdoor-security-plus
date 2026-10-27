import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _checker():
    path = ROOT / "tools" / "check_repository_integrity.py"
    spec = importlib.util.spec_from_file_location("integrity", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_architecture_gate_passes():
    assert _checker().architecture()["status"] == "PASS"


def test_mermaid_gate_passes():
    assert _checker().mermaid()["status"] == "PASS"


def test_architecture_index_contains_core_models():
    text = (ROOT / "docs/architecture/README.md").read_text(encoding="utf-8")
    for name in ("CONFIG_ENTRY_MODEL.md", "DEVICE_MODEL.md", "EVENT_MODEL.md", "DATA_FLOW.md"):
        assert name in text
