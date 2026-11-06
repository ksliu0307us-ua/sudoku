import pytest

from sudoku import generator, grid, solver
from sudoku.cli import main

# Project Euler problem 96, grid 01, and its known solution
PE01 = "003020600900305001001806400008102900700000008006708200002609500800203009005010300"
PE01_SOLUTION = "483921657967345821251876493548132976729564138136798245372689514814253769695417382"

# "AI Escargot", a famously hard one
ESCARGOT = "1....7.9..3..2...8..96..5....53..9...1..8...26....4...3......1..4......7..7...3.."

# two solutions: the empty grid with one clue
AMBIGUOUS = "5" + "." * 80

# contradictory givens
BROKEN = "55" + "." * 79


# --- grid ------------------------------------------------------------------------

def test_parse_accepts_layouts():
    boxed = grid.to_text(grid.parse(PE01))
    assert grid.parse(boxed) == grid.parse(PE01)
    assert grid.parse(PE01.replace("0", ".")) == grid.parse(PE01)
    with pytest.raises(grid.GridError):
        grid.parse("123")


def test_units_and_peers():
    assert len(grid.UNITS) == 27
    assert all(len(u) == 9 for u in grid.UNITS)
    assert all(len(p) == 20 for p in grid.PEERS)
    assert 1 in grid.PEERS[0] and 9 in grid.PEERS[0] and 20 in grid.PEERS[0] and 21 not in grid.PEERS[0]


def test_conflicts_and_complete():
    assert grid.conflicts(grid.parse(PE01)) == []
    assert grid.conflicts(grid.parse(BROKEN)) == [0, 1]
    assert grid.is_complete(grid.parse(PE01_SOLUTION))
    assert not grid.is_complete(grid.parse(PE01))


def test_svg_has_digits():
    svg = grid.to_svg(grid.parse(PE01))
    assert svg.startswith("<svg") and ">3<" in svg


# --- solver ----------------------------------------------------------------------

def test_solves_known_puzzle_without_guessing():
    stats = {}
    sol = solver.solve(grid.parse(PE01), stats)
    assert grid.to_line(sol) == PE01_SOLUTION
    assert stats["guesses"] == 0


def test_solves_hard_puzzle():
    cells = grid.parse(ESCARGOT)
    sol = solver.solve(cells)
    assert grid.is_complete(sol)
    assert all(sol[i] == v for i, v in enumerate(cells) if v)  # givens kept
    assert solver.rate(cells) == "expert"


def test_count_solutions():
    assert solver.count_solutions(grid.parse(PE01)) == 1
    assert solver.count_solutions(grid.parse(AMBIGUOUS)) == 2  # stops at the limit
    assert solver.count_solutions(grid.parse(AMBIGUOUS), limit=5) == 5
    assert solver.count_solutions(grid.parse(BROKEN)) == 0


def test_unsolvable_raises():
    with pytest.raises(solver.Unsolvable):
        solver.solve(grid.parse(BROKEN))
    # no two givens clash, but cell 9 of row 1 can only be 9 and column 9 already has one
    cells = grid.parse("12345678." + "........9" + "." * 63)
    with pytest.raises(solver.Unsolvable):
        solver.solve(cells)


# --- generator ---------------------------------------------------------------------

def test_full_grid_is_valid():
    import random
    g = generator.full_grid(random.Random(3))
    assert grid.is_complete(g)


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_generated_puzzles_are_unique_and_rated(difficulty):
    puzzle, solution = generator.generate_rated(difficulty, seed=7)
    assert grid.is_complete(solution)
    assert solver.count_solutions(puzzle) == 1
    assert solver.solve(puzzle) == solution
    assert solver.rate(puzzle) == difficulty
    clues = sum(1 for v in puzzle if v)
    assert clues <= generator.TARGET_CLUES[difficulty] + 4


def test_seed_is_reproducible():
    a = generator.generate("medium", seed=11)
    b = generator.generate("medium", seed=11)
    assert a == b
    assert generator.generate("medium", seed=12) != a


def test_symmetry():
    puzzle, _ = generator.generate("easy", seed=5, symmetric=True)
    assert all((puzzle[i] == 0) == (puzzle[80 - i] == 0) for i in range(81))


def test_bad_difficulty():
    with pytest.raises(ValueError):
        generator.generate("brutal")


# --- cli --------------------------------------------------------------------------

def test_cli_solve_string_and_file(tmp_path, capsys):
    assert main(["solve", PE01, "--line"]) == 0
    assert capsys.readouterr().out.strip() == PE01_SOLUTION
    f = tmp_path / "p.txt"
    f.write_text(grid.to_text(grid.parse(PE01)), encoding="utf-8")
    assert main(["solve", str(f), "--line"]) == 0
    assert capsys.readouterr().out.strip() == PE01_SOLUTION


def test_cli_solve_errors(capsys):
    assert main(["solve", BROKEN]) == 1
    assert "conflict" in capsys.readouterr().err
    assert main(["solve", AMBIGUOUS, "--line"]) == 0
    assert "more than one" in capsys.readouterr().err


def test_cli_rate_and_new(capsys, tmp_path):
    assert main(["rate", PE01]) == 0
    assert capsys.readouterr().out.strip() == "medium"  # 30 clues, no guessing
    svg = tmp_path / "p.svg"
    assert main(["new", "-d", "easy", "-s", "1", "--line", "--solution", "--svg", str(svg)]) == 0
    out = capsys.readouterr().out.strip().splitlines()
    puzzle, solution = grid.parse(out[0]), grid.parse(out[-1])
    assert solver.solve(puzzle) == solution
    assert svg.exists()
