# GitHub validation error remediation - 2026-07-27

## Evidence reviewed

The GitHub run reported two independent failure families:

1. Ruff reported 882 findings across 121 Python files. The dominant classes were compressed multi-statement lines, import ordering, unused imports, imports below module constants, Python modernization rules, and asynchronous filesystem access rules.
2. Home Assistant 2026.3 through 2026.7 could not be installed under Python 3.13 because those releases require Python 3.14.2 or newer.

## Remediation applied

- The compatibility matrix now maps Home Assistant 2026.1 to Python 3.13 and Home Assistant 2026.3/2026.5/2026.6/2026.7 to Python 3.14.2.
- The canonical sandbox validation workflow now uses Python 3.14.2.
- The Ruff remediation workflow now installs the latest stable Ruff, applies safe fixes and formatting, captures residual findings, commits the mechanical remediation, and then fails if semantic findings remain.
- An explicit optional unsafe-fix input is available for supervised remediation runs. It does not alter the mandatory read-only validation gate.

## Release decision

The repository is not declared Ruff compliant by this change alone. The mandatory sequence is:

1. run `Ruff Remediation`;
2. review and correct any residual semantic findings;
3. run `GitHub Sandbox Validation` in read-only mode;
4. require all release, governance and Quality Scale GOLD gates to pass.

Any residual Ruff error or incompatible Home Assistant matrix job keeps the release blocked.
