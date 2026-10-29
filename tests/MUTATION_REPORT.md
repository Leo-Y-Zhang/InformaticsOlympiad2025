# Mutation-guided unit tests

Production Python files are unchanged. The only change outside `tests/` is two
CI steps in the existing checker job: install `pytest==8.4.2`, then `pytest -q`.
`conftest.py` makes the standalone modules importable from either pytest entry
point and isolates the Q1 checker's import-time argument parsing.

The core decisions are palindrome enumeration/minimal sums, board components
and move selection, and exact fuse-event periods. The three checker scripts
validate these results against independent calculations. There are no witness
files, clauses, SAT solvers, or certificate-file parsers in this repository.
Corruptions therefore use the actual result types: changed values/colours,
wrong sums and lengths, truncated boards, illegal moves, removed periods, and
changed period sets with the same count.

## Experiment

`mutation_check.py` applies 47 explicit, single-site mutations, one at a time,
in fresh temporary copies under the repository. All mutants compile. Operators
include comparison boundary changes, condition/Boolean changes, off-by-ones,
disabled assertions, reversed ordering, and incorrect arithmetic. These are
curated mutants, not an exhaustive mutation score for all possible changes.

Before means the original correctness gate; there were no existing pytest
tests. For each mutant the runner executes the affected checker and its CI
samples. Other checker/sample commands cannot import that module, so their
results cannot change. Written/search helpers have no original CI coverage.
Both runs first verify the unmodified gate; the after run also verifies the
unmodified pytest suite. After measures the original gate plus the new tests,
and also records pytest independently for every mutant. `-x` stops a mutant's
pytest run at the first failure. Timeouts are recorded separately, never
counted as kills.

The first after run left three checker mutants alive: the initial negative
fixtures were being rejected by the full-board invariant before reaching move
validation. Full starting boards and a guard against a second turn isolate
the intended rejection paths in the final tests.

Final counts are recorded in `mutations_before.json` and `mutations_after.json`;
each row includes the source line, exact replacement, and gate/pytest outcomes.

| Module | Mutants tried | Killed before | Killed after |
| --- | ---: | ---: | ---: |
| `q1_check.py` | 6 | 0 | 6 |
| `q1_palindromic_sums.py` | 6 | 4 | 6 |
| `q1_written.py` | 4 | 0 | 4 |
| `q2_check.py` | 5 | 0 | 5 |
| `q2_safe_haven.py` | 11 | 8 | 11 |
| `q3_check.py` | 3 | 1 | 3 |
| `q3_search.py` | 2 | 0 | 2 |
| `q3_short_fuse.py` | 8 | 6 | 8 |
| `q3_written.py` | 2 | 0 | 2 |
| **Total** | **47** | **19** | **47** |

All 47 final mutants were also killed by pytest independently. No mutants timed out.

## Tests and specific kills

| New test file | Example mutant killed (all survived the original gate) |
| --- | --- |
| `test_palindromic_sums.py` | #3, `q1_palindromic_sums.py:32`: `odd <= limit` becomes `<`, dropping a palindrome at the endpoint. Also #13, `q1_written.py:26`: `c >= b` becomes `>`, losing repeated terms such as `(7, 7, 7)` for 21. |
| `test_safe_haven.py` | #21, `q2_safe_haven.py:95`: `(-theirs, mine, comp[-1])` becomes `(theirs, mine, comp[-1])`, selecting the haven with more enemies. The three priority rules are tested separately. |
| `test_short_fuse.py` | #38, `q3_short_fuse.py:100`: `Fraction(p, scale)` becomes `Fraction(p, scale + 1)`. Also #44, `q3_written.py:10`: the integer/fraction formatting condition is negated. |
| `test_checkers.py` | #29, `q2_check.py:87`: the adjacency assertion is disabled. Also #41, `q3_check.py:87`: exact set equality becomes count equality, accepting a changed period with unchanged cardinality. |

Each checker has acceptance tests and deliberate rejection tests. Q1 checks
non-palindromes, wrong totals, order, minimal length, missing answers, and wrong
tie-breaks. Q2 checks changed colours/truncated boards, reversed-colour and
diagonal captures, premature endings, and enhanced moves creating no haven.
Q3 checks missing periods and changed values even when their count agrees.

## Commands and results

Local interpreter: Python 3.11.2; pytest 8.4.2. A temporary virtual environment
was used because the system interpreter has no pip. No runtime dependencies
were added. The unit tests do not use the network or invoke SAT solving.

```sh
python -m venv /work/.test-env
/work/.test-env/bin/python -m pip install pytest==8.4.2
/work/.test-env/bin/python tests/mutation_check.py --without-tests --output tests/mutations_before.json
/work/.test-env/bin/python tests/mutation_check.py --output tests/mutations_after.json
/work/.test-env/bin/pytest -q
```

The virtual environment creation and installation succeeded. The initial
`python -m ensurepip` attempt was unavailable on the system interpreter;
bootstrapping pip inside the virtual environment succeeded instead.

Full `pytest -q` output:

```text
........................................................................ [ 98%]
.                                                                        [100%]
73 passed in 1.14s
```

`/work/.test-env/bin/pytest -q --durations=5` also passed: 73 tests in 1.19s;
the slowest test was the Q2 valid-game checker test at 0.70s. Every new test
is below 2 seconds and the complete suite is below 60 seconds.

```sh
python q1_check.py && python q2_check.py && python q3_check.py
```

Result: exit 0. Q1 agreed for 1..5000 and 998000..1000000, including the
written counts; Q2 reported 6776 setups with zero mismatches and 90 amended
games with all moves legal; Q3 reported exact agreement on all 17 cases and
the written answers. All five existing CI stdout samples were also executed
and matched (`1031`, `12321`, `9610`; `3 5 5`; `2 1 1`).

`git diff --check` passed. Python compilation checks passed for the test
support files and all 47 mutants.

No production seams or fixes were needed. Python 3.9/3.13 execution is left to
the existing CI matrix; local execution used 3.11.2. The mutation
experiment covers the listed operators/sites, not every possible mutation.
