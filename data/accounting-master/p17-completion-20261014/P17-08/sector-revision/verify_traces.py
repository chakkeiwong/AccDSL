"""Independently check finite temporal, dependency and sector composition traces."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
start=time.perf_counter()
data=json.loads((OUT/"revision-traces.json").read_text())
checks=[]
def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok,detail=None):
    checks.append({"name":name,"passed":bool(ok),"detail":detail})
def equal(name,a,b):
    check(name,a==b,None if a==b else {"computed":a,"expected":b})
def time_of(value):
    d=datetime.fromisoformat(value.replace("Z","+00:00"))
    assert d.tzinfo is not None
    return d.astimezone(timezone.utc)
def result(status,selected=(),excluded=None,unresolved=(),values=None,reason=None):
    return {"status":status,"selected":sorted(selected),"excluded":excluded or {},"unresolved":sorted(unresolved),
            "values":values,"reason":reason,"commit_observation":"not_committed","additional_commit":False}
for pin in data["pins"]:
    check("pin:"+pin["path"],sha(ROOT/pin["path"])==pin["sha256"])
worlds={key:json.loads((ROOT/data[key]["path"]).read_text()) for key in ["book","bank_book"]}
for key,world in worlds.items():
    equal("world_hash:"+key,digest(world),data[key]["canonical_sha256"])
sources=data["sources"]
for key,s in sources.items():
    b=(ROOT/s["path"]).read_bytes()
    check("source_bytes:"+key,hashlib.sha256(b).hexdigest()==s["sha256"])
    check("synthetic_label:"+key,b.startswith(b"AUTHORED SYNTHETIC FIXTURE; NOT AN ISSUER DOCUMENT"))
    check("ingestion_receipt:"+key,s["ingestion_receipt_verified"] and bool(s["ingestion_receipt"]))
    if s["supersedes"]:
        check("supersession_target:"+key,s["supersedes"] in sources)
        equal("supersession_scope:"+key,s["context_key"],sources[s["supersedes"]]["context_key"])
    if s["public_at"] is not None:
        check("public_receipt:"+key,not s["byte_vintage_verified"] or bool(s["publication_receipt"]))
    if key in ["insurance-v1","insurance-v2"]:
        times=re.findall(r"2024-01-01T\d{2}:\d{2}:\d{2}Z",b.decode())
        equal("source_order:"+key,"before" if time_of(times[0])<time_of(times[1]) else "after",s["value"])

def insurance(order):
    # Reconstruct both histories from the conditional case's primitives.
    premium=F(70); recoveries_pv=F(33)/F("1.1")+F("36.3")/F("1.1")**2
    transferred_risk=F(5); original_cost=premium-recoveries_pv-transferred_risk
    recovery_component=F(30)*F(1,2) if order=="before" else F(0)
    csm=original_cost+recovery_component
    opening=recoveries_pv+transferred_risk+csm
    csm_after_one_year=csm*F("1.1")/2
    remaining=F(33)+F("2.5")+csm_after_one_year
    equity0=F(250)+opening-F(120)-F(130)
    equity1=F(173)+remaining-F("65.5")-F(71)
    terminal=F(100)+220-70-F(231)+F("69.3")
    return {k:str(v) for k,v in [("R_initial_asset",opening),("initial_equity",equity0),("year1_equity",equity1),("final_cash",terminal)]}
def bank(value):
    if value["original_risk_id"]!=value["sicr_baseline_id"] or not value["sicr_supported"]:
        raise ValueError("SICR_BASELINE_MISMATCH")
    loss=(F(121)-F("108.9"))/F("1.1")**2
    draw=F(1,2); joint_first=F(1,10);joint_second=F(1,10)
    allowance=(joint_first+joint_second)/draw*loss
    return {"allowance":str(allowance),"equity":str(F(20)-allowance),"original_risk_id":value["original_risk_id"]}

def select(q):
    candidates=q["candidate_ids"]
    if len(candidates)!=len(set(candidates)) or any(x not in sources for x in candidates):
        return result("rejected",reason="REQUEST_INVALID")
    if q.get("tampered_blob"):
        s=sources[q["tampered_blob"]]
        received=(ROOT/s["path"]).read_bytes()+b"\nchanged"
        if hashlib.sha256(received).hexdigest()!=s["sha256"]:
            return result("rejected",reason="SOURCE_HASH_MISMATCH")
    if q.get("baseline_binding_override") is not None:
        return result("rejected",reason="SICR_BASELINE_MISMATCH")
    eligible=[];excluded={};unresolved=[]
    for key in candidates:
        s=sources[key]
        if q["admission_mode"]=="investor_information" or q["information_cutoff"] is not None:
            cutoff=time_of(q["information_cutoff"])
            if s["public_at"] is None:
                unresolved.append(key+":public_time_unknown");continue
            if time_of(s["public_at"])>cutoff:
                excluded[key]="published_after_cutoff";continue
            if not s["byte_vintage_verified"]:
                unresolved.append(key+":byte_vintage_unverified");continue
        if q["admission_mode"]=="system_as_of":
            cutoff=time_of(q["system_as_of"])
            if time_of(s["ingested_at"])>cutoff:
                excluded[key]="ingested_after_cutoff";continue
            if q["layer"]=="accepted" and time_of(s["reviewed_at"])>cutoff:
                unresolved.append(key+":review_after_system_cutoff");continue
        if q["layer"]=="accepted" and time_of(s["reviewed_at"])>time_of(q["review_snapshot_at"]):
            unresolved.append(key+":review_after_snapshot");continue
        eligible.append(key)
    selected=set(eligible)
    for key in eligible:
        previous=sources[key]["supersedes"]
        seen={key}
        while previous is not None:
            if previous in seen:
                return result("rejected",reason="SUPERSESSION_CYCLE")
            if previous not in sources:
                return result("rejected",reason="SUPERSESSION_TARGET_MISSING")
            seen.add(previous)
            if previous in selected:
                selected.remove(previous);excluded[previous]="superseded"
            previous=sources[previous]["supersedes"]
    if len(selected)>1:
        unresolved.append("CONFLICTING_VERSIONS")
    if not selected and not unresolved:
        unresolved.append("no_eligible_input")
    if unresolved:
        return result("unresolved",selected,excluded,unresolved)
    if q["layer"]=="raw":
        return result("raw_available",selected,excluded)
    source=sources[next(iter(selected))]
    value=source["value"]
    if value is None:
        return result("unresolved",selected,excluded,
                      ["original_credit_baseline" if source["context_key"]=="bank-original-risk" else "treaty_order"])
    values=bank(value) if source["context_key"]=="bank-original-risk" else insurance(value)
    return result("conditional",selected,excluded,values=values)

def ancestors(root,graph):
    visited=set();active=set()
    def visit(key):
        if key not in graph:
            raise ValueError("DEPENDENCY_MISSING")
        if key in active:
            raise ValueError("DEPENDENCY_CYCLE")
        if key in visited:
            return
        active.add(key)
        for dep in graph[key]["deps"]:
            visit(dep)
        active.remove(key);visited.add(key)
    visit(root)
    return visited
def dependency(q):
    graph=deepcopy(data["dependency_graph"]);current=deepcopy(q["current_versions"])
    change=q["graph_changes"]
    if "remove" in change:
        del graph[change["remove"]]
    if change.get("cycle"):
        graph["insurance-membership"]["deps"]=["insurance-result"]
    if change.get("refresh"):
        for key in ["insurance-selection","insurance-measurement","insurance-result"]:
            graph[key]["version"]+="-new"
            current[key]=graph[key]["version"]
        graph["insurance-membership"]["version"]=current["insurance-membership"]
    try:
        closure=ancestors(q["root"],graph)
    except ValueError as e:
        return result(str(e)),[]
    # Independent breadth-first walk checks the declared DFS closure.
    pending=[q["root"]];breadth=set()
    while pending:
        key=pending.pop(0)
        if key not in breadth:
            breadth.add(key);pending.extend(graph[key]["deps"])
    equal("independent_closure:"+q["root"]+":"+str(change),sorted(closure),sorted(breadth))
    stale=sorted(k for k in closure if current.get(k)!=graph[k]["version"])
    return result("STALE_VIEW" if stale else "reusable",
        values=insurance("before") if not stale and q["root"]=="insurance-result" else None),stale

atomic=json.loads((ROOT/data["external_atomic"]["path"]).read_text())
computed=[]
for c in data["cases"]:
    q=c["request"];action=c["action"];stale=[]
    world_key="bank_book" if c["identity"]["entity"]=="Bank" else "book"
    world=worlds[world_key];before=canonical(world)
    equal("bound_before:"+c["id"],c["committed_world_before"],digest(world))
    if "book_hash" in q:
        equal("request_book_binding:"+c["id"],q["book_hash"],digest(world))
    if action=="select_and_assess":
        actual=select(q)
    elif action=="current_use":
        actual,stale=dependency(q)
    elif action=="frozen_explain":
        if q["requested_view"]!=q["frozen"]["view"]:
            actual=result("rejected",reason="FROZEN_VIEW_MISMATCH")
        else:
            stale=[k for k,v in q["frozen"]["dependency_versions"].items() if q["current_versions"].get(k)!=v]
            actual=result("historical_with_stale_warning" if stale else "historical",values=q["frozen"]["values"])
    elif action=="reading_revision":
        r=next(r for r in data["reading_versions"] if r["id"]==q["reading_id"])
        if q["mode"]=="frozen":
            check("old_reading_is_actual_error",r["value"]!=sources[r["source_id"]]["value"])
            actual=result("historical_error_not_current",values=insurance(r["value"]))
        else:
            equal("corrected_reading_source_faithful",r["value"],sources[r["source_id"]]["value"])
            actual=result("conditional",values=insurance(r["value"]))
    elif action=="correction_request":
        check("unsupported_correction_has_no_authority",q["treatment_authority"] is None)
        actual=result("unsupported",reason="TREATMENT_UNSUPPORTED")
    elif action in ["replay_existing","changed_retry"]:
        old=next(x for x in atomic["cases"] if x["id"]==q["external_case"])
        equal("exact_external_request:"+c["id"],q["request_ref"],old["candidate_request_ref"])
        equal("exact_external_result:"+c["id"],q["result_ref"],old["expected_result_ref"])
        r=atomic["record_registry"][q["result_ref"]["digest"]]["body"]
        equal("external_read_only:"+c["id"],old["before"],old["after"])
        equal("external_commit_observation:"+c["id"],r["commit_observation"],"not_committed")
        if action=="replay_existing":
            equal("replay_unchanged_current_world",digest(old["before"]),digest(world))
            check("exact_receipt_and_no_extra_commit",r["payload"]["original_receipt_ref"]==r["receipt_ref"] and not r["payload"]["additional_commit"])
            actual=result("replayed_original",reason="original_receipt_preserved")
        else:
            equal("conflict_code",old["expected_code"],"EVENT_ID_CONFLICT")
            equal("conflict_no_receipt",r["receipt_ref"],None)
            actual=result("rejected",reason="EVENT_ID_CONFLICT")
    else:
        raise AssertionError(action)
    expected=deepcopy(c["expected"])
    expected["selected"].sort();expected["unresolved"].sort()
    equal("semantic_result:"+c["id"],actual,expected)
    equal("book_unchanged:"+c["id"],canonical(world),before)
    equal("expected_after:"+c["id"],c["committed_world_after"],digest(world))
    check("no_additional_commit:"+c["id"],not actual["additional_commit"] and actual["commit_observation"]=="not_committed")
    computed.append({"id":c["id"],"result":actual,"stale_dependencies":stale})
equal("same_source_extraction_versions",len({r["source_id"] for r in data["reading_versions"]}),1)
equal("unchanged_ultimate_cash",insurance("before")["final_cash"],insurance("after")["final_cash"])
check("no_runtime_claim",not data["runtime_executed"])
equal("index_preserved",subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT),
      (ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes())
result_record={"passed":all(c["passed"] for c in checks),"check_count":len(checks),"checks":checks,"wall_seconds":time.perf_counter()-start}
(OUT/"exchange-checks.json").write_text(json.dumps(result_record,indent=2,default=str)+chr(10))
(OUT/"computed-traces.json").write_text(json.dumps(computed,indent=2)+chr(10))
print(json.dumps({"passed":result_record["passed"],"checks":len(checks),"cases":len(computed),
                  "failures":[c for c in checks if not c["passed"]]},default=str))
raise SystemExit(0 if result_record["passed"] else 1)
