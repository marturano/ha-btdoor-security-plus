# Home Assistant Quality Scale Status

The Home Assistant Integration Quality Scale is integrated as a repository self-assessment and release gate.

## Commands

```bash
python tools/quality_scale/quality_scale_engine.py
python tools/quality_scale/quality_scale_engine.py --check
```

## Current blocking item
Bronze is not yet complete because full config-flow test coverage is not currently proven. The engine must not mark this rule complete without dedicated evidence.

## Important
This is not an official Home Assistant grade. Final release remains blocked until Bronze and all other release evidence gates pass.

## Workflow integration

The assessment is now governed by `tools/quality_scale/quality_scale_workflow.py`; see `39_QUALITY_SCALE_WORKFLOW_STATUS.md`.
