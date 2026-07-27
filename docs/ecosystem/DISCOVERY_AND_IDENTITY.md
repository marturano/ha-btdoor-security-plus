# Discovery and identity

## Canonical hierarchy

```mermaid
classDiagram
    class Account { +account_id +provider }
    class Home { +home_id +name }
    class Room { +room_id +name }
    class Device { +device_id +model +capabilities }
    class Endpoint { +endpoint_id +transport }
    Account "1" --> "many" Home
    Home "1" --> "many" Room
    Home "1" --> "many" Device
    Room "0..1" --> "many" Device
    Device "1" --> "many" Endpoint
```

## Identifier rules

- `account_id`, `home_id` and `device_id` must derive from immutable upstream identifiers.
- Serial number may be used only when the vendor guarantees uniqueness and stability.
- MAC addresses are normalized and never used as user-facing names.
- Room reassignment must not change entity unique IDs.
- Adapter or transport migration must preserve the canonical device identity where equivalence is proven.

## Discovery modes

| Mode | Use |
|---|---|
| Cloud inventory | account-scoped products and homes |
| Local gateway | MyHOME or LAN-capable bridges |
| Zeroconf/SSDP | discovery hint, not identity authority |
| Manual endpoint | recovery or unsupported discovery environments |

Current BTDoor Security+ configuration is handled by the existing config flow. The broader hierarchy is an architecture contract for future adapters.
