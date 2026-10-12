"""Validate the archive bindings and the limits on chronological interpretation."""
import datetime
import hashlib
import json
import re
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def main():
    assert not (OUT / "completion.json").exists()
    start = time.monotonic()
    baseline = load(OUT / "baseline.json")
    evidence = load(OUT / "archive-evidence.json")
    raw = (ROOT / evidence["source"]).read_text()
    archive = json.loads(re.fullmatch(r"corpus\((.*)\);?\s*", raw, re.S)[1])
    coverage = {r["document_id"]: r for r in load(ROOT / "data/financial-report-benchmark/coverage.json")["rows"]}
    records = evidence["records"]
    checks = []

    def ck(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    for rel, digest in baseline["input_hashes"].items():
        ck("input identity " + rel, sha(ROOT / rel) == digest)
    receipt = evidence["receipt"]
    ck("retained official receipt", receipt["http_status"] == 200 and receipt["status"] == "ok"
       and receipt["sha256"] == evidence["source_sha256"] == sha(ROOT / evidence["source"])
       and receipt["url"].startswith("https://pa18-info.pingan.com.cn/")
       and receipt["bytes"] == (ROOT / evidence["source"]).stat().st_size)
    ck("86 archive articles retained", len(archive["articleList"]) == evidence["archive_article_count"] == 86)
    ck("sixteen unique active report dispositions", len(records) == 16 and {r["document_id"] for r in records}
       == {k for k, v in coverage.items() if v["issuer_id"] == "ping_an"})
    ck("null response dates", all(archive[k] is None for k in ["createDate", "updateDate", "publishDate"]))
    for row in records:
        key = row["document_id"]
        cov = coverage[key]
        ck("selected PDF identity " + key, sha(ROOT / row["selected_pdf"]) == row["selected_pdf_sha256"] == cov["sha256"]
           and row["selected_source_url"] == cov["source_url"])
        ck("no inferred availability " + key, row["publication_date"] is None and row["timezone"] is None
           and row["historical_unchanged_byte_availability"] == "not independently established")
        if row["exact_attachment_matches"] != 1:
            continue
        article = archive["articleList"][row["article_index"]]["content"]
        meta = row["selected_metadata"]
        ck("raw article identity " + key, row["article"] == article and article["articleId"] == meta["archive_article_id"]
           and article["articleTitle"] == meta["source_title"])
        attachments = [a for a in article["atts"] if a == row["attachment"]]
        att = row["attachment"]
        link = "https:" + att["attPath"] if att["attPath"].startswith("//") else att["attPath"]
        title = re.fullmatch(r"(20\d{2})年(年度|中期|半年度)报告", article["articleTitle"])
        ck("exact report attachment and period " + key, len(attachments) == 1 and link == row["selected_source_url"]
           and att["attType"] == "PDF" and title is not None and int(title[1]) == row["period_year"]
           and ("annual" if title[2] == "年度" else "interim_h1") == row["report_class"])
        ck("metadata maps createDate and updateDate " + key, meta["archive_created_at"] == article["createDate"]
           and meta["archive_updated_at"] == article["updateDate"] and meta["publication_date"] is None)
        clocks = row["raw_temporal_fields"]
        ck("all raw field states preserved " + key, all(v == {"present": k in article, "value": article.get(k)}
           for k, v in clocks.items()) and not clocks["publishDate"]["present"]
           and article["timingOn"] == article["timingOff"] == "")
        parsed = [datetime.datetime.strptime(article[k], "%Y-%m-%d %H:%M:%S") for k in ["createDate", "creDate", "updateDate"]]
        ck("distinct naive clocks " + key, parsed[0] != parsed[1] and all(t.tzinfo is None for t in parsed))
    matched = [r for r in records if r["exact_attachment_matches"] == 1]
    unmatched = [r for r in records if r["exact_attachment_matches"] != 1]
    ck("fifteen exact links and one mirror", len(matched) == 15 and len(unmatched) == 1
       and unmatched[0]["document_id"] == "ping_an-2019-interim_h1")
    mirror = unmatched[0]
    ck("mirror source disposition", mirror["selected_metadata"]["source_kind"] == "public_mirror"
       and "archive_article_id" not in mirror["selected_metadata"] and mirror["raw_temporal_fields"] is None
       and len(mirror["same_period_candidates"]) == 1
       and mirror["same_period_candidates"][0]["article"]["articleId"] == "15317820")
    for item in evidence["prior_mirror_basis_dispositions"]:
        ck("prior version retained " + item["sha256"], sha(ROOT / item["original"]) == item["sha256"])
    ck("both 2019 basis dispositions retained", len(evidence["prior_mirror_basis_dispositions"]) == 2
       and any("IFRS/IAS 34" in r["disposition"] for r in evidence["prior_mirror_basis_dispositions"])
       and any("ASBE" in r["disposition"] and "accepted" in r["disposition"] for r in evidence["prior_mirror_basis_dispositions"]))
    later = next(r["article"] for r in matched if r["document_id"] == "ping_an-2023-interim_h1")
    ck("two-calendar-day update gap retained", later["createDate"] == "2023-09-04 14:13:00"
       and later["creDate"] == "2023-09-04 14:14:50" and later["updateDate"] == "2023-09-06 17:55:49")
    failed = [r["name"] for r in checks if not r["passed"]]
    (OUT / "source-checks.json").write_text(json.dumps({"checks": checks,
        "passed": sum(c["passed"] for c in checks), "failed": failed, "wall_seconds": time.monotonic() - start}, indent=2) + "\n")
    print(json.dumps({"passed": sum(c["passed"] for c in checks), "failed": failed}))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
