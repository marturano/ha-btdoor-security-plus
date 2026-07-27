# Phase 7C — GitHub Publication Audit

## Decision

The exact package is prepared for repository synchronization and remote validation. This is not a declaration that GitHub, HACS or hassfest have passed: those results can only be accepted from the remote repository commit that will be installed through HACS.

## Publication contract

1. Push this exact repository content to the GitHub repository.
2. Require the Governance, Validate and release-related checks applicable to the commit.
3. Require HACS Action and hassfest to complete without errors or ignores.
4. Require Python compilation, JSON validation, publication preflight, Ruff, mypy, the complete pytest suite and the Home Assistant 2026.x compatibility matrix.
5. Create a complete GitHub prerelease for `v1.1.0-rc.15`; a tag alone is insufficient for the HACS lifecycle evidence.
6. Install the same prerelease through HACS and collect install, upgrade, rollback/removal and runtime evidence.

## Local audit results

- one integration under `custom_components`: PASS;
- root `hacs.json`: PASS;
- versioned manifest and matching runtime constant: PASS;
- config flow, integration type, IoT class, documentation, issue tracker and code owners: PASS;
- local brand assets for Home Assistant 2026.3+: PASS;
- quality scale declaration: PASS;
- HACS and hassfest workflows present: PASS (presence only);
- release workflow includes tag/version guard, archive and SHA256: PASS;
- CI upgraded to execute publication preflight, full Ruff, mypy and complete pytest suite: PASS (configuration);
- remote workflow execution: PENDING.

## Release decision

`BLOCKED`. Phase 7D remains unauthorized until the exact pushed commit and resulting GitHub release pass remote validation and are installed through HACS.
