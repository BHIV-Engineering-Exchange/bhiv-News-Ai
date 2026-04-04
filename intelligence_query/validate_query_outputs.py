"""Deterministic validator for query engine outputs.

Usage:
  python validate_query_outputs.py

Optional flags:
  --registry demo
  --queries sample_queries.json
  --expected sample_outputs.json
  --base-dir .
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from typing import Any, Dict, List, Tuple

from query_engine import run_queries_file

ALLOWED_ROUTES = {"samachar", "guptachar"}
EXPECTED_RESULT_KEYS = [
    "event_id",
    "geo",
    "timestamp",
    "truth_level",
    "conflict_flag",
    "signal_type",
    "is_sensitive",
    "route",
]
EXPECTED_OUTPUT_KEYS = [
    "query",
    "results",
    "signals",
    "summary",
    "route",
    "tts_text",
]


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _route_expected(is_sensitive: Any, truth_level: Any) -> str:
    sensitive = bool(is_sensitive)
    try:
        truth = int(truth_level)
    except (TypeError, ValueError):
        truth = 99
    if sensitive or truth <= 1:
        return "guptachar"
    return "samachar"


def _validate_output_object(output: Dict[str, Any], idx: int) -> List[str]:
    errors: List[str] = []

    if sorted(output.keys()) != sorted(EXPECTED_OUTPUT_KEYS):
        errors.append(f"output[{idx}] keys mismatch: {sorted(output.keys())}")

    route = output.get("route")
    if route not in ALLOWED_ROUTES:
        errors.append(f"output[{idx}] invalid route: {route}")

    results = output.get("results")
    signals = output.get("signals")

    if not isinstance(results, list):
        errors.append(f"output[{idx}].results must be list")
        return errors
    if not isinstance(signals, list):
        errors.append(f"output[{idx}].signals must be list")
        return errors

    result_event_ids = []
    any_guptachar = False

    for ridx, result in enumerate(results):
        if not isinstance(result, dict):
            errors.append(f"output[{idx}].results[{ridx}] must be object")
            continue

        if sorted(result.keys()) != sorted(EXPECTED_RESULT_KEYS):
            errors.append(
                f"output[{idx}].results[{ridx}] keys mismatch: {sorted(result.keys())}"
            )

        if result.get("route") not in ALLOWED_ROUTES:
            errors.append(
                f"output[{idx}].results[{ridx}] invalid route: {result.get('route')}"
            )

        expected_route = _route_expected(result.get("is_sensitive"), result.get("truth_level"))
        if result.get("route") != expected_route:
            errors.append(
                "output[%d].results[%d] route mismatch: got=%s expected=%s"
                % (idx, ridx, result.get("route"), expected_route)
            )

        if result.get("route") == "guptachar":
            any_guptachar = True

        event_id = result.get("event_id")
        if isinstance(event_id, str):
            result_event_ids.append(event_id)

    expected_overall_route = "guptachar" if any_guptachar else "samachar"
    if route != expected_overall_route:
        errors.append(
            f"output[{idx}] overall route mismatch: got={route} expected={expected_overall_route}"
        )

    signal_event_ids = []
    for sidx, signal in enumerate(signals):
        if not isinstance(signal, dict):
            errors.append(f"output[{idx}].signals[{sidx}] must be object")
            continue
        event_id = signal.get("event_id")
        if isinstance(event_id, str):
            signal_event_ids.append(event_id)

    if sorted(result_event_ids) != sorted(signal_event_ids):
        errors.append(
            "output[%d] signal/result event_id mismatch: results=%s signals=%s"
            % (idx, sorted(result_event_ids), sorted(signal_event_ids))
        )

    return errors


def validate_expected_file(expected_path: str) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not os.path.exists(expected_path):
        return False, [f"expected output not found: {expected_path}"]

    with open(expected_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        return False, ["expected payload must be JSON object"]

    if "registry" not in payload or "outputs" not in payload:
        return False, ["expected payload must contain registry and outputs"]

    outputs = payload.get("outputs")
    if not isinstance(outputs, list):
        return False, ["expected outputs must be a list"]

    for idx, output in enumerate(outputs):
        if not isinstance(output, dict):
            errors.append(f"output[{idx}] must be object")
            continue
        errors.extend(_validate_output_object(output, idx))

    return len(errors) == 0, errors


def verify_determinism(
    registry: str,
    queries_path: str,
    expected_path: str,
    base_dir: str,
) -> Tuple[bool, str, str]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp_path = tmp.name

    try:
        run_queries_file(
            registry=registry,
            queries_path=queries_path,
            output_path=tmp_path,
            base_dir=base_dir,
        )
        expected_hash = _sha256_file(expected_path)
        actual_hash = _sha256_file(tmp_path)
        return expected_hash == actual_hash, expected_hash, actual_hash
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def main() -> int:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="Validate deterministic query output")
    parser.add_argument("--registry", default="demo")
    parser.add_argument("--queries", default=os.path.join(script_dir, "fixtures", "sample_queries.json"))
    parser.add_argument("--expected", default=os.path.join(script_dir, "fixtures", "sample_outputs.json"))
    parser.add_argument("--base-dir", default=os.path.join(script_dir, "data"))
    args = parser.parse_args()

    valid, errors = validate_expected_file(args.expected)
    if not valid:
        print("VALIDATION: FAIL")
        for err in errors:
            print(f" - {err}")
        return 1

    deterministic, expected_hash, actual_hash = verify_determinism(
        registry=args.registry,
        queries_path=args.queries,
        expected_path=args.expected,
        base_dir=args.base_dir,
    )

    if not deterministic:
        print("VALIDATION: FAIL")
        print(f" - deterministic hash mismatch")
        print(f" - expected: {expected_hash}")
        print(f" - actual:   {actual_hash}")
        return 1

    print("VALIDATION: PASS")
    print(f" - schema/logic checks: OK")
    print(f" - deterministic hash:  {expected_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
