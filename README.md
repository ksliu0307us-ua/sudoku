# sudoku

Generate, solve, rate and play sudoku in the terminal. Every generated
puzzle has exactly one solution; the solver uses constraint propagation
and only guesses when it has to, which is also how it rates difficulty.

```
$ sudoku new -d hard
┌───────┬───────┬───────┐
│ . . . │ 7 . . │ . 9 . │
│ . . . │ 2 . . │ 7 . 1 │
│ . . 1 │ 9 . 3 │ . . . │
├───────┼───────┼───────┤
│ 5 2 . │ . . 4 │ . . 3 │
│ . . 8 │ . 3 . │ 2 . . │
│ 3 . . │ 1 . . │ . 5 6 │
├───────┼───────┼───────┤
│ . . . │ 4 . 9 │ 6 . . │
│ 2 . 7 │ . . 1 │ . . . │
│ . 9 . │ . . 5 │ . . . │
└───────┴───────┴───────┘

$ sudoku solve "1....7.9..3..2...8..96..5....53..9...1..8...26....4...3......1..4......7..7...3.." -v
...
guesses: 10  rating: expert
```

I wanted puzzles I could print for a flight, a way to check a newspaper
puzzle was actually solvable, and an excuse to write a proper solver.

## Who it's for

Me, and anyone who likes sudoku or wants a readable example of constraint
propagation plus backtracking that fits in one file.

## Built with

- Python 3.9+, standard library only.
- `pytest` for the tests.

## Install

```sh
git clone https://github.com/ksliu0307us-ua/sudoku.git
cd sudoku
pip install -e .
```

Or run it without installing: `python -m sudoku.cli ...`.

## Usage

```sh
sudoku new                          # a medium puzzle
sudoku new -d expert -s 42          # difficulty easy|medium|hard|expert; a seed makes it repeatable
sudoku new --solution               # print the answer too
sudoku new --line                   # 81 characters, handy for piping
sudoku new --svg puzzle.svg         # printable

sudoku solve puzzle.txt             # from a file (any layout: boxed, 9 lines, or one line)
sudoku solve "53..7....6..195..." # or the 81 characters directly; . 0 _ * mean empty
sudoku new --line | sudoku solve -  # or stdin
sudoku solve puzzle.txt -v          # how many guesses it took, and the rating

sudoku rate puzzle.txt              # easy / medium / hard / expert
sudoku play                         # interactive: 'row col value', 'hint', 'check', 'quit'
sudoku play -d hard
sudoku play puzzle.txt
```

## How it works

**Solver** (`sudoku/solver.py`). Every cell starts with candidates 1–9.
Assigning a value removes it from the 20 peers; a cell left with one
candidate is assigned (naked single); a value with only one place left in
a row, column or box goes there (hidden single). That alone solves most
published puzzles with zero guesses. If anything remains, it picks the cell
with the fewest candidates and tries each, depth first.
`count_solutions` runs the same search but keeps looking for a second
solution.

**Generator** (`sudoku/generator.py`). Fill a grid by randomised
backtracking, then remove clues — symmetric pairs first, single cells
after — keeping each removal only if the puzzle still has exactly one
solution. Stop at the clue count for the difficulty. `new` repeats this
until the solver's own rating agrees with what you asked for.

**Rating.** No guesses and 36+ clues: easy. No guesses, fewer clues:
medium. One to four guesses: hard. More: expert. It's a solver's view of
difficulty, not a human's; the roadmap has the human techniques.

## Running the tests

```sh
pip install pytest
pytest
```

The tests include a classic puzzle with its known solution, a famously
hard one, and checks that generated puzzles are unique at every level.

## Roadmap

See [ROADMAP.md](ROADMAP.md). Issues and PRs welcome.

## License

MIT. See [LICENSE](LICENSE).
