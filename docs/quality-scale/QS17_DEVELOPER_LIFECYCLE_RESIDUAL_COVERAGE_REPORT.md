# QS-17 Developer and Lifecycle Residual Coverage Report

## Scope

QS-17 extends executable coverage for Developer Tools cloud, SIP, TLS and certificate diagnostics, runtime-path fallback, and the complete diagnostic test runner. The repository baseline is QS-16.

## Measured result

- Previous integration coverage: **90.50%**.
- Current integration coverage: **91.06%**.
- Covered statements: **5073 / 5571**.
- Missing statements: **498**.
- `developer.py`: **84.67%** coverage (254 / 300 statements).
- QS-17 residual tests: **2 PASS**.
- Coverage-gate behavioural suite: **313 PASS**.

## Behaviour exercised

- authenticated Developer Tools cloud login and configured-gateway discovery;
- SIP connection-test result mapping;
- production TLS connection path, SSL runtime metadata and guaranteed writer closure;
- certificate diagnostics using a real generated RSA key and X.509 PEM certificate;
- redacted certificate subject and non-redacted issuer formatting;
- missing certificate and missing private-key failures;
- runtime certificate path fallback to config-entry data;
- execution of the complete developer diagnostic test set and successful aggregate status.

## Quality Scale decision

Bronze remains the measured tier. Silver remains blocked because the strict integration coverage rule requires coverage above 95%.

## Next priority

QS-18 should prioritize lifecycle branches in `__init__.py`, high-value SIP residual branches, and media/platform edge branches with measurable deficits.
