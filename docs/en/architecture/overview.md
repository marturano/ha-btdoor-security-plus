# Architecture overview

Each Home Assistant config entry owns one isolated gateway runtime. Cloud, SIP/TLS, dialog, media, event, persistence and diagnostics components normalize their state before entity platforms consume it. Entity properties are local reads and never initiate network access.

Global services and Assist intents resolve an exact config entry before sending a command. The physical gateway is the root device; Cloud, SIP, calls, media and diagnostics are logical devices. The Alexa / Google Gate Bridge is an independent virtual device with no `via_device` parent.

Gate commands require explicit user or service action, produce audit events and are not blindly retried. Diagnostics and Support Bundles pass through centralized sanitization. See `../../architecture/README.md` for the normative design.
