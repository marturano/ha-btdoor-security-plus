"""Regression tests for multilingual Assist support in 6.1.0-rc.2."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "custom_components" / "btdoor_security_plus"
LANGUAGES = {
    "en",
    "it",
    "fr",
    "de",
    "es",
    "nl",
    "pt",
    "pl",
    "cs",
    "da",
    "sv",
    "nb",
    "fi",
    "ja",
    "ko",
    "zh-Hans",
    "zh-Hant",
}


def test_version_alignment_rc2():
    manifest = json.loads((DOMAIN / "manifest.json").read_text(encoding="utf-8"))
    constants = (DOMAIN / "const.py").read_text(encoding="utf-8")
    assert f'INTEGRATION_VERSION = "{manifest["version"]}"' in constants


def test_all_supported_sentence_files_are_packaged_and_valid():
    found = set()
    for path in (DOMAIN / "custom_sentences").glob("*/btdoor_security_plus.yaml"):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        lang = payload["language"]
        found.add(lang)
        assert payload["intents"]["BTDoorOpenGate"]["data"][0]["sentences"]
    assert found == LANGUAGES


def test_every_sentence_language_has_localized_responses():
    tree = ast.parse((DOMAIN / "voice.py").read_text(encoding="utf-8"))
    assignment = next(
        n
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "VOICE_RESPONSES" for t in n.targets)
    )
    responses = ast.literal_eval(assignment.value)
    assert set(responses) == LANGUAGES
    assert all(len(value) == 4 and all(value) for value in responses.values())


def test_voice_handler_localizes_all_outcomes_and_keeps_multigate_guard():
    source = (DOMAIN / "voice.py").read_text(encoding="utf-8")
    assert "language = _language(intent_obj)" in source
    assert "len(entries) > 1" in source
    assert "response.async_set_speech(unavailable)" in source
    assert "response.async_set_speech(ambiguous)" in source
    assert "response.async_set_speech(opening)" in source
    assert '"source": "assist"' in source
