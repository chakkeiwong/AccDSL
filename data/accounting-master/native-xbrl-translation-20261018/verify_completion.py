"""Verify operational completion JSON; --record adds a one-time validation note."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
INTEGRATION = ROOT / "data/accounting-master/early-conversion-integration-20261018"


def load(path):
    # Timing metadata is ordinary JSON, not an L1 portable financial Record.
    return json.loads(path.read_bytes())


def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    record_path = OUT / "completion-validation.json"
    if args.record and record_path.exists():
        raise ValueError("VALIDATION_ALREADY_EXISTS")
    replay = subprocess.run([sys.executable, str(OUT / "verify.py")], cwd=ROOT, capture_output=True, text=True, check=True)
    supplement_path = INTEGRATION / "native-xbrl-translation-supplement.json"
    supplement, completion = load(supplement_path), load(OUT / "completion.json")
    rows = [supplement[k] for k in ["candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"]]
    rows += supplement["additional_evidence"] + completion["artifacts"] + [completion["pre_update_controls"]]
    snapshots = load(ROOT / completion["pre_update_controls"]["path"])["controls"]
    for snapshot in snapshots:
        assert snapshot["live_before"]["sha256"] == snapshot["snapshot"]["sha256"]
        rows.append(snapshot["snapshot"])
    for row in rows:
        assert binding(ROOT / row["path"]) == row, row["path"]
    if args.record:
        value = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
                 "command": "python3 data/accounting-master/native-xbrl-translation-20261018/verify_completion.py --record",
                 "wall_seconds": time.monotonic() - tick, "bindings_checked": len(rows), "replay": load(OUT / "checks.json")["check_count"],
                 "supplement": binding(supplement_path), "verifier": binding(Path(__file__).resolve()),
                 "validation_status": "passed", "preserved_original_binding_attempt": binding(OUT / "bind_completion.py"),
                 "repair": "The binding command wrote completion, supplement and all four snapshots, then its final self-check rejected a fractional timing value because it used the strict L1 decoder on ordinary operational JSON. This verifier reads ordinary JSON for metadata and runs the unchanged strict fixture verifier separately. No bound file was rewritten or recording command repeated.",
                 "environment_correction": {"run_manifest": binding(OUT / "run-manifest.json"), "field": "environment.conda_env", "original": "N/A", "corrected": "tfgpu",
                                            "evidence": "sys.executable=/home/chakwong/miniconda3/envs/tfgpu/bin/python3 and CONDA_DEFAULT_ENV=tfgpu; standard-library checks only, no TensorFlow or other numerical framework imported"},
                 "future_replay": "python3 data/accounting-master/native-xbrl-translation-20261018/verify_completion.py"}
        with record_path.open("x") as handle:
            json.dump(value, handle, indent=2)
            handle.write("\n")
    else:
        recorded = load(record_path)
        for name in ["supplement", "verifier", "preserved_original_binding_attempt"]:
            assert binding(ROOT / recorded[name]["path"]) == recorded[name]
        assert binding(ROOT / recorded["environment_correction"]["run_manifest"]["path"]) == recorded["environment_correction"]["run_manifest"]
    print(json.dumps({"completion": "passed", "bindings_checked": len(rows), "portable_replay": json.loads(replay.stdout)["status"],
                      "environment_correction": "tfgpu interpreter; no numerical framework imported", "original_evidence_preserved": True}))


if __name__ == "__main__":
    main()
