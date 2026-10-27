#!/usr/bin/env python3
"""Bind the four callable-note descriptions to retained 10-K PDF pages."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "data/accounting-master/jpmorgan-complete-filings-20261011/sources"
PRIOR = json.loads((ROOT / "data/accounting-master/jpmorgan-instrument-terms-20261011/terms.json").read_text())
META = OUT / "sources/CIK0000019617-submissions-057.json"
LINKS = OUT / "incorporation-links.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks: list[dict] = []


def ck(name: str, condition: bool) -> None:
    checks.append({"check": name, "passed": bool(condition)})


def compact(value: str) -> str:
    return " ".join(value.split()).replace("’", "'").lower()


def span(text: str, anchor: str, after: int = 2) -> dict:
    matches = list(re.finditer(re.escape(anchor), text, re.I))
    if len(matches) != 1:
        raise ValueError(f"anchor {anchor!r}: {len(matches)} matches")
    start = matches[0].start()
    # Only newlines define source line numbers; form-feed is a PDF page marker.
    lines = text.split("\n")
    line = text.count("\n", 0, start) + 1
    last = min(len(lines), line + after)
    quote = "\n".join(lines[line - 1:last]).strip()
    return {
        "anchor": anchor,
        "start_line": line,
        "end_line": last,
        "pdf_page_index": text.count("\f", 0, start) + 1,
        "quote": quote,
        "quote_sha256": hashlib.sha256(quote.encode()).hexdigest(),
    }


rows = []
for year in range(2022, 2026):
    pdf = SOURCE / f"jpmorgan-{year}-10k.pdf"
    txt = SOURCE / f"jpmorgan-{year}-10k.txt"
    text = txt.read_text(encoding="utf-8")
    prior = next(row for row in PRIOR["records"] if row["year"] == year)
    ck(f"{year} PDF and text identity", sha(pdf) == prior["pdf_sha256"] and sha(txt) == prior["text_sha256"])
    balance_matches = list(re.finditer(r"As of December 31, (\d{4}), \$5,000,000 aggregate principal amount of the Callable Notes were outstanding\.", text))
    ck(f"{year} unique callable balance", len(balance_matches) == 1)
    if len(balance_matches) != 1:
        continue
    as_of = int(balance_matches[0].group(1))
    ck(f"{year} exact balance date", as_of == (2024 if year == 2025 else year))
    anchors = {
        "balance": (balance_matches[0].group(0), 1),
        "issued_maturity_coupon": ("We issued the Callable Notes on June 10, 2021", 5),
        "issuer_redemption": ("On June 10, 2031", 5),
        "acceleration_amount": ("In case an event of default with respect to the Callable Notes", 5),
        "listed_market": ("The Callable Notes are listed and admitted to trading on the NYSE", 2),
        "dtc_registration": ("DTC will act as securities depositary for the Callable Notes", 4),
        "reopening": ("The Issuer may, in its sole discretion, “reopen” the Callable Notes", 5),
        "not_bank_deposit": ("The Callable Notes are not bank deposits", 2),
    }
    spans = {key: span(text, anchor, n) for key, (anchor, n) in anchors.items()}
    # Exhibit 4.4 is a two-column exhibit list. Bind the section rather than
    # assuming that extracted text has a linear reading order.
    exhibit = span(text, "Indenture, dated as of February 19, 2016,", 9)
    spans["incorporated_indentures_exhibit"] = exhibit
    ck(f"{year} Exhibit 4.4 references S-3 file", "333-209682" in exhibit["quote"])
    key_quotes = {key: compact(value["quote"]) for key, value in spans.items()}
    ck(f"{year} issue, maturity and coupon", all(term in key_quotes["issued_maturity_coupon"] for term in ("june 10, 2021", "june 10, 2032", "2.60%", "december 10")))
    ck(f"{year} all-or-nothing issuer redemption", all(term in key_quotes["issuer_redemption"] for term in ("in whole but not in part", "principal", "accrued and unpaid interest")))
    ck(f"{year} acceleration amount", all(term in key_quotes["acceleration_amount"] for term in ("$1,000 per $1,000", "accrued and unpaid interest")))
    ck(f"{year} DTC and reopening", "cede & co." in key_quotes["dtc_registration"] and "increase the aggregate principal amount" in key_quotes["reopening"])
    with fitz.open(pdf) as document:
        ck(f"{year} retained PDF page count", len(document) == prior["pdf_pages"])
        for key in ("balance", "issued_maturity_coupon", "issuer_redemption", "acceleration_amount", "listed_market", "dtc_registration", "reopening", "incorporated_indentures_exhibit"):
            value = spans[key]
            page = compact(document[value["pdf_page_index"] - 1].get_text())
            witness = {
                "balance": "5,000,000",
                "issued_maturity_coupon": "june 10, 2021",
                "issuer_redemption": "june 10, 2031",
                "acceleration_amount": "$1,000",
                "listed_market": "jpm/32",
                "dtc_registration": "cede & co.",
                "reopening": "reopen",
                "incorporated_indentures_exhibit": "february 19, 2016",
            }[key]
            ck(f"{year} PDF page witness {key}", witness in page)
    rows.append({
        "filing_year": year,
        "reported_balance_as_of": f"{as_of}-12-31",
        "reported_aggregate_principal_usd": 5_000_000,
        "reported_balance_class": "issuer disclosure of outstanding aggregate principal, not carrying or fair value",
        "source_pdf": str(pdf.relative_to(ROOT)),
        "source_pdf_sha256": sha(pdf),
        "source_text": str(txt.relative_to(ROOT)),
        "source_text_sha256": sha(txt),
        "spans": spans,
    })

metadata = json.loads(META.read_text())
indices = [i for i, (acc, number) in enumerate(zip(metadata["accessionNumber"], metadata["fileNumber"])) if acc == "0000950103-16-011338" and number == "333-209682"]
ck("unique official S-3 event", len(indices) == 1)
event = {key: metadata[key][indices[0]] for key in ("accessionNumber", "filingDate", "acceptanceDateTime", "form", "fileNumber", "primaryDocument", "primaryDocDescription")} if len(indices) == 1 else {}
ck("official S-3 date and form", event.get("filingDate") == "2016-02-24" and event.get("form") == "S-3" and event.get("primaryDocument") == "dp63627_s3.htm")
report = {
    "plan": "docs/plans/accounting-jpmorgan-callable-balance-indentures-20261011.md",
    "rows": rows,
    "official_s3_event": event,
    "official_s3_metadata": {"path": str(META.relative_to(ROOT)), "sha256": sha(META)},
    "incorporation_links": {"path": str(LINKS.relative_to(ROOT)), "sha256": sha(LINKS), "url": "https://www.sec.gov/Archives/edgar/data/19617/000095010316011338/dp63627_ex4a7.htm"},
    "access_status": "SEC Archives document and index routes returned HTTP 403; no original indenture or pricing supplement retained",
    "official_s3_route_status": "Metadata retained; SEC Archives HTML request returned HTTP 403, so the original 2016 indenture body remains uninspected.",
    "access_attempts": [
        {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "bytes": path.stat().st_size,
         "http_status_observed": 403}
        for path in sorted((OUT / "sources").glob("*.html"))
    ],
    "checks": checks,
    "passed": sum(row["passed"] for row in checks),
    "failed": sum(not row["passed"] for row in checks),
}
(OUT / "source-ledger.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"passed": report["passed"], "failed": report["failed"], "balances": [(row["filing_year"], row["reported_balance_as_of"], row["spans"]["balance"]["pdf_page_index"]) for row in rows]}))
if report["failed"]:
    raise SystemExit(1)
