import json

from analysis.svacs_intelligence_mapper import (
    SVACSIntelligenceMapper
)


def test_svacs_intelligence_mapper():

    canonical_intelligence = {
        "schema_version": "1.0.0",
        "trace_id": (
            "SAM-b95e810c-5503-48c6-9490-ad1de6eb4aa9"
        ),
        "timestamp": (
            "2026-07-14T10:42:24.487301+00:00"
        ),
        "source": {
            "input_type": "image",
            "source_system": "samachar",
            "filename": "test_ship.jpeg",
        },
        "vision_intelligence": {
            "replay_id": (
                "9b338dff-16e9-471a-8ea6-37269357f13c"
            ),
            "detections": [
                {
                    "label": "Vessel",
                    "confidence": 0.533457338809967,
                    "bounding_box": {
                        "x_min": 72.32,
                        "y_min": 301.20,
                        "x_max": 747.22,
                        "y_max": 532.46,
                    },
                }
            ],
            "ocr_results": [
                {
                    "text": "\"BALEARIA",
                    "confidence": 0.9491,
                }
            ],
        },
        "intelligence": {
            "confidence": {
                "score": 0.0,
                "summary": (
                    "0 entities, 0 evidence matches, "
                    "classification confidence 0.0"
                ),
            }
        },
    }

    mapper = SVACSIntelligenceMapper()

    result = mapper.map(
        canonical_intelligence
    )

    print(
        "\nSVACS Structured Intelligence\n"
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    assert (
        result["trace_id"]
        == canonical_intelligence["trace_id"]
    )

    assert result["source_type"] == "image"

    assert result["vessel_class"] == "unknown"

    assert (
        result["vision_confidence"]
        == 0.533457338809967
    )

    assert result["visual_features"] == []

    assert (
        result["dimensions_estimate"][
            "length_m"
        ]
        is None
    )

    assert (
        result["dimensions_estimate"][
            "beam_m"
        ]
        is None
    )

    assert (
        result["ais_data"]["mmsi"]
        is None
    )

    assert (
        result["ais_data"]["speed_knots"]
        is None
    )