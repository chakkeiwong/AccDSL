"""Exact attribution diagnostics; no accounting allocation or runtime method."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
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
PRIOR = BASE / "r03-eps-order-discriminator-20261018"
INTEGRATION = BASE / "early-conversion-integration-20261018"
SUPPLEMENT = INTEGRATION / "r03-hedge-attribution-discriminator-supplement.json"
PLAN = ROOT / "docs/plans/accounting-r03-hedge-attribution-discriminator-20261018.md"
SOURCE = ROOT / "docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt"
CONTROLS = ["docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
            "docs/plans/accounting-mission-requirements.md", "data/accounting-master/next-plan.md"]


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
    raw = subprocess.check_output(["git", "status", "--porcelain=v1", "--untracked-files=no", "-z"],
                                  cwd=ROOT, text=True)
    rows = [row for row in raw.split("\0") if row]
    assert all(row[:2] == " M" for row in rows)
    return {row[3:]: sha(ROOT / row[3:]) for row in rows}


def prepare():
    assert not (UNIT / "protection.json").exists(), "prepare is one-time"
    replay = subprocess.run([sys.executable, str(PRIOR / "verify.py")], cwd=ROOT,
                            text=True, capture_output=True, check=True)
    assert json.loads(replay.stdout)["status"] == "read-only replay passed"
    paths = {ROOT / name for name in load(PRIOR / "protection.json")["protected"]}
    paths.update(ROOT / name for name in load(PRIOR / "completion.json")["bindings"])
    paths.add(PRIOR / "completion.json")
    paths.update([PLAN, SOURCE, UNIT / "authored-targets.json", UNIT / "derivation.md", UNIT / "verify.py"])
    for directory in ("origin-matched-cessation-20261017", "partial-hedge-discontinuation-20261016",
                      "added-instruments-20261016", "financing-modifications-net-hedges-20261015"):
        paths.update(p for p in (BASE / directory).iterdir() if p.is_file())
    for name in ("accounting-origin-matched-cessation-20261017.md",
                 "accounting-added-instruments-20261016.md",
                 "accounting-partial-hedge-discontinuation-20261016.md",
                 "accounting-financing-modifications-net-hedges-20261015.md"):
        paths.add(ROOT / "docs/plans" / name)
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
        "started_utc": datetime.now(timezone.utc).isoformat(), "head": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"), "index_sha256": sha(ROOT / ".git/index"),
        "tracked_dirty": current, "protected": {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)},
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
    assessment = load(INTEGRATION / "assessment-successor.json")
    operations = load(INTEGRATION / "operation-successor.json")
    assert (len(assessment["rows"]), len(assessment["interactions"]), len(operations["rows"])) == (53, 6, 46)
    assert assessment["readiness"] == operations["readiness"] == "not_ready"
    return baseline


def sign(value):
    return (value > 0) - (value < 0)


def reserve(x, y):
    if x * y < 0:
        raise ValueError("aggregate cumulative changes do not offset in the supplied orientation")
    return sign(x) * min(abs(x), abs(y))


def calculate():
    target = load(UNIT / "authored-targets.json")
    names = []

    def check(name, condition):
        assert name not in names, name
        assert condition, name
        names.append(name)

    rows = []
    for expected in target["cases"]:
        label = expected["id"]
        x, y = [[Q(v) for v in expected[key]] for key in ("x", "y")]
        check(label + ":shape", len(x) == len(y) == 2)
        check(label + ":component-orientation", all(a * b >= 0 for a, b in zip(x, y)))
        X, Y = sum(x, Q(0)), sum(y, Q(0))
        R = reserve(X, Y)
        L = sum((reserve(a, b) for a, b in zip(x, y)), Q(0))
        row = {"id": label, "x": expected["x"], "y": expected["y"],
               **{key: str(value) for key, value in
                  {"X": X, "Y": Y, "R": R, "L": L, "profit": X-R, "gap": R-L}.items()}}
        if all(value >= 0 for value in x+y):
            U = sum((max(a-b, 0) for a, b in zip(x, y)), Q(0))
            V = sum((max(b-a, 0) for a, b in zip(x, y)), Q(0))
            row.update(U=str(U), V=str(V))
            check(label + ":min-defect", R-L == min(U, V))
            check(label + ":equality-condition", (R == L) ==
                  (all(a <= b for a, b in zip(x, y)) or all(a >= b for a, b in zip(x, y))))
            check(label + ":nonnegative-defect", R >= L)
        for key, value in expected.items():
            check(label + ":hand-" + key, row[key] == value)
        alternate = sign(X) * (abs(X)+abs(Y)-abs(abs(X)-abs(Y))) / 2
        check(label + ":independent-min-identity", R == alternate)
        check(label + ":gain-conservation", Q(row["R"])+Q(row["profit"]) == X)
        if x == y:
            check(label + ":exact-match", R == L == X)
        rows.append(row)

    allocations = []
    for expected in target["decompositions"]:
        t = Q(expected["t"])
        a, b = 10+t, 8-t
        frozen = a/2
        retained, profit = 18-frozen, 2+frozen
        row = {key: str(value) for key, value in {"t": t, "rA": a, "rB": b,
               "frozen": frozen, "retained": retained, "profit_after_cancel": profit}.items()}
        prefix = "decomposition-" + str(t)
        for key, value in expected.items():
            check(prefix + ":hand-" + key, row[key] == value)
        check(prefix + ":weak-caps", 0 <= a <= 12 and 0 <= b <= 8)
        check(prefix + ":aggregate", a+b == 18)
        check(prefix + ":before-cancel", retained+frozen+2 == 20)
        check(prefix + ":after-cancel", retained+profit == 20)
        check(prefix + ":interval", 0 <= t <= 2 and 5 <= frozen <= 6)
        allocations.append(row)
    check("distinct-releases", len({r["frozen"] for r in allocations}) == 3)
    check("strict-unsigned-disagreement", rows[0]["gap"] == "4")
    check("strict-signed-disagreement", rows[4]["gap"] == "-1" and rows[5]["gap"] == "1")
    rejected = target["refused_diagnostic"]
    try:
        reserve(sum(map(Q, rejected["x"])), sum(map(Q, rejected["y"])))
    except ValueError as error:
        reason = str(error)
    else:
        raise AssertionError("nonoffset diagnostic was not refused")
    check("nonoffset-domain-refusal", reason == rejected["reason"])
    return {"cases": rows, "decompositions": allocations, "nonoffset_refusal": reason,
            "allocation_admitted": False, "whole_rows_closed": 0}, {"status": "passed", "count": len(names), "names": names}


def record():
    assert not (UNIT / "completion.json").exists() and not (UNIT / "controls-after").exists()
    assert not SUPPLEMENT.exists()
    for name in ("result.md", "derivation.md", "source-boundary.md", "run-manifest.json"):
        assert (UNIT / name).is_file(), name
    snapshots = []
    for name in CONTROLS:
        target = UNIT / "controls-after" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write((ROOT / name).read_bytes())
        snapshots.append({"live_path": name, **binding(target)})
    write_new(SUPPLEMENT, {
        "candidate_pdf": binding(ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"),
        "protected_assessment": binding(INTEGRATION / "assessment-successor.json"),
        "protected_integration": binding(INTEGRATION / "integration-bindings.json"),
        "protected_operations": binding(INTEGRATION / "operation-successor.json"),
        "additional_evidence": [binding(UNIT / name) for name in
            ("derivation.md", "source-boundary.md", "result.md", "authored-targets.json",
             "calculations.json", "checks.json", "run-manifest.json")],
        "scope": "R03 relationship/origin lower-of discriminator and conditional non-identification; no accounting allocation admitted",
        "all_original_obligations": 53, "interactions": 6, "operations": 46,
        "whole_rows_closed": 0, "readiness": "not_ready", "independent_domain_human_acceptance": "pending",
    })
    paths = [p for p in UNIT.iterdir() if p.is_file() and p.name != "completion.json"]
    paths += [p for directory in ("controls-before", "controls-after") for p in (UNIT / directory).rglob("*") if p.is_file()]
    paths += [PLAN, SUPPLEMENT]
    write_new(UNIT / "completion.json", {
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "command": shlex.join([sys.executable, *sys.argv]),
        "bindings": {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)},
        "controls_at_completion": snapshots,
        "control_replay_policy": "Immutable snapshots; live controls may advance in authorised successor units.",
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    for name in ("prepare", "calculate", "record"):
        modes.add_argument("--"+name, action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
        return
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    baseline = preservation()
    data, checks = calculate()
    if args.calculate:
        for name in ("calculations.json", "checks.json", "run-manifest.json"):
            assert not (UNIT / name).exists(), name
        write_new(UNIT / "calculations.json", data)
        write_new(UNIT / "checks.json", checks)
        write_new(UNIT / "run-manifest.json", {
            "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
            "validation_wall_seconds": time.monotonic()-tick,
            "command": shlex.join([sys.executable, *sys.argv]), "git_commit": baseline["head"],
            "index_sha256": baseline["index_sha256"], "staging": "empty; unchanged",
            "tracked_dirty_paths": len(baseline["tracked_dirty"]),
            "environment": {"python_executable": sys.executable, "python_version": platform.python_version(),
                            "environment_path": str(Path(sys.executable).parent.parent), "imports": "standard library only"},
            "cpu_gpu_status": "CPU only; CUDA_VISIBLE_DEVICES=-1 intentionally hides GPUs; no framework initialization",
            "data_version": "N/A: exact supplied synthetic marks; no empirical outcomes",
            "random_seeds": "N/A: deterministic algebra and fixed witnesses",
            "plan": binding(PLAN), "result_file": str((UNIT / "result.md").relative_to(ROOT)),
            "source": binding(SOURCE), "protected_inputs": binding(UNIT / "protection.json"),
            "artifacts": [binding(UNIT / name) for name in
                          ("calculations.json", "checks.json", "authored-targets.json", "verify.py", "derivation.md")],
            "checks": checks["count"], "allocation_admissions": 0, "whole_rows_closed": 0,
        })
    assert load(UNIT / "calculations.json") == data
    assert load(UNIT / "checks.json") == checks
    if args.record:
        record()
    status = "calculated; completion not yet recorded"
    if (UNIT / "completion.json").exists():
        completion = load(UNIT / "completion.json")
        for name, expected in completion["bindings"].items():
            assert sha(ROOT / name) == expected, name
        for row in completion["controls_at_completion"]:
            assert row["live_path"] in CONTROLS and binding(ROOT / row["path"]) == {
                "path": row["path"], "sha256": row["sha256"]}
        supplement = load(SUPPLEMENT)
        for key in ("candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"):
            row = supplement[key]
            assert binding(ROOT / row["path"]) == row
        for row in supplement["additional_evidence"]:
            assert binding(ROOT / row["path"]) == row
        assert (supplement["all_original_obligations"], supplement["interactions"], supplement["operations"],
                supplement["whole_rows_closed"], supplement["readiness"]) == (53, 6, 46, 0, "not_ready")
        status = "recorded and verified" if args.record else "read-only replay passed"
    preservation()
    print(json.dumps({"status": status, "checks": checks["count"], "cases": len(data["cases"]),
                      "decompositions": len(data["decompositions"]), "unsigned_gap": data["cases"][0]["gap"],
                      "signed_gap": data["cases"][4]["gap"], "allocation_admissions": 0, "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
