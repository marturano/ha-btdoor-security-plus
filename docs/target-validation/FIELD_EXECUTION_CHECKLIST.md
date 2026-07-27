# Field Execution Checklist — Phase 7C

Use this checklist on supported Home Assistant 2026.x target instances. Include at least one complete run on the 2026.7.x reference target. It does not replace `result.json`; it defines the operator sequence and evidence expected for each blocking evidence ID.

## Preconditions

- Install the exact repository package being certified.
- Record Home Assistant version and installation type.
- Create a dedicated long-lived access token for the validation session; remove it when finished.
- Do not store tokens, passwords, SIP credentials, serial numbers, MAC addresses, public URLs or personal images in evidence.
- Enable debug logging only for the shortest necessary interval.

## Create the run

```bash
python tools/target_validation/target_validation.py init --run-id ha-2026.7-<date>-<operator>
```

Set `HA_URL` and `HA_TOKEN`, then collect the non-secret environment snapshot:

```bash
python tools/target_validation/target_validation.py collect --run-id ha-2026.7-<date>-<operator>
```

The collector stores only the host label, never the token or full URL.

## EV-PERF-002 — Runtime and performance

- Measure Home Assistant restart-to-integration-ready time.
- Measure Config Entry reload completion time.
- Record memory before setup and after a stable observation interval.
- Observe the integration for at least 30 minutes without unhandled exceptions, leaked tasks or growing memory.
- Record reconnect time after a temporary device/network interruption.

Recommended evidence:

- sanitized timestamped log extract;
- measurement CSV or Markdown table;
- System Information screenshot with sensitive fields removed;
- before/after memory snapshot.

## EV-COMP-001 — Home Assistant compatibility

- Clean setup through the UI.
- Full Home Assistant restart and automatic recovery.
- Config Entry reload.
- Entity and Device Registry continuity.
- Temporary unavailable state and recovery.
- Diagnostics export from the integration page.
- Remove and re-add the Config Entry.

Acceptance requires no unexpected traceback, no duplicate device/entity and no loss of stable unique IDs.

## EV-PUB-001 — HACS lifecycle

- Add the GitHub repository as a custom integration repository.
- Clean install from a release asset.
- Restart Home Assistant and complete setup.
- Upgrade from the previous supported RC/release.
- Roll back to the previous release.
- Reinstall the candidate and verify configuration continuity.

Retain HACS screenshots, installed version evidence and sanitized Home Assistant logs.

## EV-SEC-002 — Runtime security

- Review diagnostics and support bundle redaction.
- Search logs for tokens, passwords, SIP secrets, certificate material and personal identifiers.
- Confirm actions fail safely and expose translated user-facing errors.
- Confirm no credentials are written to the repository or target-validation evidence.
- Record dependency review output from CI or the release environment.

## EV-UX-001 — UX and accessibility

- Complete setup, options, reconfigure and repair flows using keyboard navigation.
- Review labels, descriptions, errors and entity names in Italian and English.
- Verify dashboard cards remain readable in light and dark themes.
- Verify controls provide clear state feedback and destructive actions require intentional confirmation.
- Record any known limitation explicitly.

## Finalize

For every check in `result.json`:

1. set `status` to `VALIDATED` only after the check passes;
2. enter measured `value` and `unit` where applicable;
3. reference one or more sanitized files under `evidence/`;
4. set each completed section to `VALIDATED`;
5. complete operator attestation.

Then run:

```bash
python tools/target_validation/target_validation.py status --run-id <id>
python tools/target_validation/target_validation.py validate --run-id <id>
python tools/target_validation/target_validation.py import --run-id <id>
python tools/certification/run_certification.py
python tools/release/release_decision.py
```

The run must not be imported when any check failed, was skipped, lacks evidence or was executed outside the supported Home Assistant 2026.x series. Final Phase 7C closure additionally requires a complete 2026.7.x reference-target run.
