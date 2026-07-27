# QS-4 Services and Cloud Coverage Report

## Scope

QS-4 expanded executable behavioural coverage for the global service layer and the MyHomeWeb cloud client without changing production behaviour.

## Measured result

- Previous total integration coverage: **53.24%**
- Current total integration coverage: **59.24%**
- Increase: **6.00 percentage points**
- Test suite: **253 PASS**
- Silver threshold: **above 95%**
- Quality Scale tier remains: **Bronze**

## Module results

- `services.py`: exercised service selection, registration, idempotency, successful gate opening, failure events, statistics reset, connection test, call rejection, developer actions, support reports, journal export/rebuild, and symmetric unregistration.
- `cloud.py`: increased from 0% to **55%** by covering authentication classification, parsing helpers, gateway discovery, SIP-user reuse/creation, certificate-file handling, identity helpers, and login outcomes.

## Remaining priority

The largest remaining coverage deficits are:

1. `sip_client.py`
2. `__init__.py`
3. `developer.py`
4. `media.py`
5. remaining branches in `cloud.py`

Silver remains blocked solely by the measured coverage rule.
