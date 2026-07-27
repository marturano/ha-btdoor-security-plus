# Official Workflow Reference

The authoritative workflow is `docs/project/WORKFLOW.md`.

This handoff file intentionally contains no duplicated workflow text in accordance with RG-004. Current execution state is maintained in `handoff/28_IMMEDIATE_RESUME_POINT.md` and the dedicated status handoffs.

## Canonical gate references

Release readiness and validation maintenance are governed exclusively by `docs/project/WORKFLOW.md` and its registered derived artifacts. This handoff does not duplicate those normative definitions.

## GitHub Sandbox Validation Gate
After local checks and before packaging any RC or Final release:
1. dispatch Ruff Remediation when Ruff errors exist;
2. review the generated commit and evidence;
3. run the read-only GitHub Sandbox Validation workflow;
4. require all publication, HACS/Hassfest, repository and Quality Scale gates to pass;
5. import evidence into release readiness and the Release Decision Engine;
6. package only the validated commit.
A failed check blocks progression and must be fixed without lowering the GOLD requirement.
