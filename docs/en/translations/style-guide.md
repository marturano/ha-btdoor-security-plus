# Translation style guide

English engineering documentation is normative. User-facing guides and Home Assistant strings are maintained in English, Italian, French, German, Spanish and Dutch. Preserve entity IDs, service names, code, placeholders such as `{entry_title}`, product names and protocol acronyms.

Translate meaning rather than word order. Use the terminology in `docs/shared/terminology.yaml`; avoid mixing languages inside one sentence. Technical terms may remain unchanged only when they are standard interface or protocol names.

Every locale must contain the same JSON key structure and placeholder set as `strings.json`. A translation must not claim validation, certification or compatibility absent from the English source. Translation review is a release gate, not a post-release task.
