# ADR-0014 — Developer Toolkit

## Status
Accepted for 4.0.0-alpha.27.

## Decision
The repository ships a dependency-free toolkit under `tools/` for validation, local/mounted deployment, config-entry reload, controlled Core restart, source watching, log filtering and support-bundle generation.

A config-entry reload is used for configuration, translations, service metadata and runtime reset workflows. A Core restart remains the safe default after Python or manifest changes because CPython keeps imported integration modules in memory; unloading a config entry does not guarantee code-module replacement.

## Security
Long-lived access tokens are read from `HA_TOKEN` or an explicit command argument and are never written to project files. Runtime certificate, log and support directories are preserved during deployment.
