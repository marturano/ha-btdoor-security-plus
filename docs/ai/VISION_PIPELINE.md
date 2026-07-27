# Vision Pipeline

## Scope
Camera snapshots, image entities and externally supplied media may be analyzed for scene description, OCR and object detection.

```mermaid
flowchart LR
    SOURCE[Camera / Image / Event media] --> CONSENT[Consent and privacy check]
    CONSENT --> PREP[Resize / mask / redact]
    PREP --> PROVIDER[Vision capability]
    PROVIDER --> NORMALIZE[Normalized detections]
    NORMALIZE --> EVENT[HA event / notification / timeline]
```

Cloud upload requires explicit policy approval. Media retention and metadata retention are separate controls.
