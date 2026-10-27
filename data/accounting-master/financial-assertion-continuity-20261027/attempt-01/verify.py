"""Diagnose exact state continuity before binding reports to economic histories."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime, timezone
import importlib.util
import json
import os
import platform
import resource
import subprocess
import sys
import time
import traceback

H=Path(__file__).resolve().parent
R=H.parents[2]
E=H.parent/"symbolic-path-composition-20261026/expected_path.py"
spec=importlib.util.spec_from_file_location("continuity_independent_path",E)
ep=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ep)


def substitute(value, values):
    if isinstance(value,(list,tuple)):
        if value and value[0]=="linear":
            return str(Q(value[2])+sum(Q(a)*values[k] for k,a in value[1]))
        if value and value[0]=="literal":
            return value[2]
        if value and value[0]=="all":
            return all(substitute(v,values) for v in value[1])
        if value and value[0] in ("le","lt","eq"):
            number=Q(substitute(value[1],values))
            return number<=0 if value[0]=="le" else number<0 if value[0]=="lt" else number==0
        return [substitute(v,values) for v in value]
    if isinstance(value,dict):
        return {k:substitute(v,values) for k,v in value.items()}
    return value


def canonical(value):
    return json.loads(json.dumps(value))


def states(steps):
    return [steps[0]["before"]]+[step["after"] for step in steps]


def continuous(prefix,suffix):
    for left,right in zip(prefix+suffix,(prefix+suffix)[1:]):
        if left["after"]!=right["before"]:
            raise ValueError("carried_state_changed_without_event")
    return True


def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120))
    attempt=sys.argv[1];assert attempt in ("01","02","03")
    A=H/("attempt-"+attempt);A.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat();start=time.monotonic()
    checks=[];cases=[];controls=[];pins={}
    def save(name,value):(A/name).write_text(json.dumps(value,indent=2)+chr(10))
    def ck(name,value):
        checks.append(dict(name=name,passed=bool(value)))
        if not value:raise AssertionError(name)
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,AssertionError,TypeError) as error:
            controls.append(dict(name=name,reason=str(error)));ck("reject:"+name,True)
        else:ck("reject:"+name,False)
    try:
        ck("cpu_hidden",os.environ.get("CUDA_VISIBLE_DEVICES")=="-1")
        B=H.parent/"symbolic-path-composition-20261026/attempt-01"
        ck("protected_status",json.loads((B/"verification.json").read_text())["status"]=="PASS")
        for name,digest in json.loads((B/"source-lock.json").read_text()).items():
            ck("baseline:"+name,sha256((R/name).read_bytes()).hexdigest()==digest);pins[name]=digest
        for p in [B/"cases.json",B/"verification.json",E,H/"verify.py",H/"contract.md",R/"docs/plans/accounting-financial-assertion-continuity-20261027.md"]:
            pins[str(p.relative_to(R))]=sha256(p.read_bytes()).hexdigest()
        save("source-lock.json",pins)
        for name in ("verify.py","contract.md"):(A/name).write_bytes((H/name).read_bytes())
        saved=[v for v in json.loads((B/"cases.json").read_text()) if v["chart"]=="alpha"]
        by={(v["mode"],v["right"],*v["actions"]):v for v in saved}
        for row in saved:
            mode,right=row["mode"],row["right"];a1,a2=row["actions"]
            label=mode+":"+str(right)+":"+a1+":"+a2
            expected=canonical(ep.steps(mode,right,a1,a2))
            ck(label+":independent_symbolic_steps",row["steps"]==expected)
            values={"I1":Q(5 if mode=="fixed" else 6),"I2":Q(5),"R":Q(7)}
            old=substitute(row["steps"],values)
            new=substitute(row["steps"],{**values,"R":Q(6)})
            os_,ns=states(old),states(new)
            changed=[]
            for i,(left,rightstate) in enumerate(zip(os_,ns)):
                ck(label+":receipt_dependence:"+str(i),(left==rightstate)==(i<3))
                ck(label+":balances:"+str(i),sum(Q(v) for v in left["book"].values())==sum(Q(v) for v in rightstate["book"].values())==0)
                if i>=3:
                    ck(label+":cash_delta:"+str(i),Q(left["book"]["cash"])-Q(rightstate["book"]["cash"])==1)
                    ck(label+":income_delta:"+str(i),Q(left["book"]["income"])-Q(rightstate["book"]["income"])==-1)
                    changed.append(i)
            ck(label+":pre_receipt_join",continuous(old[:2],new[2:]))
            ck(label+":join_equals_complete_world",old[:2]+new[2:]==new)
            for k in (3,4,5):reject(label+":post_receipt_join:"+str(k),lambda k=k:continuous(old[:k],new[k:]))
            other=substitute(by[(mode,not right,a1,a2)]["steps"],values)
            for i,(one,two) in enumerate(zip(os_,states(other))):
                ck(label+":right_changes_memory:"+str(i),one["book"]==two["book"] and one["memory"]["right"]!=two["memory"]["right"] and one!=two)
            accepted=all(all(step[phase].values()) for step in new for phase in ("pre","post"))
            cases.append(dict(case=label,old_receipt=7,corrected_world_receipt=6,coupons=[str(values["I1"]),str(values["I2"])],
                              changed_state_indices=changed,all_corrected_guards_pass=accepted,old_steps=old,corrected_world_steps=new))
        for label,expected_final,expected_fee in [("fixed:True:pay:pay","3/2","0"),("floating:True:draw:pay","1/4","1/4")]:
            row=next(v for v in cases if v["case"]==label)
            end=row["corrected_world_steps"][-1]["after"]
            ck(label+":valid_example",row["all_corrected_guards_pass"])
            ck(label+":independent_cash",end["book"]["cash"]==expected_final)
            ck(label+":independent_fee",end["book"]["fee_expense"]==expected_fee)
            ck(label+":one_receipt",[flow[4] for flow in end["flows"] if flow[1]=="operating_receipt"]==["6"])
        ck("contradictory_same_event_claims",not any(r==6 and r==7 for r in (6,7)))
        for path,digest in pins.items():ck("preserved:"+path,sha256((R/path).read_bytes()).hexdigest()==digest)
        summary=dict(status="PASS",symbolic_cases=len(saved),state_boundary_comparisons=len(saved)*7,
                     assertions=len(checks),continuity_refusals=len(controls),protected_files=len(pins),
                     scope="exact receipt/right carry diagnostic; no assertion truth or actor policy admission")
    except Exception:
        summary=dict(status="FAIL",assertions=len(checks),error=traceback.format_exc());save("failure.json",summary)
    finally:
        for name,value in [("verification.json",summary),("checks.json",checks),("controls.json",controls),("cases.json",cases)]:save(name,value)
        save("run-manifest.json",dict(command="env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 data/accounting-master/financial-assertion-continuity-20261027/verify.py "+attempt,
             git_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=R,text=True).strip(),environment=platform.python_version(),
             cpu_gpu="CPU; GPU intentionally hidden",started_utc=started,wall_seconds=time.monotonic()-start,seeds="N/A exact rational diagnostic",data_version="source-lock.json",
             plan="docs/plans/accounting-financial-assertion-continuity-20261027.md",result="data/accounting-master/financial-assertion-continuity-20261027/result.md",artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    return summary["status"]!="PASS"


if __name__=="__main__":sys.exit(main())
