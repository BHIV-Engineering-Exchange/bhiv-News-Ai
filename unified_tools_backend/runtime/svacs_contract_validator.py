from datetime import datetime


class SVACSContractValidator:
    """
    Validates Samachar structured intelligence
    against the frozen SVACS v1 contract.
    """

    ALLOWED_SOURCE_TYPES = {
        "image",
        "manual",
        "satellite_feed",
    }

    ALLOWED_VESSEL_CLASSES = {
        "cargo",
        "tanker",
        "patrol",
        "fishing",
        "submarine",
        "unknown",
    }

    REQUIRED_FIELDS = {
        "trace_id",
        "source_type",
        "vessel_class",
        "confidence_score",
        "vision_confidence",
        "ocr_results",
        "visual_features",
        "dimensions_estimate",
        "ais_data",
        "timestamp_utc",
    }

    @classmethod
    def validate(
        cls,
        payload: dict
    ) -> dict:
        """
        Validate a Samachar -> SVACS payload.
        """

        errors = []

        if not isinstance(payload, dict):
            return {
                "valid": False,
                "contract_version": "1.0.0",
                "errors": [
                    "SVACS payload must be an object"
                ],
            }

        missing_fields = (
            cls.REQUIRED_FIELDS
            - set(payload.keys())
        )

        for field in sorted(missing_fields):
            errors.append(
                f"Missing required field: {field}"
            )

        if errors:
            return {
                "valid": False,
                "contract_version": "1.0.0",
                "errors": errors,
            }

        trace_id = payload.get("trace_id")

        if (
            not isinstance(trace_id, str)
            or not trace_id.startswith("SAM-")
        ):
            errors.append(
                "trace_id must be a Samachar "
                "trace identifier"
            )

        source_type = payload.get(
            "source_type"
        )

        if (
            source_type
            not in cls.ALLOWED_SOURCE_TYPES
        ):
            errors.append(
                "source_type is not supported "
                "by SVACS contract v1"
            )

        vessel_class = payload.get(
            "vessel_class"
        )

        if (
            vessel_class
            not in cls.ALLOWED_VESSEL_CLASSES
        ):
            errors.append(
                "vessel_class is outside the "
                "SVACS vessel taxonomy"
            )

        cls._validate_score(
            payload.get("confidence_score"),
            "confidence_score",
            errors,
            allow_null=False,
        )

        cls._validate_score(
            payload.get("vision_confidence"),
            "vision_confidence",
            errors,
            allow_null=True,
        )

        # Validate Vision Runtime OCR results
        ocr_results = payload.get(
            "ocr_results"
        )

        if not isinstance(ocr_results,list):
            errors.append("ocr_results must be an array")

        else:
            for index, ocr_result in enumerate(
                ocr_results
            ):

                if not isinstance(
                    ocr_result,
                    dict
                ):
                    errors.append(
                        f"ocr_results[{index}] "
                        "must be an object"
                    )

                    continue

                text = ocr_result.get(
                    "text"
                )

                confidence = ocr_result.get(
                    "confidence"
                )

                if not isinstance(
                    text,
                    str
                ):
                    errors.append(
                        f"ocr_results[{index}].text "
                        "must be a string"
                    )

                elif not text.strip():
                    errors.append(
                        f"ocr_results[{index}].text "
                        "cannot be empty"
                    )

                if (
                    not isinstance(
                        confidence,
                        (int, float)
                    )
                    or isinstance(
                        confidence,
                        bool
                    )
                ):
                    errors.append(
                        f"ocr_results[{index}].confidence "
                        "must be a number"
                    )

                elif not (
                    0.0
                    <= confidence
                    <= 1.0
                ):
                    errors.append(
                        f"ocr_results[{index}].confidence "
                        "must be between 0.0 and 1.0"
                    )

        if not isinstance(
            payload.get("visual_features"),
            list
        ):
            errors.append(
                "visual_features must be an array"
            )

        dimensions = payload.get(
            "dimensions_estimate"
        )

        if not isinstance(dimensions, dict):
            errors.append(
                "dimensions_estimate must be an object"
            )

        else:
            if "length_m" not in dimensions:
                errors.append(
                    "dimensions_estimate.length_m "
                    "is required"
                )

            if "beam_m" not in dimensions:
                errors.append(
                    "dimensions_estimate.beam_m "
                    "is required"
                )

        ais_data = payload.get("ais_data")

        if not isinstance(ais_data, dict):
            errors.append(
                "ais_data must be an object"
            )

        else:
            if "mmsi" not in ais_data:
                errors.append(
                    "ais_data.mmsi is required"
                )

            if "speed_knots" not in ais_data:
                errors.append(
                    "ais_data.speed_knots is required"
                )

        timestamp_utc = payload.get(
            "timestamp_utc"
        )

        if not cls._is_iso_timestamp(
            timestamp_utc
        ):
            errors.append(
                "timestamp_utc must be a valid "
                "ISO-8601 timestamp"
            )

        return {
            "valid": len(errors) == 0,
            "contract_version": "1.0.0",
            "errors": errors,
        }

    @staticmethod
    def _validate_score(
        value,
        field_name: str,
        errors: list,
        allow_null: bool,
    ):
        if value is None and allow_null:
            return

        if not isinstance(
            value,
            (int, float)
        ):
            errors.append(
                f"{field_name} must be numeric"
            )

            return

        if value < 0.0 or value > 1.0:
            errors.append(
                f"{field_name} must be between "
                "0.0 and 1.0"
            )

    @staticmethod
    def _is_iso_timestamp(
        value
    ) -> bool:

        if not isinstance(value, str):
            return False

        normalized_value = value.replace(
            "Z",
            "+00:00"
        )

        try:
            datetime.fromisoformat(
                normalized_value
            )

            return True

        except ValueError:
            return False