#!/usr/bin/env python3
from __future__ import annotations
import json, re
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REG=ROOT/'docs/i18n/language_registry.json'
OUT_JSON=ROOT/'docs/i18n/LOCALIZATION_REPORT.json'
OUT_MD=ROOT/'docs/i18n/LOCALIZATION_REPORT.md'
PH=re.compile(r'\{([A-Za-z0-9_]+)\}')
def flatten(v,p=''):
    out={}
    if isinstance(v,dict):
        for k,x in v.items(): out.update(flatten(x,f'{p}.{k}' if p else k))
    else: out[p]=v
    return out
def main()->int:
    reg=json.loads(REG.read_text(encoding='utf-8'))
    base_path=ROOT/reg['base_translation']; base=flatten(json.loads(base_path.read_text(encoding='utf-8')))
    results=[]; errors=[]
    for loc in reg['integration_locales']:
        path=ROOT/reg['translation_directory']/f'{loc}.json'
        item={'locale':loc,'file':str(path.relative_to(ROOT)),'status':'PASS','missing':[],'extra':[],'placeholder_errors':[],'empty':[]}
        if not path.exists():
            item['status']='FAIL'; item['missing_file']=True; errors.append(f'{loc}: missing file'); results.append(item); continue
        data=flatten(json.loads(path.read_text(encoding='utf-8')))
        item['missing']=sorted(set(base)-set(data)); item['extra']=sorted(set(data)-set(base))
        for k in sorted(set(base)&set(data)):
            if sorted(PH.findall(str(base[k])))!=sorted(PH.findall(str(data[k]))): item['placeholder_errors'].append(k)
            if isinstance(data[k],str) and not data[k].strip(): item['empty'].append(k)
        if item['missing'] or item['extra'] or item['placeholder_errors'] or item['empty']:
            item['status']='FAIL'; errors.append(f'{loc}: parity/placeholder/value failure')
        results.append(item)
    payload={'schema_version':1,'generated':date.today().isoformat(),'base_keys':len(base),'locales':results,'status':'PASS' if not errors else 'FAIL','errors':errors}
    OUT_JSON.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    lines=['# Localization Report','',f"**Generated:** {payload['generated']}",f"**Status:** **{payload['status']}**",f"**Base keys:** {len(base)}",'', '| Locale | Status | Missing | Extra | Placeholder | Empty |','|---|---:|---:|---:|---:|---:|']
    for x in results: lines.append(f"| {x['locale']} | {x['status']} | {len(x['missing'])} | {len(x['extra'])} | {len(x['placeholder_errors'])} | {len(x['empty'])} |")
    OUT_MD.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f"Localization framework: {payload['status']} ({len(results)} locales, {len(base)} keys)")
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
