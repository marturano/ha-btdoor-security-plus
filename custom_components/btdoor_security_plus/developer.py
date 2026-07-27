"""Developer and support tooling for BTDoor Security+."""
from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import json
from pathlib import Path
import platform
import shutil
import ssl
import sys
from typing import Any
import zipfile
import warnings

from cryptography import x509
from cryptography.hazmat.primitives import hashes

from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import entity_registry as er

from .cloud import BticinoCloudClient
from .const import (
    CONF_CLIENT_CERT_PATH, CONF_CLIENT_KEY_PATH, CONF_EMAIL, CONF_GATEWAY_ID,
    CONF_PASSWORD, CONF_SERVER, CONF_VERIFY_SERVER, DOMAIN, SUPPORT_REPORT_RETENTION,
)
from .support_debug import redact, redact_text, redact_support_text
from .diagnostic_framework import DiagnosticEngine, HealthEngine
from .diagnostic_framework.bundle import BundleLayoutBuilder
from .diagnostic_framework.providers import StaticResultProvider
from .support_naming import (
    build_support_artifact_names,
    is_managed_support_artifact,
)
from .visibility import visibility_for_entry
from .support_models import (
    SupportSnapshot,
    build_timeline_summary,
    json_dumps,
    sanitize_jsonl,
    sanitize_support_data,
    structure_dialog_headers,
)





def _safe_x509_name(name, *, redact: bool) -> str:
    """Format an X.509 name without RFC4514 length validation warnings."""
    parts: list[str] = []
    for attribute in name:
        label = attribute.oid._name or attribute.oid.dotted_string
        value = str(attribute.value)
        if redact:
            value = redact_text(value)
        parts.append(f"{label}={value}")
    return ", ".join(parts)


class DeveloperModeDisabledError(RuntimeError):
    """Raised when a developer action is requested while disabled."""


class DeveloperTools:
    """Safe developer diagnostics and support report generator."""

    def __init__(self, hass: HomeAssistant, entry, runtime, enabled: bool) -> None:
        self.hass = hass
        self.entry = entry
        self.runtime = runtime
        self.enabled = enabled
        self.output_dir = Path(hass.config.path("custom_components", DOMAIN, "support", entry.entry_id))

    def require_enabled(self) -> None:
        if not self.enabled:
            raise DeveloperModeDisabledError(
                "Developer mode is disabled. Enable it in the integration options first."
            )

    async def async_run_tests(self, test: str = "all") -> dict[str, Any]:
        self.require_enabled()
        tests = {
            "cloud": self._test_cloud,
            "certificates": self._test_certificates,
            "sip": self._test_sip,
            "tls": self._test_tls,
            "sdp": self._test_sdp,
            "media": self._test_media,
            "dialog": self._test_dialog,
            "health": self._test_health,
        }
        selected = list(tests) if test == "all" else [test]
        results: dict[str, Any] = {}
        for name in selected:
            fn = tests.get(name)
            if fn is None:
                results[name] = {"ok": False, "error": "Unknown developer test"}
                continue
            started = asyncio.get_running_loop().time()
            try:
                payload = await fn()
                results[name] = {"ok": True, "duration_ms": round((asyncio.get_running_loop().time()-started)*1000, 1), **payload}
            except Exception as err:  # diagnostic tool must aggregate failures
                results[name] = {"ok": False, "duration_ms": round((asyncio.get_running_loop().time()-started)*1000, 1), "error": redact_text(str(err))}
        clean_results = redact(results)
        self.runtime.last_developer_test_at = datetime.now(UTC)
        failed = [name for name, result in clean_results.items() if not result.get("ok")]
        self.runtime.last_developer_test_result = "ok" if not failed else f"failed: {', '.join(failed)}"
        self.runtime.debug.record("developer", "tests_completed", selected=selected, results=clean_results)
        return clean_results

    async def _test_cloud(self) -> dict[str, Any]:
        data=self.entry.data
        client=BticinoCloudClient(async_get_clientsession(self.hass), email=str(data[CONF_EMAIL]), password=str(data[CONF_PASSWORD]))
        await client.async_login()
        gateways=await client.async_list_gateways()
        return {"authenticated": True, "gateway_count": len(gateways), "configured_gateway_found": any(g.gateway_id==str(data[CONF_GATEWAY_ID]) for g in gateways)}

    async def _test_sip(self) -> dict[str, Any]:
        result=await self.runtime.client.async_test_connection()
        return {"status": result.status, "code": result.code, "server": self.runtime.client.server, "port": self.runtime.client.port}

    async def _test_tls(self) -> dict[str, Any]:
        client=self.runtime.client
        reader, writer=await client._async_connect()  # intentionally uses the same production TLS path
        try:
            ssl_obj=writer.get_extra_info("ssl_object")
            return {"connected": True, "tls_version": ssl_obj.version() if ssl_obj else None, "cipher": ssl_obj.cipher() if ssl_obj else None, "peername": writer.get_extra_info("peername"), "verify_server": client.verify_server}
        finally:
            writer.close(); await writer.wait_closed()

    async def _test_certificates(self) -> dict[str, Any]:
        """Inspect the exact certificate paths currently used by the SIP runtime."""
        cert_path, key_path = self._runtime_certificate_paths()
        return await asyncio.to_thread(self._certificate_info, cert_path, key_path)

    def _runtime_certificate_paths(self) -> tuple[Path, Path]:
        """Return certificate paths from the live SIP client, with entry fallback.

        Using the runtime paths keeps diagnostics aligned with the production TLS
        connection after config-entry migrations or certificate renewal.
        """
        client = self.runtime.client
        cert_value = getattr(client, "client_cert_path", None) or self.entry.data.get(
            CONF_CLIENT_CERT_PATH, ""
        )
        key_value = getattr(client, "client_key_path", None) or self.entry.data.get(
            CONF_CLIENT_KEY_PATH, ""
        )
        return Path(str(cert_value)).expanduser(), Path(str(key_value)).expanduser()

    async def _certificate_status(self) -> dict[str, Any]:
        """Return a non-raising certificate status for aggregate health checks."""
        cert_path, key_path = self._runtime_certificate_paths()
        cert_exists, key_exists = await asyncio.to_thread(
            lambda: (cert_path.is_file(), key_path.is_file())
        )
        return {
            "certificate_exists": cert_exists,
            "private_key_exists": key_exists,
            "certificate_path": "configured" if cert_path else "missing",
            "private_key_path": "configured" if key_path else "missing",
        }

    @staticmethod
    def _certificate_info(cert_path: Path, key_path: Path) -> dict[str, Any]:
        if not cert_path.is_file(): raise FileNotFoundError(f"Client certificate not found: {cert_path}")
        if not key_path.is_file(): raise FileNotFoundError(f"Client private key not found: {key_path}")
        cert=x509.load_pem_x509_certificate(cert_path.read_bytes())
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"Attribute's length must be >= 1 and <= 64, but it was 66",
                category=UserWarning,
            )
            subject = cert.subject
            issuer = cert.issuer

        return {
            "certificate_exists": True,
            "private_key_exists": True,
            "not_before": cert.not_valid_before_utc.isoformat(),
            "not_after": cert.not_valid_after_utc.isoformat(),
            "serial": hex(cert.serial_number),
            "sha256": cert.fingerprint(hashes.SHA256()).hex()[:16],
            "subject": _safe_x509_name(subject, redact=True),
            "issuer": _safe_x509_name(issuer, redact=False),
        }

    async def _test_sdp(self) -> dict[str, Any]:
        c=self.runtime.client
        return {
            "available": bool(c.last_sdp_offer),
            "summary": c.last_sdp_summary,
            "session_address": c.sdp_session_address,
            "audio": {
                "address": c.sdp_audio_address,
                "port": c.sdp_audio_port,
                "protocol": c.sdp_audio_protocol,
                "direction": c.sdp_audio_direction,
                "payload_types": list(c.sdp_audio_payload_types),
                "codecs": list(c.sdp_audio_codecs),
                "fmtp": dict(c.sdp_audio_fmtp),
            },
            "video": {
                "address": c.sdp_video_address,
                "port": c.sdp_video_port,
                "protocol": c.sdp_video_protocol,
                "direction": c.sdp_video_direction,
                "payload_types": list(c.sdp_video_payload_types),
                "codecs": list(c.sdp_video_codecs),
                "fmtp": dict(c.sdp_video_fmtp),
            },
            "raw_sdp": redact_text(c.last_sdp_offer or ""),
        }

    async def _test_media(self) -> dict[str, Any]:
        """Return the current or last prepared media runtime."""
        c = self.runtime.client
        runtime = c.media_runtime
        return {
            "available": bool(c.media_plan or c.last_completed_media_session),
            "runtime": runtime,
            "last_completed": c.last_completed_media_session,
            "history": list(c.media_session_history),
            "metrics": c.media_session_metrics,
            "instrumentation": c.media_instrumentation,
            "sip_dispatcher": c.sip_dispatcher_diagnostics,
            "remote_sdp_available": bool(c.last_media_remote_sdp),
            "local_sdp_available": bool(c.last_media_local_sdp),
            "sdp_diff_available": bool(c.last_media_sdp_diff),
        }

    async def _test_dialog(self) -> dict[str, Any]:
        c = self.runtime.client
        s = c._session
        return {
            "registered": c.registered,
            "dialog_state": c.dialog_state,
            "last_method": c.last_sip_method,
            "call_id": c.last_call_id,
            "ringing": c.ringing,
            "identity_uri": redact_text(s.identity_uri) if s else None,
            "contact_uri": redact_text(s.contact_uri) if s else None,
            "proxy_uri": s.proxy_uri if s else None,
            "digest_cached": c._message_challenge is not None,
            "dialog_headers": structure_dialog_headers(c.last_dialog_headers),
            "timeline_current_session": redact(c.current_session_timeline),
            "timeline_historical": redact(list(c.sip_timeline)),
            "session_id": c.runtime_session_id,
            "session_started_at": c.runtime_session_started_at.isoformat(),
        }

    async def _test_health(self) -> dict[str, Any]:
        """Run a non-invasive health assessment without cascading failures."""
        c = self.runtime.client
        cert = await self._certificate_status()
        session_open = bool(
            c._session is not None and not c._session.writer.is_closing()
        )
        tls_runtime = session_open and bool(c.registered)
        checks = {
            "runtime": True,
            "certificates": bool(
                cert.get("certificate_exists") and cert.get("private_key_exists")
            ),
            "sip_registered": bool(c.registered),
            "tls_runtime": tls_runtime,
            "storage_support_writable": await asyncio.to_thread(
                self._directory_writable, self.output_dir
            ),
            "debug_dropped_records_zero": not bool(
                self.runtime.debug and self.runtime.debug.dropped_records
            ),
            "media_runtime_observable": bool(
                c.media_plan or c.last_completed_media_session
            ) if c.last_sdp_offer else True,
        }
        weights = {
            "runtime": 15,
            "certificates": 15,
            "sip_registered": 25,
            "tls_runtime": 20,
            "storage_support_writable": 10,
            "debug_dropped_records_zero": 5,
            "media_runtime_observable": 10,
        }
        score = sum(weights[name] for name, ok in checks.items() if ok)
        issues = [name for name, ok in checks.items() if not ok]
        return {
            "score": score,
            "status": "healthy"
            if score >= 95
            else "degraded"
            if score >= 70
            else "unhealthy",
            "checks": checks,
            "issues": issues,
            "certificate_status": cert,
            "note": (
                "Health checks are independent; a certificate-file failure no longer "
                "marks TLS as failed when the live SIP/TLS session is established."
            ),
        }

    @staticmethod
    def _directory_writable(path: Path) -> bool:
        try:
            path.mkdir(parents=True, exist_ok=True)
            probe = path / ".write-test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return True
        except OSError:
            return False

    async def async_generate_support_report(self, include_logs: bool = True) -> dict[str, Any]:
        self.require_enabled()
        await asyncio.to_thread(self.output_dir.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(self._enforce_report_retention)
        generated_at = datetime.now(UTC)
        artifact_names = build_support_artifact_names(generated_at)
        tests = await self.async_run_tests("all")
        integration = await async_get_integration(self.hass, DOMAIN)
        system_info = await asyncio.to_thread(self._system_info)
        snapshot = self._snapshot(tests, integration.version, system_info)
        provider_results, framework_health = await self._async_framework_diagnostics(tests)
        snapshot["diagnostic_framework"] = {
            "schema_version": 3,
            "health": framework_health,
            "providers": {name: result.as_dict() for name, result in provider_results.items()},
        }
        md=self._markdown(snapshot)
        report = self.output_dir / artifact_names.report_name
        bundle = self.output_dir / artifact_names.bundle_name
        await asyncio.to_thread(report.write_text, md, encoding='utf-8')
        from .device_model.manager import device_registry_report, device_translation_report
        from .managers.device_manager import DeviceManager
        registry_report = device_registry_report(self.hass, self.entry)
        registry_report["topology_validation"] = (
            DeviceManager(self.hass, self.entry).validate_topology().as_dict()
        )
        translation_report = device_translation_report(self.entry)
        entity_registry_report = self._entity_registry_report()
        await asyncio.to_thread(
            self._write_bundle, bundle, report, snapshot, include_logs,
            registry_report, translation_report, entity_registry_report,
        )
        self.runtime.last_support_report_at = datetime.now(UTC)
        self.runtime.last_support_report_path = str(report)
        self.runtime.last_support_bundle_path = str(bundle)
        self.runtime.debug.record("developer", "support_report_generated", report=str(report), bundle=str(bundle))
        if self.runtime.event_bus is not None:
            from .event_bus import RuntimeEvent, RuntimeEventType, RuntimeSource
            self.runtime.event_bus.publish(
                RuntimeEvent(
                    event_type=RuntimeEventType.SUPPORT_BUNDLE_CREATED,
                    source=RuntimeSource.DIAGNOSTICS,
                    payload={"generated_at": snapshot["generated_at"]},
                )
            )
        return {"report_path": str(report), "bundle_path": str(bundle), "generated_at": snapshot["generated_at"]}

    async def async_clean_debug_environment(self) -> dict[str, Any]:
        """Remove debug logs and generated reports without touching certificates."""
        self.require_enabled()
        if self.runtime.debug is not None:
            await self.runtime.debug.async_clear()
        removed = await asyncio.to_thread(self._clear_support_files)
        self.runtime.last_support_report_at = None
        self.runtime.last_support_report_path = None
        self.runtime.last_support_bundle_path = None
        return {"removed_files": removed, "support_dir": str(self.output_dir)}

    def _clear_support_files(self) -> int:
        removed = 0
        if self.output_dir.exists():
            for candidate in self.output_dir.iterdir():
                if candidate.is_file():
                    candidate.unlink(missing_ok=True)
                    removed += 1
                elif candidate.is_dir():
                    shutil.rmtree(candidate, ignore_errors=True)
                    removed += 1
        return removed

    def _enforce_report_retention(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        reports = sorted(
            [p for p in self.output_dir.iterdir() if is_managed_support_artifact(p)],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        # Keep at most SUPPORT_REPORT_RETENTION report sets (Markdown + ZIP).
        stems: list[str] = []
        for report in reports:
            stem = report.stem
            if stem not in stems:
                stems.append(stem)
        for stem in stems[SUPPORT_REPORT_RETENTION:]:
            for candidate in self.output_dir.glob(stem + ".*"):
                candidate.unlink(missing_ok=True)

    @staticmethod
    def _system_info() -> dict[str, str]:
        """Collect system details outside the Home Assistant event loop.

        ``platform.platform()`` may open the Python executable on Python 3.14,
        so callers must execute this helper in an executor thread.
        """
        return {
            "python": sys.version,
            "platform": platform.platform(),
        }

    def _snapshot(
        self,
        tests: dict[str, Any],
        integration_version: str | None,
        system_info: dict[str, str],
    ) -> SupportSnapshot:
        c = self.runtime.client
        return redact({
            "generated_at": datetime.now(UTC).isoformat(),
            "integration": {"name": "BTDoor Security+", "version": integration_version or "unknown", "domain": DOMAIN, "developer_mode": self.enabled},
            "system": {
                **system_info,
                "home_assistant_config_dir": str(self.hass.config.config_dir),
            },
            "entry": dict(self.entry.data),
            "options": dict(self.entry.options),
            "runtime": {
                "registered": c.registered, "last_status": c.last_status, "last_error": c.last_error,
                "reconnect_count": c.reconnect_count, "dialog_state": c.dialog_state,
                "last_sip_method": c.last_sip_method, "last_command_duration": c.last_command_duration,
                "call_state": c.call_state, "last_sdp_summary": c.last_sdp_summary,
                "connected_at": c.connected_at, "last_keepalive_at": c.last_keepalive_at,
                "runtime_session_id": c.runtime_session_id,
                "runtime_session_started_at": c.runtime_session_started_at,
                "timeline_current_session": c.current_session_timeline,
                "timeline_historical": list(c.sip_timeline),
                "debug_dropped_records": self.runtime.debug.dropped_records if self.runtime.debug else 0,
                "media_runtime": c.media_runtime,
                "media_last_completed": c.last_completed_media_session,
                "media_session_history": list(c.media_session_history),
                "media_session_metrics": c.media_session_metrics,
                "runtime_events": (
                    self.runtime.event_bus.history if self.runtime.event_bus else []
                ),
                "runtime_event_metrics": (
                    self.runtime.event_bus.metrics if self.runtime.event_bus else {}
                ),
                "call_journal": (
                    self.runtime.call_journal.records if self.runtime.call_journal else []
                ),
                "call_journal_metrics": (
                    self.runtime.call_journal.metrics if self.runtime.call_journal else {}
                ),
            },
            "health": tests.get("health", {}),
            "tests": tests,
            "recent_debug": self.runtime.debug.recent() if self.runtime.debug else [],
        })

    @staticmethod
    def _timeline_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate a compact call and classified SIP-event summary."""
        return build_timeline_summary(events)

    async def _async_framework_diagnostics(
        self, tests: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Normalize collected tests through the modular provider framework."""
        weights = {
            "cloud": 15,
            "certificates": 10,
            "sip": 20,
            "tls": 15,
            "sdp": 5,
            "media": 10,
            "dialog": 15,
            "health": 10,
        }
        providers = [
            StaticResultProvider(name, weights.get(name, 5), result)
            for name, result in tests.items()
        ]
        results = await DiagnosticEngine(providers).async_collect()
        health = HealthEngine.aggregate(results)
        return results, health

    def _support_summary(self, snapshot: SupportSnapshot) -> dict[str, Any]:
        """Build the small, AI-friendly entry point for a support bundle."""
        runtime = snapshot.get("runtime", {})
        framework = snapshot.get("diagnostic_framework", {})
        health = framework.get("health") or snapshot.get("health", {})
        media = runtime.get("media_runtime") or {}
        return sanitize_support_data({
            "schema_version": 3,
            "project": "BTDoor Security+",
            "domain": DOMAIN,
            "version": snapshot.get("integration", {}).get("version", "unknown"),
            "generated_at": snapshot.get("generated_at"),
            "healthy": health.get("status") == "healthy",
            "score": health.get("score"),
            "health_status": health.get("status"),
            "cloud": "ok" if snapshot.get("tests", {}).get("cloud", {}).get("ok") else "error",
            "certificates": "ok" if snapshot.get("tests", {}).get("certificates", {}).get("ok") else "error",
            "sip": "registered" if runtime.get("registered") else "not_registered",
            "dialog": runtime.get("dialog_state"),
            "media": media.get("state") or ("available" if media else "unavailable"),
            "last_media_close_reason": (
                (runtime.get("media_last_completed") or {}).get("closed_reason")
                if isinstance(runtime.get("media_last_completed"), dict)
                else None
            ),
            "tls": "ok" if snapshot.get("tests", {}).get("tls", {}).get("ok") else "error",
            "last_error": runtime.get("last_error"),
            "last_sip_method": runtime.get("last_sip_method"),
            "call_state": runtime.get("call_state"),
            "debug_dropped_records": runtime.get("debug_dropped_records", 0),
        })


    def _entity_registry_report(self) -> dict[str, Any]:
        """Return a sanitized registry snapshot for this config entry."""
        registry = er.async_get(self.hass)
        entities = []
        for entity in er.async_entries_for_config_entry(registry, self.entry.entry_id):
            state = self.hass.states.get(entity.entity_id)
            entities.append({
                "entity_id": entity.entity_id,
                "unique_id": entity.unique_id,
                "platform": entity.platform,
                "domain": entity.domain,
                "device_id": entity.device_id,
                "disabled_by": None if entity.disabled_by is None else str(entity.disabled_by),
                "hidden_by": None if entity.hidden_by is None else str(entity.hidden_by),
                "original_name": entity.original_name,
                "translation_key": getattr(entity, "translation_key", None),
                "available": state is not None and state.state != "unavailable",
                "state": None if state is None else state.state,
            })
        return {
            "schema_version": 1,
            "config_entry_id": self.entry.entry_id,
            "count": len(entities),
            "entities": entities,
        }

    def _build_info(self, snapshot: SupportSnapshot) -> dict[str, Any]:
        """Return stable build and environment metadata."""
        return sanitize_support_data({
            "project": "BTDoor Security+",
            "domain": DOMAIN,
            "version": snapshot.get("integration", {}).get("version", "unknown"),
            "build": "Persistent Runtime Snapshot",
            "support_bundle_schema": 3,
            "python": snapshot.get("system", {}).get("python"),
            "platform": snapshot.get("system", {}).get("platform"),
            "generated_at": snapshot.get("generated_at"),
        })

    @staticmethod
    def _markdown(data: dict[str, Any]) -> str:
        # Build only from an exported/support-sanitized copy. This prevents a
        # future field from bypassing IP and SIP identifier masking.
        safe = sanitize_support_data(data)
        tests = safe["tests"]
        health = safe.get("health", {})
        score = health.get("score") if isinstance(health, dict) else None
        status = health.get("status") if isinstance(health, dict) else None
        lines = [
            "# BTDoor Security+ - Report di Supporto", "",
            f"Generato: `{safe['generated_at']}`", "",
            "## Versioni", "",
            f"- Integrazione: `{safe['integration']['version']}`",
            f"- Python: `{safe['system']['python'].split()[0]}`",
            "- Target device: `BTicino Classe 300X`",
            "- Target firmware: `Door Entry 1.17.3`", "",
        ]
        if score is not None:
            lines += ["## Health Check", "", f"- Score: **{score}/100**", f"- Stato: **{status}**", ""]
        lines += ["## Esito test", ""]
        for name, result in tests.items():
            lines.append(f"- **{name}**: {'OK' if result.get('ok') else 'ERRORE'} - `{result.get('duration_ms', 0)} ms`")
        media = safe.get("runtime", {}).get("media_runtime", {})
        if media:
            plan = media.get("plan") or {}
            audio = plan.get("audio") or {}
            video = plan.get("video") or {}
            srtp = plan.get("srtp") or {}
            lines += [
                "", "## Media Engine", "",
                f"- State: **{media.get('state')}**",
                f"- Ready for answer: **{'YES' if media.get('ready_for_answer') else 'NO'}**",
                f"- Audio codec: `{audio.get('codec')}`",
                f"- Video codec: `{video.get('codec')}`",
                f"- SRTP suite: `{srtp.get('suite')}`",
                f"- Local media address: `{plan.get('local_media_address')}`",
                "",
            ]
        lines += [
            "", "## Stato runtime", "", "```json",
            json.dumps(safe["runtime"], ensure_ascii=False, indent=2, default=str), "```",
            "", "## Dettagli test", "", "```json",
            json.dumps(tests, ensure_ascii=False, indent=2, default=str), "```", "",
            "> Password, token, header Digest, chiavi SRTP, identificatori SIP e indirizzi IP sono esclusi, oscurati o anonimizzati.", "",
        ]
        return "\n".join(lines)

    def _write_bundle(
        self,
        bundle: Path,
        report: Path,
        snapshot: SupportSnapshot,
        include_logs: bool,
        registry_report: dict[str, Any],
        translation_report: dict[str, Any],
        entity_registry_report: dict[str, Any],
    ) -> None:
        """Write Support Bundle v2 from structured, pre-sanitized values only."""
        safe_snapshot = sanitize_support_data(snapshot)
        client = self.runtime.client
        safe_headers = structure_dialog_headers(client.last_dialog_headers)
        safe_current = sanitize_support_data(client.current_session_timeline)
        safe_history = sanitize_support_data(list(client.sip_timeline))
        all_events = [*safe_history, *safe_current]

        runtime = safe_snapshot.get("runtime", {})
        tests = safe_snapshot.get("tests", {})
        framework = safe_snapshot.get("diagnostic_framework", {})
        provider_payloads = {
            f"diagnostics/providers/{name}.json": payload
            for name, payload in (framework.get("providers") or {}).items()
        }

        subsystem_payloads = {
            "runtime/runtime.json": runtime,
            "runtime/connection.json": {
                "registered": runtime.get("registered"),
                "last_status": runtime.get("last_status"),
                "last_error": runtime.get("last_error"),
                "reconnect_count": runtime.get("reconnect_count"),
                "connected_at": runtime.get("connected_at"),
                "last_keepalive_at": runtime.get("last_keepalive_at"),
            },
            "runtime/dialog.json": {
                "dialog_state": runtime.get("dialog_state"),
                "last_sip_method": runtime.get("last_sip_method"),
                "call_state": runtime.get("call_state"),
                "runtime_session_id": runtime.get("runtime_session_id"),
                "runtime_session_started_at": runtime.get("runtime_session_started_at"),
            },
            "runtime/media.json": runtime.get("media_runtime") or {},
            "runtime/media-last-completed.json": client.last_completed_media_session or {},
            "runtime/media-history.json": list(client.media_session_history),
            "runtime/media-metrics.json": client.media_session_metrics,
            "events/history.json": runtime.get("runtime_events") or [],
            "events/metrics.json": runtime.get("runtime_event_metrics") or {},
            "events/schema.json": {
                "schema_version": 1,
                "event_schema_version": 1,
                "retention": 500,
            },
            "calls/journal.json": runtime.get("call_journal") or [],
            "calls/metrics.json": runtime.get("call_journal_metrics") or {},
            "calls/schema.json": {
                "schema_version": 1,
                "retention": 250,
                "source": "runtime_event_bus",
            },
            "diagnostics/cloud.json": tests.get("cloud", {}),
            "diagnostics/certificates.json": tests.get("certificates", {}),
            "diagnostics/sip.json": tests.get("sip", {}),
            "diagnostics/tls.json": tests.get("tls", {}),
            "diagnostics/dialog.json": tests.get("dialog", {}),
            "diagnostics/media.json": tests.get("media", {}),
            "diagnostics/health.json": safe_snapshot.get("health", {}),
        }

        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.write(report, report.name)
            archive.writestr("support_summary.json", json_dumps(self._support_summary(safe_snapshot)))
            archive.writestr("build_info.json", json_dumps(self._build_info(safe_snapshot)))
            archive.writestr("configuration/options.json", json_dumps(sanitize_support_data({**dict(self.entry.options), "effective_visibility": visibility_for_entry(self.entry).as_dict()})))
            archive.writestr("registry/devices.json", json_dumps(sanitize_support_data(registry_report)))
            archive.writestr("registry/entities.json", json_dumps(sanitize_support_data(entity_registry_report)))
            archive.writestr("translations/report.json", json_dumps(sanitize_support_data(translation_report)))
            archive.writestr("diagnostics.json", json_dumps(safe_snapshot))
            archive.writestr("sip/timeline-summary.json", json_dumps(self._timeline_summary(all_events)))
            for name, payload in {**subsystem_payloads, **provider_payloads}.items():
                archive.writestr(name, json_dumps(sanitize_support_data(payload)))
            archive.writestr(
                "diagnostics/framework-health.json",
                json_dumps(sanitize_support_data(framework.get("health", {}))),
            )

            if client.last_sdp_offer:
                archive.writestr("sip/original_sdp.txt", redact_support_text(client.last_sdp_offer))
            if client.last_media_remote_sdp:
                archive.writestr("media/remote_sdp.txt", redact_support_text(client.last_media_remote_sdp))
            if client.last_media_local_sdp:
                archive.writestr("media/local_sdp.txt", redact_support_text(client.last_media_local_sdp))
            if client.last_media_sdp_diff:
                archive.writestr("media/sdp_diff.txt", redact_support_text(client.last_media_sdp_diff))
            archive.writestr("media/runtime.json", json_dumps(sanitize_support_data(client.media_runtime)))
            archive.writestr("media/last-completed-session.json", json_dumps(sanitize_support_data(client.last_completed_media_session or {})))
            archive.writestr("media/session-history.json", json_dumps(sanitize_support_data(list(client.media_session_history))))
            archive.writestr("media/session-metrics.json", json_dumps(sanitize_support_data(client.media_session_metrics)))
            archive.writestr("media/instrumentation.json", json_dumps(sanitize_support_data(client.media_instrumentation)))
            archive.writestr("sip/dispatcher_trace.json", json_dumps(sanitize_support_data(client.sip_dispatcher_diagnostics)))
            archive.writestr("sip/dialog_headers.json", json_dumps(safe_headers))
            archive.writestr("sip/timeline-current-session.json", json_dumps(safe_current))
            archive.writestr("sip/timeline-historical.json", json_dumps(safe_history))

            if include_logs and self.runtime.debug:
                candidates = [
                    self.runtime.debug.log_path,
                    *[self.runtime.debug.log_path.with_suffix(f".jsonl.{index}") for index in range(1, 6)],
                ]
                for candidate in candidates:
                    if candidate.is_file():
                        raw = candidate.read_text(encoding="utf-8", errors="replace")
                        archive.writestr(f"logs/{candidate.name}", sanitize_jsonl(raw))

