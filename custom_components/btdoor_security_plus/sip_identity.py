"""SIP identity parsing helpers for runtime entities and diagnostics."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re

_ANGLE_URI_RE = re.compile(r"<(?P<uri>sips?:[^>]+)>", re.I)
_BARE_URI_RE = re.compile(r"(?P<uri>sips?:[^;\s,]+)", re.I)
_TAG_RE = re.compile(r"(?:^|;)\s*tag=(?P<tag>[^;\s,>]+)", re.I)


@dataclass(frozen=True, slots=True)
class SipIdentity:
    """Normalized From/To SIP identity."""

    raw: str
    uri: str | None = None
    user: str | None = None
    domain: str | None = None
    tag: str | None = None
    display_name: str | None = None

    @property
    def label(self) -> str:
        """Return a compact user-facing label."""
        return self.display_name or self.user or self.uri or self.raw

    def as_dict(self) -> dict[str, str]:
        """Return populated values only."""
        return {key: value for key, value in asdict(self).items() if value}


def parse_sip_identity(value: object | None) -> SipIdentity | None:
    """Parse a SIP party header without losing the original value."""
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None

    angle = _ANGLE_URI_RE.search(raw)
    bare = _BARE_URI_RE.search(raw)
    uri = angle.group("uri") if angle else bare.group("uri") if bare else None

    display_name: str | None = None
    if angle:
        prefix = raw[: angle.start()].strip().strip('"').strip()
        display_name = prefix or None

    tag_match = _TAG_RE.search(raw)
    tag = tag_match.group("tag") if tag_match else None

    user: str | None = None
    domain: str | None = None
    if uri:
        address = uri.split(":", 1)[1] if ":" in uri else uri
        address = address.split(";", 1)[0]
        if "@" in address:
            user, domain = address.split("@", 1)
        else:
            user = address or None
        user = user or None
        domain = domain or None

    return SipIdentity(
        raw=raw,
        uri=uri,
        user=user,
        domain=domain,
        tag=tag,
        display_name=display_name,
    )
