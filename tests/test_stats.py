"""Observable behavior of the example application's text statistics."""

import unittest

from repo_demo.stats import TextStats, analyze_text


class TextStatsTests(unittest.TestCase):
    def test_empty_text(self):
        self.assertEqual(analyze_text(""), TextStats(characters=0, words=0, lines=0))

    def test_single_line(self):
        self.assertEqual(analyze_text("hello world"), TextStats(11, 2, 1))

    def test_unicode_and_whitespace(self):
        self.assertEqual(analyze_text("Grüße\tWelt\n"), TextStats(11, 2, 1))

    def test_line_endings(self):
        for text, lines in [("one\ntwo", 2), ("one\r\ntwo\r\n", 2), ("\n\n", 2)]:
            with self.subTest(text=text):
                self.assertEqual(analyze_text(text).lines, lines)

    def test_whitespace_has_no_words(self):
        self.assertEqual(analyze_text(" \t\n").words, 0)


if __name__ == "__main__":
    unittest.main()
