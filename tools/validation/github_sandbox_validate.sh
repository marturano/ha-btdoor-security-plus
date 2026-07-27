#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-check}"
PYTHON_BIN="${PYTHON_BIN:-python}"
REPORT_DIR="${REPORT_DIR:-artifacts/github-sandbox-validation}"
mkdir -p "$REPORT_DIR"

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install --upgrade ruff pytest pytest-cov

RUFF_VERSION=$(ruff --version)
"$PYTHON_BIN" --version | tee "$REPORT_DIR/python-version.txt"
printf '%s\n' "$RUFF_VERSION" | tee "$REPORT_DIR/ruff-version.txt"

if [[ "$MODE" == "fix" ]]; then
  ruff check custom_components/btdoor_security_plus tests tools --fix
  ruff format custom_components/btdoor_security_plus tests tools
  ruff check custom_components/btdoor_security_plus tests tools --fix
fi

ruff format --check custom_components/btdoor_security_plus tests tools \
  | tee "$REPORT_DIR/ruff-format.txt"
ruff check custom_components/btdoor_security_plus tests tools \
  | tee "$REPORT_DIR/ruff-check.txt"

"$PYTHON_BIN" -m compileall -q custom_components tools tests
"$PYTHON_BIN" -m pytest -p no:cacheprovider \
  | tee "$REPORT_DIR/pytest.txt"

for check in \
  "tools/publication/check_repository_publication.py" \
  "tools/check_repository_integrity.py" \
  "tools/documentation/check_document_consistency.py" \
  "tools/hygiene/check_hygiene.py" \
  "tools/governance/run_governance.py" \
  "tools/certification/run_certification.py"; do
  if [[ -f "$check" ]]; then
    name=$(basename "$check" .py)
    "$PYTHON_BIN" "$check" | tee "$REPORT_DIR/${name}.txt"
  fi
done

printf '%s\n' "PASS" > "$REPORT_DIR/result.txt"
