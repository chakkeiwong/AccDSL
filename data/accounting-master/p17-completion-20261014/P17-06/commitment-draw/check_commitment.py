"""Exact documentary joint-outcome and journal comparison, not bank software."""
from collections import defaultdict
from fractions import Fraction as F
import json
from pathlib import Path
import time

OUT=Path(__file__).resolve().parent


def main():
    started=time.perf_counter()
    case=json.loads((OUT/"commitment-cases.json").read_text()); c=case["contract"]
    checks=[]
    def check(name,actual,expected=True):
        checks.append({"name":name,"passed":actual==expected,"observed":str(actual),"expected":str(expected)})
    r=F(c["original_eir"]); discount=(1+r)**c["years_to_due"]
    pv_loss=(F(c["due"])-F(c["recovery"]))/discount
    check("contract_eir",F(c["due"])/discount,F(c["limit"]))
    # Initial fair value is an admission input, not inferred from physical losses.
    check("stated_par_admission",F(c["initial_fv"]),F(c["limit"]))
    draw_probs={}
    for key in ["joint_initial","joint_sicr"]:
        tree=case[key]
        check(key+":probabilities_sum_one",sum(F(x["probability"]) for x in tree),F(1))
        check(key+":nonnegative",all(F(x["probability"])>=0 for x in tree))
        check(key+":no_default_without_draw",all(x["draw"] or x["default_year"] is None for x in tree))
        check(key+":unique_outcomes",len({(x["draw"],x["default_year"]) for x in tree}),len(tree))
        draw_probs[key]=sum(F(x["probability"]) for x in tree if x["draw"])
    def ecl(tree,horizon,condition_draw=False):
        eligible=[x for x in tree if x["draw"] and x["default_year"] is not None and x["default_year"]<=horizon]
        amount=sum((F(x["probability"])*pv_loss for x in eligible),F(0))
        return amount/sum(F(x["probability"]) for x in tree if x["draw"]) if condition_draw else amount
    m={"loss_pv_if_default":pv_loss,
       "initial_twelve_month":ecl(case["joint_initial"],1),"initial_lifetime":ecl(case["joint_initial"],2),
       "sicr_twelve_month":ecl(case["joint_sicr"],1),"sicr_lifetime":ecl(case["joint_sicr"],2),
       "funded_lifetime":ecl(case["joint_sicr"],2,True),"funded_twelve_month_wrong_horizon":ecl(case["joint_sicr"],1,True)}
    for k,v in case["expected_ecl"].items():check("ecl:"+k,m[k],F(v))
    check("draw_probability_unchanged",draw_probs["joint_initial"],draw_probs["joint_sicr"])
    check("funded_expected_terminal",F(c["due"])-F("2/5")*(F(c["due"])-F(c["recovery"])),F("116.16"))
    check("credit_history_predates_draw",case["credit_history"]["initial_date"]<case["credit_history"]["sicr_date"]<case["credit_history"]["funding_date"])
    check("not_zero_because_no_cash_due_in_twelve_months",m["initial_twelve_month"]>0 and c["years_to_due"]>1)

    def post(b,j,route):
        check(route+":"+j["id"]+":balanced",sum((F(v) for _,v in j["lines"]),F(0)),F(0))
        for name,v in j["lines"]:b[name]+=F(v)
        check(route+":"+j["id"]+":trial_balance",sum(b.values()),F(0))
        check(route+":"+j["id"]+":nonnegative_cash",b["Cash"]>=0)
    b0=defaultdict(F,{a:F(v) for a,v in case["opening"].items()})
    for j in case["common_journals"]:post(b0,j,"pre_draw")
    check("predraw_no_loan",b0["Gross loan"],F(0))
    check("predraw_no_cash_outflow",b0["Cash"],F(200))
    check("predraw_liability",-b0["Commitment provision"],m["sicr_lifetime"])
    results={}
    for route,journals in case["routes"].items():
        b=b0.copy()
        for j in journals:
            post(b,j,route)
            if j["id"]=="credit-borrower-deposit":
                check("deposit_route_cash_unchanged_on_credit",b["Cash"],F(200))
                check("deposit_route_deposit_increase",-b["Deposits"],F(280))
            if route=="deposit_then_external" and j["id"]=="transfer-and-remeasure":
                check("deposit_route_prefunding_equity",-b["Capital"]-b["Impairment"],F(16))
        m2={"cash":b["Cash"],"gross":b["Gross loan"],"allowance":-b["Loan allowance"],"provision":-b["Commitment provision"],"deposits":-b["Deposits"],"equity":-b["Capital"]-b["Impairment"],"profit":-b["Impairment"]}
        for k,v in case["expected_final"][route].items():check(route+":statement:"+k,m2[k],F(v))
        check(route+":assets_equals_liabilities_equity",m2["cash"]+m2["gross"]-m2["allowance"],m2["deposits"]+m2["provision"]+m2["equity"])
        results[route]=m2
    check("funding_routes_equal_final_state",results["direct_external"],results["deposit_then_external"])
    check("funded_loan_allowance_matches_conditional_ecl",results["direct_external"]["allowance"],m["funded_lifetime"])
    check("incremental_draw_impairment",m["funded_lifetime"]-m["sicr_lifetime"],F(2))
    check("funded_loss_rollforward",F("0.5")+F("1.5")+F(2),m["funded_lifetime"])
    check("lapse_loss_rollforward",F("0.5")+F("1.5")-F(2),F(0))
    # Distinct wrong interpretations can produce the same erroneous allowance.
    wrong_unconditional=m["sicr_lifetime"]
    wrong_reset=m["funded_twelve_month_wrong_horizon"]
    check("two_wrong_reasons_same_amount",wrong_unconditional,wrong_reset)
    check("both_understate_funded_allowance",m["funded_lifetime"]-wrong_reset,F(2))
    for name,allowance,provision,equity in [
        ("reset_stage_one",F(2),F(0),F(18)),
        ("retain_old_draw_weight",F(2),F(0),F(18)),
        ("retain_provision_and_full_allowance",F(4),F(2),F(14))]:
        check(name+":still_balances",F(100)+F(100)-allowance,F(180)+provision+equity)
        check(name+":wrong_equity",equity != results["direct_external"]["equity"])
    result={"passed":all(x["passed"] for x in checks),"check_count":len(checks),"checks":checks,
            "role":"deterministic authored probability-tree and documentary journal arithmetic; no calibrated probabilities, prudential inference or runtime",
            "wall_seconds":time.perf_counter()-started}
    (OUT/"calculation-checks.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ["passed","check_count","wall_seconds"]}))
    if not result["passed"]:
        print([x for x in checks if not x["passed"]]);raise SystemExit(1)


if __name__=="__main__":main()
