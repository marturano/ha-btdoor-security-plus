# Home Assistant Integration Quality Scale

This area contains the BTDoor Security+ self-assessment against the official Home Assistant Integration Quality Scale.

The assessment is intentionally conservative. Static checks may mark a rule `done` or `exempt`; rules requiring measured coverage, runtime behavior, dependency verification, or strict typing remain `todo` until evidence exists.

Run:

```bash
python tools/quality_scale/quality_scale_engine.py
python tools/quality_scale/quality_scale_engine.py --check
```

Generated artifacts:

- `custom_components/btdoor_security_plus/quality_scale.yaml`
- `docs/quality-scale/QUALITY_SCALE_REPORT.json`
- `docs/quality-scale/QUALITY_SCALE_REPORT.md`

The result is not an official Home Assistant Core grade. It is a governance gate for this custom integration.

## Governed workflow

The mandatory workflow is defined in `QUALITY_SCALE_WORKFLOW.md`. Configuration is stored in `quality_scale_workflow.json`; generated status and remediation artifacts are `QUALITY_SCALE_WORKFLOW_STATUS.json` and `QUALITY_SCALE_REMEDIATION_PLAN.*`.
