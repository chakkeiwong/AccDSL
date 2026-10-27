"""Bind a completed manual scope review; never certify proofs by file count.

Read-only source checks; one new result and a narrow current-ledger update.
Successful execution must not be repeated.
"""
import hashlib
import json
from pathlib import Path
import platform
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
started = time.time()
dest = OUT / "current-scopes-verification.json"
backup = OUT / "claim-ledger-before-current-scopes.json"
support_dest = OUT / "current-source-support.json"
if any(p.exists() for p in (dest, backup, support_dest)):
    raise SystemExit("one-shot output already exists; inspect it instead")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks = []


def check(label, actual, expected):
    checks.append({"label": label, "passed": actual == expected})
    if actual != expected:
        raise ValueError(label)


ledger_path = OUT / "current-claim-ledger.json"
ledger_bytes = ledger_path.read_bytes()
ledger = json.loads(ledger_bytes)
candidate = ROOT / "docs/design/proposal/manuscript-debt-reading-v553-20261027"
check("claim population", len(ledger["rows"]), 27)
check("unique claim IDs", len({r["id"] for r in ledger["rows"]}), 27)
locations = 0
for row in ledger["rows"]:
    for loc in row["current_locations"]:
        check(row["id"] + " file identity " + loc["file"],
              sha(candidate / loc["file"]), loc["sha256"])
        locations += 1
check("location population", locations, 43)
check("baseline map", sha(ROOT / ledger["baseline_claim_map"]),
      ledger["baseline_sha256"])

source_ledger_path = ROOT / "data/accounting-master/literature-closure-20261026/source-support.json"
sources = json.loads(source_ledger_path.read_text())["records"]
wanted = {"probabilistic-adapted", "time-causal-vae", "kernel-topology",
          "kara-robustness", "pflug", "adapted", "adapted-estimation"}
selected = [s for s in sources if s["id"] in wanted]
check("selected primary records", {s["id"] for s in selected}, wanted)
for source in selected:
    check("primary source " + source["id"],
          sha(ROOT / source["path"]), source["sha256"])
additional = [
    {"id": "all-adapted-topologies",
     "path": "docs/papers/All adapted topologies are equal Backhoff-Veraguas (2020).pdf",
     "sha256": "72040d8c94c9a2b123946789cc9dc2c438e658c997417c458b8b8d347188f5a7",
     "read_scope": "physical1-48; article proofs; physical34/45 rendered",
     "review": "adapted-topology-review.md",
     "limit": "weak-transport attainment and standard external dependencies not fully inspected"},
    {"id": "eder-compactness",
     "path": str((OUT / "sources/Compactness in adapted weak topologies Eder (2019).pdf").relative_to(ROOT)),
     "sha256": "db52774ea82eb95b44ad6c2cb071ef06f3c76d44dfc0eb4d54fbafe3582a48fd",
     "edition": "arXiv1905.00856v1",
     "read_scope": "physical1-14; proofs; physical12/13 rendered",
     "review": "eder-dependency-review.md",
     "limit": "bounded arXiv metadata check only; standard external dependencies scoped"},
]
for source in additional:
    check("additional source " + source["id"],
          sha(ROOT / source["path"]), source["sha256"])
stopping_path = OUT / "topology-stopping-verification.json"
stopping = json.loads(stopping_path.read_text())
check("retained exact diagnostic decision", stopping["status"],
      "literal_construction_fails_repaired_construction_passes")
check("retained diagnostic source", stopping["source"]["sha256"],
      additional[0]["sha256"])
check("diagnostic script unchanged", sha(OUT / "verify_topology_stopping.py"),
      stopping["manifest"]["script_sha256"])

reviewed = {"C02", "C03", "C04", "C05", "C18", "C19", "C20", "C21", "C26"}
for row in ledger["rows"]:
    if row["id"] in reviewed:
        check("previous status " + row["id"], row["review_status"],
              "inherited_support_not_newly_reaccepted")
        row["review_status"] = "current_scope_matches_bounded_support_provisionally"
        row["current_review"] = str((OUT / "current-scopes-review.md").relative_to(ROOT))
        row["next_action"] = "Preserve version/assumption limits; close external-dependency, fixture and independent acceptance separately"

support = {
    "date": "2026-10-27",
    "purpose": "Version-bound reuse and supplementary dependency reading; not full source acceptance",
    "inherited_ledger": str(source_ledger_path.relative_to(ROOT)),
    "inherited_ledger_sha256": sha(source_ledger_path),
    "reused_records": selected,
    "additional_records": additional,
    "financing_records": "c08-source-review.md and c08-verification.json",
    "metadata_limit": "Retain dated bounded original metadata checks; no exhaustive correction clearance or journal equivalence inferred",
}
result = {
    "status": "bounded_current_scope_review_recorded",
    "checks_passed": len(checks),
    "checks": checks,
    "newly_reviewed_claims": sorted(reviewed),
    "separately_reviewed_claims": ["C08", "C24"],
    "unreaccepted_claims": [r["id"] for r in ledger["rows"]
                            if r["review_status"] == "inherited_support_not_newly_reaccepted"],
    "manual_semantic_review": "current-scopes-review.md",
    "integrity_is_not_proof_acceptance": True,
    "manifest": {
        "git_commit": "N/A: unusable .git marker; no repository initialized",
        "command": "python3 data/accounting-master/consequential-source-review-20261027/record_current_scopes.py",
        "environment": platform.python_version(),
        "cpu_gpu": "Python standard library file checks; no GPU framework imported",
        "data_version": ledger["baseline_sha256"],
        "random_seeds": "N/A: deterministic integrity verification",
        "wall_seconds": time.time() - started,
        "plan": "docs/plans/accounting-consequential-source-review-20261027.md",
        "result": str(dest.relative_to(ROOT)),
        "script_sha256": sha(Path(__file__)),
        "input_ledger_sha256": hashlib.sha256(ledger_bytes).hexdigest(),
        "stopping_diagnostic_sha256": sha(stopping_path),
        "manual_review_sha256": sha(OUT / "current-scopes-review.md"),
        "eder_metadata_sha256": sha(OUT / "sources/eder-arxiv-20261027.html"),
    },
}
with backup.open("xb") as stream:
    stream.write(ledger_bytes)
with support_dest.open("x") as stream:
    stream.write(json.dumps(support, indent=2, ensure_ascii=False) + "\n")
ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
with dest.open("x") as stream:
    stream.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({k: result[k] for k in
                  ("status", "checks_passed", "newly_reviewed_claims", "unreaccepted_claims")}))
