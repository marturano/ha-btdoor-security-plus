# ADR-0049 — Capability adapter boundary

Status: Accepted

## Context

BTicino and Netatmo product families use different APIs, gateways and naming models.

## Decision

Vendor/product adapters terminate at a canonical capability boundary. Home Assistant entities, services and events are derived from capabilities rather than product names or transports.

## Consequences

Cloud and local implementations may coexist, identity remains stable, unsupported functions are not fabricated, and future SDK extensions can target a common contract.
