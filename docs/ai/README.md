# AI Platform Foundation

Status: Architecture foundation; no provider adapter is declared runtime-complete in RC.15.

The AI platform is provider-neutral. Callers request a capability, the policy layer authorizes data handling, the orchestrator selects an eligible provider, and results are normalized before entering Home Assistant automations or events.

## Canonical documents

- [Platform architecture](AI_PLATFORM.md)
- [Runtime and orchestration](AI_RUNTIME.md)
- [Provider interface](PROVIDER_INTERFACE.md)
- [Provider capability matrix](PROVIDER_CAPABILITIES.md)
- [Prompt engine](PROMPT_ENGINE.md)
- [Vision pipeline](VISION_PIPELINE.md)
- [Voice pipeline](VOICE_PIPELINE.md)
- [OCR pipeline](OCR_PIPELINE.md)
- [Face recognition](FACE_RECOGNITION.md)
- [Object detection](OBJECT_DETECTION.md)
- [Event normalization](EVENT_NORMALIZATION.md)
- [Automation integration](AUTOMATION.md)
- [Local models](LOCAL_MODELS.md)
- [Cloud models](CLOUD_MODELS.md)
- [Privacy and governance](PRIVACY.md)
- [Performance and observability](PERFORMANCE.md)

Legacy overview pages remain as compatibility entry points and must link back to this index.
