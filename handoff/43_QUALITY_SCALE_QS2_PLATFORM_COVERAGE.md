# Quality Scale QS-2 Platform Coverage

> **Document status:** Historical snapshot  
> **Normative:** No  
> **Superseded for current status by:** `handoff/64_QUALITY_SCALE_QS23_GOLD_PROJECT_POLICY.md`  
> **Current authoritative state:** GOLD is the permanent governed maximum; consult the master roadmap, workflow and current certificates.


## Verified baseline

- Source package: `ha-btdoor-security-plus-1.1.0-rc.15-quality-scale-qs1-progress(1).zip`
- Starting coverage: **35.54%**
- Starting tests: **240 PASS**
- Quality Scale tier: **Bronze**

## Implemented evidence

Added `tests/test_quality_scale_qs2_platform_entities.py` with behavioural coverage for:

- binary-sensor setup, filtering, state and attributes;
- event setup and supported-event filtering;
- voice-bridge option handling, success, failure, and stateless turn-off;
- gate button availability, attributes, service success and failure;
- developer test/report/cleanup buttons and notifications;
- diagnostics payload construction and sanitization boundary;
- shared entity and device-info construction paths.

The tests load the real integration modules with minimal Home Assistant contract stubs because Home Assistant is not installed in the repository test environment.

## Verified result

- Tests: **245 PASS**
- Coverage: **40.59%**
- Covered statements: **2261 / 5571**
- Silver rule completion: **9/10**
- Remaining blocker: `test-coverage`
- Silver threshold: **above 95%**
- Current tier: **Bronze**

## Immediate resume point

Continue the Quality Scale coverage program with `sensor.py`, then `services.py`. After those platform-level gains, cover `cloud.py`, integration lifecycle in `__init__.py`, and the remaining `sip_client.py` branches.

Run every batch with:

```bash
pytest -q -p no:cacheprovider
python tools/quality_scale/coverage_gate.py --measure
python tools/quality_scale/quality_scale_workflow.py run
python tools/governance/run_governance.py
```

Do not promote Silver until measured total coverage is above 95% and all gates remain green.
