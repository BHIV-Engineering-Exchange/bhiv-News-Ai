from datetime import datetime, timezone
import hashlib
import uuid

from analysis.news_intelligence_service import NewsIntelligenceService
from analysis.text_chunker import TextChunker
from runtime.replay_store import ReplayStore


class ManualIntelligenceService:
    """
    Handles operator-submitted manual intelligence.

    This service:
    - accepts manual text intelligence
    - generates a Samachar trace ID
    - preserves source provenance
    - invokes the existing Samachar intelligence engine
    - safely processes large text using bounded chunks
    - returns canonical structured intelligence

    Vision Runtime is NOT invoked for manual input.
    """

    SCHEMA_VERSION = "1.0.0"

    # Keep NLP input safely below spaCy's default 1,000,000
    # character limit.
    NLP_CHUNK_THRESHOLD = 900_000

    # Process large documents sequentially in bounded chunks.
    NLP_CHUNK_SIZE = 50_000

    # Small overlap helps prevent entities from being lost
    # when they occur across chunk boundaries.
    NLP_CHUNK_OVERLAP = 500

    def __init__(self):
        self.intelligence_service = NewsIntelligenceService()

    def _process_intelligence_text(self, content: str) -> dict:
        """
        Process intelligence safely for both normal and large inputs.

        Small inputs:
            Process normally using the existing intelligence engine.

        Large inputs:
            Split into bounded chunks and process sequentially.
            This prevents a huge document from being passed to
            spaCy/NER in a single operation.
        """
        print(
            f"[SAMACHAR CHUNK DEBUG] Incoming intelligence text: "
            f"{len(content)} characters"
        )

        if len(content) <= self.NLP_CHUNK_THRESHOLD:
            intelligence_input = {
                "title": "",
                "content": content,
                "publication_date": "",
            }

            return self.intelligence_service.process(
                intelligence_input,
                scraping_time=0,
            )

        chunk_results = []

        for chunk in TextChunker.chunks(
            content,
            chunk_size=self.NLP_CHUNK_SIZE,
            overlap=self.NLP_CHUNK_OVERLAP,
        ):
            print(
                f"[SAMACHAR CHUNK DEBUG] Processing chunk: "
                f"{len(chunk)} characters"
            )
            intelligence_input = {
                "title": "",
                "content": chunk,
                "publication_date": "",
            }

            result = self.intelligence_service.process(
                intelligence_input,
                scraping_time=0,
            )

            chunk_results.append(result)

        return self._aggregate_results(chunk_results)

    def _aggregate_results(self, results: list) -> dict:
        """
        Aggregate intelligence results produced from multiple chunks.

        The NewsIntelligenceService returns:

        validated_entities
        classification
        evidence
        confidence
        processing_trace
        rejected_entities

        Entity lists are merged and deduplicated.

        Classification, evidence and confidence are preserved
        from the first successful chunk and supplemented with
        chunk-processing metadata.
        """

        if not results:
            return {
                "validated_entities": {
                    "names": [],
                    "organizations": [],
                    "locations": [],
                    "dates": [],
                },
                "classification": {},
                "evidence": [],
                "confidence": {},
                "processing_trace": {
                    "status": "SUCCESS",
                    "steps": [],
                    "processing_time": {},
                },
                "rejected_entities": [],
            }

        if len(results) == 1:
            result = results[0]

            result["processing_trace"] = {
                **result.get("processing_trace", {}),
                "chunk_processing": {
                    "enabled": False,
                    "chunk_count": 1,
                    "chunk_size": self.NLP_CHUNK_SIZE,
                    "chunk_overlap": self.NLP_CHUNK_OVERLAP,
                },
            }

            return result

        # --------------------------------------------------
        # Entity aggregation
        # --------------------------------------------------

        entity_fields = [
            "names",
            "organizations",
            "locations",
            "dates",
        ]

        aggregated_entities = {
            "names": [],
            "organizations": [],
            "locations": [],
            "dates": [],
        }

        for result in results:
            validated_entities = result.get(
                "validated_entities",
                {},
            )

            for field in entity_fields:
                values = validated_entities.get(field, [])

                if isinstance(values, list):
                    aggregated_entities[field].extend(values)

        # Deduplicate while preserving original order.
        for field in entity_fields:
            seen = set()
            unique_values = []

            for value in aggregated_entities[field]:
                try:
                    marker = repr(value)

                    if marker not in seen:
                        seen.add(marker)
                        unique_values.append(value)

                except Exception:
                    unique_values.append(value)

            aggregated_entities[field] = unique_values

        # --------------------------------------------------
        # Rejected entity aggregation
        # --------------------------------------------------

        rejected_entities = []

        for result in results:
            values = result.get(
                "rejected_entities",
                [],
            )

            if isinstance(values, list):
                rejected_entities.extend(values)

        seen_rejected = set()
        unique_rejected = []

        for value in rejected_entities:
            try:
                marker = repr(value)

                if marker not in seen_rejected:
                    seen_rejected.add(marker)
                    unique_rejected.append(value)

            except Exception:
                unique_rejected.append(value)

        # --------------------------------------------------
        # Evidence aggregation
        # --------------------------------------------------

        evidence = []

        for result in results:
            chunk_evidence = result.get(
                "evidence",
                [],
            )

            if isinstance(chunk_evidence, list):
                evidence.extend(chunk_evidence)
            elif chunk_evidence:
                evidence.append(chunk_evidence)

        # Deduplicate evidence while preserving order.
        seen_evidence = set()
        unique_evidence = []

        for item in evidence:
            try:
                marker = repr(item)

                if marker not in seen_evidence:
                    seen_evidence.add(marker)
                    unique_evidence.append(item)

            except Exception:
                unique_evidence.append(item)

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        classifications = []

        for result in results:
            classification = result.get(
                "classification"
            )

            if classification:
                classifications.append(classification)

        if classifications:
            primary_classification = classifications[0]
        else:
            primary_classification = {}

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidences = []

        for result in results:
            confidence = result.get(
                "confidence"
            )

            if confidence:
                confidences.append(confidence)

        if confidences:
            primary_confidence = confidences[0]
        else:
            primary_confidence = {}

        # --------------------------------------------------
        # Processing trace
        # --------------------------------------------------

        processing_times = {}

        for result in results:
            trace = result.get(
                "processing_trace",
                {},
            )

            times = trace.get(
                "processing_time",
                {}
            )

            if isinstance(times, dict):
                for key, value in times.items():
                    if isinstance(value, (int, float)):
                        processing_times[key] = (
                            processing_times.get(key, 0)
                            + value
                        )

        processing_trace = {
            "status": "SUCCESS",
            "steps": [
                "Large Text Chunking",
                "Entity Extraction",
                "Validation",
                "Classification",
                "Evidence",
                "Confidence",
            ],
            "processing_time": processing_times,
            "chunk_processing": {
                "enabled": True,
                "chunk_count": len(results),
                "chunk_size": self.NLP_CHUNK_SIZE,
                "chunk_overlap": self.NLP_CHUNK_OVERLAP,
            },
        }

        # --------------------------------------------------
        # Final aggregated intelligence
        # --------------------------------------------------

        return {
            "validated_entities": aggregated_entities,
            "classification": primary_classification,
            "evidence": unique_evidence,
            "confidence": primary_confidence,
            "processing_trace": processing_trace,
            "rejected_entities": unique_rejected,
        }

    def process(
        self,
        content: str,
        source: str = "operator",
    ) -> dict:
        """
        Process manual/operator intelligence.
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

        # --------------------------------------------------
        # Deterministic full-input fingerprint
        # --------------------------------------------------

        input_fingerprint = (
            "sha256:"
            + hashlib.sha256(
                clean_content.encode("utf-8")
            ).hexdigest()
        )

        # --------------------------------------------------
        # Replay lookup
        # --------------------------------------------------

        replay_record = ReplayStore.get(
            input_fingerprint
        )

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

        # --------------------------------------------------
        # Generate trace
        # --------------------------------------------------

        trace_id = (
            f"SAM-{uuid.uuid4()}"
        )

        timestamp = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        # --------------------------------------------------
        # Intelligence processing
        # --------------------------------------------------

        intelligence_result = (
            self._process_intelligence_text(
                clean_content
            )
        )

        # --------------------------------------------------
        # Canonical intelligence
        # --------------------------------------------------

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
                    "content_trimmed": (
                        content != clean_content
                    ),

                    "source_normalized": (
                        source != clean_source
                    ),
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

                "large_text_processing": (
                    intelligence_result
                    .get(
                        "processing_trace",
                        {}
                    )
                    .get(
                        "chunk_processing",
                        {},
                    )
                ),
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

        # --------------------------------------------------
        # Save replay record
        # --------------------------------------------------

        ReplayStore.save(
            input_fingerprint=input_fingerprint,
            trace_id=trace_id,
            input_type="manual",
            schema_version=self.SCHEMA_VERSION,
            result=canonical_intelligence,
        )

        return canonical_intelligence