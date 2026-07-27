# Project Memory

## Permanent identity

BTDoor Platform is the umbrella architecture. BTDoor Security+ is the active access, video-door-entry, media, and security module. Future product lines include Home+, Energy+, Climate+, AI+, and the Developer Platform.

## Permanent architecture principles

Local-first where feasible; Home Assistant-native entities; stable identity; modular runtime; explicit capability models; adapter isolation; provider-agnostic AI; privacy by design; fail-closed unknown firmware; no credential extraction, cloning, bypass, or false certification.

## Permanent workflow

Audit → implement → test → update docs → localize → update roadmap/ADR/changelog → archive replacements → generate PCP → validate → package/checksum.

Search before creating documents. Preserve historical evidence. Never allow a conversation to become the only holder of project knowledge.

## RC.15 Phase 4 memory

AI is provider-neutral, capability-routed, policy-authorized before dispatch, normalized at the adapter boundary and local-first where eligible. Face recognition must never be the sole authorization factor for opening a door or gate.

## RC.15 Phase 5 memory

API Foundation is complete. `docs/api/` is canonical. All eleven runtime actions are documented. Physical actions require one unambiguous target. Alexa/Alexa+ and Google Assistant use Home Assistant exposure, not private integration transports. REST/WebSocket remain planned.

## Governance memory update — 2026-07-22

Permanent requirements: Engineering Notebook; Translation Review; documented Quality Reviews; documented and maintained security rules; reproducible Benchmark Review; release-aligned automation, blueprint and Lovelace guides; complete release documentation; mandatory HACS and GitHub validity and publication/maintenance instructions for every Final Release. These requirements are reflected in the Constitution, Workflow, DoR, DoD and handoff.

## Stable entity contract

- `button.apri_cancello` is the canonical native one-shot gate command.
- `switch.apri_cancello_alexa` is the optional momentary Alexa/Google voice bridge and is not a gate-state entity.
- The user previously confirmed the Alexa path operates; Google Assistant real-account validation remains pending unless newer evidence supersedes this statement.

- The Home Assistant Integration Quality Scale is a permanent workflow gate. Report current, release-minimum and desired tiers; generate remediation plans; apply only safe proven improvements; never auto-promote unproven rules.

## Permanent rule — GitHub Sandbox Validation
Before every RC or Final release, validate the exact commit in a clean GitHub-hosted sandbox with Python 3.13, the latest stable official Ruff release and all mandatory release tools. Correct every failure until the full suite passes. Never weaken lint/validation rules or reduce the required Home Assistant Integration Quality Scale level. The current minimum remains GOLD. Preserve versioned evidence and update documentation, handoff, governance, dashboards and release decision records.
