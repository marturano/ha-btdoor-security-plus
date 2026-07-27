#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_JSON = ROOT / 'docs/production-audit/PRODUCTION_AUDIT_REPORT.json'
REPORT_MD = ROOT / 'docs/production-audit/PRODUCTION_AUDIT_REPORT.md'
IGNORED_PARTS = {'.git', '.pytest_cache', '__pycache__'}
FORBIDDEN_SUFFIXES = {'.pyc', '.pyo', '.swp', '.tmp', '.bak'}
FORBIDDEN_NAMES = {'.DS_Store', 'Thumbs.db'}
SECRET_PATTERNS = [
    re.compile(r'(?i)(?:ha_token|access_token|api_key|client_secret)\s*[:=]\s*["\'](?!<|\$|example|changeme)[^"\']{12,}["\']'),
    re.compile(r'gh[pousr]_[A-Za-z0-9_]{30,}'),
]
ALLOWED_DUPLICATE_GROUPS = {
    frozenset({'custom_components/btdoor_security_plus/strings.json', 'custom_components/btdoor_security_plus/translations/en.json'}),
    frozenset({'custom_components/btdoor_security_plus/translations/nb.json', 'custom_components/btdoor_security_plus/translations/da.json'}),
}
REQUIRED = [
    'LICENSE', 'README.md', 'SECURITY.md', 'CONTRIBUTING.md', 'hacs.json',
    'custom_components/btdoor_security_plus/manifest.json',
    'custom_components/btdoor_security_plus/__init__.py',
    'custom_components/btdoor_security_plus/config_flow.py',
]


def files():
    for p in ROOT.rglob('*'):
        if p.is_file() and not any(part in IGNORED_PARTS for part in p.parts):
            yield p


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def audit() -> dict:
    all_files = list(files())
    missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
    forbidden = [rel(p) for p in all_files if p.name in FORBIDDEN_NAMES or p.suffix.lower() in FORBIDDEN_SUFFIXES]
    secret_hits = []
    for p in all_files:
        if p.suffix.lower() not in {'.py', '.json', '.yaml', '.yml', '.md', '.txt', '.toml'}:
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            secret_hits.append(rel(p))
    manifest = json.loads((ROOT / 'custom_components/btdoor_security_plus/manifest.json').read_text(encoding='utf-8'))
    hacs = json.loads((ROOT / 'hacs.json').read_text(encoding='utf-8'))
    version_ok = bool(re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', str(manifest.get('version', ''))))
    pinned = all(re.fullmatch(r'[^<>=!~]+==[^<>=!~]+', item or '') for item in manifest.get('requirements', []))
    codeowners_ok = bool(manifest.get('codeowners')) and all(str(x).startswith('@') for x in manifest['codeowners'])
    urls_ok = all(str(manifest.get(k, '')).startswith('https://') for k in ('documentation', 'issue_tracker'))
    ha_floor_ok = bool(re.fullmatch(r'2026\.\d+\.\d+', str(hacs.get('homeassistant', ''))))
    duplicate_groups = {}
    for p in all_files:
        if p.stat().st_size == 0 or rel(p).startswith(('dist/', 'docs/')):
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        duplicate_groups.setdefault(digest, []).append(rel(p))
    all_duplicates = [sorted(v) for v in duplicate_groups.values() if len(v) > 1]
    duplicates = [v for v in all_duplicates if frozenset(v) not in ALLOWED_DUPLICATE_GROUPS]
    allowed_duplicates = [v for v in all_duplicates if frozenset(v) in ALLOWED_DUPLICATE_GROUPS]
    checks = {
        'required_files': not missing,
        'forbidden_artifacts': not forbidden,
        'secret_scan': not secret_hits,
        'manifest_version': version_ok,
        'requirements_pinned': pinned,
        'codeowners': codeowners_ok,
        'https_metadata_urls': urls_ok,
        'hacs_2026_floor': ha_floor_ok,
        'production_duplicate_scan': not duplicates,
    }
    return {
        'schema_version': 1,
        'generated': date.today().isoformat(),
        'phase': '7A',
        'repository_file_count': len(all_files),
        'status': 'PASS' if all(checks.values()) else 'FAIL',
        'checks': checks,
        'findings': {
            'missing_required_files': missing,
            'forbidden_artifacts': forbidden,
            'potential_secret_files': secret_hits,
            'duplicate_groups_outside_docs_and_dist': duplicates,
            'allowed_duplicate_groups': allowed_duplicates,
        },
        'release_context': {
            'integration_version': manifest.get('version'),
            'homeassistant_minimum': hacs.get('homeassistant'),
            'publication_approval': 'NOT_GRANTED',
            'note': 'Phase 7A audits repository production readiness but does not override target certification or release gates.'
        }
    }


def write_report(payload: dict) -> None:
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    lines = ['# Production Audit Report', '', f"- Generated: `{payload['generated']}`", f"- Phase: `{payload['phase']}`", f"- Status: **{payload['status']}**", f"- Files audited: **{payload['repository_file_count']}**", '', '## Checks', '']
    for name, ok in payload['checks'].items():
        lines.append(f"- {'PASS' if ok else 'FAIL'} — `{name}`")
    lines += ['', '## Release boundary', '', payload['release_context']['note'], '', 'Publication approval remains **NOT GRANTED** until target certification and all release gates are satisfied.', '']
    REPORT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    payload = audit()
    if not args.check:
        write_report(payload)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Production audit: {payload['status']}")
        for name, ok in payload['checks'].items(): print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    return 0 if payload['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
