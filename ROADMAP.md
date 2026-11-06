# Roadmap

Roughly in order. Open an issue if you want one sooner.

## Soon

- [ ] Human-style rating: detect which techniques a puzzle needs (naked/hidden pairs, pointing pairs, X-wing, ...) instead of counting solver guesses
- [ ] `explain`: solve step by step, printing the technique used for each placement
- [ ] Pencil marks in `play` (`3 7 +5` adds a candidate note, shown small) and an `auto` toggle
- [ ] Undo in `play`, and a timer
- [ ] Faster expert generation (currently ~1 s): bias digging toward cells whose removal creates branching
- [ ] `new --count 10 --pdf` for a printable sheet of puzzles (SVG per puzzle, stitched)

## Next

- [ ] Save and resume a game (`~/.sudoku/current.json`)
- [ ] Daily puzzle: `sudoku daily` seeds from today's date so everyone gets the same one
- [ ] Import from common formats (SadMan `.sdk`, SudoCue `.sdm`, images are out of scope)
- [ ] Variants: killer cages, diagonal (X), 6×6 and 16×16 sizes (the unit tables are already data-driven)
- [ ] Colour in the terminal: givens vs entries vs conflicts

## Later / maybe

- [ ] A minimal-clue search (17-clue puzzles) as a long-running experiment
- [ ] A tiny web page version of `play` sharing the same puzzle strings
- [ ] Publish to PyPI

## Housekeeping

- [ ] Tests for `play` via scripted input
- [ ] GitHub Actions running `pytest` on Linux, macOS and Windows (box-drawing characters on Windows consoles)
- [ ] Type hints and a `mypy` pass
- [ ] CHANGELOG.md starting at 0.2.0
