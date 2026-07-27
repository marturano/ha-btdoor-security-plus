# Home Assistant Integration Quality Scale Report

**Generated:** 2026-07-27
**Assessment:** self-assessment for a custom integration; not an official Home Assistant grade
**Achieved tier:** **GOLD**
**Project target:** **GOLD**
**Release gate (minimum Gold):** **PASS**
**Platinum policy:** **OUT OF SCOPE** unless explicitly reopened by project decision

## Tier summary

| Tier | Done | Exempt | Todo | Tier complete | Cumulative complete |
|---|---:|---:|---:|---|---|
| Bronze | 17 | 3 | 0 | YES | YES |
| Silver | 10 | 0 | 0 | YES | YES |
| Gold | 19 | 2 | 0 | YES | YES |
| Platinum | 0 | 0 | 3 | NO | NO |

## Rule assessment

| Tier | Rule | Status | Reason |
|---|---|---|---|
| Bronze | `action-setup` | DONE | Service actions are present and integration setup is asynchronous. |
| Bronze | `appropriate-polling` | EXEMPT | Manifest declares cloud_push; no fixed polling interval is required. |
| Bronze | `brands` | DONE | Brand assets are present. |
| Bronze | `common-modules` | DONE | Shared entity and constants modules are present. |
| Bronze | `config-flow-test-coverage` | DONE | Dedicated behavioural coverage proves all config-flow outcomes. |
| Bronze | `config-flow` | DONE | UI config flow is enabled. |
| Bronze | `dependency-transparency` | DONE | All manifest dependencies are pinned. |
| Bronze | `docs-actions` | DONE | Action/service documentation detected. |
| Bronze | `docs-triggers` | EXEMPT | No custom device trigger module is registered. |
| Bronze | `docs-conditions` | EXEMPT | No custom device condition module is registered. |
| Bronze | `docs-high-level-description` | DONE | High-level integration description is present. |
| Bronze | `docs-installation-instructions` | DONE | Installation instructions are present. |
| Bronze | `docs-removal-instructions` | DONE | Removal instructions detected. |
| Bronze | `entity-event-setup` | DONE | Entity event lifecycle cleanup detected. |
| Bronze | `entity-unique-id` | DONE | Unique IDs are assigned by entities/config flow. |
| Bronze | `has-entity-name` | DONE | Entity naming opt-in detected. |
| Bronze | `runtime-data` | DONE | ConfigEntry.runtime_data usage detected. |
| Bronze | `test-before-configure` | DONE | Connection validation logic detected in config flow. |
| Bronze | `test-before-setup` | DONE | Setup entry performs runtime initialization and failure handling. |
| Bronze | `unique-config-entry` | DONE | Duplicate-entry prevention detected. |
| Silver | `action-exceptions` | DONE | Home Assistant service/action exceptions detected. |
| Silver | `config-entry-unloading` | DONE | Config entry unloading is implemented. |
| Silver | `docs-configuration-parameters` | DONE | Configuration/options documentation detected. |
| Silver | `docs-installation-parameters` | DONE | Installation parameters are described. |
| Silver | `entity-unavailable` | DONE | Entity availability handling detected. |
| Silver | `integration-owner` | DONE | Integration owner is declared. |
| Silver | `log-when-unavailable` | DONE | Availability transition logging detected. |
| Silver | `parallel-updates` | DONE | Platform parallel update limits are declared. |
| Silver | `reauthentication-flow` | DONE | Reauthentication flow detected. |
| Silver | `test-coverage` | DONE | Measured integration coverage is 95.08%; above 95% is required. |
| Gold | `devices` | DONE | Device registry integration detected. |
| Gold | `diagnostics` | DONE | Diagnostics are implemented. |
| Gold | `discovery-update-info` | EXEMPT | No supported network discovery mechanism is currently declared. |
| Gold | `discovery` | EXEMPT | The integration is configured explicitly and declares no discovery matcher. |
| Gold | `docs-data-update` | DONE | Data update behavior is documented. |
| Gold | `docs-examples` | DONE | Automation blueprints/examples are present. |
| Gold | `docs-known-limitations` | DONE | Known limitations are documented. |
| Gold | `docs-supported-devices` | DONE | Supported devices are documented. |
| Gold | `docs-supported-functions` | DONE | Supported functionality/entities are documented. |
| Gold | `docs-troubleshooting` | DONE | Troubleshooting documentation is present. |
| Gold | `docs-use-cases` | DONE | Use cases are documented. |
| Gold | `dynamic-devices` | DONE | Dynamic entity/device handling detected. |
| Gold | `entity-category` | DONE | Entity categories are used. |
| Gold | `entity-device-class` | DONE | Device classes are used where available. |
| Gold | `entity-disabled-by-default` | DONE | Noisy/advanced entities can be disabled by default. |
| Gold | `entity-translations` | DONE | Entity translations detected. |
| Gold | `exception-translations` | DONE | Translatable exception support detected. |
| Gold | `icon-translations` | DONE | Icon translations are provided. |
| Gold | `reconfiguration-flow` | DONE | Reconfigure flow detected. |
| Gold | `repair-issues` | DONE | Repairs integration usage detected. |
| Gold | `stale-devices` | DONE | Stale-device removal support detected. |
| Platinum | `async-dependency` | TODO | The external dependency must be formally verified as fully asynchronous. |
| Platinum | `inject-websession` | TODO | The external dependency must support injection of Home Assistant web sessions. |
| Platinum | `strict-typing` | TODO | Strict typing must be proven with a repository-wide type checker gate. |

## Governance note

This report is a repository self-assessment aligned with the official Home Assistant rule set. It does not claim an official Home Assistant Core grade or review. Manual and runtime evidence remains mandatory where static inspection cannot prove compliance.
