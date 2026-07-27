#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from collections import defaultdict
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/governance/documentation_consolidation_audit.json'
def main()->int:
    docs=[p for p in ROOT.rglob('*.md') if '.git' not in p.parts]
    groups=defaultdict(list)
    for p in docs: groups[hashlib.sha256(p.read_bytes()).hexdigest()].append(str(p.relative_to(ROOT)))
    duplicates=[v for v in groups.values() if len(v)>1]
    required=['docs/project/WORKFLOW.md','docs/governance/PROJECT_GOVERNANCE_SYSTEM.md','docs/governance/GOVERNANCE_RULE_REGISTRY.md','docs/governance/FRAMEWORK_REGISTRY.md','docs/governance/DOCUMENT_IMPACT_MATRIX.md','docs/governance/WORKFLOW_COMPLIANCE_MATRIX.md','docs/i18n/LOCALIZATION_FRAMEWORK.md','docs/i18n/language_registry.json']
    missing=[x for x in required if not (ROOT/x).exists()]
    payload={'schema_version':1,'generated':date.today().isoformat(),'markdown_files':len(docs),'exact_markdown_duplicate_groups':duplicates,'required_architecture_files':required,'missing_required_files':missing,'status':'PASS' if not missing and not duplicates else 'FAIL'}
    OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"Documentation consolidation: {payload['status']} ({len(docs)} markdown files, {len(duplicates)} exact duplicate groups)")
    return 0 if payload['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
