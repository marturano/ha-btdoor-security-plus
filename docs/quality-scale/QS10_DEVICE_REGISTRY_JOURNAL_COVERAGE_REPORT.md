# QS-10 Device Registry and Journal Coverage Report

## Scope

QS-10 adds executable behavioural coverage for logical-device registration, visibility cleanup, metadata migration, topology validation, translation reporting, and persistent Call Journal lifecycle handling.

## Measured result

- Previous measured coverage: **76.56%**
- QS-10 measured coverage: **79.23%**
- Increase: **2.67 percentage points**
- Covered statements: **4414 / 5571**
- Missing statements: **1157**

## Module results

- `device_model/manager.py`: **100%**
- `managers/device_manager.py`: **85%**
- `call_journal/journal.py`: **94%**

## Validation

- Main suite excluding nested certification launchers: PASS after coverage evidence generation.
- Runtime release certification launcher: PASS in an isolated process.
- Target validation pack launcher: PASS in an isolated process.
- QS-10 test module: 4 PASS.
- Quality Scale Engine: Bronze PASS.
- Silver remains blocked because total measured coverage does not exceed 95%.

## Next priority

QS-11 should cover cloud provisioning residuals, SIP reader/request dispatch, adapter foundations, and the remaining runtime-state and diagnostic branches.
