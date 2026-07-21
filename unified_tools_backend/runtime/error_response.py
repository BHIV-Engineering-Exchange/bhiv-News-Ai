from datetime import datetime, timezone


class RuntimeErrorResponse:
    """
    Builds governed Samachar runtime error responses.

    All operational failures are returned through a
    stable, traceable and versioned error contract.
    """

    SCHEMA_VERSION = "1.0.0"

    @classmethod
    def build(
        cls,
        trace_id: str,
        error_code: str,
        message: str,
        stage: str,
        failed_step: str,
        source_type: str = None,
    ) -> dict:

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        return {
            "schema_version": (
                cls.SCHEMA_VERSION
            ),
            "trace_id": trace_id,
            "timestamp": timestamp,
            "status": "FAILED",
            "source": {
                "input_type": source_type,
                "source_system": "samachar",
            },
            "error": {
                "code": error_code,
                "message": message,
                "stage": stage,
            },
            "processing_trace": {
                "status": "FAILED",
                "failed_step": failed_step,
            },
            "downstream": {
                "target_system": "svacs",
                "ready_for_processing": False,
            },
        }