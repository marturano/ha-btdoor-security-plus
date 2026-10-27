#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/project/canonical_documents.json"
MAP_JSON = ROOT / "docs/project/repository_dependency_map.json"
MAP_MD = ROOT / "docs/project/REPOSITORY_DEPENDENCY_MAP.md"
METRICS = ROOT / "docs/project/repository_metrics.json"
CANON_MD = ROOT / "docs/project/CANONICAL_DOCUMENTS.md"
TEXT_EXT = {".md", ".json", ".yaml", ".yml", ".py", ".toml", ".txt"}
IGNORE_PARTS = {".git", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])((?:docs|handoff|tools|tests|custom_components|dashboards|blueprints|\.github)/[A-Za-z0-9_@+./-]+\.[A-Za-z0-9_-]+)"
)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def files():
    return [
        p for p in ROOT.rglob("*") if p.is_file() and not any(x in IGNORE_PARTS for x in p.parts)
    ]


def text_files():
    return [p for p in files() if p.suffix.lower() in TEXT_EXT]


def read(p):
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def resolve_link(source: Path, target: str):
    target = target.strip().split("#", 1)[0].split("?", 1)[0]
    if not target or "://" in target or target.startswith(("mailto:", "tel:", "#")):
        return None
    return (
        (ROOT / target.lstrip("/")).resolve()
        if target.startswith("/")
        else (source.parent / target).resolve()
    )


def exempt_unreferenced(path: str) -> bool:
    return (
        path.startswith(
            (
                "docs/adr/",
                "docs/release/",
                "docs/en/",
                "docs/it/",
                "docs/de/",
                "docs/fr/",
                "docs/es/",
                "docs/nl/",
                "docs/pt/",
                "tests/",
                "custom_components/",
                "blueprints/",
                "dashboards/",
                ".github/",
            )
        )
        or path.endswith(("README.md", "index.md", "__init__.py"))
        or path in {"LICENSE", ".gitignore"}
    )


def duplicate_exempt(path: str) -> bool:
    if path == "handoff/24_OFFICIAL_WORKFLOW.md":
        return True
    return path.startswith(
        (
            "docs/en/",
            "docs/it/",
            "docs/de/",
            "docs/fr/",
            "docs/es/",
            "docs/nl/",
            "docs/pt/",
            "custom_components/btdoor_security_plus/translations/",
            "custom_components/btdoor_security_plus/custom_sentences/",
        )
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    all_files = files()
    all_rel = {rel(p): p for p in all_files}
    txt = text_files()
    # Generated rationalization outputs are valid registry targets during the first run.
    generated_targets = {rel(MAP_JSON), rel(MAP_MD), rel(METRICS), rel(CANON_MD)}
    edges = defaultdict(set)
    inbound = defaultdict(set)
    broken = []
    for p in txt:
        src = rel(p)
        content = read(p)
        for raw in LINK_RE.findall(content) if p.suffix.lower() == ".md" else []:
            dest = resolve_link(p, raw)
            if dest is None:
                continue
            try:
                drel = dest.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if dest.exists():
                edges[src].add(drel)
                inbound[drel].add(src)
            else:
                broken.append({"source": src, "target": raw})
        for hit in PATH_RE.findall(content):
            hit = hit.rstrip(".,;:)`")
            if hit in all_rel and hit != src:
                edges[src].add(hit)
                inbound[hit].add(src)
    missing_canonical = []
    canonical_paths = set()
    derived_paths = set()
    for area in registry["areas"]:
        canonical_paths.add(area["canonical"])
        derived_paths.update(area.get("derived", []))
        if area["canonical"] not in all_rel and area["canonical"] not in generated_targets:
            missing_canonical.append(area["canonical"])
        for d in area.get("derived", []):
            if d not in all_rel and d not in generated_targets:
                missing_canonical.append(d)
    hashes = defaultdict(list)
    for p in txt:
        rp = rel(p)
        if duplicate_exempt(rp):
            continue
        normalized = "\n".join(line.rstrip() for line in read(p).strip().splitlines())
        if normalized:
            hashes[hashlib.sha256(normalized.encode()).hexdigest()].append(rp)
    duplicates = [v for v in hashes.values() if len(v) > 1]
    unreferenced = []
    for rp in sorted(all_rel):
        if rp in canonical_paths or rp in derived_paths or exempt_unreferenced(rp):
            continue
        if not inbound.get(rp):
            unreferenced.append(rp)
    aliases = registry.get("deprecated_aliases", {})
    alias_refs = []
    for old, new in aliases.items():
        for p in txt:
            if old in read(p):
                alias_refs.append({"source": rel(p), "deprecated": old, "canonical": new})
    edge_count = sum(len(v) for v in edges.values())
    referenced = sum(1 for rp in all_rel if inbound.get(rp))
    docs = [rp for rp in all_rel if rp.startswith("docs/") and Path(rp).suffix.lower() in TEXT_EXT]
    metrics = {
        "schema_version": 1,
        "generated": date.today().isoformat(),
        "total_files": len(all_rel),
        "text_files": len(txt),
        "documentation_files": len(docs),
        "canonical_areas": len(registry["areas"]),
        "canonical_documents": len(canonical_paths),
        "derived_documents": len(derived_paths),
        "dependency_edges": edge_count,
        "referenced_files": referenced,
        "reference_coverage_percent": round(100 * referenced / max(1, len(all_rel)), 1),
        "broken_links": len(broken),
        "exact_duplicate_groups": len(duplicates),
        "unreferenced_candidates": len(unreferenced),
        "missing_registry_paths": len(missing_canonical),
        "deprecated_alias_references": len(alias_refs),
    }
    METRICS.write_text(
        json.dumps(
            {
                **metrics,
                "broken_link_details": broken,
                "duplicate_groups": duplicates,
                "unreferenced_candidates_list": unreferenced,
                "missing_registry_paths_list": missing_canonical,
                "deprecated_alias_reference_details": alias_refs,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    MAP_JSON.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated": date.today().isoformat(),
                "nodes": sorted(all_rel),
                "edges": [
                    {"source": s, "target": t} for s in sorted(edges) for t in sorted(edges[s])
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    rows = [
        "# Canonical Documents Registry",
        "",
        "**Generated:** " + date.today().isoformat(),
        "",
        "This registry defines the single source of truth for each governed project area. Derived documents may summarize or operationalize canonical content but must not redefine it.",
        "",
        "| Area | Canonical document | Owner | Derived artifacts |",
        "|---|---|---|---|",
    ]
    for a in registry["areas"]:
        rows.append(
            f"| {a['title']} | `{a['canonical']}` | {a['owner']} | "
            + (", ".join(f"`{x}`" for x in a.get("derived", [])) or "None")
            + " |"
        )
    rows += [
        "",
        "## Maintenance rules",
        "",
        "1. Change the canonical source first.",
        "2. Regenerate or update derived artifacts in the same change.",
        "3. Do not create parallel policy documents for an existing area.",
        "4. Register any replacement path in `deprecated_aliases` until all references are migrated.",
        "5. Run `python tools/repository/analyze_repository.py --check` after structural changes.",
    ]
    CANON_MD.write_text("\n".join(rows) + "\n", encoding="utf-8")
    map_rows = [
        "# Repository Dependency Map",
        "",
        "**Generated:** " + date.today().isoformat(),
        "",
        f"- Files: **{len(all_rel)}**",
        f"- Dependency edges: **{edge_count}**",
        f"- Referenced files: **{referenced}**",
        f"- Reference coverage: **{metrics['reference_coverage_percent']}%**",
        f"- Broken Markdown links: **{len(broken)}**",
        f"- Exact duplicate groups: **{len(duplicates)}**",
        f"- Unreferenced candidates: **{len(unreferenced)}**",
        "",
        "## Canonical area dependencies",
        "",
    ]
    for a in registry["areas"]:
        cp = a["canonical"]
        map_rows.append(f"### {a['title']}")
        map_rows.append(f"Canonical: `{cp}`")
        map_rows.append(f"Inbound references: **{len(inbound.get(cp, set()))}**")
        map_rows.append(f"Outbound dependencies: **{len(edges.get(cp, set()))}**")
        map_rows.append("")
    map_rows += [
        "## Interpretation",
        "",
        "Unreferenced candidates are review signals, not automatic deletion decisions. Runtime-discovered Home Assistant files, tests, localized documents, ADRs and historical release records are exempt from orphan failure rules. The machine-readable full graph is stored in `docs/project/repository_dependency_map.json`.",
    ]
    MAP_MD.write_text("\n".join(map_rows) + "\n", encoding="utf-8")
    payload = {
        "status": "PASS"
        if not (broken or duplicates or missing_canonical or alias_refs)
        else "FAIL",
        "metrics": metrics,
        "broken_links": broken,
        "duplicate_groups": duplicates,
        "missing_registry_paths": missing_canonical,
        "deprecated_alias_references": alias_refs,
        "unreferenced_candidates": unreferenced,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Repository rationalization: {payload['status']}")
        for k, v in metrics.items():
            print(f"- {k}: {v}")
    return 1 if args.check and payload["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
