from pathlib import Path

from dotenv import load_dotenv

from analysis.vision_runtime_client import VisionRuntimeClient


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


def test_vision_runtime():

    client = VisionRuntimeClient()

    image_path = BASE_DIR / "tests" / "ship3.jpeg"

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    result = client.analyze_image(
        image_bytes=image_bytes,
        filename="test_ship.jpeg",
        content_type="image/jpeg",
        return_explainable_image=False
    )

    print("\nVision Runtime Response")
    print(result)

    assert "replay_id" in result
    assert "detections" in result
    assert "ocr_results" in result