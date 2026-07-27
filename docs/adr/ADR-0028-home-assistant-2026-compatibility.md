# ADR-0028 — Home Assistant 2026.x compatibility evidence

Status: Accepted for 1.1.0-rc.9.

## Decision
Target Home Assistant 2026.x and record exact patch-level evidence as static, CI/API, runtime and real-device validation. Home Assistant 2026.7 is the primary release-validation environment, not the only supported target.

## Consequence
The minimum version remains 2026.1.0 only when required gates pass; import success alone is insufficient.
