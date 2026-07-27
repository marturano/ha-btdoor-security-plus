# ADR-0030 — Device and entity identity stability

Status: Accepted.

## Decision
Upgrades preserve entity unique IDs, config-entry identifiers, device identifiers, user names, areas and registry preferences. Logical topology changes update existing records wherever possible.

## Consequence
Migration tests must detect duplicates and must never execute the gate.
