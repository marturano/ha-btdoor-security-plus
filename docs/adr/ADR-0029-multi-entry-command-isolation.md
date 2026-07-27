# ADR-0029 — Multi-entry command isolation

Status: Accepted.

## Decision
Every command must resolve one config entry before transport access. Global services never capture an arbitrary entry runtime. Ambiguous calls fail closed.

## Consequence
Tests must cover load order, unload order, reload and explicit `entry_id`/entity targeting.
