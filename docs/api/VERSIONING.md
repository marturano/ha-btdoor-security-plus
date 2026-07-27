# API Versioning and Compatibility

## Current policy

RC.15 stabilizes documentation contracts but remains a release candidate. The integration version is independent from event `schema_version`.

## Compatible changes

- adding an optional response field;
- adding a new event type;
- adding an optional action field with a safe default;
- adding a new entity platform or entity role;
- clarifying documentation without changing behavior.

## Breaking changes

- renaming or removing an action, field, event type or documented entity role;
- changing field meaning or unit;
- changing target resolution so a physical command can reach a different device;
- making an optional field mandatory;
- exposing previously private data.

Breaking changes require an ADR, changelog entry, deprecation period where feasible, migration guidance and updated conformance tests.

## Future transports

REST and WebSocket contracts will carry explicit API versions when implemented. Internal Home Assistant APIs and Python imports are not substitutes for those future public versions.
