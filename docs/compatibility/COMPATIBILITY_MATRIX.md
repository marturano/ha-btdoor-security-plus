# Compatibility Matrix

## Scope and evidence model

BTDoor Security+ targets **Home Assistant Core 2026.x**. Every monthly Core line is listed explicitly below. A row does not imply real-device validation unless the corresponding evidence column says so.

Evidence levels:

1. **Declared target** — intended compatibility, not yet demonstrated.
2. **Static checked** — Python compilation, JSON/YAML validation and prohibited/deprecated API scan.
3. **CI/API checked** — imports and automated tests against the exact Home Assistant Core package.
4. **Runtime validated** — clean setup, reload, unload and restart on that exact patch release.
5. **Device validated** — reference gateway and, where applicable, Alexa/Google behavior exercised on that exact patch release.

## Home Assistant 2026 monthly coverage

The latest stable patch observed for each completed monthly line at the time of this review is shown as the preferred validation point. Earlier patch releases remain part of the same monthly compatibility line but are not automatically considered tested.

| HA line | Preferred exact patch | Release availability | Static | CI/API | Clean install | Upgrade | Reload/unload/restart | Gateway | Alexa | Google | Current conclusion |
|---|---:|---|---|---|---|---|---|---|---|---|---|
| 2026.1.x | 2026.1.3 | Released | Required | Pending | Pending | Pending | Pending | Pending | Pending | Unverified | Declared target only |
| 2026.2.x | 2026.2.3 | Released | Required | Pending | Pending | Pending | Pending | Pending | Pending | Unverified | Declared target only |
| 2026.3.x | 2026.3.4 | Released | Required | Pending | Pending | Pending | Pending | Pending | Pending | Unverified | Declared target only |
| 2026.4.x | 2026.4.4 | Released | Required | Pending | Pending | Pending | Pending | Pending | Pending | Unverified | Declared target only |
| 2026.5.x | 2026.5.4 | Released | Required | Pending | Pending | Pending | Pending | Pending | Pending | Unverified | Declared target only |
| 2026.6.x | 2026.6.4 | Released | Required | Pending | Pending | Pending | Pending | Pending | Pending | Unverified | Declared target only |
| 2026.7.x | 2026.7.2 | Released; primary validation line | PASS for RC.12 source | Pending | Pending | Pending | Pending | Earlier gateway evidence inherited, RC.12 regression pending | Earlier Alexa evidence inherited, RC.12 regression pending | Unverified | Primary runtime validation still required |
| 2026.8.x | Not released as of 2026-07-21 | Future | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Must be added after release |
| 2026.9.x | Not released as of 2026-07-21 | Future | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Must be added after release |
| 2026.10.x | Not released as of 2026-07-21 | Future | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Must be added after release |
| 2026.11.x | Not released as of 2026-07-21 | Future | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Must be added after release |
| 2026.12.x | Not released as of 2026-07-21 | Future | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Must be added after release |

## Minimum supported release

The intended minimum is `2026.1.0`, but it must not be advertised as fully supported until the exact-package CI/API test and at least one runtime validation on the 2026.1 line succeed. HACS metadata alone is not compatibility evidence.

## Required test set for each released monthly line

For every 2026.x month, record:

- exact Core patch and Python version;
- installation method and HACS version where applicable;
- clean install and config-flow result;
- upgrade source version;
- setup, reload, unload and restart result;
- entity/device count before and after lifecycle operations;
- registry preservation for names, areas, disabled state and unique IDs;
- no-command-on-startup/reload/migration assertion;
- multi-config-entry command isolation;
- Support Bundle sanitization;
- Alexa and Google status as independently verified, inherited or unverified.

## Stable release rule

1.1.0 Stable requires at minimum:

- CI/API checks on all released monthly lines 2026.1–2026.7;
- runtime validation on the minimum line, at least one intermediate line and 2026.7.2;
- exact-patch evidence in the release validation report;
- no use of APIs introduced after the declared minimum unless guarded;
- future monthly lines added to this matrix only after their official release.
