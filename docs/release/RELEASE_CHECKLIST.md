# Mandatory Release Checklist

A release is not complete until every applicable item is satisfied or explicitly marked blocked with evidence.

## Code and packaging

- Version synchronized in manifest, constants, project manifest, release notes, validation, and handoff.
- Python and JSON/YAML syntax checks pass.
- No cache, secret, support bundle, or transient artifact is packaged.
- ZIP and SHA-256 are generated from the validated tree.

## Documentation

- README, CHANGELOG, Project Vision, architecture, roadmap, API, ecosystem, AI, security, performance, install, developer, dashboard, and blueprint documentation reviewed.
- Documentation changelog records created, changed, deprecated, archived, and removed files.
- Internal links and canonical entry points validated.
- Superseded normative documents archived with traceability.

## Localization

- UI strings and translations have equal key coverage.
- Required user documentation exists for every supported locale.
- Release notes and release summary are available in every supported locale.
- Translation limitations are recorded in the PCP.

## Governance and continuity

- ADR created or updated for significant decisions.
- Roadmap and backlog synchronized.
- PCP 2.0 complete, including Project Execution Contract, Project Memory, status reports, and Recovery Prompt.
- No critical knowledge remains only in the conversation.

## Validation

- Relevant regression tests pass.
- Full test limitations are stated honestly.
- Compatibility claims identify evidence level: static, simulated, or real-device.

## Repository Integrity Suite

- `python tools/check_repository_integrity.py` passes.
- Roadmap milestone identifiers are unique and ordered.
- Governance Charter, Definition of Ready, and Definition of Done are current.
- Continuity Status, Integrity Suite Results, and Recovery Prompt name the current release.
- A conversation handoff is permitted only after the continuity checklist is complete.

## Project Health and formal gates

- [ ] Project Health Dashboard regenerated from canonical evidence.
- [ ] All applicable workflow gates have documented PASS, PASS WITH CONDITIONS, BLOCKED or NOT APPLICABLE decisions.
- [ ] No BLOCKED gate remains for the requested release type.

## Exact-package GitHub Actions gate

- [ ] `python tools/validation/check_github_workflows.py` passes.
- [ ] `Validate / HACS` is green for the exact commit.
- [ ] `Validate / Hassfest` is green for the exact commit.
- [ ] `Validate / Python, governance and repository gates` is green and its evidence artifact is retained.
- [ ] Every Home Assistant compatibility matrix job is green or an explicitly approved matrix correction is documented.
- [ ] `GitHub Sandbox Validation` is green and confirms a clean tree after validation.
- [ ] `Governance` is green and generated canonical documents are unchanged.
- [ ] No result inferred only from workflow syntax is recorded as PASS.
- [ ] The release archive is built from the validated commit and its SHA-256 is recalculated after final packaging.

See [GitHub Actions Validation Contract](../validation/GITHUB_ACTIONS_VALIDATION.md).
