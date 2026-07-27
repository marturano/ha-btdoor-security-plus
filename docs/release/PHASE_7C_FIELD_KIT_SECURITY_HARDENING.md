# Phase 7C Field Kit Security Hardening

**Package:** `1.1.0-rc.15-phase7c-github-publication-ready`  
**Phase:** Phase 7C — Release Candidate Approval  
**Decision:** BLOCKED

## Scope

This iteration hardens the Target Validation Pack before real Home Assistant field execution and fixes binary certificate parsing. No feature is added.

## Finding

The target-validation `run-id` was previously used as a filesystem directory name without a strict identifier contract. A crafted value containing path separators or traversal segments could influence the work or immutable import destination.

## Remediation

- enforce a 1–128 character identifier containing only letters, numbers, dots, underscores and hyphens;
- reject path separators, whitespace and every `..` sequence;
- validate the identifier before resolving any work directory;
- reject a `result.json` whose embedded `run_id` does not match its containing run directory;
- retain existing evidence-path traversal protections and immutable import behavior.

## Verification

The target-validation tests cover valid initialization, incomplete-run rejection, unsafe evidence paths, supported 2026.x targets, 2026.7.x reference-target classification, unsupported target rejection, malicious run identifiers and result/directory identity mismatch.

## Runtime certificate hardening

The cold suite exposed a nondeterministic DER parsing failure. Binary DER and DER PKCS#7 payloads were passed through `bytes.strip()`, which can remove valid trailing byte values interpreted as ASCII whitespace. The parser now preserves binary payloads exactly while continuing to normalize PEM text. A regression test verifies byte-for-byte preservation.

## Release effect

The field kit is safer for operator use, but Phase 7C remains blocked until real target evidence is collected and the Release Decision Engine returns `APPROVED`.
