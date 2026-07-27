# ADR-0045 — Zero Knowledge Loss continuity policy

## Status

Accepted

## Context

BTDoor Platform must remain coherent across long release cycles, contributors, and independent ChatGPT sessions. Manual memory is insufficient evidence.

## Decision

Require every release package to contain sufficient manifest, memory, status, handoff, and Recovery Prompt material to resume without chat history.

## Consequences

Release preparation gains deterministic checks and traceability. Contributors must update affected knowledge artifacts with code changes. A failing mandatory gate blocks publication.
