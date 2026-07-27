from __future__ import annotations
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_certification_artifacts_and_policy_exist():
    for rel in (
      'docs/certification/CERTIFICATION_POLICY.md',
      'docs/certification/BENCHMARK_PROTOCOL.md',
      'tools/certification/run_certification.py',
      'docs/adr/ADR-0060-runtime-and-release-certification.md'):
        assert (ROOT/rel).exists(), rel

def test_certification_framework_passes_and_final_remains_blocked():
    r=subprocess.run(['python','tools/certification/run_certification.py','--check'],cwd=ROOT,text=True,capture_output=True)
    assert r.returncode==0, r.stdout+r.stderr
    data=json.loads((ROOT/'docs/certification/release_certification.json').read_text())
    assert data['framework_status']=='PASS'
    assert data['decision']=='BLOCKED'
    assert data['blockers']

def test_certification_evidence_is_registered():
    data=json.loads((ROOT/'docs/quality/evidence_register.json').read_text())
    ids={e['id'] for e in data['evidence']}
    assert {'EV-CERT-001','EV-CERT-002','EV-CERT-003','EV-CERT-004'} <= ids
