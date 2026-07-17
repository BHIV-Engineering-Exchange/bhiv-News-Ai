import json
from pathlib import Path

from dotenv import load_dotenv

from analysis.vision_intelligence_service import (
    VisionIntelligenceService
)


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