from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "btdoor_security_plus"


def _load_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_runtime_summary_maps_every_field() -> None:
    module = _load_file("qs1_runtime_summary", COMPONENT / "analysis" / "runtime_summary.py")
    snapshot = SimpleNamespace(
        diagnostics=SimpleNamespace(status="degraded", score=73, issues=("sip",)),
        gateway=SimpleNamespace(gateway_name=None, device_name="Door"),
        cloud=SimpleNamespace(connected=True, status="online"),
        sip=SimpleNamespace(registered=False, status="retrying"),
        dialog=SimpleNamespace(state="idle", call_state=None, caller=None),
        media=SimpleNamespace(
            state="stopped",
            ready=False,
            audio_codec="PCMU",
            video_codec=None,
            srtp_suite=None,
            duration_seconds=1.5,
            close_reason="normal",
        ),
    )
    summary = module.build_runtime_summary(SimpleNamespace(snapshot=lambda: snapshot))
    assert summary.gateway_name == "Door"
    assert summary.health_score == 73
    assert summary.warnings == ("sip",)
    assert summary.as_dict()["audio_codec"] == "PCMU"


def test_visibility_policy_all_branches(monkeypatch) -> None:
    package = types.ModuleType("custom_components.btdoor_security_plus")
    package.__path__ = [str(COMPONENT)]
    visibility_pkg = types.ModuleType("custom_components.btdoor_security_plus.visibility")
    visibility_pkg.__path__ = [str(COMPONENT / "visibility")]
    const = types.ModuleType("custom_components.btdoor_security_plus.const")
    values = {
        "CONF_DEVELOPER_MODE": "developer_mode",
        "CONF_QUICK_VOICE_GATE": "voice",
        "CONF_SHOW_ADVANCED_DIAGNOSTICS": "diag",
        "CONF_SHOW_CALL_MONITOR": "calls",
        "CONF_SHOW_CLOUD_STATUS": "cloud",
        "CONF_SHOW_MEDIA_MONITOR": "media",
        "CONF_SHOW_SIP_MONITOR": "sip",
        "DEFAULT_DEVELOPER_MODE": False,
        "DEFAULT_QUICK_VOICE_GATE": False,
        "DEFAULT_SHOW_ADVANCED_DIAGNOSTICS": True,
        "DEFAULT_SHOW_CALL_MONITOR": True,
        "DEFAULT_SHOW_CLOUD_STATUS": True,
        "DEFAULT_SHOW_MEDIA_MONITOR": True,
        "DEFAULT_SHOW_SIP_MONITOR": True,
    }
    for key, value in values.items():
        setattr(const, key, value)
    factory = types.ModuleType("custom_components.btdoor_security_plus.device_model.factory")
    from enum import Enum

    class DeviceKind(Enum):
        GATEWAY = "gateway"
        CLOUD = "cloud"
        SIP = "sip"
        DIALOG = "dialog"
        MEDIA = "media"
        DIAGNOSTICS = "diagnostics"
        VOICE_BRIDGE = "voice"

    factory.DeviceKind = DeviceKind
    monkeypatch.setitem(sys.modules, package.__name__, package)
    monkeypatch.setitem(sys.modules, visibility_pkg.__name__, visibility_pkg)
    monkeypatch.setitem(sys.modules, const.__name__, const)
    monkeypatch.setitem(sys.modules, factory.__name__, factory)
    module = _load_file(
        "custom_components.btdoor_security_plus.visibility.manager",
        COMPONENT / "visibility" / "manager.py",
    )

    default = module.visibility_for_entry(SimpleNamespace(options={}))
    assert default.is_visible(DeviceKind.GATEWAY)
    assert default.as_dict()["sip_monitor"] is True
    disabled = module.DeviceVisibilityManager.from_entry(SimpleNamespace(options={"diag": True}))
    enabled = module.DeviceVisibilityManager.from_entry(
        SimpleNamespace(options={"developer_mode": True, "diag": True, "voice": True})
    )
    assert disabled.diagnostics is False
    assert enabled.diagnostics is True
    assert enabled.is_visible(DeviceKind.VOICE_BRIDGE)
    hidden = module.DeviceVisibilityManager(False, False, False, False, False, False)
    gateway = SimpleNamespace(_device_kind=DeviceKind.GATEWAY)
    cloud = SimpleNamespace(_device_kind=DeviceKind.CLOUD)
    assert hidden.filter_entities([gateway, cloud]) == [gateway]


def test_dashboard_manager_resolve_and_build(monkeypatch, tmp_path: Path) -> None:
    package = types.ModuleType("custom_components.btdoor_security_plus")
    package.__path__ = [str(COMPONENT)]
    managers = types.ModuleType("custom_components.btdoor_security_plus.managers")
    managers.__path__ = [str(COMPONENT / "managers")]
    ux = types.ModuleType("custom_components.btdoor_security_plus.ux")

    class Builder:
        def __init__(self, template_dir):
            self.template_dir = template_dir

        def build(self, name, entities):
            return {"name": name, "entities": entities}

    ux.DashboardBuilder = Builder
    ux.DashboardEntityResolver = SimpleNamespace(
        resolve=lambda values, config_entry_id: {
            "count": len(list(values)),
            "entry": config_entry_id,
        }
    )
    ha = types.ModuleType("homeassistant")
    helpers = types.ModuleType("homeassistant.helpers")
    er = types.ModuleType("homeassistant.helpers.entity_registry")
    er.async_get = lambda hass: SimpleNamespace(entities={"one": object()})
    monkeypatch.setitem(sys.modules, package.__name__, package)
    monkeypatch.setitem(sys.modules, managers.__name__, managers)
    monkeypatch.setitem(sys.modules, ux.__name__, ux)
    monkeypatch.setitem(sys.modules, ha.__name__, ha)
    monkeypatch.setitem(sys.modules, helpers.__name__, helpers)
    monkeypatch.setitem(sys.modules, er.__name__, er)
    module = _load_file(
        "custom_components.btdoor_security_plus.managers.dashboard_manager",
        COMPONENT / "managers" / "dashboard_manager.py",
    )
    manager = module.DashboardManager(object(), SimpleNamespace(entry_id="entry-1"), tmp_path)
    assert manager.resolve_entities() == {"count": 1, "entry": "entry-1"}
    assert manager.build("main") == {"name": "main", "entities": {"count": 1, "entry": "entry-1"}}
