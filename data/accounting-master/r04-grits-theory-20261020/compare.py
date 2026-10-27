"""Exact finite audit; standard library only; never loads acquired code."""
from collections import Counter
from copy import deepcopy
from difflib import SequenceMatcher
from fractions import Fraction
import hashlib
import inspect
import itertools
import json
from pathlib import Path
import platform

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]


def chains(m, n):
    for k in range(min(m, n) + 1):
        for left in itertools.combinations(range(m), k):
            for right in itertools.combinations(range(n), k):
                yield tuple(zip(left, right))


def exhaustive_sequence(a, b, reward):
    return max(sum(reward(a[i], b[j]) for i, j in path) for path in chains(len(a), len(b)))


def align(a, b, reward):
    # Local recurrence from the inspected mathematical algorithm, with explicit
    # original-code tie order. The exhaustive oracle uses no DP recurrence.
    m, n = len(a), len(b)
    scores = [[0] * (n + 1) for _ in range(m + 1)]
    choices = {}
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            candidates = (scores[i-1][j-1] + reward(a[i-1], b[j-1]),
                          scores[i-1][j], scores[i][j-1])
            scores[i][j] = max(candidates)
            choices[i, j] = candidates.index(scores[i][j])
    path = []
    i, j = m, n
    while i and j:
        choice = choices[i, j]
        if choice == 0:
            path.append((i-1, j-1))
            i, j = i-1, j-1
        elif choice == 1:
            i -= 1
        else:
            j -= 1
    return scores[m][n], tuple(reversed(path))


def lcs_length(a, b):
    return align(a, b, lambda x, y: int(x == y))[0]


def exhaustive_lcs(a, b):
    def subsequences(s):
        return {tuple(s[i] for i in indices) for k in range(len(s)+1)
                for indices in itertools.combinations(range(len(s)), k)}
    return max(map(len, subsequences(a) & subsequences(b)))


def grid_scores(a, b):
    assert len(a) == len(b) == 2 and all(len(row) == 2 for row in a+b)
    eq = lambda x, y: int(x == y)
    inner = lambda x, y: align(x, y, eq)[0]
    inner_oracle = lambda x, y: exhaustive_sequence(x, y, eq)
    for x in a:
        for y in b:
            assert inner(x, y) == inner_oracle(x, y)
    ur, rows = align(a, b, inner)
    assert ur == exhaustive_sequence(a, b, inner_oracle)
    at, bt = list(zip(*a)), list(zip(*b))
    uc, columns = align(at, bt, inner)
    assert uc == exhaustive_sequence(at, bt, inner_oracle)
    score = lambda rs, cs: sum(eq(a[i][k], b[j][l]) for i,j in rs for k,l in cs)
    lower = score(rows, columns)
    exact = max(score(rs, cs) for rs in chains(2, 2) for cs in chains(2, 2))
    upper = min(ur, uc)
    assert 0 <= lower <= exact <= upper <= 4
    identity = sum(eq(a[i][j], b[i][j]) for i in range(2) for j in range(2))
    row_identity = sum(eq(a[i][c], b[j][c]) for i,j in rows for c in range(2))
    shortcut = "none"
    current_lower, current_upper = lower, upper
    if identity >= 2:
        shortcut = "identity"
        current_lower = current_upper = identity
        assert identity == exact
    elif row_identity >= len(rows) * 2 - 1:
        shortcut = "row-identity"
        current_lower = current_upper = row_identity
        assert row_identity == exact == ur
    return {"lower_raw": lower, "exact_raw": exact, "upper_raw": upper,
            "row_relaxation": ur, "column_relaxation": uc,
            "rows": [list(x) for x in rows], "columns": [list(x) for x in columns],
            "lower_normalised": str(Fraction(lower, 4)),
            "exact_normalised": str(Fraction(exact, 4)),
            "upper_normalised": str(Fraction(upper, 4)),
            "current_shortcut": shortcut, "current_lower_raw": current_lower,
            "current_upper_raw": current_upper}


def calculate():
    strings = []
    for name, a, b in (("short", "aaa", "abaa"), ("order-forward", "tide", "diet"),
                       ("order-reverse", "diet", "tide"), ("popular", "x"*200, "y"+"x"*200)):
        exact = lcs_length(a, b)
        if max(len(a), len(b)) <= 4:
            assert exact == exhaustive_lcs(a, b)
        else:
            assert exact == min(len(a), len(b)) == 200
            assert a == b[1:]
        matcher = SequenceMatcher(None, a, b)
        blocks = [[x.a, x.b, x.size] for x in matcher.get_matching_blocks()]
        count = sum(x[2] for x in blocks)
        without_autojunk = sum(x.size for x in SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks())
        strings.append({"name": name, "a": a, "b": b, "lcs_length": exact,
            "matching_blocks": blocks, "sequence_matcher_count": count,
            "claimed_lcs_reward": str(Fraction(2*exact, len(a)+len(b))),
            "computed_block_reward": str(Fraction(2*count, len(a)+len(b))),
            "count_without_autojunk": without_autojunk,
            "default_autojunk": matcher.autojunk})
    a, b = [["a","b"],["b","a"]], [["b","a"],["a","b"]]
    fixed = grid_scores(a, b)
    assert (fixed["lower_raw"], fixed["exact_raw"], fixed["upper_raw"]) == (0, 2, 2)
    grids = [[list(bits[:2]), list(bits[2:])] for bits in itertools.product("ab", repeat=4)]
    summary, shortcuts = Counter(), Counter()
    for x in grids:
        for y in grids:
            score = grid_scores(x, y)
            summary["pairs"] += 1
            summary["lower_equals_exact"] += int(score["lower_raw"] == score["exact_raw"])
            summary["lower_strictly_below_exact"] += int(score["lower_raw"] < score["exact_raw"])
            summary["upper_equals_exact"] += int(score["upper_raw"] == score["exact_raw"])
            summary["upper_strictly_above_exact"] += int(score["upper_raw"] > score["exact_raw"])
            shortcuts[score["current_shortcut"]] += 1
            transposed = grid_scores([list(z) for z in zip(*x)], [list(z) for z in zip(*y)])
            assert score["lower_raw"] == transposed["lower_raw"]
    source = Path(inspect.getsourcefile(SequenceMatcher))
    return {"strings": strings, "grid_witness": {"a": a, "b": b, **fixed},
            "binary_2x2_domain": dict(summary), "current_shortcuts": dict(shortcuts),
            "stdlib": {"python": platform.python_version(), "source": str(source),
                       "sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
            "upstream_executed": False, "historical_experiment_reproduced": False}


def check():
    def load(name):
        return json.loads((UNIT / name).read_text())
    count = 0
    def require(condition, label):
        nonlocal count
        assert condition, label
        count += 1
    ledger = load("source-ledger.json")
    for row in ledger["acquisitions"]:
        for field in ("body", "headers", "receipt"):
            item = row[field]
            require(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], field)
        r = json.loads((ROOT / row["receipt"]["path"]).read_text())
        require(r["exitcode"] == 0 and r["http_code"] == 200, "HTTP success")
        require(r["size_download"] == (ROOT / row["body"]["path"]).stat().st_size, "receipt size")
    for row in ledger["passages"]:
        line = (ROOT / row["path"]).read_text().splitlines()[row["line"]-1]
        require(row["quote"] in line, row["id"])
    tree = load("sources/04-tree.json")
    require(tree["truncated"] is False, "tree complete flag")
    for name, original in (("05-metric.py", "src/grits.py"), ("06-eval.py", "src/eval.py")):
        body = (UNIT / "sources" / name).read_bytes()
        blob = hashlib.sha1(b"blob "+str(len(body)).encode()+b"\0"+body).hexdigest()
        entry = next(x for x in tree["tree"] if x["path"] == original)
        require(blob == entry["sha"] and len(body) == entry["size"], "git blob " + original)
    computed = calculate()
    require(computed == load("witnesses.json"), "independent exact replay")
    rejected = []
    for label, edit in (
        ("lower treated as optimum", lambda w: w["grid_witness"].update(exact_raw=0)),
        ("bound changed", lambda w: w["grid_witness"].update(upper_raw=0)),
        ("SequenceMatcher called exact LCS", lambda w: w["strings"][0].update(sequence_matcher_count=3)),
        ("autojunk hidden", lambda w: w["strings"][3].update(default_autojunk=False)),
        ("upstream execution invented", lambda w: w.update(upstream_executed=True)),
        ("historical equivalence invented", lambda w: w.update(historical_experiment_reproduced=True)),
    ):
        changed = deepcopy(computed)
        edit(changed)
        require(changed != computed, label)
        rejected.append(label)
    for name in ("source-support", "citation-venue", "backward-snowball", "forward-snowball", "claim-support", "omission-risk"):
        require(bool(load(name+"-ledger.json")), name)
    return {"status": "passed", "acquisitions": len(ledger["acquisitions"]),
            "source_anchors": len(ledger["passages"]), "assertions": count,
            "exact_grid_pairs": computed["binary_2x2_domain"]["pairs"], "string_witnesses": 4,
            "rejected_controls": len(rejected), "whole_rows_closed": 0}
