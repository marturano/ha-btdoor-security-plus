# Evidence Register

The machine-readable source of truth is `evidence_register.json`. Every formal gate must reference evidence with a unique ID, owner, status, source and blocking classification.

## Status model

- **VALIDATED:** source exists and the evidence has been reviewed for the current package.
- **PENDING:** activity is planned or underway but not validated.
- **MISSING:** the required evidence artifact does not exist.
- **REJECTED:** evidence exists but does not satisfy the gate.

Run:

```bash
python tools/evidence/quality_intelligence.py --check
```

Evidence coverage is descriptive. A high percentage never overrides a single missing blocking item.
