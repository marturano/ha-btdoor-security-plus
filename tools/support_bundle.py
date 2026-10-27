#!/usr/bin/env python3
"""Generate a BTDoor Security+ support bundle via the HA REST API."""

from __future__ import annotations

import argparse
import json

from _ha_toolkit import request_json, token_from_env

p = argparse.ArgumentParser()
p.add_argument("--ha-url", default="http://homeassistant.local:8123")
p.add_argument("--token")
p.add_argument("--entry-id", required=True)
p.add_argument("--no-logs", action="store_true")
a = p.parse_args()
r = request_json(
    a.ha_url,
    token_from_env(a.token),
    "/api/services/btdoor_security_plus/export_debug_bundle?return_response",
    {"entry_id": a.entry_id, "include_logs": not a.no_logs},
)
print(json.dumps(r, indent=2, ensure_ascii=False))
