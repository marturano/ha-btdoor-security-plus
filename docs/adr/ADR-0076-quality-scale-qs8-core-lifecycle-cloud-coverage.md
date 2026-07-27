# ADR-0076: QS-8 Core Lifecycle and Cloud Coverage

## Status
Accepted

## Decision
Add behavioural coverage for core lifecycle and certificate renewal paths, preserve cumulative coverage through executed-line union, and validate nested certification tests in isolated processes to avoid false timeout failures.

## Consequences
The integration core lifecycle is substantially better protected. Silver remains blocked until aggregate measured coverage exceeds 95%; no tier promotion is inferred from local module improvements.
