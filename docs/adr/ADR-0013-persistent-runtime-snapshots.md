# ADR-0013: Persistent Runtime Snapshots

- Status: Accepted
- Version: 4.0.0-alpha.26

## Decision

Live media state remains ephemeral, but every completed media session is converted into a sanitized immutable diagnostic snapshot. The latest snapshot and a bounded history of ten sessions are retained in memory and exported in the Support Bundle.

## Rationale

A support report is commonly generated after a SIP dialog has already ended. Clearing all media details at teardown made post-event diagnosis impossible and incorrectly classified media as unobservable. Bounded snapshots preserve evidence without retaining key material or creating unbounded memory growth.
