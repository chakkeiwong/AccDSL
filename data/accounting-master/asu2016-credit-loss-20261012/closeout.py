#!/usr/bin/env python3
"""Verify the bounded historical source unit and its pre-update controls."""

import hashlib
import json
from pathlib import Path


root = Path(__file__).resolve().parent
repo = root.parents[2]
checks = []


def add(name, ok):
    checks.append({"name": name, "pass": bool(ok)})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


source_run = json.loads((root / "check-run.json").read_text())
add("source run passes", source_run["checks"] == 147 and not source_run["failed"])
for name in [
    "result.md", "method-consequences.md", "author-review.md",
    "next-source-frontier.md", "source-ledger.json", "source-pages.json",
    "render-manifest.json", "pointer-snapshots.json",
]:
    add(name + " exists", (root / name).is_file())

for snap in json.loads((root / "pointer-snapshots.json").read_text()):
    path = repo / snap["snapshot"]
    add(snap["live"] + " pre-update hash", path.is_file() and sha(path) == snap["sha256"])

result = (root / "result.md").read_text()
add("result distinguishes ASU authority", "ASU is not" in result)
add("result refuses current ASC claim", "operative ASC wording" in result)
add("result has decision table", "| Decision | Primary criterion |" in result)
add("result keeps readiness open", "**not_ready**" in result)
add("manuscript baseline retained", sha(repo / "docs/design/proposal/manuscript-jpmorgan-commitments-20261012/accounting-product-proposal.pdf") == "48bce1dae3f6b23b88a540489d064258870250673a57fce0ae681cc7ce598496")

failed = [item["name"] for item in checks if not item["pass"]]
(root / "closeout-checks.json").write_text(json.dumps({"checks": len(checks), "failed": failed, "results": checks}, indent=2) + "\n")
print(json.dumps({"checks": len(checks), "failed": failed}))
raise SystemExit(bool(failed))
