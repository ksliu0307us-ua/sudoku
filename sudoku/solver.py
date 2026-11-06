"""Solve by constraint propagation first, search second.

Each cell holds a set of candidates. Assigning a value removes it from all
peers; when a peer drops to one candidate it's assigned too (naked single),
and when a unit has only one place left for a value it goes there (hidden
single). That alone finishes most newspaper puzzles. Anything left is
solved by trying candidates in the cell with the fewest, depth first.

`count_solutions` is the same search but keeps going to find a second
solution, which is how the generator checks a puzzle is unique.
"""

from .grid import PEERS, UNITS_OF, DIGITS


class Unsolvable(Exception):
    pass


def _assign(cand, i, v):
    """Set cell i to v and propagate. Raises Unsolvable on contradiction."""
    others = cand[i] - {v}
    for o in others:
        _eliminate(cand, i, o)


def _eliminate(cand, i, v):
    if v not in cand[i]:
        return
    cand[i].discard(v)
    if not cand[i]:
        raise Unsolvable("cell has no candidates")
    if len(cand[i]) == 1:
        (only,) = cand[i]
        for p in PEERS[i]:
            _eliminate(cand, p, only)
    # hidden single: is v now forced somewhere in one of i's units?
    for unit in UNITS_OF[i]:
        places = [j for j in unit if v in cand[j]]
        if not places:
            raise Unsolvable("value has nowhere to go")
        if len(places) == 1:
            _assign(cand, places[0], v)


def propagate(cells):
    """Return the candidate sets after propagation, or raise Unsolvable."""
    cand = [set(range(1, 10)) for _ in range(81)]
    for i, v in enumerate(cells):
        if v:
            if v not in cand[i]:
                raise Unsolvable("givens conflict")
            _assign(cand, i, v)
    return cand


def _search(cand, stats, limit):
    """Yield solved candidate grids (each cell a 1-set), up to `limit`."""
    if all(len(c) == 1 for c in cand):
        yield cand
        return
    # cell with fewest candidates
    i = min((i for i in range(81) if len(cand[i]) > 1), key=lambda i: len(cand[i]))
    stats["guesses"] += 1
    found = 0
    for v in sorted(cand[i]):
        branch = [set(c) for c in cand]
        try:
            _assign(branch, i, v)
        except Unsolvable:
            continue
        for sol in _search(branch, stats, limit - found):
            found += 1
            yield sol
            if found >= limit:
                return


def solve(cells, stats=None):
    """Return the solved grid (list of 81 ints). Raises Unsolvable."""
    stats = stats if stats is not None else {}
    stats.setdefault("guesses", 0)
    cand = propagate(cells)
    for sol in _search(cand, stats, 1):
        return [next(iter(c)) for c in sol]
    raise Unsolvable("no solution")


def count_solutions(cells, limit=2):
    """Number of solutions, stopping at `limit`. 1 means a proper puzzle."""
    try:
        cand = propagate(cells)
    except Unsolvable:
        return 0
    stats = {"guesses": 0}
    return sum(1 for _ in _search(cand, stats, limit))


def rate(cells):
    """A rough difficulty label from how much the solver had to guess."""
    stats = {}
    solve(cells, stats)
    clues = sum(1 for v in cells if v)
    guesses = stats["guesses"]
    if guesses == 0:
        return "easy" if clues >= 36 else "medium"
    if guesses <= 4:
        return "hard"
    return "expert"
