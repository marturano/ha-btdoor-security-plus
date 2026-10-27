import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType, SimpleNamespace

import yaml

ROOT = Path(__file__).resolve().parents[1]
UX = ROOT / "custom_components" / "btdoor_security_plus" / "ux"


def _load_ux_modules():
    package = ModuleType("btdoor_ux_test")
    package.__path__ = [str(UX)]
    sys.modules[package.__name__] = package
    modules = {}
    for name in ("entity_resolver", "dashboard_builder"):
        full_name = f"{package.__name__}.{name}"
        spec = spec_from_file_location(full_name, UX / f"{name}.py")
        module = module_from_spec(spec)
        sys.modules[full_name] = module
        assert spec and spec.loader
        spec.loader.exec_module(module)
        modules[name] = module
    return modules


MODULES = _load_ux_modules()
DashboardEntityResolver = MODULES["entity_resolver"].DashboardEntityResolver
DashboardBuilder = MODULES["dashboard_builder"].DashboardBuilder


def test_entity_resolver_uses_unique_ids_not_entity_names():
    entries = [
        SimpleNamespace(
            config_entry_id="entry",
            unique_id="gateway_open_gate_button",
            entity_id="button.custom_gate",
        ),
        SimpleNamespace(
            config_entry_id="entry",
            unique_id="gateway_sip_registered",
            entity_id="binary_sensor.custom_sip",
        ),
        SimpleNamespace(
            config_entry_id="other", unique_id="gateway_runtime_score", entity_id="sensor.other"
        ),
    ]
    result = DashboardEntityResolver.resolve(entries, config_entry_id="entry")
    assert result.open_gate == "button.custom_gate"
    assert result.sip_registered == "binary_sensor.custom_sip"
    assert result.runtime_score is None


def test_dashboard_builder_requires_gate_confirmation():
    entries = [
        SimpleNamespace(
            config_entry_id="entry", unique_id=f"gateway{suffix}", entity_id=f"sensor.{key}"
        )
        for key, suffix in {
            "open_gate": "_open_gate_button",
            "sip_registered": "_sip_registered",
            "cloud_connected": "_cloud_connected",
            "ringing": "_ringing",
            "call_state": "_call_state",
            "last_caller": "_last_caller",
            "last_gate_open": "_last_gate_open",
            "runtime_score": "_runtime_score",
            "runtime_healthy": "_runtime_healthy",
        }.items()
    ]
    entity_map = DashboardEntityResolver.resolve(entries, config_entry_id="entry")
    result = DashboardBuilder(ROOT / "dashboards" / "templates").build(
        "user-dashboard.yaml", entity_map
    )
    data = yaml.safe_load(result.content)
    button = data["views"][0]["cards"][1]
    assert button["tap_action"]["confirmation"]["text"]
    assert button["tap_action"]["action"] == "perform-action"
    assert button["tap_action"]["perform_action"] == "button.press"
    assert button["tap_action"]["target"]["entity_id"] == "sensor.open_gate"
    assert "btdoor_template_" not in result.content


def test_blueprint_catalog_and_files_are_valid_yaml():
    catalog = yaml.safe_load((ROOT / "blueprints" / "catalog.yaml").read_text())
    assert len(catalog["blueprints"]) >= 6
    for item in catalog["blueprints"]:
        path = ROOT / "blueprints" / item["path"]
        assert path.exists()
        text = path.read_text()
        assert "blueprint:" in text
        assert "min_version: 2026.7.0" in text


def test_area_report_uses_observable_semantics():
    model = (
        ROOT / "custom_components" / "btdoor_security_plus" / "models" / "device.py"
    ).read_text()
    manager = (
        ROOT / "custom_components" / "btdoor_security_plus" / "managers" / "device_manager.py"
    ).read_text()
    assert "integration_assigns_areas" in model
    assert "integration_suggested_areas" in model
    assert "integration_assigns_areas=False" in manager
    assert "automatic_areas_assigned=False" in manager


def test_raw_dashboard_templates_use_valid_entity_ids():
    """Source templates must be safe if a user imports them without the builder."""
    import re

    entity_id = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")
    for template_name in ("user-dashboard.yaml", "mobile-dashboard.yaml"):
        yaml.safe_load((ROOT / "dashboards" / "templates" / template_name).read_text())
        text = (ROOT / "dashboards" / "templates" / template_name).read_text()
        assert "__ENTITY_" not in text
        for match in re.findall(r"(?:entity:|entity_id:)\s*([a-zA-Z0-9_.-]+)", text):
            assert entity_id.fullmatch(match), f"Invalid entity ID {match} in {template_name}"


def test_dashboard_builder_recursively_replaces_legacy_tokens(tmp_path):
    template = tmp_path / "stored-dashboard.yaml"
    template.write_text(
        """
views:
  - cards:
      - entity: __ENTITY_OPEN_GATE__
        tap_action:
          action: perform-action
          perform_action: button.press
          target:
            entity_id: __ENTITY_OPEN_GATE__
      - entities:
          - entity: __ENTITY_RINGING__
          - entity: __ENTITY_CALL_STATE__
          - entity: __ENTITY_LAST_CALLER__
          - entity: __ENTITY_LAST_GATE_OPEN__
      - conditions:
          - entity: __ENTITY_RINGING__
            state: 'on'
      - custom:
          __ENTITY_OPEN_GATE__: __ENTITY_CALL_STATE__
""",
        encoding="utf-8",
    )
    entity_map = MODULES["entity_resolver"].DashboardEntityMap(
        open_gate="cover.esterno_citofono_maria_cancello",
        ringing="binary_sensor.esterno_citofono_maria_chiamata_in_corso",
        call_state="sensor.esterno_citofono_maria_stato_chiamata",
        last_caller="sensor.esterno_citofono_maria_ultimo_chiamante",
        last_gate_open="sensor.esterno_citofono_maria_ultima_apertura",
    )

    result = DashboardBuilder(tmp_path).build(template.name, entity_map)
    data = yaml.safe_load(result.content)
    cards = data["views"][0]["cards"]

    assert cards[0]["entity"] == "cover.esterno_citofono_maria_cancello"
    assert cards[0]["tap_action"]["target"]["entity_id"] == "cover.esterno_citofono_maria_cancello"
    assert (
        cards[1]["entities"][0]["entity"]
        == "binary_sensor.esterno_citofono_maria_chiamata_in_corso"
    )
    assert (
        cards[2]["conditions"][0]["entity"]
        == "binary_sensor.esterno_citofono_maria_chiamata_in_corso"
    )
    assert (
        cards[3]["custom"]["cover.esterno_citofono_maria_cancello"]
        == "sensor.esterno_citofono_maria_stato_chiamata"
    )
    assert "__ENTITY_" not in result.content
    assert result.missing_entities == ()
