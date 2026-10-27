# Linux validation completion — 2026-10-27

**Current package:** `1.1.0-rc.15-phase7c-github-publication-ready`

This checkpoint supersedes the unresolved local-check status in the earlier Ruff
remediation report. It does not certify a live installation or authorize Final.

## Executed successfully

Ubuntu 24.04 under WSL, native Linux temporary filesystem, CPython 3.14.2,
Home Assistant 2026.7.2. Direct validation dependencies are pinned in
`requirements-validation.txt`; the companion evidence records the full resolved set.

| Check | Actual result |
|---|---|
| Ruff check and format | PASS, zero findings, 218 Python files formatted |
| mypy | PASS, no issues in 78 integration source files |
| Full pytest suite | PASS, 347 tests, zero skipped/failed |
| Fresh integration coverage | PASS, 95.01%, above the governed 95% threshold |
| Python compilation and 21 JSON parses | PASS |
| Publication preflight and workflow contract | PASS |
| Repository integrity, document consistency and hygiene | PASS |
| Governance automation | PASS, all 18 subchecks |
| Local certification framework | PASS; Final remains BLOCKED |
| Canonical Bash runner | PASS, exit 0; source hashes unchanged for all 816 input files |
| Real HA import/API smoke | PASS on Home Assistant 2026.7.2 in a fresh process |
| SIP protocol logic comparison | PASS, 59 methods unchanged after removing type annotations/casts/local aliases |
| Cloud source comparison | PASS, byte-identical to the previous delivered Ruff-fixed ZIP |

The raw canonical coverage report is retained as
`docs/quality-scale/integration_coverage.raw.json`. This measurement replaces the
historical 95.08% value for the edited code. The 95% threshold was not reduced.

## Corrections

- Made the visibility assertion insensitive to whitespace. POSIX key mode 0600
  remains mandatory on Linux; Windows ACLs are outside that mode-bit assertion.
- Used the current interpreter for certification/governance subprocesses and
  normalized certification exclusion paths using as_posix.
- Added explicit internal types for the 73 existing persisted SIP fields, SDP
  buffers and service responses. Preserved existing restore guards, exported
  state keys, service schemas, timeout names/defaults and SIP/Cloud protocol logic.
- Annotated existing JSON/support structures, avoided a reused codec variable and
  used binascii.Error directly. Only untyped third-party asn1crypto imports are
  exempt from mypy; no integration module or error class is globally ignored.
- Updated publication preflight to follow canonical runner delegation. Five
  regression cases verify acceptance and rejection when a gate or delegation is removed.
- Pinned the complete validation dependencies and aligned Governance with Python
  3.14.2. Fixed the direct HA smoke script's checkout import path.
- Isolated generated test/governance reports, bytecode, caches and coverage state.
  The canonical runner checks the source tree, runs mutating gates on an exact
  temporary copy, then exports evidence. Nonzero command exits remain blocking.
- Removed only known empty test workspaces. Unexpected files still fail inventory
  and hygiene checks.

## Attempts and limits

The original Windows run had 337 passed and 3 failures. Those failures were
reproduced on the original ZIP; they are superseded by the successful Linux run.
An attempted run with inaccessible Windows temporary directories produced 37
setup errors and is retained in the earlier evidence rather than counted as PASS.
The first Linux run had 343 passed and 2 inventory-related failures. Intermediate
canonical runs correctly stopped on empty test directories and then on the
coverage database inside the tree; their logs are retained separately. The final
runner passed with the source tree unchanged.

GitHub-hosted HACS, Hassfest and the full supported-HA matrix are separate checks.
Their results must be tied to the pushed commit, not inferred from this local run.
Real HA/device/cloud SIP calls, install/update/rollback, benchmarks, target security
and interactive UX remain NOT EXECUTED. The five target-certification blockers and
the governed Final BLOCKED decision remain in force. No release tag, merge or live
deployment is part of this correction.

## GitHub follow-up

The first pushed commit passed HACS, Hassfest, all five HA matrix targets, Validate and GitHub Sandbox Validation. Standalone Governance exposed a source-hygiene false positive on empty Git metadata directories; the checker now excludes only .git internals. Two additional regression cases accept empty Git internals and reject an actual empty project directory. The updated canonical Linux run passes all 347 tests. The Governance workflow also uploads its JSON evidence on failure.

Live remote check status and exact commits are available on [pull request #1](https://github.com/marturano/ha-btdoor-security-plus/pull/1). They must be read from the commit checks rather than inferred from this local report.

The stale July candidate build manifest from the uploaded ZIP was removed from active package content and retained in the companion evidence. It is not a checksum for the new archive.

A later local staging attempt retained the obsolete July build manifest and correctly failed inventory. Recreating the staging copy from scratch restored a complete PASS; no source gate was disabled.
