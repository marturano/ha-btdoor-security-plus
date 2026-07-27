# Governance Automation Framework

## Status

Implemented for Phase 6A and mandatory for subsequent package changes.

## Purpose

The framework turns project governance into repeatable checks without replacing human review. It verifies the existence, consistency and traceability of governed evidence, then produces machine-readable results.

## Entry point

```bash
python tools/governance/run_governance.py
```

The command runs:

1. governance document and workflow validation;
2. handoff continuity validation;
3. release-readiness structural validation;
4. repository integrity suite;
5. repository hygiene/orphan validation;
6. repository rationalization, canonical-reference and dependency validation;
7. health and compliance calculation.

The consolidated report is written to:

```text
docs/validation/governance-automation-report.json
```

## Health and compliance

`tools/health/calculate_health.py` generates `docs/project/project_health_calculated.json`.

- **Health Score** combines governed domain scores, gate status and evidence coverage.
- **Compliance Score** measures whether mandatory evidence paths exist.

These scores cannot override a blocked gate, an incomplete review or missing runtime evidence.

## Maintenance rule

Update the underlying evidence first. Run the framework after every meaningful repository change and during Validation Maintenance and Update, Release Readiness and Handoff closure.

## Repository rationalization

`tools/repository/analyze_repository.py --check` validates the canonical registry, Markdown links, exact active-document duplication and deprecated aliases, then regenerates the dependency graph and repository metrics.
