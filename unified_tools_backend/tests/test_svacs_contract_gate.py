import json

from runtime.svacs_contract_validator import (SVACSContractValidator)

from runtime.error_response import (RuntimeErrorResponse)


def test_svacs_contract_governance_gate():

    invalid_svacs_payload = {
        "trace_id": (
            "SAM-contract-gate-test"
        ),
        "source_type": "image",
        "vessel_class": "destroyer",
        "confidence_score": 0.85,
        "vision_confidence": 0.91,
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
            "2026-07-15T05:00:00+00:00"
        ),
    }

    contract_validation = (
        SVACSContractValidator.validate(
            invalid_svacs_payload
        )
    )

    assert (
        contract_validation["valid"]
        is False
    )

    error_response = (
        RuntimeErrorResponse.build(
            trace_id=(
                invalid_svacs_payload[
                    "trace_id"
                ]
            ),
            error_code=(
                "SVACS_CONTRACT_VALIDATION_FAILED"
            ),
            message=(
                "; ".join(
                    contract_validation[
                        "errors"
                    ]
                )
            ),
            stage=(
                "svacs_contract_validation"
            ),
            failed_step=(
                "SVACS Contract Validation"
            ),
            source_type="image",
        )
    )

    print(
        "\nSVACS CONTRACT GOVERNANCE FAILURE\n"
    )

    print(
        json.dumps(
            error_response,
            indent=2,
            ensure_ascii=False,
        )
    )

    assert (
        error_response["status"]
        == "FAILED"
    )

    assert (
        error_response["error"]["code"]
        == (
            "SVACS_CONTRACT_VALIDATION_FAILED"
        )
    )

    assert (
        error_response["downstream"][
            "ready_for_processing"
        ]
        is False
    )