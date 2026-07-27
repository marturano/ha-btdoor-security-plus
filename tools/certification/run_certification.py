#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, platform, re, subprocess, sys, time
from datetime import date, datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/certification'
REPORTS=OUT/'reports'

def write_json(name,data):
    p=OUT/name; p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); return p

def write_md(name,title,sections):
    lines=[f'# {title}','',f"**Generated:** {date.today().isoformat()}",'']
    for heading,body in sections:
        lines += [f'## {heading}','',body,'']
    p=REPORTS/name; p.write_text('\n'.join(lines),encoding='utf-8'); return p

def cmd(command,timeout=300):
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'; env['PYTEST_ADDOPTS']='-p no:cacheprovider'
    start=time.perf_counter(); p=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,env=env,timeout=timeout); elapsed=time.perf_counter()-start
    return {'command':' '.join(command),'exit_code':p.returncode,'duration_seconds':round(elapsed,3),'stdout_tail':'\n'.join(p.stdout.splitlines()[-20:]),'stderr_tail':'\n'.join(p.stderr.splitlines()[-20:])}

def environment():
    data={'schema_version':1,'generated':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),'system':platform.system(),'release':platform.release(),'machine':platform.machine(),'python':platform.python_version(),'processor_count':os.cpu_count(),'home_assistant_runtime':False,'scope':'repository-local'}
    return data

def runtime_certification():
    result=cmd([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests/test_governance_automation.py','tests/test_project_health_dashboard.py','tests/test_quality_release_intelligence.py','tests/test_repository_rationalization.py','tests/test_rc15_repository_integrity.py'],timeout=300)
    passed=result['exit_code']==0
    return {'schema_version':1,'generated':date.today().isoformat(),'scope':'repository-local test runtime','status':'VALIDATED' if passed else 'FAILED','home_assistant_target_status':'PENDING','measurements':result,'limitations':['No Home Assistant 2026.x instance was available.','CPU and memory deltas for integration setup, reload and sustained operation were not measured.']}

def compatibility():
    manifest=json.loads((ROOT/'custom_components/btdoor_security_plus/manifest.json').read_text())
    hacs=json.loads((ROOT/'hacs.json').read_text())
    required=['domain','name','version','config_flow','iot_class','requirements']
    checks=[]
    for k in required: checks.append({'check':f'manifest:{k}','pass':k in manifest})
    checks += [
      {'check':'domain_directory_match','pass':manifest.get('domain')=='btdoor_security_plus'},
      {'check':'version_is_rc15','pass':manifest.get('version')=='1.1.0-rc.15'},
      {'check':'requirements_pinned','pass':all('==' in x for x in manifest.get('requirements',[]))},
      {'check':'config_flow_present','pass':(ROOT/'custom_components/btdoor_security_plus/config_flow.py').exists()},
      {'check':'translations_present','pass':(ROOT/'custom_components/btdoor_security_plus/translations').is_dir()},
      {'check':'hacs_name_present','pass':bool(hacs.get('name'))},
    ]
    ok=all(x['pass'] for x in checks)
    return {'schema_version':1,'generated':date.today().isoformat(),'repository_status':'VALIDATED' if ok else 'FAILED','home_assistant_2026x_status':'PENDING','hacs_lifecycle_status':'PENDING','checks':checks,'limitations':['Clean install, upgrade, rollback and device/entity continuity require a real Home Assistant/HACS environment.']}

def security():
    text_ext={'.py','.json','.yaml','.yml','.md','.toml','.txt'}
    secret_patterns=[re.compile(r'(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["\'][^"\']{12,}["\']'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
    findings=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in text_ext or any(x in p.parts for x in {'.git','.pytest_cache','__pycache__'}): continue
        rel=str(p.relative_to(ROOT))
        if rel=='tools/certification/run_certification.py': continue
        try: text=p.read_text(encoding='utf-8')
        except UnicodeDecodeError: continue
        for pat in secret_patterns:
            if pat.search(text):
                matches=[m.group(0) for m in pat.finditer(text)]
                if rel=='custom_components/btdoor_security_plus/const.py' and all(('CONF_PASSWORD' in m or 'CONF_SIP_PASSWORD' in m or '"password"' in m or '"sip_password"' in m) for m in matches):
                    continue
                findings.append({'file':rel,'type':'possible_secret'})
        if p.suffix=='.py' and ('shell=True' in text or 'os.system(' in text): findings.append({'file':str(p.relative_to(ROOT)),'type':'shell_execution_review'})
    manifest=json.loads((ROOT/'custom_components/btdoor_security_plus/manifest.json').read_text())
    unpinned=[x for x in manifest.get('requirements',[]) if '==' not in x]
    status='VALIDATED' if not findings and not unpinned else 'REVIEW_REQUIRED'
    return {'schema_version':1,'generated':date.today().isoformat(),'repository_status':status,'target_runtime_status':'PENDING','possible_findings':findings,'unpinned_requirements':unpinned,'limitations':['Pattern scanning is not a substitute for dependency vulnerability scanning or target-runtime security review.']}

def ux():
    checks=[
      {'check':'dashboard_assets','pass':any((ROOT/'dashboards').rglob('*'))},
      {'check':'translations','pass':len(list((ROOT/'custom_components/btdoor_security_plus/translations').glob('*.json')))>=2},
      {'check':'translation_review','pass':(ROOT/'docs/i18n/TRANSLATION_REVIEW.md').exists()},
      {'check':'lovelace_guide','pass':(ROOT/'docs/automation-assets/LOVELACE_GUIDE.md').exists()},
      {'check':'accessibility_policy','pass':(ROOT/'docs/certification/UX_ACCESSIBILITY_CERTIFICATION.md').exists()},
    ]
    ok=all(x['pass'] for x in checks)
    return {'schema_version':1,'generated':date.today().isoformat(),'structural_status':'VALIDATED' if ok else 'FAILED','interactive_review_status':'PENDING','checks':checks,'limitations':['Contrast, keyboard navigation and screen-reader behavior were not exercised in a browser or Home Assistant frontend.']}

def latest_target_run():
    runs=ROOT/'docs/target-validation/runs'
    accepted=[]
    if runs.exists():
        for rp in runs.glob('*/result.json'):
            try:
                data=json.loads(rp.read_text(encoding='utf-8'))
            except (OSError,json.JSONDecodeError):
                continue
            if data.get('import_status')=='ACCEPTED':
                accepted.append((data.get('imported_at',''),rp,data))
    return max(accepted,key=lambda x:x[0]) if accepted else None

def apply_target_evidence(runtime,comp,sec,uxr):
    latest=latest_target_run()
    if not latest: return None
    _,path,data=latest
    sections=data.get('sections',{})
    if sections.get('runtime',{}).get('status')=='VALIDATED': runtime['home_assistant_target_status']='VALIDATED'
    if sections.get('compatibility',{}).get('status')=='VALIDATED': comp['home_assistant_2026x_status']='VALIDATED'
    if sections.get('hacs_lifecycle',{}).get('status')=='VALIDATED': comp['hacs_lifecycle_status']='VALIDATED'
    if sections.get('security',{}).get('status')=='VALIDATED': sec['target_runtime_status']='VALIDATED'
    if sections.get('ux_accessibility',{}).get('status')=='VALIDATED': uxr['interactive_review_status']='VALIDATED'
    return {'run_id':data.get('run_id'),'source':str(path.relative_to(ROOT)),'imported_at':data.get('imported_at')}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    REPORTS.mkdir(parents=True,exist_ok=True)
    env=environment(); runtime=runtime_certification(); comp=compatibility(); sec=security(); uxr=ux(); target_evidence=apply_target_evidence(runtime,comp,sec,uxr)
    write_json('certification_environment.json',env)
    write_json('runtime_certification.json',runtime)
    write_json('compatibility_certification.json',comp)
    write_json('security_certification.json',sec)
    write_json('ux_accessibility_certification.json',uxr)
    write_md('RUNTIME_CERTIFICATION_REPORT.md','Runtime Certification Report',[('Result',f"Repository-local runtime: **{runtime['status']}**\n\nHome Assistant target runtime: **{runtime['home_assistant_target_status']}**"),('Measurements',f"Command: `{runtime['measurements']['command']}`\n\nDuration: {runtime['measurements']['duration_seconds']} s\n\nExit code: {runtime['measurements']['exit_code']}"),('Limitations','\n'.join(f'- {x}' for x in runtime['limitations']))])
    write_md('COMPATIBILITY_CERTIFICATION_REPORT.md','Compatibility Certification Report',[('Result',f"Repository metadata: **{comp['repository_status']}**\n\nHome Assistant 2026.x: **{comp['home_assistant_2026x_status']}**\n\nHACS lifecycle: **{comp['hacs_lifecycle_status']}**"),('Checks','\n'.join(f"- {'PASS' if x['pass'] else 'FAIL'} — {x['check']}" for x in comp['checks'])),('Limitations','\n'.join(f'- {x}' for x in comp['limitations']))])
    write_md('SECURITY_CERTIFICATION_REPORT.md','Security Certification Report',[('Result',f"Repository scan: **{sec['repository_status']}**\n\nTarget runtime: **{sec['target_runtime_status']}**"),('Findings', '\n'.join(f"- {x['type']}: `{x['file']}`" for x in sec['possible_findings']) or '- None'),('Limitations','\n'.join(f'- {x}' for x in sec['limitations']))])
    write_md('UX_ACCESSIBILITY_CERTIFICATION_REPORT.md','UX and Accessibility Certification Report',[('Result',f"Structural review: **{uxr['structural_status']}**\n\nInteractive review: **{uxr['interactive_review_status']}**"),('Checks','\n'.join(f"- {'PASS' if x['pass'] else 'FAIL'} — {x['check']}" for x in uxr['checks'])),('Limitations','\n'.join(f'- {x}' for x in uxr['limitations']))])
    blockers=[]
    if runtime['home_assistant_target_status']!='VALIDATED': blockers.append('Home Assistant target runtime benchmark')
    if comp['home_assistant_2026x_status']!='VALIDATED': blockers.append('Home Assistant 2026.x compatibility lifecycle')
    if comp['hacs_lifecycle_status']!='VALIDATED': blockers.append('HACS install/update/rollback lifecycle')
    if sec['target_runtime_status']!='VALIDATED': blockers.append('Target runtime security review')
    if uxr['interactive_review_status']!='VALIDATED': blockers.append('Interactive UX/accessibility review')
    release={'schema_version':1,'generated':date.today().isoformat(),'target':'1.1.0 Final','framework_status':'PASS' if runtime['status']=='VALIDATED' and comp['repository_status']=='VALIDATED' and sec['repository_status'] in {'VALIDATED','REVIEW_REQUIRED'} and uxr['structural_status']=='VALIDATED' else 'FAIL','decision':'BLOCKED' if blockers else 'CERTIFIED','blockers':blockers,'target_evidence':target_evidence,'artifacts':['docs/certification/runtime_certification.json','docs/certification/compatibility_certification.json','docs/certification/security_certification.json','docs/certification/ux_accessibility_certification.json']}
    write_json('release_certification.json',release)
    write_md('RELEASE_CERTIFICATION_REPORT.md','Release Certification Report',[('Decision',f"**{release['decision']}**"),('Framework',f"Certification framework status: **{release['framework_status']}**"),('Blocking target evidence','\n'.join(f'- {x}' for x in blockers) or '- None'),('Interpretation','A BLOCKED decision is expected until target Home Assistant, HACS, security and interactive UX evidence is collected.')])
    payload={'environment':env,'runtime':runtime,'compatibility':comp,'security':sec,'ux_accessibility':uxr,'release':release}
    if args.json: print(json.dumps(payload,indent=2,ensure_ascii=False))
    else:
        print(f"Certification framework: {release['framework_status']}")
        print(f"Final certification: {release['decision']}")
        print(f"Blockers: {len(blockers)}")
    return 1 if args.check and release['framework_status']!='PASS' else 0
if __name__=='__main__': raise SystemExit(main())
