# ADR-0065: Home Assistant Integration Quality Scale Gate

## Status
Accepted

## Context
BTDoor Security+ requires an external, Home Assistant-aligned quality model in addition to its internal governance framework.

## Decision
Adopt the official Home Assistant Integration Quality Scale rule set as a conservative self-assessment. Generate `quality_scale.yaml`, JSON and Markdown reports, and require at least cumulative Bronze alignment before Final release approval.

The result is not represented as an official Home Assistant Core grade. Rules that cannot be proven statically remain pending until measured or runtime evidence exists.

## Consequences
- Bronze becomes a blocking release gate.
- Silver, Gold and Platinum remain progressive targets.
- Exemptions require explicit comments.
- Rule-set changes require regeneration and review.
