# ADR-0058 — Repository Rationalization and Canonical Registry

- **Status:** Accepted
- **Date:** 2026-07-22

## Context

The project contains a broad documentation, validation and continuity ecosystem. Filename existence and orphan checks alone cannot distinguish legitimate convention-loaded assets from duplicate or superseded material.

## Decision

Adopt a machine-readable canonical-document registry, generate a repository dependency graph, verify Markdown link integrity, detect exact duplicate active documents and publish repository metrics. Unreferenced files are candidates for review, not automatic deletion targets.

## Consequences

- Each governed topic has one declared source of truth.
- Structural changes become measurable and CI-verifiable.
- Derived documents remain allowed but cannot redefine canonical policy.
- Destructive cleanup requires evidence beyond absence of textual references.
