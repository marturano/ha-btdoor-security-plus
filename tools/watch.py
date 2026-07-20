#!/usr/bin/env python3
"""Poll source files and redeploy when they change."""
from __future__ import annotations
import argparse
import subprocess
import sys
import time
from pathlib import Path
from _ha_toolkit import ROOT
p=argparse.ArgumentParser()
p.add_argument("--config-dir", required=True)
p.add_argument("--ha-url", default="http://homeassistant.local:8123")
p.add_argument("--token")
p.add_argument("--entry-id", required=True)
p.add_argument("--interval", type=float, default=1.0)
p.add_argument("--python-action", choices=("reload","restart","none"), default="restart")
a=p.parse_args()
watch_roots=[ROOT/"custom_components"/"btdoor_security_plus"]
def snapshot():
    return {p: p.stat().st_mtime_ns for root in watch_roots for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
state=snapshot(); print("Watching BTDoor Security+ sources. Press Ctrl+C to stop.")
while True:
    time.sleep(a.interval); new=snapshot()
    changed={p for p in set(state)|set(new) if state.get(p)!=new.get(p)}
    if not changed: continue
    action=a.python_action if any(p.suffix==".py" or p.name=="manifest.json" for p in changed) else "reload"
    print("Changed:", ", ".join(str(p.relative_to(ROOT)) for p in sorted(changed)))
    cmd=[sys.executable,str(ROOT/"tools"/"deploy.py"),"--config-dir",a.config_dir,"--ha-url",a.ha_url,"--entry-id",a.entry_id,"--action",action]
    if a.token: cmd += ["--token",a.token]
    subprocess.run(cmd, check=False); state=new
