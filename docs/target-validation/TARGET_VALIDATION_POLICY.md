# Target Validation Policy

## Required domains

A complete Final-target run must retain evidence for:

1. Home Assistant 2026.x runtime benchmark;
2. Home Assistant compatibility lifecycle;
3. HACS clean install, upgrade and rollback lifecycle;
4. target-runtime security review;
5. interactive UX and accessibility review.

## Integrity rules

- Credentials and access tokens must never be stored in the repository.
- Automatic collection and manual observations must be distinguished.
- Every validated section requires at least one retained evidence file.
- `VALIDATED` is forbidden when a required check is missing or failed.
- Imported evidence is immutable. Corrections require a new run identifier.
- The Release Decision Engine remains authoritative for Final approval.
