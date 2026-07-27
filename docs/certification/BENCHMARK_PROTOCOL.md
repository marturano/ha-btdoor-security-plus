# Benchmark Protocol

## Reproducibility

Record date, operating system, Python version, processor count, command, sample count, wall-clock duration, peak process RSS when available, test selection and exit code.

## Repository-local benchmark

The repository-local benchmark executes the deterministic unit/regression suite with pytest cache disabled and Python bytecode disabled. It measures the repository in the current execution environment only.

## Home Assistant target benchmark

The Final runtime baseline must additionally measure on a supported Home Assistant 2026.x installation:

- integration setup duration;
- reload duration;
- entity and device registration duration;
- idle memory delta;
- active-call/event memory delta;
- CPU during idle and representative workload;
- event-dispatch latency;
- 24-hour stability;
- clean shutdown and restart.

## Acceptance

Thresholds must be recorded in `docs/benchmarks/BASELINES.md`. A local benchmark cannot close the Home Assistant runtime evidence item.
