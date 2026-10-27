"""Construct finite documentary exchanges; never execute a reserving model."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
REGISTRY={}
BLOBS={}

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def save(p,x): p.write_text(json.dumps(x,indent=2)+"\n")
def schema(kind):
    return {"OperationRequest":"accdsl.operation.request.v1",
            "OperationResult":"accdsl.operation.result.v1"}.get(kind,"accdsl.reserving."+kind.lower()+".v1")
def refs(x):
    if isinstance(x,dict):
        if set(x)=={"kind","schema","digest"}:
            yield x
        else:
            for y in x.values(): yield from refs(y)
    elif isinstance(x,list):
        for y in x: yield from refs(y)
def add(kind,key,body):
    deps={canon(r):r for r in refs(body)}
    record={"kind":kind,"schema":schema(kind),"key":key,"revision":0,
            "body":body,"dependencies":[deps[k] for k in sorted(deps)]}
    digest=hashlib.sha256(("accdsl.portable.v1/"+schema(kind)).encode()+b"\0"+canon(record)).hexdigest()
    REGISTRY[digest]=record
    return {"kind":kind,"schema":schema(kind),"digest":digest}
def blob(path):
    data=path.read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    BLOBS[digest]={"path":str(path.relative_to(ROOT)),"byte_length":len(data)}
    return {"kind":"blob","algorithm":"sha256","digest":digest,"byte_length":len(data)}
def rat(n,d=1):
    v=Fraction(n,d)
    return {"n":str(v.numerator),"d":str(v.denominator)}
def closed(props):
    return {"type":"object","properties":props,"required":list(props),"additionalProperties":False}
def array(items): return {"type":"array","items":items}
def enum(*values): return {"enum":list(values)}
def nullable(value): return {"anyOf":[value,{"type":"null"}]}
TEXT={"type":"string","minLength":1}
INT={"type":"integer","minimum":0}
BOOL={"type":"boolean"}
RAT=closed({"n":{"type":"string","pattern":"^(0|-?[1-9][0-9]*)$"},
            "d":{"type":"string","pattern":"^[1-9][0-9]*$"}})
BLOB=closed({"kind":{"const":"blob"},"algorithm":{"const":"sha256"},
             "digest":{"type":"string","pattern":"^[0-9a-f]{64}$"},"byte_length":INT})
def ref(kind=None):
    return closed({"kind":{"const":kind} if kind else TEXT,
                   "schema":{"const":schema(kind)} if kind else TEXT,
                   "digest":{"type":"string","pattern":"^[0-9a-f]{64}$"}})
CELL=closed({"origin":TEXT,"development":INT,"payment_period":TEXT,
             "role":enum("observed","future"),"observed_cumulative":nullable(RAT)})
OUTPUT_CELL=closed({"origin":TEXT,"development":INT,"fit_id":TEXT,"fitted_mean":RAT,
                    "status":enum("ok","failed","pending","unavailable"),"payment":nullable(RAT),"reason":nullable(TEXT)})
DRAW=closed({"draw_id":TEXT,"fit_id":TEXT,"cells":array(OUTPUT_CELL)})
STATUS=closed({"structural_validity":enum("valid","invalid"),
 "mathematical_status":enum("defined","unresolved"),"computation_status":enum("complete","partial","not_computed","cancelled"),
 "empirical_justification":{"const":"not_established"},"capability_status":{"const":"specified_only_no_runtime"},
 "accounting_validity":{"const":"not_assessed"},"forecast_validity":{"const":"not_assessed"},
 "product_readiness":{"const":"not_implemented"},"human_acceptance":{"const":"pending"}})
DIAG=closed({"code":TEXT,"stage":TEXT,"record_ref":nullable(ref()),"source_locator":nullable(TEXT),
 "field_path":TEXT,"affected_query_branch_ids":array(TEXT),"dependency_path":array(ref()),
 "observed":TEXT,"expected_rule":TEXT,"retry_advice":TEXT,"blocking_diagnostic_ids":array(TEXT)})
SCHEMAS={
 "SchemaLock":closed({"schema_blob":BLOB,"semantic_contract_blob":BLOB}),
 "Profile":closed({"profile_id":TEXT,"schema_lock_ref":ref("SchemaLock"),"mode":{"const":"documentary_only"}}),
 "Signature":closed({"operation":{"const":"reserving.evaluate@1"},"schema_lock_ref":ref("SchemaLock"),
                     "arguments":array(TEXT),"output_schema":TEXT}),
 "View":closed({"view_id":TEXT,"scope":{"const":"authored_synthetic"},"historical_availability_claim":{"const":False}}),
 "Environment":closed({"numerics":{"const":"exact_rational_fixture"},"runtime_executed":{"const":False},"gpu":{"const":"not_used"}}),
 "Triangle":closed({"view_ref":ref("View"),"entity":TEXT,"portfolio":TEXT,"currency":TEXT,
                     "base_unit":TEXT,"scale":{"type":"integer"},"valuation_date":TEXT,
                     "origins":array(TEXT),"developments":array(INT),"cells":array(CELL)}),
 "Law":closed({"family":enum("negative_binomial_mu_size","poisson_lambda","gamma_shape_scale","scaled_poisson"),
                "dispersion":RAT,"currency":TEXT,"base_unit":TEXT,"scale":{"type":"integer"}}),
 "Method":closed({"source_blob":BLOB,"description_blob":BLOB,"snapshot":TEXT,"implementation":enum("native_snapshot","instrumented_fixture"),
                   "native_selector":enum("od.pois","gamma"),"law_ref":ref("Law"),
                   "target":{"const":"lifetime_process_payments"},
                   "conditioning":{"const":"declared_triangle_method"},
                   "rng_policy":{"const":"authored_values_no_rng_execution"},
                   "runtime_dependencies":{"const":"unresolved_no_runtime"},
                   "terms":{"const":"GPL>=2_source_only_distribution_unresolved"}}),
 "DrawPlan":closed({"draw_ids":array(TEXT),"semantics":{"const":"computational_replicates_not_economic_mass"}}),
 "Producer":closed({"raw_blob":BLOB,"method_ref":ref("Method"),
                    "evidence":enum("native_post_coercion","authored_pre_coercion"),
                    "currency":TEXT,"base_unit":TEXT,"scale":{"type":"integer"},
                    "termination":enum("finished","confirmed_cancelled","unknown"),
                    "draws":array(DRAW),"values_are_fitted":{"const":False}}),
 "OperationRequest":closed({"operation":{"const":"reserving.evaluate@1"},"request_id":TEXT,"workspace_key":TEXT,
    "profile_ref":ref("Profile"),"signature_ref":ref("Signature"),"view_ref":ref("View"),
    "arguments":closed({"triangle_ref":ref("Triangle"),"method_ref":ref("Method"),
                       "draw_plan_ref":ref("DrawPlan"),"producer_ref":ref("Producer")}),
    "execution":closed({"mode":{"const":"specification_example"},
      "budget":closed({"operation_count":INT,"elapsed_seconds":nullable(INT),"elapsed_reason":TEXT}),
      "environment_ref":ref("Environment")}),"expected_head":{"type":"null"}}),
 "Submission":closed({"blob_ref":BLOB,"media_type":{"const":"application/json"},
                      "transport":{"const":"documentary_file"},"decoder":{"const":"accdsl.portable.v1"}}),
 "DrawDomain":closed({"request_ref":ref("OperationRequest"),"draw_ids":array(TEXT),
                       "meaning":{"const":"computational_draw_ids_not_economic_probability"}}),
 "DrawRegion":closed({"domain_ref":ref("DrawDomain"),"draw_ids":array(TEXT),
                       "status":enum("completed","unresolved","cancelled","unsupported")}),
 "DrawSummary":closed({"draw_id":TEXT,"outcome":enum("completed","failed","pending"),
                        "total":nullable(RAT),"successful_cells":INT,"failed_cells":INT,"pending_cells":INT}),
 "BatchSummary":closed({"request_ref":ref("OperationRequest"),"producer_ref":ref("Producer"),
  "draws":array(ref("DrawSummary")),"requested":INT,"attempted":INT,"completed":INT,"failed":INT,"pending":INT,
  "requested_sample_mean":nullable(RAT),"completed_only_diagnostic_mean":nullable(RAT),
  "economic_probability_mass":{"type":"null"}}),
}
SCHEMAS["OperationResult"]=closed({
 "submission_ref":ref("Submission"),"request_ref":nullable(ref("OperationRequest")),
 "operation":nullable(TEXT),"input_view_ref":nullable(ref("View")),
 "disposition":enum("completed","partial","cancelled","rejected","unsupported"),
 "statuses":STATUS,"payload":nullable(closed({"kind":{"const":"reserving_candidate"},"summary_ref":ref("BatchSummary")})),
 "diagnostics":array(DIAG),
 "coverage":nullable(closed({"domain_ref":ref("DrawDomain"),**{k:array(ref("DrawRegion")) for k in
             ["completed","unresolved","unsupported","infeasible","cancelled"]},"relation":{"const":"disjoint_partition"}})),
 "unresolved":array(TEXT),"continuation_ref":{"type":"null"},"commit_observation":{"const":"not_committed"},
 "receipt_ref":{"type":"null"},"evidence_mode":{"const":"specification_example"}})

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    schema_path=OUT/"record-schemas.json"
    save(schema_path,{"$schema":"https://json-schema.org/draft/2020-12/schema","bodies":SCHEMAS})
    lock=add("SchemaLock","schema-lock",{"schema_blob":blob(schema_path),
        "semantic_contract_blob":blob(ROOT/"docs/design/proposal/architecture/reserving-adapter-contract-20261014.md")})
    profile=add("Profile","profile",{"profile_id":"authored-reserving-exchange-v1","schema_lock_ref":lock,"mode":"documentary_only"})
    signature=add("Signature","signature",{"operation":"reserving.evaluate@1","schema_lock_ref":lock,
        "arguments":["triangle_ref","method_ref","draw_plan_ref","producer_ref"],"output_schema":schema("OperationResult")})
    view=add("View","view",{"view_id":"authored-2024-close","scope":"authored_synthetic","historical_availability_claim":False})
    env=add("Environment","environment",{"numerics":"exact_rational_fixture","runtime_executed":False,"gpu":"not_used"})
    observed={(0,0):100,(0,1):150,(0,2):185,(1,0):120,(1,1):190,(2,0):140}
    triangle={"view_ref":view,"entity":"synthetic-insurer","portfolio":"authored","currency":"CU","base_unit":"one-CU","scale":0,
        "valuation_date":"2024-12-31","origins":["2022","2023","2024"],"developments":[0,1,2],"cells":[]}
    for i,origin in enumerate(triangle["origins"]):
        for j in range(3):
            triangle["cells"].append({"origin":origin,"development":j,"payment_period":str(2022+i+j),
               "role":"observed" if (i,j) in observed else "future",
               "observed_cumulative":rat(observed[i,j]) if (i,j) in observed else None})
    base_method={"source_blob":blob(ROOT/"data/accounting-master/p17-completion-20261014/P17-09/reserving-bootstrap/sources/BootstrapReserve.R"),
       "description_blob":blob(ROOT/"data/accounting-master/p17-completion-20261014/P17-09/reserving-bootstrap/sources/ChainLadder-DESCRIPTION"),
       "snapshot":"5cd0dd441c3bb9e1ee6d7572d5bc1475f29be728","implementation":"instrumented_fixture",
       "native_selector":"od.pois","target":"lifetime_process_payments","conditioning":"declared_triangle_method",
       "rng_policy":"authored_values_no_rng_execution","runtime_dependencies":"unresolved_no_runtime",
       "terms":"GPL>=2_source_only_distribution_unresolved"}
    law={"family":"negative_binomial_mu_size","dispersion":rat(2),"currency":"CU","base_unit":"one-CU","scale":0}
    locations=[("2023",2),("2024",1),("2024",2)]
    base_draws=[]
    for k,values in enumerate([[0,4,8],[2,6,10]]):
        fit="fit-"+str(k)
        base_draws.append({"draw_id":"draw-"+str(k),"fit_id":fit,"cells":[
            {"origin":o,"development":j,"fit_id":fit,"fitted_mean":rat(m),"status":"ok","payment":rat(v),"reason":None}
            for (o,j),m,v in zip(locations,[2,4,6],values)]})
    # Expectations are authored separately from the checker, not produced by its classifier.
    cases=[
      ("complete","completed",None,[12,18],15,15,[2,2,2,0,0]),
      ("one_failed","partial","FAILED_DRAW",[None,18],None,18,[2,2,1,1,0]),
      ("cancelled","cancelled","CANCELLED",[12,None],None,12,[2,1,1,0,1]),
      ("termination_unknown","partial","TERMINATION_UNCONFIRMED",[12,None],None,12,[2,1,1,0,1]),
      ("native_zero_loss","unsupported","PRECOERCION_EVIDENCE_UNAVAILABLE",[],None,None,None),
      ("wrong_law","rejected","PROCESS_LAW_MISMATCH",[],None,None,None),
      ("underdispersed_native","unsupported","UNSUPPORTED_DISPERSION",[],None,None,None),
      ("mixed_fit","rejected","FIT_ID_MISMATCH",[],None,None,None),
      ("duplicate_draw","rejected","DRAW_ID_MISMATCH",[],None,None,None),
      ("missing_cell","rejected","CELL_DOMAIN_MISMATCH",[],None,None,None),
      ("wrong_currency","rejected","UNIT_MISMATCH",[],None,None,None),
      ("observed_null","rejected","OBSERVED_CELL_MISSING",[],None,None,None),
      ("negative_payment","rejected","SUPPORT_VIOLATION",[],None,None,None),
      ("noninteger_payment","rejected","SUPPORT_VIOLATION",[],None,None,None),
      ("gamma_underdispersion","completed",None,[13,18],rat(31,2),rat(31,2),[2,2,2,0,0]),
      ("poisson_at_one","completed",None,[12,18],15,15,[2,2,2,0,0]),
      ("rectangular","unsupported","UNSUPPORTED_TRIANGLE_SHAPE",[],None,None,None),
      ("zero_fitted_mean","rejected","SUPPORT_VIOLATION",[],None,None,None),
    ]
    exchanges=[]
    for name,disposition,diagnostic,totals,fullmean,diagmean,counts in cases:
        tri=deepcopy(triangle); meth=deepcopy(base_method); lawbody=deepcopy(law); draws=deepcopy(base_draws)
        termination="finished"; evidence="authored_pre_coercion"; currency="CU"
        if name=="one_failed":
            draws[0]["cells"][2].update(status="failed",payment=None,reason="NONFINITE_PROCESS_DRAW")
        if name in ["cancelled","termination_unknown"]:
            termination="confirmed_cancelled" if name=="cancelled" else "unknown"
            for c in draws[1]["cells"]: c.update(status="pending",payment=None,reason="NOT_ATTEMPTED")
        if name=="native_zero_loss":
            meth["implementation"]="native_snapshot"; evidence="native_post_coercion"
            draws[0]["cells"][2]["payment"]=rat(0)
            for draw in draws:
                for c in draw["cells"]: c.update(status="unavailable",reason="NATIVE_MASK_NOT_RETURNED")
        if name=="wrong_law": lawbody["family"]="scaled_poisson"
        if name=="underdispersed_native": lawbody["dispersion"]=rat(1,2)
        if name=="mixed_fit": draws[0]["cells"][2]["fit_id"]="other-fit"
        if name=="duplicate_draw": draws[1]["draw_id"]="draw-0"
        if name=="missing_cell": draws[0]["cells"].pop()
        if name=="wrong_currency": currency="USD"
        if name=="observed_null": tri["cells"][0]["observed_cumulative"]=None
        if name=="negative_payment": draws[0]["cells"][0]["payment"]=rat(-1)
        if name=="noninteger_payment": draws[0]["cells"][0]["payment"]=rat(1,2)
        if name=="gamma_underdispersion":
            lawbody.update(family="gamma_shape_scale",dispersion=rat(1,2))
            meth["native_selector"]="gamma"; draws[0]["cells"][0]["payment"]=rat(1)
        if name=="poisson_at_one":
            lawbody.update(family="poisson_lambda",dispersion=rat(1))
        if name=="rectangular":
            tri["origins"]=["2022","2023"]
            tri["cells"]=[c for c in tri["cells"] if c["origin"] in tri["origins"]]
        if name=="zero_fitted_mean": draws[0]["cells"][0]["fitted_mean"]=rat(0)
        lawref=add("Law",name+"-law",lawbody); meth["law_ref"]=lawref
        method=add("Method",name+"-method",meth)
        triref=add("Triangle",name+"-triangle",tri)
        plan=add("DrawPlan",name+"-draws",{"draw_ids":["draw-0","draw-1"],"semantics":"computational_replicates_not_economic_mass"})
        rawpath=OUT/(name+"-raw.json")
        save(rawpath,{"nature":"authored_possible_values_not_fitted_or_sampled","draws":draws})
        producer=add("Producer",name+"-producer",{"raw_blob":blob(rawpath),"method_ref":method,"evidence":evidence,
           "currency":currency,"base_unit":"one-CU","scale":0,"termination":termination,"draws":draws,"values_are_fitted":False})
        request_body={"operation":"reserving.evaluate@1","request_id":name,"workspace_key":"documentary-reserving",
           "profile_ref":profile,"signature_ref":signature,"view_ref":view,
           "arguments":{"triangle_ref":triref,"method_ref":method,"draw_plan_ref":plan,"producer_ref":producer},
           "execution":{"mode":"specification_example","budget":{"operation_count":2,"elapsed_seconds":None,
                        "elapsed_reason":"No runtime execution"},"environment_ref":env},"expected_head":None}
        request=add("OperationRequest",name+"-request",request_body)
        request_path=OUT/(name+"-request.json"); request_path.write_bytes(canon(REGISTRY[request["digest"]]))
        submission=add("Submission",name+"-submission",{"blob_ref":blob(request_path),"media_type":"application/json",
                        "transport":"documentary_file","decoder":"accdsl.portable.v1"})
        valid_input=name not in ["observed_null","wrong_law","underdispersed_native","rectangular"]
        domain=add("DrawDomain",name+"-domain",{"request_ref":request,"draw_ids":["draw-0","draw-1"],
                      "meaning":"computational_draw_ids_not_economic_probability"}) if valid_input else None
        coverage=None
        if domain:
            coverage={"domain_ref":domain,**{k:[] for k in ["completed","unresolved","unsupported","infeasible","cancelled"]},
                      "relation":"disjoint_partition"}
            for i in range(2):
                state="completed" if totals and totals[i] is not None else (
                    "cancelled" if disposition=="cancelled" else "unsupported" if disposition=="unsupported" else "unresolved")
                r=add("DrawRegion",name+"-region-"+str(i),{"domain_ref":domain,"draw_ids":["draw-"+str(i)],"status":state})
                coverage[state].append(r)
        payload=None
        if counts:
            ds=[]
            for i,total in enumerate(totals):
                cs=draws[i]["cells"]
                outcome="completed" if total is not None else "failed" if any(c["status"]=="failed" for c in cs) else "pending"
                ds.append(add("DrawSummary",name+"-summary-"+str(i),{
                  "draw_id":"draw-"+str(i),"outcome":outcome,"total":rat(total) if total is not None else None,
                  "successful_cells":sum(c["status"]=="ok" for c in cs),
                  "failed_cells":sum(c["status"]=="failed" for c in cs),"pending_cells":sum(c["status"]=="pending" for c in cs)}))
            summary=add("BatchSummary",name+"-summary",{"request_ref":request,"producer_ref":producer,"draws":ds,
              **dict(zip(["requested","attempted","completed","failed","pending"],counts)),
              "requested_sample_mean":fullmean if isinstance(fullmean,dict) else rat(fullmean) if fullmean is not None else None,
              "completed_only_diagnostic_mean":diagmean if isinstance(diagmean,dict) else rat(diagmean) if diagmean is not None else None,
              "economic_probability_mass":None})
            payload={"kind":"reserving_candidate","summary_ref":summary}
        diagnostics=[] if diagnostic is None else [{"code":diagnostic,"stage":"input" if not valid_input else "producer",
           "record_ref":producer if valid_input else triref,"source_locator":None,"field_path":"producer.draws" if valid_input else "triangle.cells",
           "affected_query_branch_ids":[],"dependency_path":[],"observed":name,
           "expected_rule":"reserving-adapter-contract-20261014","retry_advice":"Preserve evidence; repair named condition before dependent use",
           "blocking_diagnostic_ids":[]}]
        result=add("OperationResult",name+"-result",{
           "submission_ref":submission,"request_ref":request if valid_input else None,"operation":"reserving.evaluate@1",
           "input_view_ref":view if valid_input else None,"disposition":disposition,
           "statuses":{"structural_validity":"valid" if valid_input else "invalid",
             "mathematical_status":"defined" if disposition=="completed" else "unresolved",
             "computation_status": {"completed":"complete","partial":"partial","cancelled":"cancelled"}.get(disposition,"not_computed"),
             "empirical_justification":"not_established","capability_status":"specified_only_no_runtime",
             "accounting_validity":"not_assessed","forecast_validity":"not_assessed","product_readiness":"not_implemented","human_acceptance":"pending"},
           "payload":payload,"diagnostics":diagnostics,"coverage":coverage,
           "unresolved":[] if diagnostic is None else [diagnostic],"continuation_ref":None,
           "commit_observation":"not_committed","receipt_ref":None,"evidence_mode":"specification_example"})
        exchanges.append({"name":name,"request":request,"result":result})
    save(OUT/"portable-exchanges.json",{"records":REGISTRY,"blobs":BLOBS,"cases":exchanges,
       "scope":"Authored documentary exchange only; no fitting, random sampling or runtime adapter"})
    print(json.dumps({"records":len(REGISTRY),"blobs":len(BLOBS),"cases":len(exchanges)}))

if __name__=="__main__":
    main()
