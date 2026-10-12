"""Check source-bound facts, authority links and the limited arithmetic claims."""
import hashlib
import json
import re
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name):
    return json.loads((OUT / name).read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / "completion.json").exists()
    start = time.monotonic()
    checks = []

    def ck(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    for path, digest in load("baseline.json")["input_hashes"].items():
        ck("input " + path, sha(ROOT / path) == digest)
    captures = load("captures.json")
    review = load("visual-review.json")["pages"]
    ck("nine rendered-page reads", len(review) == len(captures) == 9 and all(p["inspected"] for p in review)
       and {(p["pdf_page"], p["render_sha256"]) for p in review} == {(p["pdf_page"], p["render_sha256"]) for p in captures})
    for p in captures:
        ck("captured page " + str(p["pdf_page"]), sha(ROOT / p["text"]) == p["text_sha256"]
           and sha(ROOT / p["render"]) == p["render_sha256"])
    texts = {p["pdf_page"]: (ROOT / p["text"]).read_text() for p in captures}
    normalized = {k: "".join(v.split()) for k, v in texts.items()}
    facts = []

    def fact(key, page, quote, interpretation, **extra):
        ck("source quote " + key, quote in normalized[page])
        facts.append({"id": key, "pdf_page": page, "printed_page": page-2,
                      "normalized_quote": quote, "interpretation": interpretation, **extra})

    fact("listed_entity", 114, "已分别在香港联合交易所和上海证券交易所上市", "Issuer reports domestic and overseas listings")
    fact("adoption", 114, "本集团自2019年1月1日起适用于《企业会计准则第21号－租赁》", "ASBE 21 adopted 2019-01-01")
    fact("comparatives", 114, "本集团未调整2018年度的比较财务报表", "2018 comparatives remain on the previous lease basis")
    fact("opening", 114, "确认了使用权资产人民币18,500百万元以及租赁负债人民币17,667百万元", "Reported opening recognition balances", ROU=18500, liability=17667, date="2019-01-01")
    fact("transition_discount", 114, "该租赁负债以剩余租赁付款额按2019年1月1日的承租人增量借款利率折现的现值计量", "Adoption-date incremental borrowing rate; no numeric rate supplied in this passage")
    fact("commitment_bridge", 114, "与于2019年1月1日确认的租赁负债金额的差额不重大", "Difference to discounted previously disclosed operating-lease commitments is not material; not zero or a numeric tolerance")
    fact("june_ROU", 101, "使用权资产17,390–", "June 2019 carrying balance and unadjusted December comparative dash", value=17390, date="2019-06-30", comparative_raw="–")
    fact("june_liability", 102, "租赁负债17,212–", "June 2019 carrying balance and unadjusted December comparative dash", value=17212, date="2019-06-30", comparative_raw="–")
    fact("undiscounted_basis", 166, "未经折现的合同现金流量及预期现金流量", "Source definition of remaining-maturity analysis")
    fact("maturity_row", 167, "租赁负债–1,5155,88511,048485–18,933", "June 2019 lease-liability row under the undiscounted heading", amounts=[None,1515,5885,11048,485,None], raw_dashes=["immediate","no_term"], total=18933)
    fact("finance_leasing_business", 108, "融资租赁业务借款净增加额6,46413,099", "Borrowing cash flows of the finance-leasing business; not identified lessee rent payments")
    fact("finance_leasing_receivables", 108, "融资租赁业务长期应收款净增加额(27,148)(27,511)", "Finance-leasing receivable cash-flow line; not identified lessee debt settlement")
    fact("qualified_contract_statement", 88, "本报告期内公司无应披露的托管、承包、租赁及其他重大合同事项", "Company's reportable-major-contract qualification; not a group-wide assertion that no leases exist")
    expedients = [
        ("short_remaining_term", "剩余租赁期短于十二个月的经营租赁作为短期租赁处理", "第六十三条", "first simplification", "将于首次执行日后12个月内完成的租赁"),
        ("initial_direct_costs", "首次执行日确认使用权资产时扣除初始直接费用", "第六十三条", "second simplification, second limb", "使用权资产的计量可不包含初始直接费用"),
        ("similar_discount_rates", "对具有相似特征的租赁采用同一折现率", "第六十三条", "second simplification, first limb", "具有相似特征的租赁可采用同一折现率"),
        ("option_information", "可根据首次执行日前选择权的实际行使及其他最新情况确定租赁期", "第六十三条", "third simplification", "首次执行日前选择权的实际行使及其他最新情况"),
        ("onerous_contract_assessment", "作为使用权资产减值测试的替代", "第六十三条", "fourth simplification", "作为使用权资产减值测试的替代")]
    authority = load("authority-excerpts.json")
    articles = {r["article"]: "".join(r["quote"].split()) for r in authority["articles"]}
    mappings = []
    for key, quote, article, clause, authority_quote in expedients:
        ck("issuer election " + key, quote in normalized[115])
        ck("authority correspondence " + key, authority_quote in articles[article])
        mappings.append({"id": key, "issuer_pdf_page": 115, "issuer_normalized_quote": quote,
                         "authority_article": article, "clause": clause, "authority_normalized_quote": authority_quote,
                         "status": "reported election and paragraph correspondence; actual application not audited"})
    ck("notice supports 2019 listed-entity class", "在境内外同时上市的企业" in authority["notice_text"]
       and "自2019年1月1日起施行" in authority["notice_text"])
    ck("transition permits more than one asset measurement", "并根据预付租金进行必要调整" in articles["第六十一条"]
       and "假设自租赁期开始日即采用本准则的账面价值" in articles["第六十一条"])
    ck("cumulative route does not restate comparatives", "不调整可比期间信息" in articles["第六十一条"])
    ck("source uses qualifier on materiality", "差额不重大" in normalized[114])
    ck("no invented issuer contract rate", "2019年1月1日的承租人增量借款利率" in normalized[114])
    calculations = [
        {"id": "opening_displayed_difference", "inputs": [18500,17667], "operation": "subtract", "value": 18500-17667,
         "meaning": "difference between reported opening balances; not identified retained earnings", "expected": 833},
        {"id": "ROU_displayed_net_change", "inputs": [17390,18500], "operation": "subtract", "value": 17390-18500,
         "meaning": "post-adoption net carrying-balance change; not identified depreciation", "expected": -1110},
        {"id": "liability_displayed_net_change", "inputs": [17212,17667], "operation": "subtract", "value": 17212-17667,
         "meaning": "post-adoption net liability change; not identified payments", "expected": -455},
        {"id": "maturity_numeric_cell_sum", "inputs": [1515,5885,11048,485], "operation": "sum", "value": sum([1515,5885,11048,485]),
         "meaning": "numeric maturity cells equal the displayed total; dashes retained without asserting exact underlying zero", "expected": 18933},
        {"id": "within_12_months_numeric_cells", "inputs": [1515,5885], "operation": "sum", "value": 1515+5885,
         "meaning": "sum of the displayed first two dated maturity buckets; no within-bucket timing", "expected": 7400},
        {"id": "different_measurement_displayed_difference", "inputs": [18933,17212], "operation": "subtract", "value": 18933-17212,
         "meaning": "undiscounted-versus-carrying difference; not period interest expense or a solved discount rate", "expected": 1721}]
    for row in calculations:
        ck("arithmetic " + row["id"], row["value"] == row["expected"])
    # These two balanced entry fragments refute inference from arithmetic alone.
    # They are conditional bookkeeping examples, not admitted actual histories.
    fragments = [
        {"assumption": "833 of pre-existing prepaid rent is reclassified", "debits": {"ROU": 18500}, "credits": {"lease_liability": 17667, "prepaid_rent": 833}, "equity_change": 0},
        {"assumption": "no other asset/liability adjustment; residual is an equity credit", "debits": {"ROU": 18500}, "credits": {"lease_liability": 17667, "retained_earnings": 833}, "equity_change": 833}]
    ck("conditional fragments balance with different equity", all(sum(r["debits"].values()) == sum(r["credits"].values()) for r in fragments)
       and fragments[0]["equity_change"] != fragments[1]["equity_change"])
    save("lease-evidence.json", {"source_pdf": "data/accounting-master/pingan-2019-counterparts-20261013/sources/2464938e.pdf",
        "source_sha256": sha(ROOT / "data/accounting-master/pingan-2019-counterparts-20261013/sources/2464938e.pdf"),
        "scope": "Nine inspected report pages; 27 exact-term hit-page dispositions; seventeen authority articles",
        "reported_amount_unit": "RMB million", "precision": "displayed amounts; exact underlying amounts and rounding rule not established",
        "facts": facts, "election_mappings": mappings, "calculations": calculations,
        "conditional_entry_fragments": fragments, "fragment_status": "bookkeeping non-identification examples only; not actual issuer histories or proven ASBE-admissible full histories",
        "unidentified": ["lease-level payment schedules and discount rates", "actual opening reclassifications and equity adjustment",
                         "per-lease ROU transition measurement choice", "complete ROU and liability movement decompositions",
                         "numeric tolerance behind not-material language", "historical public availability"],
        "conflict_status": "No genuine same-context conflict: carrying/undiscounted bases, group/major-contract scopes and lessee/lessor roles differ"})
    failed = [r["name"] for r in checks if not r["passed"]]
    save("source-checks.json", {"checks": checks, "passed": sum(r["passed"] for r in checks), "failed": failed, "wall_seconds": time.monotonic()-start})
    print(json.dumps({"passed": sum(r["passed"] for r in checks), "failed": failed, "source_facts": len(facts), "elections": len(mappings), "calculations": len(calculations)}))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
