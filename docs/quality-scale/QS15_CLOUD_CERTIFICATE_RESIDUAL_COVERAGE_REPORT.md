# QS-15 Cloud Certificate Residual Coverage Report

## Scope

QS-15 extends executable coverage for the MyHomeWeb cloud client and its certificate provisioning pipeline. The repository baseline is QS-14.

## Measured result

- Previous integration coverage: **88.42%**.
- Current integration coverage: **90.13%**.
- Covered statements: **5021 / 5571**.
- Missing statements: **550**.
- `cloud.py`: **95.57%** coverage (345 / 361 statements).
- QS-15 tests: **4 PASS**.
- Main behavioural suite: **301 PASS**.

## Behaviour exercised

- official-format device identifier generation;
- CSR and private-key generation;
- nested MyHomeWeb payload parsing;
- certificate response decoding from raw and Base64 data;
- PEM and DER certificate loading;
- certificate bundles carried in ZIP archives;
- private-key and certificate public-key matching;
- certificate chain ordering and expiry extraction;
- missing, invalid and mismatched certificate failures;
- certificate file backup, permissions, full-chain creation and stale chain removal;
- complete cloud provisioning result creation;
- incomplete SIP credential and attachment checksum failures;
- SIP user reuse by device ID;
- fallback to the created user and missing-created-user failure.

## Quality Scale decision

Bronze remains the measured tier. Silver remains blocked because the strict integration coverage rule requires coverage above 95%.

## Next priority

QS-16 should prioritize lifecycle branches in `__init__.py`, config-flow validation and reauthentication branches, and residual SIP transport/dialog branches.
