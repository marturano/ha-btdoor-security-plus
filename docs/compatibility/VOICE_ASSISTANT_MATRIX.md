# Voice Assistant Compatibility

| Assistant | Current position | Exposure path | Validation level |
|---|---|---|---|
| Home Assistant Assist | Native entity/action path | Home Assistant intent/entity model | Static/integration validation |
| Amazon Alexa | Optional button/switch exposure through Home Assistant | Home Assistant Cloud or manual Alexa integration | User runtime evidence for gate discovery/operation |
| Alexa+ | Separate validation target; no compatibility assumption beyond Alexa exposure architecture | Home Assistant exposure configuration | Unverified |
| Google Assistant | Entity exposure architecture documented | Home Assistant Cloud or manual Google Assistant integration | Real-device validation pending |

Only explicitly selected entities may be shared. Diagnostics and developer entities must remain private. Physical actions require target isolation, assistant-side safeguards and real-account validation.

See [`../api/VOICE_ASSISTANTS.md`](../api/VOICE_ASSISTANTS.md).
