# Public API Audit

> **Document status:** Historical / informational  
> **Normative:** No  
> **Active roadmap scope:** Excluded  
> **Current policy:** GOLD is the permanent governed maximum. This document is retained only as historical engineering evidence.


## Exposed Home Assistant surface

Platforms:

- binary sensor;
- button;
- event;
- sensor;
- switch.

Registered service actions:

- `open_gate`;
- `reset_statistics`;
- `test_connection`;
- `reject_call`;
- `developer_test`;
- `generate_support_report`;
- `export_debug_bundle`;
- `clean_debug_environment`;
- `clear_call_journal`;
- `export_call_journal`;
- `rebuild_call_journal`.

Additional surfaces include diagnostics, repairs, config/reconfigure/reauth flows, Assist intents/sentences, device registry, runtime API, event bus, call journal, and support bundles.

## Findings

The API surface is broad but organized. No API removal is required to satisfy the three Platinum rules.

Potential consolidation candidates for a future major/minor release:

- `generate_support_report` and `export_debug_bundle` currently share the same handler;
- developer-only actions should remain clearly gated and disabled by default;
- dictionary-based internal runtime exports should migrate to typed models as part of strict typing;
- public service response schemas should be treated as stable contracts.

## Recommendation

Do not combine public API cleanup with Platinum compliance unless typing requires a non-breaking internal model. API consolidation is optional and creates avoidable regression and migration risk.
