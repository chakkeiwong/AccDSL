"""Author bounded composition traces; no runtime model/book operations."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2)+chr(10))

sources={}
def source(key,text,pub,ingested,reviewed,value,supersedes=None,vintage=True):
    p=OUT/"synthetic-sources"/(key+".txt")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text("AUTHORED SYNTHETIC FIXTURE; NOT AN ISSUER DOCUMENT\n"+text+"\n")
    sources[key]={"source_id":key,"path":str(p.relative_to(ROOT)),"sha256":sha(p),
        "economic_time":"2024-01-01T08:00:00Z","public_at":pub,"ingested_at":ingested,
        "reviewed_at":reviewed,"byte_vintage_verified":vintage,"ingestion_receipt_verified":True,
        "reading_id":key+"-reading-1","value":value,"supersedes":supersedes,
        "context_key":"bank-original-risk" if key.startswith("bank") else "insurer-B-R-order",
        "evidence_mode":"authored_synthetic","reviewer":"authored-reviewer",
        "publication_receipt":"authored-public-receipt-"+key if pub is not None and vintage else None,
        "ingestion_receipt":"authored-ingestion-receipt-"+key}
source("bank-missing","Original commitment credit baseline not supplied.",
       "2024-01-02T08:00:00Z","2024-01-02T09:00:00Z","2024-01-02T10:00:00Z",None)
source("bank-restored","Irrevocable commitment at08:00; first-year default probability0.1. Original risk ID commitment-risk0; current supported SICR comparison retains that ID.",
       "2024-01-02T12:00:00Z","2024-01-05T09:00:00Z","2024-01-06T10:00:00Z",
       {"original_risk_id":"commitment-risk0","first_year_default":"1/10","sicr_baseline_id":"commitment-risk0","sicr_supported":True},"bank-missing")
source("insurance-v1","Treaty R entered2024-01-01T07:59:00Z; group B recognised2024-01-01T08:00:00Z.",
       "2024-01-10T08:00:00Z","2024-01-12T09:00:00Z","2024-01-13T10:00:00Z","before")
source("insurance-v2","Correction of the same treaty date: R entered2024-01-01T08:01:00Z, after B recognition2024-01-01T08:00:00Z. Supersedes the v1 order assertion only.",
       "2024-02-10T08:00:00Z","2024-02-11T09:00:00Z","2024-02-12T10:00:00Z","after","insurance-v1")
source("insurance-unknown","Competing order assertion: R entered after B. Public availability and historical byte linkage unestablished.",
       None,"2024-02-14T09:00:00Z","2024-02-15T10:00:00Z","after",None,False)
source("insurance-vintage","Order said to be after B; publication date asserted without exact-byte historical linkage.",
       "2024-01-09T08:00:00Z","2024-02-14T09:00:00Z","2024-02-15T10:00:00Z","after",None,False)
source("insurance-order-unknown","Treaty entry and B recognition occur on1January; their order is not given.",
       "2024-01-10T08:00:00Z","2024-01-12T09:00:00Z","2024-01-13T10:00:00Z",None)

atomic_path=ROOT/"data/accounting-master/p17-completion-20261014/P17-10/insurance-atomic/portable-exchanges.json"
atomic=json.loads(atomic_path.read_text())
replay=next(c for c in atomic["cases"] if c["id"]=="replay_after_settlement")
changed=next(c for c in atomic["cases"] if c["id"]=="changed_request_id")
book=deepcopy(replay["before"])
save("committed-world.json",book)
bank_path=ROOT/"data/accounting-master/p17-completion-20261014/P17-06/commitment-draw/commitment-cases.json"
bank_fixture=json.loads(bank_path.read_text())
bank_book={"mode":"authored_synthetic","identity":{"entity":"Bank","book":"AASB2024","branch":"commitment-draw"},
           "source_fixture":str(bank_path.relative_to(ROOT)),"source_sha256":sha(bank_path),
           "opening":bank_fixture["opening"],"credit_history":bank_fixture["credit_history"],
           "common_journals":bank_fixture["common_journals"],
           "route":bank_fixture["routes"]["direct_external"],
           "closing":bank_fixture["expected_final"]["direct_external"]}
save("bank-world.json",bank_book)
graph={
 "insurance-membership":{"version":"m0","deps":[]},
 "insurance-reading":{"version":"r0","deps":[]},
 "insurance-rule":{"version":"aasb17-pinned","deps":[]},
 "insurance-selection":{"version":"sel0","deps":["insurance-membership","insurance-reading"]},
 "insurance-measurement":{"version":"measure0","deps":["insurance-selection","insurance-rule"]},
 "insurance-result":{"version":"result0","deps":["insurance-measurement"]},
 "later-child":{"version":"child0","deps":["insurance-result"]},
 "bank-risk":{"version":"risk0","deps":[]},
 "bank-rule":{"version":"aasb9-pinned","deps":[]},
 "bank-result":{"version":"bank0","deps":["bank-risk","bank-rule"]}
}
current={k:v["version"] for k,v in graph.items()}
current["insurance-membership"]="m1"
frozen={"id":"insurance-result0","view":"insurance-view0","dependency_versions":{k:v["version"] for k,v in graph.items() if k.startswith("insurance")},
        "values":{"R_initial_asset":"85","initial_equity":"85","year1_equity":"83","final_cash":"883/10"},
        "evidence_mode":"authored_synthetic","book_hash":digest(book)}
cases=[]
identity={"workspace":"authored-sector-review","entity":"Insurer","book":"Pretax","branch":"connected-2024","book_mode":"synthetic"}
def case(key,action,request,expected,sector="insurance"):
    world_hash=digest(book if sector=="insurance" else bank_book)
    request=deepcopy(request)
    if "book_hash" in request:
        request["book_hash"]=world_hash
    cases.append({"id":key,"action":action,"identity":identity if sector=="insurance" else
        {"workspace":"authored-sector-review","entity":"Bank","book":"AASB2024","branch":"commitment-draw","book_mode":"synthetic"},
        "request":request,"expected":expected,"committed_world_before":world_hash,
        "committed_world_after":world_hash,"evidence_mode":"specification_example"})
def selection(mode="investor_information",cutoff="2024-01-31T23:59:59Z",system=None,layer="accepted",
              ids=None,view="insurance-view0",review="2024-02-20T12:00:00Z",**extra):
    q={"admission_mode":mode,"information_cutoff":cutoff,"system_as_of":system,
       "layer":layer,"selection":"latest_available","candidate_ids":ids or ["insurance-v1"],
       "view_id":view,"review_snapshot_at":review,"economic_target":"2024-01-01",
       "requested_quantities":["R_initial_asset","initial_equity","year1_equity","final_cash"],
       "book_hash":digest(book),"method":"conditional-connected-insurance-2.83"}
    q.update(extra);return q
def outcome(status,selected=(),excluded=None,unresolved=(),values=None,reason=None):
    return {"status":status,"selected":list(selected),"excluded":excluded or {},"unresolved":list(unresolved),
            "values":values,"reason":reason,"commit_observation":"not_committed","additional_commit":False}
timely={"R_initial_asset":"85","initial_equity":"85","year1_equity":"83","final_cash":"883/10"}
late={"R_initial_asset":"70","initial_equity":"70","year1_equity":"299/4","final_cash":"883/10"}
bank={"allowance":"4","equity":"16","original_risk_id":"commitment-risk0"}
b=selection(ids=["bank-missing"],method="conditional-commitment-draw-2.82",view="bank-view0",
            requested_quantities=["allowance","equity","original_risk_id"])
case("bank_missing_original","select_and_assess",b,outcome("unresolved",["bank-missing"],unresolved=["original_credit_baseline"]),sector="bank")
b=selection(ids=["bank-missing","bank-restored"],cutoff="2024-01-03T12:00:00Z",view="bank-view1",
            method="conditional-commitment-draw-2.82",requested_quantities=["allowance","equity","original_risk_id"])
case("bank_restored_later_ingestion","select_and_assess",b,outcome("conditional",["bank-restored"],{"bank-missing":"superseded"},values=bank),sector="bank")
for key,system,layer,expected in [
 ("bank_not_yet_ingested","2024-01-03T12:00:00Z","raw",outcome("unresolved",excluded={"bank-restored":"ingested_after_cutoff"},unresolved=["no_eligible_input"])),
 ("bank_raw_before_review","2024-01-05T12:00:00Z","raw",outcome("raw_available",["bank-restored"])),
 ("bank_accepted_before_review","2024-01-05T12:00:00Z","accepted",outcome("unresolved",unresolved=["bank-restored:review_after_system_cutoff"])),
 ("bank_system_after_review","2024-01-07T12:00:00Z","accepted",outcome("conditional",["bank-restored"],values=bank))]:
    q=deepcopy(b);q.update(admission_mode="system_as_of",information_cutoff=None,system_as_of=system,layer=layer,candidate_ids=["bank-restored"])
    case(key,"select_and_assess",q,expected,sector="bank")
q=deepcopy(b);q["baseline_binding_override"]="draw-date-risk"
case("bank_draw_baseline_reset","select_and_assess",q,outcome("rejected",reason="SICR_BASELINE_MISMATCH"),sector="bank")
case("insurance_original_view","select_and_assess",selection(),outcome("conditional",["insurance-v1"],values=timely))
case("later_revision_old_cutoff","select_and_assess",selection(ids=["insurance-v1","insurance-v2"],view="insurance-view1"),
     outcome("conditional",["insurance-v1"],{"insurance-v2":"published_after_cutoff"},values=timely))
q=selection(ids=["insurance-v1","insurance-v2"],view="insurance-view1",cutoff="2024-02-20T12:00:00Z")
case("later_revision_new_cutoff","select_and_assess",q,outcome("conditional",["insurance-v2"],{"insurance-v1":"superseded"},values=late))
q=selection(ids=["insurance-v1","insurance-v2","insurance-unknown"],view="insurance-view2",cutoff="2024-02-20T12:00:00Z")
case("unknown_competitor","select_and_assess",q,outcome("unresolved",["insurance-v2"],{"insurance-v1":"superseded"},["insurance-unknown:public_time_unknown"]))
q=selection(ids=["insurance-v1","insurance-vintage"],view="insurance-view3")
case("unknown_historical_bytes","select_and_assess",q,outcome("unresolved",["insurance-v1"],unresolved=["insurance-vintage:byte_vintage_unverified"]))
q=selection(ids=["insurance-order-unknown"])
case("unknown_treaty_order","select_and_assess",q,outcome("unresolved",["insurance-order-unknown"],unresolved=["treaty_order"]))
q=selection(ids=["insurance-v1"]);q["tampered_blob"]="insurance-v1"
case("source_hash_mismatch","select_and_assess",q,outcome("rejected",reason="SOURCE_HASH_MISMATCH"))
q=selection(ids=["insurance-v1","insurance-unknown"],mode="system_as_of",cutoff=None,system="2024-02-20T12:00:00Z")
case("system_private_competing_assertions","select_and_assess",q,outcome("unresolved",["insurance-unknown","insurance-v1"],unresolved=["CONFLICTING_VERSIONS"]))
q=selection(mode="system_as_of",cutoff="2024-01-31T23:59:59Z",system="2024-01-11T12:00:00Z")
case("dual_cutoff_requires_ingestion","select_and_assess",q,outcome("unresolved",excluded={"insurance-v1":"ingested_after_cutoff"},unresolved=["no_eligible_input"]))
for key,root,expected,changes in [
 ("membership_stales_unchanged_selected","insurance-result","STALE_VIEW",{}),
 ("late_created_child_is_stale","later-child","STALE_VIEW",{}),
 ("unrelated_bank_reusable","bank-result","reusable",{}),
 ("missing_required_ancestor","insurance-result","DEPENDENCY_MISSING",{"remove":"insurance-reading"}),
 ("cyclic_dependency","insurance-result","DEPENDENCY_CYCLE",{"cycle":True}),
 ("fresh_manifest_same_values","insurance-result","reusable",{"refresh":True})]:
    case(key,"current_use",{"root":root,"graph_changes":changes,"current_versions":current,"book_hash":digest(book)},
         outcome(expected,values=timely if expected=="reusable" and root=="insurance-result" else None))
case("frozen_explanation","frozen_explain",{"output_id":frozen["id"],"requested_view":"insurance-view0","frozen":frozen,"current_versions":current},
     outcome("historical_with_stale_warning",values=timely))
case("wrong_frozen_view","frozen_explain",{"output_id":frozen["id"],"requested_view":"insurance-view1","frozen":frozen,"current_versions":current},
     outcome("rejected",reason="FROZEN_VIEW_MISMATCH"))
# The old extraction error and corrected reading share exact issuer-v2 source bytes.
reading_versions=[
 {"id":"reading-wrong","source_id":"insurance-v2","value":"before","reviewed_at":"2024-02-12T10:00:00Z","supersedes":None,"assessment":"historically accepted extraction error"},
 {"id":"reading-corrected","source_id":"insurance-v2","value":"after","reviewed_at":"2024-02-16T10:00:00Z","supersedes":"reading-wrong","assessment":"source-time faithful correction"}
]
case("extraction_error_frozen","reading_revision",{"reading_id":"reading-wrong","mode":"frozen","current_reading":"reading-corrected"},
     outcome("historical_error_not_current",values=timely))
case("extraction_correction_current","reading_revision",{"reading_id":"reading-corrected","mode":"current","current_reading":"reading-corrected"},
     outcome("conditional",values=late))
case("correction_not_authorized","correction_request",{"new_projection":late,"prior_projection":timely,"treatment_authority":None,
    "change_kind":"issuer_assertion_revision","book_hash":digest(book)},
    outcome("unsupported",reason="TREATMENT_UNSUPPORTED"))
case("original_exact_retry","replay_existing",{"external_case":"replay_after_settlement","current_evidence_view":"insurance-view1",
    "request_ref":replay["candidate_request_ref"],"result_ref":replay["expected_result_ref"]},
    outcome("replayed_original",reason="original_receipt_preserved"))
case("changed_request_is_conflict","changed_retry",{"external_case":"changed_request_id","current_evidence_view":"insurance-view1",
    "request_ref":changed["candidate_request_ref"],"result_ref":changed["expected_result_ref"]},
    outcome("rejected",reason="EVENT_ID_CONFLICT"))
pins=[
 "docs/design/proposal/architecture/evidence-contract-v3.md","docs/design/proposal/architecture/time-contract-v2.md",
 "docs/design/proposal/architecture/history-families-contract-v1.md","docs/design/proposal/architecture/persistence-contract-v1.md",
 "docs/design/proposal/architecture/interfaces-contract-v1.md",
 "docs/design/proposal/manuscript-bank-prudential-20261014/sections/bank-commitment-draw.tex",
 "docs/design/proposal/manuscript-bank-prudential-20261014/sections/insurance-connected-groups.tex",
 str(atomic_path.relative_to(ROOT)),str(bank_path.relative_to(ROOT))]
fixture={"schema":"SectorRevisionTrace/v1","evidence_mode":"authored_synthetic","runtime_executed":False,
 "sources":sources,"reading_versions":reading_versions,"dependency_graph":graph,"frozen_result":frozen,
 "book":{"path":str((OUT/"committed-world.json").relative_to(ROOT)),"canonical_sha256":digest(book)},
 "bank_book":{"path":str((OUT/"bank-world.json").relative_to(ROOT)),"canonical_sha256":digest(bank_book)},
 "external_atomic":{"path":str(atomic_path.relative_to(ROOT)),"sha256":sha(atomic_path)},
 "pins":[{"path":p,"sha256":sha(ROOT/p)} for p in pins],"cases":cases,
 "limits":["composed semantic traces; not new portable OperationRequest encodings","no actual historical evidence",
           "no monetary correction rule inferred","no runtime or current compliance claim"]}
save("revision-traces.json",fixture)
print(json.dumps({"cases":len(cases),"synthetic_sources":len(sources),"pins":len(pins),"book_hash":digest(book)}))
