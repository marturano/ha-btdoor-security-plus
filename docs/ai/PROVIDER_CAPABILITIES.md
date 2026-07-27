# Provider Capabilities

## Capability vocabulary
`chat`, `vision`, `ocr`, `face_recognition`, `object_detection`, `speech_to_text`, `text_to_speech`, `embeddings`, `summarization`, `translation`, `reasoning`.

## Target matrix

| Provider family | Mode | Text | Vision/OCR | Speech | Identity | RC.15 runtime status |
|---|---|---:|---:|---:|---:|---|
| Home Assistant Assist / AI Task | Local/Cloud | Yes | Platform-dependent | Platform-dependent | No | Contract only |
| OpenAI | Cloud | Yes | Yes | Yes | No | Contract only |
| Anthropic Claude | Cloud | Yes | Yes | No | No | Contract only |
| Google Gemini | Cloud | Yes | Yes | Yes | No | Contract only |
| Amazon Rekognition | Cloud | No | Yes | No | Yes | Contract only |
| Ollama / LocalAI / llama.cpp | Local | Model-dependent | Model-dependent | Model-dependent | No | Contract only |
| Frigate / DOODS / CodeProject.AI | Local | Limited | Detection | No | Limited | Contract only |
| Double Take / CompreFace | Local | No | No | No | Yes | Contract only |

Availability must be discovered at runtime and never inferred solely from provider brand.
