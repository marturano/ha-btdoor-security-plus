#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOCALES=('en','it','fr','de','es','nl')
RELEASE='1.1.0-rc.15'

def result(name, errors): return {'gate':name,'status':'PASS' if not errors else 'FAIL','errors':errors}
def roadmap():
    errors=[]; seen={}
    idx=ROOT/'docs/roadmap/ROADMAP.md'
    if not idx.exists(): errors.append('Missing ROADMAP.md'); return result('roadmap',errors)
    for p in sorted((ROOT/'docs/roadmap').glob('ROADMAP_[1-5]X.md')):
        nums=[]
        for line in p.read_text(encoding='utf-8').splitlines():
            m=re.match(r'^##\s+(\d+\.\d+)\s+[—-]\s+(.+)$',line)
            if m:
                ident,title=m.groups(); nums.append(tuple(map(int,ident.split('.'))))
                if ident in seen: errors.append(f'Duplicate milestone {ident}: {seen[ident]} and {p.name}')
                seen[ident]=p.name
                if not title.strip(): errors.append(f'Empty milestone title {ident}')
        if nums != sorted(nums): errors.append(f'Out-of-order milestones in {p.name}')
    return result('roadmap',errors)
def documentation():
    req=['README.md','PROJECT_MANIFEST.md','docs/project/PROJECT_CONSTITUTION.md','PROJECT_VISION.md','docs/repository/REPOSITORY_POLICY.md','docs/index.md','docs/release/DOCUMENTATION_CHANGELOG.md','docs/quality/README.md']
    return result('documentation',[f'Missing {x}' for x in req if not (ROOT/x).exists()])
def translation():
    errors=[]
    for loc in LOCALES:
        for rel in [f'docs/{loc}/index.md',f'docs/{loc}/release/{RELEASE}.md',f'custom_components/btdoor_security_plus/translations/{loc}.json']:
            if not (ROOT/rel).exists(): errors.append(f'Missing {rel}')
    return result('translation',errors)
def adr():
    errors=[]; files=sorted((ROOT/'docs/adr').glob('ADR-*.md')); ids=[]
    for p in files:
        m=re.match(r'ADR-(\d{4})-',p.name)
        if not m: errors.append(f'Invalid ADR filename {p.name}'); continue
        ids.append(int(m.group(1)))
        text=p.read_text(encoding='utf-8')
        if not re.search(r'Status', '\n'.join(text.splitlines()[:12]), re.I): errors.append(f'Missing Status in {p.name}')
    if len(ids)!=len(set(ids)): errors.append('Duplicate ADR identifiers')
    return result('adr',errors)
def structure():
    req=['custom_components/btdoor_security_plus','docs','handoff','tests','tools']
    errors=[f'Missing {x}' for x in req if not (ROOT/x).exists()]
    if (ROOT/'.pytest_cache').exists(): errors.append('Forbidden root .pytest_cache directory')
    return result('repository_structure',errors)
def links():
    errors=[]
    pat=re.compile(r'\[[^\]]+\]\(([^)]+)\)')
    for p in list((ROOT/'docs').rglob('*.md'))+list((ROOT/'handoff').rglob('*.md')):
        if '/archive/' in p.as_posix(): continue
        for target in pat.findall(p.read_text(encoding='utf-8')):
            if target.startswith(('http://','https://','#','mailto:')): continue
            clean=target.split('#',1)[0]
            if clean and not (p.parent/clean).resolve().exists(): errors.append(f'{p.relative_to(ROOT)} -> {target}')
    return result('links',errors)
def handoff():
    req=['handoff/00_PROJECT_EXECUTION_CONTRACT.md','handoff/01_PROJECT_MEMORY.md','handoff/17_CONTINUITY_STATUS.md','handoff/18_INTEGRITY_SUITE_RESULTS.md','handoff/19_GOVERNANCE_STATUS.md','handoff/CONTINUITY_CHECKLIST.md','handoff/16_RECOVERY_PROMPT.md','handoff/HANDOFF_INDEX.md']
    errors=[f'Missing {x}' for x in req if not (ROOT/x).exists()]
    for x in req:
        p=ROOT/x
        if p.exists() and x not in ('handoff/00_PROJECT_EXECUTION_CONTRACT.md','handoff/01_PROJECT_MEMORY.md','handoff/CONTINUITY_CHECKLIST.md','handoff/HANDOFF_INDEX.md') and RELEASE not in p.read_text(encoding='utf-8'): errors.append(f'Stale release in {x}')
    return result('handoff',errors)
def compatibility():
    req=['docs/compatibility/COMPATIBILITY_MATRIX.md','docs/compatibility/DEVICE_COMPATIBILITY_MATRIX.md','docs/compatibility/HOME_ASSISTANT.md','docs/compatibility/VOICE_ASSISTANT_MATRIX.md']
    return result('compatibility',[f'Missing {x}' for x in req if not (ROOT/x).exists()])
def release():
    req=['CHANGELOG.md',f'docs/release/{RELEASE}.md',f'docs/validation/VALIDATION_REPORT_{RELEASE}.md','docs/release/RELEASE_CHECKLIST.md','docs/release/DOCUMENTATION_CHANGELOG.md']
    errors=[f'Missing {x}' for x in req if not (ROOT/x).exists()]
    values=[]
    values.append(json.loads((ROOT/'custom_components/btdoor_security_plus/manifest.json').read_text())['version'])
    m=re.search(r'INTEGRATION_VERSION\s*=\s*"([^"]+)"',(ROOT/'custom_components/btdoor_security_plus/const.py').read_text())
    values.append(m.group(1) if m else 'missing')
    if any(v!=RELEASE for v in values): errors.append(f'Version mismatch: {values}')
    return result('release_completeness',errors)
def api():
    errors=[]
    req=['docs/api/README.md','docs/api/ENTITIES.md','docs/api/EVENTS.md','docs/api/SERVICES.md','docs/api/ERRORS.md','docs/api/VERSIONING.md','docs/api/SECURITY.md','docs/api/VOICE_ASSISTANTS.md','docs/api/AUTOMATION_EXAMPLES.md','docs/api/REST.md','docs/api/WEBSOCKET.md']
    index=(ROOT/'docs/api/README.md').read_text(encoding='utf-8') if (ROOT/'docs/api/README.md').exists() else ''
    for rel in req:
        target=ROOT/rel
        if not target.exists(): errors.append(f'Missing {rel}')
        elif rel!='docs/api/README.md' and Path(rel).name not in index: errors.append(f'API index omits {Path(rel).name}')
    services=(ROOT/'custom_components/btdoor_security_plus/services.yaml').read_text(encoding='utf-8')
    docs=(ROOT/'docs/api/SERVICES.md').read_text(encoding='utf-8') if (ROOT/'docs/api/SERVICES.md').exists() else ''
    for name in re.findall(r'^([a-z][a-z0-9_]+):\s*$',services,re.M):
        if f'`{name}`' not in docs: errors.append(f'SERVICES.md omits {name}')
    events=(ROOT/'docs/api/EVENTS.md').read_text(encoding='utf-8') if (ROOT/'docs/api/EVENTS.md').exists() else ''
    for name in ('btdoor_security_plus_event','gate_open_requested','gate_open_succeeded','gate_open_failed','schema_version'):
        if name not in events: errors.append(f'EVENTS.md omits {name}')
    return result('api',errors)

def voice_assistant_api():
    errors=[]
    path=ROOT/'docs/api/VOICE_ASSISTANTS.md'
    text=path.read_text(encoding='utf-8') if path.exists() else ''
    for marker in ('Alexa','Alexa+','Google Assistant','Home Assistant','Security expectations','Validation checklist'):
        if marker not in text: errors.append(f'Voice assistant API missing {marker}')
    matrix=ROOT/'docs/compatibility/VOICE_ASSISTANT_MATRIX.md'
    if not matrix.exists(): errors.append('Missing voice assistant compatibility matrix')
    return result('voice_assistant_api',errors)

def architecture():
    errors=[]
    base=ROOT/'docs/architecture'
    required=['README.md','SYSTEM_ARCHITECTURE.md','CORE_RUNTIME.md','LIFECYCLE_AND_ISOLATION.md','CONFIG_ENTRY_MODEL.md','DATA_FLOW.md','MODULE_BOUNDARIES.md','DEVICE_MODEL.md','ENTITY_MODEL.md','SERVICE_MODEL.md','EVENT_MODEL.md','EVENT_BUS.md','MEDIA_PIPELINE.md','VOICE_PIPELINE.md','NOTIFICATION_PIPELINE.md','AI_PIPELINE.md','TIMELINE_ENGINE.md','DIAGNOSTICS_AND_SUPPORT.md']
    index=(base/'README.md').read_text(encoding='utf-8') if (base/'README.md').exists() else ''
    for name in required:
        target=base/name
        if not target.exists(): errors.append(f'Missing docs/architecture/{name}')
        elif name!='README.md' and name not in index: errors.append(f'Architecture index omits {name}')
    path_pat=re.compile(r'`(custom_components/[^`]+)`')
    for doc in base.glob('*.md'):
        for ref in path_pat.findall(doc.read_text(encoding='utf-8')):
            candidate=ROOT/ref.rstrip('/.,')
            if not candidate.exists(): errors.append(f'{doc.relative_to(ROOT)} references missing {ref}')
    return result('architecture',errors)

def mermaid():
    errors=[]; supported=('flowchart','graph','sequenceDiagram','stateDiagram','stateDiagram-v2','classDiagram','erDiagram','journey','gantt','pie','mindmap','timeline')
    for p in list((ROOT/'docs').rglob('*.md'))+list((ROOT/'handoff').rglob('*.md')):
        text=p.read_text(encoding='utf-8')
        starts=[m.start() for m in re.finditer(r'```mermaid\s*\n',text)]
        for start in starts:
            body_start=re.search(r'```mermaid\s*\n',text[start:]).end()+start
            end=text.find('```',body_start)
            if end<0: errors.append(f'Unclosed Mermaid block in {p.relative_to(ROOT)}'); continue
            body=text[body_start:end].strip()
            first=body.splitlines()[0].strip() if body else ''
            if not first.startswith(supported): errors.append(f'Unsupported/empty Mermaid block in {p.relative_to(ROOT)}: {first or "empty"}')
            if any(x in body for x in ('TODO_DIAGRAM','PLACEHOLDER_DIAGRAM')): errors.append(f'Placeholder Mermaid block in {p.relative_to(ROOT)}')
    return result('mermaid',errors)


def ecosystem():
    errors=[]
    base=ROOT/'docs/ecosystem'
    required=['README.md','SUPPORT_MATRIX.md','CAPABILITY_MODEL.md','ADAPTER_CONTRACT.md','DISCOVERY_AND_IDENTITY.md','BTICINO.md','NETATMO.md','HOME_CONTROL.md','HOME_SECURITY.md','LIVING_NOW.md','LIVINGLIGHT.md','MATIXGO.md','BTDIN.md','SMARTHER.md','MYHOME.md','VIDEO_DOOR_ENTRY.md']
    index=(base/'README.md').read_text(encoding='utf-8') if (base/'README.md').exists() else ''
    matrix=(base/'SUPPORT_MATRIX.md').read_text(encoding='utf-8') if (base/'SUPPORT_MATRIX.md').exists() else ''
    mandatory=('## Status','## Capability scope','## Home Assistant mapping principles','## Dependencies and acceptance','## Related documentation')
    product_docs=required[5:]
    for name in required:
        target=base/name
        if not target.exists(): errors.append(f'Missing docs/ecosystem/{name}')
        elif name!='README.md' and name not in index: errors.append(f'Ecosystem index omits {name}')
    for name in product_docs:
        target=base/name
        if not target.exists(): continue
        text=target.read_text(encoding='utf-8')
        for heading in mandatory:
            if heading not in text: errors.append(f'{name} missing {heading}')
        title=text.splitlines()[0].lstrip('# ').strip() if text.splitlines() else name
        token={'BTICINO.md':'BTicino','NETATMO.md':'Netatmo','HOME_CONTROL.md':'Home + Control','HOME_SECURITY.md':'Home + Security','LIVING_NOW.md':'Living Now','LIVINGLIGHT.md':'Livinglight','MATIXGO.md':'MatixGO','BTDIN.md':'BTDIN','SMARTHER.md':'Smarther','MYHOME.md':'MyHOME','VIDEO_DOOR_ENTRY.md':'Video door entry'}[name]
        if token not in matrix: errors.append(f'Support matrix omits {token}')
    return result('ecosystem',errors)


def ai_documentation():
    errors=[]
    base=ROOT/'docs/ai'
    required=['README.md','AI_PLATFORM.md','AI_RUNTIME.md','PROVIDER_INTERFACE.md','PROVIDER_CAPABILITIES.md','PROMPT_ENGINE.md','VISION_PIPELINE.md','VOICE_PIPELINE.md','OCR_PIPELINE.md','FACE_RECOGNITION.md','OBJECT_DETECTION.md','EVENT_NORMALIZATION.md','AUTOMATION.md','LOCAL_MODELS.md','CLOUD_MODELS.md','PRIVACY.md','PERFORMANCE.md']
    index=(base/'README.md').read_text(encoding='utf-8') if (base/'README.md').exists() else ''
    for name in required:
        target=base/name
        if not target.exists(): errors.append(f'Missing docs/ai/{name}')
        elif name!='README.md' and name not in index: errors.append(f'AI index omits {name}')
    checks={
        'AI_PLATFORM.md':('## Status','## Goals','## Architecture','## Non-goals'),
        'AI_RUNTIME.md':('## Request lifecycle','## Failure contract'),
        'PRIVACY.md':('## Principles','## Classification'),
        'FACE_RECOGNITION.md':('## Safety baseline',),
    }
    for name,headings in checks.items():
        target=base/name
        if not target.exists(): continue
        text=target.read_text(encoding='utf-8')
        for heading in headings:
            if heading not in text: errors.append(f'{name} missing {heading}')
    platform=base/'AI_PLATFORM.md'
    if platform.exists() and 'does not claim working' not in platform.read_text(encoding='utf-8'):
        errors.append('AI_PLATFORM.md must explicitly avoid unfinished runtime claims')
    return result('ai_documentation',errors)

def provider_capability():
    errors=[]
    path=ROOT/'docs/ai/PROVIDER_CAPABILITIES.md'
    if not path.exists(): return result('provider_capability',['Missing docs/ai/PROVIDER_CAPABILITIES.md'])
    text=path.read_text(encoding='utf-8')
    capabilities=('chat','vision','ocr','face_recognition','object_detection','speech_to_text','text_to_speech','embeddings','summarization','translation','reasoning')
    providers=('OpenAI','Anthropic Claude','Google Gemini','Amazon Rekognition','Ollama','Home Assistant Assist')
    for item in capabilities:
        if item not in text: errors.append(f'Missing capability {item}')
    for item in providers:
        if item not in text: errors.append(f'Missing provider family {item}')
    for marker in ('Mode','RC.15 runtime status','Contract only'):
        if marker not in text: errors.append(f'Provider matrix missing {marker}')
    return result('provider_capability',errors)


def document_consistency():
    import subprocess
    proc=subprocess.run([sys.executable, str(ROOT/'tools/documentation/check_document_consistency.py')], cwd=ROOT, text=True, capture_output=True)
    errors=[] if proc.returncode==0 else [line[2:] if line.startswith('- ') else line for line in proc.stdout.splitlines() if line.startswith('- ')]
    if proc.returncode!=0 and not errors:
        errors.append(proc.stderr.strip() or 'Documentation consistency validator failed')
    return result('document_consistency',errors)


def project_impact():
    import subprocess
    proc=subprocess.run([sys.executable, str(ROOT/'tools/governance/check_project_impact.py'), '--json'], cwd=ROOT, text=True, capture_output=True)
    errors=[]
    if proc.returncode != 0:
        try:
            errors=json.loads(proc.stdout).get('errors', [])
        except json.JSONDecodeError:
            errors=[proc.stderr.strip() or 'Project impact validator failed']
    return result('project_impact', errors)

def handoff_synchronization():
    import subprocess
    proc=subprocess.run([sys.executable, str(ROOT/'tools/handoff/sync_handoff.py'), '--check', '--json'], cwd=ROOT, text=True, capture_output=True)
    errors=[]
    if proc.returncode != 0:
        try:
            errors=json.loads(proc.stdout).get('errors', [])
        except json.JSONDecodeError:
            errors=[proc.stderr.strip() or 'Handoff synchronization validator failed']
    return result('handoff_synchronization', errors)

CHECKS={'roadmap':roadmap,'documentation':documentation,'translation':translation,'adr':adr,'structure':structure,'links':links,'handoff':handoff,'compatibility':compatibility,'release':release,'api':api,'architecture':architecture,'mermaid':mermaid,'ecosystem':ecosystem,'ai_documentation':ai_documentation,'provider_capability':provider_capability,'voice_assistant_api':voice_assistant_api,'document_consistency':document_consistency,'project_impact':project_impact,'handoff_synchronization':handoff_synchronization}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',choices=CHECKS); ap.add_argument('--json',action='store_true'); args=ap.parse_args()
    out=[CHECKS[args.check]()] if args.check else [f() for f in CHECKS.values()]
    if args.json: print(json.dumps(out,indent=2))
    else:
        for item in out:
            print(f"[{item['status']}] {item['gate']}")
            for e in item['errors']: print(f'  - {e}')
    return 1 if any(x['status']=='FAIL' for x in out) else 0
if __name__=='__main__': raise SystemExit(main())

# Active-package orphan hygiene is validated separately by tools/check_orphans.py.
