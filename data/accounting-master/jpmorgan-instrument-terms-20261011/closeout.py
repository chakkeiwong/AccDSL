#!/usr/bin/env python3
"""Close the bounded JPMorgan instrument-terms source unit."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
start = time.monotonic()
checks = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(label: str, passed: bool, details=None) -> None:
    row = {"check": label, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    checks.append(row)


terms = json.loads((OUT / "terms.json").read_text(encoding="utf-8"))
check("terms extraction passes", terms["passed"] == 48 and terms["failed"] == 0)
check("terms extraction has four years", [r["year"] for r in terms["records"]] == [2022, 2023, 2024, 2025])
check("terms result remains qualified", "no legal enforceability" in terms["scope"] and "outstanding-balance" in terms["scope"])

manifest = json.loads((OUT / "render-manifest.json").read_text(encoding="utf-8"))
for row in manifest["images"]:
    path = ROOT / row["path"]
    check("render hash: " + str(row["year"]) + " page " + str(row["page"]), path.is_file() and sha(path) == row["sha256"])

for name in ["result.md", "author-review.md", "next-source-frontier.md", "run-manifest.json", "terms.json", "render-manifest.json", "build_terms.py"]:
    check("artifact exists: " + name, (OUT / name).is_file())

plan = (ROOT / "docs/plans/accounting-jpmorgan-instrument-terms-20261011.md").read_text(encoding="utf-8")
check("plan records evidence contract", "Promotion criterion" in plan and "Must not be concluded" in plan)
check("plan records skeptical audit", "Skeptical audit and pre-mortem" in plan)
result = (OUT / "result.md").read_text(encoding="utf-8")
check("result records 48 checks", "48 checks pass" in result)
check("result keeps acceptance pending", "Independent reader, domain and legal" in result)

run = json.loads((OUT / "run-manifest.json").read_text(encoding="utf-8"))
check("run manifest records source-only scope", "local retained PDFs only" in run["git_worktree"])
check("run manifest records 48 checks", run["source_check_count"] == 48)
check("run manifest retains pending statuses", run["independent_reader"] == "pending" and run["domain_acceptance"] == "pending")

for row in terms["records"]:
    pdf = ROOT / row["pdf"]
    text = ROOT / row["text"]
    check(f"{row['year']} PDF identity bound", pdf.is_file() and sha(pdf) == row["pdf_sha256"] and len(fitz.open(pdf)) == row["pdf_pages"])
    check(f"{row['year']} text identity bound", text.is_file() and sha(text) == row["text_sha256"])

report = {
    "recorded_at": "2026-10-11",
    "command": ["python3", str(Path(__file__).relative_to(ROOT))],
    "checks": checks,
    "passed": sum(row["passed"] for row in checks),
    "failed": sum(not row["passed"] for row in checks),
    "wall_seconds": time.monotonic() - start,
    "scope": "Source identity, bounded terms extraction and rendered page binding; no legal, accounting, outstanding-balance or independent acceptance claim.",
}
(OUT / "closeout-checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
(OUT / "completion.json").write_text(json.dumps({
    "recorded_at": "2026-10-11",
    "status": "closed_bounded_source_unit",
    "source_checks": 48,
    "closeout_checks": report["passed"],
    "readiness": "not_ready",
    "independent_reader": "pending",
    "domain_acceptance": "pending",
    "next_frontier": "data/accounting-master/jpmorgan-instrument-terms-20261011/next-source-frontier.md",
}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: report[key] for key in ["passed", "failed", "wall_seconds"]}, indent=2))
if report["failed"]:
    raise SystemExit(1)
