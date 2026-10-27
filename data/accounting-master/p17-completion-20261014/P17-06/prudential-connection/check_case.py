"""Exact documentary derivation; no live bank, rule engine or stochastic run."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
CHECKS=[]
def check(name,ok,detail=None):CHECKS.append({"name":name,"passed":bool(ok),"detail":detail})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {k:exact(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [exact(v) for v in x]
    return x
def save(name,x):(OUT/name).write_text(json.dumps(exact(x),indent=2)+"\n")

def main():
    start=time.perf_counter();started=datetime.now(timezone.utc).isoformat()
    case=json.loads((OUT/"case.json").read_text())
    a={k:F(v) for k,v in case["opening"].items()}; opening=deepcopy(a)
    assets=["cash","loans","goodwill","allowance"]
    income=["interest_income","interest_expense","credit_loss_expense"]
    def book(a):
        net=sum(a[k] for k in assets);liabilities=-a["deposits"]-a["borrowing"]
        equity=-a["common_stock"]-a["retained_earnings"]-sum(a[k] for k in income)
        assert sum(a.values())==0 and net==liabilities+equity
        assert a["allowance"]<=0 and a["deposits"]<=0 and a["borrowing"]<=0
        return {"cash":a["cash"],"net_assets":net,"deposits":-a["deposits"],"borrowing":-a["borrowing"],
                "equity":equity,"income_before_close":-sum(a[k] for k in income)}
    def capital(a):
        b=book(a);allowance=-a["allowance"];base=a["loans"]
        admitted=min(allowance,base/F(80));excess=allowance-admitted
        cet1=b["equity"]-a["goodwill"];denominator=base-excess
        return {**b,"cet1":cet1,"tier1":cet1,"additional_tier1":F(0),"goodwill_deduction":a["goodwill"],
                "gross_loan_exposure":a["loans"],"cap_base":base,"cap":base/F(80),"aacl":allowance,
                "tier2":admitted,"excess":excess,"rwa":denominator,"total_capital":cet1+admitted,
                "ratios":{"cet1":cet1/denominator,"tier1":cet1/denominator,"total":(cet1+admitted)/denominator} if denominator>0 else None}
    def expected(name,values):
        for k,v in case["expected"][name].items():check(name+":"+k,values[k]==F(v),str(values[k]))
    expected("opening",capital(a))
    check("opening_allowance_below_cap",-a["allowance"]<a["loans"]/80)
    states=[{"event":"opening","accounts":deepcopy(a),"assessment":capital(a)}];journals=[]
    for event in case["events"]:
        kind=event["kind"];v=F(event.get("amount",0))
        if kind=="originate_credit_deposit":lines=[("loans",v),("deposits",-v)]
        elif kind=="pay_deposit_externally":lines=[("deposits",v),("cash",-v)]
        elif kind=="receive_earned_interest":lines=[("cash",v),("interest_income",-v)]
        elif kind=="credit_deposit_interest":lines=[("interest_expense",v),("deposits",-v)]
        elif kind=="supplied_allowance_remeasurement":
            change=F(event["target_allowance"])+a["allowance"]
            lines=[("credit_loss_expense",change),("allowance",-change)]
            check("allowance_is_supplied",event["measurement_status"]=="supplied_not_estimated")
        elif kind=="close_income_accounts":
            lines=[(k,-a[k]) for k in income]+[("retained_earnings",sum(a[k] for k in income))]
        else:raise ValueError(kind)
        check(event["id"]+":derived_journal",lines==[(k,F(v)) for k,v in event["expected_lines"]])
        check(event["id"]+":balanced",sum(v for _,v in lines)==0)
        previous=deepcopy(a)
        for k,v in lines:a[k]+=v
        check(event["id"]+":book_balance",sum(a.values())==0)
        state={"event":event["id"],"accounts":deepcopy(a),"assessment":capital(a)};states.append(state)
        journals.append({"event":event["id"],"lines":lines,"before":previous,"after":deepcopy(a)})
    expected("pre_runoff",capital(a));expected("risk_ratios",capital(a)["ratios"])
    check("income_is_closed_separately",all(a[k]==0 for k in income) and a["retained_earnings"]==F(-18,5))
    check("income_and_equity_movement",F(6)-F(2)-F(8,5)==book(a)["equity"]-book(opening)["equity"]==F(12,5))
    check("origination_is_not_cash_payment",states[1]["accounts"]["cash"]==opening["cash"] and states[1]["accounts"]["deposits"]==F(-130))
    check("pre_runoff_cash_bridge",a["cash"]-opening["cash"]==F(-15)+F(6))
    check("final_allowance_above_cap",-a["allowance"]>a["loans"]/80)
    base_cap=capital(a);branches={}
    for name,demand_key in [("runoff","runoff"),("stress","stress_runoff")]:
        demand=F(case["funding"][demand_key]);limit=F(case["funding"]["limit"]);x=deepcopy(a)
        draw=min(max(demand-x["cash"],F(0)),limit);paid=min(demand,x["cash"]+draw);unpaid=demand-paid
        lines=[("cash",draw),("borrowing",-draw),("deposits",paid),("cash",-paid)]
        for k,v in lines:x[k]+=v
        values=capital(x);values["unpaid"]=unpaid;expected(name,values)
        check(name+":cash_bridge",x["cash"]==a["cash"]+draw-paid)
        check(name+":equity_and_prudential_unchanged",all(values[k]==base_cap[k] for k in ["equity","cet1","tier2","rwa","total_capital"]))
        check(name+":unpaid_retained",values["deposits"]>=unpaid and values["deposits"]==F(117)-paid)
        branches[name]={"accounts":x,"lines":lines,"draw":draw,"paid":paid,"unpaid":unpaid,"status":"default_unpaid" if unpaid else "settled","assessment":values}
    check("stress_default_not_ratio_failure",branches["stress"]["status"]=="default_unpaid" and branches["stress"]["assessment"]["ratios"]==branches["runoff"]["assessment"]["ratios"])

    def assess(c,state,perimeter=None,rule_date=None,average_marker=True):
        # A bounded fixture oracle only, not an implementation of a general legal rule engine.
        identities=c["identity"]
        if (perimeter or identities["perimeter_id"])!=identities["perimeter_id"] or (rule_date or c["rule_snapshot"])!="2026-01-01":
            return {"status":"input_rejected","capital":None,"leverage":None,"commit":False}
        if c["scope"]["pcd"] or c["exposures"]["nonaccrual"]:
            return {"status":"unsupported_exposure_profile","capital":None,"leverage":None,"commit":False}
        eligibility=list(c["stock_eligibility"].values())
        if any(v is None for v in eligibility):
            return {"status":"capital_unresolved","capital":None,"leverage":None,"known_gross_loan":state["loans"],"commit":False}
        if not all(v is True for v in eligibility):
            return {"status":"unsupported_capital_profile","capital":None,"leverage":None,"commit":False}
        cap=capital(state);avg=c["average_assets_input"] if average_marker else None
        result={"status":"complete_conditional","capital":cap,"leverage":None,"commit":False}
        if avg is None:result["status"]="leverage_unresolved_only";return result
        if any(avg[k]!=identities[k] for k in ["bank_id","perimeter_id","currency","unit"]) or avg["window_id"]!=c["reporting_window"]["window_id"] or avg["statistic"]!="average_total_consolidated_assets":
            result["status"]="leverage_input_rejected";return result
        denominator=F(avg["value"])-state["goodwill"]
        if denominator<=0:result["status"]="leverage_undefined";return result
        result["leverage"]={"numerator":cap["tier1"],"denominator":denominator,"ratio":cap["tier1"]/denominator}
        return result
    original=deepcopy(a);positive=assess(case,a);expected("leverage",positive["leverage"])
    check("assessment_never_posts",a==original and positive["commit"] is False)
    decisions=[]
    for fixture in case["adverse_cases"]:
        c=deepcopy(case);kwargs={};mutation=fixture["mutation"]
        if mutation=="stock_eligibility.x_unknown":c["stock_eligibility"]["x"]=None
        elif mutation=="stock_eligibility.x_false":c["stock_eligibility"]["x"]=False
        elif mutation=="request.perimeter_parent":kwargs["perimeter"]="parent-group"
        elif mutation=="request.rule_snapshot_changed":kwargs["rule_date"]="2026-04-01"
        elif mutation=="average_absent":kwargs["average_marker"]=False
        elif mutation=="average_statistic_closing_assets":
            c["average_assets_input"]["statistic"]="period_end_assets";c["average_assets_input"]["value"]=str(book(a)["net_assets"])
        elif mutation=="average.perimeter_parent":c["average_assets_input"]["perimeter_id"]="parent-group"
        elif mutation=="exposures.nonaccrual_true":c["exposures"]["nonaccrual"]=True
        elif mutation=="scope.pcd_true":c["scope"]["pcd"]=True
        elif mutation=="average_equals_goodwill":c["average_assets_input"]["value"]=str(a["goodwill"])
        else:raise ValueError(mutation)
        result=assess(c,a,**kwargs)
        check(fixture["id"]+":status",result["status"]==fixture["expected"])
        check(fixture["id"]+":no_posting",result["commit"] is False and a==original)
        if fixture["expected"].startswith("leverage"):
            check(fixture["id"]+":risk_results_preserved",result["capital"]==base_cap and result["leverage"] is None)
        decisions.append({**fixture,"derived_result":result})

    # Compare independent wrong computations with the claimed target; every one discriminates.
    gross=a["loans"];allowance=-a["allowance"];goodwill=a["goodwill"]
    wrong_base=gross-allowance;wrong_t=min(allowance,wrong_base/80)
    wrong_circular_t=(gross-allowance)/79
    errors={
        "net_loan_exposure":{"cap_base":wrong_base,"tier2":wrong_t,"rwa":wrong_base-(allowance-wrong_t)},
        "omit_excess":{"rwa":gross},
        "deduct_full_allowance":{"rwa":gross-allowance},
        "include_deducted_goodwill":{"cap_base":gross+goodwill,"tier2":(gross+goodwill)/80,"rwa":gross+goodwill-(allowance-(gross+goodwill)/80)},
        "circular_cap":{"tier2":wrong_circular_t,"rwa":gross-allowance+wrong_circular_t},
        "deduct_allowance_twice":{"cet1":base_cap["cet1"]-allowance},
        "accounting_equity_is_capital":{"cet1":book(a)["equity"]}}
    for name,values in errors.items():
        check(name+":wrong_relative_to_target",any(v!=base_cap[k] for k,v in values.items()),exact(values))
    check("circular_answer_solves_wrong_equation",wrong_circular_t==(gross-allowance+wrong_circular_t)/80 and wrong_circular_t!=base_cap["tier2"])
    check("closing_assets_does_not_supply_average",book(a)["net_assets"]!=F(case["average_assets_input"]["value"]))
    check("synthetic_evidence_and_rules",case["runtime_executed"] is False and case["reporting_window"]["law_mode"]=="conditional_frozen_2026-01-01_rules")
    check("parameters_match_inspected_clauses",{k:F(v) for k,v in case["rule_parameters"].items()}=={"cash_weight":F(0),"loan_weight":F(1),"allowance_cap_rate":F(1,80),"goodwill_deduction_fraction":F(1)})
    check("all_stock_conditions_explicit",list(case["stock_eligibility"])==["i","ii","iii","iv","v","vi","vii","viii","ix","x","xi","xii","xiii"] and all(case["stock_eligibility"].values()))
    check("unrelated_index_preserved",(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()==subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT))
    save("calculated-case.json",{"states":states,"journals":journals,"alternative_runoff_branches":branches,"assessment":positive,"adverse_decisions":decisions,"wrong_computations":errors})
    result={"passed":all(c["passed"] for c in CHECKS),"check_count":len(CHECKS),"checks":CHECKS,"wall_seconds":time.perf_counter()-start}
    save("calculation-checks.json",result)
    save("calculation-run.json",{"command":["python3",str(Path(__file__).relative_to(ROOT))],"started_utc":started,"wall_seconds":result["wall_seconds"],
        "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"environment":"system Python fractions; deterministic CPU",
        "gpu":"N/A; no framework or GPU initialized","seeds":"N/A; exact authored example","data_version":sha(OUT/"case.json"),
        "plan":"docs/plans/accounting-bank-prudential-connection-20261014.md","result":str((OUT/"result.md").relative_to(ROOT)),"script_sha256":sha(Path(__file__))})
    print(json.dumps({"passed":result["passed"],"checks":len(CHECKS),"failures":[c for c in CHECKS if not c["passed"]]}))
    if not result["passed"]:raise SystemExit(1)

if __name__=="__main__":main()
