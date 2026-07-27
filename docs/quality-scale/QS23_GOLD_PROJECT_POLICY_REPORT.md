# QS-23 Gold Project Policy Report

## Scope

QS-23 converts the project decision to remain at Quality Scale Gold into an executable workflow rule. No runtime integration behaviour is changed.

## Governed policy

| Setting | Required value |
|---|---|
| Release minimum | Gold |
| Desired tier | Gold |
| Maximum governed tier | Gold |
| Platinum | Out of scope unless explicitly reopened by project decision |

## Enforcement

`tools/quality_scale/quality_scale_workflow.py check` now verifies that:

1. the generated current tier is Gold;
2. release minimum, desired tier and maximum governed tier are all Gold;
3. the Gold release gate passes;
4. the policy has not been silently changed;
5. release advancement is blocked on any Gold regression.

The Quality Scale engine still reports Bronze, Silver, Gold and Platinum rule states for transparency, but its project target and release gate are Gold.

## Runtime impact

None. Changes are limited to governance tooling, tests, reports, roadmap policy, documentation and handoff.

## Decision

Gold is the stable Quality Scale target for the whole project and all release lines unless a future ADR explicitly changes the policy.
