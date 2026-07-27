# Target Validation Pack

This area contains the executable and auditable process used to collect the five target-environment evidence sets required for `1.1.0 Final`.

The pack never promotes a target status merely because a result file exists. A run must identify a supported Home Assistant 2026.x environment, retain sanitized evidence paths, validate every required check and include explicit operator attestation. Home Assistant 2026.7.x is the reference target and must be represented in the final certification evidence set.

## Operator documents

- `FIELD_EXECUTION_CHECKLIST.md` — exact field sequence and acceptance expectations.
- `EVIDENCE_SANITIZATION_GUIDE.md` — mandatory privacy and secret-handling rules.
- `TARGET_VALIDATION_GUIDE.md` — command workflow.
- `TARGET_VALIDATION_POLICY.md` — governing policy.

## Commands

```bash
python tools/target_validation/target_validation.py init --run-id <id>
python tools/target_validation/target_validation.py collect --run-id <id>
python tools/target_validation/target_validation.py status --run-id <id>
python tools/target_validation/target_validation.py validate --run-id <id>
python tools/target_validation/target_validation.py import --run-id <id>
```

`collect` reads `HA_URL` and `HA_TOKEN` from the environment. The token and full URL are never written to disk; only a host label is retained.

Imported evidence is stored below `docs/target-validation/runs/`. The certification engine consumes only runs whose `import_status` is `ACCEPTED`.
