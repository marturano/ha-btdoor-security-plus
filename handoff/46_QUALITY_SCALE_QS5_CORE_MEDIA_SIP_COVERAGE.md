# Quality Scale QS-5 Core, Media and SIP Coverage

> **Document status:** Historical snapshot  
> **Normative:** No  
> **Superseded for current status by:** `handoff/64_QUALITY_SCALE_QS23_GOLD_PROJECT_POLICY.md`  
> **Current authoritative state:** GOLD is the permanent governed maximum; consult the master roadmap, workflow and current certificates.


QS-5 is complete on the official QS-4 baseline.

## Evidence

- Test suite: **258 PASS**
- Total measured coverage: **64.62%**
- Previous coverage: **59.24%**
- Increase: **5.38 percentage points**
- `__init__.py`: **26%**
- `media.py`: **84%**
- `sip_client.py`: **40%**
- Quality Scale: **Bronze**
- Silver: **9/10 rules**, blocked only by `test-coverage`

## Implemented tests

`tests/test_quality_scale_qs5_core_media_sip.py` executes real core, media and SIP modules. It covers availability logging, certificate storage, retired entity cleanup, SRTP attributes, codec selection, SDP generation/redaction, media preparation, SIP state handling, SDP parsing, header/status parsing and digest authentication.

## Resume point

Continue with **QS-6 Developer and Lifecycle Coverage** in this order:

1. `developer.py`
2. lifecycle and certificate renewal branches in `__init__.py`
3. transport/dialog branches in `sip_client.py`
4. residual `cloud.py` branches
5. zero-coverage runtime/support modules

Never promote Silver until measured integration coverage exceeds 95% and the complete suite remains green.
