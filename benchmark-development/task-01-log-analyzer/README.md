# Task 01: Log Event Analyzer

## Goal

Implement a function that summarizes application log events. This is an original,
self-contained benchmark example for demonstrating task specification and verification.

## Candidate task

Implement `summarize_events(lines)` in `solution.py`.

Each input line is expected to have this format:

```text
<LEVEL> <MESSAGE>
```

Supported levels are `INFO`, `WARNING`, and `ERROR`.

Return a dictionary with exactly these keys:

- `total`: number of valid events
- `counts`: a dictionary containing all three supported levels, including zero counts
- `errors`: a list of messages from `ERROR` events, in input order

Rules:

1. Ignore blank lines.
2. Ignore lines whose level is not supported.
3. Split each valid line only at the first whitespace boundary, so the message may contain spaces.
4. Strip leading and trailing whitespace from the message.
5. A supported level with an empty message is still a valid event.
6. Do not mutate the input list.

## Run

From this directory:

```bash
python -m unittest -v
```

## Evaluation notes

The test suite covers ordinary inputs, blank lines, unsupported levels, empty messages,
messages containing spaces, ordering, and input immutability. These tests are illustrative;
a production benchmark should also consider randomized and adversarial cases.
