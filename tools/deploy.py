#!/usr/bin/env python3
"""Validate, deploy and optionally reload/restart Home Assistant."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _ha_toolkit import ROOT, copy_component, request_json, token_from_env

p = argparse.ArgumentParser()
p.add_argument("--config-dir", required=True, help="Mounted Home Assistant /config directory")
p.add_argument("--ha-url", default="http://homeassistant.local:8123")
p.add_argument("--token")
p.add_argument("--entry-id")
p.add_argument("--action", choices=("none", "reload", "restart"), default="reload")
p.add_argument("--skip-validate", action="store_true")
a = p.parse_args()
if not a.skip_validate:
    subprocess.run([sys.executable, str(ROOT / "tools" / "validate.py")], check=True)
target = copy_component(Path(a.config_dir))
print(f"Deployed integration to {target}")
if a.action == "none":
    raise SystemExit(0)
token = token_from_env(a.token)
if a.action == "reload":
    if not a.entry_id:
        raise SystemExit("--entry-id is required for --action reload")
    request_json(
        a.ha_url,
        token,
        "/api/services/homeassistant/reload_config_entry?return_response",
        {"entry_id": a.entry_id},
    )
    print("Config entry reload requested. Python module changes may still require a Core restart.")
else:
    request_json(a.ha_url, token, "/api/services/homeassistant/restart", {})
    print("Home Assistant restart requested.")
