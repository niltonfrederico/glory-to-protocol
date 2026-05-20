from rich.cells import cell_len as _cell_len


def cell_len(text: str) -> int:
    """Width of `text` in terminal cells, safe for Cyrillic and CJK."""
    return _cell_len(text)


def pad_to(text: str, width: int) -> str:
    """Pad `text` with spaces on the right to occupy `width` cells."""
    deficit = width - cell_len(text)
    if deficit <= 0:
        return text
    return text + " " * deficit


def truncate_to(text: str, width: int) -> str:
    """Truncate `text` so it occupies at most `width` cells."""
    if cell_len(text) <= width:
        return text
    out: list[str] = []
    used = 0
    for ch in text:
        w = _cell_len(ch)
        if used + w > width:
            break
        out.append(ch)
        used += w
    return "".join(out)
