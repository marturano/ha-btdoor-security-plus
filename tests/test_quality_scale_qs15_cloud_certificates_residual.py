"""QS-15 behavioural coverage for cloud certificate provisioning and residual modules."""

from __future__ import annotations

import asyncio
import base64
import importlib
import importlib.util
import io
import json
import sys
import types
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "custom_components" / "btdoor_security_plus"


def _reset_package() -> None:
    for name in list(sys.modules):
        if name.startswith("custom_components.btdoor_security_plus"):
            sys.modules.pop(name, None)
    root = types.ModuleType("custom_components")
    root.__path__ = [str(ROOT / "custom_components")]
    sys.modules[root.__name__] = root
    package = types.ModuleType("custom_components.btdoor_security_plus")
    package.__path__ = [str(PKG)]
    sys.modules[package.__name__] = package


def _load(name: str):
    full = f"custom_components.btdoor_security_plus.{name}"
    path = PKG.joinpath(*name.split("."))
    path = path / "__init__.py" if path.is_dir() else path.with_suffix(".py")
    spec = importlib.util.spec_from_file_location(
        full,
        path,
        submodule_search_locations=[str(path.parent)] if path.name == "__init__.py" else None,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[full] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def cloud():
    previous = {
        n: m
        for n, m in sys.modules.items()
        if n.startswith("custom_components.btdoor_security_plus")
    }
    _reset_package()
    module = _load("cloud")
    try:
        yield module
    finally:
        for name in list(sys.modules):
            if name.startswith("custom_components.btdoor_security_plus"):
                sys.modules.pop(name, None)
        sys.modules.update(previous)


def _cert(key, subject_cn: str, issuer_cert=None, issuer_key=None, *, ca=False):
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)])
    issuer = issuer_cert.subject if issuer_cert else subject
    signer = issuer_key or key
    now = datetime.now(UTC)
    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
        .sign(signer, hashes.SHA256())
    )


def test_cloud_payload_files_and_csr_helpers(cloud, tmp_path):
    assert cloud._parse_payload({"payload": json.dumps(json.dumps({"x": 1}))}) == {"x": 1}
    assert cloud._parse_payload("not-json") == "not-json"
    assert cloud._items({"Plants": [{"id": 1}]}) == [{"id": 1}]
    assert cloud._items([json.dumps({"id": 2}), "bad", 3]) == [{"id": 2}]
    assert cloud._items(4) == []
    assert cloud._get({"SipAccount": "a"}, "sipaccount") == "a"
    assert cloud._get({"x": ""}, "x") == ""

    key_pem, csr = cloud._generate_official_csr("user@example.com")
    assert b"BEGIN PRIVATE KEY" in key_pem
    assert "BEGIN CERTIFICATE REQUEST" in csr and "\n" not in csr
    assert len(cloud.generate_id_device()) == 12

    key = tmp_path / "client-key.pem"
    cert = tmp_path / "client-cert.pem"
    full = tmp_path / "client-fullchain.pem"
    chain = tmp_path / "ca-chain.pem"
    for p in (key, cert, full, chain):
        p.write_bytes(b"old")
    cloud._write_certificate_files(key, cert, full, chain, b"key", b"leaf", None)
    assert key.read_bytes() == b"key" and cert.read_bytes() == b"leaf"
    assert not chain.exists()
    backups = list((tmp_path / "backup").glob("*/*"))
    assert backups

    cloud._write_certificate_files(key, cert, full, chain, b"key2", b"leaf2", b"chain2")
    assert full.read_bytes() == b"leaf2chain2" and chain.read_bytes() == b"chain2"


def test_cloud_certificate_decoding_loading_and_unpacking(cloud, tmp_path):
    root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    root = _cert(root_key, "Root", ca=True)
    inter_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    inter = _cert(inter_key, "Intermediate", root, root_key, ca=True)
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    leaf = _cert(leaf_key, "Leaf", inter, inter_key)
    leaf_key_pem = leaf_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    pem_blob = (
        b"junk\n"
        + leaf.public_bytes(serialization.Encoding.PEM)
        + inter.public_bytes(serialization.Encoding.PEM)
        + root.public_bytes(serialization.Encoding.PEM)
    )

    assert cloud._decode_certificate_response(base64.b64encode(pem_blob)) == pem_blob
    assert cloud._decode_certificate_response(pem_blob) == pem_blob
    assert cloud._decode_certificate_response(b"%%%") == b"%%%"
    assert len(cloud._load_certificates(pem_blob)) == 3
    assert len(cloud._load_certificates(leaf.public_bytes(serialization.Encoding.DER))) == 1
    assert cloud._load_certificates(b"invalid") == []

    leaf_pem, chain_pem, expiry = cloud._unpack_certificate(pem_blob, leaf_key_pem)
    assert b"BEGIN CERTIFICATE" in leaf_pem
    assert chain_pem and b"Intermediate" not in chain_pem  # PEM is encoded, but chain exists.
    assert expiry.tzinfo is not None

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr("certs.pem", pem_blob)
        archive.writestr("folder/", b"")
    assert cloud._unpack_certificate(buf.getvalue(), leaf_key_pem)[0] == leaf_pem

    wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    with pytest.raises(cloud.BticinoCloudError, match="does not match"):
        cloud._unpack_certificate(pem_blob, wrong_key)
    with pytest.raises(cloud.BticinoCloudError, match="No X.509"):
        cloud._unpack_certificate(b"bad", leaf_key_pem)

    cert_path = tmp_path / "cert.pem"
    cert_path.write_bytes(leaf_pem)
    assert cloud.certificate_expiry(cert_path) is not None
    assert cloud.certificate_expiry(tmp_path / "missing.pem") is None


@pytest.mark.asyncio
async def test_cloud_provision_success_and_failures(cloud, tmp_path, monkeypatch):
    selection = cloud.PlantGateway("p", "Plant", "g", "Gate")
    client = cloud.BticinoCloudClient(SimpleNamespace(), email="a@b.c", password="p")
    client._async_get_or_create_sip_user = AsyncMock(
        return_value={"SipAccount": "sip:a", "SipPassword": "pw", "IdDevice": "id2"}
    )
    client._request_bytes = AsyncMock(return_value=(b"blob", {}))
    monkeypatch.setattr(cloud, "_generate_official_csr", lambda cn: (b"key", "csr"))
    monkeypatch.setattr(cloud, "_decode_certificate_response", lambda blob: b"decoded")
    expiry = datetime.now(UTC) + timedelta(days=30)
    monkeypatch.setattr(cloud, "_unpack_certificate", lambda blob, key: (b"leaf", b"chain", expiry))
    monkeypatch.setattr(
        cloud,
        "_write_certificate_files",
        lambda *args: [
            p.write_bytes(data)
            for p, data in (
                (args[0], args[4]),
                (args[1], args[5]),
                (args[2], args[5] + args[6]),
                (args[3], args[6]),
            )
        ],
    )
    result = await client.async_provision(
        selection=selection, device_name="HA", id_device="id", storage_dir=tmp_path / "certs"
    )
    assert result.sip_account == "sip:a" and result.id_device == "id2"
    assert result.ca_chain_path and await asyncio.to_thread(Path(result.client_cert_path).exists)

    client._async_get_or_create_sip_user = AsyncMock(return_value={})
    with pytest.raises(cloud.BticinoCloudError, match="Incomplete"):
        await client.async_provision(
            selection=selection, device_name="HA", id_device="id", storage_dir=tmp_path / "bad"
        )

    client._async_get_or_create_sip_user = AsyncMock(
        return_value={"SipAccount": "sip:a", "SipPassword": "pw"}
    )
    client._request_bytes = AsyncMock(return_value=(b"blob", {"X-AttachmentMD5": "bad"}))
    with pytest.raises(cloud.BticinoCloudError, match="checksum"):
        await client.async_provision(
            selection=selection, device_name="HA", id_device="id", storage_dir=tmp_path / "bad2"
        )


@pytest.mark.asyncio
async def test_cloud_user_creation_residual_paths(cloud):
    selection = cloud.PlantGateway("p", "Plant", "g", "Gate")
    client = cloud.BticinoCloudClient(SimpleNamespace(), email="A@B.C", password="p")
    client._request = AsyncMock(
        side_effect=[({"users": [{"IdDevice": "ID", "SipAccount": "other"}]}, {})]
    )
    assert (
        await client._async_get_or_create_sip_user(
            selection=selection, device_name="HA", id_device="id"
        )
    )["IdDevice"] == "ID"

    client._request = AsyncMock(side_effect=[([], {}), ([{"SipAccount": "created"}], {}), ([], {})])
    assert (
        await client._async_get_or_create_sip_user(
            selection=selection, device_name="HA", id_device="id"
        )
    )["SipAccount"] == "created"

    client._request = AsyncMock(side_effect=[([], {}), ([], {}), ([], {})])
    with pytest.raises(cloud.BticinoCloudError, match="did not return"):
        await client._async_get_or_create_sip_user(
            selection=selection, device_name="HA", id_device="id"
        )


def test_der_certificate_loader_preserves_binary_payload(cloud, monkeypatch):
    payload = b"\x30\x82binary-der-ending-with-whitespace-byte\x0d"
    sentinel = object()
    seen = []

    def fake_der_loader(value):
        seen.append(value)
        return sentinel

    monkeypatch.setattr(cloud.x509, "load_der_x509_certificate", fake_der_loader)
    assert cloud._load_certificates(payload) == [sentinel]
    assert seen == [payload]
