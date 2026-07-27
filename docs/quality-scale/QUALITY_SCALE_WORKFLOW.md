# Home Assistant Quality Scale Workflow

**Status:** Mandatory project workflow component  
**Assessment:** repository self-assessment aligned with Home Assistant; not an official Core grade

## Purpose

The Quality Scale is evaluated at the beginning and end of every implementation phase. The workflow reports the current level, compares it with the configured desired level, creates a remediation plan and applies only changes that can be made safely and proven deterministically.

## Fixed Gold policy

- **Release minimum tier:** Gold. Falling below Gold blocks Release Readiness and publication.
- **Desired tier:** Gold.
- **Maximum governed tier:** Gold.
- **Platinum policy:** out of scope unless explicitly reopened by a new project decision and ADR. Platinum rules remain informational and are not remediation items.

The values are configured in `quality_scale_workflow.json` and must not be silently changed to make a gate pass.

## Mandatory cycle

1. Run the Quality Scale assessment before implementation.
2. Record current and desired levels.
3. Generate `QUALITY_SCALE_REMEDIATION_PLAN.json` and `.md`.
4. Apply safe automatic remediations.
5. Implement manual remediation items with tests and evidence.
6. Rerun the assessment after implementation.
7. Update validation, health, release decision, roadmap and handoff.
8. Block release advancement when the minimum tier is not achieved.

## Commands

```bash
python tools/quality_scale/quality_scale_workflow.py status
python tools/quality_scale/quality_scale_workflow.py plan
python tools/quality_scale/quality_scale_workflow.py apply
python tools/quality_scale/quality_scale_workflow.py run
python tools/quality_scale/quality_scale_workflow.py check
```

`check` is the strict release gate. `run` updates status and planning without falsely claiming that manual or runtime requirements are complete.

## Automation boundary

Automatic remediation is limited to deterministic documentation, metadata and validation scaffolding. The workflow may not automatically claim test coverage, runtime behaviour, strict typing, asynchronous dependency compliance or functional correctness. Those rules require implementation and validated evidence.
## Bronze achievement - 2026-07-22

Gold was achieved in QS-21 and became the permanent project target in QS-23. The strict workflow check blocks any regression below Gold and does not pursue Platinum.

