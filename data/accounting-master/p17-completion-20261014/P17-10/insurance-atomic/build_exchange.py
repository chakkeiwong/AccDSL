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
    return common.get(kind, "accdsl.insurance-close."+kind.lower()+".v1")


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
TEMPLATE = ROOT/"data/accounting-master/p17-completion-20261014/P17-10/state-only/record-schemas.json"
SCHEMAS = json.loads(TEMPLATE.read_text().replace("accdsl.advance-allocation.","accdsl.insurance-close."))["$defs"]
GROUP_IDS = ["A","B","R"]
PHASES = ["opening","finance","service","incurrence","settlement"]
ACCOUNTS = ["cash","A_LRC","B_LRC","R_ARC","A_LIC","B_LIC","R_incurred","equity_open",
            "finance_A","finance_B","finance_R","revenue_A","revenue_B","B_loss_reversal",
            "R_premium_allocation","R_loss_reversal","issued_claims","R_claim_recovery"]
BALANCES = closed({k:RAT for k in ACCOUNTS})
GROUP = closed({"group_id":{"enum":GROUP_IDS},"role":{"enum":["issued","held"]},"portfolio_id":IDENT,
    "issue_year":{"const":2024},"profitability":{"enum":["profitable","onerous","held"]},
    "covered_group_ids":arr({"enum":GROUP_IDS}),"pv":RAT,"ra":RAT,"csm":RAT,"loss_component":RAT,
    "incurred":RAT,"coverage_units":INT})
GROUPS = arr(GROUP,3)
SCHEMAS["Assumptions"] = closed({"rate":RAT,"B_loss_ratio":RAT,"reinsurance_share":RAT,
    "claims":closed({k:RAT for k in GROUP_IDS}),"unchanged_estimates":BOOL,
    "finance_all_profit_loss":BOOL,"fact_status":{"const":"authored_synthetic"}})
SCHEMAS["CompanyState"] = closed({"context_ref":ref("Context"),"branch_ref":ref("Branch"),"chart_ref":ref("Chart"),
    "sequence":INT,"phase":{"enum":PHASES},"balances":BALANCES,"groups":GROUPS})
SCHEMAS["GroupMeasurement"] = closed({"group_id":{"enum":GROUP_IDS},"phase":{"enum":PHASES[1:]},
    "context_ref":ref("Context"),"branch_ref":ref("Branch"),"time_ref":ref("Time"),"view_ref":ref("View"),
    "method_ref":ref("MethodDefinition"),"source_ref":ref("SourceSupport"),"before":GROUP,"after":nullable(GROUP),
    "status":{"enum":["complete","unresolved"]},"reason":nullable(TEXT)})
SCHEMAS["EconomicEvent"] = closed({"business_event_id":IDENT,"version":INT,"kind":{"const":"insurance_group_close"},
    "phase":{"enum":PHASES[1:]},"context_ref":ref("Context"),"branch_ref":ref("Branch"),"time_ref":ref("Time"),
    "required_group_ids":arr({"enum":GROUP_IDS},3),"measurement_refs":arr(ref("GroupMeasurement"))})
LINE = closed({"group_id":{"enum":GROUP_IDS},"account_id":{"enum":ACCOUNTS},"amount":RAT})
SCHEMAS["JournalProposal"] = closed({"basis_ref":ref("AccountingEventBasis"),"authorization_ref":ref("PostingAuthorization"),
    "context_ref":ref("Context"),"chart_ref":ref("Chart"),"effect":{"const":"monetary_and_components"},"lines":arr(LINE,1)})
SCHEMAS["EconomicDelta"] = closed({"basis_ref":ref("AccountingEventBasis"),"authorization_ref":ref("PostingAuthorization"),
    "context_ref":ref("Context"),"chart_ref":ref("Chart"),"account_changes":BALANCES,"before_groups":GROUPS,"after_groups":GROUPS})
SCHEMAS["AuditCandidate"] = closed({"submission_ref":ref("Submission"),"measurement_refs":arr(ref("GroupMeasurement")),
    "reason":TEXT,"committed":{"const":False}})
SCHEMAS["TransportObservation"] = closed({"submission_ref":ref("Submission"),"request_ref":ref("OperationRequest"),
    "observation":{"const":"acknowledgement_timeout"},"commit_observation":{"const":"unknown"},
    "receipt_ref":{"type":"null"},"next_action":{"const":"resubmit_exact_original_request"}})
PAYLOAD = SCHEMAS["OperationResult"]["properties"]["payload"]["anyOf"][0]
PAYLOAD["properties"]["kind"] = {"const":"insurance_group_commit"}


def body(r):
    return REGISTRY[r["digest"]]["body"]


def main():
    schemas={"$schema":"https://json-schema.org/draft/2020-12/schema","description":"Closed documentary insurance-close profile bodies; common envelope fields unchanged.",
             "schema_ids":{k:schema_id(k) for k in SCHEMAS},"$defs":SCHEMAS}
    (OUT/"record-schemas.json").write_text(json.dumps(schemas,indent=2)+"\n")
    contract=ROOT/"docs/design/proposal/architecture/insurance-atomic-commit-20261014.md"
    lock=add("SchemaLock","schema-lock",{"schema_blob":blob(OUT/"record-schemas.json"),"semantic_contract_blob":blob(contract),"format":"jsonschema2020-12"})
    source=add("SourceSupport","connected-source",{"source_blob":blob(ROOT/"docs/design/research/standards/aasb17.pdf"),
        "locator":"AASB17 December2022 F2023C00382; paragraphs32-52,60-68,78-88,B72,B119-B125; connected-group dossier",
        "scope":"Historical Australian private-sector calendar2024-2025; supplied synthetic assumptions, no current real-book permission."})
    authority=add("SyntheticAuthority","synthetic-authority",{"source_ref":source,"nature":"authored_synthetic","limit":"Existing A/B/R conditional example only; no real insurer or general actuarial authority."})
    method=add("MethodDefinition","group-close-method",{"method_id":"authored.insurance.close","version":1,"event_kind":"insurance_group_close",
        "state_schema":schema_id("CompanyState"),"event_schema":schema_id("EconomicEvent"),"journal_schema":schema_id("JournalProposal"),
        "delta_schema":schema_id("EconomicDelta"),"output_schema":schema_id("StateTransitionReceipt"),
        "required_contexts":["one synthetic entity/book/branch; separate issued A/B and held R; 2024 closing in CU"],"authority_requirements":[authority],
        "preconditions":["complete A/B/R measurements in one frozen view/method","ordered finance/service/incurrence/settlement","synthetic admission","independent component reconciliation"],
        "algorithm":"Apply the selected phase from the locked semantic contract to each group; reconcile ordered lines, complete delta and one company state; P2 atomic publication.",
        "account_roles":ACCOUNTS,"report_mappings":"Separate issued revenue/claims, reinsurance service and finance; loss components remain inside coverage; cash flows occur on settlement.",
        "numerical_capability":"reduced exact rationals","examples":["A/B/R 2024 unchanged timely-treaty path"],
        "unsupported_cases":["real book","cross-book event","changed estimates, OCI, tax or partial cover","independent group publication for this event"]})
    profile=add("PostingProfile","group-close-profile",{"profile_id":"authored.insurance.close.v1","version":1,"schema_lock_ref":lock,
        "method_ref":method,"supported_book_modes":["synthetic"],"operations":["accounting.commit@1"]})
    signature=add("OperationSignature","commit-signature",{"operation":"accounting.commit@1","schema_lock_ref":lock,
        "argument_fields":["basis_ref","authorization_ref","journal_ref","delta_ref"],"result_schema":schema_id("OperationResult")})
    view=add("View","scenario-view",{"view_id":"authored-timely-2024","mode":"synthetic","historical_availability_claim":False})
    context=add("Context","insurer-context",{"entity_id":"Insurer","book_id":"Pretax","currency":"CU","unit":"units","scale":0,
        "basis":"AASB17 December2022 synthetic historical case","annual_period_start":"2024-01-01","perimeter":"one synthetic legal insurer"})
    branch=add("Branch","insurer-branch",{"branch_key":"connected-2024","book_mode":"synthetic","view_ref":view,"family_id":"authored-A-B-R"})
    time=add("Time","closing-time",{"economic_date":"2024-12-31","reporting_start":"2024-01-01","reporting_end":"2024-12-31","view_ref":view,
        "availability_scope":"Authored information sequence; no exact-byte historical-availability claim."})
    credit_accounts={"A_LRC","B_LRC","A_LIC","B_LIC","equity_open","finance_R","revenue_A","revenue_B","B_loss_reversal","R_claim_recovery"}
    chart=add("Chart","insurer-chart",{"context_ref":context,"accounts":[{"account_id":k,"concept_id":k,"normal_side":"credit" if k in credit_accounts else "debit"} for k in ACCOUNTS]})
    assumptions=add("Assumptions","case-assumptions",{"rate":rat(1,10),"B_loss_ratio":rat(3,13),"reinsurance_share":rat(1,2),
        "claims":{"A":rat(44),"B":rat(66),"R":rat(33)},"unchanged_estimates":True,"finance_all_profit_loss":True,"fact_status":"authored_synthetic"})
    evidence=add("Evidence","case-evidence",{"assumptions_ref":assumptions,"source_ref":source,"nature":"authored_synthetic"})
    admission=add("Admission","case-admission",{"evidence_ref":evidence,"view_ref":view,"status":"synthetic_only","reason":"Supplied A/B/R case, not actual insurer facts."})
    environment=add("Environment","documentary-environment",{"purpose":"documentary_fixture","numerics":"exact_rational","runtime_executed":False})
    decoder=add("Decoder","json-decoder",{"media_type":"application/json","canonical_encoding":"accdsl.portable.v1"})

    def groups(values, units=2):
        return [{"group_id":g,"role":"held" if g=="R" else "issued","portfolio_id":"held-treaty" if g=="R" else "issued-cover",
                 "issue_year":2024,"profitability":{"A":"profitable","B":"onerous","R":"held"}[g],"covered_group_ids":["B"] if g=="R" else [],
                 **{k:rat(Fraction(v)) for k,v in zip(["pv","ra","csm","loss_component","incurred"],values[g])},"coverage_units":units} for g in GROUP_IDS]

    group_states=[
      groups({"A":[80,10,30,0,0],"B":[120,10,0,30,0],"R":[60,5,20,15,0]}),
      groups({"A":[88,10,33,0,0],"B":[132,10,0,"426/13",0],"R":[66,5,22,"213/13",0]}),
      groups({"A":[44,5,"33/2",0,0],"B":[66,5,0,"213/13",0],"R":[33,"5/2",11,"213/26",0]},1),
      groups({"A":[44,5,"33/2",0,44],"B":[66,5,0,"213/13",66],"R":[33,"5/2",11,"213/26",33]},1),
      groups({"A":[44,5,"33/2",0,0],"B":[66,5,0,"213/13",0],"R":[33,"5/2",11,"213/26",0]},1)]
    raw_lines={
      "finance":[("A","finance_A",11),("A","A_LRC",-11),("B","finance_B",12),("B","B_LRC",-12),("R","R_ARC",8),("R","finance_R",-8)],
      "service":[("A","A_LRC","131/2"),("A","revenue_A","-131/2"),("B","B_LRC",71),("B","revenue_B","-710/13"),("B","B_loss_reversal","-213/13"),
                 ("R","R_premium_allocation","498/13"),("R","R_loss_reversal","213/26"),("R","R_ARC","-93/2")],
      "incurrence":[("A","issued_claims",44),("A","A_LIC",-44),("B","issued_claims",66),("B","B_LIC",-66),("R","R_incurred",33),("R","R_claim_recovery",-33)],
      "settlement":[("A","A_LIC",44),("A","cash",-44),("B","B_LIC",66),("B","cash",-66),("R","cash",33),("R","R_incurred",-33)]}
    lines={p:[{"group_id":g,"account_id":a,"amount":rat(Fraction(v))} for g,a,v in rows] for p,rows in raw_lines.items()}
    balances={k:Fraction(0) for k in ACCOUNTS};balances.update(cash=Fraction(250),A_LRC=Fraction(-120),B_LRC=Fraction(-130),R_ARC=Fraction(85),equity_open=Fraction(-85))
    states=[]
    for i,phase in enumerate(PHASES):
        if i:
            for line in raw_lines[phase]: balances[line[1]]+=Fraction(line[2])
        states.append(add("CompanyState",phase+"-state",{"context_ref":context,"branch_ref":branch,"chart_ref":chart,"sequence":i,"phase":phase,
            "balances":{k:rat(v) for k,v in balances.items()},"groups":group_states[i]}))
    owner="Insurer/Pretax/connected-2024"
    base_identity={"entity_id":"Insurer","book_id":"Pretax","branch_key":"connected-2024"}
    def publish_closure(world):
        found={}
        def walk(r):
            if r["digest"] in found: return
            found[r["digest"]]=r
            for child in REGISTRY[r["digest"]]["dependencies"]: walk(child)
        for field in ["committed_state_refs","committed_journal_refs","committed_delta_refs","receipt_refs"]:
            for r in world[field]: walk(r)
        world["published_record_refs"]=[found[d] for d in sorted(found)]
        world["published_dependency_edges"]=sorted(
            [{"from_ref":found[d],"to_ref":child} for d in found for child in REGISTRY[d]["dependencies"]],key=canonical)
        return world
    start_world=publish_closure({"head":{"owner_key":owner,"state_ref":states[0],"generation":0},"identity_index":[],
        "committed_state_refs":[states[0]],"committed_journal_refs":[],"committed_delta_refs":[],"receipt_refs":[]})
    cases=[]

    def packet(name, phase="finance", event_id=None, fault=None):
        i=PHASES.index(phase); event_id=event_id or "2024-close-"+phase
        use_branch=branch; opening=states[i-1]
        if fault=="real_book":
            use_branch=add("Branch",name+"-real-branch",{**body(branch),"book_mode":"real"})
            opening=add("CompanyState",name+"-real-opening",{**body(opening),"branch_ref":use_branch})
        measurements=[]
        for j,g in enumerate(GROUP_IDS):
            m={"group_id":g,"phase":phase,"context_ref":context,"branch_ref":use_branch,"time_ref":time,"view_ref":view,
               "method_ref":method,"source_ref":source,"before":group_states[i-1][j],"after":group_states[i][j],"status":"complete","reason":None}
            if g=="R" and fault=="unresolved_R":
                m.update(after=None,status="unresolved",reason="Required admitted R measurement unavailable; A/B candidates are diagnostic only.")
            if g=="R" and fault=="wrong_book":
                m["context_ref"]=add("Context",name+"-other-context",{**body(context),"book_id":"OtherBook"})
            if g=="R" and fault=="wrong_view":
                m["view_ref"]=add("View",name+"-other-view",{**body(view),"view_id":"other-scenario"})
            if g=="R" and fault=="wrong_method":
                m["method_ref"]=add("MethodDefinition",name+"-other-method",{**body(method),"method_id":"other.measurement"})
            if g=="R" and fault=="wrong_branch":
                m["branch_ref"]=add("Branch",name+"-other-branch",{**body(branch),"branch_key":"other-branch"})
            if g=="R" and fault=="wrong_measurement":
                m["after"]={**m["after"],"loss_component":rat(0)}
            measurements.append(add("GroupMeasurement",name+"-"+g+"-measurement",m))
        event_measurements=list(measurements)
        if fault=="missing_group": event_measurements=event_measurements[:2]
        if fault=="duplicate_group": event_measurements.append(event_measurements[0])
        event=add("EconomicEvent",name+"-event",{"business_event_id":event_id,"version":1,"kind":"insurance_group_close","phase":phase,
            "context_ref":context,"branch_ref":use_branch,"time_ref":time,"required_group_ids":GROUP_IDS,"measurement_refs":event_measurements})
        basis=add("AccountingEventBasis",name+"-basis",{"identity":{**base_identity,"business_event_id":event_id},"event_ref":event,"opening_ref":opening,
            "context_ref":context,"branch_ref":use_branch,"time_ref":time,"chart_ref":chart,"authority_refs":[authority],"method_ref":method,
            "evidence_refs":[evidence],"admission_refs":[admission],"assumptions_ref":assumptions,"view_ref":view})
        eligible=fault!="unresolved_R"
        authorization=add("PostingAuthorization",name+"-authorization",{"basis_ref":basis,"posting_profile_ref":profile,"method_ref":method,"authority_refs":[authority],
            "status":"eligible" if eligible else "unresolved","findings":[{"name":g+"_measurement","status":"unknown" if g=="R" and not eligible else "satisfied",
            "support":"Retained group measurement in this event"} for g in GROUP_IDS],"posting_permitted":eligible and fault!="false_permission",
            "evidence_level":"authored-synthetic","view_ref":view})
        jlines=deepcopy(lines[phase])
        if fault=="double_count_component":
            jlines += [{"group_id":"R","account_id":"R_ARC","amount":rat(18,13)},
                       {"group_id":"R","account_id":"finance_R","amount":rat(-18,13)}]
        journal=add("JournalProposal",name+"-journal",{"basis_ref":basis,"authorization_ref":authorization,"context_ref":context,"chart_ref":chart,
            "effect":"monetary_and_components","lines":jlines})
        changes={k:Fraction(0) for k in ACCOUNTS}
        for line in jlines: changes[line["account_id"]]+=Fraction(int(line["amount"]["n"]),int(line["amount"]["d"]))
        after_groups=deepcopy(group_states[i])
        if fault=="lost_component": after_groups[2]["loss_component"]=group_states[i-1][2]["loss_component"]
        delta=add("EconomicDelta",name+"-delta",{"basis_ref":basis,"authorization_ref":authorization,"context_ref":context,"chart_ref":chart,
            "account_changes":{k:rat(v) for k,v in changes.items()},"before_groups":group_states[i-1],"after_groups":after_groups})
        request=add("OperationRequest",name+"-request",{"operation":"accounting.commit@1","request_id":"request-"+event_id,"workspace_key":"authored-insurance",
            "profile_ref":profile,"signature_ref":signature,"view_ref":view,"arguments":{"basis_ref":basis,"authorization_ref":authorization,"journal_ref":journal,"delta_ref":delta},
            "execution":{"mode":"specification_example","budget":{"operation_count":1,"elapsed_seconds":60},"environment_ref":environment},
            "expected_head":{"owner_key":owner,"state_ref":opening,"generation":i-1}})
        wire=OUT/(name+"-request.json");wire.write_bytes(canonical(REGISTRY[request["digest"]]))
        submission=add("Submission",name+"-submission",{"blob_ref":blob(wire),"media_type":"application/json","transport":"documentary_file","decoder_ref":decoder})
        return {"request":request,"submission":submission,"basis":basis,"authorization":authorization,"journal":journal,"delta":delta,
                "measurements":measurements,"closing":states[i]}

    def commit_world(p,before,label):
        receipt=add("StateTransitionReceipt",label+"-receipt",{"request_ref":p["request"],"identity":body(p["basis"])["identity"],"basis_ref":p["basis"],
            "authorization_ref":p["authorization"],"journal_ref":p["journal"],"delta_ref":p["delta"],"opening_ref":body(p["basis"])["opening_ref"],
            "closing_ref":p["closing"],"generation":before["head"]["generation"]+1,"status":"committed"})
        after=deepcopy(before);after["head"]={"owner_key":owner,"state_ref":p["closing"],"generation":before["head"]["generation"]+1}
        after["identity_index"].append({"identity":body(p["basis"])["identity"],"request_ref":p["request"],"receipt_ref":receipt})
        after["committed_journal_refs"].append(p["journal"]);after["committed_delta_refs"].append(p["delta"]);after["receipt_refs"].append(receipt)
        after["committed_state_refs"].append(p["closing"])
        return publish_closure(after),receipt

    def finish(name,p,before,after,disposition,code=None,stage=None,valid=True,lookup=True,new_commit=False,original=None,recheck=None):
        domain=add("RequestDomain",name+"-domain",{"request_ref":p["request"],"meaning":"singleton_request_decision"}) if valid else None
        region=add("RequestRegion",name+"-region",{"domain_ref":domain,"predicate":"this_request_decision","status":"completed"}) if valid else None
        result={"submission_ref":p["submission"],"request_ref":p["request"] if valid else None,"operation":"accounting.commit@1" if valid else None,
            "input_view_ref":view if valid else None,"disposition":disposition,
            "statuses":{"structural_validity":"valid" if valid else "invalid","mathematical_status":"failed" if stage=="candidate_reconciliation" else "defined" if valid else "unresolved",
                "computation_status":"complete" if valid else "not_computed","empirical_justification":"not_established","capability_status":"specified_only_no_runtime",
                "accounting_validity":"not_assessed","forecast_validity":"not_assessed","product_readiness":"not_implemented","human_acceptance":"pending"},
            "payload":{"kind":"insurance_group_commit","event_committed":original is not None,"additional_commit":new_commit,"observed_head":after["head"],"original_receipt_ref":original} if valid else None,
            "diagnostics":[{"code":code,"stage":stage,"record_ref":p["request"],"source_locator":None,"field_path":"$.arguments","affected_query_branch_ids":["connected-2024"],
                "dependency_path":[],"observed":name,"expected_rule":code,"retry_advice":"repair_input_or_candidate" if not valid or stage=="candidate_reconciliation" else "no_automatic_retry","blocking_diagnostic_ids":[]}] if code else [],
            "coverage":{"domain_ref":domain,"completed":[region],"unresolved":[],"unsupported":[],"infeasible":[],"cancelled":[],"relation":"singleton_partition"} if valid else None,
            "unresolved":["R measurement unresolved; A/B candidates are not a closing book"] if code=="GROUP_MEASUREMENT_UNRESOLVED" else [],
            "continuation_ref":None,"commit_observation":"committed" if new_commit else "not_committed","receipt_ref":original,"evidence_mode":"specification_example"}
        result_ref=add("OperationResult",name+"-result",result)
        audit=add("AuditCandidate",name+"-audit",{"submission_ref":p["submission"],"measurement_refs":p["measurements"],"reason":code,"committed":False}) if not valid else None
        cases.append({"id":name,"kind":"operation","candidate_request_ref":p["request"],"submission_ref":p["submission"],"expected_result_ref":result_ref,
            "before":before,"at_recheck":recheck,"after":after,"expected_lookup":lookup,"expected_code":code,"audit_candidate_ref":audit})

    worlds=[start_world];packets=[];receipts=[]
    for phase in PHASES[1:]:
        p=packet(phase,phase=phase);after,receipt=commit_world(p,worlds[-1],phase)
        finish(phase+"_commit",p,worlds[-1],after,"completed",new_commit=True,original=receipt)
        packets.append(p);receipts.append(receipt);worlds.append(after)
    first=packets[0]
    finish("replay_after_settlement",first,worlds[-1],worlds[-1],"replayed",original=receipts[0])
    changed_packets={}
    for name,field,value in [("changed_request_id","request_id","new-correlation"),("changed_budget","budget",2)]:
        p=deepcopy(first);b=deepcopy(body(first["request"]))
        if field=="budget": b["execution"]["budget"]["operation_count"]=value
        else: b[field]=value
        p["request"]=add("OperationRequest",REGISTRY[first["request"]["digest"]]["key"],b)
        ALIASES[name+"-request"]=p["request"];ALIASES["finance-request"]=first["request"]
        wire=OUT/(name+"-request.json");wire.write_bytes(canonical(REGISTRY[p["request"]["digest"]]))
        p["submission"]=add("Submission",name+"-submission",{"blob_ref":blob(wire),"media_type":"application/json","transport":"documentary_file","decoder_ref":decoder})
        changed_packets[name]=p
        finish(name,p,worlds[-1],worlds[-1],"rejected","EVENT_ID_CONFLICT","receipt_lookup")
    alternate=packet("alternate-finance",event_id="other-2024-finance")
    finish("stale_new_event",alternate,worlds[1],worlds[1],"rejected","STALE_OPENING_STATE","freshness")
    for fault,code,stage in [("wrong_book","GROUP_BINDING_MISMATCH","bindings"),("wrong_view","GROUP_BINDING_MISMATCH","bindings"),
        ("wrong_method","GROUP_BINDING_MISMATCH","bindings"),("wrong_branch","GROUP_BINDING_MISMATCH","bindings"),
        ("wrong_measurement","GROUP_MEASUREMENT_MISMATCH","authorization"),
        ("missing_group","GROUP_SET_MISMATCH","bindings"),("duplicate_group","GROUP_SET_MISMATCH","bindings"),
        ("false_permission","POSTING_NOT_AUTHORIZED","authorization"),("unresolved_R","GROUP_MEASUREMENT_UNRESOLVED","authorization"),
        ("real_book","BOOK_MODE_NOT_AUTHORIZED","authorization")]:
        p=packet(fault,fault=fault)
        # Existing receipt deliberately tests that bad input cannot bypass validation.
        finish(fault,p,worlds[1],worlds[1],"rejected",code,stage,valid=False,lookup=False)
    for fault,code in [("lost_component","ECONOMIC_DELTA_MISMATCH"),("double_count_component","JOURNAL_METHOD_MISMATCH")]:
        p=packet(fault,fault=fault)
        finish(fault,p,start_world,start_world,"rejected",code,"candidate_reconciliation")
    competitor_world,competitor_receipt=commit_world(alternate,start_world,"competitor")
    finish("race_other_event",first,start_world,competitor_world,"rejected","STALE_OPENING_STATE","atomic_recheck",recheck=competitor_world)
    finish("race_same_request",first,start_world,worlds[1],"replayed",original=receipts[0],recheck=worlds[1])
    different_world,different_receipt=commit_world(changed_packets["changed_budget"],start_world,"different-request")
    finish("race_different_request",first,start_world,different_world,"rejected","EVENT_ID_CONFLICT","atomic_recheck",recheck=different_world)
    for side,stored in [("before",start_world),("after",worlds[1])]:
        observation=add("TransportObservation","timeout-"+side,{"submission_ref":first["submission"],"request_ref":first["request"],
            "observation":"acknowledgement_timeout","commit_observation":"unknown","receipt_ref":None,"next_action":"resubmit_exact_original_request"})
        cases.append({"id":"lost_ack_"+side,"kind":"transport_ambiguity","candidate_request_ref":first["request"],"submission_ref":first["submission"],
            "observation_ref":observation,"before":start_world,"stored_world":stored,"expected_result_ref":None})
    finish("retry_after_precommit_loss",first,start_world,worlds[1],"completed",new_commit=True,original=receipts[0])
    finish("retry_after_postcommit_loss",first,worlds[1],worlds[1],"replayed",original=receipts[0])
    pins=[]
    paths=[ROOT/"docs/design/proposal/architecture"/f for f in ["interfaces-contract-v1.md","persistence-contract-v1.md","cross-contract-amendment-v1.md","language-ir-contract-v1.md","failure-contract-v1.md"]]
    paths += [TEMPLATE]
    paths += [ROOT/"data/accounting-master/p17-completion-20261014/P17-07/connected-groups"/f for f in
              ["group-cases.json","calculated-schedules.json","source-manifest.json","result.md"]]
    for path in paths:
        pins.append({"path":str(path.relative_to(ROOT)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    bundle={"schema":"accdsl.insurance-close.examples.v1","evidence_mode":"specification_example","product_implemented":False,
        "record_registry":REGISTRY,"aliases":ALIASES,"blobs":BLOBS,"schema_lock_ref":lock,"source_pins":pins,"cases":cases,
        "sequence":{phase:states[i] for i,phase in enumerate(PHASES)},
        "limits":["authored historical synthetic case","no live store or runtime execution","no distributed atomicity","no financial probability or stochastic ranking"]}
    (OUT/"portable-exchanges.json").write_text(json.dumps(bundle,indent=2)+"\n")
    (OUT/"build-exchange-run.json").write_text(json.dumps({"command":["python3",str(Path(__file__).relative_to(ROOT))],
        "written_utc":datetime.now(timezone.utc).isoformat(),"records":len(REGISTRY),"blobs":len(BLOBS),"cases":len(cases),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+"\n")
    print(json.dumps({"records":len(REGISTRY),"blobs":len(BLOBS),"cases":len(cases),"status":"authored; independent verification pending"}))


if __name__=="__main__":
    main()
