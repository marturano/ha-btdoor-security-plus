# ADR-0057 — Gate-Based Workflow and Project Health Dashboard

## Status

Accepted — 2026-07-22

## Context

The project workflow had become complete but remained mostly linear. Release decisions required a clearer separation between activities and formal approval gates, plus a single evidence-based view of project health across quality, security, benchmarks, translations, compatibility, validation, documentation, publication and continuity.

## Decision

Adopt the gate-based workflow in `docs/project/WORKFLOW.md` and the gate catalogue in `docs/project/WORKFLOW_GATES.md`. Introduce the governed Project Health Dashboard using `docs/project/project_health.json` as its data source, `tools/update_project_health.py` as its renderer and `docs/project/PROJECT_HEALTH_DASHBOARD.md` as its human-readable output.

The dashboard is mandatory after Validation Maintenance and Update, before Release Readiness, whenever a gate changes and at release closure. It summarizes evidence but cannot replace or override gate decisions.

## Consequences

- Release blockers become visible and traceable.
- Quality, security, performance, documentation, validation, publication and Final Release decisions are explicit gates.
- Static analysis, layered tests, accessibility, compatibility verification, repository documentation and publication readiness are first-class workflow activities.
- Dashboard maintenance becomes part of Definition of Done, validation and handoff.
