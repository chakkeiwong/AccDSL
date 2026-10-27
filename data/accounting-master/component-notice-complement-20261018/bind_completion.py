"""Record notice completion and snapshot live controls once; do not update controls."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
INTEGRATION = ROOT / "data/accounting-master/early-conversion-integration-20261018"
CONTROLS = ["docs/plans/accounting-master-current.md",
            "docs/plans/accounting-master-checkpoint.md",
            "data/accounting-master/next-plan.md",
            "docs/plans/accounting-mission-requirements.md"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def write_once(path, data):
    with path.open("x") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    start = datetime.now(timezone.utc)
    clock_start = time.monotonic()
    run_path = OUT / "run-manifest.json"
    supplement_path = INTEGRATION / "component-notice-complement-supplement.json"
    snapshot_dir = INTEGRATION / "controls-notice-complement-before"
    snapshot_manifest = INTEGRATION / "controls-notice-complement-manifest.json"
    for path in [run_path, supplement_path, snapshot_dir, snapshot_manifest]:
        assert not path.exists(), path
    manifest = json.loads((OUT / "source-manifest.json").read_bytes())
    checks = json.loads((OUT / "checks.json").read_bytes())
    assert checks["all_passed"] and len(checks["checks"]) == 209
    assert checks["source_manifest_sha256"] == sha(OUT / "source-manifest.json")
    for row in manifest["protected_inputs"] + manifest["artifacts"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
    assessment_path = INTEGRATION / "assessment-successor.json"
    operations_path = INTEGRATION / "operation-successor.json"
    assessment = json.loads(assessment_path.read_bytes())
    operations = json.loads(operations_path.read_bytes())
    assert (len(assessment["rows"]), len(assessment["interactions"]), len(operations["rows"])) == (53, 6, 46)
    control_rows = []
    for name in CONTROLS:
        source = ROOT / name
        target = snapshot_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(source.read_bytes())
        assert sha(source) == sha(target)
        control_rows.append({"live_before": ref(source), "snapshot": ref(target)})
    write_once(snapshot_manifest, {"recorded_utc": start.isoformat(), "controls": control_rows})
    names = ["source-manifest.json", "source-manifest-extracted-reading-pending.json",
             "source-reading.md", "result.md", "checks.json", "extraction-manifest.json",
             "apache-comparison.json", "extract_notices.py", "compare_apache_bodies.py",
             "finalize_reading_manifest.py", "verify_bindings.py", "bind_completion.py"]
    commands = ["python3 data/accounting-master/component-notice-complement-20261018/" + name
                for name in ["finalize_reading_manifest.py", "verify_bindings.py --record",
                             "verify_bindings.py", "bind_completion.py"]]
    interval = (datetime.fromisoformat(checks["finished_utc"]) -
                datetime.fromisoformat(manifest["started_utc"])).total_seconds()
    write_once(run_path, {
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "worktree": "36 pre-existing tracked dirty entries; preserved; no commit made",
        "commands_actually_run_in_completion": commands,
        "earlier_activity": "Extraction and complete author readings are preserved in their own extraction/source records; this completion record does not reconstruct unrecorded reading shell commands.",
        "environment": {"executable": sys.executable, "python": platform.python_version(),
                        "packages": "Python standard library only; no upstream package imported"},
        "cpu_gpu_status": "Static CPU file/hash operations only; no numerical framework, GPU detection, initialization or use",
        "random_seeds": "N/A: deterministic documentary work",
        "data_version": manifest["archive"],
        "wall_seconds": {"initial_verifier": checks["wall_seconds"],
                         "extraction_to_initial_verification_elapsed_interval": interval,
                         "active_reading": None,
                         "completion_record_preparation": time.monotonic() - clock_start},
        "time_limit": "Elapsed interval includes interruptions and is not active reading time; active reading was not measured.",
        "plan": manifest["plan"], "result": ref(OUT / "result.md"),
        "artifacts": [ref(OUT / name) for name in names],
        "pre_update_controls": ref(snapshot_manifest),
        "decision": "Deliver the retained 23-text complement; actual-build/component, incorporated notices, compatibility and rights decisions remain pending."
    })
    write_once(supplement_path, {
        "candidate_pdf": ref(ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"),
        "protected_assessment": ref(assessment_path),
        "protected_integration": ref(INTEGRATION / "integration-bindings.json"),
        "protected_operations": ref(operations_path),
        "additional_evidence": [ref(OUT / name) for name in
                                ["source-reading.md", "source-manifest.json", "checks.json", "run-manifest.json", "result.md"]],
        "scope": "R06 static complete reading of this retained archive: prior five plus 23 disjoint complementary texts, 64 new clause anchors, 209 initial checks and successful read-only replay; no actual-build applicability or rights clearance",
        "all_original_obligations": 53, "interactions": 6, "operations": 46,
        "whole_rows_closed": 0, "readiness": "not_ready",
        "independent_domain_human_acceptance": "pending"
    })
    print(json.dumps({"run_manifest": str(run_path.relative_to(ROOT)),
                      "supplement": str(supplement_path.relative_to(ROOT)),
                      "control_snapshots": len(control_rows), "checks": 209}))


if __name__ == "__main__":
    main()
