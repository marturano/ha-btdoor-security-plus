#!/usr/bin/env python3
"""Canonical wrapper for active-package repository hygiene validation."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
raise SystemExit(subprocess.run(["python", "tools/check_orphans.py"], cwd=ROOT).returncode)
