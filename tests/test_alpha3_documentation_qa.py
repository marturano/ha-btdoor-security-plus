from pathlib import Path
import json
import yaml

ROOT=Path(__file__).resolve().parents[1]
PKG=ROOT/"custom_components/btdoor_security_plus"

def test_version_is_current_release_candidate():
    assert json.loads((PKG/"manifest.json").read_text())["version"] == "1.1.0-rc.15"

def test_document_manifest_has_six_locales_and_required_sections():
    data=yaml.safe_load((ROOT/"docs/document_manifest.yaml").read_text())
    assert data["supported_locales"] == ["en","it","fr","de","es","nl"]
    assert len(data["required_documents"]) >= 8
    for lang in data["supported_locales"]:
        for rel in data["required_documents"]:
            assert (ROOT/"docs"/lang/rel).exists(), (lang,rel)

def test_area_report_contract_is_observable_and_policy_aware():
    source=(PKG/"models/device.py").read_text()
    assert "devices_with_area" in source
    assert "devices_without_area" in source
    assert "integration_assigns_areas" in source
    manager=(PKG/"managers/device_manager.py").read_text()
    assert "integration_assigns_areas=False" in manager
    assert "automatic_areas_assigned=False" in manager

def test_italian_open_gate_service_translation_present():
    data=json.loads((PKG/"translations/it.json").read_text())
    assert data["services"]["open_gate"]["name"] == "Apri cancello"
