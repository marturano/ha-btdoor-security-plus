# QS-23 Handoff — Gold Project Policy

## Completed

- fixed release minimum, desired tier and maximum governed tier to Gold;
- added strict workflow enforcement and regression blocking;
- excluded Platinum from active remediation;
- retained Platinum assessment only as informational transparency;
- added executable Gold-policy tests;
- updated canonical workflow, roadmap, Quality Scale documentation and handoff.

## Mandatory project rule

Every future phase must start and end with:

```bash
python tools/quality_scale/quality_scale_workflow.py check
```

The command must return success with:

- `current_tier = gold`;
- `gold_policy_verified = true`;
- `advancement_status = ALLOWED`.

Any result below Gold blocks release progression. Platinum must not be implemented or added to remediation work unless a new explicit ADR reopens that decision.

## Resume point

Continue with the remaining external certification and 1.1.0 Final stabilization gates while preserving Gold.
