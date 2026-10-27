"""Author complete finite portable exchanges; never write a live accounting book."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
REGISTRY, ALIASES, BLOBS = {}, {}, {}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def rat(n, d=1):
    value = Fraction(n, d)
    return {"n":str(value.numerator), "d":str(value.denominator)}


def schema_id(kind):
    common = {"OperationRequest":"accdsl.operation.request.v1",
              "OperationResult":"accdsl.operation.result.v1"}
    return common.get(kind, "accdsl.advance-allocation."+kind.lower()+".v1")


def refs(value):
    if isinstance(value, dict):
        if set(value) == {"kind","schema","digest"}:
            yield value
        else:
            for child in value.values():
                yield from refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from refs(child)


def add(kind, key, body):
    deps = {canonical(r):r for r in refs(body)}
    record = {"kind":kind,"schema":schema_id(kind),"key":key,"revision":0,
              "body":body,"dependencies":[deps[k] for k in sorted(deps)]}
    digest = hashlib.sha256(("accdsl.portable.v1/"+record["schema"]).encode()+b"\0"+canonical(record)).hexdigest()
    REGISTRY[digest] = record
    ref = {"kind":kind,"schema":record["schema"],"digest":digest}
    ALIASES[key] = ref
    return ref


def blob(path):
    path = Path(path)
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    BLOBS[digest] = {"path":str(path.relative_to(ROOT)),"byte_length":len(data)}
    return {"kind":"blob","algorithm":"sha256","digest":digest,"byte_length":len(data)}


def closed(fields):
    return {"type":"object","properties":fields,"required":list(fields),"additionalProperties":False}


def arr(items, minimum=0):
    return {"type":"array","items":items,"minItems":minimum}


def nullable(value):
    return {"anyOf":[value,{"type":"null"}]}


def ref(kind=None):
    fields = {"kind": {"const":kind} if kind else TEXT,
              "schema": {"const":schema_id(kind)} if kind else TEXT,
              "digest":{"type":"string","pattern":"^[0-9a-f]{64}$"}}
    return closed(fields)


TEXT = {"type":"string","minLength":1}
IDENT = {"type":"string","pattern":"^[A-Za-z0-9_.:@/-]+$"}
BOOL = {"type":"boolean"}
INT = {"type":"integer","minimum":0}
RAT = closed({"n":{"type":"string","pattern":"^(0|-?[1-9][0-9]*)$"},
              "d":{"type":"string","pattern":"^[1-9][0-9]*$"}})
BLOB = closed({"kind":{"const":"blob"},"algorithm":{"const":"sha256"},
               "digest":{"type":"string","pattern":"^[0-9a-f]{64}$"},"byte_length":INT})
IDENTITY = closed({k:IDENT for k in ["entity_id","book_id","branch_key","business_event_id"]})
HEAD = closed({"owner_key":IDENT,"state_ref":ref("CompanyState"),"generation":INT})
ACCOUNTS = ["cash","accounts_receivable","contract_asset","contract_liability","revenue"]
BALANCES = closed({k:RAT for k in ACCOUNTS})
ECONOMIC = closed({"contract_id":IDENT,"price":RAT,"R":RAT,"G":RAT,"A":RAT,"K":RAT,"C":RAT,
    "advances":arr(closed({"advance_id":IDENT,"received":RAT,"applied":RAT}),1),
    "invoices":arr(closed({"invoice_id":IDENT,"gross":RAT,"applied":RAT,"unpaid":RAT})),
    "allocations":arr(closed({"advance_id":IDENT,"invoice_id":IDENT,"amount":RAT}))})
FINDING = closed({"name":IDENT,"status":{"enum":["satisfied","failed","unknown"]},"support":TEXT})
ARGS = closed({"basis_ref":ref("AccountingEventBasis"),"authorization_ref":ref("PostingAuthorization"),
               "journal_ref":ref("JournalProposal"),"delta_ref":ref("EconomicDelta")})
DIAGNOSTIC = closed({"code":IDENT,"stage":TEXT,"record_ref":nullable(ref()),
    "source_locator":nullable(TEXT),"field_path":TEXT,"affected_query_branch_ids":arr(IDENT),
    "dependency_path":arr(ref()),"observed":TEXT,"expected_rule":TEXT,"retry_advice":TEXT,
    "blocking_diagnostic_ids":arr(IDENT)})
SCHEMAS = {
    "SchemaLock":closed({"schema_blob":BLOB,"semantic_contract_blob":BLOB,"format":{"const":"jsonschema2020-12"}}),
    "SourceSupport":closed({"source_blob":BLOB,"locator":TEXT,"scope":TEXT}),
    "SyntheticAuthority":closed({"source_ref":ref("SourceSupport"),"nature":{"const":"authored_synthetic"},"limit":TEXT}),
    "MethodDefinition":closed({"method_id":IDENT,"version":INT,"event_kind":IDENT,
        **{k:TEXT for k in ["state_schema","event_schema","journal_schema","delta_schema","output_schema"]},
        "required_contexts":arr(TEXT,1),"authority_requirements":arr(ref("SyntheticAuthority"),1),
        "preconditions":arr(TEXT,1),"algorithm":TEXT,"account_roles":arr(IDENT,1),"report_mappings":TEXT,
        "numerical_capability":TEXT,"examples":arr(TEXT,1),"unsupported_cases":arr(TEXT,1)}),
    "PostingProfile":closed({"profile_id":IDENT,"version":INT,"schema_lock_ref":ref("SchemaLock"),
        "method_ref":ref("MethodDefinition"),"supported_book_modes":arr({"enum":["synthetic","real"]},1),
        "operations":arr(IDENT)}),
    "OperationSignature":closed({"operation":{"const":"accounting.commit@1"},"schema_lock_ref":ref("SchemaLock"),
        "argument_fields":arr(IDENT,4),"result_schema":{"const":schema_id("OperationResult")}}),
    "View":closed({"view_id":IDENT,"mode":{"const":"synthetic"},"historical_availability_claim":{"const":False}}),
    "Context":closed({"entity_id":IDENT,"book_id":IDENT,"currency":{"const":"CU"},"unit":{"const":"units"},
        "scale":{"const":0},"basis":TEXT,"annual_period_start":{"type":"string","format":"date"},"perimeter":TEXT}),
    "Branch":closed({"branch_key":IDENT,"book_mode":{"enum":["synthetic","real"]},"view_ref":ref("View"),"family_id":IDENT}),
    "Time":closed({"economic_date":{"type":"string","format":"date"},"reporting_start":{"type":"string","format":"date"},
        "reporting_end":{"type":"string","format":"date"},"view_ref":ref("View"),"availability_scope":TEXT}),
    "Chart":closed({"context_ref":ref("Context"),"accounts":arr(closed({"account_id":IDENT,"concept_id":IDENT,"normal_side":{"enum":["debit","credit"]}}),1)}),
    "Assumptions":closed({"contract_id":IDENT,"price":RAT,"advance_precedes_all_performance_and_billing":BOOL,
        "no_refund_financing_tax_or_impairment_in_slice":BOOL,"fact_status":{"const":"authored_synthetic"}}),
    "Evidence":closed({"assumptions_ref":ref("Assumptions"),"source_ref":ref("SourceSupport"),"nature":{"const":"authored_synthetic"}}),
    "Admission":closed({"evidence_ref":ref("Evidence"),"view_ref":ref("View"),"status":{"const":"synthetic_only"},"reason":TEXT}),
    "CompanyState":closed({"context_ref":ref("Context"),"branch_ref":ref("Branch"),"chart_ref":ref("Chart"),"sequence":INT,"balances":BALANCES,"contract":ECONOMIC}),
    "EconomicEvent":closed({"business_event_id":IDENT,"version":INT,"kind":{"const":"allocate_prepaid_invoice"},
        "context_ref":ref("Context"),"branch_ref":ref("Branch"),"time_ref":ref("Time"),"contract_id":IDENT,
        "invoice_id":IDENT,"advance_id":IDENT,"gross":RAT,"applied_credit":RAT}),
    "AccountingEventBasis":closed({"identity":IDENTITY,"event_ref":ref("EconomicEvent"),"opening_ref":ref("CompanyState"),
        "context_ref":ref("Context"),"branch_ref":ref("Branch"),"time_ref":ref("Time"),"chart_ref":ref("Chart"),
        "authority_refs":arr(ref("SyntheticAuthority"),1),"method_ref":ref("MethodDefinition"),"evidence_refs":arr(ref("Evidence"),1),
        "admission_refs":arr(ref("Admission"),1),"assumptions_ref":ref("Assumptions"),"view_ref":ref("View")}),
    "PostingAuthorization":closed({"basis_ref":ref("AccountingEventBasis"),"posting_profile_ref":ref("PostingProfile"),
        "method_ref":ref("MethodDefinition"),"authority_refs":arr(ref("SyntheticAuthority"),1),
        "status":{"enum":["eligible","unresolved","ineligible","outside_scope"]},"findings":arr(FINDING,1),
        "posting_permitted":BOOL,"evidence_level":{"const":"authored-synthetic"},"view_ref":ref("View")}),
    "JournalProposal":closed({"basis_ref":ref("AccountingEventBasis"),"authorization_ref":ref("PostingAuthorization"),
        "context_ref":ref("Context"),"chart_ref":ref("Chart"),"effect":{"const":"state_only"},"lines":{"type":"array","maxItems":0}}),
    "EconomicDelta":closed({"basis_ref":ref("AccountingEventBasis"),"authorization_ref":ref("PostingAuthorization"),
        "context_ref":ref("Context"),"chart_ref":ref("Chart"),"account_changes":BALANCES,"before_contract":ECONOMIC,"after_contract":ECONOMIC}),
    "Environment":closed({"purpose":{"const":"documentary_fixture"},"numerics":{"const":"exact_rational"},"runtime_executed":{"const":False}}),
    "Decoder":closed({"media_type":{"const":"application/json"},"canonical_encoding":{"const":"accdsl.portable.v1"}}),
    "OperationRequest":closed({"operation":{"const":"accounting.commit@1"},"request_id":IDENT,"workspace_key":IDENT,
        "profile_ref":ref("PostingProfile"),"signature_ref":ref("OperationSignature"),"view_ref":ref("View"),"arguments":ARGS,
        "execution":closed({"mode":{"const":"specification_example"},"budget":closed({"operation_count":INT,"elapsed_seconds":INT}),"environment_ref":ref("Environment")}),
        "expected_head":HEAD}),
    "Submission":closed({"blob_ref":BLOB,"media_type":{"const":"application/json"},"transport":{"const":"documentary_file"},"decoder_ref":ref("Decoder")}),
    "StateTransitionReceipt":closed({"request_ref":ref("OperationRequest"),"identity":IDENTITY,"basis_ref":ref("AccountingEventBasis"),
        "authorization_ref":ref("PostingAuthorization"),"journal_ref":ref("JournalProposal"),"delta_ref":ref("EconomicDelta"),
        "opening_ref":ref("CompanyState"),"closing_ref":ref("CompanyState"),"generation":INT,"status":{"const":"committed"}}),
    "RequestDomain":closed({"request_ref":ref("OperationRequest"),"meaning":{"const":"singleton_request_decision"}}),
    "RequestRegion":closed({"domain_ref":ref("RequestDomain"),"predicate":{"const":"this_request_decision"},"status":{"const":"completed"}}),
}
STATUS = closed({"structural_validity":{"enum":["valid","invalid"]},"mathematical_status":{"enum":["defined","failed","unresolved"]},
    "computation_status":{"enum":["complete","not_computed"]},"empirical_justification":{"const":"not_established"},
    "capability_status":{"const":"specified_only_no_runtime"},"accounting_validity":{"const":"not_assessed"},
    "forecast_validity":{"const":"not_assessed"},"product_readiness":{"const":"not_implemented"},"human_acceptance":{"const":"pending"}})
COVERAGE = closed({"domain_ref":ref("RequestDomain"),"completed":arr(ref("RequestRegion")),
    **{k:arr(ref("RequestRegion")) for k in ["unresolved","unsupported","infeasible","cancelled"]},"relation":{"const":"singleton_partition"}})
PAYLOAD = closed({"kind":{"const":"state_only_commit"},"event_committed":BOOL,"additional_commit":BOOL,
    "observed_head":HEAD,"original_receipt_ref":nullable(ref("StateTransitionReceipt"))})
SCHEMAS["OperationResult"] = closed({"submission_ref":ref("Submission"),"request_ref":nullable(ref("OperationRequest")),
    "operation":nullable(IDENT),"input_view_ref":nullable(ref("View")),"disposition":{"enum":["completed","replayed","rejected","unsupported"]},
    "statuses":STATUS,"payload":nullable(PAYLOAD),"diagnostics":arr(DIAGNOSTIC),"coverage":nullable(COVERAGE),
    "unresolved":arr(TEXT),"continuation_ref":{"type":"null"},"commit_observation":{"enum":["committed","not_committed"]},
    "receipt_ref":nullable(ref("StateTransitionReceipt")),"evidence_mode":{"const":"specification_example"}})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    schemas = {"$schema":"https://json-schema.org/draft/2020-12/schema",
        "description":"Closed body schemas for this authored synthetic package; L1 wrappers and semantic predicates additionally apply.",
        "schema_ids":{k:schema_id(k) for k in SCHEMAS},"$defs":SCHEMAS}
    (OUT/"record-schemas.json").write_text(json.dumps(schemas,indent=2)+"\n")
    contract = ROOT/"docs/design/proposal/architecture/state-only-advance-allocation-20261014.md"
    lock = add("SchemaLock","schema-lock",{"schema_blob":blob(OUT/"record-schemas.json"),"semantic_contract_blob":blob(contract),"format":"jsonschema2020-12"})
    source = add("SourceSupport","aasb15-support",{"source_blob":blob(ROOT/"docs/design/proposal/methods/sources/aasb15-compiled-dec2022.pdf"),
        "locator":"105-108; compilation 8, 31 December 2022, F2023C00402","scope":"Historical Australian for-profit annual starts 2023-01-01 inclusive through 2026-07-01 exclusive; facts remain synthetic."})
    authority = add("SyntheticAuthority","synthetic-authority",{"source_ref":source,"nature":"authored_synthetic", "limit":"Stipulated advance/allocation facts; no real-book authorization or full compliance claim."})
    method = add("MethodDefinition","advance-allocation-method",{"method_id":"allocate-prepaid-bill","version":1,"event_kind":"allocate_prepaid_invoice",
        "state_schema":schema_id("CompanyState"),"event_schema":schema_id("EconomicEvent"),"journal_schema":schema_id("JournalProposal"),
        "delta_schema":schema_id("EconomicDelta"),"output_schema":schema_id("StateTransitionReceipt"),"required_contexts":["same entity, book, branch, contract, CU and historical rule scope"],
        "authority_requirements":[authority],"preconditions":["positive gross equals identified unused advance applied","new invoice ID","consistent aggregate and granular opening","contract bounds","synthetic admission"],
        "algorithm":"G += gross; K += credit; R,A,C unchanged; T=G+A-K, AR=G-K-C, CA=max(R-T,0), CL=max(T-R,0); append invoice/allocation and consume identified credit; all account effects zero.",
        "account_roles":ACCOUNTS,"report_mappings":"No revenue, cash flow, equity or monetary balance change; allocation memory changes.","numerical_capability":"reduced exact rationals",
        "examples":["advance30, gross30, applied30"],"unsupported_cases":["monetary invoice","real book","refund, impairment, financing or tax measurement"]})
    profile = add("PostingProfile","advance-allocation-profile",{"profile_id":"authored.customer.prepaid-bill.v1","version":1,"schema_lock_ref":lock,
        "method_ref":method,"supported_book_modes":["synthetic"],"operations":["accounting.commit@1"]})
    unsupported = add("PostingProfile","unsupported-profile",{**REGISTRY[profile["digest"]]["body"],"profile_id":"authored.unsupported.v1","operations":[]})
    signature = add("OperationSignature","commit-signature",{"operation":"accounting.commit@1","schema_lock_ref":lock,"argument_fields":list(ARGS["properties"]),"result_schema":schema_id("OperationResult")})
    view = add("View","synthetic-view",{"view_id":"author-scenario-2024","mode":"synthetic","historical_availability_claim":False})
    context = add("Context","customer-context",{"entity_id":"Company","book_id":"Pretax","currency":"CU","unit":"units","scale":0,"basis":"authored historical AASB15 slice","annual_period_start":"2024-01-01","perimeter":"one synthetic legal entity"})
    branch = add("Branch","customer-branch",{"branch_key":"advance-case","book_mode":"synthetic","view_ref":view,"family_id":"authored-one-contract"})
    time = add("Time","billing-time",{"economic_date":"2024-07-01","reporting_start":"2024-01-01","reporting_end":"2024-12-31","view_ref":view,"availability_scope":"Synthetic scenario; no historical exact-byte availability claim."})
    chart = add("Chart","customer-chart",{"context_ref":context,"accounts":[{"account_id":k,"concept_id":k,"normal_side":"credit" if k in ["revenue","contract_liability"] else "debit"} for k in ACCOUNTS]})
    assumptions = add("Assumptions","advance-assumptions",{"contract_id":"C1","price":rat(100),"advance_precedes_all_performance_and_billing":True,
        "no_refund_financing_tax_or_impairment_in_slice":True,"fact_status":"authored_synthetic"})
    evidence = add("Evidence","advance-facts",{"assumptions_ref":assumptions,"source_ref":source,"nature":"authored_synthetic"})
    admission = add("Admission","advance-admission",{"evidence_ref":evidence,"view_ref":view,"status":"synthetic_only","reason":"Authored contract/cash/advance state; no actual company assertion."})
    environment = add("Environment","documentary-environment",{"purpose":"documentary_fixture","numerics":"exact_rational","runtime_executed":False})
    decoder = add("Decoder","portable-json",{"media_type":"application/json","canonical_encoding":"accdsl.portable.v1"})
    econ = {"contract_id":"C1","price":rat(100),"R":rat(0),"G":rat(0),"A":rat(30),"K":rat(0),"C":rat(0),
        "advances":[{"advance_id":"A1","received":rat(30),"applied":rat(0)}],"invoices":[],"allocations":[]}
    balances = {k:rat(30 if k=="cash" else -30 if k=="contract_liability" else 0) for k in ACCOUNTS}
    initial_body = {"context_ref":context,"branch_ref":branch,"chart_ref":chart,"sequence":0,"balances":balances,"contract":econ}
    opening = add("CompanyState","opening-state",initial_body)
    identity = {"entity_id":"Company","book_id":"Pretax","branch_key":"advance-case","business_event_id":"E1"}
    owner = "Company/Pretax/advance-case"
    start_world = {"head":{"owner_key":owner,"state_ref":opening,"generation":0},"identity_index":[],"committed_journal_refs":[],"committed_delta_refs":[],"receipt_refs":[]}
    cases = []

    def request_case(name, invoice="I1", event_id="E1", request_id="request-E1", op_profile=None,
                     open_ref=None, permission=True, eligible=True, delta_fault=None):
        op_profile = op_profile or profile
        open_ref = open_ref or opening
        before = deepcopy(REGISTRY[open_ref["digest"]]["body"]["contract"])
        event = add("EconomicEvent",name+"-event",{"business_event_id":event_id,"version":1,"kind":"allocate_prepaid_invoice",
            "context_ref":context,"branch_ref":branch,"time_ref":time,"contract_id":"C1","invoice_id":invoice,"advance_id":"A1","gross":rat(30),"applied_credit":rat(30)})
        basis = add("AccountingEventBasis",name+"-basis",{"identity":{**identity,"business_event_id":event_id},"event_ref":event,"opening_ref":open_ref,
            "context_ref":context,"branch_ref":branch,"time_ref":time,"chart_ref":chart,"authority_refs":[authority],"method_ref":method,
            "evidence_refs":[evidence],"admission_refs":[admission],"assumptions_ref":assumptions,"view_ref":view})
        findings = [{"name":"unused_credit","status":"satisfied" if eligible else "failed","support":"A1 unused credit in pinned opening"},
                    {"name":"zero_new_right","status":"satisfied","support":"gross30 minus applied30 equals zero"},
                    {"name":"new_invoice","status":"satisfied","support":"invoice absent in pinned opening"},
                    {"name":"synthetic_scope","status":"satisfied","support":"authored branch, profile and admission"}]
        authorization = add("PostingAuthorization",name+"-authorization",{"basis_ref":basis,"posting_profile_ref":op_profile,"method_ref":method,"authority_refs":[authority],
            "status":"eligible" if eligible else "ineligible","findings":findings,"posting_permitted":permission,"evidence_level":"authored-synthetic","view_ref":view})
        journal = add("JournalProposal",name+"-journal",{"basis_ref":basis,"authorization_ref":authorization,"context_ref":context,"chart_ref":chart,"effect":"state_only","lines":[]})
        after = deepcopy(before)
        after["G"] = rat(int(before["G"]["n"])+30)
        after["K"] = rat(int(before["K"]["n"])+30)
        after["advances"][0]["applied"] = rat(int(before["advances"][0]["applied"]["n"])+30)
        after["invoices"].append({"invoice_id":invoice,"gross":rat(30),"applied":rat(30),"unpaid":rat(0)})
        after["allocations"].append({"advance_id":"A1","invoice_id":invoice,"amount":rat(30)})
        changes = {k:rat(0) for k in ACCOUNTS}
        if delta_fault == "monetary": changes["accounts_receivable"] = rat(1)
        if delta_fault == "economic": after = deepcopy(before)
        delta = add("EconomicDelta",name+"-delta",{"basis_ref":basis,"authorization_ref":authorization,"context_ref":context,"chart_ref":chart,"account_changes":changes,"before_contract":before,"after_contract":after})
        arguments = {"basis_ref":basis,"authorization_ref":authorization,"journal_ref":journal,"delta_ref":delta}
        request = add("OperationRequest",name+"-request",{"operation":"accounting.commit@1","request_id":request_id,"workspace_key":"authored-examples",
            "profile_ref":op_profile,"signature_ref":signature,"view_ref":view,"arguments":arguments,
            "execution":{"mode":"specification_example","budget":{"operation_count":1,"elapsed_seconds":60},"environment_ref":environment},
            "expected_head":{"owner_key":owner,"state_ref":open_ref,"generation":REGISTRY[open_ref["digest"]]["body"]["sequence"]}})
        wire = OUT/(name+"-request.json")
        wire.write_bytes(canonical(REGISTRY[request["digest"]]))
        submission = add("Submission",name+"-submission",{"blob_ref":blob(wire),"media_type":"application/json","transport":"documentary_file","decoder_ref":decoder})
        return {"request":request,"submission":submission,"basis":basis,"authorization":authorization,"journal":journal,"delta":delta,"after":after}

    positive = request_case("positive")
    closing = add("CompanyState","closing-state",{**initial_body,"sequence":1,"contract":positive["after"]})
    receipt = add("StateTransitionReceipt","original-receipt",{"request_ref":positive["request"],"identity":identity,"basis_ref":positive["basis"],
        "authorization_ref":positive["authorization"],"journal_ref":positive["journal"],"delta_ref":positive["delta"],"opening_ref":opening,
        "closing_ref":closing,"generation":1,"status":"committed"})
    committed_world = {"head":{"owner_key":owner,"state_ref":closing,"generation":1},
        "identity_index":[{"identity":identity,"request_ref":positive["request"],"receipt_ref":receipt}],
        "committed_journal_refs":[positive["journal"]],"committed_delta_refs":[positive["delta"]],"receipt_refs":[receipt]}

    def finish(name, packet, before, after, disposition, code=None, stage=None, valid=True, lookup=True, new_commit=False, original=None):
        domain = add("RequestDomain",name+"-domain",{"request_ref":packet["request"],"meaning":"singleton_request_decision"}) if valid else None
        region = add("RequestRegion",name+"-region",{"domain_ref":domain,"predicate":"this_request_decision","status":"completed"}) if valid else None
        output_failure = code in ["DELTA_MISMATCH","ECONOMIC_DELTA_MISMATCH"]
        result = {"submission_ref":packet["submission"],"request_ref":packet["request"] if valid else None,"operation":"accounting.commit@1" if valid else None,
            "input_view_ref":view if valid else None,"disposition":disposition,
            "statuses":{"structural_validity":"valid" if valid else "invalid","mathematical_status":"failed" if output_failure else "defined" if valid else "unresolved",
                "computation_status":"complete" if valid else "not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime",
                "accounting_validity":"not_assessed","forecast_validity":"not_assessed","product_readiness":"not_implemented","human_acceptance":"pending"},
            "payload":{"kind":"state_only_commit","event_committed":original is not None,"additional_commit":new_commit,"observed_head":after["head"],"original_receipt_ref":original} if valid else None,
            "diagnostics":[{"code":code,"stage":stage,"record_ref":packet["request"],"source_locator":None,"field_path":"$.arguments" if output_failure else "$",
                "affected_query_branch_ids":["advance-case"],"dependency_path":[],"observed":name,"expected_rule":code,
                "retry_advice":"new_request_after_input_repair" if not valid or output_failure else "no_automatic_retry","blocking_diagnostic_ids":[]}] if code else [],
            "coverage":{"domain_ref":domain,"completed":[region],"unresolved":[],"unsupported":[],"infeasible":[],"cancelled":[],"relation":"singleton_partition"} if valid else None,
            "unresolved":[],"continuation_ref":None,"commit_observation":"committed" if new_commit else "not_committed","receipt_ref":original,"evidence_mode":"specification_example"}
        result_ref = add("OperationResult",name+"-result",result)
        cases.append({"id":name,"candidate_request_ref":packet["request"],"submission_ref":packet["submission"],"expected_result_ref":result_ref,
                      "before":before,"after":after,"expected_lookup":lookup,"expected_code":code})

    finish("positive",positive,start_world,committed_world,"completed",new_commit=True,original=receipt)
    finish("replay",positive,committed_world,committed_world,"replayed",original=receipt)
    finish("changed_invoice",request_case("changed_invoice",invoice="I2"),committed_world,committed_world,"rejected","EVENT_ID_CONFLICT","receipt_lookup")
    # Preserve inner records; only the complete operation envelope/request key changes.
    request_id_packet = deepcopy(positive)
    body = deepcopy(REGISTRY[positive["request"]["digest"]]["body"]); body["request_id"]="another-correlation-id"
    changed_ref = add("OperationRequest",REGISTRY[positive["request"]["digest"]]["key"],body)
    ALIASES["changed-request-id"] = changed_ref
    ALIASES["positive-request"] = positive["request"]
    request_id_packet["request"]=changed_ref
    wire=OUT/"changed-request-id-request.json"; wire.write_bytes(canonical(REGISTRY[changed_ref["digest"]]))
    request_id_packet["submission"]=add("Submission","changed-request-id-submission",{"blob_ref":blob(wire),"media_type":"application/json","transport":"documentary_file","decoder_ref":decoder})
    finish("changed_request_id",request_id_packet,committed_world,committed_world,"rejected","EVENT_ID_CONFLICT","receipt_lookup")
    finish("stale_head",request_case("stale_head",invoice="I2",event_id="E2"),committed_world,committed_world,"rejected","STALE_OPENING_STATE","freshness")
    finish("reused_credit",request_case("reused_credit",invoice="I2",event_id="E2",open_ref=closing,permission=False,eligible=False),committed_world,committed_world,"rejected","POSTING_NOT_AUTHORIZED","authorization",valid=False,lookup=False)
    finish("false_authorization",request_case("false_authorization",permission=False),start_world,start_world,"rejected","POSTING_NOT_AUTHORIZED","authorization",valid=False,lookup=False)
    finish("unsupported_profile",request_case("unsupported_profile",op_profile=unsupported),start_world,start_world,"unsupported","UNSUPPORTED_PROFILE_OPERATION","capability",valid=False,lookup=False)
    finish("nonzero_delta",request_case("nonzero_delta",delta_fault="monetary"),start_world,start_world,"rejected","DELTA_MISMATCH","candidate_reconciliation")
    finish("lost_allocation",request_case("lost_allocation",delta_fault="economic"),start_world,start_world,"rejected","ECONOMIC_DELTA_MISMATCH","candidate_reconciliation")
    pins = []
    for filename in ["language-ir-contract-v1.md","interfaces-contract-v1.md","persistence-contract-v1.md","cross-contract-amendment-v1.md","failure-contract-v1.md","accounting-records-contract-v1.md"]:
        path=ROOT/"docs/design/proposal/architecture"/filename
        pins.append({"path":str(path.relative_to(ROOT)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    bundle={"schema":"accdsl.advance-allocation.examples.v1","evidence_mode":"specification_example","product_implemented":False,
        "record_registry":REGISTRY,"aliases":ALIASES,"blobs":BLOBS,"schema_lock_ref":lock,"source_pins":pins,"cases":cases,
        "limits":["synthetic cases only","not a runtime transaction or crash test","no native schema changes","tax and whole company effects not inferred"]}
    (OUT/"portable-exchanges.json").write_text(json.dumps(bundle,indent=2,ensure_ascii=False)+"\n")
    (OUT/"build-exchange-run.json").write_text(json.dumps({"command":["python3",str(Path(__file__).relative_to(ROOT))],"written_utc":datetime.now(timezone.utc).isoformat(),
        "records":len(REGISTRY),"blobs":len(BLOBS),"cases":len(cases),"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+"\n")
    print(json.dumps({"records":len(REGISTRY),"blobs":len(BLOBS),"cases":len(cases),"status":"authored; independent verification pending"}))


if __name__=="__main__":
    main()
