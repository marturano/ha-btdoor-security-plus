"""BTicino MyHomeWeb cloud provisioning client."""

from __future__ import annotations

import asyncio

import base64
import hashlib
import io
import json
import logging
import re
import secrets
import shutil
import zipfile
import warnings
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aiohttp import (
    ClientConnectionError,
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    ServerDisconnectedError,
)
from asn1crypto import algos as asn1_algos
from asn1crypto import csr as asn1_csr
from asn1crypto import keys as asn1_keys
from asn1crypto import pem as asn1_pem
from asn1crypto import x509 as asn1_x509
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import pkcs7

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://www.myhomeweb.com"
APP_VERSION = "legacy-215"
HEADERS = {
    "prj_name": "C3X",
    "Content-Type": "application/json",
    "User-Agent": "Door Entry CLASSE300X/1.17.3",
}


class BticinoCloudError(Exception):
    """Base cloud error."""


class BticinoCloudAuthenticationError(BticinoCloudError):
    """Cloud authentication failed."""


class BticinoCloudConnectionError(BticinoCloudError):
    """Cloud connection failed."""


def _looks_like_auth_rejection(status: int, raw: str, body: Any) -> bool:
    """Return True when the MyHomeWeb response represents rejected credentials."""
    if status in (401, 403, 498):
        return True

    # MyHomeWeb has historically returned several non-standard status codes
    # for an invalid login. Do not classify network throttling/timeouts as bad
    # credentials.
    if 400 <= status < 500 and status not in (408, 425, 429):
        return True
    if status == 500:
        return True

    values: list[str] = [raw]
    if isinstance(body, dict):
        for key in (
            "message", "Message", "error", "Error",
            "description", "Description", "result", "Result",
            "status", "Status",
        ):
            value = body.get(key)
            if value is not None:
                values.append(str(value))

    normalized = " ".join(values).casefold()
    markers = (
        "invalid credential", "invalid credentials",
        "invalid username", "invalid password",
        "wrong password", "authentication failed",
        "authentication rejected", "unauthorized",
        "access denied", "login failed",
        "utente non valido", "password non valida",
        "credenziali non valide", "autenticazione fallita",
    )
    return any(marker in normalized for marker in markers)


@dataclass(slots=True)
class PlantGateway:
    """Combined plant and gateway selection."""

    plant_id: str
    plant_name: str
    gateway_id: str
    gateway_name: str

    @property
    def label(self) -> str:
        """Return UI label."""
        name = self.plant_name or "BTDoor Security+"
        gateway = self.gateway_name or self.gateway_id
        return f"{name} - {gateway} ({self.gateway_id})"


@dataclass(slots=True)
class ProvisionedCredentials:
    """Provisioned SIP and certificate credentials."""

    plant_id: str
    plant_name: str
    gateway_id: str
    gateway_name: str
    sip_account: str
    sip_password: str
    id_device: str
    device_name: str
    client_cert_path: str
    client_key_path: str
    ca_chain_path: str | None
    certificate_not_after: str


class BticinoCloudClient:
    """Client for the legacy Door Entry 300X MyHomeWeb API."""

    def __init__(
        self,
        session: ClientSession,
        *,
        email: str,
        password: str,
        base_url: str = BASE_URL,
    ) -> None:
        self._session = session
        self.email = email.strip()
        self.password = password
        self.base_url = base_url.rstrip("/")
        self.auth_token = ""

    async def async_login(self) -> None:
        """Authenticate and acquire auth_token."""
        try:
            body, headers = await self._request(
                "POST",
                "/eliot/users/sign_in",
                {
                    "username": self.email,
                    "pwd": self.password,
                    "appVersion": APP_VERSION,
                },
                authenticated=False,
            )
        except BticinoCloudError:
            raise
        token = self.auth_token or headers.get("auth_token")
        if not token and isinstance(body, dict):
            token = body.get("auth_token")
        if not token:
            parsed = _parse_payload(body)
            if isinstance(parsed, dict):
                token = _get(parsed, "auth_token", "AuthToken", "token")
        if not token:
            _LOGGER.info(
                "MyHomeWeb login response did not contain an authentication token; "
                "treating the supplied credentials as invalid"
            )
            raise BticinoCloudAuthenticationError(
                "MyHomeWeb email or password rejected (authentication token missing)"
            )
        self.auth_token = str(token)

    async def async_list_gateways(self) -> list[PlantGateway]:
        """Return all gateways associated with the account."""
        plants_body, _ = await self._request("GET", "/eliot/plants")
        result: list[PlantGateway] = []
        for plant in _items(plants_body):
            plant_id = _get(plant, "PlantId", "id")
            if not plant_id:
                continue
            plant_name = _get(plant, "PlantName", "Name")
            gateway_body, _ = await self._request(
                "GET", f"/eliot/plants/{plant_id}/gateway/"
            )
            for gateway in _items(gateway_body):
                gateway_id = _get(gateway, "GatewayId", "id")
                if not gateway_id:
                    continue
                result.append(
                    PlantGateway(
                        plant_id=plant_id,
                        plant_name=plant_name,
                        gateway_id=gateway_id,
                        gateway_name=_get(
                            gateway, "Name", "GatewayName", "MacAddress"
                        ),
                    )
                )
        return result

    async def async_provision(
        self,
        *,
        selection: PlantGateway,
        device_name: str,
        id_device: str,
        storage_dir: Path,
    ) -> ProvisionedCredentials:
        """Create/reuse SIP user and provision a matching client certificate."""
        sip = await self._async_get_or_create_sip_user(
            selection=selection,
            device_name=device_name,
            id_device=id_device,
        )
        sip_account = _get(sip, "SipAccount")
        sip_password = _get(sip, "SipPassword")
        returned_id = _get(sip, "IdDevice") or id_device
        if not sip_account or not sip_password:
            raise BticinoCloudError("Incomplete SIP credentials returned by cloud")

        await asyncio.to_thread(storage_dir.mkdir, parents=True, exist_ok=True)
        key_pem, csr = _generate_official_csr(sip_account)
        blob, headers = await self._request_bytes(
            "POST",
            "/eliot/users/cert/signcert",
            {"CommonName": sip_account, "CSR": csr},
        )
        encoded_md5 = headers.get("X-AttachmentMD5") or headers.get(
            "x-attachmentmd5"
        )
        cert_blob = _decode_certificate_response(blob)
        if encoded_md5 and hashlib.md5(cert_blob).hexdigest().lower() != encoded_md5.lower():
            raise BticinoCloudError("Certificate attachment checksum mismatch")

        leaf_pem, chain_pem, not_after = _unpack_certificate(cert_blob, key_pem)
        key_path = storage_dir / "client-key.pem"
        cert_path = storage_dir / "client-cert.pem"
        chain_path = storage_dir / "ca-chain.pem"
        fullchain_path = storage_dir / "client-fullchain.pem"

        await asyncio.to_thread(
            _write_certificate_files,
            key_path, cert_path, fullchain_path, chain_path,
            key_pem, leaf_pem, chain_pem,
        )

        return ProvisionedCredentials(
            plant_id=selection.plant_id,
            plant_name=selection.plant_name,
            gateway_id=selection.gateway_id,
            gateway_name=selection.gateway_name,
            sip_account=sip_account,
            sip_password=sip_password,
            id_device=returned_id,
            device_name=device_name,
            client_cert_path=str(cert_path),
            client_key_path=str(key_path),
            ca_chain_path=str(chain_path) if chain_pem else None,
            certificate_not_after=not_after.isoformat(),
        )

    async def _async_get_or_create_sip_user(
        self,
        *,
        selection: PlantGateway,
        device_name: str,
        id_device: str,
    ) -> dict[str, Any]:
        path = (
            f"/eliot/sip/users/plants/{selection.plant_id}/gateway/"
            f"{selection.gateway_id}"
        )
        users_body, _ = await self._request("GET", path)
        users = _items(users_body)
        local_part = self.email.replace("@", "-")
        expected = (
            f"{local_part}-{id_device}@{selection.gateway_id}.bs.iotleg.com"
        )
        for user in users:
            if _get(user, "SipAccount").lower() == expected.lower():
                return user
            if _get(user, "IdDevice").lower() == id_device.lower():
                return user

        payload = {
            "SipAccount": expected,
            "DeviceName": device_name,
            "GatewayId": selection.gateway_id,
            "IdDevice": id_device,
        }
        created_body, _ = await self._request("POST", "/eliot/sip/user", payload)
        created = _items(created_body)
        refreshed_body, _ = await self._request("GET", path)
        refreshed = _items(refreshed_body)
        for user in refreshed + created:
            if _get(user, "SipAccount").lower() == expected.lower():
                return user
        if created:
            return created[-1]
        raise BticinoCloudError("Cloud did not return the created SIP user")

    async def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        authenticated: bool = True,
    ) -> tuple[Any, dict[str, str]]:
        headers = dict(HEADERS)
        if authenticated:
            if not self.auth_token:
                raise BticinoCloudAuthenticationError("auth_token missing")
            headers["auth_token"] = self.auth_token
        data = json.dumps(payload, separators=(",", ":")) if payload is not None else None
        try:
            async with self._session.request(
                method,
                self.base_url + path,
                headers=headers,
                data=data,
                timeout=ClientTimeout(total=30),
            ) as response:
                raw = await response.text()
                new_token = response.headers.get("auth_token")
                if new_token:
                    self.auth_token = new_token
                try:
                    body: Any = json.loads(raw) if raw else {}
                except ValueError:
                    body = {"_raw": raw}
                is_login = not authenticated and path == "/eliot/users/sign_in"
                if response.status in (401, 403, 498) or (
                    is_login
                    and _looks_like_auth_rejection(response.status, raw, body)
                ):
                    _LOGGER.info(
                        "MyHomeWeb rejected the supplied login credentials (HTTP %s)",
                        response.status,
                    )
                    raise BticinoCloudAuthenticationError(
                        "MyHomeWeb email or password rejected "
                        f"(HTTP {response.status})"
                    )
                if response.status >= 400:
                    _LOGGER.warning(
                        "Unexpected MyHomeWeb response for %s %s: HTTP %s",
                        method,
                        path,
                        response.status,
                    )
                    raise BticinoCloudError(
                        f"{method} {path}: HTTP {response.status}: {raw[:300]}"
                    )
                return body, dict(response.headers)
        except BticinoCloudError:
            raise
        except (ClientResponseError, OSError, TimeoutError) as err:
            raise BticinoCloudConnectionError(str(err)) from err

    async def _request_bytes(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> tuple[bytes, dict[str, str]]:
        headers = dict(HEADERS)
        if not self.auth_token:
            raise BticinoCloudAuthenticationError("auth_token missing")
        headers["auth_token"] = self.auth_token
        data = json.dumps(payload, separators=(",", ":")) if payload is not None else None
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                async with self._session.request(
                    method,
                    self.base_url + path,
                    headers=headers,
                    data=data,
                    timeout=ClientTimeout(total=30),
                ) as response:
                    raw = await response.read()
                    new_token = response.headers.get("auth_token")
                    if new_token:
                        self.auth_token = new_token
                    if response.status in (401, 403, 498):
                        raise BticinoCloudAuthenticationError(
                            f"Cloud authentication rejected ({response.status})"
                        )
                    if response.status >= 400:
                        raise BticinoCloudError(
                            f"{method} {path}: HTTP {response.status}: "
                            f"{raw[:300].decode('utf-8', 'replace')}"
                        )
                    return raw, dict(response.headers)
            except BticinoCloudError:
                raise
            except (
                ServerDisconnectedError,
                ClientConnectionError,
                ClientResponseError,
                OSError,
                TimeoutError,
            ) as err:
                last_error = err
                if attempt < 3:
                    await asyncio.sleep(float(attempt))
                    continue
                break
        raise BticinoCloudConnectionError(
            f"Cloud connection interrupted after 3 attempts: {last_error}"
        ) from last_error


def generate_id_device() -> str:
    """Generate an official-format 12-hex-character device identifier."""
    return secrets.token_hex(6)


def certificate_expiry(path: str | Path) -> datetime | None:
    """Read the expiry date from a PEM client certificate.

    This helper performs blocking file I/O and must be called through
    ``asyncio.to_thread`` from async Home Assistant code.
    """
    try:
        cert = x509.load_pem_x509_certificate(Path(path).read_bytes())
    except (OSError, ValueError):
        return None
    expiry = getattr(cert, "not_valid_after_utc", None)
    if expiry is None:
        expiry = cert.not_valid_after.replace(tzinfo=UTC)
    return expiry


def _parse_payload(body: Any) -> Any:
    value = body.get("payload") if isinstance(body, dict) and "payload" in body else body
    for _ in range(3):
        if isinstance(value, str):
            try:
                value = json.loads(value.strip())
                continue
            except ValueError:
                pass
        break
    return value


def _items(value: Any) -> list[dict[str, Any]]:
    value = _parse_payload(value)
    if isinstance(value, dict):
        for key in ("plants", "Plants", "gateways", "Gateways", "users", "Users", "result", "Result"):
            if isinstance(value.get(key), list):
                value = value[key]
                break
        else:
            return [value]
    if not isinstance(value, list):
        return []
    output: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except ValueError:
                continue
        if isinstance(item, dict):
            output.append(item)
    return output



def _write_certificate_files(
    key_path: Path, cert_path: Path, fullchain_path: Path, chain_path: Path,
    key_pem: bytes, leaf_pem: bytes, chain_pem: bytes | None,
) -> None:
    """Back up and write certificate files outside the event loop."""
    existing = [path for path in (key_path, cert_path, fullchain_path, chain_path) if path.exists()]
    if existing:
        backup_dir = key_path.parent / "backup" / datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        for source in existing:
            shutil.copy2(source, backup_dir / source.name)
    key_path.write_bytes(key_pem)
    key_path.chmod(0o600)
    cert_path.write_bytes(leaf_pem)
    cert_path.chmod(0o600)
    fullchain_path.write_bytes(leaf_pem + (chain_pem or b""))
    fullchain_path.chmod(0o600)
    if chain_pem:
        chain_path.write_bytes(chain_pem)
        chain_path.chmod(0o600)
    elif chain_path.exists():
        chain_path.unlink()

def _get(data: dict[str, Any], *names: str) -> str:
    lowered = {str(key).lower(): value for key, value in data.items()}
    for name in names:
        value = lowered.get(name.lower())
        if value not in (None, ""):
            return str(value)
    return ""


def _generate_official_csr(common_name: str) -> tuple[bytes, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = asn1_x509.Name.build(
        {
            "country_name": "IT",
            "state_or_province_name": "Italy",
            "locality_name": "Varese",
            "organization_name": "Bticino spa",
            "organizational_unit_name": "DSI-PQS",
            "common_name": common_name,
        }
    )
    public_der = key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    request_info = asn1_csr.CertificationRequestInfo(
        {
            "version": "v1",
            "subject": subject,
            "subject_pk_info": asn1_keys.PublicKeyInfo.load(public_der),
            "attributes": [],
        }
    )
    signature = key.sign(request_info.dump(), padding.PKCS1v15(), hashes.SHA256())
    request = asn1_csr.CertificationRequest(
        {
            "certification_request_info": request_info,
            "signature_algorithm": asn1_algos.SignedDigestAlgorithm(
                {"algorithm": "sha256_rsa"}
            ),
            "signature": signature,
        }
    )
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    csr_pem = asn1_pem.armor("CERTIFICATE REQUEST", request.dump()).decode("ascii")
    return key_pem, csr_pem.replace("\n", " ")


def _decode_certificate_response(blob: bytes) -> bytes:
    stripped = blob.strip()
    if stripped.startswith(b"PK\x03\x04") or stripped.startswith(b"0\x82") or b"BEGIN CERTIFICATE" in stripped:
        return blob
    try:
        decoded = base64.b64decode(stripped, validate=True)
        return decoded or blob
    except ValueError:
        return blob


def _load_certificates(data: bytes) -> list[x509.Certificate]:
    certs: list[x509.Certificate] = []
    text_data = data.strip()
    for block in re.findall(
        br"-----BEGIN CERTIFICATE-----\s+.*?-----END CERTIFICATE-----",
        text_data,
        flags=re.S,
    ):
        try:
            certs.append(x509.load_pem_x509_certificate(block + b"\n"))
        except ValueError:
            pass
    if certs:
        return certs
    try:
        # DER is arbitrary binary data: stripping ASCII whitespace bytes can
        # corrupt a valid certificate whose encoded value ends with one of
        # those byte values.
        return [x509.load_der_x509_certificate(data)]
    except ValueError:
        pass
    for loader, payload in (
        (pkcs7.load_der_pkcs7_certificates, data),
        (pkcs7.load_pem_pkcs7_certificates, text_data),
    ):
        try:
            loaded = loader(payload)
            if loaded:
                return list(loaded)
        except ValueError:
            pass
    return []


def _public_key_fingerprint_from_key(key_pem: bytes) -> str:
    key = serialization.load_pem_private_key(key_pem, password=None)
    der = key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def _public_key_fingerprint_from_cert(cert: x509.Certificate) -> str:
    der = cert.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def _unpack_certificate(
    blob: bytes, key_pem: bytes
) -> tuple[bytes, bytes | None, datetime]:
    certs: list[x509.Certificate] = []
    if blob.startswith(b"PK\x03\x04"):
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            for name in archive.namelist():
                if not name.endswith("/"):
                    certs.extend(_load_certificates(archive.read(name)))
    else:
        certs.extend(_load_certificates(blob))
    if not certs:
        raise BticinoCloudError("No X.509 certificate found in signcert response")

    key_fp = _public_key_fingerprint_from_key(key_pem)
    leaf = next(
        (cert for cert in certs if _public_key_fingerprint_from_cert(cert) == key_fp),
        None,
    )
    if leaf is None:
        raise BticinoCloudError("Certificate does not match generated private key")

    # BTicino issues a valid certificate whose Common Name is 66 characters.
    # cryptography warns while lazily decoding subject/issuer Name attributes,
    # although the certificate has already been issued and is usable. Restrict
    # suppression to that exact upstream warning while ordering the chain.
    chain: list[x509.Certificate] = []
    current = leaf
    seen_serials: set[int] = set()
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"Attribute's length must be >= 1 and <= 64, but it was 66",
            category=UserWarning,
        )
        while current.issuer != current.subject:
            current_issuer = current.issuer
            parent = next(
                (candidate for candidate in certs if candidate.subject == current_issuer),
                None,
            )
            if parent is None or parent.serial_number in seen_serials:
                break
            seen_serials.add(parent.serial_number)
            if parent.issuer == parent.subject:
                break
            chain.append(parent)
            current = parent

    expiry = getattr(leaf, "not_valid_after_utc", None)
    if expiry is None:
        expiry = leaf.not_valid_after.replace(tzinfo=UTC)
    leaf_pem = leaf.public_bytes(serialization.Encoding.PEM)
    chain_pem = b"".join(
        cert.public_bytes(serialization.Encoding.PEM) for cert in chain
    )
    return leaf_pem, chain_pem or None, expiry
