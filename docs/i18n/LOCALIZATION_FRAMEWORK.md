# Localization Framework

**Status:** Authoritative

The Localization Framework governs every Home Assistant translation shipped by the integration and the localized user-document set.

## Source of truth

- Base schema: `custom_components/btdoor_security_plus/strings.json`
- English runtime translation: `custom_components/btdoor_security_plus/translations/en.json`
- Supported integration locales: `docs/i18n/language_registry.json`
- Localized documentation locales and required files: `docs/document_manifest.yaml`

## Mandatory checks

1. Every registered integration locale has a translation file.
2. Every translation has exactly the same leaf-key set as `strings.json`.
3. Placeholder names and multiplicity match the base value.
4. Values are valid JSON strings and are not empty.
5. Removed base keys are removed from every locale.
6. Required localized user documents exist for all documentation locales.
7. A localization report is regenerated for the exact package.

A missing or stale locale blocks RG-003 and therefore blocks phase completion and Final release.

## Support levels

- **Runtime UI and custom sentences:** all 17 registered integration locales require complete key, placeholder and JSON parity.
- **Full user documentation:** the six locales registered in `localized_documentation_locales` require the complete localized document set.
- **Release notes:** required for every full-documentation locale.
- **Fallback:** other runtime locales use the canonical English documentation.

The phrase “all supported languages” must be interpreted against the applicable support level, not as an assertion that every repository document is translated into all runtime locales.
