#!/usr/bin/env python3
"""Bind four dated 10-K default/remedy summaries; no operative-law inference."""
from __future__ import annotations
import hashlib
import json
import re
import time
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "data/accounting-master/jpmorgan-complete-filings-20261011/sources"
PRIOR = ROOT / "data/accounting-master/jpmorgan-callable-indentures-20261011/source-ledger.json"
PLAN = "docs/plans/accounting-jpmorgan-default-remedy-summaries-20261011.md"
ANCHORS = [
    ("definition", "An “Event of Default”"),
    ("acceleration_waiver", "If an Event of Default occurs"),
    ("guarantor_exclusions", "Events of bankruptcy, insolvency, resolution"),
    ("cross_series_notice", "An Event of Default with respect to one series"),
    ("trustee_direction", "The 2016 Indenture provides that the holders of a majority"),
    ("holder_action", "No holder of any debt security"),
    ("individual_payment_right", "However, the right of any holder of a debt security"),
    ("annual_statement", "The 2016 Indenture requires the Issuer and the Guarantor to file annually"),
    ("trustee_conflict", "The Issuer, the Guarantor and certain of their affiliates"),
    ("modification_consent", "Modification of the 2016 Indenture"),
    ("modification_without_consent", "The 2016 Indenture also permits"),
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def norm(value):
    return " ".join(value.split())

def tight(value):
    return re.sub(r"\s+", "", value).replace("’", "'").replace("“", '"').replace("”", '"')

def span(text, start, end):
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end-1].isspace():
        end -= 1
    quote = text[start:end]
    return {
        "start_char": start, "end_char_exclusive": end,
        "start_line": text.count("\n", 0, start)+1,
        "end_line": text.count("\n", 0, end-1)+1,
        "first_pdf_page": text.count("\f", 0, start)+1,
        "last_pdf_page": text.count("\f", 0, end-1)+1,
        "quote": quote, "quote_sha256": digest(quote),
    }

def main():
    started = time.monotonic()
    prior = json.loads(PRIOR.read_text())
    checks, records = [], []
    def ck(label, condition):
        checks.append({"check":label, "passed":bool(condition)})
    for year in range(2022, 2026):
        pdf = SOURCE / f"jpmorgan-{year}-10k.pdf"
        txt = SOURCE / f"jpmorgan-{year}-10k.txt"
        text = txt.read_text()
        old = next(x for x in prior["rows"] if x["filing_year"] == year)
        ck(f"{year}: frozen source identity", sha(pdf)==old["source_pdf_sha256"] and sha(txt)==old["source_text_sha256"])
        start = text.rfind("Events of Default and Waivers")
        end = text.find("Consolidations, Mergers, Sales and Transfers of Assets", start)
        scope = text.rfind("General Terms of the Series A Notes", 0, start)
        disclaimer = text.rfind("These descriptions are only summaries", scope, start)
        rank = text.find("The debt securities will be", disclaimer, start)
        ck(f"{year}: section boundaries", 0 < scope < disclaimer < rank < start < end)
        positions = [(key,text.find(anchor,start,end)) for key,anchor in ANCHORS]
        missing = [key for key,pos in positions if pos < 0]
        ck(f"{year}: expected clause inventory", missing == (["trustee_conflict"] if year==2022 else []))
        positions = [(key,pos) for key,pos in positions if pos >= 0]
        ck(f"{year}: clause order", [pos for _,pos in positions]==sorted(pos for _,pos in positions))
        spans = {key:span(text,pos,positions[i+1][1] if i+1<len(positions) else end) for i,(key,pos) in enumerate(positions)}
        spans["series_scope"] = span(text,scope,disclaimer)
        spans["summary_boundary"] = span(text,disclaimer,rank)
        full = span(text,start,end)
        with fitz.open(pdf) as doc:
            for key,item in spans.items():
                quote = item["quote"]
                ck(f"{year}/{key}: exact text", text[item["start_char"]:item["end_char_exclusive"]]==quote and digest(quote)==item["quote_sha256"])
                pages = tight(" ".join(doc[i-1].get_text() for i in range(item["first_pdf_page"],item["last_pdf_page"]+1)))
                q = tight(quote)
                ck(f"{year}/{key}: PDF witnesses", q[:80] in pages and q[-80:] in pages)
        n = {key:norm(item["quote"]) for key,item in spans.items()}
        tests = {
            "series scope":("series_scope",["Series A Notes issued by","JPMorgan Chase Financial Company LLC","may apply to the debt securities","including the Callable Notes"]),
            "summary only":("summary_boundary",["only summaries","additional information","qualifies the entire statement"]),
            "timings and issuer default":("definition",["continuance of such default for 30 days","when due","90 days after written notice","at least 25%","Issuer’s bankruptcy"]),
            "guarantee carveouts":("definition",["guarantee ceases to be in full force","directly or indirectly","Title 11","Title II","separately repudiated","supplemental indentures"]),
            "acceleration and waiver":("acceleration_waiver",["occurs and is continuing","not less than 25%","by written notice","automatically","without any declaration","Subject to certain conditions","majority"]),
            "guarantor distinction":("guarantor_exclusions",["other than a payment default","in the absence of any such event occurring with respect to the Issuer","not authorized to exercise any remedy","payment default by the Issuer or the Guarantor"]),
            "notice exceptions":("cross_series_notice",["does not necessarily constitute","within 90 days, unless the default is cured","good faith","may not withhold notice"]),
            "direction and indemnity":("trustee_direction",["each series affected","single class","contrary to law","security or indemnity satisfactory"]),
            "holder remedy constraints":("holder_action",["previously given","60 days","not less than 25%","each affected series","reasonable indemnity","inconsistent with the written request"]),
            "individual payment right":("individual_payment_right",["on or after its due date","without the consent of that holder"]),
            "annual knowledge statement":("annual_statement",["file annually","knowledge of a default","Section 3.05"]),
            "modification consent":("modification_consent",["majority in aggregate principal amount of each outstanding series","Each holder of an affected debt security must consent","final maturity","reduce the principal","currency","method","redemption","institute suit","reduce the percentage","adversely affect","Section 8.02"]),
            "nonconsent amendment limits":("modification_without_consent",["in certain circumstances","merger","replacement of the Trustee","ambiguity","does not materially and adversely affect","certain other purposes","Section 8.01"]),
        }
        for label,(key,needles) in tests.items():
            ck(f"{year}: {label}", all(x in n[key] for x in needles))
        if year>2022:
            ck(f"{year}: conditional trustee conflict", all(x in n["trustee_conflict"] for x in ["may be considered","may be required to resign","successor trustee","requirements for giving the Issuer default notice"]))
        records.append({
            "filing_year":year, "source_pdf":str(pdf.relative_to(ROOT)), "source_pdf_sha256":sha(pdf),
            "source_text":str(txt.relative_to(ROOT)), "source_text_sha256":sha(txt),
            "source_role":"Issuer 10-K summary; original 2016 Indenture and supplements uninspected",
            "full_default_and_modification":full, "normalized_body_sha256":digest(norm(full["quote"])),
            "spans":spans, "missing_trustee_conflict_paragraph":year==2022,
        })
    bodies = {r["filing_year"]:norm(r["full_default_and_modification"]["quote"]) for r in records}
    extra = norm(records[1]["spans"]["trustee_conflict"]["quote"])
    ck("2023–2025 normalized bodies identical", bodies[2023]==bodies[2024]==bodies[2025])
    ck("2022 differs only by later trustee-conflict paragraph", norm(bodies[2023].replace(extra,""))==bodies[2022])
    report = {
        "recorded_at":"2026-10-11", "plan":PLAN,
        "prior_ledger":{"path":str(PRIOR.relative_to(ROOT)),"sha256":sha(PRIOR)},
        "records":records,
        "comparison":{"normalization":"Whitespace only, including newlines and form-feeds; punctuation/case retained",
                      "2023_2025":"identical within bounded default/modification body",
                      "2022_difference":"Later trustee-conflict paragraph absent; remaining body matches after whitespace normalization",
                      "limitation":"Text repetition does not prove operative terms or actual instruments unchanged."},
        "checks":checks, "passed":sum(x["passed"] for x in checks), "failed":sum(not x["passed"] for x in checks),
        "readiness":"not_ready", "independent_review":"pending",
    }
    (OUT/"source-ledger.json").write_text(json.dumps(report,indent=2)+"\n")
    (OUT/"check-run.json").write_text(json.dumps({
        "command":"CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-default-remedies-20261011/build_source_ledger.py",
        "wall_seconds":time.monotonic()-started,"passed":report["passed"],"failed":report["failed"]},indent=2)+"\n")
    print(json.dumps({"passed":report["passed"],"failed":report["failed"],"spans":sum(len(r["spans"]) for r in records),
                      "failed_checks":[x["check"] for x in checks if not x["passed"]]}))
    raise SystemExit(bool(report["failed"]))

if __name__=="__main__":
    main()
