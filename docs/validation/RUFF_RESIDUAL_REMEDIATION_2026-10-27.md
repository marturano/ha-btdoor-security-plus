# Ruff residual remediation — 2026-10-27

Current package: `1.1.0-rc.15-phase7c-github-publication-ready`. This report supersedes historical local validation claims for the edited package. Final remains BLOCKED.

## Input and changes

Input SHA256: `beed71e44ee83de49123f0c61da75c79d6a7545b4c516354887fb12743db99cf`. Supplied checksum matches; all ZIP member CRCs pass. Ruff 0.17.3 reproduced exactly 77 baseline diagnostics.

- Preserved package-level constant exports using explicit aliases; removed unused local/type-only imports.
- Moved platform constants below imports, preserving their values.
- Offloaded eight certificate path expansions and nine flagged test filesystem operations through asyncio.to_thread.
- Preserved all SIP timeout names/defaults/logic using five documented line-specific ASYNC109 exceptions: four implementation signatures and one test double. No global lint rule was disabled.
- Removed unused test assignments while retaining loader/parsing side effects; preserved missing-attribute evaluation; replaced the test lambda with an equivalent function.
- Replaced the quality-scale helper mutable default with None; explicitly chained the certification error.
- SIP and Cloud executable ASTs are unchanged; integration function signatures and exported constant names are unchanged. These static comparisons do not replace live runtime testing.

## Actual execution

Windows 11, CPython 3.12.14, Ruff 0.17.3, pytest 9.1.1, pytest-asyncio 1.4.1, mypy 2.4.0. Dependencies are isolated outside the repository. UTF-8 enabled; pytest plugin autoload disabled; pytest_asyncio.plugin explicitly loaded. CI requires different Python versions (3.13/3.14).

| Check | Result |
|---|---|
| Input SHA256 and ZIP CRC | PASS |
| Baseline Ruff | 77 diagnostics reproduced |
| Corrected Ruff check | PASS, zero diagnostics |
| Ruff format --check | PASS, 216 files |
| Python syntax compilation | PASS, 216 files; no bytecode written |
| Integration JSON and hacs.json parse | PASS, 21 files |
| Original ZIP full pytest | 337 passed, 3 failed |
| Corrected full pytest | 337 passed, same 3 failures |
| mypy | EXECUTED, FAILED: 160 diagnostics in 27 files, including missing HA dependencies; no type-validation pass claimed |
| Fresh coverage | NOT MEASURED; historical 95.08% is not revalidated |
| HACS, Hassfest, GitHub Actions, HA compatibility matrix | NOT EXECUTED locally |
| Live SIP/Cloud, HA lifecycle, performance, security, interactive UX | BLOCKED: no configured target runtime/device/cloud environment |

Pytest command: `python -m pytest -o addopts='' -q -p no:cacheprovider -p pytest_asyncio.plugin`; PYTHONUTF8=1, PYTHONDONTWRITEBYTECODE=1, PYTEST_DISABLE_PLUGIN_AUTOLOAD=1.

Existing failures reproduced on original and corrected source:

1. `test_diagnostics_device_is_controlled_by_visibility_manager`: source-text expectation `developer_mode and bool` does not match the existing implementation.
2. `test_init_storage_helpers_and_legacy_entity_cleanup`: Windows file mode 0666 does not satisfy the POSIX 0600 assertion.
3. `test_certification_framework_passes_and_final_remains_blocked`: framework fails locally. Nested bare-python invocation resolves outside the isolated environment; the certification scanner also uses POSIX path exclusions that do not match Windows paths. These existing portability/tooling issues were not changed in this lint patch.

Raw logs, baseline comparison, dependency versions, changed-member hashes and gate exit codes are provided in the companion validation evidence ZIP. Generated historical coverage/certification files are retained as historical records rather than relabelled as new target evidence.

## Continuation

Run the canonical validation runner on Linux with its required Python/dependencies; resolve the pre-existing suite failures and mypy diagnostics without weakening gates. Measure fresh coverage. Collect exact-package GitHub/HACS/Hassfest and real Home Assistant/SIP/Cloud evidence. Keep Final BLOCKED until its governed gates close.

## Final local gate execution

The aggregate governance wrapper was attempted but blocked by Windows directory-removal permissions. Its individual checks were then executed directly; hygiene was checked separately after cleanup. The table records actual subprocess results, not an aggregate PASS.

| Governance subcheck | Actual result |
|---|---|
| project_impact | PASS |
| handoff_synchronization | PASS |
| governance | PASS |
| handoff | PASS |
| release_readiness | PASS |
| repository_integrity | PASS |
| repository_rationalization | PASS |
| quality_intelligence | PASS |
| target_validation_pack | PASS |
| release_pipeline_distribution | PASS |
| repository_production_audit | PASS |
| home_assistant_certification | PASS |
| home_assistant_quality_scale_workflow | PASS |
| runtime_release_certification | PASS |
| decision_traceability | PASS |
| release_decision | PASS |
| health | PASS |

Individual subchecks overall: PASS. A structural PASS does not close the engine's BLOCKED Final release decision.

Workflow contract and document consistency: PASS. Publication preflight: FAIL (`validate workflow missing pytest -q`), reproduced on the original input; the validator expects a literal command while the workflow delegates to the canonical shell runner. No workflow or gate was weakened.

An additional attempted suite run was blocked by temporary-directory permissions (300 passed, 3 failed, 37 setup errors). Its log is retained; the final suite uses a fresh writable temporary directory.
