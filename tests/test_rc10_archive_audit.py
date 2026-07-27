from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_rc15_version_alignment():
    manifest = json.loads((ROOT / 'custom_components/btdoor_security_plus/manifest.json').read_text())
    const = (ROOT / 'custom_components/btdoor_security_plus/const.py').read_text()
    assert manifest['version'] == '1.1.0-rc.15'
    assert 'INTEGRATION_VERSION = "1.1.0-rc.15"' in const


def test_archive_removed_and_cleanup_audit_present():
    assert not (ROOT / 'docs/archive').exists()
    assert (ROOT / 'docs/engineering/REPOSITORY_CLEANUP_AUDIT_2026-07-22.md').is_file()
    assert (ROOT / 'docs/validation/VALIDATION_REGISTER.md').is_file()


def test_certificate_blueprint_gap_is_preserved_in_current_project_records():
    content = ''.join(p.read_text(errors='ignore') for p in (ROOT / 'docs').rglob('*.md'))
    assert 'certificate' in content.lower()
