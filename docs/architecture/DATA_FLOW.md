# Data Flow

**Status:** Active

```mermaid
sequenceDiagram
    participant Remote as BTicino / Netatmo
    participant Client as Cloud or SIP client
    participant Runtime as Entry runtime
    participant Bus as Internal event bus
    participant Model as Runtime/device model
    participant Entity as HA entity
    participant HA as Home Assistant

    Remote->>Client: remote update or SIP message
    Client->>Runtime: parsed transport result
    Runtime->>Bus: normalized domain event
    Bus->>Model: update entry-local state
    Bus->>Entity: dispatcher/event callback
    Entity->>HA: async_write_ha_state
    Bus->>HA: optional public integration event
```

## Inbound flow

1. Transport clients receive cloud or SIP data.
2. Parsers validate shape and normalize values.
3. Runtime converts transport data to domain events and models.
4. Entry-local subscribers update journal, timeline, diagnostics and entities.
5. Only explicitly supported events are published to Home Assistant.

## Action flow

```mermaid
sequenceDiagram
    participant Caller as UI / Automation / Assistant
    participant HA as Home Assistant
    participant Router as Service or entity router
    participant Runtime as Target runtime
    participant SIP as SIP client
    participant Door as Door station

    Caller->>HA: entity action or service call
    HA->>Router: validated request
    Router->>Runtime: resolve exact entry
    Runtime->>SIP: execute validated command
    SIP->>Door: protocol operation
    Door-->>SIP: result
    SIP-->>Runtime: normalized outcome
    Runtime-->>HA: state/event/audit update
```

## Data classification

| Class | Examples | Persistence rule |
|---|---|---|
| Public metadata | integration version, supported feature | may be documented/exported |
| Operational | connection status, counters, timestamps | persisted only when required |
| Personal | caller identity, images, audio, journal details | minimize and protect |
| Secret | tokens, private keys, certificate secrets | never log or export |

## Redaction boundary

All diagnostic and support outputs pass through `support_sanitizer.py`; producers must still avoid creating secret-bearing payloads.
