"""Source-anchor, timing and exact-journal checks for the authored insurance example.

This is a document calculation, not an implementation of an insurance engine.
"""
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import time

from bs4 import BeautifulSoup

START = time.monotonic()
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
checks = []
inputs = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    inputs[str(path.relative_to(ROOT))] = sha(path)
    return json.loads(path.read_text())


def check(name, passed, details=None):
    checks.append({"check": name, "passed": bool(passed), "details": details})


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


extraction = read(OUT / "source-extract.json")
source = ROOT / extraction["source"]
check("raw source hash matches extraction", sha(source) == extraction["source_sha256"])
check("extractor matches recorded bytes", sha(OUT / "extract_sources.py") == extraction["extractor_sha256"])
check("all 120 article headings extracted in sequence", list(extraction["articles"]) == [str(n) for n in range(1, 121)])
html_text = BeautifulSoup(source.read_bytes(), "html.parser").get_text("", strip=True)
check("official title and page date present", all(s in html_text for s in ["企业会计准则第25号", "财会〔2020〕20号", "2022年02月24日"]))

# Exact normalized Chinese passages; the full paragraphs remain in the extraction.
claims = [
    ("recognition", 16, "企业应当在下列时点中的最早时点确认其签发的合同组", "Earliest recognition trigger; not necessarily the premium receipt date", "25–26"),
    ("coverage_definition", 16, "责任期，是指企业向保单持有人提供保险合同服务的期间", "Coverage is the period of service", "53(b)"),
    ("fcf_components", 21, "（二）货币时间价值及金融风险调整；\n（三）非金融风险调整", "Financial and non-financial adjustments are distinct", "32–37"),
    ("expected_cash_flows", 23, "未来现金流量估计值为无偏的概率加权平均值", "Cash-flow input is an unbiased probability-weighted mean", "33(a)"),
    ("discount", 25, "反映货币时间价值、保险合同现金流量特征以及流动性特征", "Rate must fit the cash-flow and liquidity characteristics", "36"),
    ("risk_adjustment", 26, "企业应当单独估计非金融风险调整，不得在未来现金流量和折现率的估计中隐含非金融风险调整", "Estimate the non-financial risk adjustment separately", "33(d), 37"),
    ("claim_expense", 31, "因当期发生赔案及其他相关费用导致已发生赔款负债账面价值的增加额", "Initial incurred-claim liability increase enters service expense under the stated assumptions", "84"),
    ("paa_coverage", 50, "该合同组内各项合同的责任期不超过一年", "Every contract has coverage no longer than one year", "53(b)"),
    ("paa_initial", 53, "初始确认时未到期责任负债账面价值等于已收保费", "Received premium begins LRC before the other stated adjustments", "55(a)"),
    ("premium_service_interval", 54, "提供保险合同服务每一部分服务的时点与相关保费到期日之间的间隔不超过一年", "Financing exception refers to each service portion and the related premium due date", "56"),
    ("onerous", 55, "相关事实和情况表明合同组在责任期内存在亏损时", "Emerging onerous facts require separate assessment", "57–58"),
    ("claims_fcf", 56, "根据与已发生赔案及其他相关费用有关的履约现金流量计量已发生赔款负债", "Incurred claims retain fulfilment-cash-flow measurement", "59(b)"),
    ("claim_interval", 56, "相关履约现金流量预计在赔案发生后一年内支付或收取的", "Short-settlement exception is measured from claim incurrence", "59(b)"),
    ("allocation", 57, "企业应当随时间流逝在责任期内分摊经调整的已收和预计收取的保费", "Time allocation is subject to the following risk-release exception", "B126–B127"),
    ("claim_disclosure", 86, "采用保费分配法的保险合同应分别披露未来现金流量现值和非金融风险调整", "PAA incurred-claim disclosure distinguishes PV and RA", "Not compared in this unit"),
    ("date", 120, "本准则自2023年1月1日起施行", "Text's effective-date clause, not a complete entity adoption schedule", "Not an equivalence claim"),
]
support = []
for key, article, quote, interpretation, comparator in claims:
    passage = extraction["articles"][str(article)]["text"]
    check("Chinese anchor: " + key, quote in passage)
    support.append({"id": key, "source": extraction["source"], "source_sha256": extraction["source_sha256"],
                    "article": article, "quote": quote, "full_normalized_article": passage,
                    "english_interpretation": interpretation, "translation_status": "local author translation",
                    "aasb_comparator": comparator, "evidence_class": "inspected_source_provision"})

aasb = ROOT / "docs/design/research/standards/aasb17.txt"
inputs[str(aasb.relative_to(ROOT))] = sha(aasb)
aasb_text = re.sub(r"\s+", " ", aasb.read_text())
aasb_anchors = {
    "version": "annual periods beginning on or after 1 January 2023 but before 1 July 2026",
    "coverage": "coverage period of each contract in the group",
    "financing": "between providing each part of the services and the related premium due date is no more than a year",
    "claim": "paid or received in one year or less from the date the claims are incurred",
    "risk": "compensation that the entity requires for bearing the uncertainty about the amount and timing",
    "allocation": "if the expected pattern of release of risk during the coverage period differs significantly",
}
for key, quote in aasb_anchors.items():
    check("dated AASB comparator: " + key, quote in aasb_text)

# Timing: claim is first incurred and measured at t=1/2; payment at t=5/2.
timing = {"coverage_start": F(0), "coverage_end": F(1), "premium_due": F(0),
          "premium_received": F(0), "measurement": F(1, 2), "claim_incurred": F(1, 2), "claim_paid": F(5, 2)}
check("coverage meets the one-year route", timing["coverage_end"] - timing["coverage_start"] == 1)
check("all service times are within a year of premium due", 0 <= timing["coverage_start"] - timing["premium_due"] <= timing["coverage_end"] - timing["premium_due"] <= 1)
check("claim fails the one-year settlement exception", timing["claim_paid"] - timing["claim_incurred"] == 2)
check("no intervening claim finance accrual at first measurement", timing["measurement"] == timing["claim_incurred"])

premium, expected_payment, rate, ra = F(120), F(121, 2), F(1, 10), F(5)
pv = expected_payment / (1 + rate)**2
lic = pv + ra
revenue = premium * (timing["measurement"] - timing["coverage_start"]) / (timing["coverage_end"] - timing["coverage_start"])
lrc = premium - revenue
profit = revenue - lic
check("discounted cash flow independently compounds to expected payment", pv == 50 and pv * F(121, 100) == expected_payment)
check("separate RA yields the stated incurred-claim measurement", lic == 55)
check("time allocation gives revenue and remaining coverage", revenue == lrc == 60)

# Debit-positive trial balance; explicit journals checked independently of balance-sheet formulas.
journals = [
    {"event": "premium_received", "debit": {"cash": F(120)}, "credit": {"remaining_coverage": F(120)}},
    {"event": "half_year_service", "debit": {"remaining_coverage": F(60)}, "credit": {"insurance_revenue": F(60)}},
    {"event": "claim_incurred", "debit": {"insurance_service_expense": F(55)}, "credit": {"incurred_claims": F(55)}},
]
trial = defaultdict(F)
for journal in journals:
    check("journal balances: " + journal["event"], sum(journal["debit"].values()) == sum(journal["credit"].values()))
    for account, amount in journal["debit"].items(): trial[account] += amount
    for account, amount in journal["credit"].items(): trial[account] -= amount
check("journal-derived balance sheet reconciles to source-derived amounts", trial["cash"] == 120 and -trial["remaining_coverage"] == lrc and -trial["incurred_claims"] == lic)
check("journal-derived profit equals net assets", -trial["insurance_revenue"] - trial["insurance_service_expense"] == profit == trial["cash"] + trial["remaining_coverage"] + trial["incurred_claims"] == 5)
wrong_lic = expected_payment + ra
check("undiscounted shortcut overstates the two-year liability by 10.5", wrong_lic == F(131, 2) and wrong_lic - lic == F(21, 2))
check("undiscounted shortcut understates result by the same amount", profit - (revenue - wrong_lic) == F(21, 2))
check("omitting RA understates liability by 5", lic - pv == 5)
check("zero-rate limit removes only the discount difference", expected_payment / (1 + F(0))**2 + ra == wrong_lic)

def encode(value):
    if isinstance(value, F): return {"rational": str(value), "decimal": float(value)}
    if isinstance(value, dict): return {k: encode(v) for k, v in value.items()}
    if isinstance(value, list): return [encode(v) for v in value]
    return value

write("insurance-calculation.json", encode({
    "scope": "Authored mid-coverage group example; no actuarial calibration, entity adoption or insurer forecast",
    "timing_years": timing,
    "inputs": {"premium": premium, "expected_claim_payment": expected_payment, "annual_effective_rate": rate, "present_value_risk_adjustment": ra},
    "assumptions": ["Admitted issued-insurance group, one-year coverage", "Uniform risk release", "No earlier onerous recognition", "No acquisition costs, investment components, reinsurance, tax, expenses or other movements", "No onerous remaining coverage indicated", "Claim first incurred at measurement; expected payment exactly two years later", "10% appropriate rate and RA5 are authored inputs; no real market or actuarial evidence"],
    "results": {"claim_cash_flow_pv": pv, "incurred_claims": lic, "remaining_coverage": lrc, "revenue": revenue, "service_expense": lic, "result": profit, "cash": F(120)},
    "journals": journals, "trial_balance_debit_positive": dict(trial),
    "wrong_shortcut": {"liability": wrong_lic, "excess": wrong_lic - lic, "verdict": "wrong relative to the specified discounted-fulfilment-cash-flow target"},
}))
write("source-claim-supplement.json", {"recorded_at": datetime.now(timezone.utc).isoformat(),
    "source_claims": support, "aasb_source": str(aasb.relative_to(ROOT)), "aasb_sha256": sha(aasb),
    "aasb_inspection": "Cover; 25–27, 32–37, 53–59, B126–B127; 84 for service-expense presentation",
    "local_derivation": "source-note.md and insurance-calculation.json; Article 56's discount exception fails for the two-year claim under one-year coverage",
    "unresolved": ["Original issuance/adoption schedule", "2025 implementation notice and subsequent amendments", "Actual entity/contract applicability", "Market-consistent rate and actuarial risk adjustment", "Broader insurance and whole-proposal support"],
    "full_amendment_review": False, "full_standards_equivalence": False, "independent_human_acceptance": "pending"})

report = {"recorded_at": datetime.now(timezone.utc).isoformat(), "checker_sha256": sha(Path(__file__)),
          "inputs": inputs, "source_sha256": sha(source), "checks": checks,
          "passed": sum(c["passed"] for c in checks), "failed": sum(not c["passed"] for c in checks),
          "wall_seconds": time.monotonic() - START,
          "scope": "Exact source anchors, conditions and authored arithmetic; translation and applicability require substantive interpretation; counts are not accuracy or readiness scores"}
write("authority-checks.json", report)
print(json.dumps({k: report[k] for k in ["passed", "failed", "wall_seconds"]}))
if report["failed"]:
    print(json.dumps([c for c in checks if not c["passed"]], ensure_ascii=False))
raise SystemExit(bool(report["failed"]))
