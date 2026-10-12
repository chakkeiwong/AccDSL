"""Nominate date statements from the actual active panel, with bounded stdout."""
import collections
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main():
    assert not (OUT / "discovery.json").exists(), "Retain prior discovery results"
    started = time.monotonic()
    source_path = ROOT / "data/financial-report-benchmark/source-evidence.json"
    coverage_path = ROOT / "data/financial-report-benchmark/coverage.json"
    sources = json.loads(source_path.read_text())["documents"]
    coverage = json.loads(coverage_path.read_text())
    panel_path = ROOT / coverage["panel"]
    panel = json.loads(panel_path.read_text())
    active_issuers = {r["issuer_id"] for r in panel["issuers"]}
    active = {}
    for row in coverage["rows"]:
        record = sources[row["document_id"]]
        assert row["issuer_id"] in active_issuers
        for field in ["sha256", "local_path", "extracted_text_path"]:
            assert row[field] == record[field]
        active[row["document_id"]] = record
    assert len(active) == len(coverage["rows"]) == 192
    unverified = {k: r for k, r in active.items()
                  if r["source_metadata"].get("publication_date_status", "").split(";", 1)[0].strip() == "not_verified"}
    assert len(unverified) == 136
    selected = {k: r for k, r in unverified.items() if r["issuer_id"] != "munich_re"}
    assert len(selected) == 120
    controls = []
    for rel in ["docs/plans/accounting-master-checkpoint.md", "docs/plans/accounting-master-current.md",
                "docs/plans/accounting-continuation-requirements-20261007.md", "data/accounting-master/next-plan.md"]:
        dst = OUT / "before" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dst)
        controls.append({"live": rel, "snapshot": str(dst.relative_to(ROOT)), "sha256": sha(dst)})
    save("baseline.json", {"started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                           "input_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [source_path, coverage_path, panel_path]},
                           "controls": controls, "active_reports": 192, "superseded_records_excluded": len(sources) - 192})
    save("selected-sources.json", selected)
    patterns = {
        "explicit_label": r"(?:online\s+)?publication\s+date|date\s+of\s+publication|published\s+on|released\s+on|发行日期|發行日期|发布日期|發佈日期|披露日期|公告日期|刊发日期|刊發日期",
        "release_context": r"(?:report|results|statement).{0,65}(?:published|released)|(?:published|released).{0,65}(?:report|results|statement)|本报告.{0,24}(?:发布|披露|公告)|本報告.{0,24}(?:發佈|披露|公告)",
        "imprint": r"\bimprint\b|\bpublication details\b|出版日期|出版信息|出版資訊",
    }
    compiled = {k: re.compile(v, re.I) for k, v in patterns.items()}
    records = []
    for key, record in sorted(selected.items()):
        pdf = ROOT / record["local_path"]
        text_path = ROOT / record["extracted_text_path"]
        assert sha(pdf) == record["sha256"]
        candidates = []
        for page_num, raw in enumerate(text_path.read_text().split("\f"), 1):
            normalized = " ".join(raw.split())
            matches = []
            for kind, regex in compiled.items():
                for match in regex.finditer(normalized):
                    matches.append({"kind": kind, "match": match.group(),
                                    "context": normalized[max(0, match.start() - 120):match.end() + 160]})
            if matches:
                candidates.append({"pdf_page": page_num, "matches": matches})
        records.append({"document_id": key, "issuer_id": record["issuer_id"],
                        "pdf_sha256": record["sha256"], "text_sha256": sha(text_path),
                        "candidate_pages": candidates,
                        "status": "unreviewed candidates" if candidates else "no hit in declared keyword search; unresolved"})
    save("discovery.json", {"patterns": patterns, "records": records,
                             "scope": "Nomination only; no date admissions", "wall_seconds": time.monotonic() - started})
    summary = []
    for issuer in sorted({r["issuer_id"] for r in records}):
        subset = [r for r in records if r["issuer_id"] == issuer]
        kinds = collections.Counter(m["kind"] for r in subset for p in r["candidate_pages"] for m in p["matches"])
        summary.append({"issuer": issuer, "reports": len(subset),
                        "reports_with_hits": sum(bool(r["candidate_pages"]) for r in subset), "hits": dict(kinds)})
    save("discovery-summary.json", summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
