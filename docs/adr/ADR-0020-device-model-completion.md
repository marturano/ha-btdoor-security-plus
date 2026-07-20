# ADR-0020: Device Model completion

## Decision

Every logical runtime device exposed through the Home Assistant Device Registry must own at least one native entity. Cloud and Dialog state are read through the stable Runtime State Provider API.

## Consequences

The Cloud Runtime and Dialog Runtime are visible and useful in the device page, while existing entity unique IDs and Recorder history remain unchanged.
