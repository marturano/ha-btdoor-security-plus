from __future__ import annotations
import importlib.util, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('release_pipeline', ROOT/'tools/distribution/release_pipeline.py')
MOD=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MOD)

def test_release_pipeline_structural_check_passes():
    result=MOD.inspect()
    assert result['structural_status']=='PASS'
    assert result['version']=='1.1.0-rc.15'
    assert result['publication_status'] in {'READY','BLOCKED'}

def test_candidate_build_is_inventoried_and_verified(tmp_path, monkeypatch):
    monkeypatch.setattr(MOD,'OUT_DIR',tmp_path)
    result=MOD.build(force=True)
    assert result['candidate_only'] is True
    artifact=ROOT/result['artifact'] if not Path(result['artifact']).is_absolute() else Path(result['artifact'])
    artifact=tmp_path/Path(result['artifact']).name
    assert artifact.is_file()
    with zipfile.ZipFile(artifact) as zf:
        assert 'custom_components/btdoor_security_plus/manifest.json' in zf.namelist()
    verify=MOD.verify(artifact)
    assert verify['status']=='PASS', verify

def test_normal_build_respects_publication_gate(tmp_path, monkeypatch):
    monkeypatch.setattr(MOD,'OUT_DIR',tmp_path)
    status=MOD.inspect()['publication_status']
    if status=='BLOCKED':
        import pytest
        with pytest.raises(RuntimeError): MOD.build(force=False)
