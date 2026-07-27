# ADR-0053 — Local-first AI Strategy

Status: Accepted

## Context
Local processing can reduce disclosure, latency and variable cost.

## Decision
Prefer eligible local providers when quality and hardware are adequate, while preserving explicit cloud opt-in and deterministic fallback.

## Consequences
Local provider health and capability checks are first-class requirements; local execution is not treated as automatically trusted.
