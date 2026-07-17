import json

from runtime.error_response import (
    RuntimeErrorResponse
)


def test_runtime_error_response():

    trace_id = (
        "SAM-test-error-trace"
    )

    result = RuntimeErrorResponse.build(
        trace_id=trace_id,
        error_code=(
            "VISION_RUNTIME_UNAVAILABLE"
        ),
        message=(
            "Unable to connect to Vision Runtime"
        ),
        stage="vision_runtime",
        failed_step="Vision Runtime",
        source_type="image",
    )

    print(
        "\nGOVERNED RUNTIME ERROR\n"
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    assert (
        result["schema_version"]
        == "1.0.0"
    )

    assert (
        result["trace_id"]
        == trace_id
    )

    assert (
        result["status"]
        == "FAILED"
    )

    assert (
        result["error"]["code"]
        == "VISION_RUNTIME_UNAVAILABLE"
    )

    assert (
        result["processing_trace"]["status"]
        == "FAILED"
    )

    assert (
        result["downstream"][
            "ready_for_processing"
        ]
        is False
    )