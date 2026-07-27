# Execution Runbook

1. Prepare a recoverable Home Assistant 2026.x test instance.
2. Install the current release-candidate package through the intended HACS/custom-component path.
3. Create a certification run with a unique identifier.
4. Export `HA_URL` and a temporary long-lived access token as environment variables.
5. Run the API probe.
6. Restart Home Assistant and document recovery and entity continuity.
7. Export diagnostics and sanitize them.
8. Run service and entity smoke tests without triggering unsafe physical actions.
9. Review logs for exceptions, secrets and excessive noise.
10. Create a backup, test upgrade, then perform rollback on a recoverable target.
11. Complete the operator review and attestation.
12. Validate and export the target result.
13. Copy the evidence bundle into the Target Validation Pack and run its validation/import commands.

No production gate is changed merely by completing this runbook.
