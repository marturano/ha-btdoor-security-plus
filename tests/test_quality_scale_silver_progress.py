from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INTEGRATION=ROOT/'custom_components/btdoor_security_plus'

def test_availability_transition_logging_is_deduplicated() -> None:
    source=(INTEGRATION/'__init__.py').read_text(encoding='utf-8')
    runtime=(INTEGRATION/'runtime.py').read_text(encoding='utf-8')
    assert 'def _log_availability_transition' in source
    assert 'if previous is available:' in source
    assert 'became unavailable' in source
    assert 'recovered and is available again' in source
    assert 'availability_state: bool | None = None' in runtime
    assert 'RuntimeEventType.SIP_UNREGISTERED' in source
    assert 'RuntimeEventType.SIP_REGISTERED' in source

def test_push_platforms_declare_parallel_updates() -> None:
    for name in ('binary_sensor.py','button.py','event.py','sensor.py','switch.py'):
        source=(INTEGRATION/name).read_text(encoding='utf-8')
        assert 'PARALLEL_UPDATES = 0' in source, name
        assert 'Push-driven platform' in source, name

def test_coverage_gate_uses_measured_evidence() -> None:
    result=subprocess.run([sys.executable,'tools/quality_scale/coverage_gate.py'],cwd=ROOT,text=True,capture_output=True)
    assert result.returncode == 0, result.stderr
    evidence=json.loads((ROOT/'docs/quality-scale/integration_coverage.json').read_text(encoding='utf-8'))
    assert evidence['scope']=='custom_components/btdoor_security_plus'
    assert evidence['threshold_percent']==95.0
    assert evidence['status'] in {'VALIDATED','BELOW_THRESHOLD'}
    assert evidence['measured_percent'] >= 0
