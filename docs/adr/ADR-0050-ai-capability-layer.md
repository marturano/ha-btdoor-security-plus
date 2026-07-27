# ADR-0050 — AI Capability Layer

Status: Accepted

## Context
Callers must not depend on provider-specific APIs.

## Decision
AI requests target canonical capabilities and pass through an orchestrator and provider-adapter boundary.

## Consequences
Providers become replaceable, responses are normalized, and unsupported capabilities fail explicitly.
