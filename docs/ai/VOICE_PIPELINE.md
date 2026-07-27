# AI Voice Pipeline

This document covers AI speech capabilities and complements the core voice pipeline.

Inputs may originate from Home Assistant Assist, door-station audio or automation text. The platform may request transcription, synthesis, translation or summarization.

```mermaid
flowchart LR
    INPUT[Audio or text] --> POLICY[Privacy and consent]
    POLICY --> CAP[STT / TTS / translation]
    CAP --> RESULT[Normalized transcript or audio reference]
    RESULT --> ASSIST[Assist / notification / automation]
```

Biometric voice identification is outside the initial contract.
