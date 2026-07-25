from datetime import datetime, timezone
import hashlib
import json
import uuid

from runtime.replay_store import ReplayStore

class SatelliteIntelligenceService:
    """
    Samachar future satellite feed ingestion interface.

    This service accepts satellite feed metadata and
    creates a canonical ingestion envelope.

    It does NOT perform:
    - satellite image processing
    - object detection
    - vessel detection
    - maritime reasoning
    - sensor fusion

    Vision Runtime invocation can be added when the
    production satellite feed supplies an image payload
    through an agreed interface.
    """

    SCHEMA_VERSION = "1.0.0"

    def process(
        self,
        feed_id: str,
        timestamp_utc: str,
        image_reference: str = None,
        metadata: dict = None,
    ) -> dict:
        """
        Process a satellite feed reference and metadata.
        """

        if not isinstance(feed_id, str):
            raise ValueError(
                "Satellite feed_id must be a string"
            )

        clean_feed_id = feed_id.strip()

        if not clean_feed_id:
            raise ValueError(
                "Satellite feed_id cannot be empty"
            )

        if not isinstance(timestamp_utc, str):
            raise ValueError(
                "Satellite timestamp_utc must be a string"
            )

        clean_timestamp = timestamp_utc.strip()

        if not clean_timestamp:
            raise ValueError(
                "Satellite timestamp_utc cannot be empty"
            )

        self._validate_timestamp(
            clean_timestamp
        )

        clean_image_reference = (
            str(image_reference).strip()
            if image_reference
            else None
        )

        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError(
                "Satellite metadata must be an object"
            )

        clean_metadata = metadata or {}

        fingerprint_payload = {
            "feed_id": clean_feed_id,
            "timestamp_utc": clean_timestamp,
            "image_reference": clean_image_reference,
            "metadata": clean_metadata,
        }

        serialized_payload = json.dumps(
            fingerprint_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        input_fingerprint = (
            "sha256:"
            + hashlib.sha256(
                serialized_payload.encode("utf-8")
            ).hexdigest()
        )

        replay_record = ReplayStore.get(input_fingerprint)

        if replay_record is not None:
            replay_result = replay_record["result"]

            replay_result["replay"] = {
                "status": "HIT",
                "input_fingerprint": (
                    input_fingerprint
                ),
                "original_trace_id": (
                    replay_record["trace_id"]
                ),
            }

            return replay_result
        
        trace_id = (f"SAM-{uuid.uuid4()}")

        ingestion_timestamp = (datetime.now(timezone.utc).isoformat())

        canonical_intelligence =  {
            "schema_version": self.SCHEMA_VERSION,
            "trace_id": trace_id,
            "timestamp": ingestion_timestamp,
            "source": {
                "input_type": "satellite_feed",
                "source_system": "samachar",
                "feed_id": clean_feed_id,
                "source_timestamp_utc": clean_timestamp,
                "image_reference": clean_image_reference,
            },
            "provenance": {
                "origin": "satellite_feed",
                "processed_by": [
                    "samachar",
                ],
                "vision_runtime_invoked": False,
                "vision_replay_id": None,
                "input_fingerprint": (
                    input_fingerprint
                ),
                "normalization": {
                    "feed_id_trimmed": feed_id != clean_feed_id,
                    "timestamp_trimmed": timestamp_utc != clean_timestamp,
                    "image_reference_normalized": (
                        image_reference != clean_image_reference
                    ),
                },
            },
            "satellite_feed": {
                "feed_id": clean_feed_id,
                "timestamp_utc": clean_timestamp,
                "image_reference": clean_image_reference,
                "metadata": clean_metadata,
            },
            "processing_trace": {
                "status": "SUCCESS",
                "steps": [
                    "Satellite Feed Ingestion",
                    "Feed Validation",
                    "Provenance Capture",
                    "Canonical Mapping",
                ],
            },
            "downstream": {
                "target_system": "svacs",
                "ready_for_processing": True,
            },
            "replay": {
                "status": "MISS",
                "input_fingerprint": (
                    input_fingerprint
                ),
                "original_trace_id": (
                    trace_id
                ),
            },
            "integration_status": {
                "feed_interface": "AVAILABLE",
                "vision_processing": "NOT_INVOKED",
                "production_feed_adapter": "PENDING_CONTRACT",
                "classification": "NOT_APPLICABLE",
            },
            "errors": [],
        }

        ReplayStore.save(
            input_fingerprint=input_fingerprint,
            trace_id=trace_id,
            input_type="satellite_feed",
            schema_version=self.SCHEMA_VERSION,
            result=canonical_intelligence,
        )

        return canonical_intelligence

    def _validate_timestamp(self,timestamp_utc: str):
        """
        Validate ISO-8601 satellite source timestamp.
        """

        normalized_timestamp = (
            timestamp_utc.replace(
                "Z",
                "+00:00"
            )
        )

        try:
            parsed_timestamp = (
                datetime.fromisoformat(
                    normalized_timestamp
                )
            )

        except ValueError as exc:
            raise ValueError(
                "Satellite timestamp_utc must use "
                "ISO-8601 format"
            ) from exc

        if parsed_timestamp.tzinfo is None:
            raise ValueError(
                "Satellite timestamp_utc must include "
                "timezone information"
            )
