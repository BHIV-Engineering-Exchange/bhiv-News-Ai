import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


class OutputStoreError(RuntimeError):
    """Base error for durable intelligence output storage."""


class OutputNotFoundError(OutputStoreError):
    """The referenced output does not exist."""


class OutputIntegrityError(OutputStoreError):
    """The output or manifest failed integrity validation."""


class OutputStore:
    """Secure, atomic, trace-id keyed storage for complete intelligence results."""

    TRACE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")

    def __init__(self, root: str | None = None):
        configured_root = root or os.getenv("OUTPUT_STORAGE_ROOT", "output")
        self.root = Path(configured_root).expanduser().resolve()
        self.intelligence_root = (self.root / "intelligence").resolve()

    @classmethod
    def validate_trace_id(cls, trace_id: str) -> str:
        if not isinstance(trace_id, str) or not cls.TRACE_ID_PATTERN.fullmatch(trace_id):
            raise OutputStoreError("Invalid trace_id for output storage")
        return trace_id

    def _directory(self, trace_id: str) -> Path:
        safe_trace_id = self.validate_trace_id(trace_id)
        directory = (self.intelligence_root / safe_trace_id).resolve()
        if directory.parent != self.intelligence_root:
            raise OutputStoreError("Unsafe output storage path")
        return directory

    @staticmethod
    def _atomic_write_json(path: Path, value: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temp_name = temporary.name
                json.dump(value, temporary, ensure_ascii=False, separators=(",", ":"))
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temp_name, path)
        except Exception:
            if temp_name:
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass
            raise

    def write_result(
        self,
        canonical_intelligence: Dict[str, Any],
        execution_id: str,
        input_fingerprint: str,
    ) -> Dict[str, Any]:
        if not isinstance(canonical_intelligence, dict):
            raise OutputStoreError("Canonical intelligence must be a dictionary")

        trace_id = self.validate_trace_id(canonical_intelligence.get("trace_id", ""))
        directory = self._directory(trace_id)
        result_path = directory / "result.json"
        reference = (Path("intelligence") / trace_id / "result.json").as_posix()

        self._atomic_write_json(result_path, canonical_intelligence)
        output_size_bytes = result_path.stat().st_size
        digest = hashlib.sha256(result_path.read_bytes()).hexdigest()
        created_at = datetime.now(timezone.utc).isoformat()
        manifest = {
            "trace_id": trace_id,
            "execution_id": execution_id,
            "input_fingerprint": input_fingerprint,
            "schema_version": canonical_intelligence.get("schema_version"),
            "output_reference": reference,
            "output_size_bytes": output_size_bytes,
            "output_sha256": f"sha256:{digest}",
            "created_at": created_at,
            "content_type": "application/json",
        }
        self._atomic_write_json(directory / "manifest.json", manifest)
        return manifest

    def read_by_trace_id(
        self,
        trace_id: str,
        expected_metadata: Dict[str, Any] | None = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        directory = self._directory(trace_id)
        result_path = directory / "result.json"
        manifest_path = directory / "manifest.json"
        if not result_path.is_file() or not manifest_path.is_file():
            raise OutputNotFoundError(f"Output not found for trace_id: {trace_id}")

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise OutputIntegrityError(
                f"Unable to read output for trace_id: {trace_id}"
            ) from exc

        if not isinstance(manifest, dict) or not isinstance(result, dict):
            raise OutputIntegrityError("Output and manifest must be JSON objects")

        actual_size = result_path.stat().st_size
        actual_digest = f"sha256:{hashlib.sha256(result_path.read_bytes()).hexdigest()}"
        if (
            manifest.get("trace_id") != trace_id
            or manifest.get("output_reference")
            != (Path("intelligence") / trace_id / "result.json").as_posix()
            or manifest.get("output_size_bytes") != actual_size
            or manifest.get("output_sha256") != actual_digest
            or result.get("trace_id") != trace_id
        ):
            raise OutputIntegrityError(f"Output integrity check failed for trace_id: {trace_id}")

        for key in ("output_reference", "output_size_bytes", "output_sha256"):
            if expected_metadata and key in expected_metadata:
                if manifest.get(key) != expected_metadata.get(key):
                    raise OutputIntegrityError(f"Output metadata mismatch for {key}")

        for key in ("execution_id", "input_fingerprint", "schema_version"):
            if (
                expected_metadata
                and expected_metadata.get(key) is not None
                and manifest.get(key) != expected_metadata.get(key)
            ):
                raise OutputIntegrityError(f"Output metadata mismatch for {key}")

        return result, manifest
