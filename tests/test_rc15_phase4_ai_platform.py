import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_gate(name):
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/check_repository_integrity.py"), "--check", name],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_ai_documentation_gate():
    run_gate("ai_documentation")


def test_provider_capability_gate():
    run_gate("provider_capability")


def test_ai_runtime_truth_is_explicit():
    text = (ROOT / "docs/ai/AI_PLATFORM.md").read_text(encoding="utf-8")
    assert "does not claim working" in text
    assert "provider-neutral" in text


def test_face_recognition_safety_boundary():
    text = (ROOT / "docs/ai/FACE_RECOGNITION.md").read_text(encoding="utf-8")
    assert "never unlock a door or gate based solely on recognition" in text


def test_ai_adrs_exist():
    for ident in range(50, 54):
        assert list((ROOT / "docs/adr").glob(f"ADR-{ident:04d}-*.md"))
