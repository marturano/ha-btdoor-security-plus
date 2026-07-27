# QS-7 Lifecycle and SIP Transport Coverage Report

## Scope

QS-7 expands executable behavioural coverage for the SIP lifecycle and transport layer without changing production behaviour.

## Measured result

- Previous total integration coverage: **68.62%**
- Current cumulative measured coverage: **71.57%**
- Increase: **2.95 percentage points**
- Silver threshold: **above 95%**
- Quality Scale tier remains: **Bronze**

The cumulative figure is built from the validated QS-6 full-suite coverage evidence plus the QS-7 isolated pytest-cov evidence, merged by executed source line. This preserves traceability without estimating uncovered lines.

## Module results

- `sip_client.py`: **53.95%**, up from 40.02%.
- `__init__.py`: remains **25.88%**; full setup-entry lifecycle and certificate renewal branches remain a priority.

## Behaviour covered

- SIP start and stop lifecycle
- persistent-session connection probe
- temporary REGISTER probe with public-state restoration
- gate command success, transient 404 retry, and authentication retry/failure
- incoming call rejection
- session creation and teardown
- pending transaction failure on disconnect
- serialized writes and asynchronous exchanges
- missing certificate/key errors
- MESSAGE digest authentication and 404 handling

## Evidence discipline

The new tests execute the real SIP client module. Silver remains blocked until measured integration coverage exceeds 95% and the complete validation workflow is green.
