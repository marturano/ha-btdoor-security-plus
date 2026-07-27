# ADR-0047: Configuration Entry Runtime as Ownership Boundary

**Status:** Accepted  
**Date:** 2026-07-21

## Context

Multi-entry Home Assistant integrations risk leaked tasks, cross-entry state and ambiguous global service routing.

## Decision

Each configuration entry owns one isolated runtime containing clients, tasks, subscriptions, state providers and managers. Global services must resolve explicit entry ownership before physical or destructive actions.

## Consequences

New features must be entry-local by default and prove cleanup on unload/reload.
