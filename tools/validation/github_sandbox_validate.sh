#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-check}"
PYTHON_BIN="${PYTHON_BIN:-python}"
REPORT_DIR="${REPORT_DIR:-artifacts/github-sandbox-validation}"
mkdir -p "$REPORT_DIR"

run_logged() {
  local name="$1"
  shift
  "$@" 2>&1 | tee "$REPORT_DIR/${name}.txt"
}

run_logged pip-upgrade "$PYTHON_BIN" -m pip install --upgrade pip
run_logged dependencies "$PYTHON_BIN" -m pip install --upgrade \
  ruff mypy pytest pytest-asyncio pytest-cov

run_logged python-version "$PYTHON_BIN" --version
run_logged ruff-version "$PYTHON_BIN" -m ruff --version
run_logged mypy-version "$PYTHON_BIN" -m mypy --version
run_logged pytest-version "$PYTHON_BIN" -m pytest --version

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

export PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"
run_logged pytest "$PYTHON_BIN" -m pytest -q -p no:cacheprovider -p pytest_asyncio.plugin

for check in \
  "tools/publication/check_repository_publication.py" \
  "tools/check_repository_integrity.py" \
  "tools/documentation/check_document_consistency.py" \
  "tools/hygiene/check_hygiene.py" \
  "tools/governance/run_governance.py" \
  "tools/certification/run_certification.py"; do
  if [[ -f "$check" ]]; then
    name=$(basename "$check" .py)
    run_logged "$name" "$PYTHON_BIN" "$check"
  fi
done

if ! git diff --quiet; then
  git diff --stat | tee "$REPORT_DIR/dirty-tree.txt"
  echo "Validation changed the repository tree" >&2
  exit 1
fi

printf '%s\n' "PASS" | tee "$REPORT_DIR/result.txt"
