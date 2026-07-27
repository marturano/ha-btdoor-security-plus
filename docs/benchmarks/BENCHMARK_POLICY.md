# Benchmark Policy

Benchmarks must be reproducible and comparable between releases. Every report records hardware, operating system, Python and Home Assistant versions, integration version, device/entity count, configuration, workload, warm-up, run count and raw/aggregated results.

Required metrics where applicable: setup time, update latency, command latency, CPU, memory, network/API/MQTT traffic, event throughput, errors and timeouts. Regressions beyond declared thresholds block release or require a documented exception.

## Required environment declaration

Every benchmark records Home Assistant version, Python version, operating system, host class, gateway/device/entity count, event rate, media workload, AI provider where applicable, sample duration, warm-up and measurement method. Synthetic evidence must never be presented as real-device evidence.

## Required result statistics

Report median and tail latency where meaningful, plus CPU, memory, I/O, startup, reload, unload, queue behavior and recovery after provider or gateway failure.
