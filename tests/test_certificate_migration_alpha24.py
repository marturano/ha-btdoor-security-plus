from pathlib import Path


def test_legacy_domain_is_a_certificate_migration_source() -> None:
    source = Path("custom_components/btdoor_security_plus/__init__.py").read_text(encoding="utf-8")
    assert '"custom_components", "btdoor_entry_plus", "certificate"' in source
    assert '"custom_components", "bticino_door_entry", "certificate"' in source


def test_health_isolated_from_strict_certificate_test() -> None:
    source = Path("custom_components/btdoor_security_plus/developer.py").read_text(encoding="utf-8")
    health = source.split("async def _test_health", 1)[1].split(
        "@staticmethod\n    def _directory_writable", 1
    )[0]
    assert "await self._certificate_status()" in health
    assert "await self._test_certificates()" not in health
    assert '"tls_runtime"' in health


def test_developer_diagnostics_use_runtime_certificate_paths() -> None:
    source = Path("custom_components/btdoor_security_plus/developer.py").read_text(encoding="utf-8")
    assert "def _runtime_certificate_paths" in source
    assert 'getattr(client, "client_cert_path", None)' in source
    assert 'getattr(client, "client_key_path", None)' in source
