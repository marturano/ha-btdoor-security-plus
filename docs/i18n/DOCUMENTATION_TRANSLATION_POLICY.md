# Documentation Translation Policy

BTDoor Security+ supports English, Italian, French, German, Spanish and Dutch.

## Normative sources

English is the normative language for architecture, ADRs, engineering notebooks, test internals and detailed validation reports. Translating these documents in full is optional; translated summaries must never change technical meaning or claim evidence not present in the source.

## Required localized user documentation

Every supported locale must maintain complete and current pages for:

- documentation index and glossary;
- installation and initial configuration;
- dashboards and blueprints;
- voice-assistant exposure and safety;
- Developer Console usage and privacy;
- compatibility status and known limitations.

README, stable release notes, migration and rollback guidance must provide at least English and Italian versions before Stable. Other locales may link to the English normative release artifact when a translation is not yet approved.

## Quality gate

Translation QA checks Home Assistant JSON key parity, placeholder parity, non-empty values, required localized documents, minimum meaningful content and forbidden stale markers. Product names, entity IDs, service names, protocol tokens, paths and code symbols are not translated.

A file is not complete merely because it exists. Placeholder-only pages, obsolete release numbers and unverified compatibility claims fail the release gate.
