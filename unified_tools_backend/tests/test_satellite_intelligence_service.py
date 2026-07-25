import json

from analysis.satellite_intelligence_service import (
    SatelliteIntelligenceService
)

from runtime.replay_store import ReplayStore


def test_satellite_intelligence_replay():

    ReplayStore.clear()

    service = SatelliteIntelligenceService()

    first_result = service.process(
        feed_id="SAT-TEST-001",
        timestamp_utc=(
            "2026-07-14T15:00:00Z"
        ),
        image_reference=(
            "satellite://feed/SAT-TEST-001/image"
        ),
        metadata={
            "region": "Mumbai Coastal Waters",
            "provider": "future_satellite_provider",
        },
    )

    print(
        "\nFIRST SATELLITE EXECUTION\n"
    )

    print(
        json.dumps(
            first_result,
            indent=2,
            ensure_ascii=False,
        )
    )

    second_result = service.process(
        feed_id="SAT-TEST-001",
        timestamp_utc=(
            "2026-07-14T15:00:00Z"
        ),
        image_reference=(
            "satellite://feed/SAT-TEST-001/image"
        ),
        metadata={
            "region": "Mumbai Coastal Waters",
            "provider": "future_satellite_provider",
        },
    )

    print(
        "\nSECOND SATELLITE EXECUTION\n"
    )

    print(
        json.dumps(
            second_result,
            indent=2,
            ensure_ascii=False,
        )
    )

    assert (
        first_result["replay"]["status"]
        == "MISS"
    )

    assert (
        second_result["replay"]["status"]
        == "HIT"
    )

    assert (
        first_result["trace_id"]
        == second_result["trace_id"]
    )

    assert (
        first_result["provenance"][
            "input_fingerprint"
        ]
        == second_result["provenance"][
            "input_fingerprint"
        ]
    )

    assert (
        second_result["replay"][
            "original_trace_id"
        ]
        == first_result["trace_id"]
    )

    assert ReplayStore.count() == 1


def test_satellite_intelligence_rejects_non_object_metadata():
    service = SatelliteIntelligenceService()

    try:
        service.process(
            feed_id="SAT-TEST-INVALID",
            timestamp_utc="2026-07-14T15:00:00Z",
            metadata=["invalid"],
        )
    except ValueError as exc:
        assert str(exc) == "Satellite metadata must be an object"
    else:
        raise AssertionError("Satellite metadata validation must reject arrays")
