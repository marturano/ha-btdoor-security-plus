# Phase 7C — GitHub Publication Audit Handoff

**Package:** `1.1.0-rc.15-phase7c-github-publication-ready`

The repository is prepared for synchronization to GitHub. Local checks must not be substituted for HACS Action, hassfest or GitHub Actions results from the exact remote commit.

## Immediate resume point

1. Push this exact package to `marturano/ha-btdoor-security-plus` without introducing unreviewed changes.
2. Record the commit SHA.
3. Wait for and capture Governance and Validate workflow results.
4. Do not create HACS evidence from a different commit.
5. Create the `v1.1.0-rc.15` GitHub prerelease only after required checks pass.
6. Execute the HACS installation lifecycle and import sanitized evidence into the Target Validation Pack.

## Permanent rule

Repository GitHub validation precedes HACS installation. The remote commit, GitHub release asset and HACS-installed integration must be traceably identical.
