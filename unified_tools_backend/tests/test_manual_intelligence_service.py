import json

from analysis.manual_intelligence_service import (
    ManualIntelligenceService
)

from runtime.replay_store import ReplayStore


def test_manual_intelligence_replay():

    ReplayStore.clear()

    service = ManualIntelligenceService()

    content = (
        "A suspected patrol vessel was observed "
        "near Mumbai coastal waters. "
        "Authorities started an investigation."
    )

    first_result = service.process(
        content=content,
        source="operator",
    )

    print(
        "\nFIRST MANUAL EXECUTION\n"
    )

    print(
        json.dumps(
            first_result,
            indent=2,
            ensure_ascii=False,
        )
    )

    second_result = service.process(
        content=content,
        source="operator",
    )

    print(
        "\nSECOND MANUAL EXECUTION\n"
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