#!/usr/bin/env python3
"""Request a controlled Home Assistant Core restart through the REST API."""
from __future__ import annotations
import argparse
from _ha_toolkit import request_json, token_from_env
p=argparse.ArgumentParser()
p.add_argument("--ha-url", default="http://homeassistant.local:8123")
p.add_argument("--token")
a=p.parse_args()
request_json(a.ha_url, token_from_env(a.token), "/api/services/homeassistant/restart", {})
print("Home Assistant restart requested.")
