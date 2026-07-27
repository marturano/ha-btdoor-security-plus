# Roadmap 1.x — BTDoor Core Platform

## 1.0 — Foundation
Core runtime, config flow, registry integration, normalized events, diagnostics, support bundle, SIP/media/dashboard/Assist foundations.

## 1.1 — Core Stable
Stable lifecycle, gate control, reject current call, Call Journal maintenance, Voice Bridge, Alexa, Google preparation, translations, compatibility evidence, API and architecture freeze.

Remaining release gates include the certificate-expiry sensor, exact Home Assistant CI coverage, runtime lifecycle validation, real-device Google validation and dedicated authorization regressions.

## 1.2 — Universal Door Security Bridge
Capability model, protocol adapters, discovery, multi-gateway support, normalized device profiles and adapter conformance tests.

## 1.3 — Advanced Media Foundation
Snapshot pipeline, cache, codec handling, retention, media sessions, diagnostics, privacy controls and WebRTC/RTSP preparation.

## 1.4 — Audio & Call Control
Answer, reject and terminate calls; bidirectional audio; microphone, speaker, mute and volume controls; intercom; advanced SIP state; recovery and auditable voice-assistant actions.

## 1.5 — Voicemail Center
Configurable greeting and absence modes, audio/video message capture where supported, local archive, retention, transcription, AI summary, notification and secure export/delete services.

## 1.6 — Multimedia Timeline
Unified chronology for calls, access events, media, voicemail, motion, security and notifications with correlation IDs, filters, search, export and incident views.

## 1.7 — BTicino / Netatmo Security Cameras
Indoor/outdoor cameras, live view, snapshot, motion/person/animal/vehicle events, floodlight/siren where supported, Home + Security integration, privacy mode and timeline correlation.

## 1.8 — Smart Notifications
Priorities, categories, deduplication, rate limiting, quiet hours, acknowledgement, escalation, retries, images/clips, secure quick actions, companion app, voice announcements and provider-neutral delivery.

## 1.9 — AI Vision & Recognition
Provider-neutral person, known/unknown identity, object and scene recognition compatible with Home Assistant camera/image/image_processing/ai_task sources and external integrations such as Frigate, Scrypted, DOODS, Double Take, CodeProject.AI, CompreFace, ONVIF and MQTT.

Mandatory controls: local-first preference, explicit consent for face recognition, zone masking, separate metadata/media retention, cloud cost controls, audit and prohibition of access unlock based solely on face recognition.

## 1.10 — Core Consolidation & Migration
Contract tests, deprecation policy, storage migrations, performance/security hardening, stable event schemas and preparation for the ecosystem expansion.
