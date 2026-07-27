# AI Platform Foundation Status

Release: **1.1.0-rc.15**
Phase: **RC.15 Phase 4**
Status: **Documentation and governance foundation complete**

## Completed

- Canonical AI documentation set and index.
- Capability-based orchestration and provider adapter contracts.
- Provider capability matrix covering Home Assistant, OpenAI, Claude, Gemini, Rekognition and local provider families.
- Privacy classification, policy-first dispatch and local-first strategy.
- Vision, voice, OCR, face, object, automation, normalization and performance contracts.
- ADR-0050 through ADR-0053.
- `ai_documentation` and `provider_capability` blocking gates.

## Runtime truth

No external AI provider adapter, AI service, biometric store or provider credential flow is implemented by this phase. Those require code, config flow, conformance tests, security review and Home Assistant runtime validation.

## Next coherent work unit

API Foundation: stabilize public entity, service, event, WebSocket and external integration contracts, then link future AI services to those stable APIs.

## Full-suite limitation observed in Phase 4

The focused RC.15 Phase 1–4 suite passes (13 tests). The legacy full repository suite is not a release-pass signal in this isolated environment: three modules fail collection because Home Assistant/runtime package surfaces are unavailable, and the remaining broad run reports 17 historical failures, mostly stale release-version assertions plus pre-existing runtime/import expectations. Phase 4 changes are documentation, governance, tests and integrity tooling only; these failures were not introduced or hidden. They must be triaged during stabilization with a real Home Assistant test environment.
