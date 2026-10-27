#!/usr/bin/env python3
"""Shared helpers for the BTDoor Security+ developer toolkit."""

from __future__ import annotations

import json
import os
import shutil
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DOMAIN = "btdoor_security_plus"
ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMPONENT = ROOT / "custom_components" / DOMAIN


def token_from_env(value: str | None) -> str:
    token = value or os.getenv("HA_TOKEN", "")
    if not token:
        raise SystemExit("Missing Home Assistant token. Use --token or HA_TOKEN.")
    return token


def request_json(
    base_url: str, token: str, path: str, payload: dict[str, Any] | None = None
) -> Any:
    url = base_url.rstrip("/") + path
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method="GET" if payload is None else "POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Home Assistant API error {err.code}: {detail}") from err
    except urllib.error.URLError as err:
        raise SystemExit(f"Cannot reach Home Assistant at {base_url}: {err.reason}") from err


def copy_component(config_dir: Path) -> Path:
    target = config_dir.expanduser().resolve() / "custom_components" / DOMAIN
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(target.name + ".staging")
    if staging.exists():
        shutil.rmtree(staging)
    shutil.copytree(
        SOURCE_COMPONENT,
        staging,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "logs", "support", "certificate"),
    )
    for preserved in ("logs", "support", "certificate"):
        source = target / preserved
        destination = staging / preserved
        if source.exists() and not destination.exists():
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
    backup = target.with_name(target.name + ".previous")
    if backup.exists():
        shutil.rmtree(backup)
    if target.exists():
        target.rename(backup)
    staging.rename(target)
    if backup.exists():
        shutil.rmtree(backup)
    return target
