import unittest

from solution import summarize_events


class SummarizeEventsTests(unittest.TestCase):
    def test_counts_each_supported_level(self):
        result = summarize_events([
            "INFO service started",
            "WARNING disk nearly full",
            "ERROR request failed",
            "INFO health check passed",
        ])
        self.assertEqual(result["total"], 4)
        self.assertEqual(
            result["counts"],
            {"INFO": 2, "WARNING": 1, "ERROR": 1},
        )
        self.assertEqual(result["errors"], ["request failed"])

    def test_ignores_blank_and_unsupported_lines(self):
        result = summarize_events([
            "",
            "   ",
            "DEBUG hidden detail",
            "TRACE ignored",
            "ERROR visible failure",
        ])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["counts"]["ERROR"], 1)
        self.assertEqual(result["errors"], ["visible failure"])

    def test_message_can_contain_spaces(self):
        result = summarize_events(["ERROR database connection timed out"])
        self.assertEqual(result["errors"], ["database connection timed out"])

    def test_supported_level_with_empty_message_is_valid(self):
        result = summarize_events(["INFO", "ERROR   "])
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["errors"], [""])

    def test_error_messages_preserve_input_order(self):
        result = summarize_events([
            "ERROR first",
            "INFO normal",
            "ERROR second",
        ])
        self.assertEqual(result["errors"], ["first", "second"])

    def test_does_not_mutate_input(self):
        lines = [" INFO startup ", "", "ERROR failed"]
        original = lines.copy()
        summarize_events(lines)
        self.assertEqual(lines, original)

    def test_non_string_items_are_ignored(self):
        result = summarize_events(["INFO ok", None, 42])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["counts"]["INFO"], 1)


if __name__ == "__main__":
    unittest.main()
