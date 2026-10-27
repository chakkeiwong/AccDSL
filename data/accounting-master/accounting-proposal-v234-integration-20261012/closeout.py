"""Close the bounded Version 2.34 integration without changing frozen predecessors."""

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


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")


def main():
    assert not (OUT / "completion.json").exists(), "Closed evidence stays frozen"
    checks = []

    def ck(name, passed):
        checks.append({"check": name, "passed": bool(passed)})

    report = json.loads((OUT / "check-run.json").read_text())
    baseline = json.loads((OUT / "baseline.json").read_text())
    renders = json.loads((OUT / "render-manifest.json").read_text())
    candidate = ROOT / baseline["candidate"]
    pdf = candidate / "accounting-product-proposal.pdf"
    ck("integration checks pass", report["checks"] == 130 and not report["failed"])
    ck("candidate hash matches checks and renders", sha(pdf) == report["pdf_sha256"] == renders["pdf_sha256"])
    ck("candidate has 173 pages", report["pages"] == 173)
    ck("baseline PDF preserved", sha(ROOT / baseline["baseline_pdf"]["path"]) == baseline["baseline_pdf"]["sha256"])
    ck("ten required renders", [r["pdf_page"] for r in renders["renders"]] == [118, 119, 120, 121, 122, 123, 124, 125, 168, 169])
    for row in renders["renders"]:
        ck("render page " + str(row["pdf_page"]), sha(ROOT / row["image"]) == row["sha256"])
    for name in ["result.md", "author-review.md", "four-ledger-review.md", "next-source-frontier.md", "surface-audit.json", "surface-audit.md"]:
        ck("review artifact " + name, (OUT / name).is_file())
    controls = {}
    for row in baseline["pointer_snapshots"]:
        ck("frozen prior control " + row["live"], sha(ROOT / row["snapshot"]) == row["sha256"])
        live = ROOT / row["live"]
        content = live.read_text()
        ck("live control points to candidate " + row["live"], "Version 2.34" in content and report["pdf_sha256"] in content)
        ck("live control preserves negative readiness " + row["live"], "not_ready" in content)
        controls[row["live"]] = sha(live)
    review = (OUT / "four-ledger-review.md").read_text()
    ck("independent and human acceptance pending", "Independent-reader and human acceptance pending" in review)
    ck("historical source limit retained", "current Codification" in (OUT / "result.md").read_text())
    failures = [r["check"] for r in checks if not r["passed"]]
    if failures:
        print(json.dumps({"failures": failures}))
        raise SystemExit(1)

    excluded = {"run-manifest.json", "closeout-checks.json", "completion.json"}
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob("*") if p.is_file() and p.name not in excluded}
    plan = "docs/plans/accounting-historical-credit-loss-integration-20261012.md"
    hashes[plan] = sha(ROOT / plan)
    for path in candidate.rglob("*"):
        if path.is_file() and path.suffix in {".tex", ".bib", ".lark", ".pdf", ".log", ".blg"}:
            hashes[str(path.relative_to(ROOT))] = sha(path)
    manifest = {
        "recorded_at": "2026-10-12",
        "unit": "Version 2.34 bounded historical-credit-loss integration",
        "git_commit": "8b6826ccb4a2a86f940f4ca04931d4a4cd901edb",
        "git_state": "main; unrelated dirty work preserved; .git read-only",
        "plan": plan,
        "result": str((OUT / "result.md").relative_to(ROOT)),
        "candidate_pdf": {"path": str(pdf.relative_to(ROOT)), "sha256": sha(pdf), "pages": report["pages"]},
        "baseline_pdf": baseline["baseline_pdf"],
        "data_version": "Retained official historical ASU units and frozen Version 2.33 candidate",
        "environment": {
            "python": platform.python_version(),
            "typesetter": "LuaLaTeX/TinyTeX via latexmk",
            "cpu_gpu": "CPU-only documentary/build checks; GPU not used; no ML framework imported",
            "random_seeds": "N/A; deterministic document checks",
        },
        "commands": [
            "python3 data/accounting-master/accounting-proposal-v234-integration-20261012/build_candidate.py",
            "final latexmk build: exact outer invocation not retained verbatim; build log records lualatex -interaction=nonstopmode -halt-on-error -recorder accounting-product-proposal.tex",
            "python3 data/accounting-master/accounting-proposal-v234-integration-20261012/check_integration.py",
            "python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py <candidate>/chapters/15-banking.tex --pdf <candidate>/accounting-product-proposal.pdf --output-json <unit>/surface-audit.json --output-md <unit>/surface-audit.md",
            "python3 data/accounting-master/accounting-proposal-v234-integration-20261012/closeout.py",
        ],
        "build_workdir": str(candidate.relative_to(ROOT)),
        "wall_time_seconds": {
            "final_build": float((OUT / "final-build-seconds.txt").read_text().strip()),
            "final_layout_build": float((OUT / "final-layout-seconds.txt").read_text().strip()),
            "integration_check": report["wall_seconds"],
            "closeout_before_manifest": time.monotonic() - START,
        },
        "integration_checks": report["checks"],
        "closeout_checks": len(checks),
        "controls": controls,
        "pointer_snapshots": baseline["pointer_snapshots"],
        "artifact_hashes": hashes,
        "readiness": "not_ready",
        "independent_reader": "pending",
        "human_acceptance": "pending",
        "runtime_compatibility": "not_tested",
        "current_codification": "not_verified",
    }
    write("run-manifest.json", manifest)
    write("closeout-checks.json", {"checks": checks, "passed": len(checks), "failed": 0, "manifest_sha256": sha(OUT / "run-manifest.json")})
    write("completion.json", {"status": "closed_bounded_manuscript_integration", "integration_checks": report["checks"], "closeout_checks": len(checks), "failed": 0, "manifest_sha256": sha(OUT / "run-manifest.json"), "readiness": "not_ready"})
    print(json.dumps({"integration_checks": report["checks"], "closeout_checks": len(checks), "failed": 0, "artifact_hashes": len(hashes)}))


if __name__ == "__main__":
    main()
