"""Regression tests for the 6.1.0-alpha.2 manager foundation."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _bootstrap_package() -> None:
    sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
    package = types.ModuleType("custom_components.btdoor_security_plus")
    package.__path__ = [str(PKG)]
    sys.modules["custom_components.btdoor_security_plus"] = package

    ha = types.ModuleType("homeassistant")
    helpers = types.ModuleType("homeassistant.helpers")
    registry = types.ModuleType("homeassistant.helpers.device_registry")
    registry.DeviceInfo = dict
    sys.modules.setdefault("homeassistant", ha)
    sys.modules.setdefault("homeassistant.helpers", helpers)
    sys.modules["homeassistant.helpers.device_registry"] = registry


def _load(name: str):
    path = PKG / (name.replace(".", "/") + ".py")
    spec = importlib.util.spec_from_file_location(
        f"custom_components.btdoor_security_plus.{name}", path
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_language_manager_supports_six_locales_and_fallback() -> None:
    _bootstrap_package()
    language = _load("managers.language_manager")
    assert language.SUPPORTED_LANGUAGES == ("en", "it", "fr", "de", "es", "nl")
    assert language.LanguageManager("it-IT").active_language == "it"
    assert language.LanguageManager("nl_NL").active_language == "nl"
    fallback = language.LanguageManager("pt-BR")
    assert fallback.active_language == "en"
    assert fallback.resolution.fallback_to_english is True


def test_device_name_provider_has_complete_catalog() -> None:
    _bootstrap_package()
    _load("const")
    factory = _load("device_model.factory")
    language = _load("managers.language_manager")
    provider_module = _load("managers.device_name_provider")
    for locale in language.SUPPORTED_LANGUAGES:
        provider = provider_module.DeviceNameProvider(locale)
        assert len(provider.catalog()) == 6
        assert provider.name_for(factory.DeviceKind.GATEWAY) is None
    assert provider_module.DeviceNameProvider("it").name_for(factory.DeviceKind.CLOUD) == "Stato Cloud"
    assert provider_module.DeviceNameProvider("nl").name_for(factory.DeviceKind.DIAGNOSTICS) == "Geavanceerde diagnostiek"


def test_ds_plus_device_models_are_declared() -> None:
    source = (PKG / "device_model" / "factory.py").read_text()
    for model in (
        "DS+ Suite - Integration Hub",
        "DS+ Suite - Cloud Status",
        "DS+ Suite - SIP Monitor",
        "DS+ Suite - Call Manager",
        "DS+ Suite - Multimedia Monitor",
        "DS+ Suite - Advanced Diagnostics",
    ):
        assert model in source


def test_all_six_home_assistant_translation_files_exist() -> None:
    translation_dir = PKG / "translations"
    files = {path.stem for path in translation_dir.glob("*.json")}
    assert {"en", "it", "fr", "de", "es", "nl"} <= files
    reference = json.loads((translation_dir / "en.json").read_text())
    dutch = json.loads((translation_dir / "nl.json").read_text())
    assert reference.keys() == dutch.keys()
    assert dutch["options"]["error"]["advanced_diagnostics_requires_developer_mode"]


def test_setup_uses_new_manager_facade() -> None:
    source = (PKG / "__init__.py").read_text()
    assert "from .managers import async_register_devices" in source
