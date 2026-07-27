#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, subprocess, sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/'docs/validation/governance-automation-report.json'
CHECKS=[
 ('project_impact',['python','tools/governance/check_project_impact.py','--json']),
 ('handoff_synchronization',['python','tools/handoff/sync_handoff.py','--check','--json']),
 ('governance',['python','tools/governance/check_governance.py','--json']),
 ('handoff',['python','tools/handoff/check_handoff.py','--json']),
 ('release_readiness',['python','tools/release/check_release_readiness.py','--json']),
 ('repository_integrity',['python','tools/check_repository_integrity.py','--json']),
 ('repository_rationalization',['python','tools/repository/analyze_repository.py','--check','--json']),
 ('quality_intelligence',['python','tools/evidence/quality_intelligence.py','--check','--json']),
 ('target_validation_pack',['python','tools/target_validation/target_validation.py','latest']),
 ('release_pipeline_distribution',['python','tools/distribution/release_pipeline.py','check']),
 ('repository_production_audit',['python','tools/audit/production_audit.py','--check','--json']),
 ('home_assistant_certification',['python','tools/home_assistant_certification/ha_certification.py','status']),
 ('home_assistant_quality_scale_workflow',['python','tools/quality_scale/quality_scale_workflow.py','run']),
 ('runtime_release_certification',['python','tools/certification/run_certification.py','--check','--json']),
 ('decision_traceability',['python','tools/traceability/build_traceability.py','--check']),
 ('release_decision',['python','tools/release/release_decision.py','--json']),
 ('health',['python','tools/health/calculate_health.py','--check']),
 ('repository_hygiene',['python','tools/check_orphans.py']),
]

def run_command(name,cmd):
    if name == 'repository_hygiene':
        for rel in ('ha-certification-work','target-validation-work'):
            path=ROOT/rel
            if path.exists() and path.is_dir() and not any(path.iterdir()):
                path.rmdir()
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,env=env)
    parsed=None
    if '--json' in cmd:
        try: parsed=json.loads(p.stdout)
        except json.JSONDecodeError: parsed=None
    return {'name':name,'status':'PASS' if p.returncode==0 else 'FAIL','returncode':p.returncode,'command':' '.join(cmd),'result':parsed,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); ap.add_argument('--no-report',action='store_true'); args=ap.parse_args()
    results=[run_command(n,c) for n,c in CHECKS]
    payload={'schema_version':1,'generated':date.today().isoformat(),'results':results,'overall':'PASS' if all(r['status']=='PASS' for r in results) else 'FAIL'}
    if not args.no_report:
        REPORT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    if args.json: print(json.dumps(payload,indent=2,ensure_ascii=False))
    else:
        for r in results: print(f"[{r['status']}] {r['name']}")
        print(f"Overall: {payload['overall']}")
    return 0 if payload['overall']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
