# ADR-0042 — Repository Integrity Suite

## Status

Accepted

## Context

BTDoor Platform must remain coherent across long release cycles, contributors, and independent ChatGPT sessions. Manual memory is insufficient evidence.

## Decision

Make repository knowledge checks release-blocking and execute them through one deterministic command.

## Consequences

Release preparation gains deterministic checks and traceability. Contributors must update affected knowledge artifacts with code changes. A failing mandatory gate blocks publication.
