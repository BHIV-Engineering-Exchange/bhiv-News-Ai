"""Deterministic intelligence retrieval engine for Samachar and Guptachar routing.

This module is intentionally standalone: no API wiring, no auth, no ingestion mutation.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

REQUIRED_RESULT_FIELDS = [
    "event_id",
    "geo",
    "timestamp",
    "truth_level",
    "conflict_flag",
    "signal_type",
    "is_sensitive",
]

SIGNAL_SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "info": 0,
}


def _safe_read_json(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if "events" in payload and isinstance(payload["events"], list):
            return [item for item in payload["events"] if isinstance(item, dict)]
        if "signals" in payload and isinstance(payload["signals"], list):
            return [item for item in payload["signals"] if isinstance(item, dict)]
    return []


def load_intel_events(registry: str, base_dir: str = ".") -> List[Dict[str, Any]]:
    """Load <registry>_intel_events.json from base_dir."""
    path = os.path.join(base_dir, f"{registry}_intel_events.json")
    return _safe_read_json(path)


def load_signals(registry: str, base_dir: str = ".") -> List[Dict[str, Any]]:
    """Load <registry>_signals.json from base_dir."""
    path = os.path.join(base_dir, f"{registry}_signals.json")
    return _safe_read_json(path)


def _normalize_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    return None


def _to_int(value: Any, default: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_time(ts: Any) -> str:
    # Keep deterministic lexicographic handling for ISO-like timestamps.
    if isinstance(ts, str):
        return ts
    return ""


def _is_complete_joined_record(record: Dict[str, Any]) -> bool:
    for field in REQUIRED_RESULT_FIELDS:
        if field not in record:
            return False
    return True


def join_events_signals(
    events: List[Dict[str, Any]],
    signals: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Join event and signal datasets by event_id and drop partial records."""
    signal_by_event_id: Dict[str, Dict[str, Any]] = {}
    for signal in signals:
        event_id = signal.get("event_id")
        if isinstance(event_id, str) and event_id:
            signal_by_event_id[event_id] = signal

    joined: List[Dict[str, Any]] = []
    for event in events:
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            continue
        signal = signal_by_event_id.get(event_id)
        if not signal:
            continue

        row = {
            "event_id": event_id,
            "geo": event.get("geo"),
            "timestamp": event.get("timestamp"),
            "truth_level": signal.get("truth_level"),
            "conflict_flag": signal.get("conflict_flag"),
            "signal_type": signal.get("signal_type"),
            "is_sensitive": signal.get("is_sensitive"),
            "summary": event.get("summary", ""),
        }

        if _is_complete_joined_record(row):
            joined.append(row)

    joined.sort(key=lambda item: (_parse_time(item.get("timestamp")), str(item.get("event_id", ""))))
    return joined


def filter_events(
    events: List[Dict[str, Any]],
    geo: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    min_truth_level: Optional[int] = None,
    signal_type: Optional[str] = None,
    conflict_flag: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """Apply deterministic filters. Missing filters are ignored."""

    out: List[Dict[str, Any]] = []
    for item in events:
        item_geo = item.get("geo")
        item_ts = _parse_time(item.get("timestamp"))
        item_truth = _to_int(item.get("truth_level"), default=-1)
        item_signal_type = str(item.get("signal_type", "")).lower()
        item_conflict = _normalize_bool(item.get("conflict_flag"))

        if geo is not None:
            if not isinstance(item_geo, str) or item_geo.lower() != str(geo).lower():
                continue

        if start_time is not None and item_ts:
            if item_ts < str(start_time):
                continue

        if end_time is not None and item_ts:
            if item_ts > str(end_time):
                continue

        if min_truth_level is not None:
            if item_truth < _to_int(min_truth_level, default=0):
                continue

        if signal_type is not None:
            if item_signal_type != str(signal_type).lower():
                continue

        if conflict_flag is not None:
            expected = _normalize_bool(conflict_flag)
            if expected is None:
                expected = bool(conflict_flag)
            if item_conflict is None or item_conflict != expected:
                continue

        out.append(item)

    out.sort(key=lambda item: (_parse_time(item.get("timestamp")), str(item.get("event_id", ""))))
    return out


def _route_for_result(item: Dict[str, Any]) -> str:
    sensitive = _normalize_bool(item.get("is_sensitive")) is True
    truth_level = _to_int(item.get("truth_level"), default=99)
    if sensitive or truth_level <= 1:
        return "guptachar"
    return "samachar"


def _highest_severity_signal(results: List[Dict[str, Any]]) -> str:
    if not results:
        return "none"

    best_signal = "none"
    best_score = -1
    for item in results:
        signal = str(item.get("signal_type", "info")).lower()
        score = SIGNAL_SEVERITY_ORDER.get(signal, -1)
        if score > best_score:
            best_signal = signal
            best_score = score
    return best_signal


def build_summary(results: List[Dict[str, Any]], query: Dict[str, Any]) -> str:
    count = len(results)
    if count == 0:
        return "0 events detected."

    geo_value = query.get("geo")
    if not geo_value:
        unique_geo = sorted({str(item.get("geo")) for item in results if item.get("geo") is not None})
        geo_fragment = ", ".join(unique_geo) if unique_geo else "multiple regions"
    else:
        geo_fragment = str(geo_value)

    highest_signal = _highest_severity_signal(results)
    conflict_count = sum(1 for item in results if _normalize_bool(item.get("conflict_flag")) is True)

    return (
        f"{count} events detected in {geo_fragment} with highest signal {highest_signal} "
        f"and {conflict_count} conflict{'s' if conflict_count != 1 else ''}."
    )


def build_response(query: Dict[str, Any], filtered_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    routed_results: List[Dict[str, Any]] = []
    overall_route = "samachar"

    for item in filtered_results:
        route = _route_for_result(item)
        if route == "guptachar":
            overall_route = "guptachar"

        routed_results.append(
            {
                "event_id": item["event_id"],
                "geo": item["geo"],
                "timestamp": item["timestamp"],
                "truth_level": item["truth_level"],
                "conflict_flag": item["conflict_flag"],
                "signal_type": item["signal_type"],
                "is_sensitive": item["is_sensitive"],
                "route": route,
            }
        )

    routed_results.sort(key=lambda item: (str(item["timestamp"]), str(item["event_id"])))

    response = {
        "query": query,
        "results": routed_results,
        "signals": [
            {
                "event_id": item["event_id"],
                "signal_type": item["signal_type"],
                "truth_level": item["truth_level"],
                "conflict_flag": item["conflict_flag"],
                "is_sensitive": item["is_sensitive"],
            }
            for item in routed_results
        ],
        "summary": build_summary(routed_results, query),
        "route": overall_route,
        "tts_text": build_summary(routed_results, query),
    }
    return response


def run_query(
    registry: str,
    query: Dict[str, Any],
    base_dir: str = ".",
) -> Dict[str, Any]:
    events = load_intel_events(registry=registry, base_dir=base_dir)
    signals = load_signals(registry=registry, base_dir=base_dir)

    joined = join_events_signals(events=events, signals=signals)

    filtered = filter_events(
        events=joined,
        geo=query.get("geo"),
        start_time=query.get("start_time"),
        end_time=query.get("end_time"),
        min_truth_level=query.get("min_truth_level"),
        signal_type=query.get("signal_type"),
        conflict_flag=query.get("conflict_flag"),
    )

    return build_response(query=query, filtered_results=filtered)


def run_queries_file(
    registry: str,
    queries_path: str,
    output_path: str,
    base_dir: str = ".",
) -> Dict[str, Any]:
    with open(queries_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    queries = payload.get("queries", []) if isinstance(payload, dict) else []
    outputs = []
    for query in queries:
        if isinstance(query, dict):
            outputs.append(run_query(registry=registry, query=query, base_dir=base_dir))

    result_payload = {"registry": registry, "outputs": outputs}
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result_payload, handle, indent=2)

    return result_payload


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    run_queries_file(
        registry="demo",
        queries_path=os.path.join(script_dir, "fixtures", "sample_queries.json"),
        output_path=os.path.join(script_dir, "fixtures", "sample_outputs.json"),
        base_dir=os.path.join(script_dir, "data"),
    )
