"""Record once; default verifies the frozen reconciliation without upstream execution."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from duties import DUTIES, EVIDENCE

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
MASTER = ROOT / "data/accounting-master"
INTEGRATION = MASTER / "early-conversion-integration-20261018"
PLAN = ROOT / "docs/plans/accounting-r06-duty-reconciliation-20261018.md"
BASELINE = MASTER / "native-offline-resolution-20261018/dependency-prerequisites.json"
PROTECTED = {
    "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf":
        "afbbdbe73d6ac25a9e59ea6f39e25b2e579ebd1e5fcad0ac9959e87cc6ab5d80",
    "data/accounting-master/early-conversion-integration-20261018/assessment-successor.json":
        "37ce6cae6d860bc05be31459b997f35b5ac8f2f12bd0aea3e295f4fab90ddb50",
    "data/accounting-master/early-conversion-integration-20261018/integration-bindings.json":
        "33dd3b29449a35975747b5e238ca9d6b515df9107ce74f42a1db968da3f8cc1a",
    "data/accounting-master/early-conversion-integration-20261018/operation-successor.json":
        "81ae6c695494f33ecc570c25f84a5c5247ca4d75e74e744cf76a7f1ec94d3626",
}
HEAD = "03fea070f089821f4759e49a4466a3399b7fc078"
INDEX = "54c1f8bfd32b2a3e30fe8bea70befdd1b2106ca5b9955b6ea9b526ed12604db4"


def load(path):
    return json.loads(path.read_bytes())


def binding(path):
    return {"path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write_new(name, value):
    with (OUT / name).open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def verify_bindings(value, stats):
    if isinstance(value, list):
        for item in value:
            verify_bindings(item, stats)
    elif isinstance(value, dict):
        if "live_before" in value and "snapshot" in value:
            assert value["live_before"]["sha256"] == value["snapshot"]["sha256"]
            stats["historical_control_pairs"] += 1
            verify_bindings(value["snapshot"], stats)
        elif isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            assert binding(ROOT / value["path"]) == value, value["path"]
            stats["binding_occurrences"] += 1
        else:
            for item in value.values():
                verify_bindings(item, stats)


def construct():
    stats = {"binding_occurrences": 0, "historical_control_pairs": 0}
    original = load(BASELINE)
    assert original["runtime_admission"] == "held"
    assert original["source_commit"] == "01f6a4656c2c6551d2f05f31c9d74366d133ee7e"
    assert len(original["pending"]) == len(DUTIES) == 12
    for path, digest in PROTECTED.items():
        assert binding(ROOT / path)["sha256"] == digest, path
    assessment = load(INTEGRATION / "assessment-successor.json")
    operations = load(INTEGRATION / "operation-successor.json")
    assert (len(assessment["rows"]), len(assessment["interactions"]), len(operations["rows"])) == (53, 6, 46)
    assert assessment["readiness"] == operations["readiness"] == "not_ready"
    evidence = {}
    for key, (directory, supplement) in EVIDENCE.items():
        base = MASTER / (directory + "-20261018")
        documents = [base / name for name in ("result.md", "checks.json", "run-manifest.json")]
        completion = base / "completion.json"
        if completion.exists():
            documents.append(completion)
            replay = load(completion)["replay"]
            assert replay, key
        else:
            replay = None
        if supplement:
            documents.append(INTEGRATION / (supplement + "-supplement.json"))
        for path in documents:
            if path.suffix == ".json":
                verify_bindings(load(path), stats)
        evidence[key] = {
            "documents": [binding(path) for path in documents],
            "recorded_replay_summary": replay,
            "replay_summary_role": "Preserved historical result; prior commands were not rerun by this reconciliation.",
        }
    duties = []
    for prior, (field, refs, progress, remaining) in zip(original["pending"], DUTIES):
        assert prior["field"] == field and prior["value"] is None
        assert prior["reason"] and progress and remaining
        assert refs and all(ref in evidence for ref in refs)
        duties.append({
            "original": prior,
            "documentary_progress": progress,
            "evidence_ids": refs,
            "remaining_installed_condition": remaining,
            "runtime_value": None,
            "runtime_status": "held_unverified",
        })
    reconciliation = {
        "schema": "accdsl.r06_duty_reconciliation.documentary.v1",
        "status": "documentary_progress_runtime_held",
        "baseline_binding": binding(BASELINE),
        "baseline_verbatim": original,
        "protected": [{"path": path, "sha256": digest} for path, digest in PROTECTED.items()],
        "duties": duties,
        "evidence": evidence,
        "source_qualification": "The retained XBRL instance schema describes its copy as non-normative and asserts equivalence to Appendix A; that equivalence and built-in lexical/value-space validation are unverified.",
        "limits": {
            "runtime_admission": "held", "upstream_execution": False,
            "dependency_lock": "not_selected", "schema_xbrl_validation": "not_run",
            "installed_portable_correspondence": "not_run",
            "financial_admission": "not_established", "rights_clearance": "not_established",
            "whole_rows_closed": 0, "readiness": "not_ready",
            "independent_technical_domain_human_acceptance": "pending",
        },
    }
    checks = {
        "all_passed": True, "duties_preserved": 12, "original_nulls_preserved": 12,
        "evidence_units": len(evidence),
        "bound_recorded_replay_summaries": sum(v["recorded_replay_summary"] is not None for v in evidence.values()),
        "referenced_evidence": stats, "protected_hashes": len(PROTECTED),
        "obligations": 53, "interactions": 6, "operations": 46,
        "diagnostic_roles": {
            "primary": "Preserve all original duties and bind concrete progress plus remaining installed conditions.",
            "promotion_veto": "Changed baseline/hash, missing evidence, guessed runtime value or validation/runtime credit.",
            "continuation_veto": "Corrupted protected source.",
            "explanatory_only": "Counts and prior check totals; no new scientific ranking or runtime readiness.",
        },
    }
    return reconciliation, checks


def git_state():
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT)
    assert git("rev-parse", "HEAD").decode().strip() == HEAD
    assert hashlib.sha256((ROOT / ".git/index").read_bytes()).hexdigest() == INDEX
    assert not git("diff", "--cached", "--name-only")
    dirty = [x.decode() for x in git("diff", "--name-only", "-z").split(b"\0") if x]
    assert len(dirty) == 36
    return {"git_commit": HEAD, "index_sha256": INDEX,
            "tracked_dirty": [binding(ROOT / path) for path in dirty]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    reconciliation, checks = construct()
    state = git_state()
    if args.record:
        for name in ("reconciliation.json", "checks.json", "run-manifest.json"):
            assert not (OUT / name).exists(), name
        write_new("reconciliation.json", reconciliation)
        write_new("checks.json", checks)
        manifest = {
            "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
            "command": [sys.executable, str(OUT / "check.py"), "--record"],
            "wall_seconds": time.monotonic() - tick,
            "environment": {"executable": sys.executable, "python": platform.python_version(),
                            "operations": "Standard-library files/hash/JSON only; no upstream import.",
                            "cpu_gpu": "CPU file operations; GPU not detected, initialized or used."},
            "data_version": "Frozen documentary evidence dated 2026-10-18",
            "random_seeds": "N/A: deterministic evidence reconciliation",
            "plan_file": binding(PLAN), "result_file": str((OUT / "result.md").relative_to(ROOT)),
            "protected_inputs": reconciliation["protected"] + [binding(BASELINE)],
            "artifacts": [binding(OUT / name) for name in ("duties.py", "check.py", "reconciliation.json", "checks.json")],
            "git_baseline": state,
        }
        write_new("run-manifest.json", manifest)
    assert load(OUT / "reconciliation.json") == reconciliation
    assert load(OUT / "checks.json") == checks
    manifest = load(OUT / "run-manifest.json")
    # Controls are live; their original hashes remain recorded, not asserted as current.
    verify_bindings({k: v for k, v in manifest.items() if k != "git_baseline"},
                    {"binding_occurrences": 0, "historical_control_pairs": 0})
    controls = {"docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
                "data/accounting-master/next-plan.md", "docs/plans/accounting-mission-requirements.md"}
    assert {row["path"] for row in state["tracked_dirty"]} == {row["path"] for row in manifest["git_baseline"]["tracked_dirty"]}
    for row in manifest["git_baseline"]["tracked_dirty"]:
        if row["path"] not in controls:
            assert binding(ROOT / row["path"]) == row, row["path"]
    print(json.dumps({"status": "recorded" if args.record else "read-only replay passed",
                      "duties": 12, "evidence_units": len(EVIDENCE),
                      "referenced_evidence": checks["referenced_evidence"],
                      "runtime_admission": "held", "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
