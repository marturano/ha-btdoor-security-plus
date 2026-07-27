#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "governance"))
from common import ROOT, CheckResult, exists, read


def version() -> str:
    manifest=json.loads(read('custom_components/btdoor_security_plus/manifest.json'))
    return manifest.get('version','')

def run(target: str | None=None) -> CheckResult:
    current=version(); target=target or current
    required=[
        'CHANGELOG.md', 'docs/release/RELEASE_CHECKLIST.md',
        'docs/validation/VALIDATION_REGISTER.md',
        f'docs/release/{target}.md', f'docs/validation/VALIDATION_REPORT_{target}.md',
    ]
    errors=[f'Missing {rel}' for rel in required if not exists(rel)]
    warnings=[]
    const=read('custom_components/btdoor_security_plus/const.py')
    match=re.search(r'INTEGRATION_VERSION\s*=\s*["\']([^"\']+)', const)
    if current != target: errors.append(f'manifest version {current} != target {target}')
    if not match or match.group(1) != target: errors.append('const.py version does not match target')
    if target.endswith('Final') or re.fullmatch(r'\d+\.\d+\.\d+', target):
        pub='docs/repository/validations/1.1.0-final.md'
        if not exists(pub): errors.append(f'Missing {pub}')
        else:
            text=read(pub).lower()
            if 'not started' in text or 'pending' in text: warnings.append('Final publication validation is not complete.')
    return CheckResult('release_readiness', 'PASS' if not errors else 'FAIL', errors, warnings, required)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--target'); ap.add_argument('--json',action='store_true'); a=ap.parse_args(); r=run(a.target)
    print(json.dumps(r.to_dict(),indent=2) if a.json else f'[{r.status}] release_readiness\n'+'\n'.join(f'  ERROR: {x}' for x in r.errors)+'\n'+'\n'.join(f'  WARN: {x}' for x in r.warnings))
    return 0 if r.passed else 1
if __name__=='__main__': raise SystemExit(main())
