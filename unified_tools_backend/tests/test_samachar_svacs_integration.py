import json

from analysis.manual_intelligence_service import (ManualIntelligenceService)

from analysis.satellite_intelligence_service import (SatelliteIntelligenceService)

from runtime.svacs_contract_validator import (SVACSContractValidator)

from analysis.svacs_intelligence_mapper import (SVACSIntelligenceMapper)

def test_manual_intelligence_integration():

    service = ManualIntelligenceService()

    result = service.process(
        content=(
            "A suspected patrol vessel was "
            "observed near Mumbai coastal waters. "
            "Authorities started an investigation."
        ),
        source="operator",
    )

    print(
        "\nMANUAL INTELLIGENCE INTEGRATION\n"
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    assert result["trace_id"].startswith(
        "SAM-"
    )

    assert (
        result["source"]["input_type"]
        == "manual"
    )

    assert (
        result["provenance"][
            "vision_runtime_invoked"
        ]
        is False
    )

    assert (
        result["downstream"][
            "target_system"
        ]
        == "svacs"
    )

    assert (
        result["downstream"][
            "ready_for_processing"
        ]
        is True
    )


def test_satellite_feed_integration():

    service = SatelliteIntelligenceService()

    result = service.process(
        feed_id="SAT-INTEGRATION-001",
        timestamp_utc=(
            "2026-07-15T06:00:00+00:00"
        ),
        image_reference=(
            "satellite://feed/image/001"
        ),
        metadata={
            "provider": "test_provider",
            "region": "arabian_sea",
        },
    )

    print(
        "\nSATELLITE FEED INTEGRATION\n"
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    assert result["trace_id"].startswith(
        "SAM-"
    )

    assert (
        result["source"]["input_type"]
        == "satellite_feed"
    )

    assert (
        result["integration_status"][
            "feed_interface"
        ]
        == "AVAILABLE"
    )

    assert (
        result["integration_status"][
            "production_feed_adapter"
        ]
        == "PENDING_CONTRACT"
    )

    assert (
        result["downstream"][
            "target_system"
        ]
        == "svacs"
    )


def test_svacs_contract_integration():

    canonical_intelligence = {
        "trace_id": (
            "SAM-integration-contract-test"
        ),
        "timestamp": (
            "2026-07-15T06:30:00+00:00"
        ),
        "source": {
            "input_type": "image",
            "source_system": "samachar",
        },
        "vision_intelligence": {
            "detections": [
                {
                    "label": "Vessel",
                    "confidence": 0.89,
                }
            ],
            "ocr_results": [
                {
                    "text": "\"BALEARIA",
                    "confidence": 0.9491,
                }
            ],
            "normalized_ocr_results": [
                {
                    "text": "BALEARIA",
                    "confidence": 0.9491,
                    "source": "vision_runtime_ocr",
                }
            ],
        },
        "intelligence": {
            "confidence": {
                "score": 37.0,
            }
        },
    }

    mapper = SVACSIntelligenceMapper()

    svacs_payload = mapper.map(
        canonical_intelligence
    )

    validation_result = (
        SVACSContractValidator.validate(
            svacs_payload
        )
    )

    print(
        "\nSAMACHAR TO SVACS CONTRACT INTEGRATION\n"
    )

    print(
        json.dumps(
            svacs_payload,
            indent=2,
            ensure_ascii=False,
        )
    )

    print(
        "\nCONTRACT VALIDATION\n"
    )

    print(
        json.dumps(
            validation_result,
            indent=2,
            ensure_ascii=False,
        )
    )

    assert (
        svacs_payload["trace_id"]
        == canonical_intelligence["trace_id"]
    )

    assert (
        svacs_payload["vessel_class"]
        == "unknown"
    )

    assert (
        svacs_payload["vision_confidence"]
        == 0.89
    )

    assert (
        "ocr_results"
        in svacs_payload
    )

    assert isinstance(
        svacs_payload["ocr_results"],
        list
    )

    assert (
        len(
            svacs_payload["ocr_results"]
        )
        == 1
    )

    assert (
        svacs_payload[
            "ocr_results"
        ][0]["text"]
        == "BALEARIA"
    )

    assert (
        svacs_payload[
            "ocr_results"
        ][0]["confidence"]
        == 0.9491
    )

    assert (
        svacs_payload["confidence_score"]
        == 0.37
    )

    assert (
        validation_result["valid"]
        is True
    )