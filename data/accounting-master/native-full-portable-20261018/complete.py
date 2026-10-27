"""One-time additive source completion; default replay is read-only."""
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
SUPPLEMENT = INTEGRATION / "native-full-portable-supplement.json"
SNAPSHOT = INTEGRATION / "controls-native-full-portable-before"
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
    run = subprocess.run([sys.executable, str(OUT / "check.py")], cwd=ROOT, capture_output=True, text=True, check=True)
    if args.record:
        for path in [OUT / "completion.json", SUPPLEMENT, SNAPSHOT]:
            assert not path.exists(), path
        a, o = load(INTEGRATION / "assessment-successor.json"), load(INTEGRATION / "operation-successor.json")
        assert (len(a["rows"]), len(a["interactions"]), len(o["rows"])) == (53, 6, 46)
        assert a["readiness"] == o["readiness"] == "not_ready"
        snapshots = []
        for name in CONTROLS:
            target = SNAPSHOT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as handle:
                handle.write((ROOT / name).read_bytes())
            snapshots.append({"live_before": binding(ROOT / name), "snapshot": binding(target)})
        completion = {"recorded_utc": datetime.now(timezone.utc).isoformat(),
                      "command": "python3 data/accounting-master/native-full-portable-20261018/complete.py --record",
                      "wall_seconds": time.monotonic() - tick, "replay": json.loads(run.stdout),
                      "control_snapshots": snapshots,
                      "artifacts": [binding(OUT / n) for n in ["result.md", "checks.json", "run-manifest.json", "complete.py"]]}
        with (OUT / "completion.json").open("x") as handle:
            json.dump(completion, handle, indent=2)
            handle.write("\n")
        supplement = {"candidate_pdf": binding(ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"),
                      "protected_assessment": binding(INTEGRATION / "assessment-successor.json"),
                      "protected_integration": binding(INTEGRATION / "integration-bindings.json"),
                      "protected_operations": binding(INTEGRATION / "operation-successor.json"),
                      "additional_evidence": [binding(OUT / n) for n in ["completion.json", "result.md", "checks.json", "run-manifest.json"]],
                      "scope": "R06 full retained native documentary translation: 3788 proposed records, 34883 mappings, all 1127 facts, 193 contexts, seven units and schemaRef; 196348 checks and twelve corruption rejections; no upstream execution",
                      "all_original_obligations": 53, "interactions": 6, "operations": 46, "whole_rows_closed": 0,
                      "readiness": "not_ready", "independent_domain_human_acceptance": "pending"}
        with SUPPLEMENT.open("x") as handle:
            json.dump(supplement, handle, indent=2)
            handle.write("\n")
    supplement, completion = load(SUPPLEMENT), load(OUT / "completion.json")
    rows = [supplement[k] for k in ["candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"]]
    rows += supplement["additional_evidence"] + completion["artifacts"]
    for row in completion["control_snapshots"]:
        assert row["live_before"]["sha256"] == row["snapshot"]["sha256"]
        rows.append(row["snapshot"])
    for row in rows:
        assert binding(ROOT / row["path"]) == row, row["path"]
    print(json.dumps({"completion": "recorded and verified" if args.record else "read-only replay passed",
                      "bindings": len(rows), "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
