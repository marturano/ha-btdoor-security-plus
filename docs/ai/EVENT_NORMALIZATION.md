# AI Event Normalization

All providers produce a common result envelope.

```yaml
request_id: uuid
capability: vision
status: success
summary: Person at the entrance
confidence: 0.97
objects:
  - label: person
provider:
  id: example
  mode: local
usage:
  latency_ms: 612
policy:
  classification: personal_media
  cloud_allowed: false
```

Schema changes require versioning. Raw provider payloads are not emitted on the public event bus by default.
