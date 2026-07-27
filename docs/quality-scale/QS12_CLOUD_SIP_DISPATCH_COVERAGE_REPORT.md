# QS-12 Cloud and SIP Dispatch Coverage Report

## Result

Measured integration coverage increased from **80.49%** to **83.22%**.

- Covered statements: 4636 / 5571
- Missing statements: 935
- Silver threshold: above 95%
- Current tier: Bronze

## Implemented tests

Added `tests/test_quality_scale_qs12_cloud_sip_dispatch.py` covering:

- SIP malformed request rejection;
- MESSAGE handling and duplicate suppression;
- OPTIONS, ACK, INFO, NOTIFY, REFER, SUBSCRIBE, PRACK and UPDATE dispatch;
- unsupported SIP request response;
- provisional and final SIP response dispatch;
- reader-loop disconnect handling;
- authenticated cloud requests and token rotation;
- missing authentication, authentication rejection and HTTP failures;
- binary cloud response retries and terminal connection failures.

## Validation

The QS-12 test module passes. The main behavioural suite passes when repository/certification launcher tests are executed separately, as required by the established validation workflow.
