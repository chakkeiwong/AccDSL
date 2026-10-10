#!/usr/bin/env python3
"""Close the Version 2.27 integration without rewriting frozen evidence."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
start = time.monotonic()
checks: list[dict] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(label: str, ok: bool, details=None) -> None:
    row = {"check": label, "passed": bool(ok)}
    if details is not None:
        row["details"] = details
    checks.append(row)


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


baseline = load("data/accounting-master/accounting-proposal-v227-integration-20261011/baseline.json")
candidate = ROOT / baseline["candidate_pdf"]["path"]
old_pdf = ROOT / baseline["baseline_pdf"]["path"]
expected_pdf_sha = baseline["candidate_pdf"]["sha256"]
check("candidate PDF remains bound", candidate.is_file() and sha(candidate) == expected_pdf_sha)
check("prior Version 2.26 PDF remains frozen", old_pdf.is_file() and sha(old_pdf) == baseline["baseline_pdf"]["sha256"])
with fitz.open(candidate) as doc:
    check("candidate page count remains 168", len(doc) == 168)

checker = load("data/accounting-master/accounting-proposal-v227-integration-20261011/manuscript-checks.json")
check("focused manuscript checker passes", checker["failed"] == 0 and checker["passed"] == 86)
check("focused checker binds the current candidate", checker["candidate_pdf"]["sha256"] == expected_pdf_sha)

render = load("data/accounting-master/accounting-proposal-v227-integration-20261011/render-manifest.json")
check("render manifest binds the current candidate", render["pdf_sha256"] == expected_pdf_sha and render["pages"] == 168)
for row in render["images"]:
    path = ROOT / row["path"]
    check("rendered page hash: " + str(row["page"]), path.is_file() and sha(path) == row["sha256"])

semantic = load("data/accounting-master/accounting-package-semantic-annotation-20261011/checks.json")
exhibits = load("data/accounting-master/jpmorgan-subsidiary-guarantees-20261011/checks.json")
check("semantic source unit remains passing", semantic["passed"] == 108 and semantic["failed"] == 0)
check("Exhibit source unit remains passing", exhibits["passed"] == 147 and exhibits["failed"] == 0)
prior_manifest = ROOT / baseline["prior_manifest"]
check("prior JPMorgan manifest identity remains frozen", sha(prior_manifest) == baseline["prior_manifest_sha256"])

for name in ["result.md", "author-review.md", "four-ledger-review.md", "next-source-frontier.md", "run-manifest.json", "manuscript-checks.json"]:
    check("integration artifact exists: " + name, (OUT / name).is_file())
result_text = (OUT / "result.md").read_text(encoding="utf-8")
check("result records the final PDF identity", expected_pdf_sha in result_text and "86 checks" in result_text)
check("result leaves acceptance pending", "independent-reader, domain and human acceptance remain pending" in " ".join(result_text.split()))

plan_text = (ROOT / "docs/plans/accounting-jpmorgan-manuscript-integration-20261011.md").read_text(encoding="utf-8")
check("integration plan retains its evidence contract", "Promotion requires an actual TeX/PDF delta" in plan_text and "independent_reader_pending" in plan_text)

control_paths = [
    ROOT / "docs/plans/accounting-master-checkpoint.md",
    ROOT / "docs/plans/accounting-master-current.md",
    ROOT / "docs/plans/accounting-continuation-requirements-20261007.md",
    ROOT / "data/accounting-master/next-plan.md",
]
for path in control_paths:
    text = path.read_text(encoding="utf-8")
    check("live control names Version 2.27: " + str(path.relative_to(ROOT)), "Version 2.27" in text)
    check("live control binds final PDF hash: " + str(path.relative_to(ROOT)), expected_pdf_sha in text)
    check("live control keeps readiness negative: " + str(path.relative_to(ROOT)), "not_ready" in text)

for pointer in baseline["pointer_relocations"]:
    path = ROOT / pointer["preserved_path"]
    check("preserved pointer: " + pointer["preserved_path"], path.is_file() and sha(path) == pointer["sha256"])

run_manifest = load("data/accounting-master/accounting-proposal-v227-integration-20261011/run-manifest.json")
check("run manifest binds final PDF", run_manifest["pdf"]["sha256"] == expected_pdf_sha and run_manifest["pdf"]["pages"] == 168)
check("run manifest records the 86-check result", run_manifest["manuscript_checks"] == 86)
check("run manifest leaves independent/domain acceptance pending", run_manifest["independent_reader"] == "pending" and run_manifest["domain_acceptance"] == "pending")

report = {
    "recorded_at": "2026-10-11",
    "command": ["python3", str(Path(__file__).relative_to(ROOT))],
    "candidate_pdf": {"path": str(candidate.relative_to(ROOT)), "sha256": sha(candidate), "pages": 168},
    "checks": checks,
    "passed": sum(row["passed"] for row in checks),
    "failed": sum(not row["passed"] for row in checks),
    "wall_seconds": time.monotonic() - start,
    "scope": "Integration closeout and control binding; no product, accounting, runtime, independent-reader or domain acceptance claim.",
}
(OUT / "closeout-checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
(OUT / "completion.json").write_text(json.dumps({
    "recorded_at": "2026-10-11",
    "status": "closed_bounded_integration",
    "candidate_pdf": report["candidate_pdf"],
    "focused_checks": 86,
    "closeout_checks": report["passed"],
    "independent_reader": "pending",
    "domain_acceptance": "pending",
    "readiness": "not_ready",
    "next_frontier": "data/accounting-master/accounting-proposal-v227-integration-20261011/next-source-frontier.md",
}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: report[key] for key in ["passed", "failed", "wall_seconds"]}, indent=2))
if report["failed"]:
    raise SystemExit(1)
