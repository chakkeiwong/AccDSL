"""Exact documentary allocation and statement checks; no runtime implementation."""
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
CHECKS=[]


def check(name,actual,expected):
    CHECKS.append({"name":name,"passed":actual==expected,"actual":actual,"expected":expected})


def encode(x):
    if isinstance(x,F): return str(x)
    raise TypeError(type(x).__name__)


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def allocate(amount,weights,capacities):
    """Fixed pre-allocation carrying weights; exact saturation and redistribution."""
    assert len(weights)==len(capacities)
    assert amount>=0 and all(w>=0 for w in weights) and all(c>=0 for c in capacities)
    remaining=amount; given=[F(0)]*len(weights); trace=[]
    active=[i for i,c in enumerate(capacities) if c>0]
    while remaining>0 and active:
        denominator=sum(weights[i] for i in active)
        if denominator==0:
            return {"allocated":given,"residual":remaining,"status":"allocation_basis_unresolved","trace":trace}
        proposals={i:remaining*weights[i]/denominator for i in active}
        saturated=[i for i in active if proposals[i]>=capacities[i]-given[i]]
        trace.append({"remaining_before":remaining,"active":active.copy(),"proposals":proposals,"saturated":saturated})
        if not saturated:
            for i in active: given[i]+=proposals[i]
            remaining=F(0)
        else:
            for i in saturated:
                delta=capacities[i]-given[i]; given[i]+=delta; remaining-=delta
                active.remove(i)
    return {"allocated":given,"residual":remaining,"status":"allocated" if remaining==0 else "capacity_exhausted","trace":trace}


def integer_oracle(amount,weights,capacities):
    """Independent finite enumeration for the selected integral worked solutions."""
    target=min(amount,sum(capacities)); matches=[]
    for candidate in itertools.product(*(range(int(c)+1) for c in capacities)):
        candidate=tuple(map(F,candidate))
        if sum(candidate)!=target: continue
        uncapped=[i for i,(x,c) in enumerate(zip(candidate,capacities)) if x<c]
        if not uncapped:
            matches.append(candidate); continue
        ratios={candidate[i]/weights[i] for i in uncapped if weights[i]>0}
        if len(ratios)!=1 or any(weights[i]==0 and candidate[i]!=0 for i in uncapped): continue
        scale=next(iter(ratios))
        if all(x==min(c,scale*w) for x,c,w in zip(candidate,capacities,weights)):matches.append(candidate)
    return matches


def floor_value(measurements):
    values=[F(0)]
    for key,unavailable in [("fvlcd","not_measurable"),("viu","not_determinable")]:
        item=measurements.get(key,{"status":"missing"})
        if item["status"]=="measured": values.append(F(item["value"]))
        elif item["status"]!=unavailable: raise ValueError("measurement_unresolved:"+key)
    return max(values)


def main():
    started=datetime.now(timezone.utc).isoformat(); timer=time.perf_counter()
    measurements=[{"fvlcd":{"status":"measured","value":"55"},"viu":{"status":"not_determinable"}},
                  {"fvlcd":{"status":"measured","value":"5"},"viu":{"status":"not_determinable"}}]
    carrying=[F(60),F(40)]; floors=[floor_value(x) for x in measurements]
    capacities=[max(b-f,F(0)) for b,f in zip(carrying,floors)]
    unit_value=max(F(70),F(65)); requested=sum(carrying)+20-unit_value
    goodwill_loss=min(F(20),requested); non_goodwill=requested-goodwill_loss
    check("requested_loss",requested,F(50));check("goodwill_first",goodwill_loss,F(20))
    cases={}
    for name,amount,weights,caps,expected in [
        ("loss",non_goodwill,carrying,capacities,[F(5),F(25)]),
        ("nonbinding_loss",F(5),carrying,capacities,[F(3),F(2)]),
        ("capacity_stress",F(50),carrying,capacities,[F(5),F(35)]),
        ("reversal",F(34),[F(44),F(12)],[F(4),F(20)],[F(4),F(20)]),
        ("smaller_reversal",F(19),[F(44),F(12)],[F(4),F(20)],[F(4),F(15)]),
    ]:
        answer=allocate(amount,weights,caps); cases[name]={"request":amount,"weights":weights,"capacities":caps,**answer}
        check(name+":expected",answer["allocated"],expected)
        check(name+":sum",sum(answer["allocated"])+answer["residual"],amount)
        check(name+":capacity",all(F(0)<=v<=c for v,c in zip(answer["allocated"],caps)),True)
        check(name+":termination",len(answer["trace"])<=len(weights)+1,True)
        check(name+":independent_enumeration",integer_oracle(amount,weights,caps),[tuple(expected)])
    check("loss:floor_result",[b-x for b,x in zip(carrying,cases["loss"]["allocated"])],[F(55),F(15)])
    check("loss:allocated_total",goodwill_loss+sum(cases["loss"]["allocated"]),F(50))
    check("loss:closing_unit",sum(carrying)-sum(cases["loss"]["allocated"]),unit_value)
    check("stress:unallocated",cases["capacity_stress"]["residual"],F(10))
    cases["capacity_stress"]["admission"]="diagnostic injection only; measurement/perimeter/other-standard review required; no liability authorized"
    after_loss=[b-x for b,x in zip(carrying,cases["loss"]["allocated"])]
    depreciation=[b/5 for b in after_loss]; unimpaired_dep=[b/5 for b in carrying]
    before_reversal=[b-d for b,d in zip(after_loss,depreciation)]
    ceilings=[b-d for b,d in zip(carrying,unimpaired_dep)]
    check("depreciation:actual",depreciation,[F(11),F(3)])
    check("depreciation:counterfactual",unimpaired_dep,[F(12),F(8)])
    check("reversal:input_weights",before_reversal,cases["reversal"]["weights"])
    check("reversal:input_capacities",[c-b for c,b in zip(ceilings,before_reversal)],cases["reversal"]["capacities"])
    after_reversal=[b+x for b,x in zip(before_reversal,cases["reversal"]["allocated"])]
    check("reversal:counterfactual_cap",after_reversal,ceilings)
    check("reversal:recognized_increase",sum(cases["reversal"]["allocated"]),F(24))
    check("reversal:unrecognized_excess",F(90)-sum(after_reversal),F(10))
    check("reversal:next_year_depreciation",[v/4 for v in after_reversal],[F(12),F(8)])
    zero=allocate(F(5),[F(0),F(0)],[F(10),F(10)])
    check("zero_weight:unresolved",zero["status"],"allocation_basis_unresolved")
    check("zero_weight:no_equal_split",zero["allocated"],[F(0),F(0)])
    cases["zero_weight"]=zero
    fractional=allocate(F(1),[F(2),F(3)],[F(10),F(10)])
    check("nonintegral_exact_split",fractional["allocated"],[F(2,5),F(3,5)])
    cases["fractional_split"]=fractional
    missing=[]
    for key in ["fvlcd","viu"]:
        bad={**measurements[0],key:{"status":"missing"}}
        try: floor_value(bad)
        except ValueError as e: missing.append({"case":key,"status":str(e)})
    check("missing_measurements_rejected",len(missing),2)
    high_floor=floor_value({"fvlcd":{"status":"measured","value":"70"},"viu":{"status":"not_determinable"}})
    check("floor_above_cost:no_writeup_or_reduction",max(F(60)-high_floor,F(0)),F(0))
    # Explicit entries are checked against the independent allocation and depreciation paths.
    events=[
        {"date":"T0","name":"impair","lines":{"impairment_expense":50,"goodwill":-20,"impairment_A":-5,"impairment_B":-25}},
        {"date":"T0","name":"close","lines":{"impairment_expense":-50,"retained":50}},
        {"date":"T1","name":"depreciate","lines":{"depreciation_expense":14,"ad_A":-11,"ad_B":-3}},
        {"date":"T1","name":"reverse","lines":{"impairment_A":4,"impairment_B":20,"reversal_gain":-24}},
        {"date":"T1","name":"close","lines":{"depreciation_expense":-14,"reversal_gain":24,"retained":-10}},
    ]
    ledger=defaultdict(F,cash=F(80),ppe_A=F(60),ppe_B=F(40),goodwill=F(20),capital=F(-200))
    snapshots=[]
    for event in events:
        lines={k:F(v) for k,v in event["lines"].items()};event["lines"]=lines
        check(event["date"]+":"+event["name"]+":balance",sum(lines.values()),F(0))
        for k,v in lines.items():ledger[k]+=v
        check(event["date"]+":"+event["name"]+":trial_balance",sum(ledger.values()),F(0))
        if event["name"]=="close":
            values=[ledger["ppe_"+i]+ledger["ad_"+i]+ledger["impairment_"+i] for i in ["A","B"]]
            expected=after_loss if event["date"]=="T0" else after_reversal
            check(event["date"]+":independent_assets",values,expected)
            equity=-ledger["capital"]-ledger["retained"]
            check(event["date"]+":balance_sheet",ledger["cash"]+sum(values)+ledger["goodwill"],equity)
            check(event["date"]+":goodwill_not_restored",ledger["goodwill"],F(0))
            snapshots.append({"date":event["date"],"ledger":dict(ledger),"assets":values,"equity":equity})
    check("T0:equity",snapshots[0]["equity"],F(150));check("T1:equity",snapshots[1]["equity"],F(160))
    check("remaining_impairment_allowances",[-ledger["impairment_A"],-ledger["impairment_B"]],[F(1),F(5)])
    check("T0:indirect_cash",F(-50)+50,F(0));check("T1:indirect_cash",F(10)+14-24,F(0))
    check("direct_cash",sum(e["lines"].get("cash",F(0)) for e in events),F(0))
    check("equity_bridge",F(200)-50-14+24,F(160))
    adverse=[
        {"case":"one_pass_clipping","computed_allocation":[5,12],"lost_loss":13,"disposition":"reject; redistribution required"},
        {"case":"unconstrained_split","computed_allocation":[18,12],"A_closing":42,"A_floor":55,"disposition":"reject; floor breach"},
        {"case":"erase_all_original_allowances","PPE":86,"ceiling":80,"disposition":"reject; no-impairment depreciation history required"},
        {"case":"restore_goodwill_10","unit_total":90,"disposition":"reject; IAS36.124"},
        {"case":"time_passage_only","requested_reversal":24,"disposition":"not_admitted; IAS36.114/116 needs changed estimate"},
    ]
    check("adverse:lost_allocation",F(30)-5-12,F(13))
    check("adverse:floor_breach",F(60)-18<F(55),True)
    check("adverse:excess_reversal",F(100)-14-F(80),F(6))
    result={"schema":"documentary-impairment-cases.v1","numbers":"exact rational strings; debit-positive journals",
            "scope":"synthetic historical IAS36 cost model; no current entity admission, tax or runtime",
            "measurement_inputs":measurements,"unit_value":{"viu":70,"fvlcd":65,"T1_recoverable":90,"T1_reason":"supported changed future cash-flow estimates; authored"},
            "allocations":cases,"journals":events,"statements":snapshots,"missing_input_cases":missing,"adverse":adverse,
            "depreciation":depreciation,"unimpaired_depreciation":unimpaired_dep}
    elapsed=time.perf_counter()-timer
    (OUT/"impairment-cases.json").write_text(json.dumps(result,indent=2,default=encode)+"\n")
    report={"passed":all(c["passed"] for c in CHECKS),"check_count":len(CHECKS),"checks":CHECKS,"wall_seconds":elapsed}
    (OUT/"calculation-checks.json").write_text(json.dumps(report,indent=2,default=encode)+"\n")
    run={"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"started_utc":started,
         "wall_seconds":elapsed,"command":["python3",str(Path(__file__).resolve().relative_to(ROOT))],"environment":"system Python; fractions and standard library",
         "cpu_gpu_status":"CPU exact documentary calculations; no numerical framework or GPU initialized","random_seeds":"N/A; deterministic",
         "data_version":"synthetic impairment-cases.v1; retained original EU2023/1803 plus date corrigendum",
         "plan":"docs/plans/accounting-impairment-floors-20261014.md","result":str((OUT/"result.md").relative_to(ROOT)),
         "script_sha256":sha(Path(__file__)),"outputs":{p.name:sha(p) for p in [OUT/"impairment-cases.json",OUT/"calculation-checks.json"]}}
    (OUT/"calculation-run.json").write_text(json.dumps(run,indent=2)+"\n")
    print(json.dumps({"passed":report["passed"],"checks":len(CHECKS),"failed":[c["name"] for c in CHECKS if not c["passed"]]}))
    if not report["passed"]: raise SystemExit(1)


if __name__=="__main__": main()
