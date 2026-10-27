"""Exact documentary checks; this is not a corporate runtime implementation."""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import time

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
checks=[]


def check(name,condition,detail=None):
    checks.append({"name":name,"passed":bool(condition),"detail":detail})


def number(x):
    return str(x) if x.denominator != 1 else int(x)


class Book:
    def __init__(self,opening=None):
        self.balances=defaultdict(F,{k:F(v) for k,v in (opening or {}).items()})
        self.events=[]

    def post(self,name,**debit_signed):
        lines={k:F(v) for k,v in debit_signed.items() if v}
        check(name+":journal_balance",sum(lines.values())==0)
        for account,value in lines.items():
            self.balances[account]+=value
        check(name+":book_balance",sum(self.balances.values())==0)
        self.events.append({"event":name,"debit_signed_lines":{k:number(v) for k,v in lines.items()},
            "closing":{k:number(v) for k,v in self.balances.items()}})


def advance_path(order):
    book=Book()
    state={k:F(0) for k in ["R","G","A","K","C"]}
    def apply(kind,amount,credit=0):
        amount,credit=F(amount),F(credit)
        if kind=="advance":
            if any(state[k] for k in ["R","G","K","C"]) or state["A"]+amount>100:
                raise ValueError("advance_scope")
            state["A"]+=amount
            book.post("advance",cash=amount,cl=-amount)
        elif kind=="earn":
            if state["R"]+amount>100:
                raise ValueError("price_exceeded")
            use=min(amount,-book.balances["cl"])
            state["R"]+=amount
            book.post("earn",cl=use,ca=amount-use,revenue=-amount)
        elif kind=="bill":
            if credit>min(amount,state["A"]-state["K"]):
                raise ValueError("advance_overapplication")
            net=amount-credit
            state["G"]+=amount
            state["K"]+=credit
            use=min(net,book.balances["ca"])
            book.post("bill",ar=net,ca=-use,cl=-(net-use))
        else:
            if amount>book.balances["ar"]:
                raise ValueError("overcollection")
            state["C"]+=amount
            book.post("collect",cash=amount,ar=-amount)
        r,g,a,k,c=(state[x] for x in ["R","G","A","K","C"])
        t=g+a-k
        expected={"cash":a+c,"ar":g-k-c,"ca":max(r-t,0),"cl":-max(t-r,0),"revenue":-r}
        check(kind+":recurrence_matches_journal",all(book.balances[x]==v for x,v in expected.items()))
        check(kind+":revenue_net_asset_identity",a+c+(g-k-c)+max(r-t,0)-max(t-r,0)==r)
    apply("advance",30)
    for kind in order:
        apply(kind,60 if kind=="earn" else 80,30 if kind=="bill" else 0)
    apply("collect",20)
    midpoint=dict(book.balances)
    check("midpoint_known_result",[midpoint[k] for k in ["cash","ar","ca","cl","revenue"]]==[50,30,0,-20,-60])
    snapshot=(dict(book.balances),dict(state),len(book.events))
    try:
        apply("bill",20,30)
    except ValueError as error:
        check("reused_credit_rejected",str(error)=="advance_overapplication")
    else:
        check("reused_credit_rejected",False)
    check("rejection_no_mutation",snapshot==(dict(book.balances),dict(state),len(book.events)))
    apply("earn",40)
    apply("bill",20)
    apply("collect",50)
    check("completed_contract",all(book.balances[k]==v for k,v in {"cash":100,"ar":0,"ca":0,"cl":0,"revenue":-100}.items()))
    return {"ordering":order,"midpoint":{k:number(v) for k,v in midpoint.items()},"events":book.events}


def main():
    started=time.perf_counter()
    paths=[advance_path(["earn","bill"]),advance_path(["bill","earn"])]
    check("both_orderings_same_endpoint",paths[0]["midpoint"]==paths[1]["midpoint"])
    # A separate wholly prepaid bill must change allocation but no account.
    before={"R":0,"G":0,"A":30,"K":0,"C":0}
    after={**before,"G":30,"K":30}
    def balances(s):
        t=s["G"]+s["A"]-s["K"]
        return (s["A"]+s["C"],s["G"]-s["K"]-s["C"],max(s["R"]-t,0),max(t-s["R"],0))
    check("state_only_bill_same_accounts",balances(before)==balances(after)==(30,0,0,30))
    check("state_only_bill_consumes_credit",before["A"]-before["K"]==30 and after["A"]-after["K"]==0)
    check("wrong_initial_revenue_balances",30-30==0)
    check("wrong_initial_revenue_fails_performance",30!=before["R"])
    check("wrong_gross_receivable_overstates_right",80-(80-30)==30)

    book=Book({"inventory":600,"opening_equity":-600})
    book.post("2024-transfer",cash=1000,revenue=-900,refund=-100,cogs=540,recovery=60,inventory=-600)
    check("initial_profit",-(book.balances["revenue"]+book.balances["cogs"])==360)
    book.post("2024-reestimate",revenue=20,refund=-20,recovery=12,cogs=-12)
    year1=dict(book.balances)
    check("2024_balances",[year1[k] for k in ["cash","recovery","refund","revenue","cogs"]]==[1000,72,-120,-880,528])
    profit1=-(year1["revenue"]+year1["cogs"])
    check("2024_equity",600+profit1==952)
    check("2024_indirect_cash",profit1+600-72+120==1000)
    book.post("2025-final-reestimate",refund=40,revenue=-40,cogs=24,recovery=-24)
    book.post("2025-settle-eight",refund=80,cash=-80,inventory=48,recovery=-48)
    final=book.balances
    profit_total=-(final["revenue"]+final["cogs"])
    profit2=profit_total-profit1
    check("final_balances",[final[k] for k in ["cash","inventory","recovery","refund","revenue","cogs"]]==[920,48,0,0,-920,552])
    check("2025_profit",profit2==16)
    check("2025_indirect_cash",profit2-48+72-120==-80)
    check("lifetime_quantity_cost",92*6==final["cogs"] and 8*6==final["inventory"])
    check("lifetime_cash_price",92*10==final["cash"] and 100*10-8*10==final["cash"])
    check("lifetime_equity",600+profit_total==final["cash"]+final["inventory"]==968)
    recovery=12*(F(6)-F(1)-F(1,2))
    check("recovery_cost_sensitivity",recovery==54 and 600-recovery==546 and 880-(600-recovery)==334)
    check("wrong_gross_sale_balances",1000-1000+600-600==0)
    check("wrong_gross_sale_fails_refund_target",1000-880==120 and 600-528==72)
    check("netted_refund_hides_gross_balances",120-72==48 and 48!=120)
    # Scope/unknown conditions are specified outcomes, not a tested runtime.
    expected_failures={"control_not_transferred":"ineligible","required_estimate_unknown":"unresolved",
        "defective_product_exchange":"outside_scope: warranty","unsupported_state_only_profile":"UNSUPPORTED_PROFILE_OPERATION",
        "credit_reuse":"reject without mutation","unadmitted_tax":"downstream unresolved, not zero"}
    source=ROOT/"docs/design/proposal/methods/sources/aasb15-compiled-dec2022.pdf"
    output={"scope":"deterministic documentary calculation; no domain runtime", "advances":paths,
        "state_only_bill":{"before":before,"after":after,"journal_lines":[]},
        "returns":{"opening":{"inventory":600,"equity":600},"events":book.events,"year1_profit":number(profit1),"year2_profit":number(profit2),"lifetime_profit":number(profit_total)},
        "specified_unexecuted_failure_contracts":expected_failures}
    (OUT/"customer-contract-cases.json").write_text(json.dumps(output,indent=2)+"\n")
    (OUT/"calculation-checks.json").write_text(json.dumps({"passed":all(x["passed"] for x in checks),"checks":checks,"count":len(checks)},indent=2)+"\n")
    manifest={"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "command":"python3 data/accounting-master/p17-completion-20261014/P17-04/check_customer_contracts.py",
        "python":platform.python_version(),"cpu_gpu":"CPU-only exact Fraction arithmetic; no numerical framework or GPU initialized",
        "seeds":"N/A; deterministic","data_version":"Synthetic cases specified before computation; retained AASB15 compilation 8 for selected rule support",
        "source_pdf_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "plan":"docs/plans/accounting-corporate-operation-repair-20261014.md","result":str((OUT/"result.md").relative_to(ROOT)),
        "wall_seconds":time.perf_counter()-started,"outputs":["customer-contract-cases.json","calculation-checks.json"]}
    (OUT/"calculation-run.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"passed":all(x["passed"] for x in checks),"checks":len(checks),"failed":[x["name"] for x in checks if not x["passed"]]}))
    if not all(x["passed"] for x in checks):
        raise SystemExit(1)


if __name__=="__main__":
    main()
