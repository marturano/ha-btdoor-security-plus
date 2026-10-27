from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = "btdoor_security_plus"
INTEGRATION = ROOT / "custom_components" / DOMAIN


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PUBLICATION PREFLIGHT: FAIL: {message}")


def check_validation_contract(root: Path) -> None:
    """Check the workflow delegation and the actual blocking Python gates."""
    validate = (root / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    for token in (
        "hacs/action@",
        "home-assistant/actions/hassfest@",
        "bash tools/validation/github_sandbox_validate.sh check",
    ):
        require(token in validate, f"validate workflow missing {token}")
    runner = (root / "tools/validation/github_sandbox_validate.sh").read_text(encoding="utf-8")
    require("set -euo pipefail" in runner, "validation runner must preserve gate failures")
    for gate in ("ruff-format", "ruff-check", "mypy", "pytest"):
        require(
            re.search(rf"(?m)^run_logged {gate} \"\$PYTHON_BIN\" -m ", runner) is not None,
            f"validation runner missing blocking {gate} gate",
        )
    require(
        re.search(
            r"(?m)^run_logged pytest .* -p no:cacheprovider -p pytest_asyncio\.plugin(?:\s|$)",
            runner,
        )
        is not None,
        "validation runner must explicitly configure pytest plugins",
    )


def main() -> None:
    require((ROOT / "README.md").is_file(), "README.md missing")
    require((ROOT / "LICENSE").is_file(), "LICENSE missing")
    require((ROOT / "hacs.json").is_file(), "hacs.json missing")
    require(INTEGRATION.is_dir(), f"custom_components/{DOMAIN} missing")

    integrations = sorted(
        path.name for path in (ROOT / "custom_components").iterdir() if path.is_dir()
    )
    require(integrations == [DOMAIN], f"expected one integration, found {integrations}")

    manifest = json.loads((INTEGRATION / "manifest.json").read_text(encoding="utf-8"))
    hacs = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
    version = manifest.get("version", "")
    require(manifest.get("domain") == DOMAIN, "manifest domain mismatch")
    require(bool(re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version)), "invalid version")
    require(manifest.get("config_flow") is True, "config_flow must be true")
    require(bool(manifest.get("integration_type")), "integration_type missing")
    require(bool(manifest.get("iot_class")), "iot_class missing")
    require(bool(manifest.get("documentation")), "documentation URL missing")
    require(bool(manifest.get("issue_tracker")), "issue tracker URL missing")
    require(bool(manifest.get("codeowners")), "codeowners missing")
    require(hacs.get("name") == manifest.get("name"), "HACS and manifest names differ")
    require(bool(hacs.get("homeassistant")), "minimum Home Assistant version missing")

    const_text = (INTEGRATION / "const.py").read_text(encoding="utf-8")
    match = re.search(r'^INTEGRATION_VERSION\s*=\s*["\']([^"\']+)["\']', const_text, re.MULTILINE)
    require(match is not None and match.group(1) == version, "const.py version mismatch")
    require((ROOT / "docs" / "release" / f"{version}.md").is_file(), "release notes missing")
    require((INTEGRATION / "quality_scale.yaml").is_file(), "quality_scale.yaml missing")
    require((INTEGRATION / "brand" / "icon.png").is_file(), "brand icon.png missing")
    require((INTEGRATION / "brand" / "icon@2x.png").is_file(), "brand icon@2x.png missing")

    check_validation_contract(ROOT)

    release = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    require("Verify tag and manifest versions" in release, "release tag/version guard missing")
    require("sha256sum" in release, "release checksum generation missing")

    print("PUBLICATION PREFLIGHT: PASS")
    print(f"domain={DOMAIN}")
    print(f"version={version}")
    print(f"minimum_home_assistant={hacs['homeassistant']}")
    print("remote_required=HACS,hassfest,GitHub Actions,release lifecycle")


if __name__ == "__main__":
    main()
