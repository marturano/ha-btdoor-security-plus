# Project Execution Contract

This contract is mandatory for every future session, contributor, build, RC, stable release, and hotfix.

## Non-negotiable rules

1. **Repository is the source of truth.** No critical decision may exist only in conversation.
2. **Documentation parity.** Every change updates all affected active documents, examples, dashboards, blueprints, matrices, and user guidance.
3. **Localization parity.** User-facing UI and required documentation are synchronized across `en`, `it`, `fr`, `de`, `es`, and `nl`; limitations are recorded.
4. **Roadmap discipline.** Features update the canonical roadmap, relevant series roadmap, milestone status, and backlog. Planned scope must never be described as implemented.
5. **ADR discipline.** Significant architecture, security, compatibility, data-model, provider, release-process, or governance decisions require an ADR.
6. **Compatibility honesty.** Distinguish static checks, simulations, user evidence, and real-device validation. Never invent protocol or certification claims.
7. **Test evidence.** Record what passed, failed, was skipped, and why. A blocked full suite is not reported as success.
8. **Archive before replacement.** Normative documents are archived with release, reason, replacement, and changelog entry.
9. **Security and privacy.** Never package secrets, unsanitized support data, credentials, personal media, or identity data. AI/vision features are opt-in, provider-agnostic, and retention-aware.
10. **Continuity.** Every package contains a complete PCP and Recovery Prompt sufficient for a new prompt.
11. **No unsafe physical automation.** Gate/access commands require explicit intent, correct config-entry routing, and no blind retry.
12. **Definition of Done.** Code, tests, docs, translations, roadmap, ADR, changelog, release evidence, archive actions, PCP, package, and checksum are synchronized.

A release that violates an applicable rule is incomplete.

## Documented review rule

Every applicable workflow gate must leave versioned evidence. Reviews not documented in the repository are treated as not executed. Final Releases additionally require documented HACS and GitHub lifecycle validation.
