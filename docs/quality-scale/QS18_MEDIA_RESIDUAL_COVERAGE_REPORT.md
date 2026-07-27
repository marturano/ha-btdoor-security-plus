# QS-18 Media Residual Coverage Report

## Scope

QS-18 extends executable coverage for media negotiation edge cases, SRTP metadata handling, socket lifecycle and failure cleanup. The repository baseline is QS-17.

## Measured result

- Previous integration coverage: **91.06%**.
- Current integration coverage: **91.49%**.
- Covered statements: **5097 / 5571**.
- Missing statements: **474**.
- `media.py`: **99.16%** coverage (235 / 237 statements).
- QS-18 residual tests: **4 PASS**.
- Coverage-gate behavioural suite: **317 PASS**.

## Behaviour exercised

- non-inline, invalid and valid SDES-SRTP key material;
- lifetime, MKI and public redacted crypto metadata;
- socket release tolerant of already-closed descriptors;
- RTP/RTCP pair exhaustion and cleanup;
- local-address discovery fallback on routing errors;
- empty SDP diff handling;
- degraded media negotiation for invalid remote keys and unsupported video codecs;
- cleanup of already-reserved sockets when later media preparation fails.

## Quality Scale decision

Bronze remains the measured tier. Silver remains blocked because the strict integration coverage rule requires coverage above 95%.

## Next priority

QS-19 should prioritize lifecycle branches in `__init__.py`, high-value SIP client residual paths, and remaining developer/platform deficits.
