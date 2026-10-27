#!/usr/bin/env python3
"""Bounded integrity and anchor checks for the historical ASU 2016-13 reading."""

import hashlib
import json
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
checks = []


def check(name, condition):
    checks.append({"name": name, "pass": bool(condition)})


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(name):
    return json.loads((ROOT / name).read_text())


ledger = read_json("source-ledger.json")
pages = read_json("source-pages.json")
renders = read_json("render-manifest.json")
pdf_path = REPO / pages["pdf"]

check("official PDF exists", pdf_path.is_file())
check("PDF signature", pdf_path.read_bytes()[:4] == b"%PDF")
check("PDF hash", digest(pdf_path) == ledger["source_sha256"] == pages["sha256"])
with fitz.open(pdf_path) as pdf:
    check("291 PDF pages", len(pdf) == 291)
    cover = pdf[0].get_text()
    check("FASB cover", "An Amendment of the FASB Accounting Standards Codification" in cover)
    check("2016-13 edition", "2016-13" in cover)
    check("credit-loss title", "Measurement of Credit Losses" in cover)

check("status is historical", "historical nonauthoritative ASU" in ledger["authority"])
check("current ASC not claimed", "current ASC not verified" in ledger["authority"])
check("44 retained text pages", len(pages["pages"]) == 44)
check("18 retained renders", len(renders["rendered_pages"]) == 18)
for item in pages["pages"]:
    path = REPO / item["text"]
    check(f"text {item['pdf_page']} hash", path.is_file() and digest(path) == item["sha256"])
for item in renders["rendered_pages"]:
    path = REPO / item["image"]
    check(f"render {item['pdf_page']} hash", path.is_file() and digest(path) == item["sha256"])

required = {
    "status", "scope", "exclusions", "measurement", "enhancements",
    "remeasurement", "presentation", "cancellable_example", "guarantee_aspects",
    "guarantee_initial", "guarantee_subsequent", "method_limit",
    "other_guarantees", "original_dates", "rationale_start", "rationale_end",
}
check("all planned paragraph anchors", {x["id"] for x in ledger["entries"]} == required)
for entry in ledger["entries"]:
    path = REPO / entry["text_path"]
    raw = path.read_text()
    span = entry["raw_span"]
    name = entry["id"]
    check(f"{name} exact span", raw[entry["start_offset"]:entry["end_offset"]].strip() == span)
    check(f"{name} span hash", hashlib.sha256(span.encode()).hexdigest() == entry["raw_span_sha256"])
    check(f"{name} page label", entry["printed_page"] == entry["pdf_page"] - 6 if entry["pdf_page"] >= 105 else entry["printed_page"] is None)
    check(f"{name} historical boundary", entry["claim_class"] == "historical_source_reading_only")

by_id = {entry["id"]: entry for entry in ledger["entries"]}
check("status notice says ASU is not authoritative", "An Accounting Standards Update is not" in by_id["status"]["raw_span"])
check("scope includes Topic 815 exception", "Topic 815" in by_id["scope"]["raw_span"])
check("measurement includes cancellation", "unconditionally cancellable" in by_id["measurement"]["raw_span"])
check("measurement includes funding", "likelihood that funding will occur" in by_id["measurement"]["raw_span"])
check("guarantee inception requires both", "both of the following as liabilities" in by_id["guarantee_initial"]["raw_span"])
check("presentation marked as mixed typography", "mixed strikeout and addition" in by_id["presentation"]["text_status"])
check("guarantee aspects marked as mixed typography", "mixed strikeout and addition" in by_id["guarantee_aspects"]["text_status"])
check("original dates not promoted", "historical only" in by_id["original_dates"]["interpretation"])
check("BC97 explanatory", "Explanatory rationale" in by_id["rationale_end"]["interpretation"])

failed = [x["name"] for x in checks if not x["pass"]]
report = {"checks": len(checks), "failed": failed, "results": checks}
(ROOT / "check-run.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"checks": len(checks), "failed": failed}))
raise SystemExit(bool(failed))
