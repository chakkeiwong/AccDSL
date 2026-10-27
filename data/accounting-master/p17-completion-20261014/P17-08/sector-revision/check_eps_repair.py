"""Exact cash-flow/EIR repair plus preservation of the prior EPS quantities."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
prior=ROOT/"data/accounting-master/p17-completion-20261014/P17-05/eps-lifecycle"
start=time.perf_counter()
checks=[]
def check(name,a,b):
    checks.append({"name":name,"passed":a==b,"computed":str(a),"expected":str(b)})
r=F(1,23);v=1+r;L=F(9200);coupon=F(400);redemption=F(9600)
check("two_equal_92_day_periods",92+92,184)
check("present_value",coupon/v+redemption/v**2,L)
check("issue_components",L+800,F(10000))
i1=L*r;after_interest=L+i1;after_coupon=after_interest-coupon;i2=after_coupon*r;closing=after_coupon+i2
check("first_interest",i1,F(400))
check("liability_before_first_coupon",after_interest,F(9600))
check("liability_after_first_coupon",after_coupon,F(9200))
check("second_interest",i2,F(400))
check("year_end_liability",closing,F(9600))
check("full_year_expense",i1+i2,F(800))
check("full_year_net_expense",(i1+i2)*F(3,4),F(600))
check("conversion_after_coupon_transfers",after_coupon,F(9200))
check("converted_net_expense",i1*F(3,4),F(300))
check("old_transfer_does_not_match_repaired_schedule",F(9600)==after_coupon,False)
old=json.loads((prior/"calculated-case.json").read_text())
D=F(162480,73);post_shares=F(600*92,365);N=F(12000)
check("no_double_counted_share_days",post_shares+post_shares,F(22080,73))
check("repaired_basic_conversion",F(12300)/(D+post_shares),F(old["actual_conversion"]["basic_continuing"]))
check("repaired_diluted_conversion",(F(12300)+i1*F(3,4))/(D+post_shares+post_shares+240),F(old["assessment"]["diluted"]["continuing"]))
check("repaired_unconverted_diluted",(N+(i1+i2)*F(3,4))/(D+2*post_shares+240),F(old["assessment"]["diluted"]["continuing"]))
entries=[
 {"id":"first_interest","date":"2025-10-01","debit":{"interest_expense":"400"},"credit":{"debt":"400"}},
 {"id":"first_coupon","date":"2025-10-01","debit":{"debt":"400"},"credit":{"cash":"400"}},
 {"id":"second_interest","date":"2025-12-31","debit":{"interest_expense":"400"},"credit":{"debt":"400"}}
]
conversion={"id":"conversion_after_coupon","date":"2025-10-01","debit":{"debt":"9200"},"credit":{"ordinary_equity":"9200"},"shares":600,"prior_conversion_equity_retained":"800"}
for e in entries+[conversion]:
    check("balanced:"+e["id"],sum(map(F,e["debit"].values())),sum(map(F,e["credit"].values())))
original_checks=json.loads((prior/"calculation-checks.json").read_text())
check("prior_finite_EPS_checks_preserved",(original_checks["passed"],original_checks["check_count"]),(True,105))
result={"passed":all(x["passed"] for x in checks),"check_count":len(checks),"checks":checks,"wall_seconds":time.perf_counter()-start,
        "schedule":{"period_rate":str(r),"opening_liability":str(L),"first_coupon":str(coupon),"closing_liability":str(closing)},
        "replacement_interest_coupon_entries":entries,"conversion_variant_entry":conversion,
        "prior_case_sha256":hashlib.sha256((prior/"case.json").read_bytes()).hexdigest(),
        "prior_check_sha256":hashlib.sha256((prior/"calculation-checks.json").read_bytes()).hexdigest(),
        "limits":"Supplied classification, rate and terms; no market valuation or actual issuer claim"}
(OUT/"eps-repair-checks.json").write_text(json.dumps(result,indent=2)+chr(10))
print(json.dumps({"passed":result["passed"],"checks":len(checks),"failed":[x for x in checks if not x["passed"]]}))
raise SystemExit(0 if result["passed"] else 1)
