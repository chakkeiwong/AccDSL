"""Exact two-date financial source selection without financial trace splicing."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime, timezone
from itertools import product
import importlib.util
import json
import os
import platform
import resource
import subprocess
import sys
import time
import traceback

H = Path(__file__).resolve().parent
R = H.parents[2]
spec = importlib.util.spec_from_file_location("own_revisable_joint_sources", H / "joint.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
fx = m.t.prior.load("financial_clock_fixtures", H.parent / "source-time-intervals-20261027/fixtures.py")
OLD = (7, "committed", "refined")
NEW = (6, "committed", "refined")
UNKNOWN = ("unresolved",)


def label(value):
    if value["status"] != "selected_conditional":
        return UNKNOWN
    s = value["scenario"]
    return (s["receipt"], s["family"], s["view"])


def fixture(clock, payload=None, disposition="assertion", supersedes=True, observation=False, inconsistent=False):
    base = fx.oldcases.base()
    head = fx.oldcases.add(base, "financial_family", None if disposition == "retraction" else payload or {"receipt":6,"family":"committed"},
                          supersedes=base["names"]["financial_family"] if supersedes else None,
                          when="2026-01-01T01:00:00Z", disposition=disposition)
    clocks = {head: {"access:Alice": clock}}
    if observation:
        oh = fx.oldcases.add(base, "observation_scheme", {"view":"coarse"},
                             supersedes=base["names"]["observation_scheme"], when="2026-01-01T01:00:00Z")
        clocks[oh] = {"access:Alice": fx.point("2026-01-02T12:00:00Z")}
    if inconsistent:
        clocks[head]["published"] = fx.point("2026-01-03T00:00:00Z")
    value = fx.convert(base, clocks, cutoffs={"system_asof":"2026-01-04T00:00:00Z"})
    return m.request(m.f.wire(value), "2026-01-03T00:00:00Z", "2026-01-03T00:00:00Z")


def inputs():
    for name, clock, expected in [
        ("before_both",fx.point("2026-01-01T12:00:00Z"),{(NEW,NEW)}),
        ("between",fx.point("2026-01-02T12:00:00Z"),{(OLD,NEW)}),
        ("after_both",fx.point("2026-01-03T12:00:00Z"),{(OLD,OLD)}),
        ("at_first",fx.point("2026-01-02T00:00:00Z"),{(NEW,NEW)}),
        ("just_after_first",fx.point("2026-01-02T00:00:00.0000001Z"),{(OLD,NEW)}),
        ("at_second",fx.point("2026-01-03T00:00:00Z"),{(OLD,NEW)}),
        ("interval",fx.interval("2026-01-01T12:00:00Z","2026-01-03T12:00:00Z"),{(OLD,OLD),(OLD,NEW),(NEW,NEW)}),
        ("unknown_access",fx.unknown(),{(OLD,OLD),(OLD,NEW),(NEW,NEW)})]:
        yield name, fixture(clock), expected
    between = fx.point("2026-01-02T12:00:00Z")
    yield "changed_right_assertion", fixture(between,payload={"receipt":7,"family":"mixed"}), {(OLD,(7,"mixed","refined"))}
    yield "concurrent_observation_correction", fixture(between,observation=True), {(OLD,(6,"committed","coarse"))}
    yield "late_retraction", fixture(between,disposition="retraction"), {(OLD,UNKNOWN)}
    yield "late_conflict", fixture(between,supersedes=False), {(OLD,UNKNOWN)}
    yield "inconsistent_clocks", fixture(between,inconsistent=True), set()


def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120))
    attempt = sys.argv[1]
    assert attempt in ("01","02","03")
    A = H / ("attempt-" + attempt)
    A.mkdir(exist_ok=False)
    start, started = time.monotonic(), datetime.now(timezone.utc).isoformat()
    checks, controls, cases, pins = [], [], [], {}

    def save(name,value):
        (A/name).write_text(json.dumps(value,indent=2)+chr(10))

    def ck(name,condition):
        checks.append(dict(name=name,passed=bool(condition)))
        if not condition:
            raise AssertionError(name)

    def refuse(name,fn):
        try:
            fn()
        except (ValueError,KeyError,TypeError,AssertionError) as err:
            controls.append(dict(name=name,reason=str(err)))
            ck("reject:"+name,True)
        else:
            ck("reject:"+name,False)

    try:
        ck("cpu_hidden",os.environ.get("CUDA_VISIBLE_DEVICES")=="-1")
        base = H.parent/"two-decision-source-views-20261027/attempt-01"
        ck("baseline_pass",json.loads((base/"verification.json").read_text())["status"]=="PASS")
        for name,digest in json.loads((base/"source-lock.json").read_text()).items():
            ck("baseline:"+name,sha256((R/name).read_bytes()).hexdigest()==digest)
            pins[name]=digest
        for path in list(base.glob("*.json"))+[H/"joint.py",H/"verify.py",H/"contract.md",H/"prepare_module.py",R/"docs/plans/accounting-joint-financial-source-20261027.md"]:
            pins[str(path.relative_to(R))]=sha256(path.read_bytes()).hexdigest()
        save("source-lock.json",pins)
        for name in ("joint.py","verify.py","contract.md"):
            (A/name).write_bytes((H/name).read_bytes())
        prior=json.loads((base/"cases.json").read_text())
        for ref in prior:
            result=m.evaluate(ref["input"],m.identity(ref["input"]))
            ck("fixed_subset:"+ref["case"],m.verify(result,m.identity(result),m.identity(ref["input"])))
            for key in ("tree","outcomes","supports","nodes","status","complete","remainder"):
                ck("fixed_subset:"+ref["case"]+":"+key,result[key]==ref["result"][key])
        plans=list(inputs())
        save("inputs-and-expectations.json",[dict(case=name,input=x,expected=sorted(want)) for name,x,want in plans])
        for name,x,want in plans:
            xid=m.identity(x)
            result=m.evaluate(x,xid)
            ck(name+":independent_tree",m.verify(result,m.identity(result),xid))
            ck(name+":pure",m.identity(x)==xid)
            actual={tuple(label(o) for o in pair) for pair in result["outcomes"]}
            ck(name+":authored_joint_pairs",actual==want)
            ck(name+":no_financial_policy",result["financial_policy_binding"]=="not_assessed_source_selection_only" and "candidates" not in result)
            prepared,_=m.prepare(x,xid)
            marginals=[]
            for stage,p in enumerate(prepared):
                marginal=m.t.enumerate_views(p)
                out,nodes=m.t.verify_tree(p,marginal["tree"])
                ck(name+":marginal_certificate:"+str(stage),nodes==marginal["nodes"])
                ck(name+":marginal_projection:"+str(stage),{m.identity(pair[stage]) for pair in result["outcomes"]}=={m.identity(o) for o in out})
                marginals.append(out)
            cart={tuple(label(o) for o in pair) for pair in product(*marginals)}
            if name=="interval":
                ck("cartesian_impossible_new_old",cart-actual=={(NEW,OLD)})
            cases.append(dict(case=name,input=x,result=result,expected=sorted(want),cartesian_extra=sorted(cart-actual)))
        base=next(v for v in cases if v["case"]=="between")
        x,res=base["input"],base["result"]
        xid=m.identity(x)
        cap=m.evaluate(x,xid,2)
        ck("cap_unresolved",cap["status"]=="unresolved_budget" and cap["tree"] is None)
        ck("cap_checked",m.verify(cap,m.identity(cap),xid))
        ck("cap_full_remainder",cap["remainder"]["request"]==x)
        save("cap-case.json",cap)
        for name,change in [
            ("drop_support",lambda z:z["supports"].pop()),
            ("drop_outcome",lambda z:z["outcomes"].pop()),
            ("false_feasible",lambda z:z.update(status="conditionally_feasible")),
            ("fake_policy_binding",lambda z:z.update(financial_policy_binding="evaluated")),
            ("insert_policy_population",lambda z:z.update(candidates=[])),
            ("change_scope",lambda z:z.update(scope="policy_binding")),
            ("wrong_method",lambda z:z.update(method_identity="0"*64))]:
            bad=cp(res);change(bad)
            refuse(name,lambda z=bad:m.verify(z,m.identity(z),xid))
        for flag in m.t.FLAGS:
            bad=cp(res);bad[flag]=True
            refuse("admission:"+flag,lambda z=bad:m.verify(z,m.identity(z),xid))
        def first_leaf(node):
            if node["kind"]=="leaf":return node
            for child in node.get("children",[]):
                found=first_leaf(child)
                if found is not None:return found
        bad=cp(res);first_leaf(bad["tree"])["outcomes"].reverse()
        refuse("rewrite_first_financial_view",lambda:m.verify(bad,m.identity(bad),xid))
        bad=cp(cap);bad["remainder"]["request"]["second_decision_at"]="2026-01-04T00:00:00Z"
        refuse("change_capped_question",lambda:m.verify(bad,m.identity(bad),xid))
        badx=cp(x);badx["second_decision_at"]=x["original"]["request"]["decision_at"]
        refuse("unordered_decisions",lambda:m.evaluate(badx,m.identity(badx)))
        badx=cp(x);badx["second_effective_at"]="2025-12-31T00:00:00Z"
        refuse("backward_effective_cutoff",lambda:m.evaluate(badx,m.identity(badx)))
        refuse("stale_external_request",lambda:m.evaluate(x,"0"*64))
        for path,digest in pins.items():ck("preserved:"+path,sha256((R/path).read_bytes()).hexdigest()==digest)
        summary=dict(status="PASS",prior_cases=len(prior),new_cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),
                     scope="joint financial and observation source selection; financial policy and economic-history continuity unassessed")
    except Exception:
        summary=dict(status="FAIL",error=traceback.format_exc(),assertions=len(checks));save("failure.json",summary)
    finally:
        for name,value in [("verification.json",summary),("checks.json",checks),("controls.json",controls),("cases.json",cases)]:save(name,value)
        save("run-manifest.json",dict(command="env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 data/accounting-master/joint-financial-source-20261027/verify.py "+attempt,
             git_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=R,text=True).strip(),environment=platform.python_version(),
             cpu_gpu="CPU; GPU intentionally hidden",started_utc=started,wall_seconds=time.monotonic()-start,seeds="N/A exact finite comparisons",
             data_version="source-lock.json",plan="docs/plans/accounting-joint-financial-source-20261027.md",
             result="data/accounting-master/joint-financial-source-20261027/result.md",artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    return summary["status"]!="PASS"


if __name__=="__main__":sys.exit(main())
