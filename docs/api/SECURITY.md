# API Security and Authorization

## Trust boundary

Home Assistant authentication, authorization, context and exposure configuration remain the outer control plane. BTDoor Security+ adds target isolation, audit metadata, redaction and safe failure behavior.

## Physical commands

- Gate opening must resolve to exactly one loaded config entry.
- `reason`, `source`, Home Assistant context/user ID and `request_id` support auditing.
- Voice-assistant exposure is opt-in and must be reviewed separately for Alexa, Alexa+ and Google Assistant.
- AI, face recognition or object detection may inform an automation but must not be the sole authorization factor for unlocking/opening.

## Data minimization

Event and response payloads should contain only what consumers need. Support bundles and call-journal exports are private artifacts and must retain restrictive filesystem permissions.

## External integrations

External systems interact through Home Assistant entities, actions and events. They must not receive SIP credentials, certificate private keys or internal dispatcher access.
