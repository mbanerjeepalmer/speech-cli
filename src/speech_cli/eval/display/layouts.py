"""Rendering strategy helpers for eval display."""


def tail_text(text: str, width: int) -> str:
    """Return the last `width` characters of text, for single-line display."""
    if len(text) <= width:
        return text
    return text[-width:]


def truncate_text(text: str, width: int) -> str:
    """Truncate text to `width` characters with ellipsis."""
    if len(text) <= width:
        return text
    return text[: width - 1] + "\u2026"
