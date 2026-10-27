#!/usr/bin/env python3
"""Calculate multilingual documentation coverage without treating placeholders as complete."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MIN_WORDS = 25


def word_count(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    return len([word for word in text.replace("#", " ").split() if word.strip()])


def main() -> int:
    manifest = yaml.safe_load((DOCS / "document_manifest.yaml").read_text(encoding="utf-8"))
    locales = manifest["supported_locales"]
    documents = manifest.get("required_user_documents", manifest.get("required_documents", []))
    forbidden = manifest.get("forbidden_active_markers", [])
    report: dict[str, object] = {"minimum_words": MIN_WORDS, "locales": {}}
    complete = True
    for locale in locales:
        records = []
        completed = 0
        for relative in documents:
            path = DOCS / locale / relative
            words = word_count(path) if path.exists() else 0
            text = path.read_text(encoding="utf-8") if path.exists() else ""
            stale = [marker for marker in forbidden if marker in text]
            ok = path.exists() and words >= MIN_WORDS and not stale
            completed += int(ok)
            complete &= ok
            records.append(
                {
                    "path": relative,
                    "exists": path.exists(),
                    "words": words,
                    "stale_markers": stale,
                    "complete": ok,
                }
            )
        report["locales"][locale] = {
            "completed": completed,
            "required": len(documents),
            "coverage_percent": round(100 * completed / len(documents), 2),
            "documents": records,
        }
    report["release_gate_passed"] = complete
    output = DOCS / "release" / "documentation-coverage.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
