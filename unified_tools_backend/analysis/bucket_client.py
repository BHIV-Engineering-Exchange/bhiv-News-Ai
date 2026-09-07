import os
import uuid
import logging
import json
import re
from threading import Lock

import requests


logger = logging.getLogger(__name__)


class BucketClient:

    _trace_to_artifact = {}
    _lock = Lock()
    _trace_id_pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")

    def __init__(self):
        self.base_url = os.getenv("BUCKET_URL")
        self._last_response_hash = None

        if not self.base_url:
            raise RuntimeError(
                "BUCKET_URL is not configured."
            )

    def get_latest_hash(self):
        """
        Fetch the latest hash from Bucket.

        Returns:
            str | None:
                Latest Bucket hash when available.
                None when Bucket reports no latest hash or
                the endpoint cannot be reached.
        """

        try:
            response = requests.get(
                f"{self.base_url}/bucket/latest-hash",
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            latest_hash = data.get("last_hash")

            logger.info(
                "Bucket latest hash: %s",
                latest_hash
            )

            return latest_hash

        except Exception as exc:
            logger.warning(
                "Unable to fetch latest bucket hash: %s",
                exc
            )

            return None

    def get_artifact(self, trace_id: str):
        """
        Fetch an artifact from Bucket by trace_id.

        Returns:
            dict | None:
                Stored artifact when found.
                None when Bucket reports an error or artifact is not found.
        """

        if (
            not isinstance(trace_id, str)
            or not self._trace_id_pattern.fullmatch(trace_id.strip())
        ):
            return None

        trace_id = trace_id.strip()
        with self._lock:
            mapped_artifact_id = self._trace_to_artifact.get(trace_id)

        if mapped_artifact_id:
            try:
                response = requests.get(
                    f"{self.base_url}/bucket/artifact/{mapped_artifact_id}",
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()
                    if not isinstance(data, dict):
                        raise ValueError("Bucket artifact response must be an object")

                    logger.info(
                        "Successfully retrieved artifact for id %s "
                        "(trace_id: %s)",
                        mapped_artifact_id,
                        trace_id
                    )

                    return data

                if response.status_code != 404:
                    response.raise_for_status()

            except Exception as exc:
                logger.warning(
                    "Unable to fetch artifact from Bucket for id %s: %s",
                    mapped_artifact_id,
                    exc
                )

        try:
            response = requests.get(
                f"{self.base_url}/bucket/artifacts",
                params={"trace_id": trace_id},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            logger.warning(
                "Unable to query Bucket artifacts for trace_id %s: %s",
                trace_id,
                exc,
            )
            return None

        if not isinstance(data, dict) or not isinstance(data.get("artifacts"), list):
            logger.warning(
                "Bucket artifact query returned a malformed response for trace_id %s",
                trace_id,
            )
            return None

        matches = [
            artifact
            for artifact in data["artifacts"]
            if (
                isinstance(artifact, dict)
                and artifact.get("trace_id") == trace_id
                and isinstance(artifact.get("artifact_id"), str)
                and artifact["artifact_id"]
            )
        ]
        if not matches:
            logger.info(
                "Artifact with trace_id %s not found in Bucket.",
                trace_id,
            )
            return None

        selected_artifact = max(
            matches,
            key=lambda artifact: (
                artifact.get("timestamp_utc") or "",
                artifact["artifact_id"],
            ),
        )
        artifact_id = selected_artifact["artifact_id"]

        try:
            response = requests.get(
                f"{self.base_url}/bucket/artifact/{artifact_id}",
                timeout=15,
            )
            response.raise_for_status()
            artifact = response.json()
            if not isinstance(artifact, dict):
                raise ValueError("Bucket artifact response must be an object")
        except Exception as exc:
            logger.warning(
                "Unable to fetch artifact from Bucket for id %s: %s",
                artifact_id,
                exc,
            )
            return None

        with self._lock:
            self._trace_to_artifact[trace_id] = artifact_id

        logger.info(
            "Successfully retrieved artifact for id %s (trace_id: %s)",
            artifact_id,
            trace_id,
        )
        return artifact

    def _resolve_parent_hash(self):
        """
        Determine the parent hash for the next artifact.

        Priority:

        1. Bucket /latest-hash value, if available.
        2. Hash returned by the previous successful /artifact call.
        3. None for the first artifact.

        Important:
        The hash returned by /artifact represents the newly
        created artifact and becomes the parent_hash for the
        next artifact.
        """

        latest_hash = self.get_latest_hash()

        if latest_hash:
            logger.info(
                "Using Bucket latest hash as parent_hash: %s",
                latest_hash
            )

            return latest_hash

        if self._last_response_hash:
            logger.info(
                "Bucket latest hash is null. "
                "Using previous artifact hash as parent_hash: %s",
                self._last_response_hash
            )

            return self._last_response_hash

        logger.info(
            "Bucket latest hash is null and no previous artifact "
            "hash exists. Using parent_hash=null for first artifact."
        )

        return None

    def store_artifact(
        self,
        canonical_intelligence: dict
    ):
        """
        Store canonical intelligence in Bucket.

        Parent-hash behavior:

        First artifact:
            parent_hash = None

        Subsequent artifact:
            parent_hash = hash returned by the previous
            successful /artifact request, unless
            /latest-hash provides a valid hash.

        The hash generated by Bucket for the current artifact
        is stored locally and becomes the parent_hash for the
        next artifact when /latest-hash returns null.
        """

        parent_hash = self._resolve_parent_hash()

        artifact_id = str(uuid.uuid4())

        trace_id = canonical_intelligence.get("trace_id")

        bucket_payload = {
            "artifact_id": artifact_id,

            "trace_id": trace_id,

            "timestamp_utc": (
                canonical_intelligence.get("timestamp")
            ),

            "schema_version": (
                canonical_intelligence.get("schema_version")
            ),

            "source_module_id": "samachar",

            "artifact_type": "canonical_intelligence",

            "parent_hash": parent_hash,

            "payload": canonical_intelligence,
        }

        logger.info(
            "Storing artifact in Bucket. "
            "parent_hash=%s artifact_id=%s trace_id=%s",
            parent_hash,
            artifact_id,
            trace_id
        )

        # --------------------------------------------------
        # Diagnostic: calculate serialized payload size.
        #
        # This helps determine whether Bucket is rejecting
        # large canonical artifacts.
        # --------------------------------------------------

        try:
            serialized_payload = json.dumps(
                bucket_payload,
                ensure_ascii=False,
                default=str
            )

            payload_size_bytes = len(
                serialized_payload.encode("utf-8")
            )

            logger.info(
                "Bucket artifact payload size: %.2f MB",
                payload_size_bytes / (1024 * 1024)
            )

        except Exception as exc:
            logger.warning(
                "Unable to calculate Bucket payload size: %s",
                exc
            )

        # --------------------------------------------------
        # Send artifact to Bucket.
        # --------------------------------------------------

        try:
            response = requests.post(
                f"{self.base_url}/bucket/artifact",
                json=bucket_payload,
                timeout=30
            )

        except requests.exceptions.RequestException as exc:
            logger.error(
                "Bucket request failed before receiving a response: %s",
                exc
            )
            raise

        # --------------------------------------------------
        # IMPORTANT:
        # Capture the actual Bucket response body when the
        # server rejects the artifact.
        #
        # Previously raise_for_status() only exposed:
        # "400 Client Error: Bad Request"
        #
        # The response body may contain the actual contract
        # validation error.
        # --------------------------------------------------

        if not response.ok:

            logger.error(
                "Bucket rejected artifact. "
                "status=%s response=%s",
                response.status_code,
                response.text
            )

            raise requests.HTTPError(
                (
                    f"Bucket returned {response.status_code}: "
                    f"{response.text}"
                ),
                response=response
            )

        # --------------------------------------------------
        # Parse successful response.
        # --------------------------------------------------

        try:
            resp_json = response.json()

        except ValueError as exc:
            logger.error(
                "Bucket returned a successful HTTP status but "
                "invalid JSON response: %s",
                exc
            )

            raise RuntimeError(
                "Bucket returned an invalid JSON response."
            ) from exc

        # --------------------------------------------------
        # IMPORTANT:
        # Only update trace_id -> artifact_id AFTER Bucket
        # successfully stores the artifact.
        # --------------------------------------------------

        if isinstance(resp_json, dict):

            resp_artifact_id = resp_json.get("artifact_id")

            successful_artifact_id = (
                resp_artifact_id
                or artifact_id
            )

            if trace_id:
                with self._lock:
                    self._trace_to_artifact[
                        trace_id
                    ] = successful_artifact_id

            generated_hash = resp_json.get("hash")

            if generated_hash:

                self._last_response_hash = generated_hash

                logger.info(
                    "Bucket generated artifact hash: %s",
                    generated_hash
                )

            else:

                logger.warning(
                    "Bucket artifact response did not contain "
                    "a generated hash."
                )

        logger.info(
            "Artifact stored successfully in Bucket."
        )

        return resp_json