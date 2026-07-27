# Handoff 71 — Phase 7C Runtime Lifecycle Hardening

**Date:** 2026-07-23  
**Current package:** `1.1.0-rc.15-phase7c-runtime-hardening`  
**Phase:** 7C — Release Candidate Approval  
**Decision:** BLOCKED

## Completed

- audited config-entry setup and unload lifecycle;
- fixed cleanup after certificate-renewal, SIP-start, device-registration and platform-forwarding failures;
- centralized runtime cleanup for normal unload and failed setup;
- made SIP call-timeout cancellation deterministic by awaiting the cancelled task;
- added two regression tests;
- verified 332 repository tests with a clean, isolated pytest invocation.

## Runtime files changed

- `custom_components/btdoor_security_plus/__init__.py`
- `custom_components/btdoor_security_plus/sip_client.py`

## Test files changed

- `tests/test_quality_scale_qs19_lifecycle_sip_residual.py`

## Resume point

Continue Phase 7C evidence closure. Execute Ruff on the exact package, then perform target-runtime, performance, UX, publication and final Quality Scale evidence collection. Do not start Phase 7D until the Release Decision Engine returns `APPROVED`.
