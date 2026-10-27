"""QS-9 behavioural coverage for runtime, support, voice and sentences."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _reset() -> None:
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus") or name.startswith(
            "homeassistant"
        ):
            sys.modules.pop(name, None)
    root = types.ModuleType("custom_components")
    root.__path__ = [str(ROOT / "custom_components")]
    pkg = types.ModuleType("custom_components.btdoor_security_plus")
    pkg.__path__ = [str(PKG)]
    sys.modules[root.__name__] = root
    sys.modules[pkg.__name__] = pkg


def _load(name: str):
    full = f"custom_components.btdoor_security_plus.{name}"
    path = PKG.joinpath(*name.split("."))
    if path.is_dir():
        path = path / "__init__.py"
    else:
        path = path.with_suffix(".py")
    spec = importlib.util.spec_from_file_location(
        full,
        path,
        submodule_search_locations=[str(path.parent)] if path.name == "__init__.py" else None,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full] = mod
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def _ha_stubs() -> None:
    ha = types.ModuleType("homeassistant")
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    helpers = types.ModuleType("homeassistant.helpers")
    storage = types.ModuleType("homeassistant.helpers.storage")
    storage.Store = object
    intent = types.ModuleType("homeassistant.helpers.intent")

    class IntentHandler:
        pass

    class Intent:
        pass

    intent.IntentHandler = IntentHandler
    intent.Intent = Intent
    intent.IntentResponse = object
    intent.registered = []
    intent.async_register = lambda hass, handler: intent.registered.append(handler)
    sys.modules.update({m.__name__: m for m in (ha, core, helpers, storage, intent)})


@pytest.fixture
def modules():
    _reset()
    _ha_stubs()
    _load("const")
    return SimpleNamespace(
        runtime=_load("runtime"),
        support=_load("support_debug"),
        sentence=_load("sentence_manager"),
        voice=_load("voice"),
    )


def test_runtime_data_defaults(modules):
    obj = modules.runtime.BTDoorRuntimeData(client=object(), store=object())
    assert obj.last_open is None and obj.language == "en"
    assert obj.availability_state is None and obj.call_journal is None


def test_support_redaction_and_recording(modules, tmp_path):
    s = modules.support
    text = "Authorization: Digest secret\nuser@example.com 192.168.1.22 branch=z9hG4bKabc;tag=xyz\na=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:secret"
    redacted = s.redact_support_text(text)
    assert "secret" not in redacted
    assert "***@example.com" in redacted
    assert "192.168.xxx.xxx" in redacted
    assert "[HASH:" in redacted
    assert s.redact({"password": "x", "nested": [b"sip_password=y"]})["password"] == "[REDACTED]"

    off = s.SupportDebugRecorder(tmp_path / "off", s.DEBUG_MODE_OFF)
    assert not off.enabled and not off.deep
    off.record("x", "y", password="secret")
    assert off.recent() == []

    deep = s.SupportDebugRecorder(tmp_path / "deep", s.DEBUG_MODE_DEEP)
    assert deep.enabled and deep.deep
    deep.record("integration", "event", password="secret", email="abc@example.com")
    deep.protocol("rx", b"Authorization: token")
    assert len(deep.recent()) == 2
    assert deep.recent()[0]["data"]["password"] == "[REDACTED]"


@pytest.mark.asyncio
async def test_support_writer_rotation_and_clear(modules, tmp_path, monkeypatch):
    s = modules.support
    monkeypatch.setattr(s, "DEBUG_LOG_MAX_BYTES", 50)
    monkeypatch.setattr(s, "DEBUG_LOG_BACKUP_COUNT", 2)
    rec = s.SupportDebugRecorder(tmp_path, s.DEBUG_MODE_DEEP)
    await rec.async_start()
    rec.record("test", "one", value="a" * 100)
    rec.record("test", "two", value="b" * 100)
    await rec.async_stop()
    assert rec.log_path.exists()
    assert any(tmp_path.glob("support-debug.jsonl.*"))
    await rec.async_clear()
    assert rec.recent() == [] and rec.dropped_records == 0
    assert not list(tmp_path.glob("support-debug*.jsonl*"))


def test_sentence_install_new_update_preserve(modules, tmp_path):
    m = modules.sentence
    src = tmp_path / "src"
    dst = tmp_path / "cfg"
    lang = src / "it"
    lang.mkdir(parents=True)
    source = lang / "btdoor_security_plus.yaml"
    source.write_text("language: it\n", encoding="utf-8")
    assert m._install(src, dst) == {"installed": 1, "updated": 0, "preserved": 0}
    assert m._install(src, dst) == {"installed": 0, "updated": 0, "preserved": 0}
    source.write_text("language: it\nnew: true\n", encoding="utf-8")
    assert m._install(src, dst)["updated"] == 1
    target = dst / "custom_sentences" / "it" / "btdoor_security_plus.yaml"
    target.write_text("user edit", encoding="utf-8")
    source.write_text("language: it\nnewer: true\n", encoding="utf-8")
    assert m._install(src, dst)["preserved"] == 1
    assert len(m._digest(b"x")) == 64


@pytest.mark.asyncio
async def test_async_install_sentences(modules, monkeypatch, tmp_path):
    called = {}
    monkeypatch.setattr(
        modules.sentence,
        "_install",
        lambda source, config: (
            called.update(source=source, config=config)
            or {"installed": 1, "updated": 0, "preserved": 0}
        ),
    )
    hass = SimpleNamespace(config=SimpleNamespace(path=lambda: str(tmp_path)))
    result = await modules.sentence.async_install_sentences(hass)
    assert result["installed"] == 1 and called["config"] == tmp_path


class Response:
    def __init__(self):
        self.speech = None

    def async_set_speech(self, value):
        self.speech = value


class IntentObject:
    def __init__(self, hass, language="it"):
        self.hass = hass
        self.language = language
        self.context = object()

    def create_response(self):
        return Response()


@pytest.mark.asyncio
async def test_voice_intent_all_paths(modules):
    v = modules.voice
    handler = v.BTDoorOpenGateIntent()
    config = SimpleNamespace(language="it")

    hass = SimpleNamespace(
        config=config,
        config_entries=SimpleNamespace(async_entries=lambda domain: []),
        services=SimpleNamespace(),
    )
    response = await handler.async_handle(IntentObject(hass))
    assert "disponibile" in response.speech

    entries = [
        SimpleNamespace(entry_id="a", runtime_data=object()),
        SimpleNamespace(entry_id="b", runtime_data=object()),
    ]
    hass.config_entries.async_entries = lambda domain: entries
    response = await handler.async_handle(IntentObject(hass))
    assert "più cancelli" in response.speech

    entries.pop()
    hass.services.async_call = AsyncMock(return_value={"a": {"success": False}})
    response = await handler.async_handle(IntentObject(hass, "it-IT"))
    assert "disponibile" in response.speech
    hass.services.async_call = AsyncMock(return_value={"a": {"success": True}})
    response = await handler.async_handle(IntentObject(hass, "xx"))
    assert response.speech == v.VOICE_RESPONSES["en"][2]
    kwargs = hass.services.async_call.await_args.kwargs
    assert kwargs["blocking"] is True and kwargs["return_response"] is True


def test_voice_registration_idempotent(modules):
    v = modules.voice
    hass = SimpleNamespace(data={})
    v.async_register_voice_intents(hass)
    v.async_register_voice_intents(hass)
    intent_mod = sys.modules["homeassistant.helpers.intent"]
    assert len(intent_mod.registered) == 1
    assert hass.data[f"{v.DOMAIN}_voice_intents_registered"] is True
