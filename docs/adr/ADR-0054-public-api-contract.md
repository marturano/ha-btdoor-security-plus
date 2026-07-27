# ADR-0054 — Public API Contract

Status: Accepted

## Context

Entities, actions and events were implemented but not documented with enough precision to serve as stable integration surfaces.

## Decision

The canonical public surface is `docs/api/`. Only explicitly documented entities, actions, events and future transports are public. Internal Python modules and dispatcher signals are private.

## Consequences

API changes require documentation, compatibility classification, validation and release evidence.
