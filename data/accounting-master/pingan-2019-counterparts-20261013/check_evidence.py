"""Check candidate identity, scope and correspondence without admitting dates."""
import hashlib
import json
import time
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((OUT / name).read_text())


def main():
    assert not (OUT / "completion.json").exists()
    start = time.monotonic()
    sources = load("source-inventory.json")
    comparison = load("text-comparisons.json")
    checks = []

    def ck(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    for path, digest in load("baseline.json")["input_hashes"].items():
        ck("baseline " + path, sha(ROOT / path) == digest)
    for kind, row in sources.items():
        ck("source identity " + kind, sha(ROOT / row["pdf"]) == row["sha256"]
           and len(fitz.open(ROOT / row["pdf"])) == row["pdf_pages"])
    for stem, kind in [("2464938e", "full"), ("073a50e0", "extract")]:
        receipt = load(f"sources/{stem}-trusted-receipt.json")
        ck("trusted acquisition " + kind, receipt["exitcode"] == 0 and receipt["http_code"] == 200
           and receipt["content_type"] == "application/pdf" and receipt["url_effective"].startswith("https://www.pingan.com/")
           and receipt["size_download"] == (ROOT / sources[kind]["pdf"]).stat().st_size
           and (ROOT / sources[kind]["pdf"]).read_bytes().startswith(b"%PDF-"))
        sandbox = load(f"sources/{stem}-sandbox-receipt.json")
        ck("sandbox DNS failure distinguished " + kind, sandbox["exitcode"] == 6 and sandbox["http_code"] == 0)
    docs = {k: fitz.open(ROOT / r["pdf"]) for k, r in sources.items()}
    for label, left, right in [("full_vs_mirror", "full", "mirror"), ("extract_vs_full", "extract", "full")]:
        rows = comparison[label]["pairs"]
        valid = []
        for row in rows:
            a = docs[left][row["left_pdf_page"] - 1].get_text()
            b = docs[right][row["right_pdf_page"] - 1].get_text()
            valid.append(a == b and row["exact_text_equal"]
                         and hashlib.sha256(a.encode()).hexdigest() == row["left_text_sha256"]
                         and hashlib.sha256(b.encode()).hexdigest() == row["right_text_sha256"])
        ck("all page text pairs reproduce " + label, all(valid) and len(valid) == (184 if left == "full" else 9))
    ck("empty covers not textual evidence", comparison["full_vs_mirror"]["empty_equal_pairs"] == 2)
    captures = load("captures.json")
    reviewed = load("visual-review.json")["pages"]
    ck("nine inspected renders", len(reviewed) == len(captures) == 9 and all(r["inspected"] for r in reviewed)
       and {(r["source"], r["pdf_page"], r["render_sha256"]) for r in reviewed}
       == {(r["source"], r["pdf_page"], r["render_sha256"]) for r in captures})
    for row in captures:
        ck("capture " + str((row["source"], row["pdf_page"])), sha(ROOT / row["text"]) == row["text_sha256"]
           and sha(ROOT / row["render"]) == row["render_sha256"])
    text = lambda kind, number: "".join(docs[kind][number-1].get_text().split())
    ck("full ASBE preparation basis", all(s in text("full", 114) for s in
       ["中期财务报表编制基础", "《企业会计准则－基本准则》", "《企业会计准则第32号－中期财务报告》",
        "2019年6月30日", "中国平安保险（集团）股份有限公司"]))
    ck("review rather than audit", "审阅报告" in text("full", 100) and "保证程度低于审计" in text("full", 100))
    ck("board authorisation distinguished", "于2019年8月15日批准并授权发布" in text("full", 180))
    ck("wrapper dates its announcement", "海外監管公告" in text("mirror", 1)
       and "2019年8月15日" in text("mirror", 1) and "根據中國會計準則" in text("mirror", 1))
    ck("nine-page candidate is incomplete", len(docs["extract"]) == 9 and
       all("编制基础" not in text("extract", i+1) for i in range(9))
       and "中期合并资产负债表" in text("extract", 1)
       and "后附财务报表附注为财务报表的组成部分" in text("extract", 9))
    decisions = {
        "full": {**sources["full"], "status": "accepted_issuer_hosted_ASBE_counterpart",
                 "relation_to_selected_mirror": "All 184 report pages have identical extracted text; mirror has one extra announcement page",
                 "basis_anchor": "PDF 114 / printed 112", "authorised_for_issue_date": "2019-08-15",
                 "authorisation_anchor": "PDF 180 / printed 178", "publication_date": None},
        "extract": {**sources["extract"], "status": "retained_statement_extract_not_complete_report",
                    "relation_to_full": "PDF 1–9 equals full PDF 101–109 / printed 99–107 in extracted text",
                    "missing": "company statements, preparation note and all financial-statement notes",
                    "publication_date": None},
        "historical_byte_admissions": 0, "publication_declarations_added": 0,
        "limits": "Text-layer correspondence is not byte identity, all-page visual equivalence or historical availability"}
    (OUT / "dispositions.json").write_text(json.dumps(decisions, ensure_ascii=False, indent=2) + "\n")
    failed = [r["name"] for r in checks if not r["passed"]]
    (OUT / "source-checks.json").write_text(json.dumps({"checks": checks, "passed": sum(r["passed"] for r in checks),
        "failed": failed, "wall_seconds": time.monotonic() - start}, indent=2) + "\n")
    print(json.dumps({"passed": sum(r["passed"] for r in checks), "failed": failed}))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
