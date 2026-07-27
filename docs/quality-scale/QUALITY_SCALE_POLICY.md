# Quality Scale Governance Policy

1. The official Home Assistant Integration Quality Scale rule set is the external reference.
2. The repository records progress in `quality_scale.yaml` using `done`, `exempt`, and `todo`.
3. An exemption requires an explicit technical reason.
4. Static evidence cannot substitute runtime evidence, measured test coverage, security review, or target validation.
5. **Gold is the minimum release gate, desired tier and maximum governed tier for the entire BTDoor Security+ project.**
6. Every phase and release must preserve Gold; any regression below Gold blocks advancement.
7. Platinum is out of scope and creates no remediation work unless a future explicit ADR reopens the decision.
8. Platinum rules remain visible in reports only for transparency.
9. The assessment is self-declared for a custom integration and must never be presented as an official Home Assistant grade.
10. A rule-set update must trigger regeneration and review of the report and confirmation that Gold remains complete.
