# QS-19 Lifecycle and SIP Residual Coverage Report

## Scope

QS-19 extends executable coverage for integration-wide setup and migration helpers, optional-resource unload paths, certificate storage edge cases, and SIP stream framing/response handling. The repository baseline is QS-18.

## Measured result

- Previous integration coverage: **91.49%**.
- Current integration coverage: **92.55%**.
- Covered statements: **5156 / 5571**.
- Missing statements: **415**.
- `sip_client.py`: **87.09%** coverage (1025 / 1177 statements).
- `__init__.py`: **69.80%** coverage (178 / 255 statements).
- QS-19 residual tests: **4 PASS**.
- Coverage-gate behavioural suite: **321 PASS**.

## Behaviour exercised

- integration-wide sentence, voice and service registration;
- restart-repair creation and deletion semantics;
- v1-to-v2 config-entry migration and update-triggered reload;
- certificate storage reuse, full-chain migration and key permissions;
- unload with optional runtime resources absent;
- SIP request framing with bodies and leading CRLF keepalives;
- SIP response filtering for non-SIP data and provisional responses;
- exact response-body reads and incomplete-frame error handling.

## Quality Scale decision

Bronze remains the measured tier. Silver remains blocked because the strict integration coverage rule requires coverage above 95%.

## Next priority

QS-20 should prioritize remaining lifecycle setup branches in `__init__.py`, residual SIP transaction branches, and developer support-bundle paths.
