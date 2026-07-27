# Decisions and Constraints

1. The canonical product history is 1.0 Foundation → 1.1 Core Stable → roadmap 1.2–2.0.
2. Older 3.x–6.x labels are provenance only and do not define parallel products.
3. Compatibility target: Home Assistant Core 2026.x.
4. Primary final-validation environment: Home Assistant 2026.7.x.
5. Minimum supported release: 2026.1.0 only after the compatibility matrix gates pass.
6. The native gate action is `button.apri_cancello`.
7. The optional assistant bridge is `switch.apri_cancello_alexa` on `DeviceKind.VOICE_BRIDGE`, without `via_device`.
8. No dashboard may use the retired gate cover model.
9. Commands require explicit action, exact config-entry resolution and no blind retry.
10. Setup, migration, reload, restart, diagnostics and restoration must never open the gate.
11. Unique IDs, device/config-entry identifiers, names, areas and registry preferences are preserved.
12. Support data is centrally sanitized; credentials, secrets and private paths are never exported.
13. Unknown firmware/protocol behavior fails closed.
14. Future pairing uses owner-authorized revocable identities where technically available.
15. No identity cloning, extracted-secret distribution, TLS/auth bypass or false certification claims.
16. Google Assistant is marked unverified until a real account/device test is recorded.
17. Runtime evidence and source code are distinct release inputs.
