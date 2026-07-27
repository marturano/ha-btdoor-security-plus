# Architecture Principles

1. **Stable domain contracts** — entities, services and events are treated as public contracts once marked stable.
2. **Capability-driven design** — devices expose capabilities rather than vendor-specific assumptions.
3. **Layered adapters** — transport, protocol, device and Home Assistant entity layers remain separable.
4. **Event normalization** — all major runtime events use versioned schemas and correlation identifiers.
5. **Provider neutrality** — AI, media, notifications, storage and cloud services use replaceable provider contracts.
6. **Local-first resilience** — local control and graceful degradation are preferred where possible.
7. **Privacy by default** — facial recognition, cloud uploads and retention are opt-in.
8. **No silent privilege escalation** — access control actions are never inferred from low-confidence AI output.
9. **Observability without leakage** — diagnostics are useful but sanitized.
10. **Progressive platformization** — the 1.x and 2.x product lines validate domain models before the 3.x public SDK freezes them.
