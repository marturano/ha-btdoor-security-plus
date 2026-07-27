# Contributing

Preserve asynchronous safety, per-entry isolation, stable device/entity identities and centralized sanitization. Do not perform blocking file or platform operations on Home Assistant's event loop. Do not add network calls to entity properties.

Architecture-affecting changes require an ADR and an Engineering Notebook entry. Update changelog, compatibility evidence and translations in the same change. Physical-gate commands require explicit intent and must never run during setup, migration, reload or retry.

The 1.1 branch is stabilization-only: do not introduce 1.2 adapters or claim compatibility with unknown firmware. New user-facing English strings must be added to every supported project locale with identical placeholders.
