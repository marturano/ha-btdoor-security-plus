# BTDoor Security+ 6.0.0 release checklist

## Repository gate

- [ ] Default branch contains the exact validated 6.0.0 runtime.
- [ ] `manifest.json` and `INTEGRATION_VERSION` both equal `6.0.0`.
- [ ] HACS validation passes without ignored checks.
- [ ] Hassfest passes.
- [ ] Python compilation and release regression tests pass.
- [ ] `LICENSE`, `README.md`, `hacs.json`, and release notes are present.

## Publication gate

- [ ] Create and push annotated tag `v6.0.0`.
- [ ] Confirm the Release package workflow completes.
- [ ] Publish a GitHub Release, not only a tag.
- [ ] Attach the generated ZIP and SHA-256 file.
- [ ] Verify HACS detects `v6.0.0` as the remote version.

## Installation gate

- [ ] Perform a clean HACS installation on Home Assistant 2026.7 or newer.
- [ ] Upgrade one existing rc.3g installation without deleting the Config Entry.
- [ ] Restart Home Assistant and verify version `6.0.0`.
- [ ] Confirm the six expected registry devices and no duplicates.
- [ ] Confirm localized Italian names and preserved `name_by_user`.
- [ ] Execute a successful gate-opening command.
- [ ] Generate and archive a final Stable Support Bundle.
- [ ] Confirm Health Score 100, Cloud OK, SIP registered, TLS active, and no errors.

## Post-release tracking

The following are not 6.0.0 blockers and must be tracked separately:

- SIP timeline summary classifies events as `unknown`.
- TLS server identity verification is disabled in the current runtime.
- Support Bundle does not export entity and area registry invariants.
- Full guided Repairs coverage remains incomplete.
