from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROHIBITED_DIR_NAMES = {'.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache'}
PROHIBITED_FILES = {'.DS_Store', 'Thumbs.db'}
DEPRECATED_PATHS = {
    'docs/archive',
    'docs/project/NEW_CHAT_HANDOFF.md',
    'docs/project/PRODUCT_ROADMAP_1.1_TO_2.0.md',
    'docs/project/DOCUMENTATION_INDEX.md',
}
REQUIRED = {
    'docs/project/REPOSITORY_INVENTORY.md',
    'docs/validation/VALIDATION_MAINTENANCE_POLICY.md',
    'docs/validation/VALIDATION_REGISTER.md',
    'docs/validation/VALIDATION_REPORT_1.1.0-rc.15.md',
}

errors=[]
for path in ROOT.rglob('*'):
    rel=path.relative_to(ROOT).as_posix()
    if path.is_dir() and path.name in PROHIBITED_DIR_NAMES:
        errors.append(f'cache directory: {rel}')
    if path.is_file() and path.name in PROHIBITED_FILES:
        errors.append(f'local artifact: {rel}')
    if path.is_dir() and not any(path.iterdir()):
        errors.append(f'empty directory: {rel}')
for rel in DEPRECATED_PATHS:
    if (ROOT/rel).exists(): errors.append(f'deprecated path retained: {rel}')
for rel in REQUIRED:
    if not (ROOT/rel).is_file(): errors.append(f'missing canonical file: {rel}')
if errors:
    print('ORPHAN/HYGIENE CHECK FAILED')
    print('\n'.join(f'- {e}' for e in errors))
    sys.exit(1)
print('ORPHAN/HYGIENE CHECK PASSED')
