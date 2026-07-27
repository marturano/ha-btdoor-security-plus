# ADR-0061: Target Validation Pack

## Status
Accepted

## Decision
Use a portable, schema-governed target validation pack to collect the five external evidence domains required by the Final release. Only immutable imported runs with explicit operator attestation and retained evidence may update target certification statuses.

## Consequences
- Runtime credentials remain outside the repository.
- Incomplete or contradictory runs are rejected.
- Certification remains blocked until a real target run is imported.
- Revisions use a new run identifier rather than modifying accepted evidence.
