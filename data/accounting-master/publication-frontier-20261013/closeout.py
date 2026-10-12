"""Freeze the discovery and nineteen declarations after source review."""
import datetime
import hashlib
import json
import platform
import re
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((OUT / name).read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    assert not (OUT / "completion.json").exists(), "Closed evidence remains frozen"
    start = time.monotonic()
    baseline = read("baseline.json")
    reports = [read("henkel-checks.json"), read("hsbc-checks.json")]
    rows = read("henkel-date-evidence.json")["primary"] + read("hsbc-date-evidence.json")["primary"]
    checks = []

    def ck(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    ck("110 source checks pass", sum(r["passed"] for r in reports) == 110
       and all(not r["failed"] and all(c["passed"] for c in r["checks"]) for r in reports))
    ck("nineteen distinct source declarations", len(rows) == len({r["document_id"] for r in rows}) == 19)
    ck("date precision and availability limits retained", all(r["date_precision"] == "day"
       and r["time_of_day"] is None and r["timezone"] is None
       and r["historical_unchanged_byte_availability"] == "not independently established" for r in rows))
    for row in rows:
        ck("report identity " + row["document_id"], sha(ROOT / row["pdf"]) == row["pdf_sha256"])
    discovery = read("discovery.json")
    ck("discovery is 120 unique active reports", len(discovery["records"]) == 120
       and len({r["document_id"] for r in discovery["records"]}) == 120)
    recovery = json.loads((ROOT / "data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json").read_text())
    for rel, digest in recovery["protected_hashes"].items():
        ck("protected " + rel, sha(ROOT / rel) == digest)
    for rel, digest in baseline["input_hashes"].items():
        ck("baseline " + rel, sha(ROOT / rel) == digest)
    controls = {}
    for row in baseline["controls"]:
        ck("snapshot " + row["live"], sha(ROOT / row["snapshot"]) == row["sha256"])
        p = ROOT / row["live"]
        text = p.read_text()
        ck("live control " + row["live"], "publication-frontier-20261013/result.md" in text
           and "accounting-jpmorgan-filing-events-20261013.md" in text and "not_ready" in text)
        if "requirements" not in p.name:
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if not target.startswith(("http", "#")):
                    ck("local link " + target, (p.parent / target.split("#")[0]).exists())
        controls[row["live"]] = sha(p)
    failed = [r["name"] for r in checks if not r["passed"]]
    if failed:
        print(json.dumps({"failed": failed}))
        raise SystemExit(1)
    excluded = {"run-manifest.json", "completion.json", "closeout-checks.json"}
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob("*")
              if p.is_file() and p.name not in excluded and p.suffix != ".pyc"}
    plan = "docs/plans/accounting-publication-frontier-20261013.md"
    hashes[plan] = sha(ROOT / plan)
    manifest = {"completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": baseline["git_commit"], "plan": plan,
        "result": str((OUT / "result.md").relative_to(ROOT)),
        "data_version": "Frozen active panel v2 and selected source evidence; 32 superseded records excluded",
        "environment": {"python": platform.python_version(),
                        "pdf_library": "PyMuPDF", "cpu_gpu": "CPU-only; no GPU/framework probes",
                        "random_seeds": "N/A deterministic source discovery and inspection"},
        "commands": ["python3 data/accounting-master/publication-frontier-20261013/discover.py",
                     "python3 data/accounting-master/publication-frontier-20261013/read_henkel.py",
                     "python3 data/accounting-master/publication-frontier-20261013/check_henkel.py",
                     "python3 inline report-specific regex discovery and two-page HSBC capture (patterns/capture hashes retained)",
                     "python3 data/accounting-master/publication-frontier-20261013/check_hsbc.py",
                     "python3 data/accounting-master/publication-frontier-20261013/closeout.py"],
        "wall_seconds": {"discovery": discovery["wall_seconds"],
                         "source_checks": sum(r["wall_seconds"] for r in reports),
                         "closeout_before_manifest": time.monotonic() - start,
                         "interactive_reading": "not timed"},
        "source_checks": 110, "closeout_checks": len(checks), "historical_byte_admissions": 0,
        "new_author_exposed_reports": [r["document_id"] for r in rows],
        "artifact_hashes": hashes, "controls_at_closeout": controls,
        "readiness": "not_ready"}
    save("run-manifest.json", manifest)
    digest = sha(OUT / "run-manifest.json")
    save("closeout-checks.json", {"checks": checks, "passed": len(checks), "failed": [], "manifest_sha256": digest})
    save("completion.json", {"status": "closed_discovery_and_nineteen_declared_dates", "source_checks": 110,
                             "closeout_checks": len(checks), "failed": [], "manifest_sha256": digest,
                             "readiness": "not_ready"})
    print(json.dumps({"source_checks": 110, "closeout_checks": len(checks), "failed": []}))


if __name__ == "__main__":
    main()
