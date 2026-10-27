"""Exact diagnostic worlds and candidate traces; no admitted EPS selector."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
import time

sys.dont_write_bytecode = True
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["GIT_OPTIONAL_LOCKS"] = "0"
UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
BASE = ROOT / "data/accounting-master"
PRIOR = BASE / "r05-dependent-loss-source-20261018"
INTEGRATION = BASE / "early-conversion-integration-20261018"
SUPPLEMENT = INTEGRATION / "r03-eps-order-discriminator-supplement.json"
PLAN = ROOT / "docs/plans/accounting-r03-eps-order-discriminator-20261018.md"
CONTROLS = ["docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
            "docs/plans/accounting-mission-requirements.md", "data/accounting-master/next-plan.md"]
SERIES = {"A": (Q(10), 40), "B": (Q(60), 34), "C": (Q(10), 8)}
SUBSETS = [(), ("A",), ("B",), ("C",), ("A", "B"), ("A", "C"),
           ("B", "C"), ("A", "B", "C")]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text())


def write_new(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def dirty():
    raw = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=no", "-z"],
        cwd=ROOT, text=True)
    rows = raw.split("\0")
    rows = [r for r in rows if r]
    assert all(r[:2] == " M" for r in rows)
    return {r[3:]: sha(ROOT / r[3:]) for r in rows}


def prepare():
    assert not (UNIT / "protection.json").exists(), "prepare is one-time only"
    prior_check = subprocess.run([sys.executable, str(PRIOR / "complete.py")], cwd=ROOT,
                                 text=True, capture_output=True, check=True)
    assert json.loads(prior_check.stdout)["completion"] == "read-only replay passed"
    previous = load(PRIOR / "protection.json")
    paths = {ROOT / name for name in previous["protected"]}
    paths.update(ROOT / name for name in load(PRIOR / "completion.json")["bindings"])
    paths.add(PRIOR / "completion.json")
    paths.update(ROOT / name for name in load(PRIOR / "source-manifest.json")["entries"])
    paths.update([PLAN,
        ROOT / "docs/plans/accounting-dependent-eps-20261016.md",
        ROOT / "docs/plans/accounting-dependent-eps-source-selection-20261017.md",
        ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/sections/dependent-eps.tex",
        BASE / "dependent-eps-20261016/semantic-contract.md",
        BASE / "dependent-eps-20261016/authored-cases.json"])
    paths.update(p for p in (BASE / "dependent-eps-source-selection-20261017").iterdir() if p.is_file())
    current = dirty()
    assert len(current) == 36 and git("diff", "--cached", "--name-only") == ""
    snapshots = {}
    for name in CONTROLS:
        target = UNIT / "controls-before" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write((ROOT / name).read_bytes())
        snapshots[str(target.relative_to(ROOT))] = sha(target)
    write_new(UNIT / "protection.json", {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
        "index_sha256": sha(ROOT / ".git/index"), "tracked_dirty": current,
        "protected": {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)},
        "control_snapshots": snapshots,
    })
    print(json.dumps({"prepared": True, "protected_files": len(paths), "tracked_dirty": len(current)}))


def preservation():
    baseline = load(UNIT / "protection.json")
    assert git("rev-parse", "HEAD") == baseline["head"]
    assert git("branch", "--show-current") == baseline["branch"]
    assert sha(ROOT / ".git/index") == baseline["index_sha256"]
    assert git("diff", "--cached", "--name-only") == ""
    current = dirty()
    assert current.keys() == baseline["tracked_dirty"].keys()
    for name, expected in baseline["tracked_dirty"].items():
        if name not in CONTROLS:
            assert current[name] == expected, name
    for group in ("protected", "control_snapshots"):
        for name, expected in baseline[group].items():
            assert sha(ROOT / name) == expected, name
    a, o = [load(INTEGRATION / name) for name in ("assessment-successor.json", "operation-successor.json")]
    assert (len(a["rows"]), len(a["interactions"]), len(o["rows"])) == (53, 6, 46)
    assert a["readiness"] == o["readiness"] == "not_ready"
    return baseline


def world(selected, n=72, q=Q(1, 2)):
    x = Q(90) + sum((SERIES[i][0] for i in selected), Q(0))
    bonus = q * max(x - 100, 0)
    tax = (x - bonus) / 5
    earnings = x - bonus - tax
    shares = n + sum(SERIES[i][1] for i in selected)
    return {"pretax": x, "bonus": bonus, "tax": tax, "earnings": earnings,
            "shares": shares, "ratio": earnings / shares}


def encode_world(selected, n=72, q=Q(1, 2)):
    return {"subset": list(sorted(selected)), **{k: str(v) for k, v in world(selected, n, q).items()}}


def incremental(selected, issue, n=72, q=Q(1, 2)):
    return (world([*selected, issue], n, q)["earnings"] - world(selected, n, q)["earnings"]) / SERIES[issue][1]


def trace(policy, n=72, q=Q(1, 2), order=None):
    selected, rows = [], []
    remaining = list(order) if order is not None else sorted(SERIES, key=lambda i: (incremental([], i, n, q), i))
    while remaining:
        if policy == "marginal":
            remaining.sort(key=lambda i: (incremental(selected, i, n, q), i))
        issue = remaining.pop(0)
        current, trial = world(selected, n, q), world([*selected, issue], n, q)
        # Cross-product comparison is independent of the Fraction ratio field.
        decrease = trial["earnings"] * current["shares"] < current["earnings"] * trial["shares"]
        assert decrease == (trial["ratio"] < current["ratio"])
        rows.append({"issue": issue, "current": str(current["ratio"]),
                     "incremental": str(incremental(selected, issue, n, q)),
                     "trial": str(trial["ratio"]), "accepted": decrease,
                     "strict_decision": trial["ratio"] != current["ratio"]})
        if decrease:
            selected.append(issue)
    return {"policy": policy, "order": [r["issue"] for r in rows], "trace": rows,
            "accepted": sorted(selected), "ratio": str(world(selected, n, q)["ratio"]),
            "accounting_admission": "not_evaluated"}


def calculate():
    checks = []

    def require(name, condition):
        assert condition, name
        checks.append(name)

    # Hand expectations were recorded in the plan before any calculation.
    expected = [(90, 0, 18, 72, 72), (100, 0, 20, 80, 112), (150, 25, 25, 100, 106),
                (100, 0, 20, 80, 80), (160, 30, 26, 104, 146), (110, 5, 21, 84, 120),
                (160, 30, 26, 104, 114), (170, 35, 27, 108, 154)]
    for subset, wanted in zip(SUBSETS, expected):
        w = world(subset)
        name = "".join(subset) or "empty"
        for key, value in zip(("pretax", "bonus", "tax", "earnings", "shares"), wanted):
            require(name + ".hand_" + key, w[key] == value)
        require(name + ".conservation", w["bonus"] + w["tax"] + w["earnings"] == w["pretax"])
        # A separate piecewise expression eliminates bonus and tax variables.
        affine = Q(4, 5) * w["pretax"] if w["pretax"] <= 100 else Q(2, 5) * w["pretax"] + 40
        require(name + ".independent_piecewise_earnings", affine == w["earnings"])
        require(name + ".positive_denominator", w["shares"] > 0)
    require("standalone_ratios", [incremental([], i) for i in "ABC"] == [Q(1, 5), Q(14, 17), Q(1)])
    require("after_A_ratios", [incremental(["A"], i) for i in "BC"] == [Q(12, 17), Q(1, 2)])
    require("strict_rank_reversal", incremental([], "B") < incremental([], "C") and
            incremental(["A"], "B") > incremental(["A"], "C"))
    fixed, marginal = trace("fixed"), trace("marginal")
    require("fixed_order", fixed["order"] == list("ABC"))
    require("fixed_accepts_all", fixed["accepted"] == list("ABC") and fixed["ratio"] == "54/77")
    require("marginal_order", marginal["order"] == list("ACB"))
    require("marginal_excludes_B", marginal["accepted"] == list("AC") and marginal["ratio"] == "7/10")
    require("main_evaluated_decisions_strict", all(r["strict_decision"] for t in (fixed, marginal) for r in t["trace"]))
    require("final_difference", Q(fixed["ratio"]) - Q(marginal["ratio"]) == Q(1, 770))
    require("fixed_B_removal_lowers_ratio", world("AC")["ratio"] < world("ABC")["ratio"])
    minima = [list(s) for s in SUBSETS if world(s)["ratio"] == min(world(t)["ratio"] for t in SUBSETS)]
    require("descriptive_subset_envelope", minima == [list("AC")])
    permutations = [trace("prescribed_permutation", order=p) for p in itertools.permutations("ABC")]
    wanted = {"ABC": ("ABC", "54/77"), "ACB": ("AC", "7/10"),
              "BAC": ("ABC", "54/77"), "BCA": ("ABC", "54/77"),
              "CAB": ("AB", "52/73"), "CBA": ("AB", "52/73")}
    for row in permutations:
        require("permutation_" + "".join(row["order"]),
                ("".join(row["accepted"]), row["ratio"]) == wanted["".join(row["order"])] )
    upper = Q(80 * 34, 24) - 40
    lower = Q(84 * 34, 24) - 48
    require("analytic_interval", (lower, upper) == (Q(71), Q(220, 3)))
    boundaries = []
    for n in (71, 72, 73, 74):
        f, m = trace("fixed", n), trace("marginal", n)
        gap = Q(f["ratio"]) - Q(m["ratio"])
        require("strict_interval_" + str(n), (gap > 0) == (lower < n < upper))
        require("candidate_gap_" + str(n), gap == (Q(24 * (n - 71), (n + 82) * (n + 48)) if n < upper else 0))
        boundaries.append({"ordinary_shares": n, "fixed": f, "marginal": m, "gap": str(gap)})
    require("upper_boundary_equality", Q(80) / (upper + 40) == Q(12, 17))
    require("lower_boundary_equality", Q(84) / (lower + 48) == Q(12, 17))
    additive = [trace(p, q=Q(0)) for p in ("fixed", "marginal")]
    require("additive_orders_agree", all(t["order"] == list("ACB") for t in additive))
    require("additive_selection_agrees", all(t["accepted"] == ["A"] and t["ratio"] == "5/7" for t in additive))
    for subset in SUBSETS:
        actual = world(subset, q=Q(0))["earnings"] - world([], q=Q(0))["earnings"]
        standalone = sum((incremental([], i, q=Q(0)) * SERIES[i][1] for i in subset), Q(0))
        require("additive_effect_" + ("".join(subset) or "empty"), actual == standalone)
    inherited = []
    for p, targets in ((80, (64, 80, 88)), (90, (72, 84, 92))):
        amounts = []
        for count, expected_n in enumerate(targets):
            x = Q(p + 20 * count)
            actual = Q(4, 5) * (x - max(x - 100, 0) / 2)
            require("inherited_P%d_%d" % (p, count), actual == expected_n)
            amounts.append(str(actual))
        inherited.append({"pretax": p, "earnings": amounts})
    source = (BASE / "dependent-eps-source-selection-20261017/aasb133-2020.txt").read_text()
    require("retained_consequence_anchor", "profit-sharing plan" in source)
    require("retained_sequential_anchor", "each issue or series" in source and "earnings per incremental" in source)
    return ({"scope": "Unadmitted three-series documentary discriminator; no production method mutation",
             "worlds": [encode_world(s) for s in SUBSETS], "fixed": fixed, "marginal": marginal,
             "permutations": permutations, "boundaries": boundaries, "additive_control": additive,
             "inherited_two_series": inherited, "descriptive_minimizing_subsets": minima,
             "final_diluted_eps": None, "selection_status": "not_evaluated",
             "empirical_admissions": 0, "whole_rows_closed": 0},
            {"status": "passed", "count": len(checks), "checks": checks,
             "stochastic_experiments": 0, "accounting_rule_promotions": 0})


def record():
    for name in ("completion.json", "controls-after"):
        assert not (UNIT / name).exists(), name + " already exists"
    assert not SUPPLEMENT.exists()
    for name in ("derivation.md", "source-boundary.md", "result.md", "run-manifest.json"):
        assert (UNIT / name).is_file(), name + " missing"
    snapshots = []
    for name in CONTROLS:
        destination = UNIT / "controls-after" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as handle:
            handle.write((ROOT / name).read_bytes())
        snapshots.append({"live_path": name, **binding(destination)})
    write_new(SUPPLEMENT, {
        "candidate_pdf": binding(ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"),
        "protected_assessment": binding(INTEGRATION / "assessment-successor.json"),
        "protected_integration": binding(INTEGRATION / "integration-bindings.json"),
        "protected_operations": binding(INTEGRATION / "operation-successor.json"),
        "additional_evidence": [binding(UNIT / name) for name in (
            "result.md", "derivation.md", "source-boundary.md", "calculations.json", "checks.json", "run-manifest.json")],
        "scope": "R03 exact three-series discriminator; fixed versus recomputed ranking differ; no general selector admitted",
        "all_original_obligations": 53, "interactions": 6, "operations": 46,
        "whole_rows_closed": 0, "readiness": "not_ready", "independent_domain_human_acceptance": "pending",
    })
    paths = [p for p in UNIT.iterdir() if p.is_file() and p.name != "completion.json"]
    paths += [p for d in ("controls-before", "controls-after") for p in (UNIT / d).rglob("*") if p.is_file()]
    paths += [PLAN, SUPPLEMENT]
    write_new(UNIT / "completion.json", {
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "command": shlex.join([sys.executable, *sys.argv]),
        "bindings": {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)},
        "controls_at_completion": snapshots,
        "control_replay_policy": "Immutable before/after snapshots; live controls may advance in authorised successor units.",
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    for name in ("prepare", "calculate", "record"):
        modes.add_argument("--" + name, action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
        return
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    baseline = preservation()
    data, checks = calculate()
    if args.calculate:
        for name in ("calculations.json", "checks.json", "run-manifest.json"):
            assert not (UNIT / name).exists(), name + " already exists"
        write_new(UNIT / "calculations.json", data)
        write_new(UNIT / "checks.json", checks)
        write_new(UNIT / "run-manifest.json", {
            "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
            "validation_wall_seconds": time.monotonic() - tick,
            "command": shlex.join([sys.executable, *sys.argv]),
            "git_commit": baseline["head"], "index_sha256": baseline["index_sha256"],
            "staging": "empty; unchanged", "tracked_dirty_paths": len(baseline["tracked_dirty"]),
            "environment": {"python_executable": sys.executable, "python_version": platform.python_version(),
                            "environment_path": str(Path(sys.executable).parent.parent), "imports": "standard library only"},
            "cpu_gpu_status": "CPU only; GPUs intentionally hidden by CUDA_VISIBLE_DEVICES=-1; no framework/GPU initialization",
            "data_version": "N/A: supplied synthetic terms; no empirical outcomes",
            "random_seeds": "N/A: exact deterministic derivation checks",
            "plan": binding(PLAN), "protected_inputs": binding(UNIT / "protection.json"),
            "result_file": str((UNIT / "result.md").relative_to(ROOT)),
            "artifacts": [binding(UNIT / name) for name in ("calculations.json", "checks.json", "verify.py")],
            "checks": checks["count"], "whole_rows_closed": 0,
        })
    assert load(UNIT / "calculations.json") == data
    assert load(UNIT / "checks.json") == checks
    if args.record:
        record()
    if (UNIT / "completion.json").exists():
        completion = load(UNIT / "completion.json")
        for name, expected in completion["bindings"].items():
            assert sha(ROOT / name) == expected, name
        for row in completion["controls_at_completion"]:
            assert row["live_path"] in CONTROLS and sha(ROOT / row["path"]) == row["sha256"]
        supplement = load(SUPPLEMENT)
        for key in ("candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"):
            row = supplement[key]
            assert binding(ROOT / row["path"]) == row
        for row in supplement["additional_evidence"]:
            assert binding(ROOT / row["path"]) == row
        assert (supplement["all_original_obligations"], supplement["interactions"], supplement["operations"],
                supplement["whole_rows_closed"], supplement["readiness"]) == (53, 6, 46, 0, "not_ready")
        status = "recorded and verified" if args.record else "read-only replay passed"
    else:
        status = "calculated; completion not yet recorded"
    preservation()
    print(json.dumps({"status": status, "checks": checks["count"], "worlds": len(data["worlds"]),
                      "permutations": len(data["permutations"]), "fixed_ratio": data["fixed"]["ratio"],
                      "marginal_ratio": data["marginal"]["ratio"], "rule_promotions": 0, "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
