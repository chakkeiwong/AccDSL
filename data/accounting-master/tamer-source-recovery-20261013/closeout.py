"""Record failed acquisition faithfully; preserve the existing source claims."""
import datetime
import hashlib
import json
import platform
import re
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + "\n")


def main():
    assert not (OUT / "completion.json").exists()
    start = time.monotonic()
    baseline = json.loads((OUT / "baseline.json").read_text())
    checks = []

    def ck(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    for rel, digest in baseline["input_hashes"].items():
        ck("input preserved " + rel, sha(ROOT / rel) == digest)
    recovery = json.loads((ROOT / "data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json").read_text())
    for rel, digest in recovery["protected_hashes"].items():
        ck("frozen evidence " + rel, sha(ROOT / rel) == digest)
    attempts = []
    expected = {"harvard-sandbox": (0,6), "harvard-trusted": (405,22),
                "bitstream-metadata": (401,22), "author-sandbox": (0,6), "author-trusted": (403,22)}
    for stem, statuses in expected.items():
        receipt = json.loads((OUT / "sources" / (stem+"-receipt.json")).read_text())
        ck("observed receipt " + stem, (receipt["http_code"],receipt["exitcode"]) == statuses)
        attempts.append({"attempt": stem, "permission_context": "sandbox" if "sandbox" in stem else "trusted",
             "url": receipt["url"], "http_status": receipt["http_code"], "exit_code": receipt["exitcode"],
             "wall_seconds": receipt["time_total"], "bytes_downloaded": receipt["size_download"],
             "receipt": str((OUT / "sources" / (stem+"-receipt.json")).relative_to(ROOT))})
    ck("explicit repository challenge", "x-amzn-waf-action: captcha" in (OUT / "sources/harvard-trusted-headers.txt").read_text())
    ck("API requires authentication", json.loads((OUT / "sources/bitstream-metadata.json").read_text())["message"] == "Authentication is required")
    ck("author response is denial", "Access Denied" in (OUT / "sources/author-response.bin").read_text())
    ck("three distinct URLs within cap", len({x["url"] for x in attempts}) == 3)
    controls = {}
    for row in baseline["controls"]:
        ck("prior control " + row["live"], sha(ROOT / row["snapshot"]) == row["sha256"])
        p=ROOT / row["live"];t=p.read_text()
        ck("current control " + row["live"], all(x in t for x in ["Version 2.51", "not_ready",
            "tamer-source-recovery-20261013/result.md", "accounting-caiani-source-recovery-20261013.md"]))
        controls[row["live"]]=sha(p)
    failed=[x["name"] for x in checks if not x["passed"]]
    if failed:
        print(json.dumps({"failed":failed}));raise SystemExit(1)
    save("source-status.json", {"source_support": {"id":"tamer2010", "status":"SOURCE_BLOCKED", "full_text":None,
        "technical_sections_inspected":[], "official_code":"not checked; no method adopted"},
        "claim_support":{"technical_claims_allowed":[], "forbidden":"Technical claims from uninspected full text"},
        "citation_venue_metadata":{"source":"docs/design/research/raw/tamer2010-search.json", "date":"inherited 2 October 2026 ledger",
            "citation_count":327, "venue":"Annual Review of Economics", "current_refresh":"not performed",
            "correction_retraction_check":"old index metadata only; no current technical-support admission"},
        "backward_screening":"No paper reference list inspected",
        "forward_screening":"No new citing-work search performed",
        "omissions":{"reason":"three documented access blockers", "risk":"important identification survey remains technically uninspected"},
        "attempts":attempts, "readiness":"not_ready"})
    plan="docs/plans/accounting-tamer-source-recovery-20261013.md"
    paths=[p for p in OUT.rglob("*") if p.is_file() and "__pycache__" not in p.parts]+[ROOT/plan]
    manifest={"completed_at":datetime.datetime.now(datetime.timezone.utc).isoformat(), "git_commit":baseline["git_commit"],
        "plan":plan, "result":str((OUT/"result.md").relative_to(ROOT)),
        "environment":{"python":platform.python_version(), "cpu_gpu":"CPU-only; no framework/GPU calls", "seeds":"N/A deterministic retrieval"},
        "data_version":"Retained institutional landing and discovery metadata; hashes in baseline.json",
        "commands":"Bounded curl GET requests; exact URLs, flags and output paths in acquisition-commands.json",
        "attempts":attempts, "wall_seconds":{"curl_total":sum(x["wall_seconds"] for x in attempts),"closeout":time.monotonic()-start,"interactive_work":"not timed"},
        "artifact_hashes":{str(p.relative_to(ROOT)):sha(p) for p in paths}, "controls_at_closeout":controls,
        "checks":len(checks), "interpretation":"record fidelity and preservation checks; acquisition did not pass", "readiness":"not_ready"}
    save("run-manifest.json",manifest);digest=sha(OUT/"run-manifest.json")
    save("checks.json",{"checks":checks,"passed":len(checks),"failed":[],"manifest_sha256":digest})
    save("completion.json",{"status":"closed_source_blocked","checks":len(checks),"full_text_acquired":False,"manifest_sha256":digest,"readiness":"not_ready"})
    print(json.dumps({"status":"closed_source_blocked","checks":len(checks),"failed":[]}))


if __name__ == "__main__":
    main()
