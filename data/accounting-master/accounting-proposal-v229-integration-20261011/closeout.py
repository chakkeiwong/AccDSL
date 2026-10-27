#!/usr/bin/env python3
"""Close the bounded Version 2.29 manuscript integration without rebuilding it."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT / "data/accounting-master/accounting-proposal-v228-integration-20261011"
SOURCE = ROOT / "data/accounting-master/jpmorgan-callable-indentures-20261011"
BASE_PDF = ROOT / "docs/design/proposal/manuscript-jpmorgan-terms-20261011/accounting-product-proposal.pdf"
PDF = ROOT / "docs/design/proposal/manuscript-jpmorgan-balance-20261011/accounting-product-proposal.pdf"
CONTROL_NAMES = {
    "docs/plans/accounting-master-checkpoint.md": "accounting-master-checkpoint.md",
    "docs/plans/accounting-master-current.md": "accounting-master-current.md",
    "docs/plans/accounting-continuation-requirements-20261007.md": "accounting-continuation-requirements-20261007.md",
    "data/accounting-master/next-plan.md": "next-plan.md",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def write(name: str, value: dict) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    start = time.monotonic()
    checks: list[dict] = []

    def ck(label: str, ok: bool) -> None:
        checks.append({"check": label, "passed": bool(ok)})

    old_hash = "23c4e9dd0df82a62cdfa4dcf76716f19cee7b8f47d3c50d588c66cc61791f6ab"
    new_hash = "aebe128cada22e57907e9651a43cc37b4031f2af34d951cc0bcf48dc64aa406b"
    ck("protected Version 2.28 PDF", sha(BASE_PDF) == old_hash and len(fitz.open(BASE_PDF)) == 169)
    ck("Version 2.29 PDF identity", sha(PDF) == new_hash and len(fitz.open(PDF)) == 169)

    ms = json.loads((OUT / "manuscript-checks.json").read_text())
    ck("88/0 manuscript checks", ms["passed"] == 88 and ms["failed"] == 0)
    ck("48 displayed equations unchanged", any(x["check"] == "displayed equations unchanged" and x["passed"] for x in ms["checks"]))
    ck("Version 2.28 bank prose retained", any(x["check"] == "all Version 2.28 bank prose retained" and x["passed"] for x in ms["checks"]))

    ledger = json.loads((SOURCE / "source-ledger.json").read_text())
    ck("70/0 callable-note source checks", ledger["passed"] == 70 and ledger["failed"] == 0)
    dates = [(r["filing_year"], r["reported_balance_as_of"], r["reported_aggregate_principal_usd"]) for r in ledger["rows"]]
    ck("filing years, as-of dates and principal", dates == [(2022, "2022-12-31", 5000000), (2023, "2023-12-31", 5000000), (2024, "2024-12-31", 5000000), (2025, "2024-12-31", 5000000)])
    ck("source PDF and text bytes retained", all(sha(ROOT / r["source_pdf"]) == r["source_pdf_sha256"] and sha(ROOT / r["source_text"]) == r["source_text_sha256"] for r in ledger["rows"]))
    ck("2016 Indenture blocker recorded", "HTTP 403" in ledger["official_s3_route_status"] and not (SOURCE / "sources/2016-indentures-ex4a7.htm").exists())

    render = json.loads((OUT / "render-manifest.json").read_text())
    images = render["rendered_pages"]
    ck("nine ordered rendered pages bound", render["pdf_sha256"] == new_hash and [x["pdf_page_index"] for x in images] == list(range(114, 123)) and all(sha(ROOT / x["image"]) == x["sha256"] for x in images))
    old_manifest = json.loads((PRIOR / "run-manifest.json").read_text())
    relocations = []
    for current, filename in CONTROL_NAMES.items():
        saved = OUT / "pointers-before" / filename
        old_control_hash = old_manifest["controls"][current]
        ck("pre-update control " + filename, saved.is_file() and sha(saved) == old_control_hash)
        relocations.append({"historical_path": current, "preserved_path": rel(saved), "sha256": old_control_hash, "recovered_from": "staged Git index"})

    current_text = (ROOT / "docs/plans/accounting-continuation-requirements-20261007.md").read_text()
    old_section = current_text.split("## Version 2.28 integration evidence", 1)[1].split("\n## ", 1)[0]
    ck("historical Version 2.28 status repaired", "preserved Version 2.28 manuscript" in old_section and "current manuscript" not in old_section)
    ck("four live controls point to Version 2.29", all("Version 2.29" in (ROOT / p).read_text() for p in CONTROL_NAMES))
    for name in ("result.md", "author-review.md", "four-ledger-review.md", "next-source-frontier.md"):
        ck("review artifact " + name, (OUT / name).is_file())

    failed = [x["check"] for x in checks if not x["passed"]]
    if failed:
        write("closeout-checks.json", {"recorded_at": "2026-10-11", "checks": checks, "passed": len(checks) - len(failed), "failed": len(failed), "failed_names": failed})
        raise SystemExit(1)

    baseline = {
        "recorded_at": "2026-10-11",
        "baseline_pdf": {"path": rel(BASE_PDF), "sha256": old_hash, "pages": 169},
        "pointer_relocations": relocations,
        "recovery_note": "The staged Git index held the four Version 2.28 controls with the exact hashes in its run manifest; these copies precede the live Version 2.29 pointer update.",
    }
    write("baseline.json", baseline)

    build_log = OUT / "build-stdout.log"
    build_run = {
        "recorded_at": "2026-10-11",
        "command": "TEXMFVAR=/tmp/accdsl-texmfvar TEXMFCACHE=/tmp/accdsl-texmfvar latexmk -g -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex",
        "workdir": "docs/design/proposal/manuscript-jpmorgan-balance-20261011",
        "environment": "LuaHBTeX 1.24.0 / Latexmk 4.88 / TinyTeX",
        "stdout_log": rel(build_log),
        "stdout_sha256": sha(build_log),
        "candidate_pdf_sha256": new_hash,
        "wall_time": "Original build duration was not recorded; do not infer it from file timestamps.",
    }
    write("build-run.json", build_run)

    result = OUT / "result.md"
    git_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    paths = [
        OUT / "baseline.json", OUT / "build-run.json", OUT / "build-stdout.log",
        OUT / "manuscript-checks.json", OUT / "render-manifest.json", OUT / "check_integration.py",
        OUT / "closeout.py", OUT / "result.md", OUT / "author-review.md",
        OUT / "four-ledger-review.md", OUT / "next-source-frontier.md",
        SOURCE / "source-ledger.json",
    ]
    paths.extend(OUT / "pointers-before" / name for name in CONTROL_NAMES.values())
    paths.extend(ROOT / x["image"] for x in images)
    manifest = {
        "recorded_at": "2026-10-11",
        "unit": "Version 2.29 callable-note manuscript integration and bounded author closeout",
        "git_commit": git_commit,
        "git_branch": "main",
        "git_worktree": "Extensive unrelated dirty work preserved; .git mounted read-only; no Git write attempted.",
        "plan": "docs/plans/accounting-jpmorgan-callable-manuscript-integration-20261011.md",
        "source_plan": "docs/plans/accounting-jpmorgan-callable-balance-indentures-20261011.md",
        "result": rel(result),
        "candidate_pdf": {"path": rel(PDF), "sha256": new_hash, "pages": 169},
        "baseline_pdf": baseline["baseline_pdf"],
        "commands": [
            "python3 data/accounting-master/jpmorgan-callable-indentures-20261011/build_source_ledger.py",
            build_run["command"],
            "python3 data/accounting-master/accounting-proposal-v229-integration-20261011/check_integration.py",
            "python3 data/accounting-master/accounting-proposal-v229-integration-20261011/closeout.py",
        ],
        "environment": {"source_checks": "Python 3.11 CPU; no GPU framework initialized", "document_build": build_run["environment"], "gpu_status": "No GPU used; document and source-verification work", "random_seeds": "N/A; deterministic documentary checks"},
        "data_version": "Four retained issuer-hosted 2022–2025 Form 10-K PDFs and texts, individually hash-bound in source-ledger.json",
        "wall_time": {"original_build": build_run["wall_time"], "closeout_seconds": time.monotonic() - start},
        "source_checks": {"passed": 70, "failed": 0},
        "manuscript_checks": {"passed": 88, "failed": 0},
        "rendered_pages": list(range(114, 123)),
        "pointer_relocations": relocations,
        "controls": {p: sha(ROOT / p) for p in CONTROL_NAMES},
        "artifact_hashes": {rel(p): sha(p) for p in paths},
        "readiness": "not_ready",
        "independent_reader": "pending",
        "domain_acceptance": "pending",
        "legal_acceptance": "pending",
        "source_limit": "Original 2016 Indenture, supplements and amendments uninspected; SEC Archives route returned HTTP 403.",
    }
    write("run-manifest.json", manifest)
    manifest_hash = sha(OUT / "run-manifest.json")
    checks.append({"check": "run manifest binds four live controls and preserved prior controls", "passed": all(sha(ROOT / p) == h for p, h in manifest["controls"].items()) and len(relocations) == 4})
    report = {
        "recorded_at": "2026-10-11",
        "candidate_pdf": manifest["candidate_pdf"],
        "run_manifest_sha256": manifest_hash,
        "checks": checks,
        "passed": sum(x["passed"] for x in checks),
        "failed": sum(not x["passed"] for x in checks),
        "wall_seconds": time.monotonic() - start,
        "scope": "Bounded author closeout; no accounting, legal, independent-reader or full-readiness acceptance.",
    }
    write("closeout-checks.json", report)
    write("completion.json", {
        "recorded_at": "2026-10-11",
        "status": "closed_bounded_integration",
        "candidate_pdf": manifest["candidate_pdf"],
        "source_checks": 70,
        "manuscript_checks": 88,
        "closeout_checks": report["passed"],
        "run_manifest_sha256": manifest_hash,
        "readiness": "not_ready",
        "independent_reader": "pending",
        "domain_acceptance": "pending",
        "legal_acceptance": "pending",
        "next_frontier": rel(OUT / "next-source-frontier.md"),
    })
    print(json.dumps({"passed": report["passed"], "failed": report["failed"], "pdf_sha256": new_hash, "wall_seconds": report["wall_seconds"]}))


if __name__ == "__main__":
    main()
