#!/usr/bin/env python3
"""Bind two unresolved exact exhibits and the observed access failures."""
import hashlib
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = OUT / "sources"
CASE = ROOT / "docs/design/cases/apple/continuation-20261007/case-supplement-v1.json"
PLAN = ROOT / "docs/plans/accounting-apple-constitutional-sources-20261011.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")


def main():
    start = time.monotonic()
    checks = []

    def check(name, value):
        checks.append({"check": name, "passed": bool(value)})

    case = json.loads(CASE.read_text())
    rows = {r["id"]: r for r in case["reference_frontier"]}
    a, b = rows["annual.exhibit.3.1"], rows["annual.exhibit.3.2"]
    check("both historical targets unresolved", all(r["document_status"] == "unresolved_target" for r in (a, b)))
    check("articles exact date/form", a["referenced_form"] == "8-K" and a["referenced_date_or_period"] == "8/7/20" and "August 3, 2020" in a["description"])
    check("bylaws exact date/form", b["referenced_form"] == "8-K" and b["referenced_date_or_period"] == "8/23/24" and "August 20, 2024" in b["description"])
    annual = ROOT / a["reference_source"]["extraction_path"]
    check("reference extraction hash", sha(annual) == a["reference_source"]["extraction_sha256"] == b["reference_source"]["extraction_sha256"])
    text = annual.read_text()
    check("source spans exact", all(text[r["reference_source"]["start"]:r["reference_source"]["end"]] == r["reference_source"]["quote"] for r in (a, b)))
    challenge = (SRC / "governance-index-trusted.html").read_text()
    check("issuer route challenged", "403" in (SRC / "governance-index-trusted.headers").read_text() and "Just a moment" in challenge)
    sandbox = json.loads((SRC / "governance-index.receipt.json").read_text())
    check("sandbox DNS failure retained", sandbox["curl_exit"] == 6 and sandbox["bytes"] == 0)
    check("exact outbound links retained", "0001193125-20-213158" in a["target_links"][0] and "0001140361-24-038403" in b["target_links"][0])
    check("exhibit attempts have no response headers", all((SRC / name).stat().st_size == 0 for name in ("articles-2020-linked.headers", "bylaws-2024-linked.headers", "articles-2020-http1.headers", "bylaws-2024-http1.headers")))
    check("no exhibit body admitted", not any((SRC / name).exists() for name in ("articles-2020-linked.html", "bylaws-2024-linked.html", "articles-2020-http1.html", "bylaws-2024-http1.html")))
    for name in ("result.md", "author-review.md", "next-source-frontier.md"):
        check(name + " retained", (OUT / name).is_file())

    if any(not c["passed"] for c in checks):
        write("checks.json", {"checks": checks, "failed": sum(not c["passed"] for c in checks)})
        raise SystemExit(1)

    paths = [p for p in OUT.rglob("*") if p.is_file() and p.name not in {"checks.json", "run-manifest.json", "completion.json"}]
    paths += [CASE, PLAN, annual]
    manifest = {
        "recorded_at": "2026-10-11",
        "unit": "Apple 2020 articles and August 2024 bylaws exact-source attempt",
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip(),
        "git_state": "Unrelated work preserved; read-only .git prevents commit; no retry.",
        "plan": str(PLAN.relative_to(ROOT)),
        "result": str((OUT / "result.md").relative_to(ROOT)),
        "data_version": "Frozen FY2024 Apple exhibit references and retained 2025 proxy discovery lead",
        "commands": ["python3 data/accounting-master/apple-constitutional-sources-20261011/acquire.py", "curl --location <exact issuer governance URL from proxy route hypothesis>", "curl --location <two exact outbound exhibit links from case supplement>", "curl --http1.1 --location <same two exact outbound exhibit links after HTTP/2 failure>", "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/apple-constitutional-sources-20261011/closeout.py"],
        "observed_access": {"issuer_sandbox": "DNS failure; curl exit 6", "issuer_trusted": "HTTP 403; 5523-byte challenge", "exact_exhibits_http2": "both curl exit 92; zero response bytes", "exact_exhibits_http1": "both curl exit 28 after 25 seconds; zero response bytes"},
        "environment": {"python": "Python 3.11", "cpu_gpu": "CPU-only documentary checks; GPU intentionally hidden", "random_seeds": "N/A; deterministic"},
        "wall_time": {"issuer_sandbox_seconds": sandbox["elapsed_seconds"], "other_requests": "Not separately measured; bounded by command options", "closeout_seconds": time.monotonic() - start},
        "checks": len(checks),
        "artifact_hashes": {str(p.relative_to(ROOT)): sha(p) for p in paths},
        "status": "source_blocked_exact_targets",
        "readiness": "not_ready",
    }
    write("run-manifest.json", manifest)
    write("checks.json", {"checks": checks, "passed": len(checks), "failed": 0, "run_manifest_sha256": sha(OUT / "run-manifest.json")})
    write("completion.json", {"status": "closed_bounded_access_attempt", "checks": len(checks), "failed": 0, "run_manifest_sha256": sha(OUT / "run-manifest.json"), "targets_resolved": 0, "readiness": "not_ready"})
    print(json.dumps({"passed": len(checks), "failed": 0, "targets_resolved": 0}))


if __name__ == "__main__":
    main()
