"""Record completion once; default performs read-only integrity/replay checks."""
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
SUPPLEMENT = INTEGRATION / "native-offline-resolution-supplement.json"
SNAPSHOT = INTEGRATION / "controls-native-offline-before"
CONTROLS = ["docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
            "data/accounting-master/next-plan.md", "docs/plans/accounting-mission-requirements.md"]


def load(path):
    return json.loads(path.read_bytes())


def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    tick = time.monotonic()
    result = subprocess.run([sys.executable, str(OUT / "check.py")], cwd=ROOT, capture_output=True, text=True, check=True)
    prior = ROOT / "docs/design/proposal/methods/preparation-20261005-v1/03-adapters"
    register_path = prior / "source-register.json"
    register = load(register_path)
    anchor_paths = {r["path"] for r in load(OUT / "source-anchors.json")}
    pins = []
    for row in register["sources"]:
        path = prior / row["path"]
        if str(path.relative_to(ROOT)) in anchor_paths:
            assert row["commit"] == "01f6a4656c2c6551d2f05f31c9d74366d133ee7e"
            assert binding(path)["sha256"] == row["sha256"]
            pins.append(binding(path))
    receipt_path = ROOT / "data/accounting-master/taxonomy-reuse-20261007/sources/arelle-cntlrcmdline-trusted.receipt.json"
    receipt = load(receipt_path)
    assert receipt["request"]["commit"] == "01f6a4656c2c6551d2f05f31c9d74366d133ee7e"
    assert receipt["http_status"] == 200 and binding(ROOT / receipt["body"])["sha256"] == receipt["sha256"]
    assert len(pins) == 5 and len(anchor_paths) == 6
    if args.record:
        for path in [OUT / "completion.json", SUPPLEMENT, SNAPSHOT]:
            assert not path.exists(), path
        assessment, operation = load(INTEGRATION / "assessment-successor.json"), load(INTEGRATION / "operation-successor.json")
        assert (len(assessment["rows"]), len(assessment["interactions"]), len(operation["rows"])) == (53, 6, 46)
        assert assessment["readiness"] == operation["readiness"] == "not_ready"
        snapshots = []
        for name in CONTROLS:
            destination = SNAPSHOT / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as handle:
                handle.write((ROOT / name).read_bytes())
            snapshots.append({"live_before": binding(ROOT / name), "snapshot": binding(destination)})
        completion = {"recorded_utc": datetime.now(timezone.utc).isoformat(),
                      "command": "python3 data/accounting-master/native-offline-resolution-20261018/complete.py --record",
                      "wall_seconds": time.monotonic() - tick, "replay": json.loads(result.stdout),
                      "source_pin_evidence": [binding(register_path), binding(receipt_path)], "verified_source_files": pins + [binding(ROOT / receipt["body"])],
                      "control_snapshots": snapshots,
                      "artifacts": [binding(OUT / name) for name in ["result.md", "checks.json", "run-manifest.json", "complete.py"]]}
        with (OUT / "completion.json").open("x") as handle:
            json.dump(completion, handle, indent=2)
            handle.write("\n")
        supplement = {"candidate_pdf": binding(ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"),
                      "protected_assessment": binding(INTEGRATION / "assessment-successor.json"),
                      "protected_integration": binding(INTEGRATION / "integration-bindings.json"),
                      "protected_operations": binding(INTEGRATION / "operation-successor.json"),
                      "additional_evidence": [binding(OUT / name) for name in ["completion.json", "result.md", "checks.json", "run-manifest.json"]],
                      "scope": "R06 proposed offline byte-resolution and dependency prerequisites; 27 resources, 3551 references, 21 rejected cases, 12 unresolved lock fields; no runtime",
                      "all_original_obligations": 53, "interactions": 6, "operations": 46, "whole_rows_closed": 0,
                      "readiness": "not_ready", "independent_domain_human_acceptance": "pending"}
        with SUPPLEMENT.open("x") as handle:
            json.dump(supplement, handle, indent=2)
            handle.write("\n")
    supplement, completion = load(SUPPLEMENT), load(OUT / "completion.json")
    rows = [supplement[k] for k in ["candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"]]
    rows += supplement["additional_evidence"] + completion["artifacts"] + completion["source_pin_evidence"] + completion["verified_source_files"]
    for row in completion["control_snapshots"]:
        assert row["live_before"]["sha256"] == row["snapshot"]["sha256"]
        rows.append(row["snapshot"])
    for row in rows:
        assert binding(ROOT / row["path"]) == row, row["path"]
    print(json.dumps({"completion": "recorded and verified" if args.record else "read-only replay passed",
                      "bindings": len(rows), "source_pins": 6, "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
