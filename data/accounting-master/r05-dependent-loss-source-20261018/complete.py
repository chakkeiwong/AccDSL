"""Record this documentary unit once; default invocation only verifies it."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shlex
import sys
import time

sys.dont_write_bytecode = True
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from check_evidence import check
from verify import CONTROLS, ROOT, UNIT, preservation, sha, write_new

INTEGRATION = ROOT / "data/accounting-master/early-conversion-integration-20261018"
SUPPLEMENT = INTEGRATION / "r05-dependent-loss-source-supplement.json"
PLANS = [ROOT / ("docs/plans/" + name) for name in (
    "accounting-r05-dependent-loss-source-20261018.md",
    "accounting-r05-dependent-loss-acquisition-repair-20261018.md",
    "accounting-r05-forecomp-source-lead-20261018.md",
)]


def load(path):
    return json.loads(path.read_text())


def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def obligations():
    assessment = load(INTEGRATION / "assessment-successor.json")
    operations = load(INTEGRATION / "operation-successor.json")
    assert (len(assessment["rows"]), len(assessment["interactions"]),
            len(operations["rows"])) == (53, 6, 46)
    assert assessment["readiness"] == operations["readiness"] == "not_ready"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    if args.record:
        for name in ("checks.json", "run-manifest.json", "completion.json", "controls-after"):
            assert not (UNIT / name).exists(), "already exists: " + name
        assert not SUPPLEMENT.exists(), "supplement already exists"
    baseline = preservation()
    obligations()
    measured = check()
    validation_seconds = time.monotonic() - tick
    assert measured["checks"] == 232
    if args.record:
        snapshots = []
        for name in CONTROLS:
            destination = UNIT / "controls-after" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as handle:
                handle.write((ROOT / name).read_bytes())
            snapshots.append({"live_path": name, **binding(destination)})
            assert sha(ROOT / name) == sha(destination)
        write_new(UNIT / "checks.json", measured)
        acquisitions = load(UNIT / "acquisition-manifest.json")
        write_new(UNIT / "run-manifest.json", {
            "started_utc": started,
            "finished_validation_utc": datetime.now(timezone.utc).isoformat(),
            "validation_wall_seconds": validation_seconds,
            "wall_time_scope": "This completion validation only; prior network transfer durations remain separate.",
            "command": shlex.join([sys.executable, *sys.argv]),
            "git_commit": baseline["head"], "git_branch": baseline["branch"],
            "index_sha256": baseline["index_sha256"],
            "staging": "empty; unchanged", "tracked_dirty_paths": len(baseline["tracked_dirty"]),
            "environment": {"python_executable": sys.executable,
                            "python_version": platform.python_version(),
                            "environment_path": str(Path(sys.executable).parent.parent),
                            "imports": "standard library and local documentary checkers only"},
            "cpu_gpu_status": "CPU only; CUDA_VISIBLE_DEVICES=-1 intentionally hides GPU devices; no framework or GPU initialization",
            "data_version": "82 retained source files; exact identities in source-manifest.json; no company outcomes used",
            "random_seeds": "N/A: deterministic documentary checks and exact enumeration",
            "plans": [binding(path) for path in PLANS],
            "result_file": str((UNIT / "result.md").relative_to(ROOT)),
            "output_directory": str(UNIT.relative_to(ROOT)),
            "acquisition_manifest": binding(UNIT / "acquisition-manifest.json"),
            "actual_acquisition_tool_calls": binding(UNIT / "acquisition-tool-calls.json"),
            "network_transfer_seconds_sum": acquisitions["transfer_seconds_sum"],
            "validation": {k: v for k, v in measured.items() if k != "labels"},
        })
        pdf = ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"
        write_new(SUPPLEMENT, {
            "candidate_pdf": binding(pdf),
            "protected_assessment": binding(INTEGRATION / "assessment-successor.json"),
            "protected_integration": binding(INTEGRATION / "integration-bindings.json"),
            "protected_operations": binding(INTEGRATION / "operation-successor.json"),
            "additional_evidence": [binding(UNIT / name) for name in (
                "result.md", "checks.json", "run-manifest.json", "source-reading.md",
                "derivation.md", "admission-note.md", "source-manifest.json",
                "acquisition-manifest.json")],
            "scope": "R05 finite dependent-loss source inquiry; scalar-to-panel transfer limits, unselected E3 inference and exact illustrative covariance counterexample",
            "all_original_obligations": 53, "interactions": 6, "operations": 46,
            "whole_rows_closed": 0, "readiness": "not_ready",
            "empirical_admissions": 0, "independent_domain_human_acceptance": "pending",
        })
        paths = [p for p in UNIT.iterdir() if p.is_file() and p.name != "completion.json"]
        paths += PLANS + [SUPPLEMENT]
        paths += [p for directory in ("controls-before", "controls-after")
                  for p in (UNIT / directory).rglob("*") if p.is_file()]
        write_new(UNIT / "completion.json", {
            "recorded_utc": datetime.now(timezone.utc).isoformat(),
            "bindings": {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)},
            "controls_at_completion": snapshots,
            "control_replay_policy": "Verify exact snapshots; live controls may advance in subsequent authorised units.",
            "record_wall_seconds": time.monotonic() - tick,
        })
    completion = load(UNIT / "completion.json")
    for name, expected in completion["bindings"].items():
        assert sha(ROOT / name) == expected, name
    for row in completion["controls_at_completion"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
        assert row["live_path"] in CONTROLS
    assert load(UNIT / "checks.json") == measured, "check results changed"
    supplement = load(SUPPLEMENT)
    for key in ("candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"):
        row = supplement[key]
        assert binding(ROOT / row["path"]) == row
    for row in supplement["additional_evidence"]:
        assert binding(ROOT / row["path"]) == row
    assert (supplement["all_original_obligations"], supplement["interactions"],
            supplement["operations"], supplement["whole_rows_closed"],
            supplement["readiness"]) == (53, 6, 46, 0, "not_ready")
    preservation()
    print(json.dumps({"completion": "recorded and verified" if args.record else "read-only replay passed",
                      "bindings": len(completion["bindings"]),
                      **{k: v for k, v in measured.items() if k != "labels"}}))


if __name__ == "__main__":
    main()
