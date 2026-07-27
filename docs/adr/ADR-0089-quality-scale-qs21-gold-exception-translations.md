# ADR-0089: Complete translated exceptions and promote the self-assessment to Gold

## Status

Accepted

## Context

After QS-20, the integration had achieved Silver with measured coverage above 95%. The only open Gold rule was `exception-translations`. Several service and entity paths still raised English positional messages, preventing Home Assistant from presenting localized errors.

## Decision

All user-facing service and entity exceptions are represented by Home Assistant translation metadata. Invalid user selection uses `ServiceValidationError`; runtime and communication failures use `HomeAssistantError`. Runtime details are passed only through translation placeholders.

The six exception keys are present in `strings.json` and every supported locale file. Behavioural tests verify key parity and runtime metadata.

Gold is promoted only after the generated Quality Scale Engine reports the cumulative Gold tier complete.

## Consequences

- Frontend service and entity errors can be localized.
- Tests no longer depend on English exception strings.
- Translation files must preserve exception-key parity.
- Gold remains a repository self-assessment, not an official Home Assistant certification.
- Platinum remains out of scope until its three remaining rules are independently completed.
