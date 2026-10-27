"""Source-only lifecycle; no-argument replay never writes files."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["GIT_OPTIONAL_LOCKS"] = "0"
UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
BASE = ROOT / "data/accounting-master"
PRIOR = BASE / "r06-calc11-processor-20261020"
INTEGRATION = BASE / "early-conversion-integration-20261018"
PLAN = ROOT / "docs/plans/accounting-r06-calc11-conditional-20261020.md"
SUPPLEMENT = INTEGRATION / "r06-calc11-conditional-supplement.json"
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


def bind(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def write_new(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def dirty():
    raw = subprocess.check_output(["git", "status", "--porcelain=v1", "--untracked-files=no", "-z"],
                                  cwd=ROOT, text=True)
    rows = [row for row in raw.split("\0") if row]
    assert all(row[:2] == " M" for row in rows), "unexpected staged/renamed path"
    return {row[3:]: sha(ROOT / row[3:]) for row in rows}


def prepare():
    assert not (UNIT / "protection.json").exists(), "one-time preparation"
    prior = subprocess.run([sys.executable, str(PRIOR / "verify.py")], cwd=ROOT,
                           check=True, capture_output=True, text=True)
    assert json.loads(prior.stdout)["status"] == "read-only replay passed"
    paths = {ROOT / name for name in load(PRIOR / "protection.json")["protected"]}
    paths.update(ROOT / name for name in load(PRIOR / "completion.json")["bindings"])
    paths.add(PRIOR / "completion.json")
    for name in ("consequential-literature-20261015", "source-protocol-reuse-refresh-20261016", "protocol-delta-refresh-20261018", "rate-interval-propagation-20261017", "participating-tax-allocation-20261017", "zero-cost-collar-20261017", "origin-matched-cessation-20261017", "early-conversion-source-20261018"):
        paths.update(p for p in (BASE / name).rglob("*") if p.is_file())
    paths.update([PLAN, UNIT / "verify.py", ROOT / "docs/design/research/text/green2007.txt", ROOT / "docs/papers/Provenance semirings Green (2007).pdf", ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/chapters/03-literature.tex"])
    paths.update((ROOT / "docs/design/research").glob("*.json"))
    paths.update(ROOT / "docs/design/research/raw" / name for name in ("smock2022-citing-recent.json", "zheng2021-citing-recent.json"))
    paths.add(ROOT / "docs/design/research/text/smock2022.txt")
    paths.difference_update(ROOT / name for name in CONTROLS)
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
        "control_snapshots": snapshots, "prior_read_only_replay": json.loads(prior.stdout),
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


def check():
    spec = importlib.util.spec_from_file_location("oim_mapping", UNIT / "compare.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.check()


def record(baseline, checks):
    assert not (UNIT / "completion.json").exists(), "one-time recording"
    assert load(UNIT / "checks.json") == checks
    for name in ("result.md", "review.md", "source-ledger.json"):
        assert (UNIT / name).is_file(), name
    snapshots = {}
    for name in CONTROLS:
        target = UNIT / "controls-after" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write((ROOT / name).read_bytes())
        snapshots[str(target.relative_to(ROOT))] = sha(target)
    command = "CUDA_VISIBLE_DEVICES=-1 " + shlex.join([sys.executable, "-B", str(UNIT / "verify.py"), "--record"])
    write_new(UNIT / "run-manifest.json", {
        "git_commit": baseline["head"], "branch": baseline["branch"], "commands": [
            command.replace("--record", flag) for flag in ("--prepare", "--check", "--record", "")],
        "acquisition_commands": "None; exact retained primary documents reused", "environment": sys.executable,
        "python": platform.python_version(), "cpu_gpu": "CPU only; CUDA_VISIBLE_DEVICES=-1; standard library only; no GPU imported",
        "data_version": "retained lead and acquired primary identities in source-ledger.json",
        "seeds": "N/A deterministic source comparison", "started_utc": baseline["started_utc"],
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "wall_seconds_to_record": (datetime.now(timezone.utc) - datetime.fromisoformat(baseline["started_utc"])).total_seconds(),
        "plan": str(PLAN.relative_to(ROOT)), "result": str((UNIT / "result.md").relative_to(ROOT)),
        "output": str(UNIT.relative_to(ROOT)), "held_actions": ["runtime", "installation", "empirical execution", "commit", "outreach", "fees"],
    })
    write_new(SUPPLEMENT, {
        "scope": "R06 conditional exact report interval arithmetic; no processor execution or conformance admission",
        "candidate_version": "3.44", "candidate_pdf": bind(ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"),
        "protected_assessment": bind(INTEGRATION / "assessment-successor.json"),
        "protected_integration": bind(INTEGRATION / "integration-bindings.json"),
        "protected_operations": bind(INTEGRATION / "operation-successor.json"),
        "all_original_obligations": 53, "interactions": 6, "operations": 46,
        "whole_rows_closed": 0, "readiness": "not_ready",
        "checks": checks, "result": bind(UNIT / "result.md"), "review": bind(UNIT / "review.md"),
        "plan": bind(PLAN), "manuscript_changed": False, "runtime_admitted": False,
    })
    files = [p for p in UNIT.rglob("*") if p.is_file() and p.name != "completion.json"]
    files.extend([PLAN, SUPPLEMENT])
    write_new(UNIT / "completion.json", {
        "bindings": {str(p.relative_to(ROOT)): sha(p) for p in sorted(files)},
        "controls_at_completion": snapshots,
        "control_replay_policy": "Immutable snapshots; live controls may advance in authorised successor units.",
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    for flag in ("prepare", "check", "record"):
        modes.add_argument("--" + flag, action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
        return
    baseline = preservation()
    checks = check()
    if args.check:
        write_new(UNIT / "checks.json", checks)
        print(json.dumps(checks))
        return
    if args.record:
        record(baseline, checks)
    assert load(UNIT / "checks.json") == checks
    completion = load(UNIT / "completion.json")
    for name, expected in completion["bindings"].items():
        assert sha(ROOT / name) == expected, name
    supplement = load(SUPPLEMENT)
    for key in ("candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"):
        item = supplement[key]
        assert bind(ROOT / item["path"]) == item
    assert (supplement["all_original_obligations"], supplement["interactions"], supplement["operations"],
            supplement["whole_rows_closed"], supplement["readiness"]) == (53, 6, 46, 0, "not_ready")
    print(json.dumps({"status": "recorded and verified" if args.record else "read-only replay passed",
                      "checks": checks, "protected_files": len(baseline["protected"]),
                      "completion_bindings": len(completion["bindings"]), "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
