# AI Agent Evaluation Portfolio

An independently created portfolio demonstrating software-engineering benchmark design,
automated verification, terminal-based evaluation, and analysis of AI-agent behavior.

> **Scope and attribution:** The examples in this repository are original demonstrations
> created for this portfolio. They are not Project Dynamo deliverables and do not contain
> client prompts, proprietary code, hidden fixtures, or internal evaluation rubrics.
> Any professional experience should be described separately and accurately.

## Repository contents

- `benchmark-development/task-01-log-analyzer/` — a small coding benchmark with a clear
  specification, reference implementation, and automated tests.
- `python-verifiers/` — reusable verification examples will be added here.
- `agent-evaluation/` — evaluation notes and failure-analysis examples will be added here.
- `terminal-environments/` — reproducible command-line workflows will be added here.

## Run the first benchmark

Requirements: Python 3.10 or newer. No third-party packages are required.

```bash
cd benchmark-development/task-01-log-analyzer
python -m unittest -v
```

The tests validate the reference implementation. To evaluate a candidate solution,
replace the implementation in `solution.py` while keeping the public function contract
and run the same test command.

## Skills demonstrated

- Translating a natural-language request into a testable specification
- Writing Python code with explicit input and output contracts
- Designing edge-case tests
- Verifying behavior with automated tests
- Documenting limitations and expected behavior

## Suggested next additions

1. Add an independent candidate implementation and compare its behavior against the
   acceptance tests.
2. Add a verifier that reports individual requirement checks.
3. Add a terminal task with setup instructions and a reproducible grading command.
4. Add a short failure-analysis report based on observed test results.
