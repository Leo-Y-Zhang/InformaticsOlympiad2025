# BIO 2025 Round One — written answers

Name: ………………………  Age: ……  School/College: ………………………

## Program names

| Part | Program |
|------|---------|
| 1(a) | `q1_palindromic_sums.py` |
| 2(a) | `q2_safe_haven.py` |
| 3(a) | `q3_short_fuse.py` |
| helpers used to answer 1(b),(c) | `q1_written.py` |
| helpers used to answer 2(b),(c),(d) | `q2_written.py`, `q2_check.py` |
| helpers used to answer 3(b),(c) | `q3_written.py`, `q3_search.py`, `q3_check.py` |

All programs are Python 3 (no compiler, so no executables). Each prints an
identifying banner on stderr so that stdout matches the sample runs exactly.

---

## Question 1 — Palindromic Sums

### 1(a)
`q1_palindromic_sums.py`. Sample run reproduced: input `1031` → `1 101 929`.

Method: generate every palindrome ≤ n by mirroring each "half" 1, 2, 3, …
(1 998 of them below 10^6). If n is a palindrome, answer is n. Otherwise scan
palindromes p upwards and stop at the first with n − p palindromic — because the
scan is upwards this automatically has the lowest possible smallest term. If no
pair exists, scan the smallest term a upwards and, for each, scan the largest
term c downwards, stopping at the first pair (a, c) with n − a − c palindromic;
that gives the lowest smallest term, then the highest largest term.

### 1(b) — the palindromic sums that represent 54

54 is not a palindrome, and it is not the sum of two palindromes (the only
palindromes ≤ 54 are 1–9, 11, 22, 33, 44, and none of 53, 52, …, 45, 43, 32,
21, 10 is palindromic). So every palindromic sum for 54 has three terms, and
there are **five** of them:

* 54 = 1 + 9 + 44
* 54 = 2 + 8 + 44
* 54 = 3 + 7 + 44
* 54 = 4 + 6 + 44
* 54 = 5 + 5 + 44

(All five must use 44: with a largest term of 33 or less the other two would have
to total 21 or more from {1…9, 11, 22, 33}, and no such pair sums correctly.)
Applying the tie-break rules, the program prints `1 9 44`.

### 1(c) — how many n in 1…1 000 000 need three palindromes

**266 948**

Full breakdown of 1…1 000 000:

| terms needed | count |
|---|---|
| 1 (n is itself palindromic) | 1 998 |
| exactly 2 | 731 054 |
| **exactly 3** | **266 948** |
| 4 or more | 0 |
| total | 1 000 000 |

Computed two independent ways (bitmask convolution of the palindrome set in
`q1_written.py`, and explicit set arithmetic in `q1_check.py`) — they agree, and
the "4 or more" row confirms the paper's claim that three palindromes always
suffice.

---

## Question 2 — Safe Haven

### 2(a)
`q2_safe_haven.py`. Sample run reproduced: input `3 5 5` → `2 1`.

Method: the set-up is done by collecting the still-empty squares in the cyclic
order they will be visited and indexing straight to element `(modifier − 1) mod
(number of empty squares)` — this handles modifiers far larger than the number
of empty squares without looping. Havens are the connected components of the
non-empty squares (flood fill). The haven is chosen with the sort key
(−opponent squares, own squares, highest position), maximised.

### 2(b) — set-up grid for input `3 123456789 987654321`

```
R G R
R G G
G R R
```

Red controls 1, 3, 4, 8, 9; Green controls 2, 5, 6, 7.

Order of claiming: R1, G2, R3, G6, R4, G5, R9, G7, R8.

### 2(c) — modifiers under 50 giving a 4×4 chequerboard

**r = 25, g = 41**

This is the *only* pair with both modifiers below 50 (checked exhaustively over
all 49 × 49 pairs). The resulting grid is

```
R G R G
G R G R
R G R G
G R G R
```

so no two neighbouring squares are held by the same player.

### 2(d) — amended strategy, input `10 810 2025`

**Red 20, Green 17.**

(For comparison, the unamended strategy of part (a) gives Red 10, Green 5 on the
same input — the safe-haven-first rule roughly doubles both totals, because
players lock away small groups instead of fighting on.)

---

## Question 3 — Short Fuse

### 3(a)
`q3_short_fuse.py`. Sample run reproduced: input `2` then `1 1` → `7`.

Method: a fuse has a mode — 0 unlit, 1 burning at one end, 2 burning at both —
which can never decrease, and a remaining burn time that falls at `mode` per unit
time. Decisions can only be taken at time 0 and at each instant a fuse finishes,
so a schedule is a path of at most f events. A measurable period is the gap
between two events of one schedule (time 0 counts as an event). Because the
future depends only on the current state, the answer is the union over every
reachable state S of {0} together with the set of future event offsets from S,
and that offset set memoises on the state — which makes the search tiny. Times
are kept as exact integers scaled by 2^(f+2) (at most f halvings can occur).

Runtime for the hardest four-fuse inputs is a few hundredths of a second.

### 3(b) — periods measurable with fuses of burn time 1 and 2

**Nine periods: 0, ½, ¾, 1, 1¼, 1½, 2, 2½, 3.**

Sample constructions:

| period | how |
|---|---|
| 0 | light nothing |
| ½ | fuse 1 at both ends |
| ¾ | light fuse 1 at both ends and fuse 2 at one end; at ½ fuse 2 has 1½ left, light its other end → it ends at 1¼. Time the gap from ½ to 1¼ |
| 1 | fuse 1 at one end (or fuse 2 at both ends) |
| 1¼ | as for ¾ but time from 0 to 1¼ |
| 1½ | fuse 1 both ends (ends ½), then fuse 2 both ends (ends 1½) |
| 2 | fuse 2 at one end |
| 2½ | fuse 1 both ends (ends ½), then fuse 2 at one end (ends 2½) |
| 3 | fuse 1 at one end, then fuse 2 at one end |

### 3(c) — maximum number of periods

* **Two fuses: 17.** First achieved by burn times 3 and 5 (also 7 and 11, and
  almost any pair of large "generic" values — e.g. 2522 and 4808).
  The 17 periods for (3, 5) are
  0, ¼, ½, 1, 1½, 1¾, 2, 2½, 2¾, 3, 3¼, 3½, 4, 5, 5½, 6½, 8.
* **Three fuses: 163.** First achieved by burn times 41, 52, 55 (and by many
  large generic triples, e.g. 3901, 3975, 4015).

The count depends only on the *ratios* of the burn times, so the maximum sits at
a generic ratio. Evidence: exhaustive sweep of all coprime pairs up to 320 and
all coprime triples up to 100, plus 100 000 random pairs and 300 000 random
triples drawn from 1…5000 — nothing beat 17 or 163. Note the maximum is *not*
at equal or tiny burn times: (1,1) gives only 7 and (1,1,1) only 16.

---

## Verification performed

* Q1: `q1_check.py` takes every n from 1 to 5000 — exhaustive, not sampled —
  and compares the solver against an independent enumeration of *every*
  minimal-length representation, checking correct total, all terms
  palindromic, ascending order, minimal length, and then that the answer is
  the exact representation the paper's tie-break selects. 2778 of the 5000
  admit more than one minimal representation, so the tie-break is what most of
  the range is testing. Stated examples reproduced: 12321 → `12321`,
  9610 → `161 9449`, 1031 → `1 101 929`; CI runs all three on every push.
  It also recounts 1(c) by set arithmetic over palindromes found by testing
  every n, confirms the five sums for 54 in 1(b), and checks that every answer
  for n = 998 000 … 1 000 000 is a valid sum of minimal length.
* Q2: the modular set-up cross-checked against a literal square-by-square
  simulation for every (n ≤ 7, r ≤ 25, g ≤ 25) and every (n = 4, r, g < 50) —
  no mismatches. Every game checked to terminate leaving only single-coloured
  havens. The paper's worked tie-break example (havens 1R/0G, 2R/3G, 4R/3G,
  9R/4G → pick 4R/3G) reproduced. The amended strategy of 2(d) is played out
  over the same 90 inputs: every move legal, every safe-haven-first move
  really adds a safe haven for the mover, every game ending in single-coloured
  havens. The answers to 2(b), 2(c) (from the literal simulation) and 2(d) are
  asserted.
* Q3: the memoised solver cross-checked against a completely independent
  exact-`Fraction` brute force over 17 inputs including four-fuse cases —
  identical period *values*, not just counts. The same brute force confirms
  the nine periods of 3(b) and that each tuple quoted in 3(c) reaches 17 or 163.
