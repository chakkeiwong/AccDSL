#!/usr/bin/env python3
"""Bind the reviewed Version 2.31, source unit and four live controls."""

import hashlib
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")


def main():
    start = time.monotonic()
    checks = []

    def check(name, passed):
        checks.append({"check": name, "passed": bool(passed)})

    manuscript = json.loads((OUT / "manuscript-checks.json").read_text())
    baseline = json.loads((OUT / "baseline.json").read_text())
    renders = json.loads((OUT / "render-manifest.json").read_text())
    source = ROOT / "data/accounting-master/jpmorgan-succession-20261011"
    source_manifest = json.loads((source / "run-manifest.json").read_text())

    check("84/0 manuscript checks", manuscript["passed"] == 84 and manuscript["failed"] == 0)
    for key in ("baseline_pdf", "candidate_pdf"):
        item = manuscript[key]
        check(key + " bytes match", sha(ROOT / item["path"]) == item["sha256"])
    check(
        "final eleven-page render bound",
        renders["pdf_sha256"] == manuscript["candidate_pdf"]["sha256"]
        and len(renders["rendered_pages"]) == 11
        and [p["pdf_page_index"] for p in renders["rendered_pages"]] == list(range(114, 125))
        and all(sha(ROOT / p["image"]) == p["sha256"] for p in renders["rendered_pages"]),
    )
    relocations = baseline["pointer_relocations"]
    check(
        "four previous controls preserved",
        len(relocations) == 4
        and all(sha(ROOT / p["preserved_path"]) == p["sha256"] for p in relocations),
    )
    controls = {p["historical_path"]: sha(ROOT / p["historical_path"]) for p in relocations}
    for path in controls:
        body = (ROOT / path).read_text()
        check(
            "live control " + path,
            "Version 2.31" in body
            and manuscript["candidate_pdf"]["sha256"] in body
            and "not_ready" in body,
        )
    for name in ("result.md", "author-review.md", "four-ledger-review.md", "next-source-frontier.md"):
        check(name + " exists", (OUT / name).is_file())
    check("source manifest records 84/0", source_manifest["source_checks"] == {"passed": 84, "failed": 0})
    check(
        "source artifact hashes remain valid",
        all(sha(ROOT / path) == digest for path, digest in source_manifest["artifact_hashes"].items()),
    )
    source_status = json.loads((source / "browser-inspection.json").read_text())
    check(
        "unsupported original claims excluded",
        source_status.get("verification_status") == "UNSUPPORTED_ORIGINAL_TEXT_READING"
        and source_status.get("admitted_original_findings") == [],
    )
    check(
        "2022 trustee correction recorded",
        "page 330" in (OUT / "result.md").read_text()
        and "page 330" in (ROOT / "docs/plans/accounting-master-checkpoint.md").read_text(),
    )

    if any(not item["passed"] for item in checks):
        write("closeout-checks.json", {"checks": checks, "failed": sum(not x["passed"] for x in checks)})
        raise SystemExit(1)

    paths = [
        p for p in OUT.rglob("*")
        if p.is_file() and p.name not in {"run-manifest.json", "closeout-checks.json", "completion.json"}
        and "__pycache__" not in p.parts
    ]
    paths += [
        ROOT / manuscript["plan"],
        ROOT / "docs/plans/accounting-jpmorgan-succession-20261011.md",
        source / "run-manifest.json",
    ]
    manifest = {
        "recorded_at": "2026-10-11",
        "unit": "Version 2.31 succession/source-context manuscript integration",
        "git_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip(),
        "git_branch": "main",
        "git_state": "Unrelated work preserved; read-only .git prevents commit; no retry.",
        "plan": manuscript["plan"],
        "result": str((OUT / "result.md").relative_to(ROOT)),
        "candidate_pdf": manuscript["candidate_pdf"],
        "baseline_pdf": manuscript["baseline_pdf"],
        "commands": [
            "TEXMFVAR=/tmp/accdsl-texmfvar TEXMFCACHE=/tmp/accdsl-texmfvar latexmk -g -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex",
            "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v231-integration-20261011/check_integration.py",
            "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v231-integration-20261011/closeout.py",
        ],
        "environment": {
            "tex": "LuaHBTeX 1.24.0 / Latexmk 4.88 / TinyTeX",
            "python": "Python 3.11",
            "cpu_gpu": "CPU-only documentary checks; GPU intentionally hidden",
            "random_seeds": "N/A; deterministic",
        },
        "wall_time": {
            "build": "Not measured end-to-end; no inferred duration",
            "verification": json.loads((OUT / "check-run.json").read_text())["wall_seconds"],
            "closeout_seconds": time.monotonic() - start,
        },
        "data_version": source_manifest["data_version"],
        "source_checks": 84,
        "manuscript_checks": 84,
        "controls": controls,
        "pointer_relocations": relocations,
        "source_manifest": {
            "path": str((source / "run-manifest.json").relative_to(ROOT)),
            "sha256": sha(source / "run-manifest.json"),
        },
        "artifact_hashes": {str(p.relative_to(ROOT)): sha(p) for p in paths},
        "readiness": "not_ready",
        "independent_reader": "pending",
        "domain_acceptance": "pending",
        "legal_acceptance": "pending",
    }
    write("run-manifest.json", manifest)
    report = {
        "recorded_at": "2026-10-11",
        "checks": checks,
        "passed": len(checks),
        "failed": 0,
        "run_manifest_sha256": sha(OUT / "run-manifest.json"),
        "wall_seconds": time.monotonic() - start,
    }
    write("closeout-checks.json", report)
    write("completion.json", {
        "status": "closed_bounded_integration",
        "recorded_at": "2026-10-11",
        "candidate_pdf": manuscript["candidate_pdf"],
        "source_checks": 84,
        "manuscript_checks": 84,
        "closeout_checks": len(checks),
        "run_manifest_sha256": report["run_manifest_sha256"],
        "readiness": "not_ready",
        "next_frontier": str((OUT / "next-source-frontier.md").relative_to(ROOT)),
    })
    print(json.dumps({"passed": len(checks), "failed": 0, "candidate": manuscript["candidate_pdf"]}))


if __name__ == "__main__":
    main()
