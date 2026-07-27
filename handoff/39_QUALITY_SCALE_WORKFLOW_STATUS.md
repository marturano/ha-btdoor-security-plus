# Quality Scale Workflow Status

**Phase:** Workflow integration active  
**Current level:** BRONZE  
**Release minimum:** BRONZE  
**Desired level:** GOLD  
**Quality Scale advancement:** ALLOWED

## Permanent workflow rule

Every future phase must run the Quality Scale workflow before and after implementation, refresh the remediation plan, apply safe deterministic improvements, implement evidence-backed manual improvements where in scope, and update governance and handoff.

## Bronze evidence

`config-flow-test-coverage` is validated by executable behavioural tests in `tests/test_config_flow_full_coverage.py` and the evidence manifest `docs/quality-scale/config_flow_coverage.json`. The engine verifies the complete required scenario set and does not accept a simple keyword match.

## Remaining progression

Gold is the configured release minimum, desired level and maximum governed tier. Any regression below Gold blocks advancement. Platinum is informational and out of scope unless explicitly reopened by ADR.

## Resume command

```bash
python tools/quality_scale/quality_scale_workflow.py run
```
