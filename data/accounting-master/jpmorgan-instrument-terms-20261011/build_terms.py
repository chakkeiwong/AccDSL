#!/usr/bin/env python3
"""Extract bounded, source-bound Series A and guarantee passages."""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "data/accounting-master/jpmorgan-complete-filings-20261011/sources"
EXHIBIT_ROOT = ROOT / "data/accounting-master/jpmorgan-subsidiary-guarantees-20261011/sources"
ACQUISITIONS = ROOT / "data/accounting-master/jpmorgan-complete-filings-20261011/acquisitions.json"
start = time.monotonic()
checks: list[dict] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(text: str) -> str:
    return " ".join(text.replace("’", "'").replace("“", '"').replace("”", '"').split()).lower()


def check(label: str, passed: bool, details=None) -> None:
    row = {"check": label, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    checks.append(row)


MARKERS = {
    "issuer_obligation": "the debt securities will be the issuer's direct, unsecured general obligations",
    "subordination": "the guarantor is a holding company",
    "guarantee_core": "the guarantor will fully and unconditionally guarantee",
    "guarantee_limit": "the guarantor's obligations under the guarantee are unconditional and absolute",
}

FUNDING_MARKER = "the ability of the bank and the ihc to make payments"


def line_span(lines: list[str], marker: str, radius: int = 3) -> dict:
    target = norm(marker)
    for index, line in enumerate(lines):
        if target in norm(line):
            lo = max(0, index - radius)
            hi = min(len(lines), index + radius + 4)
            quote = "\n".join(lines[lo:hi]).strip()
            return {
                "start_line": lo + 1,
                "end_line": hi,
                "quote": quote,
                "quote_sha256": hashlib.sha256(quote.encode()).hexdigest(),
            }
    return {"start_line": None, "end_line": None, "quote": "", "quote_sha256": None}


def pdf_pages(pdf: Path, marker: str) -> list[int]:
    target = norm(marker)
    hits: list[int] = []
    with fitz.open(pdf) as doc:
        for index, page in enumerate(doc):
            if target in norm(page.get_text()):
                hits.append(index + 1)
    return hits


acquisitions = {row["year"]: row for row in json.loads(ACQUISITIONS.read_text(encoding="utf-8"))}
records = []
for year in (2022, 2023, 2024, 2025):
    pdf = SOURCE_ROOT / f"jpmorgan-{year}-10k.pdf"
    text_path = SOURCE_ROOT / f"jpmorgan-{year}-10k.txt"
    text = text_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    expected_pdf_sha = acquisitions[year]["sha256"]
    check(f"{year} PDF exists and retains acquisition hash", pdf.is_file() and sha(pdf) == expected_pdf_sha)
    check(f"{year} extracted text exists", text_path.is_file() and bool(text))
    spans = {}
    pages = {}
    for key, marker in MARKERS.items():
        span = line_span(lines, marker)
        spans[key] = {"marker": marker, **span}
        pages[key] = pdf_pages(pdf, marker)
        check(f"{year} text marker: {key}", span["start_line"] is not None)
        check(f"{year} PDF page marker: {key}", bool(pages[key]), pages[key])
    funding_span = line_span(lines, FUNDING_MARKER)
    funding_pages = pdf_pages(pdf, FUNDING_MARKER)
    spans["funding_dependency"] = {"marker": FUNDING_MARKER, **funding_span}
    pages["funding_dependency"] = funding_pages
    if year == 2022:
        check("2022 funding-dependency wording is not silently imported", funding_span["start_line"] is None and not funding_pages)
    else:
        check(f"{year} funding-dependency wording retained", funding_span["start_line"] is not None and bool(funding_pages), funding_pages)
    exhibit = EXHIBIT_ROOT / f"{year}-ex22.2-reading.txt"
    exhibit_text = exhibit.read_text(encoding="utf-8")
    check(f"{year} Exhibit 22.2 summary retained", "registration statement" in exhibit_text.lower() and "guaranteed" in exhibit_text.lower())
    records.append({
        "year": year,
        "pdf": str(pdf.relative_to(ROOT)),
        "pdf_sha256": sha(pdf),
        "pdf_pages": len(fitz.open(pdf)),
        "text": str(text_path.relative_to(ROOT)),
        "text_sha256": sha(text_path),
        "spans": spans,
        "pdf_page_hits": pages,
        "exhibit_summary": str(exhibit.relative_to(ROOT)),
    })

result = {
    "recorded_at": "2026-10-11",
    "plan": "docs/plans/accounting-jpmorgan-instrument-terms-20261011.md",
    "records": records,
    "checks": checks,
    "passed": sum(row["passed"] for row in checks),
    "failed": sum(not row["passed"] for row in checks),
    "wall_seconds": time.monotonic() - start,
    "scope": "Bounded source transcription and PDF/text identity checks for Series A and guarantee descriptions; no legal enforceability, outstanding-balance, valuation or accounting-recognition claim.",
}
(OUT / "terms.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({key: result[key] for key in ["passed", "failed", "wall_seconds"]}, indent=2))
if result["failed"]:
    raise SystemExit(1)
