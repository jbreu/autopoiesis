"""Command-line entry point for the demo application."""

import argparse
import sys
from collections.abc import Sequence

from repo_demo import __version__
from repo_demo.stats import analyze_text


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Count characters, words and lines.")
    parser.add_argument("text", nargs="?", help="Text to analyze; omit to read standard input.")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    text = args.text if args.text is not None else sys.stdin.read()
    stats = analyze_text(text)
    print(f"Characters: {stats.characters}")
    print(f"Words: {stats.words}")
    print(f"Lines: {stats.lines}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
