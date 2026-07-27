# ADR-0071: QS-3 Sensor Platform Coverage

## Status
Accepted

## Context
After QS-2, `sensor.py` contained 713 uncovered statements and represented the highest-value low-runtime-risk coverage target.

## Decision
Add behavioural, repository-local tests that load the actual sensor platform with controlled Home Assistant stubs and exercise every public sensor class, setup mode, listener path, API fallback, and meaningful branch.

## Consequences
- `sensor.py` coverage rises to 98.74%.
- Total integration coverage rises from 40.59% to 53.24%.
- Silver remains blocked until total measured coverage exceeds 95%.
- The next coverage batch targets services, cloud, integration setup, and SIP runtime modules.
