"""Bind once with --record; default verifies the additive completion read-only."""
import argparse
from datetime import datetime, timezone
import json
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from common import OUT, ROOT, read, require, sha, write_once

INTEGRATION = ROOT / "data/accounting-master/early-conversion-integration-20261018"
CONTROLS = ["docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
            "data/accounting-master/next-plan.md", "docs/plans/accounting-mission-requirements.md"]
SUPPLEMENT = INTEGRATION / "native-xbrl-translation-supplement.json"
SNAPSHOT = INTEGRATION / "controls-native-xbrl-before"
SNAPSHOT_MANIFEST = INTEGRATION / "controls-native-xbrl-manifest.json"
COMPLETION = OUT / "completion.json"


def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes())}


def verify(row):
    require(binding(ROOT / row["path"]) == row, "BINDING:" + row["path"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    tick = time.monotonic()
    replay = subprocess.run([sys.executable, str(OUT / "verify.py")], cwd=ROOT, capture_output=True, text=True, check=True)
    if args.record:
        for path in [SUPPLEMENT, SNAPSHOT, SNAPSHOT_MANIFEST, COMPLETION]:
            require(not path.exists(), "COMPLETION_ALREADY_EXISTS:" + str(path))
        assessment, operations = read(INTEGRATION / "assessment-successor.json"), read(INTEGRATION / "operation-successor.json")
        require((len(assessment["rows"]), len(assessment["interactions"]), len(operations["rows"])) == (53, 6, 46), "ORIGINAL_OBLIGATIONS")
        require(assessment["readiness"] == operations["readiness"] == "not_ready", "READINESS")
        snapshots = []
        for name in CONTROLS:
            target = SNAPSHOT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as handle:
                handle.write((ROOT / name).read_bytes())
            snapshots.append({"live_before": binding(ROOT / name), "snapshot": binding(target)})
        write_once(SNAPSHOT_MANIFEST, {"recorded_utc": datetime.now(timezone.utc).isoformat(), "controls": snapshots})
        write_once(COMPLETION, {"recorded_utc": datetime.now(timezone.utc).isoformat(),
                   "command": "python3 data/accounting-master/native-xbrl-translation-20261018/bind_completion.py --record",
                   "git_commit": read(OUT / "preparation.json")["git_commit"], "replay": json.loads(replay.stdout),
                   "wall_seconds": str(time.monotonic() - tick), "pre_update_controls": binding(SNAPSHOT_MANIFEST),
                   "artifacts": [binding(OUT / name) for name in ["result.md", "checks.json", "run-manifest.json", "bind_completion.py"]]})
        write_once(SUPPLEMENT, {"candidate_pdf": binding(ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"),
                   "protected_assessment": binding(INTEGRATION / "assessment-successor.json"),
                   "protected_integration": binding(INTEGRATION / "integration-bindings.json"),
                   "protected_operations": binding(INTEGRATION / "operation-successor.json"),
                   "additional_evidence": [binding(OUT / name) for name in ["completion.json", "result.md", "checks.json", "run-manifest.json"]],
                   "scope": "R06 proposed native-XBRL documentary translation: 80 records, 653 mappings, 3710 checks, 44 rejected corruptions and signed-Int case; no upstream execution or schema registration",
                   "all_original_obligations": 53, "interactions": 6, "operations": 46, "whole_rows_closed": 0,
                   "readiness": "not_ready", "independent_domain_human_acceptance": "pending"})
    supplement, completion = read(SUPPLEMENT), read(COMPLETION)
    for name in ["candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"]:
        verify(supplement[name])
    for row in supplement["additional_evidence"] + completion["artifacts"]:
        verify(row)
    verify(completion["pre_update_controls"])
    for row in read(SNAPSHOT_MANIFEST)["controls"]:
        verify(row["snapshot"])
        require(row["snapshot"]["sha256"] == row["live_before"]["sha256"], "SNAPSHOT_IDENTITY")
    print(json.dumps({"status": "recorded and verified" if args.record else "read-only completion verification passed",
                      "supplement": str(SUPPLEMENT.relative_to(ROOT)), "controls_preserved": 4, "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
