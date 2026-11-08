"""Reference implementation for the Event Stream Sessionizer benchmark."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_event(raw: str) -> dict[str, Any]:
    """Parse and validate one JSONL record; return a normalized event."""
    try:
        item = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("invalid JSON") from exc

    if not isinstance(item, dict):
        raise ValueError("event must be a JSON object")

    for field in ("event_id", "user_id", "timestamp", "event_type"):
        value = item.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")

    timestamp_text = item["timestamp"].strip()
    if timestamp_text.endswith("Z"):
        timestamp_text = timestamp_text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(timestamp_text)
    except ValueError as exc:
        raise ValueError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")

    return {
        "event_id": item["event_id"],
        "user_id": item["user_id"],
        "timestamp": parsed.astimezone(timezone.utc),
        "event_type": item["event_type"],
    }


def format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_report(events: list[dict[str, Any]], rejected: int,
                 duplicates: int, idle_minutes: int) -> dict[str, Any]:
    by_user: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        by_user.setdefault(event["user_id"], []).append(event)

    users_output = []
    total_sessions = 0
    threshold_seconds = idle_minutes * 60

    for user_id in sorted(by_user):
        user_events = sorted(
            by_user[user_id],
            key=lambda event: (event["timestamp"], event["line_number"]),
        )
        groups: list[list[dict[str, Any]]] = []
        for event in user_events:
            if not groups:
                groups.append([event])
                continue
            previous = groups[-1][-1]
            gap = (event["timestamp"] - previous["timestamp"]).total_seconds()
            if gap > threshold_seconds:
                groups.append([event])
            else:
                groups[-1].append(event)

        sessions_output = []
        for index, group in enumerate(groups, start=1):
            start = group[0]["timestamp"]
            end = group[-1]["timestamp"]
            counts = Counter(event["event_type"] for event in group)
            sessions_output.append({
                "session_index": index,
                "start": format_utc(start),
                "end": format_utc(end),
                "event_count": len(group),
                "duration_seconds": (end - start).total_seconds(),
                "event_types": {key: counts[key] for key in sorted(counts)},
            })
        total_sessions += len(sessions_output)
        users_output.append({"user_id": user_id, "sessions": sessions_output})

    return {
        "accepted_events": len(events),
        "rejected_records": rejected,
        "duplicate_records": duplicates,
        "session_count": total_sessions,
        "users": users_output,
    }


def process_file(path: Path, idle_minutes: int) -> dict[str, Any]:
    retained: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    rejected = 0
    duplicates = 0

    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                event = parse_event(raw)
            except ValueError:
                rejected += 1
                continue
            if event["event_id"] in seen_ids:
                duplicates += 1
                continue
            seen_ids.add(event["event_id"])
            event["line_number"] = line_number
            retained.append(event)

    return build_report(retained, rejected, duplicates, idle_minutes)


def positive_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize user event sessions.")
    parser.add_argument("input", help="path to a UTF-8 JSONL event file")
    parser.add_argument("--idle-minutes", type=positive_integer, default=30)
    args = parser.parse_args(argv)

    try:
        report = process_file(Path(args.input), args.idle_minutes)
    except OSError as exc:
        print(f"error: cannot read input file: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(report, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
