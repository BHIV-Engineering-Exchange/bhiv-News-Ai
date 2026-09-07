import json
import asyncio
from unittest.mock import Mock

import pytest

from analysis import bucket_client
from runtime.output_store import (
    OutputIntegrityError,
    OutputNotFoundError,
    OutputStore,
)


def test_output_store_round_trip_and_large_result(tmp_path):
    result = {
        "trace_id": "SAM-TRACE-large",
        "schema_version": "1.0.0",
        "payload": "x" * (17 * 1024 * 1024),
    }
    store = OutputStore(str(tmp_path))

    manifest = store.write_result(
        result,
        execution_id="SAM-EXEC-large",
        input_fingerprint="sha256:input",
    )
    loaded, loaded_manifest = store.read_by_trace_id(
        result["trace_id"],
        expected_metadata=manifest,
    )

    assert loaded == result
    assert loaded_manifest["output_size_bytes"] > 16 * 1024 * 1024
    assert loaded_manifest["output_reference"].startswith("intelligence/")


def test_output_store_rejects_missing_and_tampered_output(tmp_path):
    store = OutputStore(str(tmp_path))
    result = {"trace_id": "SAM-TRACE-integrity", "value": "original"}
    store.write_result(result, "SAM-EXEC-integrity", "sha256:input")

    with pytest.raises(OutputNotFoundError):
        store.read_by_trace_id("SAM-TRACE-missing")

    result_path = tmp_path / "intelligence" / result["trace_id"] / "result.json"
    result_path.write_text(json.dumps({"trace_id": result["trace_id"], "value": "tampered"}), encoding="utf-8")
    with pytest.raises(OutputIntegrityError):
        store.read_by_trace_id(result["trace_id"])


def test_output_store_rejects_unsafe_trace_id(tmp_path):
    store = OutputStore(str(tmp_path))
    with pytest.raises(Exception):
        store.read_by_trace_id("../outside")


def test_bucket_receives_compact_reference_for_large_payload(monkeypatch):
    monkeypatch.setenv("BUCKET_URL", "http://bucket.test")
    posted = {}

    def fake_get(*args, **kwargs):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"last_hash": None}
        return response

    def fake_post(*args, **kwargs):
        posted.update(kwargs["json"])
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "success": True,
            "artifact_id": posted["artifact_id"],
            "hash": "hash-1",
        }
        return response

    monkeypatch.setattr(bucket_client.requests, "get", fake_get)
    monkeypatch.setattr(bucket_client.requests, "post", fake_post)

    metadata = {
        "trace_id": "SAM-TRACE-large-bucket",
        "execution_id": "SAM-EXEC-large-bucket",
        "input_fingerprint": "sha256:input",
        "schema_version": "1.0.0",
        "timestamp": "2026-09-04T00:00:00+00:00",
        "output_reference": "intelligence/SAM-TRACE-large-bucket/result.json",
        "output_size_bytes": 17 * 1024 * 1024,
        "output_sha256": "sha256:output",
        "artifact_type": "canonical_intelligence_reference",
    }
    response = bucket_client.BucketClient().store_artifact(metadata)

    assert response["success"] is True
    assert posted["payload"]["output_size_bytes"] > 16 * 1024 * 1024
    assert "payload" not in posted["payload"]


def _bucket_response(status_code, payload):
    response = Mock()
    response.status_code = status_code
    response.ok = status_code < 400
    response.json.return_value = payload
    response.raise_for_status.side_effect = (
        None if response.ok else RuntimeError(f"Bucket HTTP {status_code}")
    )
    return response


def test_bucket_retrieval_uses_existing_in_memory_mapping(monkeypatch):
    client = bucket_client.BucketClient.__new__(bucket_client.BucketClient)
    client.base_url = "http://bucket.test"
    trace_id = "SAM-TRACE-mapped"
    bucket_client.BucketClient._trace_to_artifact[trace_id] = "artifact-mapped"
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return _bucket_response(200, {"artifact": {"trace_id": trace_id}})

    monkeypatch.setattr(bucket_client.requests, "get", fake_get)
    assert client.get_artifact(trace_id) == {"artifact": {"trace_id": trace_id}}
    assert calls == [
        ("http://bucket.test/bucket/artifact/artifact-mapped", {"timeout": 15})
    ]
    bucket_client.BucketClient._trace_to_artifact.pop(trace_id, None)


def test_bucket_retrieval_resolves_trace_after_mapping_is_absent(monkeypatch):
    client = bucket_client.BucketClient.__new__(bucket_client.BucketClient)
    client.base_url = "http://bucket.test"
    trace_id = "SAM-TRACE-restarted"
    bucket_client.BucketClient._trace_to_artifact.pop(trace_id, None)
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        if url.endswith("/bucket/artifacts"):
            return _bucket_response(200, {
                "artifacts": [
                    {
                        "artifact_id": "artifact-old",
                        "trace_id": trace_id,
                        "timestamp_utc": "2026-09-03T00:00:00+00:00",
                    },
                    {
                        "artifact_id": "artifact-new",
                        "trace_id": trace_id,
                        "timestamp_utc": "2026-09-04T00:00:00+00:00",
                    },
                ]
            })
        return _bucket_response(200, {"artifact_id": "artifact-new"})

    monkeypatch.setattr(bucket_client.requests, "get", fake_get)
    assert client.get_artifact(trace_id) == {"artifact_id": "artifact-new"}
    assert calls == [
        (
            "http://bucket.test/bucket/artifacts",
            {"params": {"trace_id": trace_id}, "timeout": 15},
        ),
        ("http://bucket.test/bucket/artifact/artifact-new", {"timeout": 15}),
    ]
    assert bucket_client.BucketClient._trace_to_artifact[trace_id] == "artifact-new"
    bucket_client.BucketClient._trace_to_artifact.pop(trace_id, None)


def test_bucket_retrieval_reports_no_artifact(monkeypatch):
    client = bucket_client.BucketClient.__new__(bucket_client.BucketClient)
    client.base_url = "http://bucket.test"
    monkeypatch.setattr(
        bucket_client.requests,
        "get",
        lambda *args, **kwargs: _bucket_response(200, {"artifacts": []}),
    )
    assert client.get_artifact("SAM-TRACE-absent") is None


def test_bucket_retrieval_rejects_malformed_trace_query(monkeypatch):
    client = bucket_client.BucketClient.__new__(bucket_client.BucketClient)
    client.base_url = "http://bucket.test"
    monkeypatch.setattr(
        bucket_client.requests,
        "get",
        lambda *args, **kwargs: _bucket_response(200, {"artifact": {}}),
    )
    assert client.get_artifact("SAM-TRACE-malformed") is None


def test_bucket_retrieval_handles_bucket_error(monkeypatch):
    client = bucket_client.BucketClient.__new__(bucket_client.BucketClient)
    client.base_url = "http://bucket.test"
    monkeypatch.setattr(
        bucket_client.requests,
        "get",
        lambda *args, **kwargs: _bucket_response(500, {"detail": "Bucket down"}),
    )
    assert client.get_artifact("SAM-TRACE-error") is None


def test_existing_retrieval_endpoint_combines_bucket_and_output(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_STORAGE_ROOT", str(tmp_path))
    from main import get_intelligence_by_trace_id

    result = {
        "trace_id": "SAM-TRACE-retrieve",
        "schema_version": "1.0.0",
        "provenance": {
            "execution_id": "SAM-EXEC-retrieve",
            "input_fingerprint": "sha256:input",
        },
        "intelligence": {"value": "complete"},
    }
    manifest = OutputStore(str(tmp_path)).write_result(
        result,
        "SAM-EXEC-retrieve",
        "sha256:input",
    )

    class FakeBucketClient:
        def __init__(self):
            pass

        def get_artifact(self, trace_id):
            return {
                "artifact": {
                    "artifact_id": "artifact-1",
                    "hash": "hash-1",
                    "parent_hash": None,
                    "payload": {
                        "trace_id": trace_id,
                        "execution_id": "SAM-EXEC-retrieve",
                        "input_fingerprint": "sha256:input",
                        **{
                            key: manifest[key]
                            for key in (
                                "schema_version",
                                "output_reference",
                                "output_size_bytes",
                                "output_sha256",
                            )
                        },
                    },
                }
            }

    monkeypatch.setattr("main.BucketClient", FakeBucketClient)
    response = asyncio.run(get_intelligence_by_trace_id(result["trace_id"]))

    assert response.status == "success"
    assert response.canonical_intelligence == result
    assert response.bucket_artifact["output_sha256"] == manifest["output_sha256"]


def test_bucket_failure_leaves_output_available_for_retry(tmp_path):
    result = {"trace_id": "SAM-TRACE-retry", "value": "preserved"}
    store = OutputStore(str(tmp_path))
    manifest = store.write_result(result, "SAM-EXEC-retry", "sha256:input")

    def failing_bucket_publish():
        raise RuntimeError("Bucket unavailable")

    with pytest.raises(RuntimeError):
        failing_bucket_publish()

    loaded, _ = store.read_by_trace_id(result["trace_id"], manifest)
    assert loaded == result


def test_retrieval_endpoint_reports_missing_referenced_output(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_STORAGE_ROOT", str(tmp_path))
    from main import get_intelligence_by_trace_id

    class FakeBucketClient:
        def __init__(self):
            pass

        def get_artifact(self, trace_id):
            return {
                "artifact": {
                    "artifact_id": "artifact-missing",
                    "payload": {
                        "trace_id": trace_id,
                        "output_reference": f"intelligence/{trace_id}/result.json",
                        "output_size_bytes": 10,
                        "output_sha256": "sha256:missing",
                    },
                }
            }

    monkeypatch.setattr("main.BucketClient", FakeBucketClient)
    response = asyncio.run(
        get_intelligence_by_trace_id("SAM-TRACE-missing-reference")
    )

    assert response.status_code == 503
    assert response.body.find(b"STORAGE_INCOMPLETE") >= 0
