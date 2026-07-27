# QS-1 Coverage Priority Map

Measured integration coverage: **35.54%**.

## Highest-impact uncovered modules

| Module | Statements | Missing | Coverage |
|---|---:|---:|---:|
| `custom_components/btdoor_security_plus/sip_client.py` | 1177 | 813 | 30.93% |
| `custom_components/btdoor_security_plus/sensor.py` | 713 | 713 | 0.00% |
| `custom_components/btdoor_security_plus/cloud.py` | 361 | 361 | 0.00% |
| `custom_components/btdoor_security_plus/developer.py` | 300 | 300 | 0.00% |
| `custom_components/btdoor_security_plus/__init__.py` | 255 | 255 | 0.00% |
| `custom_components/btdoor_security_plus/media.py` | 237 | 164 | 30.80% |
| `custom_components/btdoor_security_plus/services.py` | 135 | 135 | 0.00% |
| `custom_components/btdoor_security_plus/binary_sensor.py` | 122 | 122 | 0.00% |
| `custom_components/btdoor_security_plus/button.py` | 76 | 76 | 0.00% |
| `custom_components/btdoor_security_plus/support_debug.py` | 126 | 67 | 46.83% |
| `custom_components/btdoor_security_plus/managers/device_manager.py` | 59 | 59 | 0.00% |
| `custom_components/btdoor_security_plus/device_model/manager.py` | 54 | 54 | 0.00% |
| `custom_components/btdoor_security_plus/call_journal/journal.py` | 162 | 51 | 68.52% |
| `custom_components/btdoor_security_plus/voice.py` | 40 | 40 | 0.00% |
| `custom_components/btdoor_security_plus/sentence_manager.py` | 38 | 38 | 0.00% |
| `custom_components/btdoor_security_plus/switch.py` | 35 | 35 | 0.00% |
| `custom_components/btdoor_security_plus/adapters/base.py` | 34 | 34 | 0.00% |
| `custom_components/btdoor_security_plus/runtime.py` | 31 | 31 | 0.00% |
| `custom_components/btdoor_security_plus/config_flow.py` | 174 | 29 | 83.33% |
| `custom_components/btdoor_security_plus/event.py` | 25 | 25 | 0.00% |

## Execution order

1. Platform modules (`sensor.py`, `binary_sensor.py`, `button.py`, `switch.py`, `event.py`).
2. SIP runtime (`sip_client.py`) using deterministic protocol fixtures.
3. Cloud and setup lifecycle (`cloud.py`, `__init__.py`, `services.py`).
4. Runtime/support modules and residual branches.

Coverage must be measured after every test batch. The level remains Bronze until total coverage exceeds 95%.

## QS-2 measured update

QS-2 completed the first entity-platform batch. Current total coverage is **40.59%**. The next order is:

1. `sensor.py`
2. `services.py`
3. `cloud.py`
4. `__init__.py`
5. `sip_client.py`
