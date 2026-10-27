"""Verify explicit world assumptions against protected complete financial rows."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,os,platform,resource,subprocess,sys,time,traceback

H=Path(__file__).resolve().parent;R=H.parents[2]
s=importlib.util.spec_from_file_location("own_financial_world_binding",H/"binding.py")
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
fs=m.j.t.prior.load("world_source_fixtures",H.parent/"joint-financial-source-20261027/verify.py")


def declaration(family,kind="same_event_receipt_correction",head=None):
    if kind=="same_event_receipt_correction":
        registry=family["input"]["original"]["registry"]
        if head is None:
            entries=[h for h,r in registry.items() if r.get("slot")=="financial_family" and r["disposition"]=="assertion"]
            ancestors={registry[h]["supersedes"] for h in entries}
            head=next(h for h in entries if h not in ancestors)
        world=cp(registry[head]["payload"])
    else:head=world=None
    return dict(profile=m.PROFILE,input_sha256=family["input_sha256"],interpretation=kind,
                corrected_financial_head=head,world=world,provenance="supplied_synthetic_assumption_not_source_admission")


def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120));attempt=sys.argv[1];assert attempt in ("01","02","03")
    A=H/("attempt-"+attempt);A.mkdir(exist_ok=False);start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    checks=[];controls=[];cases=[];pins={}
    def save(name,value):(A/name).write_text(json.dumps(value,indent=2)+chr(10))
    def ck(name,value):
        checks.append(dict(name=name,passed=bool(value)))
        if not value:raise AssertionError(name)
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,TypeError,AssertionError) as error:
            controls.append(dict(name=name,reason=str(error)));ck("reject:"+name,True)
        else:ck("reject:"+name,False)
    try:
        ck("cpu_hidden",os.environ.get("CUDA_VISIBLE_DEVICES")=="-1")
        B=H.parent/"joint-financial-source-20261027/attempt-01"
        ck("source_pass",json.loads((B/"verification.json").read_text())["status"]=="PASS")
        e=m.j.d.b.Evidence()
        for name,digest in {**e.dependencies,**e.method_files,**json.loads((B/"source-lock.json").read_text())}.items():
            ck("protected:"+name,sha256((R/name).read_bytes()).hexdigest()==digest);pins[name]=digest
        for p in list(B.glob("*.json"))+[H/"binding.py",H/"verify.py",H/"contract.md",R/"docs/plans/accounting-financial-source-world-binding-20261027.md"]:
            pins[str(p.relative_to(R))]=sha256(p.read_bytes()).hexdigest()
        save("source-lock.json",pins)
        for name in ("binding.py","verify.py","contract.md"):(A/name).write_bytes((H/name).read_bytes())
        saved={v["case"]:v["result"] for v in json.loads((B/"cases.json").read_text())}
        plans=[]
        for name in ["before_both","between","after_both","at_first","just_after_first","at_second","interval","unknown_access","concurrent_observation_correction","changed_right_assertion","late_conflict","late_retraction","inconsistent_clocks"]:
            family=saved[name]
            expected="unresolved_rights_change" if name=="changed_right_assertion" else "unresolved_source_family" if name in ("late_conflict","late_retraction") else "inconsistent_clocks" if name=="inconsistent_clocks" else "conditional_fixed_world"
            plans.append((name,family,declaration(family),expected))
        cap=json.loads((B/"cap-case.json").read_text())
        plans.append(("temporal_cap",cap,declaration(cap),"unresolved_temporal_family"))
        for kind in ("unknown","actual_amendment"):
            plans.append((kind,saved["between"],declaration(saved["between"],kind),"unresolved_interpretation"))
        # Declare the original financial head as the world: a selected correction
        # outside its lineage is retained but cannot silently be explained away.
        family=saved["between"];registry=family["input"]["original"]["registry"]
        oldhead=next(h for h,r in registry.items() if r.get("slot")=="financial_family" and r["supersedes"] is None)
        plans.append(("uncovered_correction",family,declaration(family,head=oldhead),"unresolved_interpretation_coverage"))
        # Opposite correction and unchanged restatement both declare receipt 7.
        for name,receipt in [("reverse_receipt_correction",6),("unchanged_restatement",7)]:
            b=fs.fx.oldcases.base()
            if receipt==6:
                old=b["names"]["financial_family"]
                record=b["registry"][old]
                # Rebuild the synthetic baseline with receipt 6 through the fixture API.
                del b["registry"][old]
                h=fs.fx.oldcases.add(b,"financial_family",{"receipt":6,"family":"committed"},text="Synthetic original receipt6.")
                b["names"]["financial_family"]=h
            head=fs.fx.oldcases.add(b,"financial_family",{"receipt":7,"family":"committed"},supersedes=b["names"]["financial_family"],when="2026-01-01T01:00:00Z",text="Synthetic corrected receipt7.")
            v=fs.fx.convert(b,{head:{"access:Alice":fs.fx.point("2026-01-02T12:00:00Z")}},cutoffs={"system_asof":"2026-01-04T00:00:00Z"})
            x=m.j.request(m.j.f.wire(v),"2026-01-03T00:00:00Z","2026-01-03T00:00:00Z")
            family=m.j.evaluate(x,m.identity(x))
            plans.append((name,family,declaration(family),"conditional_fixed_world"))
        prior=json.loads((H.parent/"two-decision-source-views-20261027/attempt-01/cases.json").read_text())[0]["input"]
        same=m.j.evaluate(prior,m.identity(prior));plans.append(("same_financial_head",same,declaration(same),"conditional_fixed_world"))
        save("inputs-and-expectations.json",[dict(case=n,family=f,declaration=d,expected=status) for n,f,d,status in plans])
        populations={}
        for name,family,d,status in plans:
            fid,did,xid=m.identity(family),m.identity(d),family["input_sha256"]
            result=m.evaluate(family,fid,xid,d,did,e)
            ck(name+":status",result["status"]==status)
            ck(name+":independent",m.verify(result,m.identity(result),family,fid,xid,d,did,e))
            ck(name+":pure",fid==m.identity(family) and did==m.identity(d))
            ck(name+":no_policy",result["financial_policy"]=="not_assessed_no_actor_message_binding" and "candidates" not in result)
            if status=="conditional_fixed_world":
                key=m.identity(d["world"])
                if key in populations:ck(name+":same_world_same_rows",result["financial_row_ids"]==populations[key])
                populations[key]=result["financial_row_ids"]
                ck(name+":rows_present",bool(result["financial_row_ids"]))
            else:ck(name+":no_rows",result["financial_row_ids"] is None)
            cases.append(dict(case=name,result=result))
        name,family,d,status=next(p for p in plans if p[0]=="between")
        res=next(v["result"] for v in cases if v["case"]==name);fid,did,xid=m.identity(family),m.identity(d),family["input_sha256"]
        for label,change in [("drop_row",lambda q:q["financial_row_ids"].pop()),("duplicate_row",lambda q:q["financial_row_ids"].append(q["financial_row_ids"][0])),
                             ("drop_support",lambda q:q["source_supports"].pop()),("rewrite_source_pair",lambda q:q["selected_source_pairs"][0].reverse()),
                             ("fake_policy",lambda q:q.update(financial_policy="evaluated")),("add_policy_population",lambda q:q.update(candidates=[])),
                             ("fake_world",lambda q:q["world_assumption"].update(receipt=7))]:
            bad=cp(res);change(bad);reject(label,lambda z=bad:m.verify(z,m.identity(z),family,fid,xid,d,did,e))
        for flag in m.FLAGS:
            bad=cp(res);bad[flag]=True;reject("admission:"+flag,lambda z=bad:m.verify(z,m.identity(z),family,fid,xid,d,did,e))
        bad=cp(d);bad["world"]["receipt"]=7
        reject("head_world_mismatch",lambda:m.evaluate(family,fid,xid,bad,m.identity(bad),e))
        bad=cp(d);bad["provenance"]="actual_truth"
        reject("truth_admission",lambda:m.evaluate(family,fid,xid,bad,m.identity(bad),e))
        reject("stale_declaration",lambda:m.evaluate(family,fid,xid,d,"0"*64,e))
        reject("stale_result",lambda:m.verify(res,"0"*64,family,fid,xid,d,did,e))
        reject("stale_family",lambda:m.evaluate(family,"0"*64,xid,d,did,e))
        for name,family,d,status in plans:
            if status=="conditional_fixed_world":continue
            bad=cp(next(v["result"] for v in cases if v["case"]==name));bad.update(status="conditional_fixed_world",financial_row_ids=res["financial_row_ids"])
            reject(name+":false_binding",lambda z=bad,f=family,dec=d:m.verify(z,m.identity(z),f,m.identity(f),f["input_sha256"],dec,m.identity(dec),e))
        for path,digest in pins.items():ck("preserved:"+path,sha256((R/path).read_bytes()).hexdigest()==digest)
        summary=dict(status="PASS",cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),
                     bound=sum(v["result"]["status"]=="conditional_fixed_world" for v in cases),worlds=len(populations),
                     scope="explicit synthetic same-event receipt world; no actor policy or actual truth")
    except Exception:
        summary=dict(status="FAIL",error=traceback.format_exc(),assertions=len(checks));save("failure.json",summary)
    finally:
        for name,value in [("verification.json",summary),("checks.json",checks),("controls.json",controls),("cases.json",cases)]:save(name,value)
        save("run-manifest.json",dict(command="env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 data/accounting-master/financial-source-world-binding-20261027/verify.py "+attempt,
             git_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu="CPU; GPU intentionally hidden",
             started_utc=started,wall_seconds=time.monotonic()-start,seeds="N/A exact finite comparison",data_version="source-lock.json",
             plan="docs/plans/accounting-financial-source-world-binding-20261027.md",result="data/accounting-master/financial-source-world-binding-20261027/result.md",artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    return summary["status"]!="PASS"


if __name__=="__main__":sys.exit(main())
