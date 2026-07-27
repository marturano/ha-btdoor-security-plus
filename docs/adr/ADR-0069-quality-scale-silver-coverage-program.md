# ADR-0069: Quality Scale Silver Coverage Program

## Status
Accepted

## Decision
Suspend feature evolution while QS-1 raises measured integration coverage above the Home Assistant Silver threshold. Work proceeds in measured test batches ordered by uncovered executable lines. The coverage gate disables pytest's cache provider so evidence generation does not contaminate repository-integrity checks.

## Evidence from this increment
- Added behavioural tests for runtime-summary mapping, visibility policy, and dashboard resolution/building.
- Coverage increased from 34.27% to 35.54%.
- Full suite passes with 240 tests.
- Silver remains blocked because the measured result is below 95%.
