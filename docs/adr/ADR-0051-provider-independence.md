# ADR-0051 — Provider Independence

Status: Accepted

## Context
Provider models, prices and APIs change independently.

## Decision
No public automation, event or entity contract may expose a mandatory provider-specific payload.

## Consequences
Adapters absorb API churn and capability discovery becomes mandatory.
