# Phase 7C — Target Matrix Correction

**Package:** `1.1.0-rc.15-phase7c-target-matrix-corrected`  
**Phase:** 7C — Release Candidate Approval  
**Decision:** BLOCKED

## Correction

The target validation contract is:

- supported target series: **Home Assistant 2026.x**;
- reference target for final certification: **Home Assistant 2026.7.x**.

A completed and sanitized run on any Home Assistant 2026.x version may be imported as compatibility evidence. Final Phase 7C closure additionally requires at least one complete accepted run on Home Assistant 2026.7.x.

The validator no longer rejects supported 2026.x releases outside 2026.7.x. It now rejects only versions outside the 2026.x series and reports whether each run is a 2026.7.x reference-target run.

## Validation

Dedicated regression tests cover:

- acceptance of a supported 2026.x target;
- identification of a 2026.7.x reference target;
- rejection of a target outside 2026.x;
- existing evidence-path and completeness protections.

No runtime integration feature was changed. Phase 7D remains unauthorized.
