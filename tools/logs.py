#!/usr/bin/env python3
"""Follow the local Home Assistant log and show integration-related lines."""
from __future__ import annotations
import argparse
import time
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument("--config-dir", required=True); p.add_argument("--from-start", action="store_true"); a=p.parse_args()
path=Path(a.config_dir).expanduser()/"home-assistant.log"
with path.open("r", encoding="utf-8", errors="replace") as handle:
    if not a.from_start: handle.seek(0,2)
    while True:
        line=handle.readline()
        if not line: time.sleep(.25); continue
        if "btdoor_security_plus" in line.lower() or "btdoor security+" in line.lower(): print(line, end="")
