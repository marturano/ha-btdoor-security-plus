# Repository Production Audit

This canonical area contains the Phase 7A production audit for BTDoor Security+.

Run:

```bash
python tools/audit/production_audit.py
python tools/audit/production_audit.py --check --json
```

The audit verifies repository essentials, HACS and Home Assistant metadata, pinned runtime requirements, accidental secrets, temporary artifacts, and exact duplicate production files. It is intentionally non-promotional: a PASS result confirms repository production hygiene only and cannot approve a Final release without target validation.
