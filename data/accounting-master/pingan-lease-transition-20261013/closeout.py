"""Close the verified source/manuscript unit without rewriting prior evidence."""
import datetime
import json
import platform
import re
import subprocess
import time

import fitz

from build_candidate import CAND, OUT, ROOT, sha, save


def load(path):
    return json.loads(path.read_text())


def main():
    assert not (OUT / "completion.json").exists()
    started = time.monotonic()
    baseline = load(OUT / "baseline.json")
    source = load(OUT / "source-checks.json")
    manuscript = load(OUT / "manuscript-checks.json")
    recovery = load(ROOT / "data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json")
    checks = []

    def ck(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    ck("source evidence passes", source["passed"] == 51 and not source["failed"])
    ck("manuscript evidence passes", manuscript["passed"] == 124 and not manuscript["failed"])
    for rel, digest in recovery["protected_hashes"].items():
        ck("protected " + rel, sha(ROOT / rel) == digest)
    controls = {}
    for row in baseline["controls"]:
        ck("prior control " + row["live"], sha(ROOT / row["snapshot"]) == row["sha256"])
        p = ROOT / row["live"]
        text = p.read_text()
        ck("current control " + row["live"], all(x in text for x in [
            "Version 2.51", "193 pages", manuscript["pdf_sha256"], "not_ready",
            "pingan-lease-transition-20261013/result.md", "accounting-tamer-source-recovery-20261013.md"]))
        if "requirements" not in p.name:
            ck("local links " + row["live"], all((p.parent / t.split("#")[0]).exists()
               for t in re.findall(r"\]\(([^)]+)\)", text) if not t.startswith(("http", "#"))))
        controls[row["live"]] = sha(p)
    failed = [x["name"] for x in checks if not x["passed"]]
    if failed:
        print(json.dumps({"failed": failed}))
        raise SystemExit(1)
    paths = [p for p in OUT.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    paths += [p for p in CAND.rglob("*") if p.is_file() and p.suffix in {".tex", ".bib", ".lark", ".pdf"}]
    plan = "docs/plans/accounting-pingan-lease-transition-20261013.md"
    next_plan = "docs/plans/accounting-tamer-source-recovery-20261013.md"
    paths += [ROOT / plan, ROOT / next_plan]
    build = load(OUT / "build-run.json")
    manifest = {"completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": baseline["git_commit"], "plan": plan, "next_plan": next_plan,
        "result": str((OUT / "result.md").relative_to(ROOT)),
        "environment": {"python": platform.python_version(), "pymupdf": fitz.VersionBind,
            "cpu_gpu": "CPU-only; GPU devices intentionally hidden for manuscript build; no framework or GPU probes",
            "random_seeds": "N/A deterministic source and manuscript verification"},
        "data_version": "Official Ping An 2019 interim ASBE PDF and retained ASBE 21; exact hashes in baseline.json",
        "commands": ["python3 data/accounting-master/pingan-lease-transition-20261013/prepare_evidence.py",
                     "python3 data/accounting-master/pingan-lease-transition-20261013/check_evidence.py",
                     "python3 data/accounting-master/pingan-lease-transition-20261013/build_candidate.py",
                     "python3 data/accounting-master/pingan-lease-transition-20261013/check_manuscript.py",
                     "python3 data/accounting-master/pingan-lease-transition-20261013/closeout.py"],
        "final_build": build, "layout_history": ["first-layout", "second-layout"],
        "wall_seconds": {"final_build": build["wall_seconds"], "source_checks": source["wall_seconds"],
            "manuscript_checks": manuscript["wall_seconds"], "closeout": time.monotonic()-started,
            "interactive_reading_and_editing": "not timed"},
        "source_checks": 51, "manuscript_checks": 124, "closeout_checks": len(checks),
        "artifact_hashes": {str(p.relative_to(ROOT)): sha(p) for p in paths},
        "controls_at_closeout": controls, "pdf_sha256": manuscript["pdf_sha256"],
        "readiness": "not_ready", "human_acceptance": "pending"}
    save("run-manifest.json", manifest)
    digest = sha(OUT / "run-manifest.json")
    save("closeout-checks.json", {"checks": checks, "passed": len(checks), "failed": [], "manifest_sha256": digest})
    save("completion.json", {"status": "closed_source_case_and_v251_integration", "source_checks": 51,
         "manuscript_checks": 124, "closeout_checks": len(checks), "manifest_sha256": digest,
         "readiness": "not_ready", "failed": []})
    print(json.dumps({"source_checks": 51, "manuscript_checks": 124, "closeout_checks": len(checks), "failed": []}))


if __name__ == "__main__":
    main()
