import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "custom_components" / "btdoor_security_plus"


def _load_sanitizer():
    package = ModuleType("btdoor_hotfix_test")
    package.__path__ = [str(PACKAGE_DIR)]
    sys.modules[package.__name__] = package
    for name in ("support_debug", "support_sanitizer"):
        full_name = f"{package.__name__}.{name}"
        spec = spec_from_file_location(full_name, PACKAGE_DIR / f"{name}.py")
        module = module_from_spec(spec)
        sys.modules[full_name] = module
        assert spec and spec.loader
        spec.loader.exec_module(module)
    return sys.modules[f"{package.__name__}.support_sanitizer"]


def test_support_export_masks_persistent_ids_and_certificate_paths():
    module = _load_sanitizer()
    result = module.sanitize_export_data(
        {
            "plant_id": "5617397",
            "id_device": "5bf91ddf146d",
            "client_cert_path": "/config/custom_components/btdoor_security_plus/certificate/2621300/client-cert.pem",
            "client_key_path": "/config/custom_components/btdoor_security_plus/certificate/2621300/client-key.pem",
            "ca_chain_path": "/config/custom_components/btdoor_security_plus/certificate/2621300/ca-chain.pem",
        }
    )
    assert result["plant_id"].startswith("[HASH:")
    assert result["id_device"].startswith("[HASH:")
    assert result["client_cert_path"] == "[REDACTED]"
    assert result["client_key_path"] == "[REDACTED]"
    assert result["ca_chain_path"] == "[REDACTED]"
