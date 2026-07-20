# BTDoor Security+ 6.0.1 release checklist

## Repository

- [ ] `manifest.json` and `INTEGRATION_VERSION` both equal `6.0.1`.
- [ ] HACS validation passes.
- [ ] Hassfest validation passes.
- [ ] Python critical lint and regression tests pass.
- [ ] `RELEASE_NOTES_6.0.1.md` is present.

## Regression scope

- [ ] Cloud authentication and gateway discovery remain healthy.
- [ ] SIP registers successfully over TLS.
- [ ] Gate opening returns a successful SIP response.
- [ ] Device and entity identifiers remain unchanged.
- [ ] Existing user-defined device names remain unchanged.

## Timeline fix

- [ ] Generate a fresh Support Bundle.
- [ ] Verify `sip/timeline-summary.json` contains recognized SIP methods and response classes.
- [ ] Verify the sum of `events_by_type` equals `event_count`.
- [ ] Verify valid `INVITE`, `CANCEL`, `MESSAGE`, `REGISTER`, and SIP responses are not classified as `unknown`.

## Release

- [ ] Merge the validated maintenance branch into `main`.
- [ ] Create annotated tag `v6.0.1`.
- [ ] Verify the GitHub Release archive and SHA-256 asset.
- [ ] Install or update Home Assistant and perform the final Support Bundle validation.
