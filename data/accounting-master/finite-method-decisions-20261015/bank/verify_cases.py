"""Independent finite bank journal, cash, credit and collateral calculations."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,subprocess,time
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
START=time.perf_counter()
checks=[];traces={}
def check(name,condition,detail=None):
    checks.append({"name":name,"passed":bool(condition),"detail":detail})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def plain(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,list):return [plain(v) for v in x]
    return x
d=json.loads((OUT/"cases.json").read_text())
sources=json.loads((OUT/"source-support.json").read_text())
check("source_binding",sha(OUT/"source-support.json")==d["source_support_sha256"])
for s in sources["authorities"]:
    check("source:"+s["id"],sha(ROOT/s["pdf"])==s["pdf_sha256"] and
          sha(ROOT/s["text"])==s["text_sha256"] and not s["current_authority_claim"])
    text=(ROOT/s["text"]).read_text()
    for span in s["spans"]:
        actual=text[span["start"]:span["end"]]
        check("span:"+s["id"]+":"+span["id"],
              actual==span["text"] and hashlib.sha256(actual.encode()).hexdigest()==span["sha256"])
check("authority_window","before 1 July 2026" in sources["authorities"][0]["cover"])
assets={"cash","securities","gross_loan","allowance"}
liabilities={"deposits","funding_liability"}
pnl={"interest_income","impairment_expense","modification_expense","derecognition_gain"}
for c in d["cases"]:
    name=c["id"];ledger={k:F(v) for k,v in c["opening"].items()}
    opening_cash=ledger["cash"];opening_equity=-ledger.get("opening_equity",F(0))
    cf={"operating":F(0),"financing":F(0)};attrs={};rows=[]
    for e in c["events"]:
        j={k:F(v) for k,v in e["journal"].items()}
        check(name+":"+e["id"]+":journal",sum(j.values(),F(0))==0)
        for k,v in j.items():ledger[k]=ledger.get(k,F(0))+v
        attrs.update(e["attributes_after"])
        if e["cash_class"]:
            cf[e["cash_class"]]+=j.get("cash",F(0))
        else:
            check(name+":"+e["id"]+":cash_unchanged",j.get("cash",F(0))==0)
        a=sum((ledger.get(k,F(0)) for k in assets),F(0))
        l=-sum((ledger.get(k,F(0)) for k in liabilities),F(0))
        p=-sum((ledger.get(k,F(0)) for k in pnl),F(0))
        r={"cash":ledger["cash"],"gross":ledger.get("gross_loan",F(0)),
           "allowance":-ledger.get("allowance",F(0)),"liabilities":l,
           "equity":opening_equity+p,"profit":p,"interest":-ledger.get("interest_income",F(0)),
           "operating_cash":cf["operating"],"financing_cash":cf["financing"],"oci":F(0)}
        for k in ["contractual_claim","unpaid_due"]:
            if k in attrs:r[k]=F(attrs[k])
        check(name+":"+e["id"]+":statement",a==l+r["equity"])
        check(name+":"+e["id"]+":cash_bridge",r["cash"]==opening_cash+sum(cf.values(),F(0)))
        check(name+":"+e["id"]+":nonnegative_cash_allowance",r["cash"]>=0 and r["allowance"]>=0)
        rows.append({"event":e["id"],"ledger":dict(ledger),"attributes":dict(attrs),"report":r})
    last=rows[-1]["report"]
    check(name+":final",all(last[k]==F(v) for k,v in c["expected"].items()))
    traces[name]=rows
    by={r["event"]:r for r in rows}
    if c["kind"]=="modified":
        check(name+":explicit_assessment_order",c["assessment_time"]=="2024-12-31"
              and c["payment_time"]=="2025-12-31" and
              c["assessment_order"]=="modification_then_forecast_then_distinct_credit_review_same_close")
        rate=1+F(c["rate"]["rate"])
        mean0=sum((F(x["weight"])*F(x["payment"]) for x in c["law_after_modification"]),F(0))
        mean1=sum((F(x["weight"])*F(x["payment"]) for x in c["law_after_credit_review"]),F(0))
        check(name+":laws",all(sum((F(x["weight"]) for x in c[key]),F(0))==1
              for key in ["law_after_modification","law_after_credit_review"]))
        check(name+":modified_gross",F(110)/rate==100 and
              by["modify_continuing_rights"]["report"]["gross"]==100)
        check(name+":separate_modification_ecl",
              mean0==88 and F(100)-mean0/rate==20==
              by["measure_modified_ecl"]["report"]["allowance"])
        reviewed=by["dated_credit_assessment"]
        check(name+":reviewed_allowance",mean1==99 and F(100)-mean1/rate==10==reviewed["report"]["allowance"])
        check(name+":original_risk_and_sicr_retained",
              reviewed["attributes"]["original_risk_ref"]=="origination-2023" and reviewed["attributes"]["sicr"])
        check(name+":separate_credit_impairment_finding",
              reviewed["attributes"]["credit_impaired"]!=c["cured"] and
              reviewed["attributes"]["objective_improvement"]==c["cured"])
        basis=F(100) if c["cured"] else F(90)
        check(name+":correct_interest_basis",last["interest"]==basis*F(c["rate"]["rate"]))
        check(name+":independent_lifetime_result",
              last["profit"]==110-(110-55) and last["cash"]==100+110)
    elif c["kind"]=="release":
        check(name+":net_carrying_gain",last["profit"]==85-(100-20))
        check(name+":expired_rights",attrs["rights"]=="expired" and bool(attrs["release_evidence"]))
    elif c["kind"]=="collateral":
        recoveries=c["conditional_default_recoveries"]
        check(name+":default_law",sum(F(x["weight"]) for x in recoveries)==1
              and sum(F(x["weight"])*F(x["net_receipt"]) for x in recoveries)==F(1331,20)
              and all(x["period"]==3 for x in recoveries))
        check(name+":no_premature_fixed_loss",max(F(x["net_receipt"]) for x in recoveries)==121
              and c["writeoff_assessment"]["earlier_no_recovery_finding"]=="requires_earlier_partial_writeoff")
        check(name+":actual_supported_outcome",F(recoveries[c["writeoff_assessment"]["actual_outcome_index"]]["net_receipt"])==F(1331,20))
        growth=1+F(c["rate"]["rate"])
        check(name+":half_year_rate_not_annual",growth**2-1==F(c["rate"]["annual_effective"]))
        pv=sum((F(s["weight"])*sum((F(x["receipt"])/growth**x["period"] for x in s["payments"]),F(0))
                for s in c["law"]),F(0))
        check(name+":cash_shortfall_pv",pv==80 and 100-pv==20)
        delayed=c["law"][1]["payments"][0]
        check(name+":costs_once",F(delayed["gross_agent_proceeds"])-F(delayed["agent_costs"])==F(delayed["receipt"]))
        check(name+":post_maturity_timing",delayed["period"]>2 and F(delayed["receipt"])/growth**3==50)
        check(name+":mixture_discount_roll",
              by["pre_observation_allowance"]["report"]["allowance"]==110-pv*growth==22)
        default=by["observed_default"]["report"]
        check(name+":default_measurement",default["gross"]-default["allowance"]==F(delayed["receipt"])/growth**2==55)
        maturity=by["maturity_net_interest"]["report"]
        late=by["post_maturity_net_interest"]["report"]
        check(name+":no_new_contractual_interest",maturity["gross"]==late["gross"]==late["contractual_claim"]==121)
        check(name+":net_interest_unwind",
              maturity["gross"]-maturity["allowance"]==F(121,2)
              and late["gross"]-late["allowance"]==F(delayed["receipt"]))
        check(name+":written_off_rights_preserved",
              last["gross"]==last["allowance"]==0 and last["contractual_claim"]==121-F(delayed["receipt"])
              and attrs["rights"]=="not_legally_released")
        check(name+":actual_loss_and_negative_equity",
              last["profit"]==F(delayed["receipt"])-100 and last["equity"]<0)
    else:
        f=c["facility"];capacity=min(F(f["limit"])-F(f["existing_draw"]),
                                    F(f["eligible_market_value"])*(1-F(f["haircut"])))
        received=F(c["confirmed_fill"])
        check(name+":capacity",capacity==8 and F(by["request_funding"]["attributes"]["capacity"])==capacity)
        check(name+":request_is_not_cash",
              by["request_funding"]["report"]["cash"]==20 and not by["request_funding"]["ledger"].get("funding_liability",0))
        check(name+":confirmed_cash",by["confirm_receipt"]["report"]["cash"]==20+received)
        check(name+":capacity_not_asset",ledger["securities"]==50 and set(ledger)<=assets|liabilities|pnl|{"opening_equity"})
        check(name+":unpaid_inside_deposits",last["unpaid_due"]==30-(20+received)
              and -ledger["deposits"]==90+last["unpaid_due"] and last["liabilities"]==100)
        if not received:
            check(name+":pending_requires_cash_evidence",
                  f["receipt_evidence"]=="independently_confirmed_no_receipt_by_deadline" and
                  f["request_status"]=="pending")

rc=traces["modified_cured"][-1]["report"]
ri=traces["modified_still_impaired"][-1]["report"]
check("same_closing_balances_different_interest",
      {k:v for k,v in rc.items() if k!="interest"}=={k:v for k,v in ri.items() if k!="interest"}
      and rc["interest"]!=ri["interest"])
targets={
    "use_net_interest_after_cure":rc["interest"],
    "use_gross_interest_still_impaired":ri["interest"],
    "omit_late_collateral":F(20),
    "invent_post_maturity_claim":F(121),
    "writeoff_erases_legal_right":traces["delayed_collateral"][-1]["report"]["contractual_claim"],
    "post_capacity_as_cash":traces["funding_0"][0]["report"]["cash"],
    "post_request_instead_of_partial_fill":traces["funding_6"][1]["report"]["cash"],
    "duplicate_unpaid_liability":traces["funding_8"][-1]["report"]["liabilities"]
}
for x in d["adverse"]:
    if "wrong" in x:
        check("adverse:"+x["id"],F(x["wrong"])!=targets[x["id"]]==F(x["required"]))
    elif "requested" in x:
        check("adverse:"+x["id"],F(x["requested"])>F(x["capacity"]) and x["decision"]=="request_rejected")
    elif "received" in x:
        check("adverse:"+x["id"],F(x["received"])>F(x["capacity"]) and
              x["decision"]=="record_receipt_and_control_violation")
check("unrelated_index",subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)
      ==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes())
extra=json.loads((OUT/"supplemental-source-support.json").read_text())
src=ROOT/extra["text_path"]
check("supplemental_source",sha(src)==extra["text_sha256"])
lines=src.read_text().splitlines(keepends=True)
for s in extra["spans"]:
    actual="".join(lines[s["first_line"]-1:s["last_line"]])
    check("supplement:"+s["id"],actual==s["text"] and
          hashlib.sha256(actual.encode()).hexdigest()==s["sha256"])
result={"passed":all(c["passed"] for c in checks),"check_count":len(checks),"checks":checks,
        "wall_seconds":time.perf_counter()-START,"case_sha256":sha(OUT/"cases.json"),
        "scope":"Documentary arithmetic and selected numeric admission checks. Remaining semantic adverse dispositions are source-reviewed obligations, not runtime test results."}
(OUT/"independent-checks.json").write_text(json.dumps(result,indent=2)+"\n")
(OUT/"checked-statements.json").write_text(json.dumps(plain(traces),indent=2)+"\n")
print(json.dumps({"passed":result["passed"],"checks":len(checks),"failed":[c["name"] for c in checks if not c["passed"]]}))
if not result["passed"]:raise SystemExit(1)
