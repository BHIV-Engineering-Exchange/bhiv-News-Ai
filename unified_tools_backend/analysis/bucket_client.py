import os
import uuid
import logging
import requests

logger = logging.getLogger(__name__)


class BucketClient:

    def __init__(self):

        self.base_url = os.getenv("BUCKET_URL")

        if not self.base_url:
            raise RuntimeError(
                "BUCKET_URL is not configured."
            )

    def get_latest_hash(self):

        try:

            response = requests.get(
                f"{self.base_url}/bucket/latest-hash",
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            return data.get("last_hash")

        except Exception as exc:

            logger.warning(
                "Unable to fetch latest bucket hash: %s",
                exc
            )

            return None

    def store_artifact(
        self,
        canonical_intelligence: dict
    ):

        parent_hash = self.get_latest_hash()

        bucket_payload = {

            "artifact_id": str(uuid.uuid4()),

            "trace_id":
                canonical_intelligence["trace_id"],

            "timestamp_utc":
                canonical_intelligence["timestamp"],

            "schema_version":
                canonical_intelligence["schema_version"],

            "source_module_id":
                "samachar",

            "artifact_type":
                "canonical_intelligence",

            "parent_hash":
                parent_hash,

            "payload":
                canonical_intelligence,
        }

        response = requests.post(
            f"{self.base_url}/bucket/artifact",
            json=bucket_payload,
            timeout=30
        )

        response.raise_for_status()

        logger.info(
            "Artifact stored successfully in Bucket."
        )

        return response.json()