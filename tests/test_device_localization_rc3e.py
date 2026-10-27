"""Regression tests for localized device registry names in rc.3e."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _load_modules():
    package = types.ModuleType("custom_components.btdoor_security_plus")
    package.__path__ = [str(PKG)]
    sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
    sys.modules["custom_components.btdoor_security_plus"] = package

    # Stub Home Assistant's DeviceInfo for factory import.
    ha = types.ModuleType("homeassistant")
    helpers = types.ModuleType("homeassistant.helpers")
    registry = types.ModuleType("homeassistant.helpers.device_registry")
    registry.DeviceInfo = dict
    sys.modules.setdefault("homeassistant", ha)
    sys.modules.setdefault("homeassistant.helpers", helpers)
    sys.modules["homeassistant.helpers.device_registry"] = registry

    for name in ("const", "device_model.factory", "device_model.names"):
        path = PKG / (name.replace(".", "/") + ".py")
        spec = importlib.util.spec_from_file_location(
            f"custom_components.btdoor_security_plus.{name}", path
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)

    return (
        sys.modules["custom_components.btdoor_security_plus.device_model.factory"],
        sys.modules["custom_components.btdoor_security_plus.device_model.names"],
    )


def test_italian_device_names_are_localized() -> None:
    factory, names = _load_modules()
    assert names.device_name(factory.DeviceKind.CLOUD, "it") == "Stato Cloud"
    assert names.device_name(factory.DeviceKind.SIP, "it") == "Monitor SIP"
    assert names.device_name(factory.DeviceKind.DIALOG, "it") == "Monitor Chiamate"
    assert names.device_name(factory.DeviceKind.MEDIA, "it") == "Monitor Multimediale"
    assert names.device_name(factory.DeviceKind.DIAGNOSTICS, "it") == "Diagnostica Avanzata"


def test_language_normalization_and_fallback() -> None:
    _, names = _load_modules()
    assert names.normalize_language("it-IT") == "it"
    assert names.normalize_language("nl_NL") == "nl"
    assert names.normalize_language("pt-BR") == "en"
