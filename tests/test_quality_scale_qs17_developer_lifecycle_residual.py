"""QS-17 behavioural coverage for residual developer and lifecycle helpers."""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from test_quality_scale_qs6_developer_lifecycle import _load_developer, _tools


@pytest.fixture(autouse=True)
def _restore_module_state():
    tracked = {
        name: module
        for name, module in sys.modules.items()
        if name == "custom_components"
        or name.startswith("custom_components.btdoor_security_plus")
        or name.startswith("homeassistant")
    }
    yield
    for name in list(sys.modules):
        if (
            name == "custom_components"
            or name.startswith("custom_components.btdoor_security_plus")
            or name.startswith("homeassistant")
        ):
            sys.modules.pop(name, None)
    sys.modules.update(tracked)


def _certificate(tmp_path: Path) -> tuple[Path, Path]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "BTDoor Test")])
    now = datetime.now(UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=30))
        .sign(key, hashes.SHA256())
    )
    cert_path = tmp_path / "client-cert.pem"
    key_path = tmp_path / "client-key.pem"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    return cert_path, key_path


def test_developer_cloud_sip_tls_and_certificate_residual(tmp_path, monkeypatch):
    module = _load_developer(tmp_path)
    tools, client = _tools(module, tmp_path)

    class Cloud:
        def __init__(self, session, *, email, password):
            assert session == "session" and email == "a" and password == "b"

        async def async_login(self):
            return None

        async def async_list_gateways(self):
            return [SimpleNamespace(gateway_id="gw"), SimpleNamespace(gateway_id="other")]

    monkeypatch.setattr(module, "BticinoCloudClient", Cloud)
    assert asyncio.run(tools._test_cloud()) == {
        "authenticated": True,
        "gateway_count": 2,
        "configured_gateway_found": True,
    }

    client.async_test_connection = lambda: asyncio.sleep(
        0, result=SimpleNamespace(status="ok", code=200)
    )
    sip = asyncio.run(tools._test_sip())
    assert sip["status"] == "ok" and sip["server"] == "sip.example"

    class SSLObject:
        def version(self):
            return "TLSv1.3"

        def cipher(self):
            return ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)

    class Writer:
        def __init__(self):
            self.closed = False

        def get_extra_info(self, name):
            return SSLObject() if name == "ssl_object" else ("sip.example", 5061)

        def close(self):
            self.closed = True

        async def wait_closed(self):
            return None

    writer = Writer()
    client._async_connect = lambda: asyncio.sleep(0, result=(object(), writer))
    tls = asyncio.run(tools._test_tls())
    assert tls["tls_version"] == "TLSv1.3" and writer.closed

    cert_path, key_path = _certificate(tmp_path)
    client.client_cert_path = str(cert_path)
    client.client_key_path = str(key_path)
    info = asyncio.run(tools._test_certificates())
    assert info["certificate_exists"] and "redacted:" in info["subject"]
    assert "commonName=BTDoor Test" in info["issuer"]

    with pytest.raises(FileNotFoundError, match="certificate"):
        tools._certificate_info(tmp_path / "missing.pem", key_path)
    with pytest.raises(FileNotFoundError, match="private key"):
        tools._certificate_info(cert_path, tmp_path / "missing-key.pem")


def test_developer_all_runner_and_entry_path_fallback(tmp_path, monkeypatch):
    module = _load_developer(tmp_path)
    tools, client = _tools(module, tmp_path)
    client.client_cert_path = ""
    client.client_key_path = ""
    tools.entry.data.update(
        {"client_cert_path": "~/entry-cert.pem", "client_key_path": "~/entry-key.pem"}
    )
    cert_path, key_path = tools._runtime_certificate_paths()
    assert cert_path.name == "entry-cert.pem" and key_path.name == "entry-key.pem"

    names = ("cloud", "certificates", "sip", "tls", "sdp", "media", "dialog", "health")
    for name in names:
        monkeypatch.setattr(
            tools, f"_test_{name}", lambda name=name: asyncio.sleep(0, result={"name": name})
        )
    result = asyncio.run(tools.async_run_tests("all"))
    assert list(result) == list(names)
    assert all(item["ok"] for item in result.values())
    assert tools.runtime.last_developer_test_result == "ok"
