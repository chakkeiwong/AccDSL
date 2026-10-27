"""One bounded deterministic specification diagnostic, not an accounting engine."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
started = time.monotonic()
MUTANT_MODE = sys.argv[1:] == ["--mutant-probe"]
if sys.argv[1:] and not MUTANT_MODE:
    raise SystemExit("usage: arithmetic-check.py [--mutant-probe]")
case = json.load(sys.stdin) if MUTANT_MODE else json.loads((ROOT / "fixtures.json").read_text())
register = json.loads((ROOT / "source-register.json").read_text())
checks = []


def check(label, actual, expected):
    ok = actual == expected
    checks.append({"check": label, "pass": ok, "actual": str(actual), "expected": str(expected)})
    if not ok:
        if MUTANT_MODE:
            print(json.dumps({"status": "INVARIANT_FAILURE", "failure": checks[-1],
                              "prior_checks_passed": len(checks)-1}))
            raise SystemExit(3)
        raise AssertionError(checks[-1])


def balance(entries, through="9999-12-31"):
    out = defaultdict(F)
    for event in entries:
        if event["date"] > through:
            continue
        for line in event["lines"]:
            out[line["account"]] += F(line["amount"]) * (1 if line["side"] == "debit" else -1)
    return out


for sid, spec in case.items():
    if not isinstance(spec, dict) or "journals" not in spec:
        continue
    for entry in spec["journals"]:
        sums = [sum((F(x["amount"]) for x in entry["lines"] if x["side"] == side), F(0)) for side in ("debit", "credit")]
        check(f"{sid}:{entry['event']} conservation", sums[0], sums[1])
        check(f"{sid}:{entry['event']} positive lines", all(F(x["amount"]) > 0 for x in entry["lines"]), True)
    check(f"{sid} dated order", [x["date"] for x in spec["journals"]], sorted(x["date"] for x in spec["journals"]))

# Independently value unpaid future cash flows at each date, rather than using
# the journal-generation helper or only checking debit/credit conservation.
l=case["L01"]; r=F(l["rate"]); payments=list(map(F,l["payments"]))
pv=sum((p/(1+r)**i for i,p in enumerate(payments,1)),F(0))
check("L01 initial present value",pv,F(l["initial_pv"]))
for i,row in enumerate(l["schedule"],1):
    remaining=sum((p/(1+r)**j for j,p in enumerate(payments[i:],1)),F(0))
    opening=sum((p/(1+r)**j for j,p in enumerate(payments[i-1:],1)),F(0))
    b=balance(l["journals"],f"{row['year']}-12-31")
    check(f"L01 {row['year']} opening PV",opening,F(row["opening"]))
    check(f"L01 {row['year']} interest",opening*r,F(row["interest"]))
    check(f"L01 {row['year']} closing PV",remaining,F(row["closing"]))
    check(f"L01 {row['year']} journal liability",-b["lease_liability"],remaining)
    check(f"L01 {row['year']} independent ROU",b["rou_cost"]+b["rou_accumulated_depreciation"],pv*(1-F(i,2)))
    check(f"L01 {row['year']} stated ROU",F(row["rou"]),pv*(1-F(i,2)))
    check(f"L01 {row['year']} annual expense",pv/2+opening*r,F(row["expense"]))
    check(f"L01 {row['year']} cash effects",b["cash"],-sum(payments[:i]))
    check(f"L01 {row['year']} net assets equals liability minus expenses",b["rou_cost"]+b["rou_accumulated_depreciation"]+b["cash"],-b["lease_liability"]-b["interest_expense"]-b["depreciation_expense"])
check("L01 lifetime interest",balance(l["journals"])["interest_expense"],sum(payments)-pv)

m=case["L02"]; mr=F(m["revised_rate"]); mp=list(map(F,m["payments"]))
mpv=sum((p/(1+mr)**i for i,p in enumerate(mp,1)),F(0))
check("L02 revised PV",mpv,F(m["revised_pv"]))
check("L02 liability adjustment",mpv-F(m["old_liability"]),F(m["liability_adjustment"]))
new_rou=F(m["old_rou"])+mpv-F(m["old_liability"])
check("L02 revised ROU",new_rou,F(m["revised_rou"]))
modification_balance=balance(m["journals"],m["effective"])
check("L02 modification-date liability",-modification_balance["lease_liability"],mpv)
check("L02 modification-date ROU",modification_balance["rou_cost"]+modification_balance["rou_accumulated_depreciation"],new_rou)
for i,row in enumerate(m["schedule"],1):
    opening=sum((p/(1+mr)**j for j,p in enumerate(mp[i-1:],1)),F(0))
    remaining=sum((p/(1+mr)**j for j,p in enumerate(mp[i:],1)),F(0))
    b=balance(m["journals"],f"{row['year']}-12-31")
    check(f"L02 {row['year']} opening PV",opening,F(row["opening"]))
    check(f"L02 {row['year']} interest",opening*mr,F(row["interest"]))
    check(f"L02 {row['year']} closing PV",remaining,F(row["closing"]))
    check(f"L02 {row['year']} liability journals",-b["lease_liability"],remaining)
    check(f"L02 {row['year']} remaining ROU",b["rou_cost"]+b["rou_accumulated_depreciation"],new_rou*(1-F(i,2)))
    check(f"L02 {row['year']} stated ROU",F(row["rou"]),new_rou*(1-F(i,2)))
    check(f"L02 {row['year']} cash effects",b["cash"],-F(121)-sum(mp[:i]))
mb=balance(m["journals"])
check("L02 total cash",-mb["cash"],F(409))
check("L02 lifetime expense equals cash",mb["interest_expense"]+mb["depreciation_expense"],-mb["cash"])

for name in ["T01","T02"]:
    t=case[name]; cost=F(t["cost"]); dep=F(t["book_depreciation"]); profit=F(t["pretax_book_profit"])
    previous_dtl=F(0); cum_deductions=F(0); current_total=F(0); expense_total=F(0)
    for i,row in enumerate(t["schedule"]):
        year=row["year"]; deduction=F(row["tax_depreciation"]);cum_deductions+=deduction
        carrying=cost-dep*(i+1); taxbase=cost-cum_deductions
        taxable=profit+dep-deduction; current=taxable*F(t["current_rates"][i]); dtl=(carrying-taxbase)*F(t["reversal_rates"][i])
        deferred=dtl-previous_dtl; previous_dtl=dtl
        current_total+=current;expense_total+=current+deferred
        b=balance(t["journals"],f"{year}-12-31")
        for field,actual in [("carrying_amount",carrying),("tax_base",taxbase),("dtl",dtl),("taxable_profit",taxable),("current_tax",current),("deferred_expense",deferred),("total_tax_expense",current+deferred)]:
            check(f"{name} {year} independently derived {field}",actual,F(row[field]))
        check(f"{name} {year} journal DTL",-b["dtl"],dtl)
        check(f"{name} {year} book asset",b["ppe_cost"]+b["ppe_accumulated_depreciation"],carrying)
        check(f"{name} {year} unpaid current tax",-b["current_tax_payable"],current)
        check(f"{name} {year} cumulative current expense",b["current_tax_expense"],current_total)
        check(f"{name} {year} cumulative total expense",b["current_tax_expense"]+b["deferred_tax_expense"],expense_total)
        settled=balance(t["journals"],f"{year+1}-03-31")
        check(f"{name} {year} next-March payable clears",settled["current_tax_payable"],F(0))
        check(f"{name} {year} cash equals purchase and cumulative tax",settled["cash"],-cost-current_total)
    final=balance(t["journals"])
    check(f"{name} final DTL reverses",final["dtl"],F(0))
    check(f"{name} lifetime current equals total tax",final["current_tax_expense"],expense_total)
check("T02 2025 current stays at old rate",F(case["T02"]["schedule"][1]["current_tax"]),F(100))
check("T02 rate-only difference",F(case["T02"]["schedule"][1]["dtl"])-F(case["T01"]["schedule"][1]["dtl"]),F(15))

t=case["T06"]
for row in t["schedule"]:
    b=balance(t["journals"],row["date"])
    dta=(F(row["liability"])-F(t["tax_base_liability"]))*F(t["rate"])
    dtl=(F(row["rou"])-F(t["tax_base_rou"]))*F(t["rate"])
    check(f"T06 {row['date']} DTA from liability tax base",dta,F(row["dta"]))
    check(f"T06 {row['date']} DTL from ROU tax base",dtl,F(row["dtl"]))
    check(f"T06 {row['date']} gross journal DTA",b["dta"],dta)
    check(f"T06 {row['date']} gross journal DTL",-b["dtl"],dtl)
check("T06 year1 deferred benefit",balance(t["journals"],"2024-12-31")["deferred_tax_expense"],-F(5,4))
check("T06 final deferred expense reverses",balance(t["journals"])["deferred_tax_expense"],F(0))
check("T03 potential versus recognition distinction",F(case["T03"]["unused_loss"])*F(case["T03"]["rate"]),F(case["T03"]["unrecognized_potential"]))
check("T03 no unsupported recognized DTA",F(case["T03"]["recognized_dta"]),F(0))

if MUTANT_MODE:
    print(json.dumps({"status": "PASS", "checks": len(checks)}))
    raise SystemExit(0)


def probe(payload):
    """Execute this same oracle on supplied fixture bytes, with no report writes."""
    result=subprocess.run([sys.executable,str(Path(__file__).resolve()),"--mutant-probe"],
                          input=json.dumps(payload),text=True,capture_output=True,timeout=15)
    try:
        outcome=json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError({"unrelated_probe_error":result.stderr,"returncode":result.returncode}) from error
    return result.returncode,outcome,result.stderr


baseline_code,baseline_outcome,baseline_stderr=probe(deepcopy(case))
check("unchanged copied fixtures pass same probe",(baseline_code,baseline_outcome["status"],baseline_stderr),(0,"PASS",""))
negative=case["negative_controls"]
mutant_results=[]
mutant_dir=ROOT/"mutants"
mutant_dir.mkdir(exist_ok=True)
for n in negative:
    broken=deepcopy(case)
    if n["id"]=="N01":
        event=next(e for e in broken["L01"]["journals"] if e["event"]=="interest-2025")
        wrong=F(broken["L01"]["initial_pv"])*F(broken["L01"]["rate"])
        for line in event["lines"]:
            line["amount"]=str(wrong)
        expected_invariant="L01 2025 journal liability"
        mutation="Both balanced second-year interest legs use initial liability210*10%=21 instead of remaining-liability interest."
    elif n["id"]=="N02":
        spec=broken["L02"]
        wrong=sum((F(p)/(1+F(broken["L01"]["rate"]))**i for i,p in enumerate(spec["payments"],1)),F(0))
        event=next(e for e in spec["journals"] if e["event"]=="modify")
        for line in event["lines"]:
            line["amount"]=str(wrong-F(spec["old_liability"]))
        expected_invariant="L02 modification-date liability"
        mutation="Both balanced modification legs use old10% discounting while contract facts retain revised20%."
    elif n["id"]=="N03":
        event=next(e for e in broken["T01"]["journals"] if e["event"]=="deferred-2024")
        for line in event["lines"]:
            line["side"]="credit" if line["side"]=="debit" else "debit"
        expected_invariant="T01 2024 journal DTL"
        mutation="Reverse debit/credit sides of first-year deferred-tax entry; amounts stay positive and balanced."
    elif n["id"]=="N04":
        event=next(e for e in broken["T01"]["journals"] if e["event"]=="deferred-2024")
        for line in event["lines"]:
            line["amount"]=str(F(line["amount"])/(1+F(1,10)))
        expected_invariant="T01 2024 journal DTL"
        mutation="Discount both balanced first-year deferred-tax journal legs by an arbitrary10% one-year factor."
    elif n["id"]=="N05":
        broken["T06"]["journals"]=[e for e in broken["T06"]["journals"] if e["event"]!="lease-tax-recognize"]
        expected_invariant="T06 2024-01-01 gross journal DTA"
        mutation="Omit the balanced initial gross DTA/DTL recognition event because its net amount is zero."
    else:
        raise AssertionError("unimplemented negative control "+n["id"])
    # Each mutant must remain balanced: otherwise a trivial conservation error
    # would not test the economic/tax invariant the mutation is intended to probe.
    conserved=all(sum(F(x["amount"])*(1 if x["side"]=="debit" else -1) for x in e["lines"])==0
                  for s in broken.values() if isinstance(s,dict) and "journals" in s for e in s["journals"])
    check(n["id"]+" defective journals still balance",conserved,True)
    path=mutant_dir/(n["id"]+".json")
    path.write_text(json.dumps(broken,indent=2)+"\n")
    code,outcome,stderr=probe(broken)
    check(n["id"]+" same oracle rejects payload",(code,outcome.get("status"),stderr),(3,"INVARIANT_FAILURE",""))
    check(n["id"]+" targeted invariant fails",outcome["failure"]["check"],expected_invariant)
    mutant_results.append({"id":n["id"],"defect":n["defect"],"mutation":mutation,
                           "payload":str(path.relative_to(ROOT)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                           "journal_conservation_passed":conserved,"probe_returncode":code,
                           "outcome":outcome})

for source in register["sources"]:
    for file in source["files"]:
        p=ROOT/file["path"];raw=p.read_bytes()
        check(source["id"]+" hash "+p.suffix,hashlib.sha256(raw).hexdigest(),file["sha256"])
        if p.suffix==".pdf":check(source["id"]+" PDF magic",raw[:5],b"%PDF-")
    text=(ROOT/source["files"][1]["path"]).read_text()
    # split only physical newline, preserving form feeds used for PDF pages.
    lines=text.split("\n")
    for anchor in source["anchors"]:
        check(source["id"]+" paragraph "+anchor["paragraph"]+" exact located anchor",lines[anchor["text_line"]-1].lstrip("\f").strip(),anchor["anchor"])
        prefix="\n".join(lines[:anchor["text_line"]-1])+"\n"
        raw_line=lines[anchor["text_line"]-1]
        physical_page=prefix.count("\f")+raw_line[:len(raw_line)-len(raw_line.lstrip("\f"))].count("\f")+1
        check(source["id"]+" paragraph "+anchor["paragraph"]+" physical PDF page",physical_page,anchor["pdf_page"])

report={"status":"PASS","checks":len(checks),"negative_controls_detected":len(mutant_results),"negative_control_baseline":baseline_outcome,"negative_control_results":mutant_results,"purpose":"bounded author arithmetic/source-integrity diagnostic; not runtime or treatment acceptance",
 "run_manifest":{"utc":datetime.now(timezone.utc).isoformat(),"command":"python3 arithmetic-check.py","python":sys.version,"executable":sys.executable,"platform":platform.platform(),"cpu_gpu":"standard-library CPU arithmetic only; no GPU discovery or library import","random_seeds":"N/A deterministic Fraction arithmetic","git_commit":"N/A isolated /tmp preparation; original worktree not modified","data_version":"fixtures.json + source-register.json pinned below","plan":"PLAN.md","result":"arithmetic-report.json","wall_seconds":time.monotonic()-started},
 "inputs":[{"path":p,"sha256":hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in ["fixtures.json","source-register.json","arithmetic-check.py"]],
 "decision":{"decision":"candidate specification arithmetic/source integrity passes","primary":"independent PV/tax-base/reversal equations agree with stated journal consequences","veto":"none in this bounded diagnostic","main_uncertainty":"actual contract, rate, tax-law and recoverability evidence; complete domain methods and framework applicability","next":"cross-review then integrate proposed P17 inputs under stopped-master rules","not_concluded":"product correctness, tax-law validity, professional acceptance, full P17 completion or current IFRS compliance"},"details":checks}
(ROOT/"arithmetic-report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"status":report["status"],"checks":len(checks),"negative_controls_detected":len(negative),"report":"arithmetic-report.json"}))
