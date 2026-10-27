"""Freeze the Note 33 documentary result before manuscript integration."""
import hashlib
import json
import platform
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + "\n")


def main():
    assert not (OUT / "completion.json").exists(), "Do not rewrite a completed unit"
    source = json.loads((OUT / "source-manifest.json").read_text())
    ledger = json.loads((OUT / "source-ledger.json").read_text())
    report = json.loads((OUT / "checks.json").read_text())
    checks = []

    def ck(name, value):
        checks.append({"check": name, "passed": bool(value)})

    ck("74 source and arithmetic checks", report["passed"] == 74 and report["failed"] == 0 and all(x["passed"] for x in report["checks"]))
    ck("source PDF intact", sha(ROOT / source["source_pdf"]) == source["source_pdf_sha256"])
    ck("Version 2.34 candidate intact", sha(ROOT / source["candidate_pdf"]) == source["candidate_pdf_sha256"])
    ck("three pages retained", [x["pdf_page"] for x in source["pages"]] == [21, 312, 313])
    for page in source["pages"]:
        for field in ["reading", "layout", "render"]:
            ck(f"{field} page {page['pdf_page']}", sha(ROOT / page[field]) == page[field + "_sha256"])
    ck("27 selected rows", len(ledger["selected_rows"]) == 27)
    ck("seven qualifiers", len(ledger["qualifiers"]) == 7)
    for row in ledger["selected_rows"] + ledger["qualifiers"]:
        content = (ROOT / row["source_text"]).read_text()
        ck("span " + row["id"], content[row["start"]:row["end"]] == row["quote"] and hashlib.sha256(row["quote"].encode()).hexdigest() == row["span_sha256"])
    for control in source["pointer_snapshots"]:
        ck("prior control " + control["live"], sha(ROOT / control["snapshot"]) == control["sha256"])
        ck("still-current 2.34 control " + control["live"], source["candidate_pdf_sha256"] in (ROOT / control["live"]).read_text())
    for name in ["result.md", "author-review.md", "next-source-frontier.md"]:
        ck("result artifact " + name, (OUT / name).is_file())
    failures = [x["check"] for x in checks if not x["passed"]]
    if failures:
        print(json.dumps({"failures": failures}))
        raise SystemExit(1)
    excluded = {"run-manifest.json", "closeout-checks.json", "completion.json"}
    hashes = {str(path.relative_to(ROOT)): sha(path) for path in OUT.rglob("*") if path.is_file() and path.name not in excluded}
    plan = "docs/plans/accounting-jpmorgan-parent-note-20261012.md"
    hashes[plan] = sha(ROOT / plan)
    manifest = {
        "recorded_at": "2026-10-12",
        "unit": "JPMorgan 2025 Note 33 parent-only documentary reading",
        "git_commit": "8b6826ccb4a2a86f940f4ca04931d4a4cd901edb",
        "git_state": "main; unrelated dirty work preserved; .git read-only",
        "plan": plan,
        "result": str((OUT / "result.md").relative_to(ROOT)),
        "source_pdf": {"path": source["source_pdf"], "sha256": source["source_pdf_sha256"]},
        "data_version": "Issuer-hosted complete 2025 Form 10-K candidate; selected-byte historical availability not established",
        "environment": {"python": platform.python_version(), "pdf": "PyMuPDF and pdftotext; no ML framework", "cpu_gpu": "CPU-only; GPU intentionally hidden", "random_seeds": "N/A, deterministic documentary checks"},
        "commands": [
            "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-parent-note-20261012/prepare_sources.py",
            "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-parent-note-20261012/annotate.py",
            "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-parent-note-20261012/closeout.py",
        ],
        "wall_time_seconds": {"source_preparation": source["wall_seconds"], "annotation": report["wall_seconds"], "closeout_before_manifest": time.monotonic() - START},
        "source_checks": report["passed"], "closeout_checks": len(checks),
        "artifact_hashes": hashes, "readiness": "not_ready",
        "current_codification": "not_verified", "historical_byte_availability": "not_verified",
        "independent_accounting": "pending", "human_acceptance": "pending",
    }
    write("run-manifest.json", manifest)
    write("closeout-checks.json", {"checks": checks, "passed": len(checks), "failed": 0, "manifest_sha256": sha(OUT / "run-manifest.json")})
    write("completion.json", {"status": "closed_bounded_source_reading", "source_checks": report["passed"], "closeout_checks": len(checks), "failed": 0, "manifest_sha256": sha(OUT / "run-manifest.json"), "readiness": "not_ready"})
    print(json.dumps({"source_checks": report["passed"], "closeout_checks": len(checks), "failed": 0, "artifact_hashes": len(hashes)}))


if __name__ == "__main__":
    main()
