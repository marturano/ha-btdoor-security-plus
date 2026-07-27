# Quality Scale QS-6 Developer and Lifecycle Coverage

> **Document status:** Historical snapshot  
> **Normative:** No  
> **Superseded for current status by:** `handoff/64_QUALITY_SCALE_QS23_GOLD_PROJECT_POLICY.md`  
> **Current authoritative state:** GOLD is the permanent governed maximum; consult the master roadmap, workflow and current certificates.


QS-6 is complete on the official QS-5 baseline.

## Evidence

- Test suite: **261 PASS**
- Total measured coverage: **68.62%**
- Previous coverage: **64.62%**
- Increase: **4.00 percentage points**
- `developer.py`: **74%**, previously 0%
- `__init__.py`: **26%**
- `sip_client.py`: **40%**
- Quality Scale: **Bronze**
- Silver: **9/10 rules**, blocked only by `test-coverage`

## Implemented tests

`tests/test_quality_scale_qs6_developer_lifecycle.py` executes the real developer module and covers developer-mode enforcement, aggregate tests, sanitized errors, certificate checks, health scoring, SDP/media/dialog diagnostics, directory checks, retention, support Markdown and ZIP bundles, and debug cleanup.

## Resume point

Continue with **QS-7 Lifecycle and SIP Transport Coverage** in this order:

1. setup, unload, migration and certificate renewal in `__init__.py`
2. connect, register, exchange, reader and request dispatch in `sip_client.py`
3. residual `cloud.py` branches
4. zero-coverage runtime, device-manager, adapter and voice modules

Never promote Silver until measured integration coverage exceeds 95% and the complete suite remains green.
