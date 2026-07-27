# Project Health Dashboard Status

The canonical dashboard is `docs/project/PROJECT_HEALTH_DASHBOARD.md`; its structured source is `docs/project/project_health.json` and its renderer is `tools/update_project_health.py`.

This handoff must never copy stale scores. Read the canonical dashboard directly, then verify every blocking domain against its underlying evidence.

## Resume rule

Before Release Readiness, run the affected checks, update canonical registers and reports, update `project_health.json`, execute `python tools/update_project_health.py`, and include the regenerated dashboard in Validation Maintenance and Update.

## Automated indicators

Run `python tools/health/calculate_health.py` before rendering the dashboard. The calculated artifact is `docs/project/project_health_calculated.json` and reports both evidence-adjusted Health Score and Governance Compliance Score. These indicators do not override blocked gates.
