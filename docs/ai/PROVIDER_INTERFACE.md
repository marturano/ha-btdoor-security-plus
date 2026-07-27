# Provider Interface

## Contract
Each provider adapter declares identity, mode, capabilities, limits, health and execution methods.

```python
class AIProviderAdapter:
    provider_id: str
    mode: str  # local or cloud
    async def capabilities(self): ...
    async def health_check(self): ...
    async def execute(self, request): ...
```

Adapters must not expose provider-specific response objects outside the boundary. Credentials are stored through Home Assistant config-entry mechanisms and excluded from diagnostics.

## Conformance requirements

- deterministic capability declaration;
- timeout and cancellation support;
- typed errors;
- redacted diagnostics;
- normalized usage metadata;
- no implicit data retention.
