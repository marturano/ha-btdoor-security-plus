# Home Assistant Certification Policy

## Scope

Certification applies to a real Home Assistant 2026.x installation and covers API connectivity, integration loading, entity continuity, restart behavior, diagnostics, service smoke tests, log review, backup, upgrade, rollback and operator review.

## Evidence rules

Every scenario must be `VALIDATED`, include notes, and reference at least one evidence file. API tokens must never be stored. Evidence must be sanitized before import. An operator attestation is mandatory.

## Safety

Backup and rollback tests must be executed on a disposable or recoverable target. Restoring a backup can overwrite changes made after that backup.

## Decision boundary

This pack may generate evidence but cannot set the Final release to approved. Approval remains the responsibility of the Release Decision Engine after accepted target evidence is imported.
