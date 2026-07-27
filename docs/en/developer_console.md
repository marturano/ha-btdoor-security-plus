# Developer Console and diagnostics

Enable Developer Mode and Advanced Diagnostics only when troubleshooting. The Developer Console and Runtime dashboard are generated through the dashboard manager so stable unique IDs are resolved for the selected config entry.

Developer tools include the Runtime Inspector, Event Monitor, event metrics, self-tests and support-report controls. Tests must not open the gate. Logs and reports may contain operational metadata even after sanitization, so keep generated artifacts private and remove them when no longer needed.

The Support Bundle exports normalized runtime, entity and device-registry evidence while removing secrets, private keys, absolute paths and sensitive media information. Use **Clean debug environment** only after saving the evidence required for support; configuration and certificates are preserved.
