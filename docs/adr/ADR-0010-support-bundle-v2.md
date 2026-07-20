# ADR-0010: Support Bundle v2

- Status: Accepted
- Date: 2026-07-17

## Decision

Support bundles use schema version 2 and expose a compact `support_summary.json`, stable build metadata, per-engine diagnostics, split runtime state, and aggregate timeline statistics. The existing monolithic `diagnostics.json` remains available for compatibility.

## Rationale

A stable, modular bundle is faster to inspect manually, safer to process automatically, and suitable for future AI-assisted diagnostics without breaking existing support workflows.
