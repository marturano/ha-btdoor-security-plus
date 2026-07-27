#!/usr/bin/env python3
from __future__ import annotations
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/project/REPOSITORY_INVENTORY.md'
IGNORE={'.git','.pytest_cache','__pycache__','.mypy_cache','.ruff_cache'}

def active_files():
    rows=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(part in IGNORE for part in p.parts):
            continue
        if p.resolve()==OUT.resolve():
            rows.append(p.relative_to(ROOT).as_posix())
        else:
            rows.append(p.relative_to(ROOT).as_posix())
    return sorted(set(rows))

def main()->int:
    package='1.1.0-rc.15-phase7c-github-publication-ready'
    files=active_files()
    lines=['# Repository Inventory','',f'**Generated:** {date.today().isoformat()}  ',f'**Package:** `{package}`  ','**Purpose:** canonical inventory of every active file in the exact package during Phase 7C assessment.','',f'**Active file count:** {len(files)}','','## Active files','']
    lines += [f'- `{x}`' for x in files]
    lines += ['','## Maintenance contract','','1. Regenerate this file after every file addition, removal, move or archival action.','2. The exact-package inventory must contain every active repository file.','3. Generated caches, bytecode, local coverage state and nested release archives are forbidden active-package content.','4. Run `python tools/documentation/check_document_consistency.py` after regeneration.','']
    OUT.write_text('\n'.join(lines),encoding='utf-8')
    print(f'Generated {OUT.relative_to(ROOT)} with {len(files)} active files')
    return 0
if __name__=='__main__': raise SystemExit(main())
