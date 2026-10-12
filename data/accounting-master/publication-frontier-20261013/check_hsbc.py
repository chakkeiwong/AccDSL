"""Verify three report-specific dates against their visually read columns."""
import datetime
import hashlib
import json
import re
import time
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    assert not (OUT / "completion.json").exists()
    start = time.monotonic()
    sources = json.loads((OUT / "selected-sources.json").read_text())
    pages = json.loads((OUT / "hsbc-pages.json").read_text())
    review = json.loads((OUT / "hsbc-visual-review.json").read_text())
    by_page = {(p["document_id"], p["pdf_page"]): p for p in pages}
    checks = []

    def ck(name, value):
        checks.append({"name": name, "passed": bool(value)})

    ck("four actual page reviews", len(pages) == 4 and
       {(p["document_id"], p["pdf_page"], p["render_sha256"]) for p in pages} ==
       {(p["document_id"], p["pdf_page"], p["render_sha256"]) for p in review["pages"] if p["inspected"]})
    for p in pages:
        ck("capture identity " + p["document_id"] + str(p["pdf_page"]),
           sha(ROOT / p["text"]) == p["text_sha256"] and sha(ROOT / p["render"]) == p["render_sha256"])
    groups = {}
    for folder in ["hsbc-older-results-groups-20261012", "hsbc-official-item-dates-20261012"]:
        path = ROOT / "data/accounting-master" / folder / "dated-results-groups.json"
        for record in json.loads(path.read_text())["records"]:
            if record["report_year"] in [2023, 2024, 2025]:
                groups[record["report_year"]] = (record, str(path.relative_to(ROOT)), sha(path))
    rows = []
    for year, number, date_text in [(2023, 313, "21 February 2024"),
                                    (2024, 325, "19 February 2025"),
                                    (2025, 248, "25 February 2026")]:
        key = f"hsbc-{year}-annual"
        source = sources[key]
        capture = by_page[(key, number)]
        ck("selected PDF " + key, sha(ROOT / source["local_path"]) == source["sha256"] == capture["pdf_sha256"])
        page = fitz.open(ROOT / source["local_path"])[number - 1]
        blocks = [b for b in page.get_text("blocks") if "date of publication" in b[4]]
        ck("one matching column block " + key, len(blocks) == 1)
        if len(blocks) != 1:
            continue
        block = blocks[0]
        text = " ".join(block[4].split())
        quote = (f"The procedures have been in place throughout the year and up to {date_text}, "
                 f"the date of publication of the Annual Report and Accounts {year}.")
        ck("exact column quote " + key, quote in text)
        ck("page issuer/year context " + key, "HSBC Holdings plc" in " ".join(page.get_text().split())
           and f"Annual Report and Accounts {year}" in text)
        date = datetime.datetime.strptime(date_text, "%d %B %Y").date().isoformat()
        group, group_path, group_sha = groups[year]
        ck("separate results-group date agrees " + key, group["results_group_date"] == date)
        rows.append({"document_id": key, "report_year": year, "report_class": "annual",
                     "pdf": source["local_path"], "pdf_sha256": source["sha256"],
                     "source_url": source["source_url"], "pdf_page": number, "printed_page": number - 2,
                     "column_bbox": list(block[:4]), "column_text": text,
                     "source_label": f"date of publication of the Annual Report and Accounts {year}",
                     "quote": quote, "declared_date": date, "date_precision": "day",
                     "time_of_day": None, "timezone": None, "publication_channel": "unspecified",
                     "evidence_class": "issuer-declared report publication date in internal-control discussion",
                     "historical_unchanged_byte_availability": "not independently established",
                     "frozen_corpus_date_status": source["source_metadata"]["publication_date_status"],
                     "results_group": {"date": group["results_group_date"], "evidence": group_path,
                                       "sha256": group_sha, "role": "separate corroborating event context; no byte admission"},
                     "text_sha256": capture["text_sha256"], "render_sha256": capture["render_sha256"],
                     "visual_review": "author inspected"})
    excluded = by_page[("hsbc-2023-annual", 40)]
    raw = " ".join((ROOT / excluded["text"]).read_text().split())
    quote = "The results were published on 12 July 2023 by the BoE in its Financial Stability Report"
    ck("excluded date is BoE stress-test result", quote in raw)
    ck("2023 filename distinction preserved", "240226" in sources["hsbc-2023-annual"]["source_url"])
    save("hsbc-date-evidence.json", {"primary": rows,
        "excluded": [{"document_id": "hsbc-2023-annual", "pdf_page": 40, "printed_page": 38,
                      "quote": quote, "reason": "Publication of BoE stress-test results, not this report"}],
        "filename_boundary": "The 2023 report declares 21 February 2024; URL prefix 240226 is retained without treating it as a publication or revision date.",
        "historical_byte_admissions": 0})
    failed = [r["name"] for r in checks if not r["passed"]]
    save("hsbc-checks.json", {"checks": checks, "passed": len(checks) - len(failed), "failed": failed,
                              "wall_seconds": time.monotonic() - start})
    print(json.dumps({"passed": len(checks) - len(failed), "failed": failed, "reports": len(rows)}))
    raise SystemExit(bool(failed))


if __name__ == "__main__":
    main()
