"""Typed support-diagnostic models and safe structured sanitization."""
from __future__ import annotations

from typing import Any, NotRequired, TypedDict
import re

from .support_sanitizer import ExportPolicy, sanitize_export_data


class SipPartyInfo(TypedDict, total=False):
    """Structured representation of a SIP party header."""

    raw: str
    uri: str
    display_name: str
    tag: str


class SipContactInfo(TypedDict, total=False):
    """Structured representation of a SIP Contact header."""

    raw: str
    uri: str
    instance: str
    parameters: dict[str, str | bool]


class SupportSnapshot(TypedDict, total=False):
    """Top-level support report payload."""

    generated_at: str
    integration: dict[str, Any]
    system: dict[str, Any]
    entry: dict[str, Any]
    options: dict[str, Any]
    runtime: dict[str, Any]
    health: dict[str, Any]
    tests: dict[str, Any]
    recent_debug: list[dict[str, Any]]


_ANGLE_URI_RE = re.compile(r"<(?P<uri>sips?:[^>]+)>", re.I)
_BARE_URI_RE = re.compile(r"(?P<uri>sips?:[^;\s,]+)", re.I)
_TAG_RE = re.compile(r"(?:^|;)tag=(?P<tag>[^;\s,>]+)", re.I)
_INSTANCE_RE = re.compile(
    r"(?:^|;)\+?sip\.instance\s*=\s*(?:\"(?P<quoted>[^\"]+)\"|(?P<plain>[^;\s,]+))",
    re.I,
)
_PARAM_RE = re.compile(r";(?P<name>[+a-z0-9_.-]+)(?:=(?P<value>[^;]+))?", re.I)


def sanitize_support_data(value: Any, key: str | None = None) -> Any:
    """Return a JSON-safe copy using the central standard export policy."""
    return sanitize_export_data(value, key, policy=ExportPolicy.STANDARD)


def sanitize_json_text(value: Any, *, indent: int | None = 2) -> str:
    """Serialize a sanitized structured value to guaranteed-valid JSON."""
    return json_dumps(sanitize_support_data(value), indent=indent)


def json_dumps(value: Any, *, indent: int | None = 2) -> str:
    """Central JSON serialization policy for support artifacts."""
    import json

    return json.dumps(value, ensure_ascii=False, indent=indent, default=str)


def parse_party_header(raw: Any) -> SipPartyInfo | None:
    """Parse From/To-style SIP header into a safe structured object."""
    if not raw:
        return None
    text = str(raw)
    angle = _ANGLE_URI_RE.search(text)
    bare = _BARE_URI_RE.search(text)
    uri = angle.group("uri") if angle else bare.group("uri") if bare else ""
    tag = (_TAG_RE.search(text).group("tag") if _TAG_RE.search(text) else "")
    display = text.split("<", 1)[0].strip().strip('"') if "<" in text else ""
    result: SipPartyInfo = {"raw": text}
    if uri:
        result["uri"] = uri
    if tag:
        result["tag"] = tag
    if display:
        result["display_name"] = display
    return sanitize_support_data(result)


def parse_contact_header(raw: Any) -> SipContactInfo | None:
    """Parse Contact header without relying on destructive text replacement."""
    if not raw:
        return None
    text = str(raw)
    angle = _ANGLE_URI_RE.search(text)
    bare = _BARE_URI_RE.search(text)
    uri = angle.group("uri") if angle else bare.group("uri") if bare else ""
    instance_match = _INSTANCE_RE.search(text)
    instance = ""
    if instance_match:
        instance = instance_match.group("quoted") or instance_match.group("plain") or ""
    params: dict[str, str | bool] = {}
    suffix = text[angle.end():] if angle else text
    for match in _PARAM_RE.finditer(suffix):
        name = match.group("name")
        value = match.group("value")
        params[name] = value.strip().strip('"') if value is not None else True
    result: SipContactInfo = {"raw": text, "parameters": params}
    if uri:
        result["uri"] = uri
    if instance:
        result["instance"] = instance
    return sanitize_support_data(result)


def structure_dialog_headers(headers: Any) -> dict[str, Any]:
    """Return normalized, support-safe SIP dialog headers."""
    if not isinstance(headers, dict):
        return {}
    normalized = dict(headers)
    normalized["from"] = parse_party_header(headers.get("from"))
    normalized["to"] = parse_party_header(headers.get("to"))
    normalized["contact"] = parse_contact_header(headers.get("contact"))
    return sanitize_support_data(normalized)


def sanitize_jsonl(text: str) -> str:
    """Sanitize JSONL records while preserving valid JSON on every line."""
    import json

    output: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            # Legacy/corrupt records are retained as a safely redacted text event.
            item = {"category": "legacy", "event": "unparsed_record", "data": {"raw": line}}
        output.append(json.dumps(sanitize_support_data(item), ensure_ascii=False, default=str))
    return "\n".join(output) + ("\n" if output else "")
