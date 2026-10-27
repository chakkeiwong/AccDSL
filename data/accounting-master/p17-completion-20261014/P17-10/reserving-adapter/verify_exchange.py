"""Independent finite evidence checks, not execution of an adapter."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time
import jsonschema

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def fraction(x):
    if x is None: return None
    v=F(int(x["n"]),int(x["d"]))
    assert str(v.numerator)==x["n"] and str(v.denominator)==x["d"]
    return v
def refs(x):
    if isinstance(x,dict):
        if set(x)=={"kind","schema","digest"}: yield x
        else:
            for y in x.values(): yield from refs(y)
    elif isinstance(x,list):
        for y in x: yield from refs(y)

def main():
    started=time.perf_counter()
    data=json.loads((OUT/"portable-exchanges.json").read_text())
    schemas=json.loads((OUT/"record-schemas.json").read_text())["bodies"]
    records=data["records"]; checks=[]
    def check(name,ok,detail=None):
        checks.append({"name":name,"passed":bool(ok),"detail":detail})
    def body(r):
        item=records[r["digest"]]
        assert item["kind"]==r["kind"] and item["schema"]==r["schema"]
        return item["body"]
    for digest,r in records.items():
        errors=list(jsonschema.Draft202012Validator(schemas[r["kind"]]).iter_errors(r["body"]))
        check("schema:"+r["key"],not errors,[e.message for e in errors])
        computed=hashlib.sha256(("accdsl.portable.v1/"+r["schema"]).encode()+b"\0"+canon(r)).hexdigest()
        check("digest:"+r["key"],computed==digest)
        wanted={canon(x) for x in refs(r["body"])}
        check("dependencies:"+r["key"],wanted=={canon(x) for x in r["dependencies"]})
        check("closure:"+r["key"],all(x["digest"] in records for x in refs(r)))
    for digest,r in data["blobs"].items():
        raw=(ROOT/r["path"]).read_bytes()
        check("blob:"+r["path"],len(raw)==r["byte_length"] and hashlib.sha256(raw).hexdigest()==digest)
    visited=set(); visiting=set()
    def walk(digest):
        if digest in visited: return
        assert digest not in visiting,"dependency cycle"
        visiting.add(digest)
        for r in records[digest]["dependencies"]: walk(r["digest"])
        visiting.remove(digest); visited.add(digest)
    for digest in records: walk(digest)
    check("acyclic_closure",len(visited)==len(records))

    case_summaries=[]
    for case in data["cases"]:
        name=case["name"]; req=body(case["request"]); result=body(case["result"])
        args=req["arguments"]; tri=body(args["triangle_ref"]); method=body(args["method_ref"])
        law=body(method["law_ref"]); producer=body(args["producer_ref"]); plan=body(args["draw_plan_ref"])
        code=None; expected="completed"; input_valid=True
        future={(c["origin"],c["development"]) for c in tri["cells"] if c["role"]=="future"}
        observed=[c for c in tri["cells"] if c["role"]=="observed"]
        phi=fraction(law["dispersion"])
        expected_family=("gamma_shape_scale" if method["native_selector"]=="gamma" else
                         "poisson_lambda" if phi==1 else "negative_binomial_mu_size")
        if len(tri["origins"])!=len(tri["developments"]):
            code="UNSUPPORTED_TRIANGLE_SHAPE"; expected="unsupported"; input_valid=False
        elif any(c["observed_cumulative"] is None for c in observed):
            code="OBSERVED_CELL_MISSING"; expected="rejected"; input_valid=False
        elif law["family"]!=expected_family:
            code="PROCESS_LAW_MISMATCH"; expected="rejected"; input_valid=False
        elif phi<=0 or method["native_selector"]=="od.pois" and phi<1:
            code="UNSUPPORTED_DISPERSION"; expected="unsupported"; input_valid=False
        elif producer["evidence"]!="authored_pre_coercion":
            code="PRECOERCION_EVIDENCE_UNAVAILABLE"; expected="unsupported"
        elif producer["method_ref"]!=args["method_ref"]:
            code="METHOD_ID_MISMATCH"; expected="rejected"
        elif any(producer[k]!=tri[k] or law[k]!=tri[k] for k in ["currency","base_unit","scale"]):
            code="UNIT_MISMATCH"; expected="rejected"
        elif Counter(d["draw_id"] for d in producer["draws"])!=Counter(plan["draw_ids"]):
            code="DRAW_ID_MISMATCH"; expected="rejected"
        elif any(Counter((c["origin"],c["development"]) for c in d["cells"])!=Counter(future) for d in producer["draws"]):
            code="CELL_DOMAIN_MISMATCH"; expected="rejected"
        elif any(c["fit_id"]!=d["fit_id"] for d in producer["draws"] for c in d["cells"]):
            code="FIT_ID_MISMATCH"; expected="rejected"
        else:
            for d in producer["draws"]:
                for c in d["cells"]:
                    mean=fraction(c["fitted_mean"]); value=fraction(c["payment"])
                    if mean<=0 or (c["status"]=="ok" and (value is None or value<0 or
                       (law["family"] in ["negative_binomial_mu_size","poisson_lambda"] and value.denominator!=1) or
                       (law["family"]=="gamma_shape_scale" and value<=0))):
                        code="SUPPORT_VIOLATION"; expected="rejected"
                    if c["status"]!="ok" and (value is not None or c["reason"] is None):
                        code="FAILED_VALUE_INCONSISTENT"; expected="rejected"
        sums=[]; categories=[]; counters=None
        if expected=="completed":
            for d in producer["draws"]:
                counts=Counter(c["status"] for c in d["cells"])
                outcome="failed" if counts["failed"] else "pending" if counts["pending"] else "completed"
                categories.append(outcome)
                sums.append(sum(fraction(c["payment"]) for c in d["cells"]) if outcome=="completed" else None)
            if producer["termination"]=="unknown":
                expected="partial"; code="TERMINATION_UNCONFIRMED"
            elif producer["termination"]=="confirmed_cancelled":
                expected="cancelled"; code="CANCELLED"
            elif "failed" in categories or "pending" in categories:
                expected="partial"; code="FAILED_DRAW" if "failed" in categories else "INCOMPLETE_DRAW"
            counters={"requested":len(plan["draw_ids"]),
                 "attempted":sum(any(c["status"]!="pending" for c in d["cells"]) for d in producer["draws"]),
                 "completed":categories.count("completed"),"failed":categories.count("failed"),
                 "pending":categories.count("pending")}
        check(name+":disposition",result["disposition"]==expected,{"derived":expected,"recorded":result["disposition"]})
        check(name+":diagnostic",[d["code"] for d in result["diagnostics"]]==([] if code is None else [code]))
        check(name+":validated_request",(result["request_ref"]==case["request"]) if input_valid else result["request_ref"] is None)
        check(name+":pure",result["commit_observation"]=="not_committed" and result["receipt_ref"] is None)
        check(name+":no_fabricated_resume",result["continuation_ref"] is None)
        check(name+":evidence_mode",result["evidence_mode"]=="specification_example")
        check(name+":no_empirical_promotion",result["statuses"]["empirical_justification"]=="not_established"
              and result["statuses"]["forecast_validity"]=="not_assessed")
        submission=body(result["submission_ref"])
        source=data["blobs"][submission["blob_ref"]["digest"]]
        check(name+":exact_submission",(ROOT/source["path"]).read_bytes()==canon(records[case["request"]["digest"]]))
        if counters is None:
            check(name+":no_admissible_payload",result["payload"] is None)
        else:
            summary=body(result["payload"]["summary_ref"])
            actual_draws=[body(x) for x in summary["draws"]]
            check(name+":totals",[fraction(x["total"]) for x in actual_draws]==sums)
            check(name+":draw_outcomes",[x["outcome"] for x in actual_draws]==categories)
            check(name+":counts",all(summary[k]==v for k,v in counters.items()),counters)
            completed=[v for v in sums if v is not None]
            diagnostic_mean=sum(completed)/len(completed) if completed else None
            full_mean=sum(sums)/len(sums) if all(v is not None for v in sums) else None
            check(name+":requested_mean",fraction(summary["requested_sample_mean"])==full_mean)
            check(name+":diagnostic_mean",fraction(summary["completed_only_diagnostic_mean"])==diagnostic_mean)
            check(name+":counts_not_probability_mass",summary["economic_probability_mass"] is None)
            for ds,draw in zip(actual_draws,producer["draws"]):
                cs=Counter(c["status"] for c in draw["cells"])
                check(name+":"+draw["draw_id"]+":cell_counts",
                    [ds["successful_cells"],ds["failed_cells"],ds["pending_cells"]]==[cs["ok"],cs["failed"],cs["pending"]])
        coverage=result["coverage"]
        if input_valid:
            check(name+":coverage_target",body(coverage["domain_ref"])["meaning"]=="computational_draw_ids_not_economic_probability")
            regions=[body(r) for k in ["completed","unresolved","unsupported","infeasible","cancelled"] for r in coverage[k]]
            ids=[x for r in regions for x in r["draw_ids"]]
            check(name+":coverage_partition",Counter(ids)==Counter(plan["draw_ids"]))
        else:
            check(name+":invalid_domain_withheld",coverage is None)
        case_summaries.append({"name":name,"derived_disposition":expected,"diagnostic":code,
                               "totals":[str(x) if x is not None else None for x in sums]})

    # Separate mathematical witness: information lost before the adapter sees output.
    good=[F(0),F(4),F(0)]; failed=[F(0),F(4),None]
    coercion=lambda xs:[F(0) if x is None else x for x in xs]
    check("native_coercion_noninjective",good!=failed and coercion(good)==coercion(failed))
    check("native_total_cannot_recover_failure",sum(coercion(good))==sum(coercion(failed))==4)
    # Mean/variance do not determine law: phi=3/2 scaled-Poisson cannot pay1,
    # whereas a negative-binomial with mean2,size4 has positive mass at1.
    m=F(2); phi=F(3,2); size=m/(phi-1); p=size/(size+m)
    check("negative_binomial_size",size==4)
    check("negative_binomial_mean",size*(1-p)/p==m)
    check("negative_binomial_variance",size*(1-p)/(p*p)==phi*m)
    check("law_support_differs",F(1)/phi!=int(F(1)/phi) and size*p**size*(1-p)>0)
    complete=next(x for x in data["cases"] if x["name"]=="complete")
    record=records[complete["request"]["digest"]]
    check("request_exact_retry",canon(deepcopy(record))==canon(record))
    changed=deepcopy(record); changed["body"]["request_id"]="new-correlation"
    check("request_id_changes_fingerprint",canon(changed)!=canon(record))
    changed=deepcopy(record); changed["body"]["execution"]["budget"]["operation_count"]=3
    check("budget_changes_fingerprint",canon(changed)!=canon(record))
    output={"passed":all(x["passed"] for x in checks),"check_count":len(checks),"checks":checks,
            "cases":case_summaries,"wall_seconds":time.perf_counter()-started,
            "scope":"Finite documentary schema/identity/closure/arithmetic checks; no R execution"}
    save=lambda p,x:p.write_text(json.dumps(x,indent=2)+"\n")
    save(OUT/"exchange-checks.json",output)
    print(json.dumps({"passed":output["passed"],"checks":len(checks),"cases":len(case_summaries),
                      "failed":[x["name"] for x in checks if not x["passed"]]}))
    if not output["passed"]: raise SystemExit(1)

if __name__=="__main__":
    main()
