# ADR-0007 — Rename the Home Assistant domain

- Status: Accepted
- Date: 2026-07-17
- Software release: 4.0.0-alpha.20

## Decision

The integration domain changes from `btdoor_entry_plus` to
`btdoor_security_plus`. The public project name is **BTDoor Security+** and the
repository name is `ha-btdoor-security-plus`.

## Consequences

Home Assistant treats the new domain as a different integration. Existing
config entries from alpha.19 and earlier are not discovered automatically and
must be removed before the old custom component is deleted, then created again
with the new integration. Entity identifiers and automations referencing the
old service or event namespace must be updated.

This breaking change is accepted while the project is in alpha so every future
platform component can use one stable namespace.
