"""Exercise the real CLI process with positional input and stdin."""

import subprocess
import sys
import unittest


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "repo_demo", *args],
            input=stdin,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )

    def test_positional_input(self):
        result = self.run_cli("hello world")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Characters: 11\nWords: 2\nLines: 1\n")

    def test_stdin(self):
        result = self.run_cli(stdin="first\nsecond\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Characters: 13\nWords: 2\nLines: 2\n")

    def test_empty_argument_does_not_consume_stdin(self):
        result = self.run_cli("", stdin="must not be read")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Characters: 0\nWords: 0\nLines: 0\n")

    def test_unknown_option_fails(self):
        result = self.run_cli("--unknown")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)


if __name__ == "__main__":
    unittest.main()
