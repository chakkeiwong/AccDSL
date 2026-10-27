"""Exact finite EPS specification checks; not a production calculation engine."""
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
START = time.perf_counter()
CASE = json.loads((OUT/"case.json").read_text())
CHECKS = []
def check(name, ok, detail=None):
    CHECKS.append({"name":name, "passed":bool(ok), "detail":detail})
def eq(name, a, b):
    check(name, a == b, {"computed":str(a), "expected":str(b)})
def days(start, end):
    return (date.fromisoformat(end)-date.fromisoformat(start)).days
def save(name, obj):
    (OUT/name).write_text(json.dumps(obj, indent=2, default=str)+chr(10))
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

period = CASE["period"]
T = days(period["start"], period["end_exclusive"])
eq("reporting_days",T,365)
intervals = CASE["ordinary"]["intervals"]
for i, r in enumerate(intervals):
    eq("interval_days:"+str(i),days(r["start"],r["end"]),r["expected_days"])
    eq("interval_continuity:"+str(i),r["start"],period["start"] if i==0 else intervals[i-1]["end"])
eq("interval_final_endpoint",intervals[-1]["end"],period["end_exclusive"])
eq("interval_total_days",sum(days(r["start"],r["end"]) for r in intervals),T)
share_days = sum(r["actual_outstanding"]*r["split_factor"]*days(r["start"],r["end"]) for r in intervals)
D = F(share_days,T)
eq("share_days",F(share_days),F(CASE["expected"]["ordinary_share_days"]))
eq("basic_denominator",D,F(CASE["expected"]["basic_denominator"]))

# Independent daily replay from events, without using the authored intervals.
issued = CASE["ordinary"]["opening_issued"]
treasury = CASE["ordinary"]["opening_treasury"]
total_daily = 0
day = date.fromisoformat(period["start"])
end = date.fromisoformat(period["end_exclusive"])
events = CASE["ordinary"]["events"]
register = []
while day < end:
    for event in events:
        if event["date"] == day.isoformat():
            if event["type"] == "cash_issue":
                eq("issue_receivable_date",event["date"],event["consideration_receivable"])
                issued += event["shares"]
            elif event["type"] == "split":
                issued *= event["factor"]
                treasury *= event["factor"]
                eq("split_no_new_resources",F(event["monetary_change"]),F(0))
            elif event["type"] == "treasury_purchase":
                treasury += event["shares"]
            register.append({"date":str(day),"issued":issued,"treasury":treasury,"outstanding":issued-treasury})
    factor = 1
    for event in events:
        if event["type"]=="split" and day < date.fromisoformat(event["date"]):
            factor *= event["factor"]
    total_daily += (issued-treasury)*factor
    day += timedelta(days=1)
eq("independent_daily_shares",F(total_daily,T),D)
for name, value in [("issued",issued),("treasury",treasury),("outstanding",issued-treasury)]:
    eq("closing_"+name,value,CASE["expected"]["closing_"+name])
check("closing_count_shortcut_is_wrong",D != issued-treasury)
unadjusted = F(sum(r["actual_outstanding"]*days(r["start"],r["end"]) for r in intervals),T)
check("missing_split_shortcut_is_wrong",unadjusted != D)

a = CASE["attribution"]
N = F(a["consolidated_continuing_profit"])-F(a["nci_continuing"])-F(a["current_cumulative_equity_preference"])
Ntotal = F(a["consolidated_total_profit"])-F(a["nci_total"])-F(a["current_cumulative_equity_preference"])
Ndisc = Ntotal-N
for name, val in [("basic_continuing_numerator",N),("basic_total_numerator",Ntotal),
                  ("basic_continuing",N/D),("basic_total",Ntotal/D),("basic_discontinued",Ndisc/D)]:
    eq(name,val,F(CASE["expected"][name]))
eq("attribution_reconstruction_continuing",N+F(a["current_cumulative_equity_preference"])+F(a["nci_continuing"]),F(a["consolidated_continuing_profit"]))
eq("attribution_reconstruction_total",Ntotal+F(a["current_cumulative_equity_preference"])+F(a["nci_total"]),F(a["consolidated_total_profit"]))
check("cumulative_entitlement_even_undeclared",a["declared_current"] is False and N==12000)
check("arrears_not_deducted_again",not a["prior_arrears_in_current_deduction"] and (N-F(a["prior_arrears_paid"]))/D != N/D)

o = CASE["options"]
def option_increment(count, exercise, price, service=F(0), weight=F(1)):
    adjusted = F(exercise)+F(service)/count
    return max(F(0), F(count)*(F(1)-adjusted/F(price)))*weight
eq("option_split_count",o["count"],2*o["presplit_count"])
eq("option_split_price",F(o["presplit_exercise"]),2*F(o["exercise"]))
eq("exercise_proceeds_split_invariant",o["count"]*F(o["exercise"]),o["presplit_count"]*F(o["presplit_exercise"]))
O = option_increment(o["count"],o["exercise"],o["average_market_price"])
eq("option_increment",O,F(CASE["expected"]["option_increment"]))
eq("option_fairly_priced_proceeds_shares",F(o["count"])*F(o["exercise"])/F(o["average_market_price"]),F(160))

debt, pref = CASE["convertibles"]
W = F(days(debt["issue"],debt["end_exclusive"]),T)
B = F(debt["shares"])*W
A = F(debt["expense"])-F(debt["tax_benefit"])+F(debt["other_addback"])
eq("debt_days",days(debt["issue"],debt["end_exclusive"]),184)
eq("debt_increment",B,F(CASE["expected"]["debt_increment"]))
eq("debt_addback",A,F(CASE["expected"]["debt_addback"]))
check("unweighted_debt_shortcut_wrong",B != debt["shares"])
eq("debt_component_sum",F(debt["opening_liability"])+F(debt["conversion_equity"]),F(debt["proceeds"]))
series = [("options",F(0),O),("debt",A,B),("preference",F(pref["current_equity_dividend"]),F(pref["shares"]))]
def sequential(numerator, denominator, instruments):
    n,d = numerator,denominator
    trace=[]
    for name,a,b in sorted(instruments,key=lambda item:item[1]/item[2]):
        ratio=(n+a)/(d+b)
        admit=ratio < n/d
        trace.append({"id":name,"incremental_earnings":a,"incremental_shares":b,
                      "earnings_per_increment":a/b,"before":n/d,"after_if_admitted":ratio,"included":admit})
        if admit:
            n+=a; d+=b
    return n,d,trace
n,d,trace=sequential(N,D,series)
eq("order",[r["id"] for r in trace],["options","debt","preference"])
eq("included",[r["id"] for r in trace if r["included"]],CASE["expected"]["included"])
eq("excluded",[r["id"] for r in trace if not r["included"]],CASE["expected"]["excluded"])
check("preference_individually_dilutive",(N+2000)/(D+400) < N/D)
check("preference_after_debt_antidilutive",(n+2000)/(d+400) > n/d)
for name,value in [("diluted_denominator",d),("diluted_continuing_numerator",n),
                   ("diluted_total_numerator",Ntotal+n-N),("diluted_continuing",n/d),
                   ("diluted_total",(Ntotal+n-N)/d),("diluted_discontinued",Ndisc/d)]:
    eq(name,value,F(CASE["expected"][name]))
eq("diluted_component_reconciliation",n/d+Ndisc/d,(Ntotal+n-N)/d)
# Independently enumerate subsets; no reliance on the sequential admission decisions.
from itertools import combinations
subsets=[]
for k in range(4):
    for subset in combinations(series,k):
        value=(N+sum((x[1] for x in subset),F(0)))/(D+sum((x[2] for x in subset),F(0)))
        subsets.append({"ids":[x[0] for x in subset],"value":value})
eq("independent_subset_minimum",min(r["value"] for r in subsets),n/d)
eq("independent_unique_minimum",[r["ids"] for r in subsets if r["value"]==n/d],[["options","debt"]])

conversion_day="2025-10-01"
actual_weight=F(days(conversion_day,period["end_exclusive"]),T)
pre_weight=F(days(debt["issue"],conversion_day),T)
actual_D=D+600*actual_weight
actual_N=N+300
cn,cd,ct=sequential(actual_N,actual_D,[("options",F(0),O),("debt",F(300),600*pre_weight),series[-1]])
eq("conversion_no_double_count",actual_weight+pre_weight,W)
eq("actual_conversion_same_fully_diluted_denominator",cd,d)
eq("actual_conversion_same_fully_diluted_continuing_numerator",cn,n)
eq("actual_conversion_same_fully_diluted_total",F(Ntotal+300)+cn-actual_N,F(Ntotal)+n-N)
eq("actual_conversion_liability_transfer",F(9200)+F(400),F(9600))
eq("actual_conversion_closing_outstanding",issued-treasury+600,2700)
check("actual_conversion_changes_basic",actual_N/actual_D!=N/D)
L=option_increment(400,2,5,weight=F(days(period["start"],conversion_day),T))
eq("option_lapse_days",days(period["start"],conversion_day),273)
eq("option_lapse_increment",L,F(13104,73))
eq("option_lapse_daily_comparator",L,F(sum(240 for j in range(T) if date(2025,1,1)+timedelta(days=j)<date(2025,10,1)),T))

ln,ld,lt=sequential(F(-5000),D,series)
eq("continuing_loss_keeps_basic_denominator",ld,D)
eq("continuing_loss_keeps_basic_numerator",ln,F(-5000))
check("continuing_loss_excludes_all",not any(r["included"] for r in lt))
check("total_profit_would_wrongly_admit",any(r["included"] for r in sequential(F(15000),D,series)[2]))
total_loss=F(-9000)+n-N
eq("positive_control_total_loss_numerator",total_loss,F(-8400))
check("positive_control_total_loss_less_negative_allowed",total_loss/d > F(-9000)/D)
eq("option_at_market",option_increment(400,5,5),F(0))
eq("option_out_of_money",option_increment(400,6,5),F(0))
en,ed,et=sequential(N,D,[("equal",N/D*100,F(100))])
check("equality_not_dilutive",not et[0]["included"] and en==N and ed==D)
eq("future_service_assumed_price",F(2)+F(400)/400,F(3))
eq("future_service_option_increment",option_increment(400,2,5,service=F(400)),F(160))
prior=CASE["prior_period"]
eq("prior_basic_before_split",F(prior["ordinary_profit"])/prior["constant_shares_before_split"],F(6))
eq("prior_basic_after_split",F(prior["ordinary_profit"])/(2*prior["constant_shares_before_split"]),F(3))
eq("postperiod_split_before_authorization_halves_EPS",N/(2*D),(N/D)/2)
eq("postperiod_cash_issue_has_zero_current_days",days("2026-01-01","2026-01-01"),0)

# Monetary movements are a financing slice; consolidated profit is a separate supplied input.
journals=[
 {"id":"cash_issue","date":"2025-04-01","debits":{"cash":"2400"},"credits":{"ordinary_equity":"2400"}},
 {"id":"debt_issue","date":"2025-07-01","debits":{"cash":"10000"},"credits":{"debt":"9200","conversion_equity":"800"}},
 {"id":"treasury_purchase","date":"2025-10-01","debits":{"treasury_equity":"2100"},"credits":{"cash":"2100"}},
 {"id":"debt_interest","date":"2025-12-31","debits":{"interest_expense":"800"},"credits":{"debt":"800"}},
 {"id":"debt_tax_effect","date":"2025-12-31","debits":{"tax_asset":"200"},"credits":{"tax_income":"200"}}
]
for j in journals:
    eq("balanced_journal:"+j["id"],sum(map(F,j["debits"].values())),sum(map(F,j["credits"].values())))
book={"head":"synthetic-consolidated-head","journals":journals,"ordinary_register":register,"potential_terms":deepcopy([o,debt,pref])}
before=json.dumps(book,sort_keys=True)
assessment={"identity":CASE["identity"],"period":period,"basic":{"continuing":N/D,"total":Ntotal/D,"discontinued":Ndisc/D},
            "diluted":{"continuing":n/d,"total":(Ntotal+n-N)/d,"discontinued":Ndisc/d},"trace":trace,
            "mutations":[],"status":"conditional","excluded_instruments":["preference"],"source":"IAS33 historical text"}
eq("assessment_book_unchanged",json.dumps(book,sort_keys=True),before)
check("no_assumed_exercise_or_conversion_journals",not assessment["mutations"] and all(j["id"] not in ["option_exercise","assumed_conversion"] for j in journals))

# Finite admission probe: fail dependent outputs instead of silently dropping instruments.
def admit(c):
    if c["identity"] != CASE["identity"]:
        return "rejected","binding"
    if any(c["scope"][k] for k in ["rights_issue","participating_instruments","partly_paid"]):
        return "basic_and_diluted_unsupported","dividend_rights_or_rights_issue"
    if any(c["attribution"].get(k) is None for k in [
            "consolidated_continuing_profit","consolidated_total_profit","nci_continuing",
            "nci_total","current_cumulative_equity_preference"]):
        return "basic_and_diluted_unresolved","profit_attribution"
    if any(e.get("date") is None or (e["type"]=="cash_issue" and e.get("consideration_receivable") is None)
           for e in c["ordinary"]["events"]):
        return "basic_and_diluted_unresolved","ordinary_timing"
    o=c["options"]
    for key in ["issue","average_market_price","settlement","future_services"]:
        if o.get(key) is None:
            return "basic_available_diluted_unresolved",key
    if F(o["average_market_price"])<=0:
        return "basic_available_diluted_rejected","nonpositive_market_price"
    if o["settlement"]!="cash exercise for fixed ordinary shares" or o["performance_condition"]:
        return "basic_available_diluted_unsupported","complex_terms"
    if any(c["convertibles"][0].get(k) is None for k in ["expense","tax_benefit","other_addback"]):
        return "basic_available_diluted_unresolved","earnings_adjustment"
    return "conditional","finite_profile"

mutations=[
 ("missing_average",["options","average_market_price"],None,"basic_available_diluted_unresolved"),
 ("missing_option_issue_date",["options","issue"],None,"basic_available_diluted_unresolved"),
 ("missing_ordinary_issue_date",["ordinary","events",0,"date"],None,"basic_and_diluted_unresolved"),
 ("missing_receivable_date",["ordinary","events",0,"consideration_receivable"],None,"basic_and_diluted_unresolved"),
 ("missing_attribution",["attribution","nci_continuing"],None,"basic_and_diluted_unresolved"),
 ("missing_settlement_terms",["options","settlement"],None,"basic_available_diluted_unresolved"),
 ("cash_alternative",["options","settlement"],"holder cash alternative","basic_available_diluted_unsupported"),
 ("missing_future_service_value",["options","future_services"],None,"basic_available_diluted_unresolved"),
 ("performance_award",["options","performance_condition"],True,"basic_available_diluted_unsupported"),
 ("missing_consequential_earnings",["convertibles",0,"other_addback"],None,"basic_available_diluted_unresolved"),
 ("wrong_entity_book_class",["identity","book"],"another-book","rejected"),
 ("rights_issue",["scope","rights_issue"],True,"basic_and_diluted_unsupported"),
 ("participating",["scope","participating_instruments"],True,"basic_and_diluted_unsupported"),
 ("partly_paid",["scope","partly_paid"],True,"basic_and_diluted_unsupported"),
 ("zero_average",["options","average_market_price"],"0","basic_available_diluted_rejected"),
 ("negative_average",["options","average_market_price"],"-5","basic_available_diluted_rejected")
]
eq("finite_profile_admission",admit(CASE),("conditional","finite_profile"))
decisions=[]
for name,path,value,expected in mutations:
    c=deepcopy(CASE)
    target=c
    for key in path[:-1]:
        target=target[key]
    target[path[-1]]=value
    status,reason=admit(c)
    eq("adverse_admission:"+name,status,expected)
    decisions.append((name,status,reason))
check("no_current_rule_claim",not CASE["scope"]["source_currentness_established"])
check("no_runtime_claim",not CASE["runtime_executed"])
save("calculated-case.json",{"ordinary_share_days":share_days,"basic_denominator":D,"basic_numerators":{"continuing":N,"total":Ntotal,"discontinued":Ndisc},
 "diluted_denominator":d,"diluted_numerators":{"continuing":n,"total":Ntotal+n-N,"discontinued":Ndisc},
 "assessment":assessment,"independent_subsets":subsets,"closing_register":register[-1],
 "actual_conversion":{"basic_denominator":actual_D,"basic_continuing":actual_N/actual_D,"diluted_continuing":cn/cd,"trace":ct},
 "option_lapse_increment":L,"continuing_loss_trace":lt,"positive_control_total_loss":total_loss/d,
 "financing_journal_slice":journals,"admission_decisions":[{"case":x,"status":y,"required":z} for x,y,z in decisions]})
result={"passed":all(r["passed"] for r in CHECKS),"check_count":len(CHECKS),"checks":CHECKS,"wall_seconds":time.perf_counter()-START}
save("calculation-checks.json",result)
save("calculation-run.json",{"command":["python3",str(Path(__file__).relative_to(ROOT))],"recorded_utc":datetime.now(timezone.utc).isoformat(),
 "wall_seconds":result["wall_seconds"],"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
 "environment":"System Python Fraction; exact deterministic documentary checks","gpu":"not initialized","seeds":"N/A",
 "data_version":"authored-eps-lifecycle-v1; retained EU2023/1803 IAS33","plan":"docs/plans/accounting-eps-lifecycle-20261014.md",
 "result":str((OUT/"result.md").relative_to(ROOT)),"script_sha256":sha(Path(__file__)),"fixture_sha256":sha(OUT/"case.json")})
print(json.dumps({"passed":result["passed"],"checks":len(CHECKS),"failed":[r for r in CHECKS if not r["passed"]],"basic":str(N/D),"diluted":str(n/d)}))
raise SystemExit(0 if result["passed"] else 1)
