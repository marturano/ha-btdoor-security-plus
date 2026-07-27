#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'docs/quality/decision_traceability.json'; OUT=ROOT/'docs/quality/DECISION_TRACEABILITY.md'
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
    data=json.loads(SRC.read_text(encoding='utf-8')); missing=[]
    rows=['# Decision Traceability','',f"**Generated:** {date.today().isoformat()}",'','| Decision | ADR | Roadmap | CHANGELOG | Engineering Notebook | Release evidence |','|---|---|---|---|---|---|']
    for item in data['links']:
        for k,v in item.items():
            if k!='decision' and not (ROOT/v).exists(): missing.append(v)
        rows.append('| '+item['decision']+' | '+' | '.join(f'`{item[k]}`' for k in ('adr','roadmap','changelog','notebook','release'))+' |')
    rows += ['', '## Rule','', 'Every material decision must be traceable from its ADR or decision record to roadmap intent, implementation notes, user-visible change history and release evidence.']
    OUT.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print('Decision traceability: '+('PASS' if not missing else 'FAIL'))
    return 1 if args.check and missing else 0
if __name__=='__main__': raise SystemExit(main())
