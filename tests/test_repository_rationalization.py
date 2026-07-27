from __future__ import annotations
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_canonical_registry_paths_exist():
    data=json.loads((ROOT/'docs/project/canonical_documents.json').read_text())
    for area in data['areas']:
        assert (ROOT/area['canonical']).exists(), area['canonical']
        for path in area.get('derived',[]): assert (ROOT/path).exists(), path
def test_repository_rationalization_check_passes():
    result=subprocess.run(['python','tools/repository/analyze_repository.py','--check'],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0, result.stdout+result.stderr
