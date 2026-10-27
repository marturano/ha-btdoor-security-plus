#!/usr/bin/env python3
"""Validate Home Assistant translations and multilingual documentation."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads(
    (ROOT / "docs" / "i18n" / "language_registry.json").read_text(encoding="utf-8")
)
LOCALES = tuple(REGISTRY["integration_locales"])
DOC_LOCALES = tuple(REGISTRY["localized_documentation_locales"])
TRANS = ROOT / "custom_components" / "btdoor_security_plus" / "translations"
PLACEHOLDER = re.compile(r"\{([A-Za-z0-9_]+)\}")


def flatten(value, prefix=""):
    out = {}
    if isinstance(value, dict):
        for key, item in value.items():
            out.update(flatten(item, f"{prefix}.{key}" if prefix else key))
    else:
        out[prefix] = value
    return out


def main():
    errors = []
    refs = flatten(json.loads((ROOT / REGISTRY["base_translation"]).read_text(encoding="utf-8")))
    for loc in LOCALES:
        path = TRANS / f"{loc}.json"
        if not path.exists():
            errors.append(f"missing translation file: {path}")
            continue
        data = flatten(json.loads(path.read_text(encoding="utf-8")))
        if set(data) != set(refs):
            errors.append(
                f"{loc}: key mismatch missing={sorted(set(refs) - set(data))} extra={sorted(set(data) - set(refs))}"
            )
        for key in set(data) & set(refs):
            if PLACEHOLDER.findall(str(data[key])) != PLACEHOLDER.findall(str(refs[key])):
                errors.append(f"{loc}:{key}: placeholder mismatch")
            if isinstance(data[key], str) and not data[key].strip():
                errors.append(f"{loc}:{key}: empty value")
    doc_manifest = yaml.safe_load(
        (ROOT / "docs/document_manifest.yaml").read_text(encoding="utf-8")
    )
    required = doc_manifest.get(
        "required_user_documents", doc_manifest.get("required_documents", [])
    )
    forbidden = doc_manifest.get("forbidden_active_markers", [])
    for loc in DOC_LOCALES:
        for rel in required:
            path = ROOT / "docs" / loc / rel
            if not path.exists() or not path.read_text(encoding="utf-8").strip():
                errors.append(f"missing document: {loc}/{rel}")
                continue
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                if marker in text:
                    errors.append(f"{loc}/{rel}: stale marker {marker!r}")
    if errors:
        print("Translation QA failed")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print(
        f"Translation QA passed: {len(LOCALES)} integration locales, {len(refs)} keys, {len(DOC_LOCALES)} documentation locales, {len(required)} documents per documentation locale"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
