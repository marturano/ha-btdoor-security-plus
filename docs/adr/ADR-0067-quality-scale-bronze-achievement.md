# ADR-0067: Quality Scale Bronze Achievement

## Status
Accepted — 2026-07-22

## Decision
BTDoor Security+ records Home Assistant Integration Quality Scale **Bronze** as achieved through repository-level self-assessment after adding executable behavioural coverage for the complete config-flow outcome set.

The evidence consists of `tests/test_config_flow_full_coverage.py` and `docs/quality-scale/config_flow_coverage.json`. The Quality Scale engine must verify both the required scenarios and the validated evidence manifest before marking `config-flow-test-coverage` complete.

## Boundaries
Bronze is not an official Home Assistant Core certification and does not replace target runtime, HACS lifecycle, security, UX/accessibility, or publication evidence. Final release approval remains governed by all independent release gates.

## Consequences
The minimum Quality Scale release gate now passes. Improvement work continues toward Silver, Gold, and Platinum, beginning with availability transition logging and measured test coverage.
