"""Author finite group exchanges; no accounting service is executed."""
from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
OLD=ROOT/"data/accounting-master/p17-completion-20261014/P17-05/group-fx-disposal"
REG={};ALIASES={};BLOBS={};EX=[]
def enc(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sid(k):return {"OperationRequest":"accdsl.operation.request.v1","OperationResult":"accdsl.operation.result.v1"}.get(k,"accdsl.group."+k.lower()+".v1")
def refs(x):
    if isinstance(x,dict):
        if set(x)=={"kind","schema","digest"}:yield x
        else:
            for v in x.values():yield from refs(v)
    elif isinstance(x,list):
        for v in x:yield from refs(v)
def add(k,key,b):
    links={enc(r):r for r in refs(b)}
    r={"kind":k,"schema":sid(k),"key":key,"revision":0,"body":b,
       "dependencies":[links[z] for z in sorted(links)]}
    d=hashlib.sha256(("accdsl.portable.v1/"+sid(k)).encode()+b"\0"+enc(r)).hexdigest()
    REG[d]=r;ref={"kind":k,"schema":sid(k),"digest":d};ALIASES[key]=ref;return ref
def body(r):return REG[r["digest"]]["body"]
def blob(p):
    b=p.read_bytes();d=hashlib.sha256(b).hexdigest()
    BLOBS[d]={"path":str(p.relative_to(ROOT)),"byte_length":len(b)}
    return {"kind":"blob","algorithm":"sha256","digest":d,"byte_length":len(b)}
def q(x):
    f=F(x);return {"n":str(f.numerator),"d":str(f.denominator)}
def obj(p):return {"type":"object","properties":p,"required":list(p),"additionalProperties":False}
def arr(x,n=0):return {"type":"array","items":x,"minItems":n}
def maybe(x):return {"anyOf":[x,{"type":"null"}]}
ID={"type":"string","pattern":"^[A-Za-z0-9_.:@/-]+$"}
TXT={"type":"string","minLength":1};INT={"type":"integer","minimum":0};BOOL={"type":"boolean"}
RAT=obj({"n":{"type":"string","pattern":"^(0|-?[1-9][0-9]*)$"},"d":{"type":"string","pattern":"^[1-9][0-9]*$"}})
BLOB=obj({"kind":{"const":"blob"},"algorithm":{"const":"sha256"},"digest":{"type":"string","pattern":"^[0-9a-f]{64}$"},"byte_length":INT})
def ref(k=None):return obj({"kind":{"const":k} if k else ID,"schema":{"const":sid(k)} if k else ID,"digest":{"type":"string","pattern":"^[0-9a-f]{64}$"}})
def enum(*v):return {"enum":list(v)}
ACCOUNTS=["Cash","Inventory","Goodwill","Payable","NCI","Parent CTA","Parent capital",
          "Parent operating retained profit","Revenue","Cost of sales","Disposal gain","Retained investment"]
PERF=["profit","parent_profit","nci_profit","oci","parent_oci","nci_oci","cfo","cfi_acquisition",
      "cfi_disposal","cff","cash_fx","nci_introduced","nci_removed"]
BAL=obj({k:RAT for k in ACCOUNTS});MOV=obj({k:RAT for k in PERF})
LINE=obj({"account":enum(*ACCOUNTS),"signed_amount":RAT})
IDENTITY=obj({k:ID for k in ["entity_id","book_id","branch_key","business_event_id"]})
HEAD=obj({"owner_key":ID,"state_ref":ref("GroupState"),"generation":INT})
base=json.loads((ROOT/"data/accounting-master/corporate-portable-20261015/record-schemas.json").read_text())
def remap(x):
    if isinstance(x,str):return x.replace("accdsl.corporate.","accdsl.group.")
    if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
    if isinstance(x,list):return [remap(v) for v in x]
    return x
S={k:remap(base["$defs"][k]) for k in ["SchemaLock","OperationSignature","Environment","Decoder","Submission","OperationResult","TransportObservation"]}
S["Profile"]=obj({"profile_id":{"const":"GroupForeignOperation/1"},"schema_lock_ref":ref("SchemaLock"),"operations":arr(ID,1),"book_mode":{"const":"synthetic"},"execution_mode":{"const":"specification_example"}})
S["SourceAnchor"]=obj({"case_blob":BLOB,"method_blob":BLOB,"source_manifest_blob":BLOB,
    "source_pdf_blob":BLOB,"source_excerpt_blob":BLOB,"common_contract_blob":BLOB,"scope":TXT})
S["Entity"]=obj({"entity_id":ID,"display_name":TXT,"functional_currency":enum("USD","EUR"),"legal_entity":BOOL})
S["EntityBook"]=obj({"entity_ref":ref("Entity"),"book_id":ID,"instant":INT,"currency":enum("USD","EUR"),
    "balances":BAL,"source_ref":ref("SourceAnchor")})
S["ControlAssessment"]=obj({"parent_ref":ref("Entity"),"subsidiary_ref":ref("Entity"),
    "start_inclusive":INT,"end_exclusive":INT,"power":enum("supported","unknown"),"variable_returns":BOOL,
    "power_affects_returns":BOOL,"ownership":RAT,"nci_fraction":RAT,"ordinary_equal_rights":BOOL,"source_ref":ref("SourceAnchor")})
S["Rate"]=obj({"base":{"type":"string"},"quote":{"type":"string"},"instant":INT,
    "quote_per_base":maybe(RAT),"source_ref":ref("SourceAnchor")})
S["PerimeterVersion"]=obj({"group_entity_ref":ref("Entity"),"parent_ref":ref("Entity"),"subsidiary_ref":ref("Entity"),
    "control_ref":ref("ControlAssessment"),"instant":INT,"includes_subsidiary":BOOL,"presentation_currency":{"const":"USD"},
    "nci_policy":{"const":"proportionate_identifiable_net_assets"},"policy_alignment":{"const":"supplied_no_adjustment"},
    "entity_book_refs":arr(ref("EntityBook"),2)})
S["View"]=obj({"source_ref":ref("SourceAnchor"),"control_ref":ref("ControlAssessment"),"rate_refs":arr(ref("Rate"),3),
    "mode":{"const":"archival_synthetic"},"revision":INT,"supersedes_ref":maybe(ref("View"))})
S["GroupState"]=obj({"owner_key":ID,"branch_key":ID,"sequence":INT,"instant":INT,
    "perimeter_ref":ref("PerimeterVersion"),"view_ref":ref("View"),"balances":BAL,"movements":MOV,
    "forked_from_ref":maybe(ref("GroupState"))})
S["Settlement"]=obj({"payer":ID,"payee":ID,"instant":INT,"currency":{"const":"USD"},
    "cash_consideration":RAT,"retained_fair_value":RAT,"sold_fraction":RAT,"retained_fraction":RAT,
    "control_lost":BOOL,"source_ref":ref("SourceAnchor")})
S["MethodDefinition"]=obj({"method_blob":BLOB,"source_ref":ref("SourceAnchor"),"profile_ref":ref("Profile")})
S["AccountingEventBasis"]=obj({"identity":IDENTITY,"stage":enum("A","O","R","D"),
    "opening_ref":ref("GroupState"),"target_perimeter_ref":ref("PerimeterVersion"),
    "entity_book_refs":arr(ref("EntityBook"),2),"settlement_ref":maybe(ref("Settlement")),
    "rate_refs":arr(ref("Rate"),3),"method_ref":ref("MethodDefinition"),"source_ref":ref("SourceAnchor"),
    "view_ref":ref("View"),"information_mode":enum("archival_synthetic","historical_investor")})
S["PostingAuthorization"]=obj({"basis_ref":ref("AccountingEventBasis"),"profile_ref":ref("Profile"),
    "view_ref":ref("View"),"posting_permitted":BOOL,"evidence_level":{"const":"authored-synthetic"}})
S["JournalProposal"]=obj({"basis_ref":ref("AccountingEventBasis"),"currency":{"const":"USD"},
    "entries":arr(obj({"event_id":ID,"lines":arr(LINE,2)}),1)})
S["EconomicDelta"]=obj({"basis_ref":ref("AccountingEventBasis"),"opening_ref":ref("GroupState"),
    "closing_ref":ref("GroupState"),"movement_change":MOV})
S["StateTransitionReceipt"]=obj({"request_ref":ref("OperationRequest"),"identity":IDENTITY,
    "basis_ref":ref("AccountingEventBasis"),"authorization_ref":ref("PostingAuthorization"),
    "journal_ref":ref("JournalProposal"),"delta_ref":ref("EconomicDelta"),
    "opening_ref":ref("GroupState"),"closing_ref":ref("GroupState"),"generation":INT,"status":{"const":"committed"}})
S["ReportMap"]=obj({"currency":{"const":"USD"},"interval_start":INT,"interval_end":INT,
    "profit_source":{"const":"movements_not_closing_income_accounts"},"cash_source":{"const":"cash_and_classified_movements"}})
REPORT=["cash","assets","liabilities","equity","goodwill","retained_investment","closing_nci",*PERF]
S["Report"]=obj({"state_ref":ref("GroupState"),"view_ref":ref("View"),"map_ref":ref("ReportMap"),
    "values":obj({k:RAT for k in REPORT})})
S["Obligation"]=obj({"code":ID,"required_input":TXT,"source_ref":ref("SourceAnchor")})
S["Domain"]=obj({"request_ref":ref("OperationRequest"),"meaning":{"const":"singleton_request_decision"}})
S["Region"]=obj({"domain_ref":ref("Domain"),"predicate":{"const":"this_request"}})
ARGS={"accounting.commit@1":obj({k:ref(v) for k,v in [
    ("basis_ref","AccountingEventBasis"),("authorization_ref","PostingAuthorization"),("journal_ref","JournalProposal"),("delta_ref","EconomicDelta")]}),
    "report.build@1":obj({"state_ref":ref("GroupState"),"statement_map_ref":ref("ReportMap"),"view_ref":ref("View"),"require_current":BOOL})}
S["OperationRequest"]=obj({"operation":enum(*ARGS),"request_id":ID,"workspace_key":ID,
    "profile_ref":ref("Profile"),"signature_ref":ref("OperationSignature"),"view_ref":ref("View"),
    "arguments":{"oneOf":[obj({"tag":{"const":op},"value":a}) for op,a in ARGS.items()]},
    "execution":obj({"mode":{"const":"specification_example"},"budget":obj({"operation_count":INT,"elapsed_seconds":INT}),
        "environment_ref":ref("Environment")}),"expected_head":maybe(HEAD)})
S.update({"Arguments."+k:v for k,v in ARGS.items()})

def balances(values):return {a:q(values.get(a,0)) for a in ACCOUNTS}
def movements(values):return {a:q(values.get(a,0)) for a in PERF}
def post(b,entries):
    b={k:F(v["n"])/F(v["d"]) for k,v in b.items()}
    for e in entries:
        for a,v in e["lines"]:b[a]+=F(v)
    return balances(b)
def main():
    assert not (OUT/"portable-exchanges.json").exists(),"Preserve completed evidence."
    schema={"$schema":"https://json-schema.org/draft/2020-12/schema","schema_ids":{k:sid(k) for k in S},"$defs":S}
    (OUT/"record-schemas.json").write_text(json.dumps(schema,indent=2)+"\n")
    contract=ROOT/"docs/design/proposal/architecture/group-bindings-20261015.md"
    lock=add("SchemaLock","schema-lock",{"schema_blob":blob(OUT/"record-schemas.json"),"semantic_contract_blob":blob(contract),"format":"jsonschema2020-12"})
    profile=add("Profile","profile",{"profile_id":"GroupForeignOperation/1","schema_lock_ref":lock,
        "operations":list(ARGS),"book_mode":"synthetic","execution_mode":"specification_example"})
    signatures={op:add("OperationSignature","signature."+op,{"operation":op,"profile_ref":profile,
        "arguments_definition":"Arguments."+op,"payload_kinds":["StateTransitionReceipt"] if op.startswith("accounting") else ["Report"],
        "effects":"accounting_transaction" if op.startswith("accounting") else "read"}) for op in ARGS}
    environment=add("Environment","environment",{"purpose":"documentary_fixture","numerics":"exact_rational","runtime_executed":False})
    decoder=add("Decoder","decoder",{"media_type":"application/json","canonical_encoding":"accdsl.portable.v1"})
    source=add("SourceAnchor","source",{"case_blob":blob(OLD/"group-cases.json"),
        "method_blob":blob(ROOT/"docs/design/proposal/methods/group-fx-disposal-20261014.md"),
        "source_manifest_blob":blob(OLD/"source-manifest.json"),
        "source_pdf_blob":blob(ROOT/"docs/design/research/p08-v3-preparation/eu-2023-1803-original.pdf"),
        "source_excerpt_blob":blob(OLD/"selected-source-pages.txt"),
        "common_contract_blob":blob(ROOT/"docs/design/proposal/architecture/interfaces-contract-v1.md"),
        "scope":"Historical IFRS3/10/IAS21/IAS7; relative synthetic calendar; no current applicability"})
    method=add("MethodDefinition","method",{"method_blob":blob(contract),"source_ref":source,"profile_ref":profile})
    entities={k:add("Entity",k,{"entity_id":k,"display_name":"Example Company" if k!="Group-P" else "Example Consolidation",
        "functional_currency":"EUR" if k=="Subsidiary-S" else "USD","legal_entity":k!="Group-P"})
        for k in ["Parent-P","Subsidiary-S","Group-P","Other-S"]}
    control=add("ControlAssessment","control",{"parent_ref":entities["Parent-P"],"subsidiary_ref":entities["Subsidiary-S"],
        "start_inclusive":1,"end_exclusive":4,"power":"supported","variable_returns":True,"power_affects_returns":True,
        "ownership":q("4/5"),"nci_fraction":q("1/5"),"ordinary_equal_rights":True,"source_ref":source})
    unknown_control=add("ControlAssessment","control-unknown",{**body(control),"power":"unknown"})
    rates=[add("Rate","rate."+str(t),{"base":"EUR","quote":"USD","instant":t,"quote_per_base":q(v),"source_ref":source})
           for t,v in [(1,"6/5"),(2,"5/4"),(3,"13/10")]]
    view=add("View","view.original",{"source_ref":source,"control_ref":control,"rate_refs":rates,
        "mode":"archival_synthetic","revision":0,"supersedes_ref":None})
    changed_rate=add("Rate","rate.corrected",{**body(rates[-1]),"quote_per_base":q("7/5")})
    revised=add("View","view.corrected",{**body(view),"rate_refs":rates[:2]+[changed_rate],"revision":1,"supersedes_ref":view})
    unknown_view=add("View","view.unknown-control",{**body(view),"control_ref":unknown_control})
    unknown_rate=add("Rate","rate.unknown",{**body(rates[-1]),"quote_per_base":None})
    unknown_rate_view=add("View","view.unknown-rate",{**body(view),"rate_refs":rates[:2]+[unknown_rate]})
    books={}
    for stage,t in [("A-pre",0),("A",1),("O",2),("R",3)]:
        for entity,currency,values in [
            ("Parent-P","USD",{"Cash":300,"Parent capital":-300} if t==0 else
             {"Cash":"924/5","Retained investment":"576/5","Parent capital":-300}),
            ("Subsidiary-S","EUR",{"Cash":20,"Inventory":140,"Payable":-60,"Parent capital":-100} if t<=1 else
             {"Cash":120,"Parent capital":-100,"Parent operating retained profit":-20})]:
            books[(stage,entity)]=add("EntityBook","book."+stage+"."+entity,{"entity_ref":entities[entity],
                "book_id":"Legal","instant":t,"currency":currency,"balances":balances(values),"source_ref":source})
    wrong_book=add("EntityBook","book.same-label-wrong-entity",{**body(books[("R","Subsidiary-S")]),"entity_ref":entities["Other-S"]})
    perimeters={}
    for stage,t in [("A-pre",0),("A",1),("O",2),("R",3),("D",4)]:
        bookstage="R" if stage=="D" else stage
        perimeters[stage]=add("PerimeterVersion","perimeter."+stage,{"group_entity_ref":entities["Group-P"],
            "parent_ref":entities["Parent-P"],"subsidiary_ref":entities["Subsidiary-S"],"control_ref":control,
            "instant":t,"includes_subsidiary":0<t<4,"presentation_currency":"USD",
            "nci_policy":"proportionate_identifiable_net_assets","policy_alignment":"supplied_no_adjustment",
            "entity_book_refs":[books[(bookstage,e)] for e in ["Parent-P","Subsidiary-S"]]})
    def state(key,branch,seq,stage,bal,mov,fork=None):
        return add("GroupState",key,{"owner_key":"Group-P/Consolidated/"+branch,"branch_key":branch,
            "sequence":seq,"instant":body(perimeters[stage])["instant"],"perimeter_ref":perimeters[stage],
            "view_ref":view,"balances":bal,"movements":mov,"forked_from_ref":fork})
    initial=state("state.initial","common",0,"A-pre",balances({"Cash":300,"Parent capital":-300}),movements({}))
    case=json.loads((OLD/"group-cases.json").read_text())
    groups=[("A",case["group_journals"][:1],{"cfi_acquisition":"-456/5","nci_introduced":24}),
            ("O",case["group_journals"][1:5],{"profit":25,"parent_profit":20,"nci_profit":5,
                "oci":5,"parent_oci":4,"nci_oci":1,"cfo":125,"cfi_acquisition":"-456/5","cash_fx":1,"nci_introduced":24}),
            ("R",case["group_journals"][5:],{"profit":25,"parent_profit":20,"nci_profit":5,
                "oci":"63/5","parent_oci":"52/5","nci_oci":"11/5","cfo":125,"cfi_acquisition":"-456/5","cash_fx":7,"nci_introduced":24})]
    bundles={};states={"initial":initial}
    def bundle(key,branch,stage,opening,entries,mov,settlement=None):
        closing=state("state."+key,branch,body(opening)["sequence"]+1,stage,post(body(opening)["balances"],entries),movements(mov))
        basis=add("AccountingEventBasis","basis."+key,{"identity":{"entity_id":"Group-P","book_id":"Consolidated",
            "branch_key":branch,"business_event_id":key},"stage":stage,"opening_ref":opening,
            "target_perimeter_ref":perimeters[stage],"entity_book_refs":body(perimeters[stage])["entity_book_refs"],
            "settlement_ref":settlement,"rate_refs":rates,"method_ref":method,"source_ref":source,"view_ref":view,
            "information_mode":"archival_synthetic"})
        authorization=add("PostingAuthorization","authorization."+key,{"basis_ref":basis,"profile_ref":profile,
            "view_ref":view,"posting_permitted":True,"evidence_level":"authored-synthetic"})
        journal=add("JournalProposal","journal."+key,{"basis_ref":basis,"currency":"USD",
            "entries":[{"event_id":e["id"],"lines":[{"account":a,"signed_amount":q(v)} for a,v in e["lines"]]} for e in entries]})
        changes={k:F(body(closing)["movements"][k]["n"])/F(body(closing)["movements"][k]["d"])-
                   F(body(opening)["movements"][k]["n"])/F(body(opening)["movements"][k]["d"]) for k in PERF}
        delta=add("EconomicDelta","delta."+key,{"basis_ref":basis,"opening_ref":opening,"closing_ref":closing,"movement_change":movements(changes)})
        bundles[key]={"basis_ref":basis,"authorization_ref":authorization,"journal_ref":journal,"delta_ref":delta}
        states[key]=closing
        return closing
    opening=initial
    for stage,entries,mov in groups:opening=bundle(stage,"common",stage,opening,entries,mov)
    for arm,b in case["alternatives"].items():
        fork=state("fork."+arm,arm,0,"R",deepcopy(body(opening)["balances"]),deepcopy(body(opening)["movements"]),opening)
        settlement=add("Settlement","settlement."+arm,{"payer":"ExternalBuyer","payee":"Parent-P","instant":4,
            "currency":"USD","cash_consideration":q(b["proceeds_usd"]),"retained_fair_value":q(b["retained_fv_usd"]),
            "sold_fraction":q(b["sold_fraction"]),"retained_fraction":q(b["retained_fraction"]),"control_lost":True,"source_ref":source})
        entries=[{"id":"D-deconsolidate","lines":b["journal"]},{"id":"D-recycle-parent","lines":[["Parent CTA","52/5"],["Disposal gain","-52/5"]]}]
        mov={"profit":"294/5","parent_profit":"269/5","nci_profit":5,"oci":"11/5","parent_oci":0,"nci_oci":"11/5",
            "cfo":125,"cfi_acquisition":"-456/5","cfi_disposal":b["expected"]["net_disposal_cash"],"cash_fx":7,
            "nci_introduced":24,"nci_removed":"156/5"}
        bundle(arm,arm,"D",fork,entries,mov,settlement)
    def head(st):return {"owner_key":body(st)["owner_key"],"state_ref":st,"generation":body(st)["sequence"]}
    def closure(roots):
        seen=set()
        def visit(r):
            if r["digest"] in seen:return
            seen.add(r["digest"])
            for dep in REG[r["digest"]]["dependencies"]:visit(dep)
        for r in roots:visit(r)
        return sorted(seen)
    legal=[r for r in ALIASES.values() if r["kind"]=="EntityBook"]
    def world(st):return {"head":head(st),"event_receipts":{},"journals":[],"deltas":[],"receipts":[],
        "published_records":closure([st,*legal]),"unaffected_owners":{
        "Parent-P/Legal":{"state_ref":books[("R","Parent-P")],"generation":3},
        "Subsidiary-S/Legal":{"state_ref":books[("R","Subsidiary-S")],"generation":3}}}
    def request(key,op,args,st=None,v=view,budget=1000):
        r=add("OperationRequest","request."+key,{"operation":op,"request_id":key,"workspace_key":"Group-specification",
            "profile_ref":profile,"signature_ref":signatures[op],"view_ref":v,"arguments":{"tag":op,"value":args},
            "execution":{"mode":"specification_example","budget":{"operation_count":budget,"elapsed_seconds":60},"environment_ref":environment},
            "expected_head":head(st) if st else None})
        p=OUT/"bytes"/(key+".json");p.parent.mkdir(exist_ok=True);p.write_bytes(enc(REG[r["digest"]]))
        sub=add("Submission","submission."+key,{"blob_ref":blob(p),"media_type":"application/json","transport":"authored_fixture","decoder_ref":decoder})
        return r,sub
    def result(key,req,sub,disposition,outputs=(),receipt=None,code=None,valid=True):
        domain=add("Domain","domain."+key,{"request_ref":req,"meaning":"singleton_request_decision"}) if valid else None
        region=add("Region","region."+key,{"domain_ref":domain,"predicate":"this_request"}) if valid else None
        unresolved=[]
        if disposition=="partial":unresolved=[add("Obligation","obligation."+key,{"code":code,"required_input":code,"source_ref":source})]
        statuses={"structural_validity":"valid","mathematical_status":"unresolved" if code else "defined",
            "computation_status":"not_computed" if disposition=="rejected" else "partial" if disposition=="partial" else "complete",
            "empirical_justification":"not_established","capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed",
            "forecast_validity":"not_assessed","product_readiness":"not_implemented","human_acceptance":"pending"}
        coverage=None if not valid else {"domain_ref":domain,"completed":[] if disposition=="partial" else [region],
            "unresolved":[region] if disposition=="partial" else [],"unsupported":[],"infeasible":[],"cancelled":[],"relation":"disjoint_exhaustive"}
        return add("OperationResult","result."+key,{"submission_ref":sub,"request_ref":req if valid else None,
            "operation":body(req)["operation"] if valid else None,"input_view_ref":body(req)["view_ref"] if valid else None,
            "disposition":disposition,"statuses":statuses,"payload":None if not valid else
            {"tag":body(req)["operation"],"result_refs":list(outputs),"additional_commit":disposition=="completed" and receipt is not None},
            "diagnostics":[] if not code else [{"code":code,"stage":"binding_or_financial_validation","record_ref":None,
                "source_locator":None,"field_path":"arguments","affected_query_branch_ids":[],"dependency_path":[],
                "observed":code,"expected_rule":"GroupForeignOperation/1","retry_advice":"repair_named_input_or_resubmit_exact_request",
                "blocking_diagnostic_ids":[]}],"coverage":coverage,"unresolved":unresolved,"continuation_ref":None,
            "commit_observation":"committed" if disposition=="completed" and receipt else "not_committed",
            "receipt_ref":receipt,"evidence_mode":"specification_example"})
    success={}
    for key,args in bundles.items():
        op="accounting.commit@1";b=body(args["basis_ref"]);st=b["opening_ref"]
        req,sub=request(key,op,args,st)
        predecessor={"O":"A","R":"O"}.get(key)
        before=deepcopy(success[predecessor][4]) if predecessor else world(st)
        rec=add("StateTransitionReceipt","receipt."+key,{"request_ref":req,"identity":b["identity"],**args,
            "opening_ref":st,"closing_ref":states[key],"generation":body(states[key])["sequence"],"status":"committed"})
        after=deepcopy(before);after["head"]=head(states[key]);event="/".join(b["identity"].values())
        after["event_receipts"][event]={"request_ref":req,"receipt_ref":rec}
        for dst,rr in [("journals",args["journal_ref"]),("deltas",args["delta_ref"]),("receipts",rec)]:after[dst].append(rr)
        after["published_records"]=sorted(set(before["published_records"])|set(closure([rec])))
        res=result(key,req,sub,"completed",[rec],rec)
        EX.append({"id":key,"request_ref":req,"submission_ref":sub,"response_ref":res,"world_before":before,"world_after":after})
        success[key]=(req,sub,rec,before,after)
    # Exact retries retain original request bytes and opening head.
    req,sub,rec,before,after=success["retain_twenty_percent"]
    replay=result("replay",req,sub,"replayed",[rec],rec)
    EX.append({"id":"replay","request_ref":req,"submission_ref":sub,"response_ref":replay,"world_before":after,"world_after":deepcopy(after)})
    obs=add("TransportObservation","lost-ack",{"submission_ref":sub,"request_ref":req,
        "observation":"acknowledgement_timeout","commit_observation":"unknown","receipt_ref":None,"next_action":"resubmit_exact_original_request"})
    lost={"observation_ref":obs,"before_publication":before,"after_publication":after,
        "retry_before_exchange":"retain_twenty_percent","retry_after_exchange":"replay"}
    partial_publication=deepcopy(before)
    partial_publication["event_receipts"]=deepcopy(after["event_receipts"])
    # Source and binding variants retain real records, never fake digest pointers.
    wrong_rate=add("Rate","rate.reverse",{**body(rates[-1]),"base":"USD","quote":"EUR"})
    late_rate=add("Rate","rate.wrong-time",{**body(rates[-1]),"instant":5})
    base_args=bundles["retain_twenty_percent"]
    for key,change,code in [
        ("wrong_entity",{"entity_book_refs":[books[("R","Parent-P")],wrong_book]},"entity_mismatch"),
        ("wrong_rate_direction",{"rate_refs":rates[:2]+[wrong_rate]},"currency_direction_mismatch"),
        ("wrong_rate_time",{"rate_refs":rates[:2]+[late_rate]},"rate_time_mismatch"),
        ("historical_investor",{"information_mode":"historical_investor"},"missing_public_time"),
        ("wrong_branch",{"identity":{**body(base_args["basis_ref"])["identity"],"branch_key":"full_sale"}},"branch_mismatch")]:
        b=add("AccountingEventBasis","basis."+key,{**body(base_args["basis_ref"]),**change})
        a=add("PostingAuthorization","authorization."+key,{**body(base_args["authorization_ref"]),"basis_ref":b})
        j=add("JournalProposal","journal."+key,{**body(base_args["journal_ref"]),"basis_ref":b})
        dd=add("EconomicDelta","delta."+key,{**body(base_args["delta_ref"]),"basis_ref":b})
        rq,su=request(key,"accounting.commit@1",{"basis_ref":b,"authorization_ref":a,"journal_ref":j,"delta_ref":dd},body(b)["opening_ref"])
        rr=result(key,rq,su,"rejected",code=code,valid=False)
        EX.append({"id":key,"request_ref":rq,"submission_ref":su,"response_ref":rr,"world_before":before,"world_after":deepcopy(before)})
    for key,code,budget,starting in [("changed_request","idempotency_conflict",1000,after),
            ("changed_budget","idempotency_conflict",999,after)]:
        rq,su=request(key,"accounting.commit@1",base_args,body(base_args["basis_ref"])["opening_ref"],budget=budget)
        rr=result(key,rq,su,"rejected",code=code)
        EX.append({"id":key,"request_ref":rq,"submission_ref":su,"response_ref":rr,"world_before":starting,"world_after":deepcopy(starting)})
    for key,code in [("retained_value_as_cash","wrong_cash_target"),("recycle_nci","wrong_reserve_owner"),
                     ("partial_sub_cash_removal","wrong_disposal_perimeter")]:
        jb=deepcopy(body(base_args["journal_ref"]))
        if key=="retained_value_as_cash":
            for line in jb["entries"][0]["lines"]:
                if line["account"]=="Retained investment":line["account"]="Cash"
        elif key=="recycle_nci":
            jb["entries"][1]["lines"]=[
                {"account":"Parent CTA","signed_amount":q("63/5")},
                {"account":"Disposal gain","signed_amount":q("-63/5")}]
        else:
            for line in jb["entries"][0]["lines"]:
                if line["account"]=="Cash" and line["signed_amount"]==q(-156):line["signed_amount"]=q("-624/5")
                elif line["account"]=="Disposal gain":line["signed_amount"]=q("-273/5")
        jr=add("JournalProposal","journal."+key,jb)
        rq,su=request(key,"accounting.commit@1",{**base_args,"journal_ref":jr},body(base_args["basis_ref"])["opening_ref"])
        rr=result(key,rq,su,"rejected",code=code,valid=False)
        EX.append({"id":key,"request_ref":rq,"submission_ref":su,"response_ref":rr,"world_before":before,"world_after":deepcopy(before)})
    # A valid new event on an advanced branch is stale, not a replay.
    args=deepcopy(base_args);bb=deepcopy(body(args["basis_ref"]));bb["identity"]["business_event_id"]="new-disposal"
    args["basis_ref"]=add("AccountingEventBasis","basis.new-disposal",bb)
    for field,kind in [("authorization_ref","PostingAuthorization"),("journal_ref","JournalProposal"),("delta_ref","EconomicDelta")]:
        args[field]=add(kind,field+".new-disposal",{**body(base_args[field]),"basis_ref":args["basis_ref"]})
    rq,su=request("stale_new_event","accounting.commit@1",args,bb["opening_ref"])
    rr=result("stale_new_event",rq,su,"rejected",code="stale_head")
    EX.append({"id":"stale_new_event","request_ref":rq,"submission_ref":su,"response_ref":rr,"world_before":after,"world_after":deepcopy(after)})
    mapref=add("ReportMap","report-map",{"currency":"USD","interval_start":0,"interval_end":4,
        "profit_source":"movements_not_closing_income_accounts","cash_source":"cash_and_classified_movements"})
    for key,st in [("report-full",states["full_sale"]),("report-retained",states["retain_twenty_percent"])]:
        b=body(st);v={k:F(z["n"])/F(z["d"]) for k,z in b["balances"].items()}
        values={"cash":v["Cash"],"assets":v["Cash"]+v["Goodwill"]+v["Inventory"]+v["Retained investment"],
            "liabilities":-v["Payable"],"equity":-sum(v[a] for a in ["Parent capital","Parent operating retained profit","Parent CTA","NCI","Disposal gain"]),
            "goodwill":v["Goodwill"],"retained_investment":v["Retained investment"],"closing_nci":-v["NCI"]}
        report=add("Report",key,{"state_ref":st,"view_ref":view,"map_ref":mapref,
            "values":{**{k:q(x) for k,x in values.items()},**b["movements"]}})
        args={"state_ref":st,"statement_map_ref":mapref,"view_ref":view,"require_current":False}
        rq,su=request(key,"report.build@1",args)
        rr=result(key,rq,su,"completed",[report]);w=world(st)
        EX.append({"id":key,"request_ref":rq,"submission_ref":su,"response_ref":rr,"world_before":w,"world_after":deepcopy(w)})
    for key,v,code in [("current-after-correction",revised,"stale_dependency_view"),
            ("unknown-control",unknown_view,"control_assessment_unresolved"),
            ("unknown-rate",unknown_rate_view,"rate_measurement_unresolved")]:
        args={"state_ref":states["retain_twenty_percent"],"statement_map_ref":mapref,"view_ref":v,"require_current":True}
        rq,su=request(key,"report.build@1",args,v=v)
        partial=key.startswith("unknown-")
        rr=result(key,rq,su,"partial" if partial else "rejected",code=code,valid=partial)
        EX.append({"id":key,"request_ref":rq,"submission_ref":su,"response_ref":rr,"world_before":after,"world_after":deepcopy(after)})
    packet={"evidence_mode":"specification_example","product_implemented":False,"schema_lock_ref":lock,
        "profile_ref":profile,"record_registry":REG,"aliases":ALIASES,"blobs":BLOBS,"exchanges":EX,
        "lost_acknowledgement":lost,"invalid_partial_publication":partial_publication,
        "source_pins":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in
            [OLD/"group-cases.json",OLD/"source-manifest.json",OLD/"selected-source-pages.txt",
             ROOT/"data/accounting-master/corporate-portable-20261015/record-schemas.json"]]}
    (OUT/"portable-exchanges.json").write_text(json.dumps(packet,indent=2)+"\n")
    print(json.dumps({"records":len(REG),"exchanges":len(EX),"blobs":len(BLOBS)}))
if __name__=="__main__":main()
