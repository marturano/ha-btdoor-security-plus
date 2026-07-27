# Quality Scale QS-1 Coverage Program

> **Document status:** Historical snapshot  
> **Normative:** No  
> **Superseded for current status by:** `handoff/64_QUALITY_SCALE_QS23_GOLD_PROJECT_POLICY.md`  
> **Current authoritative state:** GOLD is the permanent governed maximum; consult the master roadmap, workflow and current certificates.


## Current status

- Achieved tier: **Bronze**
- Silver rules complete: **9/10**
- Remaining Silver rule: `test-coverage`
- Previous measured coverage: **34.27%**
- Current measured coverage: **35.54%**
- Silver threshold: **above 95%**

## Changes in this increment

- Added executable behavioural coverage for runtime summary mapping.
- Added executable coverage for all visibility policy branches.
- Added executable coverage for dashboard registry resolution and build delegation.
- Made coverage measurement repository-clean by disabling the pytest cache provider.
- Added a generated high-impact module priority map.

## Immediate resume point

Continue QS-1 with the Home Assistant entity platforms, beginning with `sensor.py`, then `binary_sensor.py`, `button.py`, `switch.py`, and `event.py`. Use lightweight Home Assistant contract stubs only where the repository test environment lacks Home Assistant; assert real platform behaviour rather than source strings.

After every batch run:

```bash
python tools/quality_scale/coverage_gate.py --measure
python tools/quality_scale/quality_scale_workflow.py run
python tools/governance/run_governance.py
```

Do not promote Silver until measured total coverage is above 95% and the complete suite remains green.
