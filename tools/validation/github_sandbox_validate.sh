#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-check}"
PYTHON_BIN="${PYTHON_BIN:-python}"
SOURCE_ROOT="$(pwd -P)"
REQUESTED_REPORT_DIR="${REPORT_DIR:-$SOURCE_ROOT/artifacts/github-sandbox-validation}"
if [[ "$REQUESTED_REPORT_DIR" != /* ]]; then
  REQUESTED_REPORT_DIR="$SOURCE_ROOT/$REQUESTED_REPORT_DIR"
fi
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/btdoor-validation.XXXXXXXX")"
REPORT_DIR="$RUN_DIR/evidence"
mkdir -p "$REPORT_DIR"

finish() {
  local status=$?
  trap - EXIT
  mkdir -p "$REQUESTED_REPORT_DIR"
  cp -R "$REPORT_DIR/." "$REQUESTED_REPORT_DIR/"
  case "$RUN_DIR" in
    "${TMPDIR:-/tmp}"/btdoor-validation.*) rm -rf -- "$RUN_DIR" ;;
  esac
  exit "$status"
}
trap finish EXIT

PYTHON_BIN="$("$PYTHON_BIN" -c 'import sys; print(sys.executable)')"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$RUN_DIR/pycache"
export RUFF_CACHE_DIR="$RUN_DIR/ruff-cache"
export MYPY_CACHE_DIR="$RUN_DIR/mypy-cache"
export COVERAGE_FILE="$RUN_DIR/.coverage"

run_logged() {
  local name="$1"
  shift
  "$@" 2>&1 | tee "$REPORT_DIR/${name}.txt"
}

run_logged pip-upgrade "$PYTHON_BIN" -m pip install --upgrade pip
run_logged dependencies "$PYTHON_BIN" -m pip install -r requirements-validation.txt

run_logged python-version "$PYTHON_BIN" --version
run_logged ruff-version "$PYTHON_BIN" -m ruff --version
run_logged mypy-version "$PYTHON_BIN" -m mypy --version
run_logged pytest-version "$PYTHON_BIN" -m pytest --version
run_logged dependency-versions "$PYTHON_BIN" -m pip freeze

run_logged workflow-contract "$PYTHON_BIN" tools/validation/check_github_workflows.py

if [[ "$MODE" == "fix" ]]; then
  run_logged ruff-fix "$PYTHON_BIN" -m ruff check \
    custom_components/btdoor_security_plus tests tools --fix
  run_logged ruff-format-fix "$PYTHON_BIN" -m ruff format \
    custom_components/btdoor_security_plus tests tools
  run_logged ruff-fix-second-pass "$PYTHON_BIN" -m ruff check \
    custom_components/btdoor_security_plus tests tools --fix
fi

run_logged ruff-format "$PYTHON_BIN" -m ruff format --check \
  custom_components/btdoor_security_plus tests tools
run_logged ruff-check "$PYTHON_BIN" -m ruff check \
  custom_components/btdoor_security_plus tests tools
run_logged mypy "$PYTHON_BIN" -m mypy custom_components/btdoor_security_plus
run_logged compileall "$PYTHON_BIN" -m compileall -q custom_components tools tests

run_logged json-validation "$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path

paths = list(Path("custom_components/btdoor_security_plus").rglob("*.json"))
paths.extend((Path("hacs.json"), Path("PROJECT_MANIFEST.yaml")))
for path in paths:
    if path.suffix == ".json":
        json.loads(path.read_text(encoding="utf-8"))
print(f"Validated {sum(path.suffix == '.json' for path in paths)} JSON files")
PY

# Tests and governance generate evidence files. Run them against an exact source
# copy so their reports cannot mutate the checked-out repository or pollute its
# inventory. Publish command logs only after every gate has finished.
run_logged validation-copy "$PYTHON_BIN" - "$SOURCE_ROOT" "$RUN_DIR/repository" <<'PY'
from pathlib import Path
import shutil
import sys

source, target = map(Path, sys.argv[1:])
shutil.copytree(
    source,
    target,
    ignore=shutil.ignore_patterns(
        ".git", "artifacts", "__pycache__", ".pytest_cache", ".mypy_cache",
        ".ruff_cache", ".venv", "venv",
    ),
)
print("Prepared isolated copy of the validation source")
PY
cd "$RUN_DIR/repository"

export PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"
run_logged pytest "$PYTHON_BIN" -m pytest -q -p no:cacheprovider -p pytest_asyncio.plugin \
  -p pytest_cov.plugin --cov=custom_components/btdoor_security_plus \
  --cov-report="json:$REPORT_DIR/integration-coverage.raw.json" \
  --cov-report=term:skip-covered --cov-fail-under=95
cp "$REPORT_DIR/integration-coverage.raw.json" docs/quality-scale/integration_coverage.raw.json
run_logged coverage-gate "$PYTHON_BIN" tools/quality_scale/coverage_gate.py --check
cp docs/quality-scale/integration_coverage.json "$REPORT_DIR/integration-coverage.json"

run_logged test-workspace-cleanup "$PYTHON_BIN" - <<'PY'
from pathlib import Path

for name in ("ha-certification-work", "target-validation-work"):
    path = Path(name)
    if path.is_dir() and not any(path.iterdir()):
        path.rmdir()
print("Removed only empty test workspaces; unexpected contents remain subject to validation")
PY

for check in \
  "tools/publication/check_repository_publication.py" \
  "tools/check_repository_integrity.py" \
  "tools/documentation/check_document_consistency.py" \
  "tools/governance/run_governance.py" \
  "tools/certification/run_certification.py" \
  "tools/hygiene/check_hygiene.py"; do
  if [[ -f "$check" ]]; then
    name=$(basename "$check" .py)
    run_logged "$name" "$PYTHON_BIN" "$check"
  fi
done

cd "$SOURCE_ROOT"
if [[ "$MODE" != "fix" ]] && ! git diff --quiet; then
  git diff --stat | tee "$REPORT_DIR/dirty-tree.txt"
  echo "Validation changed the repository tree" >&2
  exit 1
fi

printf '%s\n' "PASS" | tee "$REPORT_DIR/result.txt"
