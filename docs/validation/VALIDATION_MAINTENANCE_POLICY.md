# Validation Maintenance and Update Policy

**Status:** Authoritative  
**Applies to:** every feature, fix, refactor, RC and Final Release

## Purpose

Validation evidence is a maintained project asset. It must remain current, traceable, non-duplicated and aligned with the exact repository state it evaluates.

## Mandatory gate

`Validation Maintenance and Update` is performed after QA and before Release Readiness. It must:

1. identify every validation affected by the change;
2. rerun applicable automated and manual checks;
3. consolidate overlapping evidence into the canonical release report;
4. update the validation register and status matrix;
5. remove obsolete, duplicated or unreferenced validation files;
6. distinguish static checks, simulated tests, runtime evidence, real-device evidence and external publication evidence;
7. record unresolved gaps without converting them into support claims;
8. update handoff, release documentation and Engineering Notebook.

## Canonical structure

- `docs/validation/VALIDATION_MAINTENANCE_POLICY.md`
- `docs/validation/VALIDATION_REGISTER.md`
- `docs/validation/VALIDATION_REPORT_<version>.md`
- `docs/repository/validations/` only for GitHub/HACS publication evidence tied to a Final Release.

## Lifecycle

A validation record is **Current**, **Superseded**, **Not Applicable**, **Pending**, or **Failed**. Superseded evidence is consolidated into the current report or removed after its unique information is preserved. The repository does not retain an internal archive directory.

## Release rule

A review or validation not documented in the canonical report and register is treated as not performed. Every Final Release additionally requires current GitHub and HACS publication validation.

## Dashboard synchronization

Validation Maintenance and Update is incomplete until the Project Health Dashboard source and rendered view are synchronized with the canonical validation report, registers and current gate decisions.
