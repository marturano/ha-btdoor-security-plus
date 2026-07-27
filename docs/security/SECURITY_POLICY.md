# Security Policy

## Scope

Secure development, credentials and secrets, privacy and logging, dependencies and supply chain, network/API/webhook/MQTT/SIP behavior, Home Assistant permissions, physical actions, external AI providers, vulnerability management and release criteria.

## Mandatory rules

- Never commit secrets, credentials, private keys or unredacted support data.
- Apply least privilege and explicit target isolation for physical actions.
- Validate all external input and payloads; use bounded retries and timeouts.
- Redact tokens, personal data, images, audio and identifiers from diagnostics.
- Document data sent to ChatGPT, Claude, Gemini, Amazon Rekognition, Alexa/Alexa+ or other providers, including consent, retention and fallback behavior.
- Review dependencies, GitHub Actions and release provenance.
- Record vulnerabilities, severity, remediation and disclosure decisions.
- A security-impacting change cannot release without an updated security review.
