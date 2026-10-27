"""Bounded source anchors and an independent exact loan-measurement oracle.

This is a document diagnostic, not an accounting engine or an actual-bank test.
"""
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


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(label, condition, evidence=None):
    checks.append({"check": label, "passed": bool(condition), "evidence": evidence})


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def cn_number(text):
    digits = dict(zip("一二三四五六七八九", range(1, 10)))
    if "十" in text:
        a, b = text.split("十")
        return (digits[a] if a else 1) * 10 + (digits[b] if b else 0)
    return digits[text]


source = OUT / "sources/asbe22-trusted.body"
soup = BeautifulSoup(source.read_bytes(), "html.parser")
main = soup.select_one(".TRS_Editor") or soup.select_one(".TRS_PreAppend")
paragraphs = [p.get_text("", strip=True) for p in main.find_all("p")]
articles = {}
current = None
for paragraph in paragraphs:
    match = re.match(r"^第([一二三四五六七八九十]+)条", paragraph)
    if match:
        current = cn_number(match[1])
        articles[current] = paragraph
    elif re.match(r"^第[一二三四五六七八九十]+章", paragraph):
        current = None
    elif current is not None:
        articles[current] += "\n" + paragraph

anchors = [
    ("amortised-cost-scope", 17,
     "企业管理该金融资产的业务模式是以收取合同现金流量为目标。",
     "Hold-to-collect is one condition; Article 17 also requires principal-and-interest cash flows."),
    ("allowance-in-amortised-cost", 38,
     "（三）扣除累计计提的损失准备（仅适用于金融资产）。",
     "Financial-asset amortised cost deducts the accumulated loss allowance."),
    ("subsequent-credit-impaired-interest", 39,
     "对于购入或源生的未发生信用减值、但在后续期间成为已发生信用减值的金融资产，企业应当在后续期间，按照该金融资产的摊余成本和实际利率计算确定其利息收入。",
     "Subsequent-period interest on a subsequently credit-impaired asset uses amortised cost and EIR."),
    ("credit-impairment-evidence", 40,
     "当对金融资产预期未来现金流量具有不利影响的一项或多项事件发生时，该金融资产成为已发生信用减值的金融资产。",
     "Credit impairment requires event evidence, distinct from merely assigning an allowance."),
    ("modification-before-allowance", 42,
     "未导致金融资产终止确认，但导致合同现金流量发生变化的，应当重新计算该金融资产的账面余额，并将相关利得或损失计入当期损益。",
     "A non-derecognising cash-flow modification remeasures gross balance; the rest of Article 42 specifies discounting and costs."),
    ("write-off-trigger", 43,
     "企业不再合理预期金融资产合同现金流量能够全部或部分收回的，应当直接减记该金融资产的账面余额。",
     "No reasonable expectation of recovery triggers the relevant gross write-off; do not defer a finding already made."),
    ("cash-shortfall-and-discount", 47,
     "信用损失，是指企业按照原实际利率折现的、根据合同应收的所有合同现金流量与预期收取的所有现金流量之间的差额，即全部现金短缺的现值。",
     "Loss is the PV of all contractual-versus-expected shortfalls, subject to the following POCI exception."),
    ("late-full-payment", 47,
     "即使企业预计可以全额收款但收款时间晚于合同规定的到期期限，也会产生信用损失。",
     "A full nominal recovery can still generate a loss through delay."),
    ("default-event-horizon", 48,
     "未来12个月内预期信用损失，是指因资产负债表日后12个月内（若金融工具的预计存续期少于12个月，则为预计存续期）可能发生的金融工具违约事件而导致的预期信用损失，是整个存续期预期信用损失的一部分。",
     "Twelve months limits the default-event window, not the dates of the ensuing shortfall cash flows."),
    ("sicr-is-risk-change", 52,
     "应当考虑金融工具预计存续期内发生违约风险的变化，而不是预期信用损失金额的变化。",
     "SICR compares default risk; a changed allowance alone does not establish it."),
    ("qualitative-default-definition", 52,
     "并考虑财务限制条款等其他定性指标。",
     "Default definitions also consider qualitative indicators; overdue scheduled cash is not the only possible evidence."),
    ("measurement-information", 58,
     "（一）通过评价一系列可能的结果而确定的无偏概率加权平均金额。",
     "Measurement requires an unbiased probability-weighted amount; the same article also requires time value and supported information."),
    ("impaired-asset-measurement", 59,
     "（五）对于资产负债表日已发生信用减值但并非购买或源生已发生信用减值的金融资产，信用损失应为该金融资产账面余额与按原实际利率折现的估计未来现金流量的现值之间的差额。",
     "For this non-POCI impaired asset, allowance is gross balance less PV of estimated receipts."),
    ("transition-comparatives", 73,
     "涉及前期比较财务报表数据与本准则要求不一致的，无需调整。",
     "Comparative restatement is not automatically required; the rest of Article 73 specifies opening adjustments and optional-restatement conditions."),
    ("stated-commencement", 84,
     "本准则自2018年1月1日起施行。",
     "This is the standard's stated commencement, not a checked entity-group adoption schedule."),
]
check("source has all 84 article headings", set(articles) == set(range(1, 85)))
check("official page identifies 2017 ASBE 22",
      "财会〔2017〕7号" in soup.find("meta", attrs={"name": "ArticleTitle"})["content"])
for ident, article, quote, meaning in anchors:
    check("exact article quote: " + ident, quote in articles[article])
write("source-extract.json", {
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "source_path": str(source.relative_to(ROOT)), "source_sha256": sha(source),
    "official_url": "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170908_2694655.htm",
    "page_publication_metadata": soup.find("meta", attrs={"name": "PubDate"})["content"],
    "extraction": "HTML p text with inline markup removed; paragraph boundaries retained. Original HTML is preserved.",
    "extracted_articles": articles,
    "inspected_for_current_claims": [17, 38, 39, 40, 41, 42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 72, 73, 83, 84],
    "anchors": [{"id": i, "article": a, "quote_zh": q, "interpretation_en": m}
                for i, a, q, m in anchors],
    "limit": "Only selected provisions inspected. No full-standard, current consolidated or entity-specific applicability opinion.",
})

# Derive the claimed allowances from scenario receipts, independently of postings.
rate, payment, recovery = F(1, 10), F(121), F(121, 2)
discount = lambda amount, years: amount / (1 + rate) ** years
loss_given_default = discount(payment - recovery, 2)
opening_ecl = F(1, 10) * loss_given_default
lifetime_ecl = F(2, 10) * loss_given_default
survival_pd = F(1, 10) / F(9, 10)
gross_year_one = discount(payment, 1)
expected_year_one = F(4, 5) * payment + F(1, 5) * recovery
revised_ecl = gross_year_one - discount(expected_year_one, 1)
impaired_net = discount(recovery, 1)
impaired_ecl = gross_year_one - impaired_net
net_interest = impaired_net * rate
gross_accretion = gross_year_one * rate
allowance_unwind = (payment - recovery) - impaired_ecl
check("original EIR reproduces advance", discount(payment, 2) == 100)
check("initial twelve-month and lifetime ECL", (opening_ecl, lifetime_ecl) == (5, 10))
check("survival alone is not the revised forecast", survival_pd == F(1, 9) and survival_pd != F(1, 5))
check("new forecast gives allowance 11 through expected receipts", revised_ecl == 11)
check("one remaining year makes general-method horizons coincide",
      F(1, 5) * discount(payment - recovery, 1) == revised_ecl)
check("impaired allowance and net measurement", (impaired_ecl, impaired_net) == (55, 55))
check("net interest and allowance unwind", (net_interest, allowance_unwind) == (F(11, 2), F(11, 2)))
check("gross accrual splits into income and allowance", gross_accretion == net_interest + allowance_unwind)
# A possible conditional recovery law demonstrates that a mean is not a cap.
conditional_recoveries = [(F(0), F(1, 4)), (recovery, F(1, 2)), (payment, F(1, 4))]
check("forecast mean can allow fuller recovery",
      sum(amount * weight for amount, weight in conditional_recoveries) == recovery
      and any(amount > recovery and weight > 0 for amount, weight in conditional_recoveries))
delayed_loss = discount(payment, 2) - discount(payment, 3)
check("one-year late full receipt has positive loss", delayed_loss == F(100, 11))
check("truncating cash flows to first year wrongly gives zero",
      opening_ecl == 5 and loss_given_default > 0, {"no_cash_due_or_received_in_first_year": True})

# Debit-positive ledger; allowance/liabilities/equity have credit balances.
ledger = {"cash": F(200), "gross_loan": F(0), "allowance": F(0),
          "deposits": F(-180), "opening_equity": F(-20),
          "interest_income": F(0), "impairment_expense": F(0)}
journals, states = [], []


def post(name, entries):
    entries = {key: F(value) for key, value in entries.items()}
    check("journal balances: " + name, sum(entries.values()) == 0)
    for key, value in entries.items():
        ledger[key] += value
    check("trial balance: " + name, sum(ledger.values()) == 0)
    journals.append({"event": name, "debit_positive_amounts": {k: str(v) for k, v in entries.items()}})


def snapshot(name, expected):
    values = [ledger["cash"], ledger["gross_loan"], -ledger["allowance"],
              -ledger["deposits"], -ledger["opening_equity"]
              - ledger["interest_income"] - ledger["impairment_expense"]]
    check("balance sheet and stated amounts: " + name,
          values == list(map(F, expected)) and values[0] + values[1] - values[2] == values[3] + values[4])
    states.append({"moment": name, **dict(zip(["cash", "gross", "allowance", "deposits", "equity"], map(str, values)))})


post("advance", {"gross_loan": 100, "cash": -100})
post("initial ECL", {"impairment_expense": opening_ecl, "allowance": -opening_ecl})
snapshot("initial", [100, 100, 5, 180, 15])
post("first-year gross interest", {"gross_loan": 10, "interest_income": -10})
post("revised forecast", {"impairment_expense": revised_ecl - opening_ecl, "allowance": opening_ecl - revised_ecl})
snapshot("year one", [100, 110, 11, 180, 19])
post("credit-impaired remeasurement", {"impairment_expense": impaired_ecl - revised_ecl, "allowance": revised_ecl - impaired_ecl})
snapshot("credit impaired", [100, 110, 55, 180, -25])
post("subsequent-year accrual", {"gross_loan": gross_accretion, "interest_income": -net_interest, "allowance": -allowance_unwind})
snapshot("maturity", [100, 121, F(121, 2), 180, F(-39, 2)])
post("collection", {"cash": recovery, "gross_loan": -recovery})
post("write-off on separate finding", {"allowance": payment - recovery, "gross_loan": recovery - payment})
snapshot("collection and write-off", [F(321, 2), 0, 0, 180, F(-39, 2)])
check("total P&L equals net cash loss",
      ledger["interest_income"] + ledger["impairment_expense"] == F(100) - recovery == F(79, 2))
write("loan-calculation.json", {
    "assumptions": "Authored fixed-rate, non-POCI, hold-to-collect amortised-cost loan; qualitative default, SICR and impairment findings assumed separately; no fees, FX, collateral, tax or modification. Expected recovery is a mean; write-off finding first arises at maturity on this branch.",
    "conditional_recovery_counterexample_only": [{"receipt": str(a), "weight": str(w)} for a, w in conditional_recoveries],
    "values": {"opening_ecl": str(opening_ecl), "initial_lifetime_ecl": str(lifetime_ecl),
               "survival_pd": str(survival_pd), "revised_ecl": str(revised_ecl),
               "impaired_ecl": str(impaired_ecl), "net_interest": str(net_interest),
               "delayed_full_receipt_loss": str(delayed_loss)},
    "journals": journals, "states": states,
    "not_concluded": "Actual credit judgments, calibration, regulatory capital or current ASBE compliance.",
})
write("authority-checks.json", {
    "recorded_at": datetime.now(timezone.utc).isoformat(), "checker_sha256": sha(Path(__file__)),
    "source_sha256": sha(source), "checks": checks,
    "passed": sum(c["passed"] for c in checks), "failed": sum(not c["passed"] for c in checks),
    "wall_seconds": time.monotonic() - START,
    "scope": "Exact quotations and arithmetic under authored assumptions; no source applicability or actual-bank opinion.",
})
print(json.dumps({"passed": sum(c["passed"] for c in checks), "failed": sum(not c["passed"] for c in checks)}))
raise SystemExit(any(not c["passed"] for c in checks))
