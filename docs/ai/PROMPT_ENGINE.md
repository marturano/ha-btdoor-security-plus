# Prompt Engine

Prompts are versioned templates with declared capability, inputs, output schema, privacy class and locale. Templates must avoid embedding credentials or raw Home Assistant secrets.

## Processing

```mermaid
flowchart LR
    TEMPLATE[Versioned template] --> BIND[Validated input binding]
    BIND --> CONTEXT[Allowed HA context]
    CONTEXT --> POLICY[Policy filtering]
    POLICY --> REQUEST[Normalized AI request]
```

Prompt changes that alter automation-visible output require schema versioning and release notes.
