# AI Performance and Observability

The runtime records provider health, request count, success/error rate, latency, timeout, retry, fallback, cache hit/miss and usage/cost estimates when available.

Metrics must not expose prompt contents, images, transcripts or identities. Benchmarks use synthetic or consented fixtures.

## Target budgets

- cancellation propagation for all adapters;
- bounded concurrency;
- configurable per-provider timeout;
- deterministic fallback order;
- cache keys derived from normalized request plus policy-safe content hashes.
