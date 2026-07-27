# ADR-0055 — Physical Action Target Isolation

Status: Accepted

## Context

A gate-open command must never be routed to an unintended gateway in multi-entry installations.

## Decision

Physical commands resolve exactly one loaded config entry using explicit `entry_id` or an entity owned by that entry. Ambiguity fails visibly; broad fallback is forbidden.

## Consequences

Alexa, Google, Assist, scripts and future APIs must all preserve this target-isolation rule.
