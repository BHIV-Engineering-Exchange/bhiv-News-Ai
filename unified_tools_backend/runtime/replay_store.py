import copy
from datetime import datetime, timezone
from threading import Lock


class ReplayStore:
    """
    Thread-safe in-memory replay store for Samachar.

    Maps deterministic input fingerprints to their
    original canonical intelligence result.

    Current implementation is runtime-scoped.
    Persistent replay storage can replace this adapter
    without changing ingestion service contracts.
    """

    _records = {}
    _lock = Lock()

    @classmethod
    def get(
        cls,
        input_fingerprint: str
    ):
        """
        Return the previously stored canonical result
        for an input fingerprint.
        """

        if not input_fingerprint:
            return None

        with cls._lock:
            record = cls._records.get(
                input_fingerprint
            )

            if record is None:
                return None

            return copy.deepcopy(record)

    @classmethod
    def save(
        cls,
        input_fingerprint: str,
        trace_id: str,
        input_type: str,
        schema_version: str,
        result: dict,
    ) -> dict:
        """
        Save the original canonical result.

        Existing fingerprint records are never
        overwritten.
        """

        if not input_fingerprint:
            raise ValueError(
                "Replay input fingerprint is required"
            )

        if not trace_id:
            raise ValueError(
                "Replay trace_id is required"
            )

        if not isinstance(result, dict):
            raise ValueError(
                "Replay result must be a dictionary"
            )

        with cls._lock:

            existing_record = cls._records.get(
                input_fingerprint
            )

            if existing_record is not None:
                return copy.deepcopy(
                    existing_record
                )

            record = {
                "input_fingerprint": (
                    input_fingerprint
                ),
                "trace_id": trace_id,
                "input_type": input_type,
                "schema_version": schema_version,
                "created_at": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
                "result": copy.deepcopy(result),
            }

            cls._records[
                input_fingerprint
            ] = record

            return copy.deepcopy(record)

    @classmethod
    def count(cls) -> int:
        """
        Return the number of replay records.
        """

        with cls._lock:
            return len(cls._records)

    @classmethod
    def clear(cls):
        """
        Clear runtime replay records.

        Intended for tests only.
        """

        with cls._lock:
            cls._records.clear()