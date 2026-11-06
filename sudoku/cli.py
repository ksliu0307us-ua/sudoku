import argparse
import sys
from pathlib import Path

from . import generator, grid, solver


def read_puzzle(source):
    """A file path, or the 81 characters directly, or '-' for stdin."""
    if source == "-":
        text = sys.stdin.read()
    elif Path(source).is_file():
        text = Path(source).read_text(encoding="utf-8")
    else:
        text = source
    return grid.parse(text)


def cmd_new(args):
    puzzle, solution = generator.generate_rated(args.difficulty, args.seed)
    if args.line:
        print(grid.to_line(puzzle))
    else:
        print(grid.to_text(puzzle))
    if args.solution:
        print()
        print(grid.to_line(solution) if args.line else grid.to_text(solution))
    if args.svg:
        Path(args.svg).write_text(grid.to_svg(puzzle), encoding="utf-8")
        print(f"wrote {args.svg}", file=sys.stderr)
    return 0


def cmd_solve(args):
    cells = read_puzzle(args.puzzle)
    bad = grid.conflicts(cells)
    if bad:
        print("error: the givens conflict with each other", file=sys.stderr)
        return 1
    n = solver.count_solutions(cells, 2)
    if n == 0:
        print("error: no solution", file=sys.stderr)
        return 1
    stats = {}
    solution = solver.solve(cells, stats)
    print(grid.to_line(solution) if args.line else grid.to_text(solution, marks=set(i for i, v in enumerate(cells) if v)))
    if n > 1:
        print("note: this puzzle has more than one solution; showing one", file=sys.stderr)
    if args.verbose:
        print(f"guesses: {stats['guesses']}  rating: {solver.rate(cells)}", file=sys.stderr)
    return 0


def cmd_rate(args):
    cells = read_puzzle(args.puzzle)
    n = solver.count_solutions(cells, 2)
    if n != 1:
        print("not a proper puzzle:", "no solution" if n == 0 else "more than one solution")
        return 1
    print(solver.rate(cells))
    return 0


def cmd_play(args):
    if args.puzzle:
        puzzle = read_puzzle(args.puzzle)
    else:
        puzzle, _ = generator.generate_rated(args.difficulty, args.seed)
    solution = solver.solve(puzzle)
    board = list(puzzle)
    givens = {i for i, v in enumerate(puzzle) if v}
    print(grid.to_text(board, givens))
    print("enter: row col value (1-9), e.g. '3 7 5'. 'row col 0' clears. 'hint', 'check', 'quit'.")
    while True:
        try:
            raw = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if raw in ("q", "quit", "exit"):
            return 0
        if raw == "check":
            wrong = [i for i in range(81) if board[i] and board[i] != solution[i]]
            print("all correct so far" if not wrong else f"{len(wrong)} cell(s) wrong")
            continue
        if raw == "hint":
            empties = [i for i in range(81) if not board[i]]
            if not empties:
                print("nothing left to fill")
                continue
            i = empties[0]
            board[i] = solution[i]
            print(f"row {i // 9 + 1} col {i % 9 + 1} is {solution[i]}")
            print(grid.to_text(board, givens))
            continue
        parts = raw.split()
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            print("didn't get that. try 'row col value'")
            continue
        r, c, v = (int(p) for p in parts)
        if not (1 <= r <= 9 and 1 <= c <= 9 and 0 <= v <= 9):
            print("rows and cols are 1-9, value 0-9")
            continue
        i = (r - 1) * 9 + (c - 1)
        if i in givens:
            print("that's a given")
            continue
        board[i] = v
        print(grid.to_text(board, givens))
        if grid.is_complete(board):
            print("solved. nice.")
            return 0
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="sudoku", description="make, solve and play sudoku in the terminal")
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="generate a puzzle")
    n.add_argument("-d", "--difficulty", default="medium", choices=generator.TARGET_CLUES)
    n.add_argument("-s", "--seed", type=int, help="same seed, same puzzle")
    n.add_argument("--solution", action="store_true", help="print the solution too")
    n.add_argument("--line", action="store_true", help="81 characters on one line instead of a box")
    n.add_argument("--svg", metavar="FILE", help="also write the puzzle as an SVG")
    n.set_defaults(fn=cmd_new)

    s = sub.add_parser("solve", help="solve a puzzle from a file, a string, or stdin (-)")
    s.add_argument("puzzle")
    s.add_argument("--line", action="store_true")
    s.add_argument("-v", "--verbose", action="store_true", help="show how hard the solver found it")
    s.set_defaults(fn=cmd_solve)

    r = sub.add_parser("rate", help="estimate a puzzle's difficulty")
    r.add_argument("puzzle")
    r.set_defaults(fn=cmd_rate)

    pl = sub.add_parser("play", help="play in the terminal")
    pl.add_argument("puzzle", nargs="?", help="a puzzle to play; default is a fresh one")
    pl.add_argument("-d", "--difficulty", default="easy", choices=generator.TARGET_CLUES)
    pl.add_argument("-s", "--seed", type=int)
    pl.set_defaults(fn=cmd_play)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except grid.GridError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
