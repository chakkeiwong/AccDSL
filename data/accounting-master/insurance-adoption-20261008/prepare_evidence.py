"""Preserve and check a bounded documentary comparison, not a product engine."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import time

from bs4 import BeautifulSoup
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()
if (OUT / "completion.json").exists():
    raise SystemExit("Closed unit; do not regenerate its bound evidence")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def rel(p):
    return str(p.relative_to(ROOT))


checks = []


def check(name, passed, detail=None):
    checks.append(dict(name=name, passed=bool(passed), detail=detail))


requests = []
for key, url in [
    ("issuance2020", "http://kjs.mof.gov.cn/gongzuodongtai/202012/t20201223_3636695.htm"),
    ("explanation2025", "http://kjs.mof.gov.cn/zhengcejiedu/202506/t20250612_3965540.htm"),
]:
    prefix = OUT / "sources" / key
    transfer = json.loads(prefix.with_suffix(".transfer.json").read_text())
    cmd = ["curl", "--location", "--connect-timeout", "10", "--max-time", "30", "--silent", "--show-error",
           "--dump-header", rel(prefix.with_suffix(".headers")), "--output", rel(prefix.with_suffix(".body")),
           "--write-out", "%{json}", url]
    shell = shlex.join(cmd) + " > " + rel(prefix.with_suffix(".transfer.json")) + " 2> " + rel(prefix.with_suffix(".stderr"))
    requests.append(dict(attempt=key, requested_url=url, command=shell, execution="trusted",
                         exit_code=transfer["exitcode"], http_code=transfer["http_code"],
                         transfer_seconds=transfer["time_total"], effective_url=transfer["url_effective"],
                         transfer_file_mtime=datetime.fromtimestamp(prefix.with_suffix(".transfer.json").stat().st_mtime, timezone.utc).isoformat(),
                         timestamp_basis="Transfer file mtime; approval latency not measured",
                         files={rel(prefix.with_suffix(s)): sha(prefix.with_suffix(s)) for s in [".body", ".headers", ".stderr", ".transfer.json"]},
                         disposition="official explanation inspected" if transfer["http_code"] == 200 else "HTTP failure; curl exit zero does not establish retrieval success"))
check("bounded acquisition", len(requests) <= 5 and len({r["requested_url"] for r in requests}) <= 4)
check("failed notice is not source support", requests[0]["http_code"] == 502)
check("explanation response successful", requests[1]["http_code"] == 200)
save("acquisition-receipts.json", dict(requests=requests, attempts=len(requests), distinct_requested_urls=2,
     prior_failed_routes="2025 notice HTTP and HTTPS remain failed in the prior unit; no unchanged retry",
     exact_related_link="http://kjs.mof.gov.cn/zhengcefabu/202506/t20250612_3965538.htm",
     related_link_disposition="Same previously failed operative route; not retried"))

body = OUT / "sources/explanation2025.body"
soup = BeautifulSoup(body.read_bytes(), "html.parser")
official = soup.select_one(".TRS_Editor") or soup.select_one(".TRS_UEDITOR")
assert official is not None
official_text = official.get_text("\n", strip=True)
(OUT / "sources/explanation2025.txt").write_text(official_text)
check("official title and notice identity", "答记者问" in soup.title.get_text() and "财会〔2025〕12号" in official_text)
sources = {"mof2025qa": dict(path=rel(body), sha256=sha(body), role="official explanation, not operative notice",
           title=soup.title.get_text(), displayed_date="2025-06-12", inspected="All seven question-and-answer sections")}
quotes = []


def anchor(ident, source, locator, quote, claim, text):
    normalized = re.sub(r"\s+", "", text)
    check("exact source anchor " + ident, re.sub(r"\s+", "", quote) in normalized)
    quotes.append(dict(id=ident, source=source, locator=locator, quote=quote,
                       whitespace_policy="Only whitespace removed for matching", claim=claim))


for args in [
    ("Q1", "Q1: background", "规定自2023年1月1日起在境内外同时上市以及在境外上市并采用国际财务报告准则或企业会计准则编制财务报表的企业执行，其他执行企业会计准则的企业自2026年1月1日起执行。", "Official explanation reports original entity-class 2023/2026 schedule; direct issuance notice still unavailable"),
    ("Q2", "Q2: preparation and issuance", "于2025年6月6日正式印发《通知》。", "Stated issuance date differs from explanatory-page date"),
    ("Q3", "Q3: implementation arrangements", "以及在本《通知》施行前根据财会〔2020〕20号已提前执行的企业，应当继续执行新保险合同会计准则", "Existing adopters, including qualifying earlier adopters, continue applying"),
    ("Q4", "Q3: implementation arrangements", "确有困难需暂缓执行的保险公司应当向财政部会计司和金融监管总局机构监管司局提交书面材料说明原因。", "Difficulty requires written explanatory materials to both named authorities; no automatic blanket deferral inferred"),
    ("Q5", "Q5: relationship to standard", "仅适用于非上市企业。对于《通知》中未涉及的交易或事项，非上市企业应当按照新保险合同会计准则进行会计处理。", "Simplification choices limited to unlisted entities; uncovered matters follow the standard"),
    ("Q6", "Q5: transition simplifications", "对首次执行新保险合同会计准则时比较信息的列报、修正追溯调整法下简化衔接处理方法的应用以及过渡日的确定等作出简化规定。", "Explanation identifies transition subjects, not full implementable conditions"),
]:
    anchor(args[0], "mof2025qa", *args[1:], official_text)

coverage = json.loads((ROOT / "data/financial-report-benchmark/coverage.json").read_text())["rows"]
metadata = json.loads((ROOT / "data/financial-report-benchmark/source-evidence.json").read_text())["documents"]
page_text = {}
for year, pages in [(2022, [150, 151, 152, 163, 319, 320]), (2023, [145, 146, 147, 158, 196])]:
    ident = f"ping_an-{year}-annual"
    row = next(r for r in coverage if r["document_id"] == ident)
    p = ROOT / row["local_path"]
    check(f"{year} original PDF hash agrees with accepted corpus", sha(p) == row["sha256"])
    doc = fitz.open(p)
    for n in pages:
        page_text[year, n] = doc[n - 1].get_text()
        (OUT / "sources" / f"pingan-{year}-pdf-{n}.txt").write_text(page_text[year, n])
    sources[ident] = dict(path=rel(p), sha256=sha(p), source_url=row["source_url"], role="issuer disclosure",
                         inspected_pdf_pages=pages, printed_page_offset=-4,
                         selected_source_metadata=metadata[ident]["source_metadata"],
                         revalidated_at=metadata[ident]["attempted_at"],
                         revalidation_is_not_publication_or_first_ingestion=True)
    check(f"{year} publication date explicitly unverified", metadata[ident]["source_metadata"]["publication_date"] is None)
    for n in pages[:3]:
        check(f"{year} statement page {n} economic date", "2022年12月31日" in page_text[year, n])
    basis_page = 163 if year == 2022 else 158
    anchor(f"B{year}", ident, f"Notes II–III, printed p. {basis_page-4}/PDF {basis_page}",
           "本财务报表符合企业会计准则的要求", "ASBE preparation is an inspected issuer statement", page_text[year, basis_page])

anchor("P22", "ping_an-2022-annual", "Note XIV.2, printed p. 315/PDF 319",
       "本集团将从2023年1月1日开始的会计年度起采用新保险合同准则。", "2022 report states planned adoption", page_text[2022, 319])
anchor("P23", "ping_an-2023-annual", "Note IV.34, printed p. 192/PDF 196",
       "本集团于2023年1月1日开始执行新保险合同准则，并已根据新保险合同准则的要求重述了比较期间信息。", "2023 report states actual adoption and restatement", page_text[2023, 196])
anchor("P24", "ping_an-2023-annual", "Note IV.34, printed p. 192/PDF 196",
       "本集团选择采用分类重叠法", "Financial-asset classification overlay also affects comparatives", page_text[2023, 196])
anchor("P25", "ping_an-2023-annual", "Note IV.34, printed p. 192/PDF 196",
       "对于部分保险合同组，由于追溯调整法不切实可行，本集团对过渡日的相应合同组采用了修正追溯调整法或公允价值法进行了衔接处理。", "Some groups use modified retrospective or fair-value transition; not uniform full retrospective treatment", page_text[2023, 196])
anchor("P26", "ping_an-2023-annual", "Note I, printed p. 154/PDF 158",
       "本财务报表业经本公司董事会于2024年3月21日决议批准报出。", "Board authorisation is separately dated; not proof of publication or byte vintage", page_text[2023, 158])


def values(year, page, label, count, skip=0):
    lines = [s.strip() for s in page_text[year, page].splitlines()]
    start = lines.index(label) + 1 + skip
    tokens = lines[start:start + count]
    assert all(re.fullmatch(r"\(?[\d,]+\)?", s) for s in tokens), (label, tokens)
    return [(-1 if s.startswith("(") else 1) * int(s.strip("()").replace(",", "")) for s in tokens]


rows = []
for concept, label, old_page, new_page, skip in [
    ("assets", "资产总计", 150, 145, 0),
    ("liabilities", "负债合计", 151, 146, 0),
    ("parent_equity", "归属于母公司股东权益合计", 152, 147, 0),
    ("noncontrolling_interests", "少数股东权益", 152, 147, 1),
    ("total_equity", "股东权益合计", 152, 147, 0),
]:
    old = values(2022, old_page, label, 2, skip)[0]
    current, restated, opening = values(2023, new_page, label, 3, skip)
    rows.append(dict(concept=concept, original_2022=old, restated_2022=restated,
                     difference=restated-old, current_2023=current,
                     original_locator=f"2022 report printed p. {old_page-4}/PDF {old_page}",
                     restated_locator=f"2023 report printed p. {new_page-4}/PDF {new_page}",
                     assertion_kind="balance columns reported; difference locally derived"))
    if concept in ["assets", "liabilities", "parent_equity"]:
        note_label = {"assets": "总资产", "liabilities": "总负债", "parent_equity": "归属于母公司股东权益"}[concept]
        note = values(2023, 196, note_label, 3)
        check("independent bridge matches " + concept, note == [old, restated-old, restated], note)
r = {v["concept"]: v for v in rows}
for basis in ["original_2022", "restated_2022", "current_2023"]:
    check("accounting identity " + basis, r["assets"][basis] - r["liabilities"][basis] == r["total_equity"][basis])
    check("equity attribution " + basis, r["parent_equity"][basis] + r["noncontrolling_interests"][basis] == r["total_equity"][basis])
check("total change differs from parent-only change", r["total_equity"]["difference"] == 10698 and r["parent_equity"]["difference"] == 10516 and r["noncontrolling_interests"]["difference"] == 182)
same_basis_movement = r["assets"]["current_2023"] - r["assets"]["restated_2022"]
mixed_basis_difference = r["assets"]["current_2023"] - r["assets"]["original_2022"]
check("mixing basis understates reported movement by restatement", same_basis_movement == 573477 and mixed_basis_difference == 446249 and same_basis_movement-mixed_basis_difference == 127228)
records=[]
for row in rows:
    for basis, year in [("original_2022",2022),("restated_2022",2023)]:
        records.append(dict(id=f"pa.{row['concept']}.{basis}", entity="Ping An consolidated group as reported",
          concept=row["concept"], economic_date="2022-12-31", currency="CNY", scale=1000000,
          amount=row[basis], precision="reported RMB millions; no unrounded precision inferred",
          basis_id=f"pingan.asbe.{basis}", disclosure_report=f"ping_an-{year}-annual",
          source_locator=row["original_locator" if year==2022 else "restated_locator"],
          publication_date=None, publication_status="not_verified", byte_vintage="not_verified",
          corpus_revalidated_at=metadata[f"ping_an-{year}-annual"]["attempted_at"]))
queries=[
    dict(query="original source: assets at 2022-12-31 in FY2022 report", result=11137168, record="pa.assets.original_2022"),
    dict(query="restated comparison: assets at 2022-12-31 in FY2023 report", result=11009940, record="pa.assets.restated_2022"),
    dict(query="2023 asset movement using FY2023 comparative basis", result=same_basis_movement, kind="reported-balance movement, not cash flow"),
    dict(query="same-basis movement using FY2023 assets minus FY2022 original assets", result="incompatible_basis", naive_difference=mixed_basis_difference),
    dict(query="investor information available at 2023-12-31 from these retained reports", result="availability_unresolved", reason="Neither selected source has verified publication/byte-vintage; later fiscal label is not an availability date"),
    dict(query="classify 2022 original versus restated values as a same-context conflict", result="not_same_context", reason="Explicit change of accounting basis and disclosure version"),
]
save("source-claim-supplement.json", dict(sources=sources, anchors=quotes,
     operative_notice_status="2020 and 2025 operative notices remain unverified", full_amendment_chain="not_checked"))
save("comparative-history.json", dict(unit="CNY millions", economic_date="2022-12-31", rows=rows, records=records,
     lineage=[dict(from_id=f"pa.{r['concept']}.original_2022", to_id=f"pa.{r['concept']}.restated_2022", relation="comparative_restates", support="Note IV.34") for r in rows],
     query_examples=queries, execution_status="Authored documentary examples checked arithmetically; no runtime execution",
     limits="Not a complete transition reconstruction, cash-flow bridge, forecast, compliance result or genuine same-context conflict"))
inputs={rel(p):sha(p) for p in [body, ROOT/"data/financial-report-benchmark/coverage.json", ROOT/"data/financial-report-benchmark/source-evidence.json"]}
inputs.update({s["path"]:s["sha256"] for s in sources.values()})
save("evidence-checks.json", dict(recorded_at=datetime.now(timezone.utc).isoformat(), checker_sha256=sha(Path(__file__)),
     inputs=inputs, output_hashes={rel(OUT/n):sha(OUT/n) for n in ["source-claim-supplement.json", "comparative-history.json", "acquisition-receipts.json"]},
     checks=checks, passed=sum(c["passed"] for c in checks), failed=sum(not c["passed"] for c in checks),
     wall_seconds=time.monotonic()-START, evidence_class="Deterministic documentary/arithmetic checks; no stochastic inference"))
print(json.dumps(dict(passed=sum(c["passed"] for c in checks), failed=sum(not c["passed"] for c in checks), anchors=len(quotes), rows=len(rows))))
if any(not c["passed"] for c in checks):
    print(json.dumps([c for c in checks if not c["passed"]],ensure_ascii=False))
    raise SystemExit(1)
