# Compatibility

BTDoor Security+ targets **Home Assistant Core 2026.x**. Home Assistant 2026.7.x is the primary release-validation environment, while the minimum supported 2026.x release is accepted only after the compatibility gates pass. Import success alone is not proof of runtime compatibility.

Evidence is recorded separately for compilation, automated tests, Home Assistant runtime, physical gateway, Alexa and Google Assistant. Clean installation, supported upgrade, setup, reload, unload, restart, registry identity and multi-entry isolation are mandatory Stable gates.

Alexa has real-user discovery and operation evidence. Google Assistant is architecturally supported through Home Assistant entity exposure but is currently marked unverified. See `../../compatibility/COMPATIBILITY_MATRIX.md` for exact status.
