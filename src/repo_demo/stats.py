"""Count text using explicit, Unicode-aware conventions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TextStats:
    characters: int
    words: int
    lines: int


def analyze_text(text: str) -> TextStats:
    """Count code points, whitespace-separated words and splitlines() lines.

    Empty input contains zero lines. A final newline terminates the last line
    and does not introduce another empty line.
    """
    return TextStats(
        characters=len(text),
        words=len(text.split()),
        lines=len(text.splitlines()),
    )
