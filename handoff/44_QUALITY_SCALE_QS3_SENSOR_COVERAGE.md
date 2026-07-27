# Quality Scale QS-3 Sensor Coverage

> **Document status:** Historical snapshot  
> **Normative:** No  
> **Superseded for current status by:** `handoff/64_QUALITY_SCALE_QS23_GOLD_PROJECT_POLICY.md`  
> **Current authoritative state:** GOLD is the permanent governed maximum; consult the master roadmap, workflow and current certificates.


QS-3 is complete on the official QS-2 baseline.

## Evidence

- 249 tests pass.
- Total measured coverage: **53.24%**.
- `sensor.py`: **98.74%**.
- Bronze remains achieved.
- Silver remains 9/10 because `test-coverage` is below the required threshold above 95%.

## Resume point

Continue QS-4 with `services.py`, then `cloud.py`, `__init__.py`, and `sip_client.py`. Re-measure after each batch and do not promote Silver without generated coverage evidence.
