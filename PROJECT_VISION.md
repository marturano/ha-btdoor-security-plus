# BTDoor Platform — Project Vision

## Mission

BTDoor Platform is a Home Assistant-first platform for connected access, video door entry, security and, progressively, the wider BTicino/Netatmo ecosystem. It begins with BTDoor Security+ and evolves through explicit product lines rather than by turning one integration into an unstructured monolith.

## Product family

- **BTDoor Security+** — access, video door entry, calls, media and security.
- **BTDoor Home+** — lighting, sockets, shutters, scenes and connected electrical systems.
- **BTDoor Energy+** — BTDIN, metering, load management and energy orchestration.
- **BTDoor Climate+** — Smarther, thermostats, valves and climate zones.
- **BTDoor AI+** — interoperable vision, speech and contextual intelligence.
- **BTDoor Developer Platform** — SDK, extension framework, tooling and marketplace.

## Strategic release lines

- **1.x — BTDoor Core Platform**
- **2.x — BTicino/Netatmo Ecosystem Platform**
- **3.x — Developer Platform**
- **4.x — Intelligent Whole-Home Platform**
- **5.x — Enterprise & Professional Platform**

## Principles

1. Home Assistant remains the primary runtime and user experience.
2. Local-first operation is preferred whenever device and protocol capabilities allow it.
3. Cloud services are optional, explicit and privacy-aware.
4. Public APIs are versioned, documented and protected by contract tests.
5. AI is provider-neutral and must support local and external integrations.
6. Security-sensitive actions require explicit authorization and auditable execution.
7. Existing Home Assistant integrations are composed with, not needlessly duplicated.
8. Future compatibility claims must be backed by evidence.

## Scope boundary

BTDoor Platform does not replace Home Assistant automation, storage, identity or dashboard systems. It provides domain-specific entities, services, events, diagnostics, media pipelines and integrations that fit those systems.

## Documentation continuity

Documentation quality is equal to code quality. The platform is not releasable unless implementation, architecture, roadmap, compatibility, security, translations, evidence, archive history, and PCP are synchronized. A future Documentation Platform is planned for 4.3, while repository Markdown remains the source of truth.
