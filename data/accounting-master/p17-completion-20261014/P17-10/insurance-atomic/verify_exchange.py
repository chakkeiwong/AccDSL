"""Independent finite documentary checks; no live store or runtime endpoint."""
from copy import deepcopy
from datetime import date, datetime, timezone
from fractions import Fraction as Q
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import time

from jsonschema import Draft202012Validator, FormatChecker

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
CHECKS = []
DERIVED = []


def check(name, passed, detail=None):
    CHECKS.append({"name":name,"passed":bool(passed),"detail":detail})


def encoding(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")


def number(value):
    if set(value) != {"n","d"}:
        raise ValueError("rational fields")
    n,d = int(value["n"]),int(value["d"])
    q = Q(n,d)
    if d <= 0 or str(q.numerator) != value["n"] or str(q.denominator) != value["d"]:
        raise ValueError("rational not canonical")
    return q


def rational(q):
    return {"n":str(q.numerator),"d":str(q.denominator)}


def links(value):
    if isinstance(value,dict):
        if set(value) == {"kind","schema","digest"}:
            yield value
        else:
            for v in value.values():
                yield from links(v)
    elif isinstance(value,list):
        for v in value:
            yield from links(v)


def check_values(value):
    if isinstance(value,float):
        raise ValueError("float in exact portable data")
    if isinstance(value,dict):
        if set(value)=={"n","d"}:
            number(value)
        for k,v in value.items():
            if not k.isascii():
                raise ValueError("non-ASCII object key")
            check_values(v)
    if isinstance(value,list):
        for v in value:
            check_values(v)


def main():
    timer=time.perf_counter(); started=datetime.now(timezone.utc).isoformat()
    bundle=json.loads((OUT/"portable-exchanges.json").read_text())
    schemas=json.loads((OUT/"record-schemas.json").read_text())
    registry=bundle["record_registry"]

    def record(r, kind=None):
        obj=registry[r["digest"]]
        if obj["kind"] != r["kind"] or obj["schema"] != r["schema"] or (kind is not None and obj["kind"]!=kind):
            raise ValueError("reference type mismatch")
        return obj

    def body(r, kind=None):
        return record(r,kind)["body"]

    check("documentary_only",bundle["evidence_mode"]=="specification_example" and bundle["product_implemented"] is False)
    for digest,obj in registry.items():
        label=obj["key"]+":"+digest[:8]
        check(label+":wrapper",set(obj)=={"kind","schema","key","revision","body","dependencies"}
              and type(obj["revision"]) is int and obj["revision"]>=0)
        check(label+":registered_schema",obj["schema"]==schemas["schema_ids"][obj["kind"]])
        validator=Draft202012Validator(schemas["$defs"][obj["kind"]],format_checker=FormatChecker())
        errors=[str(e.message) for e in validator.iter_errors(obj["body"])]
        check(label+":closed_shape",not errors,errors)
        try:
            check_values(obj)
        except ValueError as e:
            check(label+":exact_types",False,str(e))
        else:
            check(label+":exact_types",True)
        recalculated=hashlib.sha256(("accdsl.portable.v1/"+obj["schema"]).encode()+b"\x00"+encoding(obj)).hexdigest()
        check(label+":digest",recalculated==digest)
        found={encoding(r):r for r in links(obj["body"])}
        check(label+":declared_dependencies",obj["dependencies"]==[found[k] for k in sorted(found)])
        resolved=True
        try:
            for r in obj["dependencies"]:
                record(r)
        except (KeyError,ValueError):
            resolved=False
        check(label+":reference_resolution",resolved)
    visiting,done=set(),set()
    def visit(digest):
        if digest in visiting: raise ValueError("cycle")
        if digest in done: return
        visiting.add(digest)
        for r in registry[digest]["dependencies"]: visit(r["digest"])
        visiting.remove(digest); done.add(digest)
    for digest in registry: visit(digest)
    check("acyclic_closed_registry",len(done)==len(registry))

    for digest,info in bundle["blobs"].items():
        p=ROOT/info["path"]
        check("blob:"+info["path"],p.is_file() and len(p.read_bytes())==info["byte_length"]
              and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
    def inspect_blobs(value):
        if isinstance(value,dict):
            if value.get("kind")=="blob":
                check("blob_reference:"+value["digest"][:12],value["algorithm"]=="sha256"
                      and value["digest"] in bundle["blobs"] and value["byte_length"]==bundle["blobs"][value["digest"]]["byte_length"])
            for child in value.values(): inspect_blobs(child)
        elif isinstance(value,list):
            for child in value: inspect_blobs(child)
    for obj in registry.values(): inspect_blobs(obj)
    for pin in bundle["source_pins"]:
        check("protected_contract:"+pin["path"],hashlib.sha256((ROOT/pin["path"]).read_bytes()).hexdigest()==pin["sha256"])
    lock=body(bundle["schema_lock_ref"],"SchemaLock")
    check("actual_schema_lock",lock["schema_blob"]["digest"]==hashlib.sha256((OUT/"record-schemas.json").read_bytes()).hexdigest())

    # Reuse envelope fields, not a second operation API.
    template=json.loads((OUT.parent/"state-only/record-schemas.json").read_text()
                        .replace("accdsl.advance-allocation.","accdsl.insurance-close."))["$defs"]
    for kind in ["OperationRequest","AccountingEventBasis","PostingAuthorization","StateTransitionReceipt"]:
        check("common_schema:"+kind,schemas["$defs"][kind]==template[kind])
    result_schema=deepcopy(schemas["$defs"]["OperationResult"])
    result_schema["properties"]["payload"]=template["OperationResult"]["properties"]["payload"]
    check("common_result_envelope",result_schema==template["OperationResult"])
    for r in links({k:v for k,v in bundle.items() if k!="record_registry"}):
        record(r)
    check("all_exchange_references_resolve",True)

    baseline_dir=ROOT/"data/accounting-master/p17-completion-20261014/P17-07/connected-groups"
    inputs=json.loads((baseline_dir/"group-cases.json").read_text())
    schedule=json.loads((baseline_dir/"calculated-schedules.json").read_text())["timely"]
    assumptions=body(bundle["aliases"]["case-assumptions"],"Assumptions")
    rate=Q(inputs["rate"]); share=Q(inputs["R"]["q"])
    loss_ratio=Q(inputs["B"]["loss"])/(Q(inputs["B"]["claim_pv"])+Q(inputs["B"]["ra"]))
    claims={g:Q(inputs[g]["recoveries" if g=="R" else "claims"][0]) for g in ["A","B","R"]}
    check("assumptions_match_preserved_baseline",number(assumptions["rate"])==rate
          and number(assumptions["B_loss_ratio"])==loss_ratio and number(assumptions["reinsurance_share"])==share
          and {g:number(v) for g,v in assumptions["claims"].items()}==claims
          and assumptions["unchanged_estimates"] and assumptions["finance_all_profit_loss"]
          and claims["R"]==share*claims["B"])
    check("historical_source_bytes",hashlib.sha256((ROOT/"docs/design/research/standards/aasb17.pdf").read_bytes()).hexdigest()
          =="153e720cc1eaf7eea47d50463003391ea0433271694dd83a44c54a0e92deaec3")
    phases=["opening","finance","service","incurrence","settlement"]
    stock=["cash","A_LRC","B_LRC","R_ARC","A_LIC","B_LIC","R_incurred","equity_open"]
    components=["pv","ra","csm","loss_component","incurred"]

    def group_map(state):
        groups=state["groups"]
        assert [g["group_id"] for g in groups]==["A","B","R"]
        return {g["group_id"]:g for g in groups}

    def equity(state):
        a={k:number(v) for k,v in state["balances"].items()}
        return -a["equity_open"]-sum(v for k,v in a.items() if k not in stock)

    def validate_state(state):
        a={k:number(v) for k,v in state["balances"].items()}; gs=group_map(state)
        assert sum(a.values())==0
        assert state["sequence"]==phases.index(state["phase"])
        for g,obj in gs.items():
            assert obj["role"]==("held" if g=="R" else "issued")
            assert obj["portfolio_id"]==("held-treaty" if g=="R" else "issued-cover")
            assert obj["profitability"]=={"A":"profitable","B":"onerous","R":"held"}[g]
            assert obj["issue_year"]==inputs["admission"]["same_issue_year"]
            assert obj["covered_group_ids"]==(["B"] if g=="R" else [])
            assert all(number(obj[k])>=0 for k in components)
            amount=sum(number(obj[k]) for k in ["pv","ra","csm"])
            assert a[{"A":"A_LRC","B":"B_LRC","R":"R_ARC"}[g]]==amount*(1 if g=="R" else -1)
            assert a[{"A":"A_LIC","B":"B_LIC","R":"R_incurred"}[g]]==number(obj["incurred"])*(1 if g=="R" else -1)
            assert number(obj["loss_component"])<=amount
        assert number(gs["A"]["loss_component"])==number(gs["B"]["csm"])==0
        assert number(gs["R"]["loss_component"])==share*number(gs["B"]["loss_component"])
        assert len({g["coverage_units"] for g in gs.values()})==1
        assert equity(state)==sum(a[k] for k in stock if k!="equity_open")
        return a

    opening=body(bundle["sequence"]["opening"],"CompanyState")
    validate_state(opening)
    gs=group_map(opening)
    for g in gs:
        expected={"pv":Q(inputs[g]["claim_pv"]),"ra":Q(inputs[g]["ra"]),
                  "csm":Q(inputs[g]["timely_csm" if g=="R" else "csm"]),
                  "loss_component":Q(inputs[g]["initial_loss_recovery" if g=="R" else "loss"]),"incurred":Q(0)}
        check("opening_from_preserved_case:"+g,{k:number(gs[g][k]) for k in components}==expected
              and gs[g]["coverage_units"]==sum(inputs["coverage_units"]))
    initial_cash=Q(inputs["opening_cash_equity"])+sum(Q(inputs[g]["premium"])*(1 if g!="R" else -1) for g in gs)
    initial_equity=Q(inputs["opening_cash_equity"])-Q(inputs["B"]["loss"])+Q(inputs["R"]["initial_loss_recovery"])
    check("opening_cash_and_equity",number(opening["balances"]["cash"])==initial_cash and equity(opening)==initial_equity)

    def derive(before, phase):
        # Independent arithmetic from the retained case, never import the authoring script.
        old_accounts=validate_state(before)
        assert phases.index(phase)==before["sequence"]+1
        old=group_map(before); new=deepcopy(old); lines=[]
        values={g:{k:number(obj[k]) for k in components} for g,obj in old.items()}
        def post(g, *pairs):
            for account,amount in pairs:
                lines.append({"group_id":g,"account_id":account,"amount":rational(amount)})
        for g,v in values.items():
            nxt=dict(v)
            cover_account={"A":"A_LRC","B":"B_LRC","R":"R_ARC"}[g]
            incurred_account={"A":"A_LIC","B":"B_LIC","R":"R_incurred"}[g]
            if phase=="finance":
                nxt["pv"]+=v["pv"]*rate; nxt["csm"]+=v["csm"]*rate
                if g=="B": nxt["loss_component"]+=loss_ratio*v["pv"]*rate
                if g=="R": nxt["loss_component"]+=share*loss_ratio*values["B"]["pv"]*rate
                amount=(v["pv"]+v["csm"])*rate
                if g=="R": post(g,(cover_account,amount),("finance_R",-amount))
                else: post(g,("finance_"+g,amount),(cover_account,-amount))
            elif phase=="service":
                units=old[g]["coverage_units"]; assert units>0
                released={"pv":claims[g],"ra":v["ra"]/units,"csm":v["csm"]/units}
                for k,amount in released.items(): nxt[k]-=amount
                loss_release=loss_ratio*(claims["B"]+values["B"]["ra"]/units)
                if g=="A": loss_release=Q(0)
                if g=="R": loss_release*=share
                nxt["loss_component"]-=loss_release
                new[g]["coverage_units"]-=1; amount=sum(released.values())
                if g=="A": post(g,(cover_account,amount),("revenue_A",-amount))
                elif g=="B": post(g,(cover_account,amount),("revenue_B",-(amount-loss_release)),("B_loss_reversal",-loss_release))
                else: post(g,("R_premium_allocation",amount-loss_release),("R_loss_reversal",loss_release),(cover_account,-amount))
            elif phase=="incurrence":
                amount=claims[g]; nxt["incurred"]+=amount
                if g=="R": post(g,(incurred_account,amount),("R_claim_recovery",-amount))
                else: post(g,("issued_claims",amount),(incurred_account,-amount))
            elif phase=="settlement":
                amount=v["incurred"]; nxt["incurred"]=Q(0)
                if g=="R": post(g,("cash",amount),(incurred_account,-amount))
                else: post(g,(incurred_account,amount),("cash",-amount))
            for k,value in nxt.items(): new[g][k]=rational(value)
        changes={k:Q(0) for k in old_accounts}
        for line in lines: changes[line["account_id"]]+=number(line["amount"])
        assert sum(changes.values())==0
        state={**before,"sequence":before["sequence"]+1,"phase":phase,"groups":list(new.values()),
               "balances":{k:rational(v+changes[k]) for k,v in old_accounts.items()}}
        validate_state(state)
        return state,lines,{k:rational(v) for k,v in changes.items()}

    sequence=opening
    for phase in phases[1:]:
        sequence,_,_=derive(sequence,phase)
        check("independent_phase_state:"+phase,sequence==body(bundle["sequence"][phase],"CompanyState"))
    final=validate_state(sequence)
    observed={k:(-final[k] if k in ["A_LRC","B_LRC","A_LIC","B_LIC"] else final[k]) for k in stock if k!="equity_open"}
    observed["equity"]=equity(sequence)
    check("year_one_matches_checked_schedule",observed=={k:Q(v) for k,v in schedule["states"][1].items() if k in observed})
    for g,obj in group_map(sequence).items():
        for component,suffix in [("pv","pv"),("ra","ra"),("csm","csm"),("loss_component","lrc" if g=="R" else "lc")]:
            key=g+"_"+suffix
            if key in schedule["states"][1]:
                check("year_one_component:"+key,number(obj[component])==Q(schedule["states"][1][key]))

    def published(world):
        # Derive closure from committed roots with a breadth-first walk.
        queue=[r for field in ["committed_state_refs","committed_journal_refs","committed_delta_refs","receipt_refs"] for r in world[field]]
        seen={}; edges={}
        while queue:
            r=queue.pop(0)
            if r["digest"] in seen: continue
            seen[r["digest"]]=r
            for child in record(r)["dependencies"]:
                edge={"from_ref":r,"to_ref":child}; edges[encoding(edge)]=edge; queue.append(child)
        return [seen[d] for d in sorted(seen)],[edges[k] for k in sorted(edges)]

    def validate_world(world):
        expected_refs,expected_edges=published(world)
        assert world["published_record_refs"]==expected_refs and world["published_dependency_edges"]==expected_edges
        head=world["head"]; states=world["committed_state_refs"]; receipts=world["receipt_refs"]
        assert head["state_ref"]==states[-1] and head["generation"]==len(receipts)==len(states)-1
        assert len(world["identity_index"])==len(receipts)==len(world["committed_journal_refs"])==len(world["committed_delta_refs"])
        assert len({encoding(row["identity"]) for row in world["identity_index"]})==len(receipts)
        for i,r in enumerate(receipts):
            receipt=body(r,"StateTransitionReceipt"); req=body(receipt["request_ref"],"OperationRequest")
            basis=body(req["arguments"]["basis_ref"],"AccountingEventBasis")
            assert receipt=={"request_ref":receipt["request_ref"],"identity":basis["identity"],**req["arguments"],
                "opening_ref":states[i],"closing_ref":states[i+1],"generation":i+1,"status":"committed"}
            assert world["identity_index"][i]=={"identity":basis["identity"],"request_ref":receipt["request_ref"],"receipt_ref":r}
            assert world["committed_journal_refs"][i]==receipt["journal_ref"] and world["committed_delta_refs"][i]==receipt["delta_ref"]
            assert req["expected_head"]=={**head,"state_ref":states[i],"generation":i}
            derived,lines,changes=derive(body(states[i],"CompanyState"),body(basis["event_ref"])["phase"])
            assert body(states[i+1],"CompanyState")==derived
            assert body(receipt["journal_ref"])["lines"]==lines
            delta=body(receipt["delta_ref"])
            assert delta["account_changes"]==changes and delta["before_groups"]==body(states[i])["groups"] and delta["after_groups"]==derived["groups"]

    def evaluate(case):
        reqref=case["candidate_request_ref"]; req=body(reqref,"OperationRequest"); args=req["arguments"]
        basis=body(args["basis_ref"],"AccountingEventBasis"); auth=body(args["authorization_ref"],"PostingAuthorization")
        event=body(basis["event_ref"],"EconomicEvent"); opening=body(basis["opening_ref"],"CompanyState")
        profile=body(req["profile_ref"],"PostingProfile"); method=body(basis["method_ref"],"MethodDefinition")
        context=body(basis["context_ref"],"Context"); branch=body(basis["branch_ref"],"Branch")
        timing=body(basis["time_ref"],"Time"); signature=body(req["signature_ref"],"OperationSignature")
        journal=body(args["journal_ref"],"JournalProposal"); delta=body(args["delta_ref"],"EconomicDelta")
        identity=basis["identity"]; owner="/".join(identity[k] for k in ["entity_id","book_id","branch_key"])
        assert identity=={"entity_id":context["entity_id"],"book_id":context["book_id"],"branch_key":branch["branch_key"],"business_event_id":event["business_event_id"]}
        assert set(args)==set(signature["argument_fields"])=={"basis_ref","authorization_ref","journal_ref","delta_ref"}
        assert req["operation"]==signature["operation"]=="accounting.commit@1" and req["operation"] in profile["operations"]
        for key in ["context_ref","branch_ref","time_ref"]: assert event[key]==basis[key]
        for key in ["context_ref","branch_ref","chart_ref"]: assert opening[key]==basis[key]
        chart=body(basis["chart_ref"],"Chart")
        assert chart["context_ref"]==basis["context_ref"] and {a["account_id"] for a in chart["accounts"]}==set(opening["balances"])
        assert req["view_ref"]==basis["view_ref"]==auth["view_ref"]==branch["view_ref"]==timing["view_ref"]
        assert req["expected_head"]=={"owner_key":owner,"state_ref":basis["opening_ref"],"generation":opening["sequence"]}
        assert auth["basis_ref"]==args["basis_ref"] and auth["posting_profile_ref"]==req["profile_ref"]
        assert auth["method_ref"]==basis["method_ref"]==profile["method_ref"]
        assert auth["authority_refs"]==basis["authority_refs"]==method["authority_requirements"]
        assert profile["schema_lock_ref"]==signature["schema_lock_ref"]==bundle["schema_lock_ref"]
        assert signature["result_schema"]==schemas["schema_ids"]["OperationResult"]
        for output in [journal,delta]:
            for key in ["context_ref","chart_ref"]: assert output[key]==basis[key]
            assert output["basis_ref"]==args["basis_ref"] and output["authorization_ref"]==args["authorization_ref"]
        assert date.fromisoformat(timing["reporting_start"])<=date.fromisoformat(timing["economic_date"])<=date.fromisoformat(timing["reporting_end"])
        assert context["annual_period_start"]==timing["reporting_start"]=="2024-01-01"
        assert body(basis["assumptions_ref"],"Assumptions")==assumptions
        assert basis["admission_refs"] and basis["evidence_refs"] and basis["authority_refs"]
        for admission_ref in basis["admission_refs"]:
            admission=body(admission_ref,"Admission")
            assert admission["view_ref"]==basis["view_ref"] and admission["evidence_ref"] in basis["evidence_refs"] and admission["status"]=="synthetic_only"
        sources=[]
        for evidence_ref in basis["evidence_refs"]:
            evidence=body(evidence_ref,"Evidence"); assert evidence["assumptions_ref"]==basis["assumptions_ref"]
            assert evidence["nature"]=="authored_synthetic"; sources.append(evidence["source_ref"])
        for authority_ref in basis["authority_refs"]:
            authority=body(authority_ref,"SyntheticAuthority")
            assert authority["source_ref"] in sources and authority["nature"]=="authored_synthetic"
        validate_state(opening)
        def verdict(code=None,lookup=False,commit=False,receipt=None,state=None,stage=None):
            return {"code":code,"lookup":lookup,"commit":commit,"receipt":receipt,"state":state,"stage":stage}
        measurements=[body(r,"GroupMeasurement") for r in event["measurement_refs"]]
        if event["required_group_ids"]!=["A","B","R"] or [m["group_id"] for m in measurements]!=["A","B","R"]:
            return verdict("GROUP_SET_MISMATCH",stage="bindings")
        for m in measurements:
            if any(m[k]!=basis[k] for k in ["context_ref","branch_ref","time_ref","view_ref","method_ref"]) or m["source_ref"] not in sources:
                return verdict("GROUP_BINDING_MISMATCH",stage="bindings")
            if m["phase"]!=event["phase"] or m["before"]!=group_map(opening)[m["group_id"]]:
                return verdict("GROUP_BINDING_MISMATCH",stage="bindings")
        if branch["book_mode"]!="synthetic" or "synthetic" not in profile["supported_book_modes"]:
            return verdict("BOOK_MODE_NOT_AUTHORIZED",stage="authorization")
        if any(m["status"]!="complete" or m["after"] is None for m in measurements):
            assert all((m["after"] is None and m["reason"]) if m["status"]=="unresolved" else m["reason"] is None for m in measurements)
            return verdict("GROUP_MEASUREMENT_UNRESOLVED",stage="authorization")
        expected_state,expected_lines,expected_changes=derive(opening,event["phase"])
        if any(m["after"]!=group_map(expected_state)[m["group_id"]] or m["reason"] is not None for m in measurements):
            return verdict("GROUP_MEASUREMENT_MISMATCH",stage="authorization")
        assert [f["name"] for f in auth["findings"]]==[g+"_measurement" for g in ["A","B","R"]]
        if auth["posting_permitted"] is not True or auth["status"]!="eligible" or auth["evidence_level"]!="authored-synthetic" or any(f["status"]!="satisfied" for f in auth["findings"]):
            return verdict("POSTING_NOT_AUTHORIZED",stage="authorization")
        # This lookup must follow complete input validation, but precede head freshness.
        def lookup(world,stage):
            indexed=next((row for row in world["identity_index"] if row["identity"]==identity),None)
            if indexed:
                if indexed["request_ref"]==reqref: return verdict(lookup=True,receipt=indexed["receipt_ref"])
                return verdict("EVENT_ID_CONFLICT",lookup=True,stage=stage)
            return None
        found=lookup(case["before"],"receipt_lookup")
        if found: return found
        if req["expected_head"]!=case["before"]["head"]:
            return verdict("STALE_OPENING_STATE",lookup=True,stage="freshness")
        if journal["lines"]!=expected_lines:
            return verdict("JOURNAL_METHOD_MISMATCH",lookup=True,stage="candidate_reconciliation")
        if delta["before_groups"]!=opening["groups"] or delta["after_groups"]!=expected_state["groups"]:
            return verdict("ECONOMIC_DELTA_MISMATCH",lookup=True,stage="candidate_reconciliation")
        if delta["account_changes"]!=expected_changes:
            return verdict("DELTA_MISMATCH",lookup=True,stage="candidate_reconciliation")
        if case["at_recheck"] is not None:
            found=lookup(case["at_recheck"],"atomic_recheck")
            if found: return found
            if req["expected_head"]!=case["at_recheck"]["head"]:
                return verdict("STALE_OPENING_STATE",lookup=True,stage="atomic_recheck")
        return verdict(lookup=True,commit=True,state=expected_state)

    for case in bundle["cases"]:
        name=case["id"]; request=record(case["candidate_request_ref"],"OperationRequest")
        sub=body(case["submission_ref"],"Submission")
        raw=(ROOT/bundle["blobs"][sub["blob_ref"]["digest"]]["path"]).read_bytes()
        check(name+":exact_submission",raw==encoding(request))
        try:
            for world_field in ["before","at_recheck","after","stored_world"]:
                if case.get(world_field) is not None: validate_world(case[world_field])
        except (AssertionError,KeyError,ValueError) as e:
            check(name+":published_world_integrity",False,repr(e))
        else: check(name+":published_world_integrity",True)
        if case["kind"]=="transport_ambiguity":
            observation=body(case["observation_ref"],"TransportObservation")
            check(name+":no_fabricated_received_result",case["expected_result_ref"] is None and observation=={
                "submission_ref":case["submission_ref"],"request_ref":case["candidate_request_ref"],
                "observation":"acknowledgement_timeout","commit_observation":"unknown","receipt_ref":None,
                "next_action":"resubmit_exact_original_request"})
            DERIVED.append({"case":name,"commit_observation":"unknown","stored_generation":case["stored_world"]["head"]["generation"]})
            continue
        try: decision=evaluate(case)
        except (AssertionError,KeyError,ValueError,StopIteration) as e:
            check(name+":independent_decision",False,repr(e)); continue
        check(name+":independent_decision",True)
        code=decision["code"]; commit=decision["commit"]; replay=decision["receipt"]
        result=body(case["expected_result_ref"],"OperationResult")
        check(name+":decision_code",code==case["expected_code"])
        check(name+":lookup_order",decision["lookup"]==case["expected_lookup"])
        check(name+":diagnostics",[(d["code"],d["stage"]) for d in result["diagnostics"]]==([(code,decision["stage"])] if code else []))
        valid=decision["lookup"]
        check(name+":validated_request",result["request_ref"]==(case["candidate_request_ref"] if valid else None))
        check(name+":submission_and_view",result["submission_ref"]==case["submission_ref"]
              and result["input_view_ref"]==(request["body"]["view_ref"] if valid else None)
              and result["operation"]==("accounting.commit@1" if valid else None))
        expected_math="failed" if decision["stage"]=="candidate_reconciliation" else "defined" if valid else "unresolved"
        check(name+":status_dimensions",result["statuses"]=={
            "structural_validity":"valid" if valid else "invalid","mathematical_status":expected_math,
            "computation_status":"complete" if valid else "not_computed","empirical_justification":"not_established",
            "capability_status":"specified_only_no_runtime","accounting_validity":"not_assessed","forecast_validity":"not_assessed",
            "product_readiness":"not_implemented","human_acceptance":"pending"})
        check(name+":disposition",result["disposition"]==("completed" if commit else "replayed" if replay else "rejected"))
        check(name+":commit_observation",result["commit_observation"]==("committed" if commit else "not_committed"))
        if not valid:
            check(name+":no_invalid_publication",result["payload"] is None and result["coverage"] is None and result["receipt_ref"] is None)
            audit=body(case["audit_candidate_ref"],"AuditCandidate")
            check(name+":diagnostic_candidates_retained",audit["submission_ref"]==case["submission_ref"] and audit["reason"]==code
                  and audit["committed"] is False and len(audit["measurement_refs"])==3
                  and case["audit_candidate_ref"] not in case["after"]["published_record_refs"])
        else:
            payload=result["payload"]
            check(name+":payload_commit",payload["additional_commit"] is commit and payload["event_committed"] is bool(commit or replay))
            check(name+":observed_head",payload["observed_head"]==case["after"]["head"])
            coverage=result["coverage"]; domain=body(coverage["domain_ref"],"RequestDomain")
            regions=[body(r,"RequestRegion") for r in coverage["completed"]]
            check(name+":coverage_is_singleton_decision",domain=={"request_ref":case["candidate_request_ref"],"meaning":"singleton_request_decision"}
                  and regions==[{"domain_ref":coverage["domain_ref"],"predicate":"this_request_decision","status":"completed"}]
                  and all(coverage[k]==[] for k in ["unresolved","unsupported","infeasible","cancelled"])
                  and coverage["relation"]=="singleton_partition")
            check(name+":no_rejection_audit_for_valid_request",case["audit_candidate_ref"] is None)
        base_world=case["at_recheck"] if case["at_recheck"] is not None else case["before"]
        if commit:
            receipt_ref=result["receipt_ref"]; receipt=body(receipt_ref,"StateTransitionReceipt")
            check(name+":independent_closing_state",body(receipt["closing_ref"],"CompanyState")==decision["state"])
            expected=deepcopy(base_world)
            expected["head"]={**expected["head"],"state_ref":receipt["closing_ref"],"generation":receipt["generation"]}
            expected["identity_index"].append({"identity":receipt["identity"],"request_ref":case["candidate_request_ref"],"receipt_ref":receipt_ref})
            for field,ref_field in [("committed_state_refs","closing_ref"),("committed_journal_refs","journal_ref"),("committed_delta_refs","delta_ref")]:
                expected[field].append(receipt[ref_field])
            expected["receipt_refs"].append(receipt_ref)
            expected["published_record_refs"],expected["published_dependency_edges"]=published(expected)
            check(name+":all_or_none_publication",case["after"]==expected and result["payload"]["original_receipt_ref"]==receipt_ref)
        else:
            check(name+":requester_committed_nothing",case["after"]==base_world)
            if not replay:
                check(name+":no_receipt_for_rejection",result["receipt_ref"] is None
                      and (result["payload"] is None or result["payload"]["original_receipt_ref"] is None))
        if replay:
            check(name+":original_immutable_receipt",result["receipt_ref"]==replay==result["payload"]["original_receipt_ref"])
            check(name+":replay_before_current_freshness",request["body"]["expected_head"]!=base_world["head"])
        DERIVED.append({"case":name,"code":code,"lookup":decision["lookup"],"additional_commit":commit,
                        "replayed_original_receipt":replay,"derived_closing_state":decision["state"],
                        "external_interference":case["at_recheck"] is not None})

    by_id={c["id"]:c for c in bundle["cases"]}
    check("unique_case_ids",len(by_id)==len(bundle["cases"]))
    first=by_id["finance_commit"]
    for name in ["changed_request_id","changed_budget"]:
        a=deepcopy(record(first["candidate_request_ref"])); b=deepcopy(record(by_id[name]["candidate_request_ref"]))
        if name=="changed_request_id": b["body"]["request_id"]=a["body"]["request_id"]
        else: b["body"]["execution"]["budget"]=a["body"]["execution"]["budget"]
        check(name+":only_declared_field_changes",a==b and first["candidate_request_ref"]!=by_id[name]["candidate_request_ref"])
    replay_result=body(by_id["replay_after_settlement"]["expected_result_ref"])
    check("finance_receipt_survives_generation_four",body(replay_result["receipt_ref"])["generation"]==1
          and replay_result["payload"]["observed_head"]["generation"]==4
          and replay_result["receipt_ref"]==body(first["expected_result_ref"])["receipt_ref"])
    for side,retry in [("before","retry_after_precommit_loss"),("after","retry_after_postcommit_loss")]:
        timeout=by_id["lost_ack_"+side]; retry_case=by_id[retry]
        check("timeout_world:"+side,timeout["stored_world"]==first[side] and retry_case["before"]==timeout["stored_world"])
        check("exact_retry:"+side,timeout["candidate_request_ref"]==retry_case["candidate_request_ref"]==first["candidate_request_ref"]
              and timeout["submission_ref"]==retry_case["submission_ref"]==first["submission_ref"]
              and retry_case["after"]==first["after"])
    check("indistinguishable_transport_observations",body(by_id["lost_ack_before"]["observation_ref"])
          ==body(by_id["lost_ack_after"]["observation_ref"]))
    check("unresolved_measurement_is_not_zero",any(body(r)["status"]=="unresolved" and body(r)["after"] is None
          for r in body(by_id["unresolved_R"]["audit_candidate_ref"])["measurement_refs"]))
    double_request=body(by_id["double_count_component"]["candidate_request_ref"])
    double_lines=body(double_request["arguments"]["journal_ref"])["lines"]
    check("double_count_example_is_balanced_but_wrong",sum(number(line["amount"]) for line in double_lines)==0
          and by_id["double_count_component"]["expected_code"]=="JOURNAL_METHOD_MISMATCH")
    check("unrelated_index_preserved",(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
          ==subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT))
    result={"passed":all(c["passed"] for c in CHECKS),"check_count":len(CHECKS),"checks":CHECKS,
            "derived_cases":DERIVED,"wall_seconds":time.perf_counter()-timer}
    (OUT/"exchange-checks.json").write_text(json.dumps(result,indent=2)+"\n")
    manifest={"command":["python3",str(Path(__file__).relative_to(ROOT))],"started_utc":started,"wall_seconds":result["wall_seconds"],
        "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode().strip(),
        "environment":"system Python, fractions, hashlib, jsonschema "+importlib.metadata.version("jsonschema"),
        "gpu":"N/A; no numerical framework or GPU initialized","random_seeds":"N/A; deterministic documentary fixtures",
        "data_version":"portable-exchanges.json and pinned schema/source/contract bytes",
        "plan":"docs/plans/accounting-insurance-atomic-commit-20261014.md","result":str((OUT/"result.md").relative_to(ROOT)),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "exchange_sha256":hashlib.sha256((OUT/"portable-exchanges.json").read_bytes()).hexdigest()}
    (OUT/"verification-run.json").write_text(json.dumps(manifest,indent=2)+"\n")
    failures=[c for c in CHECKS if not c["passed"]]
    print(json.dumps({"passed":result["passed"],"checks":len(CHECKS),"cases":len(DERIVED),"failures":failures[:12]}))
    if failures: raise SystemExit(1)


if __name__=="__main__":
    main()

