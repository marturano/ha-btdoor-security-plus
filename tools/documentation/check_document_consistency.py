#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PKG='1.1.0-rc.15-phase7c-github-publication-ready'
OLD='1.1.0-rc.15-quality-release-intelligence'
ACTIVE_IDENTITY=[
 'handoff/03_PROJECT_STATE.md','handoff/14_BUILD_INFORMATION.md',
 'docs/project/REPOSITORY_INVENTORY.md','docs/project/PROJECT_HEALTH_DASHBOARD.md',
 'docs/project/project_health.json','docs/project/project_health_calculated.json',
 'PROJECT_MANIFEST.md','PROJECT_MANIFEST.yaml']
IGNORE={'.git','.pytest_cache','__pycache__','.mypy_cache','.ruff_cache'}

def files():
 return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not any(x in p.parts for x in IGNORE))

def main()->int:
 errors=[]
 for rel in ACTIVE_IDENTITY:
  p=ROOT/rel
  if not p.exists(): errors.append(f'missing active identity file: {rel}'); continue
  text=p.read_text(encoding='utf-8')
  if PKG not in text: errors.append(f'current package identity missing: {rel}')
  if OLD in text and rel not in {'handoff/14_BUILD_INFORMATION.md'}: errors.append(f'obsolete package presented in active identity file: {rel}')
 # Inventory completeness.
 inv=(ROOT/'docs/project/REPOSITORY_INVENTORY.md').read_text(encoding='utf-8')
 listed=set(re.findall(r'^- `([^`]+)`$',inv,re.M))
 actual=set(files())
 missing=sorted(actual-listed); stale=sorted(listed-actual)
 if missing: errors.append(f'inventory missing {len(missing)} files: '+', '.join(missing[:10]))
 if stale: errors.append(f'inventory lists {len(stale)} absent files: '+', '.join(stale[:10]))
 # Historical Quality Scale metadata.
 for n in range(40,64):
  for p in (ROOT/'handoff').glob(f'{n}_*.md'):
   text=p.read_text(encoding='utf-8')
   if '**Document status:** Historical snapshot' not in text or '**Normative:** No' not in text:
    errors.append(f'historical metadata missing: {p.relative_to(ROOT)}')
 for p in (ROOT/'docs/platinum').glob('*.md'):
  text=p.read_text(encoding='utf-8')
  if '**Document status:** Historical / informational' not in text or '**Active roadmap scope:** Excluded' not in text:
   errors.append(f'Platinum historical classification missing: {p.relative_to(ROOT)}')
 # Cross-locale copied English paragraph.
 marker='The public Home Assistant entity, action and event contracts are now documented'
 for loc in ('de','es','fr','it','nl'):
  p=ROOT/f'docs/{loc}/release/1.1.0-rc.15.md'
  if marker in p.read_text(encoding='utf-8'): errors.append(f'English release-note contamination: {p.relative_to(ROOT)}')
 # Health source/calculated/dashboard identity coherence.
 src=json.loads((ROOT/'docs/project/project_health.json').read_text(encoding='utf-8'))
 calc=json.loads((ROOT/'docs/project/project_health_calculated.json').read_text(encoding='utf-8'))
 dash=(ROOT/'docs/project/PROJECT_HEALTH_DASHBOARD.md').read_text(encoding='utf-8')
 if src.get('package')!=calc.get('package') or src.get('package')!=PKG: errors.append('Project Health package identity mismatch')
 if f'`{PKG}`' not in dash: errors.append('Project Health Dashboard package identity mismatch')
 # Approval semantics.
 semantic='Release Readiness `PASS` confirms package-level readiness checks only'
 for rel in ('docs/quality/RELEASE_DECISION_REPORT.md','handoff/66_PRE_PHASE_7C_REPOSITORY_AUDIT.md','docs/release/1.1.0-rc.15.md'):
  if semantic not in (ROOT/rel).read_text(encoding='utf-8'): errors.append(f'approval semantics missing: {rel}')
 status='PASS' if not errors else 'FAIL'
 print(f'Document consistency: {status}')
 for e in errors: print(f'- {e}')
 return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
