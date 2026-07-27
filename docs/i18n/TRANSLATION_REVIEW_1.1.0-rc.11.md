# Translation Review — 1.1.0-rc.11

## Scope

Reviewed project locales: English (`en`), Italian (`it`), French (`fr`), German (`de`), Spanish (`es`) and Dutch (`nl`).

## Documentation

Each locale contains the same eleven Markdown documents covering index, glossary, getting started, dashboards/blueprints, voice assistants, Developer Console, compatibility, architecture overview, contributing, test strategy and translation style. The active documents use canonical 1.0 Foundation / 1.1 Core Stable terminology.

## Home Assistant strings

For `strings.json` and the six reviewed translation files:

- 144 leaf keys per locale;
- no missing or extra keys;
- no placeholder mismatches;
- product names, entity IDs, service identifiers and protocol acronyms preserved;
- cross-language Italian text removed from FR/DE/ES/NL;
- English technical terms retained only where they are product, interface or protocol terminology, or where the existing localized wording remains preferable.

## Claim control

All locales state the same validation boundary: Alexa has real-user evidence; Google Assistant remains unverified on a real account/device. Home Assistant compatibility is expressed as target series 2026.x with 2026.7.x as the primary final-validation environment.
