# Target Validation Execution Guide

## Prepare

Run `init` on the machine used for validation. The command creates:

- `result.json`, the governed machine-readable result;
- `CHECKLIST.md`, the generated per-run field checklist;
- `evidence/`, the sanitized evidence directory.

Use `docs/target-validation/FIELD_EXECUTION_CHECKLIST.md` as the authoritative operator procedure.

## Automatic collection

Set `HA_URL` and `HA_TOKEN`, then run `collect`. The collector records Home Assistant version, installation type, integration entity totals and unavailable states. It never persists the token or full URL.

The supported target series is Home Assistant 2026.x. Home Assistant 2026.7.x is the reference target for final certification and must be included, but valid 2026.x runs are accepted as compatibility evidence.

## Manual lifecycle evidence

Complete runtime, compatibility, HACS, security and UX/accessibility checks. Save screenshots, exported diagnostics, measurements or sanitized logs under the run `evidence/` directory and reference them from `result.json`.

Use `status` during execution to show completed checks and blockers:

```bash
python tools/target_validation/target_validation.py status --run-id <id>
```

## Validate and import

`validate` rejects incomplete sections, missing files, unsafe paths, missing attestations and targets outside the Home Assistant 2026.x series. `import` accepts only a complete run and copies it into the immutable canonical evidence directory.

Then run:

```bash
python tools/certification/run_certification.py
python tools/evidence/quality_intelligence.py
python tools/release/release_decision.py
python tools/health/calculate_health.py
```
