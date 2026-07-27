# GitHub Actions Validation Contract

**Status:** Canonical and blocking for RC and Final packages  
**Applies to:** `.github/workflows/*.yml`, validation tooling, release packaging and evidence

## Purpose

A workflow being accepted by GitHub is not evidence that the repository has been validated. A release gate is considered passed only when the relevant command has run against the exact commit or exact package and has returned exit code `0` with retained evidence.

## Canonical workflows

| Workflow | Purpose | Blocking evidence |
|---|---|---|
| `validate.yml` | HACS, Hassfest, Python, governance, repository and Home Assistant compatibility matrix | All jobs green |
| `github-sandbox-validation.yml` | Clean GitHub-hosted execution of the canonical read-only runner | Green run plus uploaded evidence |
| `governance.yml` | Governance, repository rationalization and generated health state | Green run and clean generated files |
| `release.yml` | Version verification and deterministic release archive | Green tagged run and checksum |
| `ruff-remediation.yml` | Optional mechanical remediation only | Never substitutes for a later clean validation run |

## Canonical runner

`tools/validation/github_sandbox_validate.sh check` performs the read-only validation sequence. It must be invoked explicitly with Bash:

```yaml
shell: bash
run: bash tools/validation/github_sandbox_validate.sh check
```

Direct execution of repository shell scripts is forbidden because executable-bit preservation can differ between Windows workstations, ZIP archives and Git checkouts.

The runner installs and records the versions of Ruff, mypy and pytest, then executes:

1. GitHub workflow contract validation;
2. Ruff formatting check;
3. Ruff lint check;
4. mypy integration check;
5. Python compilation;
6. JSON parsing;
7. full pytest suite with explicit asyncio plugin;
8. publication preflight;
9. repository integrity;
10. documentation consistency;
11. repository hygiene;
12. governance automation;
13. certification automation;
14. clean-tree verification.

`set -euo pipefail` and the logged-command wrapper ensure a failed command remains a failed workflow even when output is piped through `tee`.

## Workflow contract validator

`python tools/validation/check_github_workflows.py` is dependency-free and blocks at least these regressions:

- missing canonical workflows;
- missing workflow names, trigger blocks, explicit permissions or manual dispatch;
- unsupported `${{ runner.temp }}` use in repository workflow environment configuration;
- direct invocation of repository `.sh` files without `bash`;
- removal of HACS, Hassfest, compatibility or canonical validation jobs;
- removal of clean-tree validation from the sandbox workflow.

## Evidence vocabulary

- **PASS:** command executed successfully, with exit code and evidence.
- **FAIL:** command executed and returned a non-zero exit code.
- **NOT VERIFIED:** command was not executed or its environment was unavailable.
- **BLOCKED:** release cannot proceed because one or more mandatory gates are FAIL or NOT VERIFIED.

A syntactically accepted workflow is never recorded as PASS by itself.

## Required release evidence

Before packaging an RC or Final release, retain:

- URL or run identifier for each required GitHub workflow;
- commit SHA used by every run;
- validation evidence artifacts;
- HACS and Hassfest outcomes;
- Ruff, mypy and pytest reports;
- compatibility matrix job outcomes;
- governance and certification reports;
- exact ZIP inventory and SHA-256.

The release package must be generated from the same tree that passed the gates. Any subsequent modification invalidates the evidence and requires rerunning the affected gates.

## Local validation limitations

Local execution can provide useful evidence but cannot replace HACS, Hassfest or GitHub-hosted runner evidence. When package repositories or external services are unavailable, the affected gate must remain `NOT VERIFIED`; it must not be converted to PASS based on configuration inspection.
