"""Freeze the scoped archive inquiry and record its actual evidence limits."""
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


def load(path):
    return json.loads(path.read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    assert not (OUT / "completion.json").exists()
    start = time.monotonic()
    baseline = load(OUT / "baseline.json")
    source = load(OUT / "source-checks.json")
    checks = []

    def ck(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    ck("123 source checks pass", source["passed"] == 123 and not source["failed"]
       and all(c["passed"] for c in source["checks"]))
    recovery = load(ROOT / "data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json")
    for rel, digest in recovery["protected_hashes"].items():
        ck("protected " + rel, sha(ROOT / rel) == digest)
    controls = {}
    for row in baseline["controls"]:
        ck("prior control " + row["live"], sha(ROOT / row["snapshot"]) == row["sha256"])
        p = ROOT / row["live"]
        text = p.read_text()
        ck("live control " + row["live"], "pingan-archive-fields-20261013/result.md" in text
           and "accounting-pingan-2019-counterparts-20261013.md" in text and "not_ready" in text)
        if "requirements" not in p.name:
            ck("local links " + row["live"], all((p.parent / t.split("#")[0]).exists()
               for t in re.findall(r"\]\(([^)]+)\)", text) if not t.startswith(("http", "#"))))
        controls[row["live"]] = sha(p)
    failed = [r["name"] for r in checks if not r["passed"]]
    if failed:
        print(json.dumps({"failed": failed}))
        raise SystemExit(1)
    plan = "docs/plans/accounting-pingan-archive-fields-20261013.md"
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob("*") if p.is_file()}
    hashes[plan] = sha(ROOT / plan)
    manifest = {"completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "git_commit": baseline["git_commit"], "plan": plan,
                "result": str((OUT / "result.md").relative_to(ROOT)),
                "environment": {"python": platform.python_version(), "cpu_gpu": "CPU-only; no GPU/framework probes",
                                "random_seeds": "N/A deterministic source inspection"},
                "data_version": "Frozen active panel v2; retained 86-article official archive response",
                "commands": ["python3 data/accounting-master/pingan-archive-fields-20261013/inspect_archive.py",
                             "python3 data/accounting-master/pingan-archive-fields-20261013/check_evidence.py",
                             "python3 data/accounting-master/pingan-archive-fields-20261013/closeout.py"],
                "wall_seconds": {"inspection": load(OUT / "archive-evidence.json")["wall_seconds"],
                                 "source_checks": source["wall_seconds"], "closeout_before_manifest": time.monotonic() - start,
                                 "interactive_reading": "not timed"},
                "source_checks": 123, "closeout_checks": len(checks), "selected_reports": 16,
                "exact_attachment_links": 15, "new_publication_dates": 0, "historical_byte_admissions": 0,
                "artifact_hashes": hashes, "controls_at_closeout": controls, "readiness": "not_ready"}
    save("run-manifest.json", manifest)
    digest = sha(OUT / "run-manifest.json")
    save("closeout-checks.json", {"checks": checks, "passed": len(checks), "failed": [], "manifest_sha256": digest})
    save("completion.json", {"status": "closed_archive_field_and_attachment_inquiry", "source_checks": 123,
                             "closeout_checks": len(checks), "failed": [], "manifest_sha256": digest,
                             "readiness": "not_ready"})
    print(json.dumps({"source_checks": 123, "closeout_checks": len(checks), "failed": []}))


if __name__ == "__main__":
    main()
