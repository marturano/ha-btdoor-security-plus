# BTDoor Security+ Platform Architecture 1.0

BTDoor Security+ separates Home Assistant orchestration from device-specific
protocol implementations.

```text
Home Assistant
  -> Platform Core
     -> DeviceAdapter contract
        -> BTicino / Legrand / Netatmo adapters
     -> Dialog Engine
     -> Media Runtime
     -> Diagnostics Runtime
```

## Golden rule

The platform core does not know concrete devices. It depends only on explicit
interfaces and serializable diagnostics contracts.

## Foundation modules

- `core`: lifecycle and subsystem orchestration.
- `adapters`: device-neutral capability and operation contracts.
- `dialog`: deterministic SIP dialog state management.
- existing cloud, SIP, media, and diagnostics modules remain operational while
  they are progressively moved behind these contracts.


## Home Assistant logical device model

Runtime entities are grouped by responsibility and connected to the root gateway device using `via_device`:

- `Cloud Status`: cloud connectivity and provisioning.
- `SIP Monitor`: registration and SIP transport state.
- `Call Manager`: dialog state, call history, call counters, and the last-call summary.
- `Multimedia Monitor`: RTP/SRTP, SDP, codecs, and media-session lifecycle.
- `Advanced Diagnostics`: Developer Mode diagnostics only.

The `BTDoorLastCallSummarySensor` uses `DeviceKind.DIALOG`; its stable unique ID remains `<entry_unique_id>_last_call_summary`.
