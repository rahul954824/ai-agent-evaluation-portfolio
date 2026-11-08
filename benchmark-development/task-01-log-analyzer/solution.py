"""Reference implementation for the Log Event Analyzer benchmark."""

SUPPORTED_LEVELS = ("INFO", "WARNING", "ERROR")


def summarize_events(lines):
    """Summarize supported log events without modifying ``lines``.

    Args:
        lines: Iterable of strings formatted as "<LEVEL> <MESSAGE>".

    Returns:
        A dictionary with total, counts, and errors.
    """
    counts = {level: 0 for level in SUPPORTED_LEVELS}
    errors = []

    for raw_line in lines:
        if not isinstance(raw_line, str):
            continue

        line = raw_line.strip()
        if not line:
            continue

        parts = line.split(None, 1)
        level = parts[0]

        if level not in counts:
            continue

        message = parts[1].strip() if len(parts) == 2 else ""
        counts[level] += 1

        if level == "ERROR":
            errors.append(message)

    return {
        "total": sum(counts.values()),
        "counts": counts,
        "errors": errors,
    }
