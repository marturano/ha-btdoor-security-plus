# ADR-0074: Quality Scale QS-6 Developer and Lifecycle Coverage

## Status

Accepted

## Context

After QS-5 the measured integration coverage was 64.62%. `developer.py` contained 300 executable statements with no measured coverage despite being responsible for diagnostics, support bundles, health assessment and cleanup.

## Decision

Add behavioural tests that execute the real developer tooling behind isolated Home Assistant boundaries. Cover enablement enforcement, test aggregation, sanitized failures, certificate status, health scoring, support retention, Markdown rendering, bundle layout and cleanup. Preserve the existing release and Quality Scale gates and do not promote Silver until measured integration coverage exceeds 95%.

## Consequences

- `developer.py` reaches 74% measured coverage.
- Total integration coverage reaches 68.62%.
- The suite reaches 261 passing tests.
- Silver remains blocked solely by `test-coverage`.
- The next cycle targets lifecycle and SIP transport branches.
