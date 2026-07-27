# Lifecycle and Multi-entry Isolation

## Global lifecycle

`async_setup` owns integration-wide services, Assist intents and managed sentence installation. These resources remain registered while individual config entries reload. Global actions are removed only when the integration no longer owns them.

## Config-entry lifecycle

1. Validate and migrate entry data without physical actions.
2. Create one runtime container for the entry.
3. Initialize Cloud/SIP/managers and restore safe persisted state.
4. Forward setup to entity platforms.
5. Register listeners and cleanup callbacks on the entry runtime.
6. On unload, stop tasks, unregister listeners and unload platforms symmetrically.

## Isolation invariant

A command resolved for entry A must never use the client, recorder, device identifiers or debug context of entry B. Service calls with multiple gateways require `entry_id` or an integration entity that resolves to one entry. Ambiguous calls fail without executing.

## Restart and reload safety

- State restoration may update sensors but cannot call gate actions.
- Task cancellation and transport shutdown tolerate already-closed resources.
- Services do not capture the first loaded entry.
- Reload must update existing registry objects, not create duplicates.
- Migration preserves unique IDs, user-assigned names and areas.
