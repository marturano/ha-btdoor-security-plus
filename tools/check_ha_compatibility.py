"""Import-time compatibility smoke test for supported Home Assistant releases."""
from __future__ import annotations

import importlib
from importlib.metadata import version

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.helpers import entity_registry, intent


def main() -> None:
    module = importlib.import_module("custom_components.btdoor_security_plus")
    services = importlib.import_module("custom_components.btdoor_security_plus.services")
    voice = importlib.import_module("custom_components.btdoor_security_plus.voice")
    assert callable(module.async_setup)
    assert callable(module.async_setup_entry)
    assert callable(module.async_unload_entry)
    assert callable(services.async_register_services)
    assert callable(intent.async_register)
    assert callable(intent.async_remove)
    assert callable(entity_registry.async_get)
    assert ConfigEntry is not None and ConfigEntryState is not None
    assert HomeAssistant is not None and SupportsResponse is not None
    assert voice.INTENT_OPEN_GATE == "BTDoorOpenGate"
    print(f"BTDoor import/API smoke test passed on Home Assistant {version('homeassistant')}")


if __name__ == "__main__":
    main()
