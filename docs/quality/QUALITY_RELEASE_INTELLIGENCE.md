# Quality and Release Intelligence

Phase 6C makes release governance explainable and evidence-driven.

## Canonical inputs

- `evidence_register.json`
- `risk_register.json`
- `technical_debt_register.json`
- `decision_traceability.json`

## Generated outputs

- `quality_release_intelligence.json`
- `release_decision.json`
- `RELEASE_DECISION_REPORT.md`
- `DECISION_TRACEABILITY.md`

## Commands

```bash
python tools/evidence/quality_intelligence.py --check
python tools/traceability/build_traceability.py --check
python tools/release/release_decision.py
```

`release_decision.py` returning a BLOCKED decision is not a tooling failure. It is the expected truthful result whenever mandatory Final evidence or severe risks remain open.
