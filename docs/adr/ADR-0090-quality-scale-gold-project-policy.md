# ADR-0090 — Quality Scale Gold Project Policy

**Status:** Accepted  
**Date:** 2026-07-23

## Context

QS-21 demonstrated the Gold tier. QS-22 established that Platinum would require architectural work, including an external async client package and repository-wide strict typing, with risk disproportionate to the current product roadmap.

## Decision

BTDoor Security+ adopts **Home Assistant Integration Quality Scale Gold as the permanent governed project target**.

The workflow must enforce all of the following:

- release minimum tier: Gold;
- desired tier: Gold;
- maximum governed tier: Gold;
- release advancement blocked when Gold is not demonstrated;
- Platinum excluded from active remediation and roadmap work;
- Platinum may be reconsidered only through a new explicit project decision and ADR.

The repository continues to assess all official tiers for transparency, but Platinum findings are informational and do not create remediation work.

## Consequences

- Every implementation phase must preserve Gold.
- Any regression below Gold blocks release advancement.
- The remediation plan is empty while Gold remains complete.
- Platinum audit documents remain historical evidence, not an active implementation plan.
- This is a repository self-assessment and not an official Home Assistant grade.
