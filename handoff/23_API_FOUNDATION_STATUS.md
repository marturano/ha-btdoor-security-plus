# API Foundation Status

Release: **1.1.0-rc.15**
Phase: **RC.15 Phase 5**
Status: **Documentation and governance foundation complete**

## Completed

- Canonical API index and current entity contract.
- Documentation for all eleven registered Home Assistant actions.
- Public event, error, security and versioning contracts.
- Alexa, Alexa+ and Google Assistant exposure boundary.
- Automation examples and explicit REST/WebSocket roadmap status.
- ADR-0054 through ADR-0056.
- Strengthened `api` and new `voice_assistant_api` gates.

## Runtime truth

No BTDoor-specific REST endpoint, WebSocket command, Alexa skill or Google cloud-to-cloud implementation is added by this phase. External assistants consume entities exposed by Home Assistant.

## Next coherent work unit

Developer Platform Foundation, followed by runtime/test stabilization in a Home Assistant 2026.7 environment.
