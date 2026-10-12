"""Check filing events, selected contexts and the separately acquired full 10-K."""
import datetime
import hashlib
import json
import re
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((OUT / name).read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    assert not (OUT / "completion.json").exists()
    start = time.monotonic()
    baseline = read("baseline.json")
    raw = read("sec-events.json")
    sources = read("selected-sources.json")
    captures = read("selected-pages.json") + read("acquired-pages.json")
    review = read("visual-review.json")
    checks = []

    def ck(name, value):
        checks.append({"name": name, "passed": bool(value)})

    ck("official SEC response identity", sha(ROOT / baseline["source"]) == baseline["source_sha256"]
       == baseline["receipt"]["sha256"] and baseline["receipt"]["url"] == "https://data.sec.gov/submissions/CIK0000019617.json")
    sec = json.loads((ROOT / baseline["source"]).read_text())
    ck("issuer CIK", sec["cik"] == "0000019617" and sec["name"] == "JPMORGAN CHASE & CO")
    ck("nine actual page reviews", len(captures) == 9 and
       {(r["document_id"], r["pdf_page"], r["render_sha256"]) for r in captures} ==
       {(r["document_id"], r["pdf_page"], r["render_sha256"]) for r in review["pages"] if r["inspected"]})
    texts = {}
    for p in captures:
        key = (p["document_id"], p["pdf_page"])
        ck("capture identity " + str(key), sha(ROOT / p["text"]) == p["text_sha256"]
           and sha(ROOT / p["render"]) == p["render_sha256"])
        texts[key] = " ".join((ROOT / p["text"]).read_text().split())
    expected = {
        "jpmorgan-2025-annual": ("10-K", "2025-12-31", "2026-02-13", "0001628280-26-008131"),
        "jpmorgan-2025-q3": ("10-Q", "2025-09-30", "2025-11-04", "0001628280-25-048859")}
    rows = []
    for event in raw["events"]:
        key = event["document_id"]
        row = event["row"]
        form, report_date, filing_date, accession = expected[key]
        ck("exact SEC row " + key, all(sec["filings"]["recent"][field][event["row_index"]] == value
           for field, value in row.items()))
        ck("form period accession " + key, (row["form"], row["reportDate"], row["filingDate"], row["accessionNumber"])
           == (form, report_date, filing_date, accession))
        ck("unique original " + key, sum(f == form and sec["filings"]["recent"]["reportDate"][i] == report_date
           for i, f in enumerate(sec["filings"]["recent"]["form"])) == 1)
        ck("selected source preserved " + key, sha(ROOT / sources[key]["local_path"]) == sources[key]["sha256"])
        accepted = datetime.datetime.fromisoformat(row["acceptanceDateTime"].replace("Z", "+00:00"))
        eastern = accepted.astimezone(ZoneInfo("America/New_York"))
        ck("acceptance timezone/date interpretation " + key, accepted.utcoffset() == datetime.timedelta(0)
           and eastern.date().isoformat() == filing_date)
        rows.append({"document_id": key, "cik": sec["cik"], "issuer_name": sec["name"],
                     "accession": accession, "form": form, "report_date": report_date,
                     "filing_date": filing_date, "acceptance_timestamp_utc": row["acceptanceDateTime"],
                     "derived_acceptance_America_New_York": eastern.isoformat(),
                     "primary_document": row["primaryDocument"], "source_row_index": event["row_index"],
                     "source": baseline["source"], "source_sha256": baseline["source_sha256"],
                     "selected_pdf": sources[key]["local_path"], "selected_pdf_sha256": sources[key]["sha256"],
                     "selected_pdf_publication": "not established by this filing event",
                     "historical_unchanged_byte_availability": "not independently established"})
    wrapper_note = "The following pages from JPMorgan Chase & Co.’s 2025 Form 10-K are not included herein: 1-42, 328"
    ck("annual wrapper explicitly abridged", wrapper_note in texts[("jpmorgan-2025-annual", 75)])
    ck("wrapper letter separate date", "April 6, 2026" in texts[("jpmorgan-2025-annual", 49)]
       and "Jamie Dimon" in texts[("jpmorgan-2025-annual", 49)])
    ck("Q3 period/form cover", all(s in texts[("jpmorgan-2025-q3", 1)]
       for s in ["FORM 10-Q", "September 30, 2025", "JPMorgan Chase & Co."]))
    ck("Q3 signature date", "November 4, 2025" in texts[("jpmorgan-2025-q3", 207)]
       and "Elena Korablina" in texts[("jpmorgan-2025-q3", 207)])
    lead = read("full-10k-lead.json")
    download = read("acquisition/trusted-curl-result.json")
    ck("new official lead identity", sha(ROOT / lead["source"]) == lead["sha256"]
       and lead["selected_item"]["docs"]["tenkDoc"]["title"] == "2025 10-K")
    pdf = OUT / "acquisition/corp-10k-2025.pdf"
    ck("official PDF retrieval", download["http_code"] == 200 and download["content_type"] == "application/pdf"
       and download["url_effective"] == lead["url"] and pdf.read_bytes().startswith(b"%PDF-")
       and download["size_download"] == pdf.stat().st_size)
    full = fitz.open(pdf)
    ck("full source page count", len(full) == 410)
    ck("full 10K cover identity", all(s in texts[("jpmorgan-2025-full-10k", 1)]
       for s in ["FORM 10-K", "December 31, 2025", "JPMorgan Chase & Co.", "1-5805"]))
    ck("full 10K signature date", "February 13, 2026" in texts[("jpmorgan-2025-full-10k", 330)])
    ck("missing numbered section present", "Item 1. Business." in texts[("jpmorgan-2025-full-10k", 3)]
       and "Signatures" in texts[("jpmorgan-2025-full-10k", 330)])
    ck("proxy incorporation remains explicit", "incorporated by reference" in texts[("jpmorgan-2025-full-10k", 1)])
    comparison = read("shared-pages-comparison.json")
    ck("comparison bound to both files", comparison["full_pdf_sha256"] == sha(pdf)
       and comparison["wrapper_sha256"] == sources["jpmorgan-2025-annual"]["sha256"])
    ck("284 equal shared pages and differing contents", len(comparison["pairs"]) == 285
       and comparison["raw_equal"] == 284
       and [r["printed_page"] for r in comparison["pairs"] if not r["exact_text_equal"]] == [43])
    full_contents = full[44].get_text()
    wrapper_contents = (ROOT / next(p["text"] for p in captures
                           if p["document_id"] == "jpmorgan-2025-annual" and p["pdf_page"] == 75)).read_text()
    insertion = "Note:\nThe following pages from JPMorgan Chase & Co.’s 2025 \nForm 10-K are not included herein: 1-42, 328\n"
    ck("only contents text difference is omission note", wrapper_contents.replace(insertion, "", 1) == full_contents)
    prior_events_path = ROOT / "data/accounting-master/jpmorgan-filing-events-20261011/filing-events.json"
    prior_events = {r["document_id"]: r for r in json.loads(prior_events_path.read_text())}
    for row in rows:
        prior = prior_events[row["document_id"]]["filing_event"]
        ck("previously completed event agrees " + row["document_id"],
           (prior["accessionNumber"], prior["filingDate"], prior["acceptanceDateTime"])
           == (row["accession"], row["filing_date"], row["acceptance_timestamp_utc"]))
    prior_acquisitions_path = ROOT / "data/accounting-master/jpmorgan-complete-filings-20261011/acquisitions.json"
    prior_pdf = next(r for r in json.loads(prior_acquisitions_path.read_text()) if r["year"] == 2025)
    ck("download revalidates already retained PDF", sha(ROOT / prior_pdf["path"]) == prior_pdf["sha256"] == sha(pdf))
    ck("current manuscript already states omission", "1--42 and 328" in
       (ROOT / "docs/design/proposal/manuscript-munich-transition-20261012/chapters/10-validation.tex").read_text())
    inventory = []
    for index, page in enumerate(full):
        text = page.get_text()
        inventory.append({"pdf_page": index + 1, "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                          "characters": len(text), "opening": " ".join(text.split())[:180],
                          "scope": "cover/index" if index < 2 else "numbered main filing" if index < 330 else "appended exhibits; not semantically inventoried"})
    save("acquired-page-inventory.json", {"pdf": str(pdf.relative_to(ROOT)), "pdf_sha256": sha(pdf), "pages": inventory})
    save("filing-evidence.json", {"events": rows, "annual_wrapper_omission_quote": wrapper_note,
        "separate_wrapper_letter_date": "2026-04-06", "full_10k": {"url": lead["url"],
        "pdf": str(pdf.relative_to(ROOT)), "sha256": sha(pdf), "pages": len(full)},
        "prior_completed_evidence": {"events": str(prior_events_path.relative_to(ROOT)),
                                     "full_pdf": prior_pdf["path"], "full_pdf_sha256": prior_pdf["sha256"],
                                     "semantic_supplement": "data/accounting-master/accounting-package-semantic-annotation-20261011/result.md"},
        "new_event_count": 0, "new_source_count": 0,
        "remaining_package_work": ["Extend existing bounded semantic annotations where material queries require it",
                                   "Continue unresolved exhibit/proxy dependencies from existing package ledger",
                                   "Preserve annual wrapper and full filing as separate sources; historical byte availability remains open"],
        "shared_text_comparison": {"pages": 285, "exact_equal": 284, "sole_difference": "contents omission note"},
        "frozen_corpus_changed": False, "historical_byte_admissions": 0})
    failed = [r["name"] for r in checks if not r["passed"]]
    save("source-checks.json", {"checks": checks, "passed": len(checks) - len(failed), "failed": failed,
                                "wall_seconds": time.monotonic() - start})
    print(json.dumps({"passed": len(checks) - len(failed), "failed": failed, "events": len(rows), "acquired_pages": len(full)}))
    raise SystemExit(bool(failed))


if __name__ == "__main__":
    main()
