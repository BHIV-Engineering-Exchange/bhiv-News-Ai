from datetime import datetime, timezone
import hashlib
import re
import time
import uuid

from analysis.vision_runtime_client import VisionRuntimeClient
from analysis.news_intelligence_service import NewsIntelligenceService

from analysis.svacs_intelligence_mapper import (
    SVACSIntelligenceMapper
)
from runtime.replay_store import ReplayStore

class VisionIntelligenceService:
    """
    Orchestrates image-based intelligence processing.

    Flow:
    Image
        -> Vision Runtime
        -> OCR Normalization
        -> Samachar Intelligence Engine
        -> Canonical Structured Intelligence

    Vision processing remains owned by the external
    Vision Runtime.
    """

    SCHEMA_VERSION = "1.0.0"

    def __init__(self):
        self.vision_client = VisionRuntimeClient()
        self.intelligence_service = NewsIntelligenceService()
        self.svacs_mapper = SVACSIntelligenceMapper()
        
    def process(
        self,
        image_bytes: bytes,
        filename: str,
        content_type: str = "image/jpeg",
        return_explainable_image: bool = False
    ) -> dict:

        total_start = time.perf_counter()

        if not isinstance(image_bytes, bytes) or not image_bytes:
            raise ValueError("Image bytes are required")

        input_fingerprint = (
            "sha256:"
            + hashlib.sha256(
                content_type.encode("utf-8") + b":" + image_bytes
            ).hexdigest()
        )

        replay_record = ReplayStore.get(input_fingerprint)

        if replay_record is not None:
            replay_result = replay_record["result"]
            replay_result["replay"] = {
                "status": "HIT",
                "input_fingerprint": input_fingerprint,
                "original_trace_id": replay_record["trace_id"],
            }
            return replay_result

        trace_id = f"SAM-{uuid.uuid4()}"

        processing_times = {}

        # ==========================================
        # 1. Vision Runtime Invocation
        # ==========================================

        start = time.perf_counter()

        vision_result = self.vision_client.analyze_image(
            image_bytes=image_bytes,
            filename=filename,
            content_type=content_type,
            return_explainable_image=return_explainable_image
        )

        processing_times["vision_runtime"] = round(
            time.perf_counter() - start,
            3
        )

        # ==========================================
        # 2. OCR Normalization
        # ==========================================

        start = time.perf_counter()

        raw_ocr_results = vision_result.get(
            "ocr_results",
            []
        )

        normalized_ocr_results = (
            self._normalize_ocr_results(
                raw_ocr_results
            )
        )

        normalized_ocr_text = " ".join(
            item["text"]
            for item in normalized_ocr_results
        )

        processing_times["ocr_normalization"] = round(
            time.perf_counter() - start,
            3
        )

        # ==========================================
        # 3. Samachar Intelligence Processing
        # ==========================================

        intelligence = None

        if normalized_ocr_text:

            start = time.perf_counter()

            intelligence_input = {
                "title": "",
                "content": normalized_ocr_text,
                "publication_date": ""
            }

            intelligence = (
                self.intelligence_service.process(
                    intelligence_input
                )
            )

            processing_times[
                "intelligence_processing"
            ] = round(
                time.perf_counter() - start,
                3
            )

        else:

            processing_times[
                "intelligence_processing"
            ] = 0.0

        # ==========================================
        # 4. Canonical Mapping
        # ==========================================

        start = time.perf_counter()

        canonical_response = {
            "schema_version": self.SCHEMA_VERSION,

            "trace_id": trace_id,

            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "source": {
                "input_type": "image",
                "source_system": "samachar",
                "filename": filename
            },

            "provenance": {
                "origin": "operator_image",

                "processed_by": [
                    "samachar",
                    "vision_runtime"
                ],

                "vision_runtime_invoked": True,

                "vision_replay_id": (
                    vision_result.get(
                        "replay_id"
                    )
                ),
                "input_fingerprint": input_fingerprint,
                "normalization": {
                    "ocr_results_received": len(raw_ocr_results),
                    "ocr_results_normalized": len(normalized_ocr_results),
                },
            },

            "vision_intelligence": {
                "replay_id": vision_result.get(
                    "replay_id"
                ),

                "detections": vision_result.get(
                    "detections",
                    []
                ),

                # Preserve Vijay's raw OCR response
                "ocr_results": raw_ocr_results,

                # Explicit Samachar normalization
                "normalized_ocr_results": (
                    normalized_ocr_results
                ),

                "explainable_image_base64": (
                    vision_result.get(
                        "explainable_image_base64"
                    )
                )
            },

            "intelligence": intelligence,

            "processing_trace": {
                "status": "SUCCESS",

                "steps": [
                    "Image Ingestion",
                    "Vision Runtime",
                    "OCR Normalization",
                    "Samachar Intelligence",
                    "Canonical Mapping"
                ],

                "processing_time": processing_times
            },

            "downstream": {
                "target_system": "svacs",
                "ready_for_processing": True
            },

            "replay": {
                "status": "MISS",
                "input_fingerprint": input_fingerprint,
                "original_trace_id": trace_id,
            },

            "errors": []
        }

        processing_times["canonical_mapping"] = round(
            time.perf_counter() - start,
            3
        )

        processing_times["total"] = round(
            time.perf_counter() - total_start,
            3
        )

        ReplayStore.save(
            input_fingerprint=input_fingerprint,
            trace_id=trace_id,
            input_type="image",
            schema_version=self.SCHEMA_VERSION,
            result=canonical_response,
        )

        return canonical_response

    def _normalize_ocr_results(
        self,
        ocr_results: list
    ) -> list:
        """
        Creates normalized OCR input for Samachar intelligence.

        Raw Vision Runtime OCR results remain unchanged
        in the canonical response.

        Current normalization:
        - Minimum confidence threshold
        - Remove surrounding punctuation
        - Remove exact duplicate OCR text

        This method does not perform OCR.
        """

        normalized_results = []

        seen_text = set()

        minimum_confidence = 0.60

        for item in ocr_results:

            text = item.get(
                "text",
                ""
            ).strip()

            confidence = item.get(
                "confidence",
                0
            )

            if not text:
                continue

            if confidence < minimum_confidence:
                continue

            text = re.sub(
                r'^[\'"“”]+|[\'"“”]+$',
                "",
                text
            ).strip()

            if not text:
                continue

            normalized_key = text.lower()

            if normalized_key in seen_text:
                continue

            seen_text.add(
                normalized_key
            )

            normalized_results.append({
                "text": text,
                "confidence": confidence,
                "source": "vision_runtime_ocr"
            })

        return normalized_results
