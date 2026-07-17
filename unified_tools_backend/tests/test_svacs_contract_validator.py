import json

from runtime.svacs_contract_validator import (
    SVACSContractValidator
)


def test_svacs_contract_validator():

    payload = {
        "trace_id": (
            "SAM-test-contract-trace"
        ),
        "source_type": "image",
        "vessel_class": "unknown",
        "confidence_score": 0.0,
        "vision_confidence": 0.89,
        "ocr_results": [
            {
                "text": "BALEARIA",
                "confidence": 0.9491,
            }
        ],
        "visual_features": [],
        "dimensions_estimate": {
            "length_m": None,
            "beam_m": None,
        },
        "ais_data": {
            "mmsi": None,
            "speed_knots": None,
        },
        "timestamp_utc": (
            "2026-07-15T04:30:00+00:00"
        ),
    }

    validation_result = (SVACSContractValidator.validate(payload))

    print("\nSVACS V1 CONTRACT VALIDATION\n")

    print(
        json.dumps(
            validation_result,
            indent=2,
            ensure_ascii=False,
        )
    )

    assert (
        validation_result["valid"]
        is True
    )

    assert (
        validation_result[
            "contract_version"
        ]
        == "1.0.0"
    )

    assert (
        validation_result["errors"]
        == []
    )

def test_svacs_contract_rejects_invalid_payload():

    payload = {
        "trace_id": "INVALID-TRACE",
        "source_type": "image",
        "vessel_class": "warship",
        "confidence_score": 2.5,
        "vision_confidence": 0.89,
        "ocr_results": [
            {
                "text": "",
                "confidence": 1.5,
            }
        ],
        "visual_features": [],
        "dimensions_estimate": {
            "length_m": None,
            "beam_m": None,
        },
        "ais_data": {
            "mmsi": None,
            "speed_knots": None,
        },
        "timestamp_utc": "invalid-date",
    }

    validation_result = (
        SVACSContractValidator.validate(
            payload
        )
    )

    print(
        "\nINVALID SVACS V1 PAYLOAD\n"
    )

    print(
        json.dumps(
            validation_result,
            indent=2,
            ensure_ascii=False,
        )
    )

    assert (
        validation_result["valid"]
        is False
    )

    assert (
        len(
            validation_result["errors"]
        )
        > 0
    )