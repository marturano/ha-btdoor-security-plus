# Test strategy

Release validation combines Python compilation, JSON/YAML parsing, HACS and hassfest checks, focused regression tests and Home Assistant 2026.x runtime testing. Runtime scenarios include clean install, supported upgrade, setup, reload, unload, restart and multiple config entries.

Registry tests verify that devices and entities are not duplicated and that unique IDs, custom names, areas and disabled states survive upgrades. Safety tests assert that setup, migration, reload and retry paths never open the gate and that one config entry cannot command another gateway.

Assistant, sanitizer, private-export, dashboard compatibility and managed Assist-resource tests are independent gates. Real-device and external-assistant results must be recorded as separate evidence classes.
