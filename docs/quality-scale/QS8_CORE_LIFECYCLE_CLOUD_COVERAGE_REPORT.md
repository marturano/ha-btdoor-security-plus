# QS-8 Core Lifecycle and Cloud Coverage Report

## Result

- Baseline coverage: **71.57%**
- Current cumulative coverage: **73.49%**
- Increase: **1.92 percentage points**
- Current Quality Scale tier: **Bronze**
- Silver test-coverage gate: **BLOCKED** (requires above 95%)

## Scope

QS-8 adds behavioural tests for integration unload, debug-storage migration, certificate-storage migration, certificate renewal success and error handling, config-entry schema migration, update-listener reload, and integration-wide setup.

`custom_components/btdoor_security_plus/__init__.py` increased from approximately **26%** to **67.84%** measured cumulative line coverage.

## Evidence method

The coverage evidence is the exact union of executed source lines from the previously validated QS-7 report and the isolated QS-8 pytest-cov run. No unexecuted line is marked covered. The full functional suite was validated in separate process groups because the certification and target-validation tests each launch nested certification subprocesses and can exceed the single-process execution limit when combined.

## Remaining work

Silver remains blocked by the aggregate coverage requirement. The next priorities are residual SIP transport branches, cloud provisioning branches, call journal, runtime-state providers, managers, adapters, voice and support modules.
