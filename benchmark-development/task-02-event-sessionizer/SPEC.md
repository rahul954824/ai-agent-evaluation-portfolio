# Event Stream Sessionizer — Specification

## 1. Input

The program is invoked as:

```bash
python sessionize.py INPUT [--idle-minutes N]
```

- `INPUT` is a UTF-8 JSON Lines file. Each nonblank line must contain one JSON object.
- `--idle-minutes` is a positive integer; default: `30`.
- A valid event has:
  - `event_id`: non-empty string
  - `user_id`: non-empty string
  - `timestamp`: ISO-8601 datetime string with an explicit UTC offset or `Z`
  - `event_type`: non-empty string
- Additional keys are allowed and ignored.
- Blank lines are ignored and do not affect any counters.

## 2. Record handling

Process records in file order.

- A malformed JSON line or an event failing validation is rejected. Increment `rejected_records` once per rejected nonblank line and continue.
- The first valid event with a given `event_id` is retained.
- Every later valid event with that same ID is ignored and increments `duplicate_records`, even if its other fields differ.
- Rejected records do not reserve their event IDs.
- Deduplication is global across all users.
- `accepted_events` is the number of retained events after deduplication.

## 3. Timestamp rules

- Parse timestamps as timezone-aware datetimes.
- Naive timestamps are invalid.
- Normalize timestamps to UTC for sorting, session calculations, and output.
- Two timestamps representing the same instant compare equal, even if their input offsets differ.
- Preserve input event order as the tie-breaker when two events for one user have equal instants.

## 4. Sessionization

- Sessionize each user's retained events independently.
- Sort each user's events by normalized timestamp, then original input line order.
- The first event for a user starts session 1.
- A new session starts only when the gap from the immediately preceding event for that user is strictly greater than `idle_minutes`.
- A gap exactly equal to the threshold remains in the same session.
- Session numbering starts at 1 separately for each user.
- Output users in lexicographic order. Within each user, sessions are chronological.

## 5. Output

On success, print one JSON object to stdout, with keys in this order:

```json
{
  "accepted_events": 3,
  "rejected_records": 0,
  "duplicate_records": 0,
  "session_count": 2,
  "users": [
    {
      "user_id": "u1",
      "sessions": [
        {
          "session_index": 1,
          "start": "2025-01-01T09:00:00Z",
          "end": "2025-01-01T09:10:00Z",
          "event_count": 2,
          "duration_seconds": 600.0,
          "event_types": {"click": 1, "view": 1}
        }
      ]
    }
  ]
}
```

Rules:
- `session_count` is the total number of sessions across all users.
- `start` and `end` are UTC timestamps formatted as `YYYY-MM-DDTHH:MM:SSZ`; discard fractional seconds in display only.
- `duration_seconds` is the exact elapsed seconds between the first and last event, represented as a JSON number (integer-valued durations may be emitted as integers or floats).
- `event_types` maps event type strings to counts and must be emitted with keys in lexicographic order.
- The `users` list is sorted by `user_id`; sessions are sorted by start time.
- No extra output keys.
- JSON output must be deterministic. Indentation is optional.

## 6. Errors and exit codes

- Missing/unreadable input file: print a useful message to stderr and exit nonzero.
- Invalid `--idle-minutes` (zero, negative, or not an integer): print a useful message to stderr and exit nonzero.
- On successful processing, exit 0 even if some records were rejected.
- Do not print progress messages or diagnostics to stdout.

## 7. Constraints

- Python 3.10+
- Standard library only
- Must not modify the input file
- Must not crash because an individual input record is malformed
