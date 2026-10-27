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

    # Reconstruct opening accounting and aggregate economic state independently.
    def validate_opening(state):
        e=state["contract"]; v={k:number(e[k]) for k in ["price","R","G","A","K","C"]}
        accounts={k:number(x) for k,x in state["balances"].items()}
        advances=e["advances"]; invoices=e["invoices"]; allocations=e["allocations"]
        assert len({a["advance_id"] for a in advances})==len(advances)
        assert len({i["invoice_id"] for i in invoices})==len(invoices)
        assert len({(a["advance_id"],a["invoice_id"]) for a in allocations})==len(allocations)
        assert all(0<=number(a["applied"])<=number(a["received"]) for a in advances)
        assert all(number(i["unpaid"])==number(i["gross"])-number(i["applied"])>=0 for i in invoices)
        assert v["A"]==sum(number(a["received"]) for a in advances)
        assert v["G"]==sum(number(i["gross"]) for i in invoices)
        assert v["K"]==sum(number(a["amount"]) for a in allocations)
        for a in advances:
            assert number(a["applied"])==sum(number(x["amount"]) for x in allocations if x["advance_id"]==a["advance_id"])
        for i in invoices:
            assert number(i["applied"])==sum(number(x["amount"]) for x in allocations if x["invoice_id"]==i["invoice_id"])
        assert all(a["advance_id"] in {v["advance_id"] for v in advances} and a["invoice_id"] in {i["invoice_id"] for i in invoices} for a in allocations)
        assert 0<=v["K"]<=min(v["A"],v["G"]) and 0<=v["C"]<=v["G"]-v["K"]
        t=v["G"]+v["A"]-v["K"]
        assert 0<=t<=v["price"] and 0<=v["R"]<=v["price"]
        derived={"cash":v["A"]+v["C"],"accounts_receivable":v["G"]-v["K"]-v["C"],
                 "contract_asset":max(v["R"]-t,Q(0)),"contract_liability":-max(t-v["R"],Q(0)),"revenue":-v["R"]}
        assert accounts==derived and sum(accounts.values())==0
        return accounts

    for name in ["opening-state","closing-state"]:
        try: validate_opening(body(bundle["aliases"][name],"CompanyState"))
        except AssertionError: check(name+":economic_and_accounting_consistency",False)
        else: check(name+":economic_and_accounting_consistency",True)

    def evaluate(case):
        reqref=case["candidate_request_ref"]; req=body(reqref,"OperationRequest"); args=req["arguments"]
        basis=body(args["basis_ref"],"AccountingEventBasis"); auth=body(args["authorization_ref"],"PostingAuthorization")
        event=body(basis["event_ref"],"EconomicEvent"); opening=body(basis["opening_ref"],"CompanyState")
        profile=body(req["profile_ref"],"PostingProfile"); method=body(basis["method_ref"],"MethodDefinition")
        context=body(basis["context_ref"],"Context"); branch=body(basis["branch_ref"],"Branch")
        timing=body(basis["time_ref"],"Time"); signature=body(req["signature_ref"],"OperationSignature")
        journal=body(args["journal_ref"],"JournalProposal"); delta=body(args["delta_ref"],"EconomicDelta")
        assumptions=body(basis["assumptions_ref"],"Assumptions")
        identity=basis["identity"]; owner="/".join(identity[k] for k in ["entity_id","book_id","branch_key"])
        # All finite submitted bindings precede lookup.
        assert identity=={"entity_id":context["entity_id"],"book_id":context["book_id"],"branch_key":branch["branch_key"],"business_event_id":event["business_event_id"]}
        for key in ["context_ref","branch_ref","time_ref"]: assert event[key]==basis[key]
        for key in ["context_ref","branch_ref","chart_ref"]: assert opening[key]==basis[key]
        assert body(basis["chart_ref"],"Chart")["context_ref"]==basis["context_ref"]
        assert {a["account_id"] for a in body(basis["chart_ref"])["accounts"]}==set(opening["balances"])
        assert event["contract_id"]==opening["contract"]["contract_id"]==assumptions["contract_id"]
        assert assumptions["price"]==opening["contract"]["price"]
        assert assumptions["advance_precedes_all_performance_and_billing"] and assumptions["no_refund_financing_tax_or_impairment_in_slice"]
        assert req["view_ref"]==basis["view_ref"]==auth["view_ref"]==branch["view_ref"]==timing["view_ref"]
        assert req["expected_head"]=={"owner_key":owner,"state_ref":basis["opening_ref"],"generation":opening["sequence"]}
        assert auth["basis_ref"]==args["basis_ref"] and auth["posting_profile_ref"]==req["profile_ref"]
        assert auth["method_ref"]==basis["method_ref"]==profile["method_ref"]
        assert auth["authority_refs"]==basis["authority_refs"]==method["authority_requirements"]
        assert profile["schema_lock_ref"]==signature["schema_lock_ref"]==bundle["schema_lock_ref"]
        for output in [journal,delta]:
            for key in ["context_ref","chart_ref"]: assert output[key]==basis[key]
            assert output["basis_ref"]==args["basis_ref"] and output["authorization_ref"]==args["authorization_ref"]
        assert date.fromisoformat(timing["reporting_start"])<=date.fromisoformat(timing["economic_date"])<=date.fromisoformat(timing["reporting_end"])
        assert context["annual_period_start"]==timing["reporting_start"] and "2023-01-01"<=context["annual_period_start"]<"2026-07-01"
        for admission_ref in basis["admission_refs"]:
            admission=body(admission_ref,"Admission"); assert admission["view_ref"]==basis["view_ref"] and admission["evidence_ref"] in basis["evidence_refs"]
            assert admission["status"]=="synthetic_only"
        for evidence_ref in basis["evidence_refs"]:
            assert body(evidence_ref,"Evidence")["assumptions_ref"]==basis["assumptions_ref"]
        before_accounts=validate_opening(opening)
        econ=opening["contract"]; g,k=number(event["gross"]),number(event["applied_credit"])
        advance=next((a for a in econ["advances"] if a["advance_id"]==event["advance_id"]),None)
        unused=advance is not None and number(advance["received"])-number(advance["applied"])>=k>0
        zero_right=g==k and k>0
        new_invoice=event["invoice_id"] not in {i["invoice_id"] for i in econ["invoices"]}
        synthetic=branch["book_mode"]=="synthetic" and "synthetic" in profile["supported_book_modes"] and auth["evidence_level"]=="authored-synthetic"
        findings={"unused_credit":unused,"zero_new_right":zero_right,"new_invoice":new_invoice,"synthetic_scope":synthetic}
        assert [f["name"] for f in auth["findings"]]==list(findings)
        assert all(f["status"]==("satisfied" if findings[f["name"]] else "failed") for f in auth["findings"])
        if req["operation"] not in profile["operations"]:
            return "UNSUPPORTED_PROFILE_OPERATION",False,False,None,None
        if not all(findings.values()) or auth["status"]!="eligible" or auth["posting_permitted"] is not True:
            return "POSTING_NOT_AUTHORIZED",False,False,None,None
        old_world=case["before"]
        indexed=next((r for r in old_world["identity_index"] if r["identity"]==identity),None)
        if indexed:
            if indexed["request_ref"]==reqref:
                return None,True,False,indexed["receipt_ref"],None
            return "EVENT_ID_CONFLICT",True,False,None,None
        if req["expected_head"]!=old_world["head"]:
            return "STALE_OPENING_STATE",True,False,None,None
        expected_econ=deepcopy(econ)
        expected_econ["G"]=rational(number(econ["G"])+g)
        expected_econ["K"]=rational(number(econ["K"])+k)
        a=next(a for a in expected_econ["advances"] if a["advance_id"]==event["advance_id"])
        a["applied"]=rational(number(a["applied"])+k)
        expected_econ["invoices"].append({"invoice_id":event["invoice_id"],"gross":rational(g),"applied":rational(k),"unpaid":rational(g-k)})
        expected_econ["allocations"].append({"advance_id":event["advance_id"],"invoice_id":event["invoice_id"],"amount":rational(k)})
        expected_state={**opening,"sequence":opening["sequence"]+1,"contract":expected_econ}
        after_accounts=validate_opening(expected_state)
        derived_changes={account:after_accounts[account]-value for account,value in before_accounts.items()}
        assert journal["effect"]=="state_only" and journal["lines"]==[] and all(v==0 for v in derived_changes.values())
        if {a:number(v) for a,v in delta["account_changes"].items()}!=derived_changes:
            return "DELTA_MISMATCH",True,False,None,None
        if delta["before_contract"]!=econ or delta["after_contract"]!=expected_econ:
            return "ECONOMIC_DELTA_MISMATCH",True,False,None,None
        assert expected_econ!=econ
        return None,True,True,None,expected_state

    for case in bundle["cases"]:
        name=case["id"]; request=record(case["candidate_request_ref"],"OperationRequest")
        sub=body(case["submission_ref"],"Submission"); raw=(ROOT/bundle["blobs"][sub["blob_ref"]["digest"]]["path"]).read_bytes()
        check(name+":exact_submission",raw==encoding(request))
        try:
            code,lookup,commit,replay_receipt,derived_state=evaluate(case)
        except (AssertionError,KeyError,ValueError,StopIteration) as e:
            check(name+":independent_binding_and_derivation",False,repr(e)); continue
        check(name+":independent_binding_and_derivation",True)
        result=body(case["expected_result_ref"],"OperationResult")
        check(name+":code",code==case["expected_code"])
        check(name+":response_diagnostics",[d["code"] for d in result["diagnostics"]]==([code] if code else []))
        check(name+":lookup_order",lookup==case["expected_lookup"])
        valid=code not in ["POSTING_NOT_AUTHORIZED","UNSUPPORTED_PROFILE_OPERATION"]
        check(name+":validated_request",result["request_ref"]==(case["candidate_request_ref"] if valid else None))
        expected_math="failed" if code in ["DELTA_MISMATCH","ECONOMIC_DELTA_MISMATCH"] else "defined" if valid else "unresolved"
        check(name+":status_dimensions",result["statuses"]["structural_validity"]==("valid" if valid else "invalid")
              and result["statuses"]["mathematical_status"]==expected_math
              and result["statuses"]["computation_status"]==("complete" if valid else "not_computed"))
        check(name+":response_submission",result["submission_ref"]==case["submission_ref"])
        check(name+":commit_observation",result["commit_observation"]==("committed" if commit else "not_committed"))
        expected_disposition="completed" if commit else "replayed" if replay_receipt else "unsupported" if code=="UNSUPPORTED_PROFILE_OPERATION" else "rejected"
        check(name+":disposition",result["disposition"]==expected_disposition)
        if not valid:
            check(name+":no_invalid_publication",result["payload"] is None and result["coverage"] is None and result["receipt_ref"] is None)
        else:
            check(name+":additional_commit",result["payload"]["additional_commit"] is commit)
            check(name+":observed_head",result["payload"]["observed_head"]==case["after"]["head"])
            domain=body(result["coverage"]["domain_ref"],"RequestDomain")
            regions=[body(r,"RequestRegion") for r in result["coverage"]["completed"]]
            check(name+":coverage_denominator",domain["request_ref"]==case["candidate_request_ref"]
                  and len(regions)==1 and regions[0]["domain_ref"]==result["coverage"]["domain_ref"])
        if commit:
            r=body(result["receipt_ref"],"StateTransitionReceipt"); closing=body(r["closing_ref"],"CompanyState")
            check(name+":independent_closing_state",closing==derived_state)
            req=request["body"]; basis=body(req["arguments"]["basis_ref"],"AccountingEventBasis")
            expected_receipt={"request_ref":case["candidate_request_ref"],"identity":basis["identity"],**req["arguments"],"opening_ref":basis["opening_ref"],"closing_ref":r["closing_ref"],"generation":case["before"]["head"]["generation"]+1,"status":"committed"}
            check(name+":receipt_bindings",r==expected_receipt)
            expected_world=deepcopy(case["before"])
            expected_world["head"]={**case["before"]["head"],"state_ref":r["closing_ref"],"generation":r["generation"]}
            expected_world["identity_index"].append({"identity":r["identity"],"request_ref":case["candidate_request_ref"],"receipt_ref":result["receipt_ref"]})
            for field,ref_field in [("committed_journal_refs","journal_ref"),("committed_delta_refs","delta_ref")]: expected_world[field].append(r[ref_field])
            expected_world["receipt_refs"].append(result["receipt_ref"])
            check(name+":atomic_domain_publication",case["after"]==expected_world)
        else:
            check(name+":all_domain_parts_unchanged",case["after"]==case["before"])
            if not replay_receipt:
                check(name+":no_receipt_for_rejection",result["receipt_ref"] is None
                      and (result["payload"] is None or (result["payload"]["original_receipt_ref"] is None and not result["payload"]["event_committed"])))
        if replay_receipt:
            check(name+":original_immutable_receipt",result["receipt_ref"]==replay_receipt==result["payload"]["original_receipt_ref"])
            check(name+":replay_precedes_freshness",request["body"]["expected_head"]!=case["before"]["head"])
        DERIVED.append({"case":name,"code":code,"lookup":lookup,"additional_commit":commit,"replayed_original_receipt":replay_receipt,
                        "derived_closing_state":derived_state,"domain_changed":case["before"]!=case["after"]})
    by_id={c["id"]:c for c in bundle["cases"]}
    a=deepcopy(record(by_id["positive"]["candidate_request_ref"])); b=deepcopy(record(by_id["changed_request_id"]["candidate_request_ref"])); b["body"]["request_id"]=a["body"]["request_id"]
    check("request_id_only_mutation",a==b)
    check("only_positive_changes_domain",[c["id"] for c in bundle["cases"] if c["before"]!=c["after"]]==["positive"])
    check("frozen_native_nonempty_lines", "`lines: nonempty array<Line>`" in (ROOT/"docs/design/proposal/architecture/accounting-records-contract-v1.md").read_text())
    check("unrelated_index_preserved",(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()==subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT))
    result={"passed":all(c["passed"] for c in CHECKS),"check_count":len(CHECKS),"checks":CHECKS,"derived_cases":DERIVED,"wall_seconds":time.perf_counter()-timer}
    (OUT/"exchange-checks.json").write_text(json.dumps(result,indent=2)+"\n")
    manifest={"command":["python3",str(Path(__file__).relative_to(ROOT))],"started_utc":started,"wall_seconds":result["wall_seconds"],
        "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode().strip(),
        "environment":"system Python, fractions, hashlib, jsonschema "+importlib.metadata.version("jsonschema"),"gpu":"N/A; no numerical framework or GPU initialized",
        "random_seeds":"N/A; deterministic authored documentary fixtures","data_version":"portable-exchanges.json and pinned schema/source/contract bytes",
        "plan":"docs/plans/accounting-state-only-allocation-20261014.md","result":str((OUT/"result.md").relative_to(ROOT)),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"exchange_sha256":hashlib.sha256((OUT/"portable-exchanges.json").read_bytes()).hexdigest()}
    (OUT/"verification-run.json").write_text(json.dumps(manifest,indent=2)+"\n")
    failures=[c for c in CHECKS if not c["passed"]]
    print(json.dumps({"passed":result["passed"],"checks":len(CHECKS),"cases":len(DERIVED),"failures":failures[:12]}))
    if failures: raise SystemExit(1)


if __name__=="__main__":
    main()
