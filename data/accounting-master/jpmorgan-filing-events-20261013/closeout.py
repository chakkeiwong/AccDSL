"""Close a revalidation without counting prior sources as new acquisitions."""
import datetime
import hashlib
import json
import platform
import re
import subprocess
import time
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((OUT / name).read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    assert not (OUT / "completion.json").exists(), "Closed evidence stays frozen"
    start = time.monotonic()
    baseline = read("baseline.json")
    report = read("source-checks.json")
    checks = []

    def ck(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    ck("forty source checks pass", report["passed"] == 40 and not report["failed"]
       and all(c["passed"] for c in report["checks"]))
    comparison = read("shared-pages-comparison.json")
    source = read("selected-sources.json")["jpmorgan-2025-annual"]
    full_path = OUT / "acquisition/corp-10k-2025.pdf"
    ck("comparison source hashes", sha(full_path) == comparison["full_pdf_sha256"]
       and sha(ROOT / source["local_path"]) == comparison["wrapper_sha256"])
    with fitz.open(full_path) as full, fitz.open(ROOT / source["local_path"]) as wrapper:
        verified = []
        for row in comparison["pairs"]:
            a = full[row["full_10k_pdf_page"] - 1].get_text()
            b = wrapper[row["wrapper_pdf_page"] - 1].get_text()
            verified.append(hashlib.sha256(a.encode()).hexdigest() == row["full_text_sha256"]
                            and hashlib.sha256(b.encode()).hexdigest() == row["wrapper_text_sha256"]
                            and (a == b) == row["exact_text_equal"])
        ck("all 285 saved text pairs reproduce", len(verified) == 285 and all(verified))
    recovery = json.loads((ROOT / "data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json").read_text())
    for rel, digest in recovery["protected_hashes"].items():
        ck("protected " + rel, sha(ROOT / rel) == digest)
    indexed = set(subprocess.check_output(["git", "ls-files", "--stage"], cwd=ROOT, text=True).splitlines())
    ck("all unrelated index entries preserved", all(r in indexed for r in recovery["unrelated_staged_entries"]))
    controls = {}
    for row in baseline["controls"]:
        ck("snapshot " + row["live"], sha(ROOT / row["snapshot"]) == row["sha256"])
        p = ROOT / row["live"]
        text = p.read_text()
        ck("current control " + row["live"], "jpmorgan-filing-events-20261013/result.md" in text
           and "accounting-pingan-archive-fields-20261013.md" in text and "not_ready" in text)
        if "requirements" not in p.name:
            targets = re.findall(r"\]\(([^)]+)\)", text)
            ck("local links " + row["live"], all((p.parent / t.split("#")[0]).exists()
               for t in targets if not t.startswith(("http", "#"))))
        controls[row["live"]] = sha(p)
    ck("next plan exists", (ROOT / "docs/plans/accounting-pingan-archive-fields-20261013.md").is_file())
    failed = [r["name"] for r in checks if not r["passed"]]
    if failed:
        print(json.dumps({"failed": failed}))
        raise SystemExit(1)
    excluded = {"run-manifest.json", "completion.json", "closeout-checks.json"}
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob("*")
              if p.is_file() and p.name not in excluded and p.suffix != ".pyc"}
    plan = "docs/plans/accounting-jpmorgan-filing-events-20261013.md"
    hashes[plan] = sha(ROOT / plan)
    manifest = {
        "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": baseline["git_commit"], "plan": plan,
        "result": str((OUT / "result.md").relative_to(ROOT)),
        "data_version": "Frozen active panel v2; retained SEC response and already acquired 2025 full 10-K",
        "environment": {"python": platform.python_version(), "pdf_library": fitz.VersionBind,
                        "cpu_gpu": "CPU-only; no GPU/framework probes", "random_seeds": "N/A deterministic source comparison"},
        "commands": ["python3 data/accounting-master/jpmorgan-filing-events-20261013/prepare.py",
                     "curl request and trusted retry; exact URL and transport results retained in acquisition/",
                     "Python inline full-PDF capture and shared-page comparison; page mappings and hashes retained",
                     "python3 data/accounting-master/jpmorgan-filing-events-20261013/check_evidence.py",
                     "python3 data/accounting-master/jpmorgan-filing-events-20261013/closeout.py"],
        "wall_seconds": {"source_checks": report["wall_seconds"],
                         "trusted_download": read("acquisition/trusted-curl-result.json")["time_total"],
                         "closeout_before_manifest": time.monotonic() - start, "interactive_reading": "not timed"},
        "source_checks": 40, "closeout_checks": len(checks), "new_filing_events": 0,
        "new_source_acquisitions": 0, "historical_byte_admissions": 0,
        "new_comparison": {"page_pairs": 285, "identical_raw_text": 284, "difference": "wrapper omission note"},
        "artifact_hashes": hashes, "controls_at_closeout": controls, "readiness": "not_ready"}
    save("run-manifest.json", manifest)
    digest = sha(OUT / "run-manifest.json")
    save("closeout-checks.json", {"checks": checks, "passed": len(checks), "failed": [], "manifest_sha256": digest})
    save("completion.json", {"status": "closed_revalidation_and_text_comparison", "source_checks": 40,
                             "closeout_checks": len(checks), "failed": [], "manifest_sha256": digest,
                             "readiness": "not_ready"})
    print(json.dumps({"source_checks": 40, "closeout_checks": len(checks), "failed": []}))


if __name__ == "__main__":
    main()
