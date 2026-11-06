"""Make puzzles: fill a grid at random, then dig out clues while the solution stays unique."""

import random

from .grid import PEERS
from .solver import count_solutions, rate

TARGET_CLUES = {"easy": 38, "medium": 32, "hard": 27, "expert": 20}


def full_grid(rng):
    """A random complete valid grid, by randomised backtracking."""
    cells = [0] * 81

    def fill(i):
        if i == 81:
            return True
        used = {cells[p] for p in PEERS[i]}
        options = [v for v in range(1, 10) if v not in used]
        rng.shuffle(options)
        for v in options:
            cells[i] = v
            if fill(i + 1):
                return True
        cells[i] = 0
        return False

    fill(0)
    return cells


def generate(difficulty="medium", seed=None, symmetric=True):
    """Return (puzzle, solution). Harder levels remove more clues; always unique."""
    if difficulty not in TARGET_CLUES:
        raise ValueError(f"difficulty must be one of {', '.join(TARGET_CLUES)}")
    rng = random.Random(seed)
    solution = full_grid(rng)
    puzzle = list(solution)
    target = TARGET_CLUES[difficulty]

    def dig(groups):
        for group in groups:
            group = [j for j in group if puzzle[j]]
            if not group:
                continue
            if sum(1 for v in puzzle if v) - len(group) < target:
                continue
            saved = {j: puzzle[j] for j in group}
            for j in group:
                puzzle[j] = 0
            if count_solutions(puzzle, 2) != 1:
                for j, v in saved.items():
                    puzzle[j] = v
            if sum(1 for v in puzzle if v) <= target:
                return True
        return False

    order = list(range(81))
    rng.shuffle(order)
    # pass 1: symmetric pairs (looks nicer); pass 2: single cells, to get harder
    done = dig([{i, 80 - i} for i in order] if symmetric else [{i} for i in order])
    if not done and symmetric:
        rng.shuffle(order)
        dig([{i} for i in order])

    return puzzle, solution


def generate_rated(difficulty="medium", seed=None, attempts=40):
    """Like generate(), but retries until the solver's own rating agrees."""
    rng = random.Random(seed)
    last = None
    for _ in range(attempts):
        puzzle, solution = generate(difficulty, rng.random())
        last = (puzzle, solution)
        if rate(puzzle) == difficulty:
            return puzzle, solution
    return last
