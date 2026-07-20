#!/usr/bin/env python3
"""Reload the BTDoor Security+ config entry through the HA REST API."""
from __future__ import annotations
import argparse
from _ha_toolkit import request_json, token_from_env
p=argparse.ArgumentParser()
p.add_argument("--ha-url", default="http://homeassistant.local:8123")
p.add_argument("--token")
p.add_argument("--entry-id", required=True)
a=p.parse_args()
result=request_json(a.ha_url, token_from_env(a.token), "/api/services/homeassistant/reload_config_entry?return_response", {"entry_id": a.entry_id})
print("Config entry reload requested successfully.")
if result is not None: print(result)
