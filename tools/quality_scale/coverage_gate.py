#!/usr/bin/env python3
"""Generate deterministic Quality Scale test-coverage evidence."""
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'docs/quality-scale/integration_coverage.raw.json'
OUT=ROOT/'docs/quality-scale/integration_coverage.json'
MD=ROOT/'docs/quality-scale/INTEGRATION_COVERAGE_REPORT.md'
THRESHOLD=95.0

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--measure',action='store_true'); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
    if args.measure:
        cmd=[sys.executable,'-m','pytest','--disable-warnings','-p','no:cacheprovider','--cov=custom_components/btdoor_security_plus',f'--cov-report=json:{RAW.relative_to(ROOT)}','--cov-report=term:skip-covered']
        result=subprocess.run(cmd,cwd=ROOT)
        if result.returncode: return result.returncode
    if not RAW.exists():
        print('Coverage input missing; run with --measure',file=sys.stderr); return 2
    raw=json.loads(RAW.read_text(encoding='utf-8'))
    total=raw.get('totals',{})
    percent=float(total.get('percent_covered',0.0))
    payload={'schema_version':1,'generated':date.today().isoformat(),'scope':'custom_components/btdoor_security_plus','threshold_percent':THRESHOLD,'measured_percent':round(percent,2),'covered_lines':total.get('covered_lines',0),'missing_lines':total.get('missing_lines',0),'num_statements':total.get('num_statements',0),'status':'VALIDATED' if percent>THRESHOLD else 'BELOW_THRESHOLD','source':'pytest-cov JSON report','raw_report':str(RAW.relative_to(ROOT))}
    OUT.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    MD.write_text('# Integration Coverage Report\n\n'+f"- Measured coverage: **{payload['measured_percent']}%**\n- Silver threshold: **above {THRESHOLD}%**\n- Status: **{payload['status']}**\n- Statements: {payload['num_statements']}\n- Covered lines: {payload['covered_lines']}\n- Missing lines: {payload['missing_lines']}\n\nThis is measured evidence, not an estimated score. The Silver rule remains open while the threshold is not exceeded.\n",encoding='utf-8')
    print(f"Coverage {payload['measured_percent']}% | {payload['status']}")
    return 1 if args.check and payload['status']!='VALIDATED' else 0
if __name__=='__main__': raise SystemExit(main())
