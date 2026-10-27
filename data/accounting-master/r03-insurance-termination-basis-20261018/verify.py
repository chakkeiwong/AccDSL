"""Preserve the finite source inquiry; default replay never writes files."""
import argparse
from datetime import datetime, timezone
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
PRIOR = BASE / "r03-hedge-attribution-discriminator-20261018"
INTEGRATION = BASE / "early-conversion-integration-20261018"
PLAN = ROOT / "docs/plans/accounting-r03-insurance-termination-basis-20261018.md"
SUPPLEMENT = INTEGRATION / "r03-insurance-termination-basis-supplement.json"
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


def binding(path):
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
    assert all(row[:2] == " M" for row in rows)
    return {row[3:]: sha(ROOT / row[3:]) for row in rows}


def prepare():
    assert not (UNIT / "protection.json").exists(), "one-time preparation"
    prior = subprocess.run([sys.executable, str(PRIOR / "verify.py")], cwd=ROOT,
                           check=True, capture_output=True, text=True)
    assert json.loads(prior.stdout)["status"] == "read-only replay passed"
    paths = {ROOT / name for name in load(PRIOR / "protection.json")["protected"]}
    paths.update(ROOT / name for name in load(PRIOR / "completion.json")["bindings"])
    paths.add(PRIOR / "completion.json")
    for directory in ("insurance-termination-source-20261017", "insurance-service-finance-origins-20261016"):
        paths.update(p for p in (BASE / directory).rglob("*") if p.is_file())
    paths.update([PLAN, UNIT / "verify.py", ROOT / "docs/plans/accounting-insurance-termination-source-20261017.md",
                  ROOT / "docs/plans/accounting-insurance-service-finance-origins-20261016.md"])
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


def verify_evidence():
    acquisitions = load(UNIT / "acquisitions.json")
    assert 1 <= len(acquisitions) <= 5
    for row in acquisitions:
        for item in row["artifacts"]:
            assert binding(ROOT / item["path"]) == item, item["path"]
        assert row["source_url"].startswith("https://")
        assert row["http_status"] in (200, 301, 302, 303, 307, 308, 400, 401, 403, 404)
        assert row["source_role"] in ("navigation", "primary_supporting_text", "access_boundary")
    review = load(UNIT / "source-review.json")
    for span in review["inspected_spans"]:
        lines = (ROOT / span["path"]).read_text().splitlines(keepends=True)
        text = "".join(lines[span["first_line"]-1:span["last_line"]])
        assert hashlib.sha256(text.encode()).hexdigest() == span["sha256"], span["id"]
        assert span["anchor"] in text, span["id"]
    assert review["rule_admitted"] is False and review["whole_rows_closed"] == 0
    return acquisitions, review


def record():
    assert not (UNIT / "completion.json").exists() and not (UNIT / "controls-after").exists()
    assert not SUPPLEMENT.exists()
    baseline = preservation()
    acquisitions, review = verify_evidence()
    for name in ("result.md", "source-reading.md"):
        assert (UNIT / name).is_file(), name
    finished = datetime.now(timezone.utc)
    write_new(UNIT / "run-manifest.json", {
        "started_utc": baseline["started_utc"], "finished_utc": finished.isoformat(),
        "elapsed_wall_seconds": (finished-datetime.fromisoformat(baseline["started_utc"])).total_seconds(),
        "command": shlex.join([sys.executable, *sys.argv]), "git_commit": baseline["head"],
        "index_sha256": baseline["index_sha256"], "staging": "empty; unchanged",
        "tracked_dirty_paths": len(baseline["tracked_dirty"]),
        "environment": {"python_executable": sys.executable, "python_version": platform.python_version(),
                        "python_imports": "standard library only", "other_tools": "existing curl/pdftotext if used; exact commands in acquisitions.json"},
        "cpu_gpu_status": "CPU only; CUDA_VISIBLE_DEVICES=-1 intentionally hides GPUs; no framework initialization",
        "data_version": review["editions"], "random_seeds": "N/A: documentary source inquiry",
        "plan": binding(PLAN), "result_file": str((UNIT / "result.md").relative_to(ROOT)),
        "acquisitions": binding(UNIT / "acquisitions.json"), "review": binding(UNIT / "source-review.json"),
        "new_http_acquisitions": len(acquisitions), "rule_admissions": 0, "whole_rows_closed": 0,
    })
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
            ("source-reading.md", "result.md", "source-review.json", "acquisitions.json", "run-manifest.json")],
        "scope": "R03 finite primary-supporting-text follow-up; original OCI interrupted runoff remains unadmitted",
        "all_original_obligations": 53, "interactions": 6, "operations": 46,
        "whole_rows_closed": 0, "readiness": "not_ready", "independent_domain_human_acceptance": "pending",
    })
    paths = [p for p in UNIT.rglob("*") if p.is_file() and p.name != "completion.json"]
    paths += [PLAN, SUPPLEMENT]
    write_new(UNIT / "completion.json", {
        "recorded_utc": finished.isoformat(), "bindings": {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)},
        "controls_at_completion": snapshots,
        "control_replay_policy": "Immutable snapshots; live controls may advance in authorised successor units.",
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--record", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
        return
    if args.record:
        record()
    baseline = preservation()
    acquisitions, review = verify_evidence()
    completion = load(UNIT / "completion.json")
    for name, expected in completion["bindings"].items():
        assert sha(ROOT / name) == expected, name
    supplement = load(SUPPLEMENT)
    for key in ("candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"):
        item = supplement[key]
        assert binding(ROOT / item["path"]) == item
    assert (supplement["all_original_obligations"], supplement["interactions"], supplement["operations"],
            supplement["whole_rows_closed"], supplement["readiness"]) == (53, 6, 46, 0, "not_ready")
    print(json.dumps({"status": "recorded and verified" if args.record else "read-only replay passed",
                      "acquisitions": len(acquisitions), "inspected_spans": len(review["inspected_spans"]),
                      "protected_files": len(baseline["protected"]), "completion_bindings": len(completion["bindings"]),
                      "rule_admissions": 0, "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
