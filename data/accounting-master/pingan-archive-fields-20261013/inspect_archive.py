"""Bind selected reports to archive links without inventing publication dates."""
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
CORPUS = ROOT / "data/financial-report-benchmark"
SOURCE = CORPUS / "landing/ping_an/01d7a837150ded4fc90b5de18a77408dfff1b8f13937f083cb6e5e80fb5a671e.json"
FIELDS = ("creDate", "createDate", "updateDate", "publishDate", "timingOn", "timingOff")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def clocks(record):
    return {k: {"present": k in record, "value": record.get(k)} for k in FIELDS}


def absolute_attachment(value):
    return "https:" + value if value.startswith("//") else value


def main():
    assert not (OUT / "baseline.json").exists(), "Do not overwrite a captured unit"
    start = time.monotonic()
    inputs = [SOURCE, CORPUS / "coverage.json", CORPUS / "source-evidence.json",
              CORPUS / "source-access.json", CORPUS / "source-review-dispositions.json",
              ROOT / "scripts/resolve_financial_report_sources.py"]
    controls = []
    for rel in ["docs/plans/accounting-master-checkpoint.md", "docs/plans/accounting-master-current.md",
                "docs/plans/accounting-continuation-requirements-20261007.md", "data/accounting-master/next-plan.md"]:
        dest = OUT / "before" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dest)
        controls.append({"live": rel, "snapshot": str(dest.relative_to(ROOT)), "sha256": sha(dest)})
    baseline = {"started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "input_hashes": {str(p.relative_to(ROOT)): sha(p) for p in inputs}, "controls": controls}
    save("baseline.json", baseline)
    raw = SOURCE.read_text()
    match = re.fullmatch(r"corpus\((.*)\);?\s*", raw, re.S)
    assert match, "Unexpected callback or trailing material"
    archive = json.loads(match[1])
    articles = [r["content"] for r in archive["articleList"]]
    receipts = [r for r in load(CORPUS / "source-access.json")
                if r.get("local_path") == str(SOURCE.relative_to(ROOT))]
    assert len(receipts) == 1 and receipts[0]["sha256"] == sha(SOURCE)
    coverage = [r for r in load(CORPUS / "coverage.json")["rows"] if r["issuer_id"] == "ping_an"]
    evidence = load(CORPUS / "source-evidence.json")["documents"]
    rows = []
    for selected in coverage:
        key = selected["document_id"]
        source = evidence[key]
        metadata = source["source_metadata"]
        matches = [(i, a, att) for i, a in enumerate(articles) for att in a.get("atts", [])
                   if absolute_attachment(att["attPath"]) == source["source_url"]]
        candidates = []
        for i, a in enumerate(articles):
            title = re.fullmatch(r"(20\d{2})年(年度|中期|半年度)报告", a["articleTitle"])
            if title and int(title[1]) == selected["period_year"] and (
                    "annual" if title[2] == "年度" else "interim_h1") == selected["report_class"]:
                candidates.append({"article_index": i, "article": a})
        row = {"document_id": key, "period_year": selected["period_year"],
               "report_class": selected["report_class"], "selected_source_url": source["source_url"],
               "selected_pdf": source["local_path"], "selected_pdf_sha256": source["sha256"],
               "selected_metadata": metadata, "exact_attachment_matches": len(matches),
               "same_period_candidates": candidates, "publication_date": None, "timezone": None,
               "historical_unchanged_byte_availability": "not independently established"}
        if len(matches) == 1:
            i, article, attachment = matches[0]
            row.update({"disposition": "exact_selected_attachment_url",
                        "article_index": i, "article": article, "attachment": attachment,
                        "raw_temporal_fields": clocks(article),
                        "archive_created_at_mapping": "createDate; not creDate"})
        else:
            row.update({"disposition": "selected_mirror_has_no_exact_archive_attachment" if not matches else "ambiguous_attachment",
                        "raw_temporal_fields": None,
                        "reason": "Selected ASBE mirror URL differs from official same-period attachment; retain basis/version distinction."})
        rows.append(row)
    dispositions = load(CORPUS / "source-review-dispositions.json")
    prior = [r for r in dispositions["source_dispositions"] if r["document_id"] == "ping_an-2019-interim_h1"]
    save("archive-evidence.json", {"source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
                                  "receipt": receipts[0], "archive_article_count": len(articles),
                                  "response_temporal_fields": clocks(archive), "records": rows,
                                  "prior_mirror_basis_dispositions": prior,
                                  "interpretation": "Attachment links and raw backend clocks only; field semantics/timezone undocumented",
                                  "wall_seconds": time.monotonic() - start})
    print(json.dumps({"selected_reports": len(rows), "exact_url_matches": sum(r["exact_attachment_matches"] == 1 for r in rows),
                      "unmatched": [r["document_id"] for r in rows if r["exact_attachment_matches"] != 1]}))


if __name__ == "__main__":
    main()
