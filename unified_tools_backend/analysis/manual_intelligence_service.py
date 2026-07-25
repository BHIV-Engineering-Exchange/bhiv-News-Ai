from datetime import datetime, timezone
import hashlib
import uuid

from analysis.news_intelligence_service import(NewsIntelligenceService)
from runtime.replay_store import ReplayStore

class ManualIntelligenceService:
    """
    Handles operator-submitted manual intelligence.

    This service:
    - accepts manual text intelligence
    - generates a Samachar trace ID
    - preserves source provenance
    - invokes the existing Samachar intelligence engine
    - returns canonical structured intelligence

    Vision Runtime is NOT invoked for manual input.
    """

    SCHEMA_VERSION = "1.0.0"

    def __init__(self):
        self.intelligence_service = (
            NewsIntelligenceService()
        )

    def process(self,content: str,source: str = "operator") -> dict:
        """
        Process manual operator intelligence.
        """

        if not isinstance(content, str):
            raise ValueError(
                "Manual intelligence content must be a string"
            )

        clean_content = content.strip()

        if not clean_content:
            raise ValueError(
                "Manual intelligence content cannot be empty"
            )

        clean_source = (
            str(source).strip()
            if source
            else "operator"
        )

        input_fingerprint = (
            "sha256:"
            + hashlib.sha256(
                clean_content.encode("utf-8")
            ).hexdigest()
        )

        replay_record = ReplayStore.get(input_fingerprint)

        if replay_record is not None:
            replay_result = replay_record["result"]

            replay_result["replay"] = {
                "status": "HIT",
                "input_fingerprint": input_fingerprint,
                "original_trace_id": (
                    replay_record["trace_id"]
                ),
            }

            return replay_result

        trace_id = (
            f"SAM-{uuid.uuid4()}"
        )

        timestamp = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        intelligence_input = {
            "title": "",
            "content": clean_content,
            "publication_date": "",
        }

        intelligence_result = (
            self.intelligence_service.process(
                intelligence_input,
                scraping_time=0,
            )
        )

        canonical_intelligence = {
            "schema_version": self.SCHEMA_VERSION,
            "trace_id": trace_id,
            "timestamp": timestamp,
            "source": {
                "input_type": "manual",
                "source_system": "samachar",
                "submitted_by": clean_source,
            },
            "provenance": {
                "origin": "operator_manual",
                "processed_by": [
                    "samachar",
                ],
                "vision_runtime_invoked": False,
                "vision_replay_id": None,
                "input_fingerprint": (
                    input_fingerprint
                ),
                "normalization": {
                    "content_trimmed": content != clean_content,
                    "source_normalized": source != clean_source,
                },
            },
            "intelligence": intelligence_result,
            "processing_trace": {
                "status": "SUCCESS",
                "steps": [
                    "Manual Ingestion",
                    "Samachar Intelligence",
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
                "original_trace_id": trace_id,
            },
            "errors": [],
        }

        ReplayStore.save(
            input_fingerprint=input_fingerprint,
            trace_id=trace_id,
            input_type="manual",
            schema_version=self.SCHEMA_VERSION,
            result=canonical_intelligence,
        )

        return canonical_intelligence
