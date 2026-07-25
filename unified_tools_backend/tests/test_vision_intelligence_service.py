import json
from pathlib import Path
from unittest.mock import Mock

from dotenv import load_dotenv

from analysis.vision_intelligence_service import (
    VisionIntelligenceService
)
from runtime.replay_store import ReplayStore


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    dotenv_path=BASE_DIR / ".env"
)


def test_vision_intelligence_service():

    service = VisionIntelligenceService()

    image_path = (
        BASE_DIR
        / "tests"
        / "ship3.jpeg"
    )

    with open(
        image_path,
        "rb"
    ) as image_file:

        image_bytes = image_file.read()

    result = service.process(
        image_bytes=image_bytes,
        filename="test_ship.jpeg",
        content_type="image/jpeg",
        return_explainable_image=False
    )

    print(
        "\nCanonical Vision Intelligence\n"
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )

    assert result["schema_version"] == "1.0.0"

    assert result["trace_id"].startswith(
        "SAM-"
    )

    assert (
        result["provenance"][
            "vision_runtime_invoked"
        ]
        is True
    )

    assert "vision_intelligence" in result

    assert (
        result["processing_trace"]["status"]
        == "SUCCESS"
    )

    assert (
        result["downstream"][
            "ready_for_processing"
        ]
        is True
    )


def test_vision_intelligence_replay_preserves_canonical_provenance():
    ReplayStore.clear()

    service = VisionIntelligenceService.__new__(VisionIntelligenceService)
    service.vision_client = Mock()
    service.vision_client.analyze_image.return_value = {
        "replay_id": "vision-run-001",
        "detections": [],
        "ocr_results": [],
    }
    service.intelligence_service = Mock()

    image_bytes = b"test-image-content"
    first_result = service.process(
        image_bytes=image_bytes,
        filename="test.png",
        content_type="image/png",
    )
    second_result = service.process(
        image_bytes=image_bytes,
        filename="test.png",
        content_type="image/png",
    )

    assert first_result["replay"]["status"] == "MISS"
    assert second_result["replay"]["status"] == "HIT"
    assert first_result["trace_id"] == second_result["trace_id"]
    assert "input_fingerprint" in first_result["provenance"]
    assert first_result["provenance"]["normalization"]["ocr_results_received"] == 0
    assert service.vision_client.analyze_image.call_count == 1
