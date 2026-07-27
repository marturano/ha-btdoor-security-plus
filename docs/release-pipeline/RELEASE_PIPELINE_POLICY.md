# Release Pipeline Policy

1. `custom_components/btdoor_security_plus/manifest.json` is the technical version source of truth.
2. Every artifact must be reproducible, inventoried and protected by SHA-256.
3. A candidate artifact may be generated while gates are blocked, but must be marked `candidate_only: true`.
4. Publication requires both an approved Release Decision and an approved Release Certification.
5. The pipeline must never change governance evidence or promote a version automatically.
6. Secrets, caches, bytecode, test output and local runtime evidence are excluded from distributable archives.
