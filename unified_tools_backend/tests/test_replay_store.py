from runtime.replay_store import ReplayStore


def test_replay_store():

    ReplayStore.clear()

    fingerprint = (
        "sha256:test-fingerprint"
    )

    original_result = {
        "schema_version": "1.0.0",
        "trace_id": "SAM-TEST-001",
        "source": {
            "input_type": "manual"
        },
    }

    first_record = ReplayStore.save(
        input_fingerprint=fingerprint,
        trace_id="SAM-TEST-001",
        input_type="manual",
        schema_version="1.0.0",
        result=original_result,
    )

    assert (
        first_record["trace_id"]
        == "SAM-TEST-001"
    )

    assert ReplayStore.count() == 1

    replay_record = ReplayStore.get(
        fingerprint
    )

    assert replay_record is not None

    assert (
        replay_record["trace_id"]
        == "SAM-TEST-001"
    )

    assert (
        replay_record["result"]
        == original_result
    )

    duplicate_result = {
        "schema_version": "1.0.0",
        "trace_id": "SAM-TEST-002",
    }

    duplicate_record = ReplayStore.save(
        input_fingerprint=fingerprint,
        trace_id="SAM-TEST-002",
        input_type="manual",
        schema_version="1.0.0",
        result=duplicate_result,
    )

    assert (
        duplicate_record["trace_id"]
        == "SAM-TEST-001"
    )

    assert ReplayStore.count() == 1