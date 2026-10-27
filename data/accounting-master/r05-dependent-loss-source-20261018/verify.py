"""Bounded source-evidence preservation; no framework or stochastic execution."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UNIT = Path(__file__).resolve().parent
CONTROLS = [
    "docs/plans/accounting-master-current.md",
    "docs/plans/accounting-master-checkpoint.md",
    "data/accounting-master/next-plan.md",
    "docs/plans/accounting-mission-requirements.md",
]
PROTECTED = [
    "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf",
    *[f"data/accounting-master/early-conversion-integration-20261018/{name}" for name in (
        "assessment-successor.json", "integration-bindings.json", "operation-successor.json",
        "r05-vintage-admission-supplement.json")],
]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode()


def dirty():
    raw = git("status", "--porcelain=v1", "--untracked-files=no", "-z")
    rows = [r for r in raw.split("\0") if r]
    assert all(r[:2] == " M" for r in rows), "unexpected staged/renamed/deleted path"
    return {r[3:]: sha(ROOT / r[3:]) for r in rows}


def write_new(path, data):
    with path.open("x") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def prepare():
    assert not (UNIT / "protection.json").exists(), "prepare is one-time only"
    current = dirty()
    assert len(current) == 36
    assert git("diff", "--cached", "--name-only") == ""
    saved = {}
    for name in CONTROLS:
        destination = UNIT / "controls-before" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as f:
            f.write((ROOT / name).read_bytes())
        saved[str(destination.relative_to(ROOT))] = sha(destination)
    protected = {p: sha(ROOT / p) for p in PROTECTED}
    prior = ROOT / "data/accounting-master/r05-vintage-admission-20261018"
    protected.update({str(p.relative_to(ROOT)): sha(p) for p in prior.iterdir() if p.is_file()})
    plan = "docs/plans/accounting-r05-dependent-loss-source-20261018.md"
    protected[plan] = sha(ROOT / plan)
    write_new(UNIT / "protection.json", {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "head": git("rev-parse", "HEAD").strip(),
        "branch": git("branch", "--show-current").strip(),
        "index_sha256": sha(ROOT / ".git/index"),
        "tracked_dirty": current, "protected": protected,
        "control_snapshots": saved,
    })
    print(json.dumps({"prepared": True, "tracked_dirty": len(current),
                      "protected_files": len(protected), "control_snapshots": len(saved)}))


def preservation():
    baseline = json.loads((UNIT / "protection.json").read_text())
    assert git("rev-parse", "HEAD").strip() == baseline["head"]
    assert git("branch", "--show-current").strip() == baseline["branch"]
    assert sha(ROOT / ".git/index") == baseline["index_sha256"]
    assert git("diff", "--cached", "--name-only") == ""
    current = dirty()
    assert current.keys() == baseline["tracked_dirty"].keys()
    for path, expected in baseline["tracked_dirty"].items():
        if path not in CONTROLS:
            assert current[path] == expected, path
    for key in ("protected", "control_snapshots"):
        for path, expected in baseline[key].items():
            assert sha(ROOT / path) == expected, path
    return baseline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
        return
    baseline = preservation()
    if not (UNIT / "completion.json").exists():
        print(json.dumps({"preservation": "passed", "completion": "not recorded"}))
        return
    completion = json.loads((UNIT / "completion.json").read_text())
    for path, expected in completion["bindings"].items():
        assert sha(ROOT / path) == expected, path
    print(json.dumps({"replay": "passed", "bindings": len(completion["bindings"]),
                      "tracked_dirty": len(baseline["tracked_dirty"]),
                      "index": "unchanged", "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
