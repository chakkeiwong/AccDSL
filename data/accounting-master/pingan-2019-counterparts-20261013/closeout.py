"""Record the finite acquisition result and preserve prior corpus evidence."""
import datetime
import hashlib
import json
import platform
import re
import time
from pathlib import Path

import fitz

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

    ck("29 source checks pass", source["passed"] == 29 and not source["failed"]
       and all(c["passed"] for c in source["checks"]))
    recovery = load(ROOT / "data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json")
    for rel, digest in recovery["protected_hashes"].items():
        ck("protected " + rel, sha(ROOT / rel) == digest)
    controls = {}
    for row in baseline["controls"]:
        ck("prior control " + row["live"], sha(ROOT / row["snapshot"]) == row["sha256"])
        p = ROOT / row["live"]
        text = p.read_text()
        ck("live control " + row["live"], "pingan-2019-counterparts-20261013/result.md" in text
           and "accounting-pingan-lease-transition-20261013.md" in text and "not_ready" in text)
        if "requirements" not in p.name:
            ck("local links " + row["live"], all((p.parent / t.split("#")[0]).exists()
               for t in re.findall(r"\]\(([^)]+)\)", text) if not t.startswith(("http", "#"))))
        controls[row["live"]] = sha(p)
    failed = [r["name"] for r in checks if not r["passed"]]
    if failed:
        print(json.dumps({"failed": failed}))
        raise SystemExit(1)
    plan = "docs/plans/accounting-pingan-2019-counterparts-20261013.md"
    commands = []
    for stem in ["2464938e", "073a50e0"]:
        for context in ["sandbox", "trusted"]:
            receipt = load(OUT / f"sources/{stem}-{context}-receipt.json")
            folder = str(OUT.relative_to(ROOT)) + "/sources/"
            commands.append({"permission_context": context, "argv": ["curl", "--location", "--fail", "--silent", "--show-error",
                "--connect-timeout", "15", "--max-time", "60", "--max-filesize", "31457280", "--dump-header",
                folder + stem + "-" + context + "-headers.txt", "--output", folder + stem + ".pdf", "--write-out", "%{json}", receipt["url"]],
                "stdout": folder + stem + "-" + context + "-receipt.json", "stderr": folder + stem + "-" + context + "-stderr.txt",
                "exit_code": receipt["exitcode"], "wall_seconds": receipt["time_total"]})
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob("*") if p.is_file()}
    hashes[plan] = sha(ROOT / plan)
    manifest = {"completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "git_commit": baseline["git_commit"],
        "plan": plan, "result": str((OUT / "result.md").relative_to(ROOT)),
        "environment": {"python": platform.python_version(), "pymupdf": fitz.VersionBind,
                        "cpu_gpu": "CPU-only; no GPU/framework probes", "random_seeds": "N/A deterministic source inspection"},
        "data_version": "Frozen panel v2 plus two separately retained official 2019 source files",
        "acquisition_commands": commands,
        "local_commands": ["python3 data/accounting-master/pingan-2019-counterparts-20261013/inspect_sources.py",
                           "python3 data/accounting-master/pingan-2019-counterparts-20261013/check_evidence.py",
                           "python3 data/accounting-master/pingan-2019-counterparts-20261013/closeout.py"],
        "wall_seconds": {"inspection_and_comparison": load(OUT / "text-comparisons.json")["wall_seconds"],
                         "source_checks": source["wall_seconds"], "closeout_before_manifest": time.monotonic() - start,
                         "interactive_reading": "not timed"},
        "source_checks": 29, "closeout_checks": len(checks), "new_publication_dates": 0, "historical_byte_admissions": 0,
        "artifact_hashes": hashes, "controls_at_closeout": controls, "readiness": "not_ready"}
    save("run-manifest.json", manifest)
    digest = sha(OUT / "run-manifest.json")
    save("closeout-checks.json", {"checks": checks, "passed": len(checks), "failed": [], "manifest_sha256": digest})
    save("completion.json", {"status": "closed_full_counterpart_and_statement_extract", "source_checks": 29,
                             "closeout_checks": len(checks), "failed": [], "manifest_sha256": digest, "readiness": "not_ready"})
    print(json.dumps({"source_checks": 29, "closeout_checks": len(checks), "failed": []}))


if __name__ == "__main__":
    main()
