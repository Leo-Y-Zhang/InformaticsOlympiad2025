# British Informatics Olympiad 2025 — Round One

Python 3 solutions and written answers to the three Round One problems, plus the
brute-force checkers used to convince myself the answers to the written parts
were right rather than merely plausible.

| Part | Program | What it does |
| --- | --- | --- |
| 1(a) | `q1_palindromic_sums.py` | Minimal-length palindromic sum for `n`, ties broken by lowest then highest palindrome used |
| 2(a) | `q2_safe_haven.py` | Question 2, part (a) |
| 3(a) | `q3_short_fuse.py` | Question 3, part (a) |
| 1(b), (c) | `q1_written.py` | Helper used to derive the written answers |
| 2(b)–(d) | `q2_written.py`, `q2_check.py` | Helper plus an independent brute-force check |
| 3(b), (c) | `q3_written.py`, `q3_search.py`, `q3_check.py` | Search plus an independent brute-force check |

`WRITTEN_ANSWERS.md` holds the prose answers in the order the paper asks for
them. Every program prints its identifying banner on **stderr**, so `stdout`
matches the sample runs byte for byte and can be diffed against them directly.

## Running

```bash
python q1_palindromic_sums.py    # reads from stdin, writes to stdout
```

Python 3 only, no dependencies, no build step. `NAME` and `SCHOOL` at the top of
each `q*(a)` program are placeholders — fill them in before submitting anything.

## Checkers

`q2_check.py` and `q3_check.py` exist because the written parts ask for counts
and bounds that are easy to get subtly wrong by reasoning alone. Each enumerates
the small cases exhaustively and compares against the answer the written
solution claims, so a wrong claim fails loudly instead of looking tidy.

## Why this repository is private

It holds worked solutions to a competition paper. The problem statements are not
reproduced here — only a one-line restatement of each input and output contract —
so this is my own work rather than a copy of theirs. But publishing solutions to
a competition is the organiser's call, not mine, and nothing is gained by getting
that wrong. It stays private unless the BIO's own rules on publishing solutions
are checked first and clearly permit it.
