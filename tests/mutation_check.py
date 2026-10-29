"""Run curated, single-site mutants against the original gate and pytest.

Run from the repository root with the same Python environment as pytest:
    python tests/mutation_check.py --without-tests --output tests/mutations_before.json
    python tests/mutation_check.py --output tests/mutations_after.json

Only the affected checker's gate and samples need rerunning: the other gate
commands cannot import the changed module. Helpers have no original CI gate.
Each mutant gets a fresh copy under the repository; production files are never
edited. A timeout is recorded separately, never counted as a killed mutant.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


# (module, unique original text, replacement). Keep these explicit so the
# experiment can be reviewed and reproduced without a mutation dependency.
MUTANTS = [
    ("q1_palindromic_sums", "return s == s[::-1]", "return s != s[::-1]"),
    ("q1_palindromic_sums", "odd > limit and even > limit", "odd > limit or even > limit"),
    ("q1_palindromic_sums", "if odd <= limit:", "if odd < limit:"),
    ("q1_palindromic_sums", "if even <= limit:", "if even < limit:"),
    ("q1_palindromic_sums", "for a in pals:", "for a in reversed(pals):"),
    ("q1_palindromic_sums", "rest - 1) - 1", "rest - 1) - 2"),
    ("q1_check", "assert all(is_pal(x) for x in got)", "assert True"),
    ("q1_check", "assert sum(got) == n, (n, got)", "assert True, (n, got)"),
    ("q1_check", "assert list(got) == sorted(got), (n, got)\n\n        options", "assert True, (n, got)\n\n        options"),
    ("q1_check", "assert len(got) == len(options[0])", "assert True"),
    ("q1_check", "if tuple(got) != want:", "if False:"),
    ("q1_check", "if c < b:", "if c <= b:"),
    ("q1_written", "if c >= b and c in pset:", "if c > b and c in pset:"),
    ("q1_written", "if c >= b and c in pset:", "if c >= b or c in pset:"),
    ("q1_written", "if pairs:\n        return pairs", "if pairs:\n        return pairs[:1]"),
    ("q1_written", "return [(n,)]", "return []"),
    ("q2_safe_haven", "if col < n - 1:", "if col < n - 2:"),
    ("q2_safe_haven", "empties[(step - 1) % len(empties)]", "empties[step % len(empties)]"),
    ("q2_safe_haven", "if all(board[q] == player for q in comp):", "if any(board[q] == player for q in comp):"),
    ("q2_safe_haven", "if mine == 0 or theirs == 0:", "if mine == 0 and theirs == 0:"),
    ("q2_safe_haven", "key = (-theirs, mine, comp[-1])", "key = (theirs, mine, comp[-1])"),
    ("q2_safe_haven", "key = (-theirs, mine, comp[-1])", "key = (-theirs, -mine, comp[-1])"),
    ("q2_safe_haven", "key = (-theirs, mine, comp[-1])", "key = (-theirs, mine, -comp[-1])"),
    ("q2_safe_haven", "return (q, min(targets))", "return (q, max(targets))"),
    ("q2_safe_haven", "for q in best_comp:", "for q in reversed(best_comp):"),
    ("q2_safe_haven", "count_safe(board, nb, N, player) > base", "count_safe(board, nb, N, player) >= base"),
    ("q2_safe_haven", "board[q], board[t] = player, opp", "board[q], board[t] = EMPTY, player"),
    ("q2_check", "assert board[q] == player and board[t] == OTHER[player]\n", "assert True\n"),
    ("q2_check", "assert t in nb[q]\n", "assert True\n"),
    ("q2_check", "assert len({board[x] for x in comp}) == 1, (n, r, g, comp)", "assert True, (n, r, g, comp)"),
    ("q2_check", "assert count_safe(board, nb, N, player) > before, (n, r, g, mv)", "assert True, (n, r, g, mv)"),
    ("q2_check", "assert bad == 0,", "assert True,"),
    ("q3_short_fuse", "opts.append((0, 1, 2))", "opts.append((1, 2))"),
    ("q3_short_fuse", "opts.append((1, 2))", "opts.append((1,))"),
    ("q3_short_fuse", "t < dt:", "t > dt:"),
    ("q3_short_fuse", "out.add(dt + x)", "out.add(dt - x)"),
    ("q3_short_fuse", "periods = {0}", "periods = set()"),
    ("q3_short_fuse", "return sorted(Fraction(p, scale) for p in periods)", "return sorted(Fraction(p, scale + 1) for p in periods)"),
    ("q3_short_fuse", "return sorted(Fraction(p, scale) for p in periods)", "return sorted(Fraction(p, scale) for p in periods)[1:]"),
    ("q3_short_fuse", "return len(periods)", "return len(periods) + 1"),
    ("q3_check", "assert a == b,", "assert len(a) == len(b),"),
    ("q3_check", "assert sorted(brute([1, 2])) ==", "assert True or sorted(brute([1, 2])) =="),
    ("q3_check", "periods.add(now2 - e)", "periods.add(now2 + e)"),
    ("q3_written", "if x.denominator == 1", "if x.denominator != 1"),
    ("q3_written", '"%d/%d" % (x.numerator, x.denominator)', '"%d/%d" % (x.denominator, x.numerator)'),
    ("q3_search", "range(1, limit + 1)", "range(1, limit)"),
    ("q3_search", "range(b, limit + 1)", "range(b, limit)"),
]

SAMPLES = {
    "q1": [("1031", "1 101 929"), ("12321", "12321"), ("9610", "161 9449")],
    "q2": [("3 5 5", "2 1")],
    "q3": [("2 1 1", "7")],
}
PROGRAMS = {"q1": "q1_palindromic_sums", "q2": "q2_safe_haven", "q3": "q3_short_fuse"}


def run(root, command, stdin=None):
    try:
        result = subprocess.run(
            [sys.executable] + command, cwd=root, input=stdin, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30,
        )
    except subprocess.TimeoutExpired:
        return "timeout", ""
    return ("pass" if result.returncode == 0 else "killed"), result.stdout


def gate(root, module):
    if module.endswith("_written") or module == "q3_search":
        return "pass"
    question = module[:2]
    status, _ = run(root, [question + "_check.py"])
    if status != "pass":
        return status
    if module == PROGRAMS[question]:
        # The CLI banners are on stderr, which the CI sample comparison ignores.
        for stdin, expected in SAMPLES[question]:
            code = (
                "import subprocess, sys; "
                "p = subprocess.run([sys.executable, %r], input=%r, text=True, capture_output=True); "
                "assert p.returncode == 0 and p.stdout.rstrip('\\n') == %r"
            ) % (module + ".py", stdin + "\n", expected)
            status, _ = run(root, ["-c", code])
            if status != "pass":
                return status
    return "pass"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--without-tests", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    results = []
    # Calibrate the unmodified gate/tests first; pre-existing failures must not
    # be mistaken for killed mutants.
    for question in SAMPLES:
        assert gate(root, PROGRAMS[question]) == "pass", "unmodified gate failed"
    if not args.without_tests:
        status, output = run(root, ["-m", "pytest", "-q"])
        assert status == "pass", output
    for number, (module, original, replacement) in enumerate(MUTANTS, 1):
        source = (root / (module + ".py")).read_text()
        # A couple of repeated assertions/ranges intentionally target the first
        # occurrence; its exact source line is included in the output.
        assert original in source, (module, original)
        line = source[:source.index(original)].count("\n") + 1
        mutated = source.replace(original, replacement, 1)
        compile(mutated, module + ".py", "exec")
        with tempfile.TemporaryDirectory(prefix=".mutation-", dir=root) as tmp:
            dest = Path(tmp)
            for path in root.glob("*.py"):
                shutil.copy2(path, dest / path.name)
            shutil.copytree(root / "tests", dest / "tests", ignore=shutil.ignore_patterns("__pycache__", "*.json", "*.md"))
            (dest / (module + ".py")).write_text(mutated)
            gate_status = gate(dest, module)
            test_status = "not run"
            if not args.without_tests:
                test_status, _ = run(dest, ["-m", "pytest", "-q", "-x"])
            killed = gate_status == "killed" or test_status == "killed"
            result = dict(id=number, module=module, line=line, original=original,
                          replacement=replacement, gate=gate_status, pytest=test_status,
                          outcome="killed" if killed else "survived")
            if "timeout" in (gate_status, test_status):
                result["outcome"] = "timeout"
            results.append(result)
            print("%02d %-22s gate=%-7s pytest=%-7s %s" %
                  (number, module, gate_status, test_status, result["outcome"]), flush=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    for module in sorted({row["module"] for row in results}):
        counts = Counter(row["outcome"] for row in results if row["module"] == module)
        print(module, dict(counts))


if __name__ == "__main__":
    main()
