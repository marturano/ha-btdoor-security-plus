# ADR-0062 — Release Pipeline and Distribution

## Status
Accepted

## Decision
BTDoor Security+ uses a reproducible distribution pipeline that creates an integration ZIP, a SHA-256 checksum and a machine-readable release manifest. Artifact construction and publication authorization are separate operations. Blocked governance gates cannot be bypassed by merely creating a ZIP.

## Consequences
Candidate artifacts can be tested before final approval, while every publishable artifact remains traceable to the certification and release-decision state.
