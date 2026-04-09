"""Common helpers shared across fact-family extractors."""

from __future__ import annotations


def line_number_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, max(offset, 0)) + 1
