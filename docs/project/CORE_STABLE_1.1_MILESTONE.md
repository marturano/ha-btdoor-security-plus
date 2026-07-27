# Milestone 1.1 — Core Stable

## Purpose

This milestone stabilizes the existing integration before work begins on the Universal Door Security+ Bridge. It is not a feature-expansion milestone.

## Release-candidate history

- **RC.6:** gate migrated from legacy `cover` behavior to a native `button` action.
- **RC.6a:** optional voice-assistant switch introduced.
- **RC.6b:** Support Bundle v2 extended with `registry/entities.json`.
- **RC.7:** voice bridge moved onto its own logical Home Assistant device; dashboards and documentation migrated away from the retired gate cover.
- **RC.9:** roadmap, project manifest, active documentation index and continuation handoff restored and packaged as release artifacts.

## Stable entity contract

| Purpose | Domain/entity example | Contract |
|---|---|---|
| Native gate action | `button.apri_cancello` | Primary Home Assistant and Assist action |
| Voice bridge | `switch.apri_cancello_alexa` | Optional momentary bridge for Alexa/Google exposure |
| Voice bridge device | `Alexa / Google Gate Bridge` | Dedicated logical device, no `via_device` parent |

Entity IDs may be customized by users. Code and generated dashboards must resolve stable unique IDs instead of assuming fixed entity IDs.

## Confirmed reference behavior

The Support Bundle generated on 2026-07-21 confirmed that both gate entities are available, not hidden and not disabled. The user subsequently confirmed that Alexa discovery and gate operation work correctly with RC.7.

## Non-regression requirements

- preserve config-entry identifiers and user customizations;
- preserve logical-device identifiers and entity unique IDs;
- never execute gate actions during setup, retry, restore, migration or state synchronization;
- keep the voice bridge disabled/absent when the corresponding option is not enabled;
- keep diagnostics privacy-safe;
- retain six-language translation compatibility;
- support multi-gateway dispatch without cross-entry actions.

## Remaining work before 1.1 Stable

- clean-install and upgrade matrix;
- Google Assistant real-device validation or explicit documented limitation;
- full HACS and hassfest validation in GitHub CI;
- final migration/rollback instructions;
- final Support Bundle evidence from the stable candidate;
- tag, release archive and checksum verification.
