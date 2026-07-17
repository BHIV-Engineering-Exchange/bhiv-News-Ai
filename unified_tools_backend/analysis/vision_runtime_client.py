import os
import requests


class VisionRuntimeClient:
    """
    Client responsible for invoking the external
    BHIV Vision Intelligence Runtime.

    This client does not perform:
    - Image preprocessing
    - Object detection
    - OCR
    - Vessel classification
    - Maritime reasoning

    All vision processing is owned by the Vision Runtime.
    """

    def __init__(self):
        self.base_url = os.getenv(
            "VISION_RUNTIME_URL",
            ""
        ).rstrip("/")

        if not self.base_url:
            raise ValueError(
                "VISION_RUNTIME_URL environment variable is not configured"
            )

    def health_check(self) -> dict:
        """
        Checks whether the Vision Runtime is reachable.
        """

        try:
            response = requests.get(
                self.base_url,
                timeout=10
            )

            response.raise_for_status()

            return response.json()

        except requests.Timeout as exc:
            raise RuntimeError(
                "Vision Runtime health check timed out"
            ) from exc

        except requests.ConnectionError as exc:
            raise RuntimeError(
                "Unable to connect to Vision Runtime"
            ) from exc

        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Vision Runtime health check failed "
                f"with status {response.status_code}"
            ) from exc

    def analyze_image(
        self,
        image_bytes: bytes,
        filename: str,
        content_type: str = "image/jpeg",
        return_explainable_image: bool = False
    ) -> dict:
        """
        Sends an image to the Vision Runtime.

        Vision Runtime endpoint:
        POST /api/v1/analyze
        """

        if not image_bytes:
            raise ValueError(
                "Image content cannot be empty"
            )

        files = {
            "file": (
                filename,
                image_bytes,
                content_type
            )
        }
        #
        params = {
            "return_explainable_image": str(
                return_explainable_image
            ).lower()
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/analyze",
                params=params,
                files=files,
                #data=data,
                timeout=120
            )

            # print(response.status_code)
            # print(response.text)
            
            response.raise_for_status()

            vision_response = response.json()

            self._validate_response(
                vision_response
            )

            return vision_response

        except requests.Timeout as exc:
            raise RuntimeError(
                "Vision Runtime request timed out"
            ) from exc

        except requests.ConnectionError as exc:
            raise RuntimeError(
                "Unable to connect to Vision Runtime"
            ) from exc

        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Vision Runtime returned HTTP "
                f"{response.status_code}"
            ) from exc

        except requests.JSONDecodeError as exc:
            raise RuntimeError(
                "Vision Runtime returned invalid JSON"
            ) from exc

    def _validate_response(
        self,
        response: dict
    ) -> None:
        """
        Validates the minimum agreed Vision Runtime contract.
        """

        required_fields = [
            "replay_id",
            "detections",
            "ocr_results"
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in response
        ]

        if missing_fields:
            raise RuntimeError(
                "Vision Runtime contract violation. "
                f"Missing fields: {missing_fields}"
            )