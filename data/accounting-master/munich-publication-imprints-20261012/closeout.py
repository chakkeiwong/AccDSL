"""Close the recovered source inquiry without rewriting the frozen corpus."""
import datetime
import hashlib
import json
import platform
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    start = time.monotonic()
    if (OUT / "completion.json").exists():
        raise SystemExit("Closed unit stays frozen")
    baseline = json.loads((OUT / "baseline.json").read_text())
    recovery = json.loads((OUT / "recovery-baseline.json").read_text())
    source = json.loads((OUT / "source-checks.json").read_text())
    dates = json.loads((OUT / "date-evidence.json").read_text())
    checks = []

    def ck(name, value):
        checks.append({"name": name, "passed": bool(value)})

    ck("source checks passed", not source["failed"] and all(c["passed"] for c in source["checks"]))
    ck("sixteen distinct report dates", len(dates["primary"]) == 16
       and len({r["document_id"] for r in dates["primary"]}) == 16)
    ck("channel labels retained", sum(r["publication_channel"] == "online" for r in dates["primary"]) == 14)
    ck("no unsupported intraday precision", all(r["date_precision"] == "day"
       and r["time_of_day"] is None and r["timezone"] is None for r in dates["primary"]))
    ck("failed run preserved", len(json.loads((OUT / "recovery-before/source-checks.json").read_text())["failed"]) == 2)
    for row in dates["primary"]:
        ck("source identity " + row["document_id"], sha(ROOT / row["pdf"]) == row["pdf_sha256"])
    for path, digest in recovery["protected_hashes"].items():
        ck("protected " + path, sha(ROOT / path) == digest)
    controls = {}
    for row in baseline["pointer_snapshots"]:
        ck("snapshot " + row["live"], sha(ROOT / row["snapshot"]) == row["sha256"])
        current = ROOT / row["live"]
        text = current.read_text()
        ck("current pointer " + row["live"], "munich-publication-imprints-20261012/result.md" in text
           and "not_ready" in text and "accounting-publication-frontier-20261013.md" in text)
        controls[row["live"]] = sha(current)
    for name in ["result.md", "author-review.md", "next-source-frontier.md", "visual-review.json"]:
        ck("review record " + name, (OUT / name).is_file())
    failed = [c["name"] for c in checks if not c["passed"]]
    if failed:
        print(json.dumps({"failed": failed}))
        raise SystemExit(1)
    excluded = {"run-manifest.json", "completion.json", "closeout-checks.json"}
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob("*")
              if p.is_file() and p.name not in excluded and p.suffix != ".pyc"}
    plan = "docs/plans/accounting-munich-publication-imprints-20261012.md"
    hashes[plan] = sha(ROOT / plan)
    manifest = {
        "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": recovery["git_commit"], "branch": recovery["branch"],
        "git_state": "Existing unrelated staged/dirty work preserved; explicit-path commit follows closeout",
        "plan": plan, "result": str((OUT / "result.md").relative_to(ROOT)),
        "data_version": "Frozen selected-source evidence " + baseline["source_evidence_sha256"],
        "environment": {"python": platform.python_version(),
                        "cpu_gpu": "CPU-only source parsing and PDF inspection; no GPU detection or framework imports",
                        "random_seeds": "N/A deterministic source inspection"},
        "commands_actually_run_during_recovery": [
            "python3 data/accounting-master/munich-publication-imprints-20261012/check_dates.py",
            "python3 data/accounting-master/munich-publication-imprints-20261012/closeout.py"],
        "prior_preparation": "Recovered prepare.py/read_pages.py outputs; original invocation timing not reconstructed",
        "wall_time_seconds": {"repaired_source_checks": source["wall_seconds"],
                              "closeout_before_manifest": time.monotonic() - start,
                              "prior_preparation": "not recorded"},
        "source_checks": source["passed"], "closeout_checks": len(checks),
        "pointer_snapshots": baseline["pointer_snapshots"], "controls_at_closeout": controls,
        "protected_hashes": recovery["protected_hashes"], "artifact_hashes": hashes,
        "historical_byte_admissions": 0, "new_author_exposed_reports": 16,
        "readiness": "not_ready"}
    save("run-manifest.json", manifest)
    digest = sha(OUT / "run-manifest.json")
    save("closeout-checks.json", {"checks": checks, "passed": len(checks), "failed": [], "manifest_sha256": digest})
    save("completion.json", {"status": "closed_attributed_publication_dates",
                             "source_checks": source["passed"], "closeout_checks": len(checks),
                             "failed": [], "manifest_sha256": digest, "readiness": "not_ready"})
    print(json.dumps({"source_checks": source["passed"], "closeout_checks": len(checks), "failed": []}))


if __name__ == "__main__":
    main()
