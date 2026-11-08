# Task 02: Event Stream Sessionizer

## Task type
Multi-step data-processing / CLI benchmark for evaluating software-engineering agents.

## Objective
Implement a deterministic command-line tool that reads newline-delimited JSON events, validates and deduplicates them, groups events into user sessions, and emits a machine-readable summary.

## Candidate task
Implement `sessionize.py` using only the Python standard library. Follow the complete contract in [SPEC.md](SPEC.md). The starter test suite is in `test_sessionize.py`.

## Run
```bash
python -m unittest -v
python sessionize.py sample_events.jsonl --idle-minutes 30
```

Python 3.10+. No third-party dependencies.

## Evaluation focus
- Strict input validation without crashing on bad records
- Correct global event-ID deduplication
- Timezone-aware timestamp parsing and chronological ordering
- Session boundary behavior at the exact idle threshold
- Stable, deterministic JSON output and CLI error handling

## Benchmark design notes
The task is intentionally more demanding than a single-function exercise: it combines parsing, validation, state management, sorting, boundary conditions, and a CLI contract. A robust hidden suite should include malformed JSON, duplicate IDs with conflicting payloads, out-of-order records, multiple users, timezone offsets, and threshold-edge timestamps.

This is an independently authored portfolio sample. It is not a Project Dynamo deliverable and contains no client prompts, proprietary code, hidden fixtures, or internal evaluation rubrics.
