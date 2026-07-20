"""Non-invasive media negotiation preparation for BTDoor Security+."""
from __future__ import annotations

from dataclasses import dataclass, field
import base64
import difflib
import hashlib
import json
import re
import secrets
import socket
import time
from typing import Any

SUPPORTED_SRTP_SUITES = (
    "AES_CM_128_HMAC_SHA1_80",
    "AES_CM_128_HMAC_SHA1_32",
)
AUDIO_CODEC_PREFERENCE = ("SPEEX/8000", "G729/8000", "PCMA/8000", "PCMU/8000", "G722/8000")
VIDEO_CODEC_PREFERENCE = ("H264/90000", "MP4V-ES/90000", "H263/90000")

@dataclass(slots=True)
class SrtpCryptoOffer:
    """One SDP SDES crypto attribute."""
    tag: int
    suite: str
    key_method: str
    key_params: str = field(repr=False)

    @property
    def inline_value(self) -> str | None:
        """Return the base64 key field only; never expose it through public_dict."""
        if self.key_method.lower() != "inline":
            return None
        return self.key_params.split("|", 1)[0].strip()

    @property
    def decoded_key(self) -> bytes | None:
        value = self.inline_value
        if not value:
            return None
        try:
            return base64.b64decode(value, validate=True)
        except (ValueError, base64.binascii.Error):
            return None

    @property
    def key_fingerprint(self) -> str:
        decoded = self.decoded_key
        source = decoded if decoded is not None else self.key_params.encode()
        return hashlib.sha256(source).hexdigest()[:16]

    @property
    def lifetime(self) -> str | None:
        parts = self.key_params.split("|")
        return parts[1] if len(parts) > 1 and parts[1] else None

    @property
    def mki(self) -> str | None:
        parts = self.key_params.split("|")
        return parts[2] if len(parts) > 2 and parts[2] else None

    def public_dict(self) -> dict[str, Any]:
        decoded = self.decoded_key
        return {
            "tag": self.tag,
            "suite": self.suite,
            "key_method": self.key_method,
            "key_fingerprint": self.key_fingerprint,
            "key_length": len(decoded) if decoded is not None else None,
            "lifetime": self.lifetime,
            "mki_present": self.mki is not None,
        }

@dataclass(slots=True)
class MediaPreparation:
    """Prepared local media endpoints and selected offer parameters."""
    state: str
    audio_payload_type: int | None = None
    audio_codec: str | None = None
    audio_local_rtp_port: int | None = None
    audio_local_rtcp_port: int | None = None
    audio_remote_address: str | None = None
    audio_remote_port: int | None = None
    audio_protocol: str | None = None
    video_payload_type: int | None = None
    video_codec: str | None = None
    video_local_rtp_port: int | None = None
    video_local_rtcp_port: int | None = None
    video_remote_address: str | None = None
    video_remote_port: int | None = None
    video_protocol: str | None = None
    srtp_suite: str | None = None
    remote_crypto_tag: int | None = None
    remote_key_fingerprint: str | None = None
    local_key_fingerprint: str | None = None
    remote_key_length: int | None = None
    local_key_length: int | None = None
    local_crypto_tag: int | None = None
    local_media_address: str | None = None
    answer_sdp_fingerprint: str | None = None
    answer_sdp_redacted: str | None = None
    prepared_at: float | None = None
    issues: tuple[str, ...] = ()
    _sockets: tuple[socket.socket, ...] = field(default=(), repr=False)
    _local_key: bytes | None = field(default=None, repr=False)

    def close(self) -> None:
        for sock in self._sockets:
            try:
                sock.close()
            except OSError:
                pass
        self._sockets = ()
        self._local_key = None
        if self.state == "prepared":
            self.state = "released"

    def public_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "audio": {
                "payload_type": self.audio_payload_type,
                "codec": self.audio_codec,
                "local_rtp_port": self.audio_local_rtp_port,
                "local_rtcp_port": self.audio_local_rtcp_port,
                "remote_address": self.audio_remote_address,
                "remote_port": self.audio_remote_port,
                "protocol": self.audio_protocol,
            },
            "video": {
                "payload_type": self.video_payload_type,
                "codec": self.video_codec,
                "local_rtp_port": self.video_local_rtp_port,
                "local_rtcp_port": self.video_local_rtcp_port,
                "remote_address": self.video_remote_address,
                "remote_port": self.video_remote_port,
                "protocol": self.video_protocol,
            },
            "srtp": {
                "suite": self.srtp_suite,
                "remote_crypto_tag": self.remote_crypto_tag,
                "local_crypto_tag": self.local_crypto_tag,
                "remote_key_fingerprint": self.remote_key_fingerprint,
                "local_key_fingerprint": self.local_key_fingerprint,
                "remote_key_length": self.remote_key_length,
                "local_key_length": self.local_key_length,
            },
            "local_media_address": self.local_media_address,
            "answer_sdp_fingerprint": self.answer_sdp_fingerprint,
            "answer_sdp_redacted": self.answer_sdp_redacted,
            "prepared_at": self.prepared_at,
            "issues": list(self.issues),
        }


def parse_crypto_attribute(value: str) -> SrtpCryptoOffer | None:
    """Parse an SDP a=crypto attribute without exposing its key material."""
    parts = value.strip().split(None, 2)
    if len(parts) < 3:
        return None
    try:
        tag = int(parts[0])
    except ValueError:
        return None
    suite = parts[1].upper()
    key_value = parts[2]
    if ":" not in key_value:
        return None
    key_method, key_params = key_value.split(":", 1)
    return SrtpCryptoOffer(tag=tag, suite=suite, key_method=key_method, key_params=key_params)


def _select_codec(codecs: tuple[str, ...], preferences: tuple[str, ...]) -> tuple[int | None, str | None]:
    parsed: list[tuple[int, str]] = []
    for item in codecs:
        if ":" not in item:
            continue
        payload, codec = item.split(":", 1)
        try:
            parsed.append((int(payload), codec.upper()))
        except ValueError:
            continue
    for preferred in preferences:
        for payload, codec in parsed:
            if codec == preferred:
                return payload, codec
    return parsed[0] if parsed else (None, None)


def _bind_udp_pair() -> tuple[socket.socket, socket.socket, int, int]:
    """Reserve a local even RTP port and its following RTCP port."""
    for _ in range(100):
        rtp_port = 20000 + 2 * secrets.randbelow(20000)
        rtp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rtcp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            rtp.bind(("0.0.0.0", rtp_port))
            rtcp.bind(("0.0.0.0", rtp_port + 1))
            rtp.setblocking(False)
            rtcp.setblocking(False)
            return rtp, rtcp, rtp_port, rtp_port + 1
        except OSError:
            rtp.close(); rtcp.close()
    raise OSError("Unable to reserve a local RTP/RTCP port pair")



def _discover_local_address(remote_address: str | None) -> str:
    """Discover the local IPv4 address selected by the routing table."""
    if not remote_address:
        return "0.0.0.0"
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect((remote_address, 9))
        return str(probe.getsockname()[0])
    except OSError:
        return "0.0.0.0"
    finally:
        probe.close()


def _codec_name(codec: str | None) -> str | None:
    if not codec:
        return None
    return codec.split("/", 1)[0]


def _build_answer_sdp(result: MediaPreparation, local_key: bytes) -> tuple[str, str]:
    """Build an in-memory SDP answer and a redacted export-safe copy."""
    address = result.local_media_address or "0.0.0.0"
    session_id = secrets.randbits(63)
    session_version = session_id
    crypto_tag = result.local_crypto_tag or 1
    suite = result.srtp_suite or "AES_CM_128_HMAC_SHA1_80"
    inline_key = base64.b64encode(local_key).decode("ascii")

    lines = [
        "v=0",
        f"o=BTDoorSecurityPlus {session_id} {session_version} IN IP4 {address}",
        "s=BTDoor Security+",
        f"c=IN IP4 {address}",
        "t=0 0",
    ]

    if result.audio_payload_type is not None and result.audio_local_rtp_port:
        lines.extend([
            f"m=audio {result.audio_local_rtp_port} RTP/SAVP {result.audio_payload_type}",
            f"a=rtcp:{result.audio_local_rtcp_port}",
            f"a=rtpmap:{result.audio_payload_type} {result.audio_codec}",
            f"a=crypto:{crypto_tag} {suite} inline:{inline_key}",
            "a=sendrecv",
        ])

    if result.video_payload_type is not None and result.video_local_rtp_port:
        lines.extend([
            f"m=video {result.video_local_rtp_port} RTP/SAVP {result.video_payload_type}",
            f"a=rtcp:{result.video_local_rtcp_port}",
            f"a=rtpmap:{result.video_payload_type} {result.video_codec}",
            f"a=crypto:{crypto_tag} {suite} inline:{inline_key}",
            "a=recvonly",
        ])

    answer = "\r\n".join(lines) + "\r\n"
    redacted = re.sub(r"(inline:)[A-Za-z0-9+/=]+", r"\1[REDACTED]", answer)
    return answer, redacted



def build_sdp_diff(remote_sdp: str | None, local_sdp_redacted: str | None) -> str:
    """Return an export-safe unified SDP diff."""
    remote = (remote_sdp or "").replace("\r\n", "\n").splitlines()
    local = (local_sdp_redacted or "").replace("\r\n", "\n").splitlines()
    if not remote and not local:
        return ""
    return "\n".join(
        difflib.unified_diff(
            remote,
            local,
            fromfile="remote_sdp",
            tofile="local_sdp",
            lineterm="",
        )
    )


def media_snapshot(plan: MediaPreparation | None) -> dict[str, Any] | None:
    """Return a detached public snapshot safe to keep after socket release."""
    if plan is None:
        return None
    return json.loads(json.dumps(plan.public_dict(), default=str))


def prepare_media_offer(description: Any) -> MediaPreparation:
    """Prepare local sockets and select offered codecs/SRTP without answering SIP."""
    sockets: list[socket.socket] = []
    issues: list[str] = []
    result = MediaPreparation(state="not_available")
    crypto_offers: list[SrtpCryptoOffer] = []
    try:
        for media in description.media:
            crypto_offers.extend(media.crypto)
            if media.media == "audio" and result.audio_codec is None and media.port:
                pt, codec = _select_codec(media.codecs, AUDIO_CODEC_PREFERENCE)
                result.audio_payload_type, result.audio_codec = pt, codec
                result.audio_remote_address = media.connection_address
                result.audio_remote_port = media.port
                result.audio_protocol = media.protocol
                rtp, rtcp, rp, rcp = _bind_udp_pair()
                sockets.extend((rtp, rtcp))
                result.audio_local_rtp_port, result.audio_local_rtcp_port = rp, rcp
            elif media.media == "video" and result.video_codec is None and media.port:
                pt, codec = _select_codec(media.codecs, VIDEO_CODEC_PREFERENCE)
                result.video_payload_type, result.video_codec = pt, codec
                result.video_remote_address = media.connection_address
                result.video_remote_port = media.port
                result.video_protocol = media.protocol
                rtp, rtcp, rp, rcp = _bind_udp_pair()
                sockets.extend((rtp, rtcp))
                result.video_local_rtp_port, result.video_local_rtcp_port = rp, rcp

        selected_crypto = next(
            (offer for suite in SUPPORTED_SRTP_SUITES for offer in crypto_offers if offer.suite == suite),
            None,
        )
        secure_protocol = any("SAVP" in str(media.protocol).upper() for media in description.media)
        if secure_protocol and selected_crypto is None:
            issues.append("No supported SDES-SRTP crypto suite was offered")
        if selected_crypto is not None:
            result.srtp_suite = selected_crypto.suite
            result.remote_crypto_tag = selected_crypto.tag
            result.local_crypto_tag = selected_crypto.tag
            result.remote_key_fingerprint = selected_crypto.key_fingerprint
            remote_key = selected_crypto.decoded_key
            result.remote_key_length = len(remote_key) if remote_key is not None else None
            if remote_key is None:
                issues.append("The remote SDES-SRTP inline key is not valid base64")
            elif len(remote_key) != 30:
                issues.append(
                    f"Unexpected remote SDES-SRTP master key length: {len(remote_key)}"
                )

            # RFC 4568 AES_CM_128 suites use 30 bytes (16-byte key + 14-byte salt).
            local_key = secrets.token_bytes(30)
            result._local_key = local_key
            result.local_key_length = len(local_key)
            result.local_key_fingerprint = hashlib.sha256(local_key).hexdigest()[:16]
            result.local_media_address = _discover_local_address(
                result.audio_remote_address or result.video_remote_address
            )
            answer_sdp, redacted_sdp = _build_answer_sdp(result, local_key)
            result.answer_sdp_fingerprint = hashlib.sha256(
                answer_sdp.encode("utf-8")
            ).hexdigest()[:16]
            result.answer_sdp_redacted = redacted_sdp

        if result.audio_codec is None:
            issues.append("No audio codec could be selected")
        if result.video_remote_port and result.video_codec is None:
            issues.append("No video codec could be selected")
        result._sockets = tuple(sockets)
        result.prepared_at = time.time()
        result.issues = tuple(issues)
        result.state = "prepared" if not issues else "degraded"
        return result
    except Exception:
        for sock in sockets:
            sock.close()
        raise
