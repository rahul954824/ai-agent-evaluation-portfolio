"""Public tests for the Event Stream Sessionizer benchmark."""
import json
import tempfile
import unittest
from pathlib import Path

from sessionize import parse_event, process_file


def row(event_id, user_id="u1", timestamp="2025-01-01T09:00:00Z",
        event_type="view", **extra):
    item = {
        "event_id": event_id,
        "user_id": user_id,
        "timestamp": timestamp,
        "event_type": event_type,
    }
    item.update(extra)
    return json.dumps(item)


class SessionizerTests(unittest.TestCase):
    def run_input(self, text, idle=30):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text(text, encoding="utf-8")
            return process_file(path, idle)

    def test_single_event(self):
        report = self.run_input(row("e1"))
        self.assertEqual(report["accepted_events"], 1)
        session = report["users"][0]["sessions"][0]
        self.assertEqual(session["event_count"], 1)
        self.assertEqual(session["duration_seconds"], 0.0)

    def test_exact_threshold_stays_in_session(self):
        report = self.run_input(
            row("e1", timestamp="2025-01-01T09:00:00Z") + "\n" +
            row("e2", timestamp="2025-01-01T09:30:00Z"), idle=30
        )
        self.assertEqual(report["session_count"], 1)

    def test_gap_over_threshold_starts_new_session(self):
        report = self.run_input(
            row("e1", timestamp="2025-01-01T09:00:00Z") + "\n" +
            row("e2", timestamp="2025-01-01T09:30:01Z"), idle=30
        )
        self.assertEqual(report["session_count"], 2)

    def test_out_of_order_input_is_sorted(self):
        report = self.run_input(
            row("later", timestamp="2025-01-01T09:20:00Z") + "\n" +
            row("earlier", timestamp="2025-01-01T09:00:00Z")
        )
        session = report["users"][0]["sessions"][0]
        self.assertEqual(session["start"], "2025-01-01T09:00:00Z")
        self.assertEqual(session["end"], "2025-01-01T09:20:00Z")

    def test_users_are_sorted_and_isolated(self):
        report = self.run_input(
            row("e1", user_id="z") + "\n" + row("e2", user_id="a")
        )
        self.assertEqual([u["user_id"] for u in report["users"]], ["a", "z"])
        self.assertEqual(report["session_count"], 2)

    def test_duplicate_ids_are_global_and_first_wins(self):
        report = self.run_input(
            row("same", user_id="u1") + "\n" +
            row("same", user_id="u2", timestamp="2025-01-01T12:00:00Z")
        )
        self.assertEqual(report["duplicate_records"], 1)
        self.assertEqual(report["accepted_events"], 1)
        self.assertEqual(report["users"][0]["user_id"], "u1")

    def test_bad_json_and_naive_timestamp_are_rejected(self):
        report = self.run_input(
            "{not json}\n" +
            row("bad", timestamp="2025-01-01T09:00:00") + "\n" +
            row("good")
        )
        self.assertEqual(report["rejected_records"], 2)
        self.assertEqual(report["accepted_events"], 1)

    def test_offsets_normalize_to_utc(self):
        event = parse_event(row("e1", timestamp="2025-01-01T10:00:00+01:00"))
        self.assertEqual(event["timestamp"].isoformat(), "2025-01-01T09:00:00+00:00")

    def test_event_type_counts_are_sorted(self):
        report = self.run_input(
            row("e1", event_type="zebra") + "\n" +
            row("e2", timestamp="2025-01-01T09:01:00Z", event_type="alpha")
        )
        keys = list(report["users"][0]["sessions"][0]["event_types"])
        self.assertEqual(keys, ["alpha", "zebra"])


if __name__ == "__main__":
    unittest.main()
