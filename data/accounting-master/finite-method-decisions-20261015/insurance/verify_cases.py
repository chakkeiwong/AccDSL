"""Independent accounting/replication oracle for authored documentary cases."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, json, subprocess, time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
START = time.perf_counter()
checks, traces = [], {}

def check(name, condition, detail=None):
    checks.append({"name": name, "passed": bool(condition), "detail": detail})

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def serialize(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize(v) for v in value]
    return value

doc = json.loads((OUT/"cases.json").read_text())
sources = json.loads((OUT/"source-support.json").read_text())
check("source_manifest_binding", sha(OUT/"source-support.json")==doc["source_support_sha256"])
for source in sources["authorities"]:
    check("pdf:"+source["id"], sha(ROOT/source["pdf"])==source["pdf_sha256"])
    check("text:"+source["id"], sha(ROOT/source["text"])==source["text_sha256"])
    text = (ROOT/source["text"]).read_text()
    for span in source["spans"]:
        actual = text[span["start"]:span["end"]]
        check("span:"+source["id"]+":"+span["id"], actual==span["text"] and
              hashlib.sha256(actual.encode()).hexdigest()==span["sha256"])
check("historical_scope", "before 1 July 2026" in sources["authorities"][0]["cover"]
      and not any(s["current_authority_claim"] for s in sources["authorities"]))

m = {k: F(v) for k, v in doc["financial_model"].items() if k!="trading"}
topup = {s: max(F(0), m["floor"]-m["share"]*m[s]) for s in ["Su", "Sd"]}
# Solve the portfolio in payoff space, then compare its current cost to the
# separately derived state-price expectation. No builder functions are imported.
delta = (topup["Su"]-topup["Sd"])/(m["Su"]-m["Sd"])
bank = (topup["Sd"]-delta*m["Sd"])/m["R"]
price = delta*m["S0"]+bank
qu = (m["R"]*m["S0"]-m["Sd"])/(m["Su"]-m["Sd"])
check("positive_state_prices", m["R"]>0 and 0<qu<1)
check("guarantee_two_state_replication",
      all(delta*m[s]+bank*m["R"]==topup[s] for s in topup))
check("reported_replication", (delta,bank)==(m["delta"],m["bank"]))
check("state_price_agreement", (qu*topup["Su"]+(1-qu)*topup["Sd"])/m["R"]==price==m["guarantee_price"])
benefit_price=m["share"]*m["S0"]+price
check("benefit_price", benefit_price==m["benefit_price"]==99)
check("whole_benefit_replication",
      all((m["share"]+delta)*m[s]+bank*m["R"]==max(m["share"]*m[s],m["floor"]) for s in topup))
p_up=F(doc["physical_model"]["p_up"])
p_die=F(doc["physical_model"]["p_death"])
physical_topup=p_up*topup["Su"]+(1-p_up)*topup["Sd"]
check("physical_and_pricing_laws_differ",
      physical_topup==F(doc["physical_model"]["expected_guarantee"]) and physical_topup!=price)
mean_death=p_die*F(doc["nonfinancial_measurement"]["mortality_benefit"])
ra=F(doc["nonfinancial_measurement"]["vfa_ra"])
initial_csm=F(110)-benefit_price-mean_death-ra
check("initial_vfa_csm", initial_csm==8 and mean_death==2 and ra==1)
check("distinct_admission_obligations",
      bool(doc["admission"]["vfa"]) and bool(doc["admission"]["non_distinct"])
      and bool(doc["admission"]["no_embedded_derivative_separation"])
      and not doc["admission"]["risk_mitigation_election"])

asset_accounts={"cash","underlying","acquisition_asset","held_asset","held_receivable"}
liability_accounts={"lrc","lic"}
pnl_accounts={"investment_result","insurance_finance","onerous_loss","onerous_reversal",
              "service_revenue","claim_expense","acquisition_expense","recovery_income",
              "held_premium_expense","loss_recovery_reversal"}

def report(ledger, cashflows):
    assets=sum((ledger.get(k,F(0)) for k in asset_accounts),F(0))
    liabilities=-sum((ledger.get(k,F(0)) for k in liability_accounts),F(0))
    profit=-sum((ledger.get(k,F(0)) for k in pnl_accounts),F(0))
    owner=-ledger.get("owner_capital",F(0))
    return {"assets":assets, "liabilities":liabilities, "profit":profit,
            "cash":ledger.get("cash",F(0)), "equity":owner+profit, "oci":F(0),
            "operating_cash":cashflows["operating"],"investing_cash":cashflows["investing"],
            "revenue":-ledger.get("service_revenue",F(0))}

vfa_expected={}
for case in doc["cases"]:
    ident=case["id"]
    ledger={k:F(v) for k,v in case["opening"].items()}
    cf={"operating":F(0),"investing":F(0)}
    components={}
    rows=[]
    for e in case["events"]:
        journal={k:F(v) for k,v in e["journal"].items()}
        check(ident+":"+e["id"]+":journal", sum(journal.values(),F(0))==0)
        check(ident+":"+e["id"]+":known_accounts",
              set(journal)<=asset_accounts|liability_accounts|pnl_accounts|{"owner_capital"})
        for k,v in journal.items():
            ledger[k]=ledger.get(k,F(0))+v
        if e["cash_class"]:
            cf[e["cash_class"]]+=journal.get("cash",F(0))
        else:
            check(ident+":"+e["id"]+":no_unclassified_cash", journal.get("cash",F(0))==0)
        if e["components_after"] is not None:
            if case["kind"]=="vfa":
                components=e["components_after"]
            else:
                components.update(e["components_after"])
        current=report(ledger,cf)
        check(ident+":"+e["id"]+":statement",
              current["assets"]==current["liabilities"]+current["equity"])
        check(ident+":"+e["id"]+":cash_bridge",
              current["cash"]==F(case["opening"]["cash"])+sum(cf.values(),F(0)))
        if case["kind"]=="vfa" and components:
            c={k:F(v) for k,v in components.items()}
            expected_lrc=c["financial_benefit"]+c["mortality_pv"]+c["ra"]+c["csm"]
            check(ident+":"+e["id"]+":component",
                  -ledger.get("lrc",F(0))==expected_lrc and
                  0<=c["loss_component"]<=expected_lrc and c["csm"]>=0)
        elif case["kind"]=="acquisition":
            if "issued" in components:
                c={k:F(v) for k,v in components["issued"].items()}
                check(ident+":"+e["id"]+":issued_component",
                      -ledger.get("lrc",F(0))==c["claims"]-c["future_premium"]+c["ra"]+c["csm"])
            if "held" in components:
                c={k:F(v) for k,v in components["held"].items()}
                check(ident+":"+e["id"]+":held_component",
                      ledger.get("held_asset",F(0))==c["recoveries"]-c["future_premium"]+c["ra"]+c["cost_csm"])
        rows.append({"event":e["id"],"report":dict(current),"ledger":dict(ledger),
                     "components":json.loads(json.dumps(components))})
    final=rows[-1]["report"]
    check(ident+":final_report",
          all(final[k]==F(v) for k,v in case["expected"].items() if not k.startswith("initial_")))
    check(ident+":settled",
          all(ledger.get(k,F(0))==0 for k in (asset_accounts-{"cash"})|liability_accounts))
    if case["kind"]=="vfa":
        is_up=case["market_state"]=="up"
        s=m["Su" if is_up else "Sd"]
        g=topup["Su" if is_up else "Sd"]
        new_csm=initial_csm+(1-m["share"])*(s-m["S0"])-(g-price)
        csm=max(F(0),new_csm); loss=max(F(0),-new_csm)
        value=max(m["share"]*s,m["floor"])
        death=F(20 if case["death"] else 0)
        economic_profit=F(110)+(s-m["S0"])-value-death
        row=next(r for r in rows if r["event"]=="pre_service_remeasurement")
        c=row["components"]
        check(ident+":independent_remeasurement",
              F(c["csm"])==csm and F(c["loss_component"])==loss
              and row["report"]["liabilities"]==value+mean_death+ra+csm)
        check(ident+":independent_lifetime_cash_profit",
              final["profit"]==economic_profit and final["cash"]==50+economic_profit)
        check(ident+":finance_matches_held_asset",
              ledger["insurance_finance"]+ledger["investment_result"]==0)
        # B120: premium adjusted for financing, excluding investment repayment.
        check(ident+":revenue_excludes_investment",
              final["revenue"]==110+ledger["insurance_finance"]-value)
        weight=(p_up if is_up else 1-p_up)*(p_die if case["death"] else 1-p_die)
        check(ident+":joint_weight", F(case["physical_weight"])==weight)
        vfa_expected[ident]={"weight":weight,"profit":economic_profit,"death":case["death"],"up":is_up}
    else:
        rec=case["prior_acquisition_recoverability"]
        inflow=F(rec["premium"])-F(rec["claims"])-F(rec["ra"])
        check(ident+":prior_recoverability", inflow==F(rec["net_inflow"])>=F(rec["asset"]))
        loss=F(100)+F(5)+F(10)-F(100)
        recovery=loss*F(1,2) if case["treaty_entered_at_or_before_underlying_recognition"] else F(0)
        base_cost=F(55)-(F(50)+F(5,2))
        held_asset=F(50)+F(5,2)+base_cost+recovery
        initial=next(r for r in rows if r["event"]=="pay_held_premium")
        check(ident+":initial_group_interaction",
              initial["report"]["equity"]==50-loss+recovery==F(case["expected"]["initial_equity"])
              and initial["ledger"]["held_asset"]==held_asset==F(case["expected"]["initial_held_asset"])
              and initial["report"]["liabilities"]==105)
        check(ident+":acquisition_transferred_once",
              initial["ledger"]["acquisition_asset"]==0 and
              sum(F(e["journal"].get("cash","0")) for e in case["events"] if "acquisition" in e["id"])==-10)
        ratio=loss/F(105)
        check(ident+":systematic_loss_release", F(100)*ratio+F(5)*ratio==loss)
        check(ident+":b125_gross_presentation",
              final["revenue"]==105-loss+10==100 and ledger["acquisition_expense"]==10)
        check(ident+":gross_and_held_not_netted",
              ledger["claim_expense"]==100 and -ledger["recovery_income"]==50+recovery
              and ledger["held_premium_expense"]==55 and ledger["loss_recovery_reversal"]==recovery)
        check(ident+":independent_lifetime_cash_profit",
              final["profit"]==100-100-10+50-55 and final["cash"]==50+100-10-55-100+50)
    traces[ident]=rows

check("physical_weights_sum", sum((x["weight"] for x in vfa_expected.values()),F(0))==1)
check("physical_marginals",
      sum((x["weight"] for x in vfa_expected.values() if x["up"]),F(0))==p_up
      and sum((x["weight"] for x in vfa_expected.values() if x["death"]),F(0))==p_die)
physical_profit=sum((x["weight"]*x["profit"] for x in vfa_expected.values()),F(0))
check("physical_expected_profit", physical_profit==F(doc["physical_model"]["expected_profit"]))
check("late_and_timely_are_different_histories",
      traces["acquisition_timely"][-1]["report"]==traces["acquisition_late"][-1]["report"]
      and traces["acquisition_timely"][5]["report"]["equity"]!=traces["acquisition_late"][5]["report"]["equity"])

required={
    "physical_pricing":price, "guarantee_omitted":benefit_price,
    "whole_gain_to_csm":F(19), "vfa_loss_added_twice":F(93),
    "investment_in_revenue_up":F(22), "retain_acquisition_asset":F(0),
    "omit_acquisition_presentation":F(100), "loss_excludes_acquisition":F(15),
    "late_treaty_recovery":F(0), "held_loss_added_twice":F(125,2)
}
def documentary_admission(p):
    if p.get("same_event_same_payload"):
        return "replay_no_change"
    if "ra" in p and p["ra"] is None:
        return "measurement_unresolved"
    if "eligibility" in p and p["eligibility"] is None:
        return "admission_unresolved"
    if "physical_dependence" in p and p["physical_dependence"] is None:
        return "joint_law_unresolved"
    if F(p.get("service_units_supplied","0"))>0:
        return "dated_allocation_required"
    if p.get("additional_financial_states"):
        return "valuation_model_unresolved"
    if not m["Sd"]<m["R"]*F(p.get("S0",str(m["S0"])))<m["Su"]:
        return "no_arbitrage_bound_failed"
    if p.get("group_kind")=="reinsurance_held" and p.get("measurement")=="VFA":
        return "outside_vfa_scope"
    return "admitted"

for row in doc["adverse"]:
    if "wrong" in row:
        check("adverse:"+row["id"], F(row["wrong"])!=required[row["id"]]==F(row["required"]))
    else:
        check("adverse:"+row["id"], documentary_admission(row["input_patch"])==row["decision"])
check("unrelated_index",
      subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)
      ==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes())
result={"passed":all(x["passed"] for x in checks),"check_count":len(checks),
        "checks":checks,"wall_seconds":time.perf_counter()-START,
        "case_sha256":sha(OUT/"cases.json"),
        "scope":"Independent documentary arithmetic/admission oracle; no product endpoint, store or runtime executed."}
(OUT/"independent-checks.json").write_text(json.dumps(result,indent=2)+"\n")
(OUT/"checked-statements.json").write_text(json.dumps(serialize(traces),indent=2)+"\n")
print(json.dumps({"passed":result["passed"],"checks":len(checks),
                  "failed":[c["name"] for c in checks if not c["passed"]]}))
if not result["passed"]:
    raise SystemExit(1)
