# QS-16 Config Flow Residual Coverage Report

## Scope

QS-16 extends executable coverage for cloud discovery, provisioning data construction, SIP validation, reauthentication error mapping, and options-flow safety. The repository baseline is QS-15.

## Measured result

- Previous integration coverage: **90.13%**.
- Current integration coverage: **90.50%**.
- Covered statements: **5042 / 5571**.
- Missing statements: **529**.
- `config_flow.py`: **95.40%** coverage (166 / 174 statements).
- QS-16 residual tests: **4 PASS**.
- Main behavioural suite: **305 PASS**.

## Behaviour exercised

- authenticated cloud discovery and gateway listing;
- construction of the cloud client from submitted credentials;
- complete provisioning data assembly including optional CA chain;
- storage-path construction for per-gateway certificates;
- SIP validation client construction and connection test;
- reauthentication mapping for cloud connection and provisioning failures;
- configured-gateway absence during reauthentication;
- options normalization when developer mode is disabled;
- explicit quick-voice confirmation form.

## Quality Scale decision

Bronze remains the measured tier. Silver remains blocked because the strict integration coverage rule requires coverage above 95%.

## Next priority

QS-17 should prioritize lifecycle branches in `__init__.py`, developer diagnostics, and high-value residual SIP branches.
