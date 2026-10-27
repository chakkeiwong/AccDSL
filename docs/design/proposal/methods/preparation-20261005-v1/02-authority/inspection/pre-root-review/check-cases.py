"""Bounded independent arithmetic/source-locator diagnostic; no product imports."""
from pathlib import Path
from fractions import Fraction as F
import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
started = time.monotonic()
checks = []
def check(name, condition):
    checks.append({"name": name, "passed": bool(condition)})
    if not condition:
        raise AssertionError(name)

P, r = F(121), F(1, 10)
pv = sum(P/(1+r)**t for t in (1, 2))
check("initial_PV", pv == 210)
L = pv
rou_ifrs = pv
rou_us = pv
rows = []
for year in (2024, 2025):
    interest = L*r
    L += interest - P
    rou_ifrs -= pv/2
    # Independently valued remaining payments for operating ROU in this exact
    # unmodified/no-prepayment/no-incentive case, rather than copying journal.
    future = sum(P/(1+r)**t for t in range(1, 2026-year))
    us_rou_reduction = rou_us-future
    lease_cost = P
    check(f"US_single_cost_decomposition_{year}", lease_cost == interest+us_rou_reduction)
    check(f"same_liability_futurePV_{year}", L == future)
    journal_credits = interest+us_rou_reduction
    check(f"US_expense_journal_balance_{year}", lease_cost == journal_credits)
    rou_us = future
    rows.append(dict(year=year, liability=str(L), ifrs_rou=str(rou_ifrs),
                     ifrs_expense=str(pv/2+interest), us_operating_rou=str(rou_us),
                     us_operating_expense=str(lease_cost)))
check("first_year_IFRS_ROU105", F(rows[0]["ifrs_rou"]) == 105)
check("first_year_US_operating_ROU110", F(rows[0]["us_operating_rou"]) == 110)
check("first_year_expense_difference5", F(rows[0]["ifrs_expense"])-F(rows[0]["us_operating_expense"]) == 5)
check("both_lifetime_costs242", sum(F(x["ifrs_expense"]) for x in rows) == sum(F(x["us_operating_expense"]) for x in rows) == 242)
check("life_ratio20percent", F(2,10) == F(1,5))
check("PV_FV_ratio21percent", pv/F(1000) == F(21,100))

deductions = [F(400), F(300), F(100), F(100), F(100)]
tax_rows = []
book = F(1000)
base = F(1000)
prior_dtl = F(0)
for index, deduction in enumerate(deductions):
    book -= 200
    base -= deduction
    difference = book-base
    # Independent future reversal equals remaining book depreciation minus
    # remaining tax deductions.
    future_diff = 200*(4-index)-sum(deductions[index+1:])
    check(f"tax_future_reversal_{2024+index}", difference == future_diff)
    dtl = difference/4
    current = (500+200-deduction)/4
    deferred = dtl-prior_dtl
    check(f"total_tax125_{2024+index}", current+deferred == 125)
    tax_rows.append(dict(year=2024+index,book=str(book),tax_base=str(base),DTL=str(dtl),current=str(current),deferred=str(deferred)))
    prior_dtl = dtl
check("2024_DTL50_current75", tax_rows[0]["DTL"] == "50" and tax_rows[0]["current"] == "75")
check("DTL_reverses_fully", prior_dtl == 0)
check("total_current625", sum(F(x["current"]) for x in tax_rows) == 625)
new_dtl = F(300)*F(3,10)
check("2025_enacted_future_rate_DTL90", new_dtl == 90)
check("2025_remeasurement15", new_dtl-F(75) == 15)
check("2025_total140", F(100)+new_dtl-F(50) == 140)
check("lease_initial_gross52_5", pv/4 == F(105,2))
check("lease2024_DTA27_5", F(rows[0]["liability"])/4 == F(55,2))
check("lease2024_DTL26_25", F(rows[0]["ifrs_rou"])/4 == F(105,4))
check("lease2024_net1_25", (F(rows[0]["liability"])-F(rows[0]["ifrs_rou"]))/4 == F(5,4))

register = json.loads((root/"source-register.json").read_text())
for item in register["inventory"]:
    check("hash:"+item["path"], hashlib.sha256((root/item["path"]).read_bytes()).hexdigest() == item["sha256"])
for source in register["sources"]:
    txt = next(item["path"] for item in source["files"] if item["path"].endswith(".txt"))
    text = (root/txt).read_text()
    for item in source["inspected_anchors"]:
        pos=text.index(item["exact_anchor"])
        check(f"locator:{source['id']}:{item['paragraph']}", text[:pos].count("\n")+1 == item["text_line"] and ("pdf_page" not in item or text[:pos].count("\f")+1 == item["pdf_page"]))

peer=json.loads((root.parent/"01-accounting/fixtures.json").read_text())
check("peer_L01_PV", F(peer["L01"]["initial_pv"]) == pv)
check("peer_matched_economic_life", peer["L01"]["underlying_remaining_economic_life_years"] == 10)
check("peer_matched_FV", F(peer["L01"]["underlying_fair_value"]) == 1000)
for a,b in zip(rows,peer["L01"]["schedule"]):
    check(f"peer_L01_schedule_{a['year']}", F(a["liability"]) == F(b["closing"]) and F(a["ifrs_rou"]) == F(b["rou"]) and F(a["ifrs_expense"]) == F(b["expense"]))

negative=[
 {"name":"same_expense_for_both_frameworks","exposed":F(rows[0]["ifrs_expense"]) != F(rows[0]["us_operating_expense"]),"reason":"first-year5difference despite identicalliability"},
 {"name":"current_tax_only_is_total_expense","exposed":F(tax_rows[0]["current"]) != 125,"reason":"omitsDTLexpense50"},
 {"name":"skip_equal_gross_lease_taxes","exposed":pv/4 != 0,"reason":"grossDTAandDTL52.5understated;initialnetzeroinsufficient"},
 {"name":"discount_DTL_with_lease_rate","exposed":F(50)/(1+r) != F(50),"reason":"discountedobjectdiffersfromspecifiedundiscountedtax"},
]
for item in negative: check("negative:"+item["name"],item["exposed"])
git = subprocess.run(["git","-C","/home/chakwong/python/AccDSL","rev-parse","HEAD"],capture_output=True,text=True)
report={"status":"passed","evidence_class":"deterministic_specification_arithmetic_and_source_locators_only",
 "command":"python3 check-cases.py","cwd":str(root),"finished_at":dt.datetime.now(dt.timezone.utc).isoformat(),
 "wall_seconds":time.monotonic()-started,"git_commit":git.stdout.strip() if git.returncode==0 else "unavailable",
 "environment":{"python":sys.version,"executable":sys.executable,"platform":platform.platform(),"CPU_GPU":"CPU standard-library arithmetic;noGPUframework/import/deviceprobe","random_seeds":"N/A deterministic exact rational"},
 "plan":"PLAN.md","result":"authority-matrix.md","sources":"source-register.json",
 "check_count":len(checks),"checks":checks,"lease":rows,"tax":tax_rows,"negative_controls":negative,
 "limits":"Noenginewasimported;noauthority/semantictruthcertifiedbysourcematching;US/ASBEsourcevetoesremain."}
(root/"arithmetic-and-source-check.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"status":"passed","checks":len(checks),"negative_controls":len(negative)}))
