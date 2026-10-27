#!/usr/bin/env python3
"""Validate every JSON/JSONL member in a generated support bundle."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    with zipfile.ZipFile(args.bundle) as archive:
        for name in archive.namelist():
            data = archive.read(name).decode("utf-8", "replace")
            if name.endswith(".json"):
                json.loads(data)
            elif name.endswith(".jsonl"):
                for number, line in enumerate(data.splitlines(), 1):
                    if line.strip():
                        try:
                            json.loads(line)
                        except json.JSONDecodeError as err:
                            raise SystemExit(f"{name}:{number}: {err}") from err
    print("Support bundle JSON validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
