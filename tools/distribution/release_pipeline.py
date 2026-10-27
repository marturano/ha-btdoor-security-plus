#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import zipfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = "btdoor_security_plus"
MANIFEST = ROOT / "custom_components" / DOMAIN / "manifest.json"
HACS = ROOT / "hacs.json"
DECISION = ROOT / "docs/quality/release_decision.json"
CERTIFICATION = ROOT / "docs/certification/release_certification.json"
OUT_DIR = ROOT / "dist"
REPORT = ROOT / "docs/release-pipeline/PUBLICATION_READINESS_REPORT.json"

REQUIRED_COMPONENT_FILES = ["__init__.py", "manifest.json", "config_flow.py"]
REQUIRED_REPOSITORY_FILES = ["README.md", "LICENSE", "hacs.json", "CHANGELOG.md"]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def current_version() -> str:
    version = str(load_json(MANIFEST).get("version", "")).strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
        raise ValueError(f"Invalid manifest version: {version!r}")
    return version


def gate_state() -> dict:
    result = {"release_decision": "UNKNOWN", "certification": "UNKNOWN"}
    if DECISION.exists():
        data = load_json(DECISION)
        result["release_decision"] = str(
            data.get("decision") or data.get("status") or "UNKNOWN"
        ).upper()
    if CERTIFICATION.exists():
        data = load_json(CERTIFICATION)
        result["certification"] = str(
            data.get("status") or data.get("decision") or "UNKNOWN"
        ).upper()
    return result


def inspect() -> dict:
    errors, warnings = [], []
    component = ROOT / "custom_components" / DOMAIN
    for rel in REQUIRED_COMPONENT_FILES:
        if not (component / rel).is_file():
            errors.append(f"missing component file: custom_components/{DOMAIN}/{rel}")
    for rel in REQUIRED_REPOSITORY_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing repository file: {rel}")
    manifest = load_json(MANIFEST)
    hacs = load_json(HACS)
    version = current_version()
    if manifest.get("domain") != DOMAIN:
        errors.append("manifest domain mismatch")
    if not manifest.get("documentation"):
        errors.append("manifest documentation URL missing")
    if not manifest.get("issue_tracker"):
        warnings.append("manifest issue_tracker URL missing")
    if not manifest.get("codeowners"):
        errors.append("manifest codeowners missing")
    if not hacs.get("homeassistant"):
        errors.append("hacs minimum Home Assistant version missing")
    if not (component / "translations" / "en.json").is_file():
        warnings.append("English translation not found")
    gates = gate_state()
    publication_ready = (
        not errors
        and gates["release_decision"] in {"APPROVED", "READY", "PASS"}
        and gates["certification"] in {"CERTIFIED", "APPROVED", "READY", "PASS"}
    )
    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "domain": DOMAIN,
        "version": version,
        "errors": errors,
        "warnings": warnings,
        "gates": gates,
        "structural_status": "PASS" if not errors else "FAIL",
        "publication_status": "READY" if publication_ready else "BLOCKED",
        "blocking_reasons": ([] if not errors else errors)
        + (
            []
            if gates["release_decision"] in {"APPROVED", "READY", "PASS"}
            else [f"release decision is {gates['release_decision']}"]
        )
        + (
            []
            if gates["certification"] in {"CERTIFIED", "APPROVED", "READY", "PASS"}
            else [f"release certification is {gates['certification']}"]
        ),
    }


def archive_members() -> list[Path]:
    members = []
    component = ROOT / "custom_components" / DOMAIN
    for p in sorted(component.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"}:
            members.append(p)
    for rel in REQUIRED_REPOSITORY_FILES:
        p = ROOT / rel
        if p.is_file():
            members.append(p)
    for rel in ["SECURITY.md", "CONTRIBUTING.md"]:
        p = ROOT / rel
        if p.is_file():
            members.append(p)
    return sorted(set(members), key=lambda p: p.relative_to(ROOT).as_posix())


def write_reproducible_zip(path: Path, members: list[Path]) -> None:
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "315532800"))
    dt = datetime.fromtimestamp(max(epoch, 315532800), tz=UTC)
    stamp = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for src in members:
            rel = src.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(rel, stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 & 0xFFFF) << 16
            zf.writestr(info, src.read_bytes())


def build(force: bool = False) -> dict:
    check = inspect()
    if check["structural_status"] != "PASS":
        raise RuntimeError("; ".join(check["errors"]))
    if check["publication_status"] != "READY" and not force:
        raise RuntimeError(
            "publication gates are blocked; use --force only for a non-publishable candidate artifact"
        )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    version = check["version"]
    artifact = OUT_DIR / f"btdoor-security-plus-{version}.zip"
    write_reproducible_zip(artifact, archive_members())
    with zipfile.ZipFile(artifact) as zf:
        files = [
            {
                "path": n,
                "sha256": hashlib.sha256(zf.read(n)).hexdigest(),
                "size": zf.getinfo(n).file_size,
            }
            for n in sorted(zf.namelist())
        ]
    release_manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "name": "BTDoor Security+",
        "domain": DOMAIN,
        "version": version,
        "artifact": artifact.name,
        "artifact_sha256": sha256(artifact),
        "artifact_size": artifact.stat().st_size,
        "publishable": check["publication_status"] == "READY",
        "candidate_only": check["publication_status"] != "READY",
        "gates": check["gates"],
        "files": files,
    }
    manifest_path = OUT_DIR / f"btdoor-security-plus-{version}.release.json"
    manifest_path.write_text(
        json.dumps(release_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    checksum = OUT_DIR / f"btdoor-security-plus-{version}.zip.sha256"
    checksum.write_text(
        f"{release_manifest['artifact_sha256']}  {artifact.name}\n", encoding="ascii"
    )

    def display(path: Path) -> str:
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)

    return {
        "artifact": display(artifact),
        "manifest": display(manifest_path),
        "checksum": display(checksum),
        **release_manifest,
    }


def verify(artifact: Path | None = None) -> dict:
    version = current_version()
    artifact = artifact or OUT_DIR / f"btdoor-security-plus-{version}.zip"
    manifest_path = OUT_DIR / f"btdoor-security-plus-{version}.release.json"
    errors = []
    if not artifact.is_file():
        errors.append(f"artifact not found: {artifact}")
    if not manifest_path.is_file():
        errors.append(f"release manifest not found: {manifest_path}")
    if errors:
        return {"status": "FAIL", "errors": errors}
    meta = load_json(manifest_path)
    if sha256(artifact) != meta.get("artifact_sha256"):
        errors.append("artifact SHA-256 mismatch")
    try:
        with zipfile.ZipFile(artifact) as zf:
            bad = zf.testzip()
            if bad:
                errors.append(f"corrupt archive member: {bad}")
            names = set(zf.namelist())
            for rel in REQUIRED_COMPONENT_FILES:
                expected = f"custom_components/{DOMAIN}/{rel}"
                if expected not in names:
                    errors.append(f"missing archive member: {expected}")
            for entry in meta.get("files", []):
                if (
                    entry["path"] not in names
                    or hashlib.sha256(zf.read(entry["path"])).hexdigest() != entry["sha256"]
                ):
                    errors.append(f"file inventory mismatch: {entry['path']}")
    except zipfile.BadZipFile:
        errors.append("invalid ZIP archive")
    return {
        "status": "PASS" if not errors else "FAIL",
        "artifact": str(artifact),
        "errors": errors,
        "artifact_sha256": sha256(artifact),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="BTDoor reproducible release pipeline")
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("check", "report"):
        sub.add_parser(name)
    b = sub.add_parser("build")
    b.add_argument("--force", action="store_true")
    v = sub.add_parser("verify")
    v.add_argument("--artifact", type=Path)
    args = ap.parse_args()
    if args.command in {"check", "report"}:
        result = inspect()
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["structural_status"] == "PASS" else 1
    if args.command == "build":
        result = build(args.force)
    else:
        result = verify(args.artifact)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status", "PASS") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
