# QS-21 Gold Exception Translation Completion Report

## Outcome

QS-21 completes the Home Assistant Quality Scale `exception-translations` rule and promotes the repository self-assessment from Silver to Gold.

- measured integration coverage: **95.08%**
- covered statements: **5297 / 5571**
- coverage-gate behavioural suite: **328 PASS**
- exception translation keys: **6**
- supported locale files with complete key parity: **17 / 17**
- Quality Scale Engine: **GOLD**
- Quality Scale Workflow: **PASS**

This is a repository self-assessment and is not an official Home Assistant Core certification.

## Runtime changes

User-facing service and entity failures now use Home Assistant translated exceptions with:

- `translation_domain=DOMAIN`
- a stable `translation_key`
- `translation_placeholders` for runtime details
- `ServiceValidationError` for invalid or ambiguous user selection
- `HomeAssistantError` for communication and runtime failures

Implemented keys:

1. `no_matching_config`
2. `multiple_gates`
3. `sip_connection_test_failed`
4. `call_rejection_failed`
5. `developer_mode_disabled`
6. `gate_open_failed`

The implementation covers global service actions, the gate button and the optional voice-assistant bridge switch.

## Translation evidence

`strings.json` and all 17 supported translation files contain the same six exception keys. English, Italian, German, Spanish, French, Portuguese and Dutch contain localized reviewed wording; the remaining locales retain explicit English fallback text so no locale can lose the exception key at runtime.

## Behavioural evidence

`tests/test_quality_scale_qs21_exception_translations.py` validates:

- source-string key completeness;
- locale key parity;
- non-empty messages;
- runtime use of `translation_domain` and stable translation keys;
- removal of previous hard-coded user-facing exception strings.

Existing service and platform tests now assert translation keys and placeholders instead of matching English exception text.

## Quality Scale decision

The generated Quality Scale evidence reports:

- Bronze: complete
- Silver: complete
- Gold: complete
- Platinum: not complete

Gold consists of 19 completed rules and 2 documented exemptions. No Platinum claim is made.
