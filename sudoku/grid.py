"""The board: 81 cells, 0 for empty. Parsing, printing, validity."""

import re

DIGITS = "123456789"

# precomputed indices
ROWS = [[r * 9 + c for c in range(9)] for r in range(9)]
COLS = [[r * 9 + c for r in range(9)] for c in range(9)]
BOXES = [[(br * 3 + r) * 9 + (bc * 3 + c) for r in range(3) for c in range(3)] for br in range(3) for bc in range(3)]
UNITS = ROWS + COLS + BOXES
UNITS_OF = [[u for u in UNITS if i in u] for i in range(81)]
PEERS = [sorted({j for u in UNITS_OF[i] for j in u} - {i}) for i in range(81)]


class GridError(Exception):
    pass


def parse(text):
    """Accept 81 digits/dots in any layout; '.', '0', '_' and '*' mean empty."""
    cleaned = re.sub(r"[^0-9.*_]", "", text)
    if len(cleaned) != 81:
        raise GridError(f"expected 81 cells, found {len(cleaned)}")
    return [int(ch) if ch.isdigit() else 0 for ch in cleaned]


def to_line(cells):
    return "".join(str(v) if v else "." for v in cells)


def to_text(cells, marks=None):
    """A boxed grid for the terminal. `marks` is an optional set of indices to highlight."""
    marks = marks or set()
    out = []
    top = "┌───────┬───────┬───────┐"
    mid = "├───────┼───────┼───────┤"
    bot = "└───────┴───────┴───────┘"
    out.append(top)
    for r in range(9):
        parts = []
        for c in range(9):
            i = r * 9 + c
            v = cells[i]
            s = str(v) if v else "."
            if i in marks and v:
                s = f"\x1b[1m{s}\x1b[0m"
            parts.append(s)
        row = "│ " + " ".join(parts[0:3]) + " │ " + " ".join(parts[3:6]) + " │ " + " ".join(parts[6:9]) + " │"
        out.append(row)
        if r in (2, 5):
            out.append(mid)
    out.append(bot)
    return "\n".join(out)


def to_svg(cells, size=450):
    cell = size / 9
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" font-family="sans-serif">',
        f'<rect width="{size}" height="{size}" fill="white"/>',
    ]
    for i in range(10):
        w = 3 if i % 3 == 0 else 1
        p = i * cell
        parts.append(f'<line x1="{p}" y1="0" x2="{p}" y2="{size}" stroke="black" stroke-width="{w}"/>')
        parts.append(f'<line x1="0" y1="{p}" x2="{size}" y2="{p}" stroke="black" stroke-width="{w}"/>')
    for i, v in enumerate(cells):
        if v:
            x = (i % 9 + 0.5) * cell
            y = (i // 9 + 0.5) * cell
            parts.append(f'<text x="{x}" y="{y}" font-size="{cell * 0.6:.0f}" text-anchor="middle" dominant-baseline="central">{v}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def conflicts(cells):
    """Indices of cells that share a value with a peer. Empty list means consistent."""
    bad = set()
    for unit in UNITS:
        seen = {}
        for i in unit:
            v = cells[i]
            if v:
                if v in seen:
                    bad.add(i)
                    bad.add(seen[v])
                seen[v] = i
    return sorted(bad)


def is_complete(cells):
    return all(cells) and not conflicts(cells)
