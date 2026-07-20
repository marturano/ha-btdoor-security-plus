"""Tests for support report naming and legacy cleanup compatibility."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from custom_components.btdoor_security_plus.support_naming import (
    SUPPORT_ARTIFACT_PREFIX,
    build_support_artifact_names,
    is_managed_support_artifact,
)


def test_support_artifacts_use_new_project_name() -> None:
    names = build_support_artifact_names(datetime(2026, 7, 17, 10, 49, 39, tzinfo=UTC))
    assert names.report_name == "BTDoorSecurityPlus_Support_20260717-104939.md"
    assert names.bundle_name == "BTDoorSecurityPlus_Support_20260717-104939.zip"
    assert names.stem.startswith(SUPPORT_ARTIFACT_PREFIX)


def test_current_and_legacy_artifacts_are_managed(tmp_path: Path) -> None:
    current = tmp_path / "BTDoorSecurityPlus_Support_20260717-104939.zip"
    legacy = tmp_path / "BTDoorPlus_Support_20260717-104939.md"
    unrelated = tmp_path / "notes.md"
    for path in (current, legacy, unrelated):
        path.write_text("test", encoding="utf-8")

    assert is_managed_support_artifact(current)
    assert is_managed_support_artifact(legacy)
    assert not is_managed_support_artifact(unrelated)
