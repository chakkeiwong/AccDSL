"""Independently expected finances, proposed projection and adverse checks."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import shutil

from reference_join import (ROOT, OUT, P5, base_facts, replay_base, derive_company,
    report_request, eps_oracle, digest, file_ref, canonical)
from schema_design import REQUEST_VALIDATOR, RESULT_VALIDATOR, QUANTITIES

BASE_PACKET = P5 / "attempt-03/portable-exchanges.json"
BASE_REF = file_ref(BASE_PACKET, "complete P5 opening, thirteen transitions and annual company report")
BASE_LOCK = json.loads((OUT / "base-packet-lock.json").read_text())
BASE_REF["sha256"] = BASE_LOCK["sha256"]
PREMISES = json.loads((OUT / "premises.json").read_text())
SUPPORT = file_ref(OUT / "premises.json", "all explicit synthetic company/instrument/tax/share scope premises")
EXPECTED = json.loads((OUT / "authored_expectations.json").read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def shape(value, template):
    if isinstance(template, dict):
        return isinstance(value, dict) and set(value) == set(template) and all(shape(value[k], v) for k, v in template.items())
    if isinstance(template, bool):
        return value is None or type(value) is bool
    return isinstance(value, type(template))


def contains_null(value):
    return value is None or isinstance(value, dict) and any(contains_null(v) for v in value.values())


def bridge(request, base, resolve_bytes=None):
    result = dict(wire="CompanyEPSJoin/1", request_sha256=digest(request), status="rejected",
        company=None, eps=None, issues=[], mutations=[], acceptance="conditional_documentary_only")

    def refuse(status, reason):
        result.update(status=status, issues=[reason])
        RESULT_VALIDATOR.validate(result)
        return result

    if not isinstance(request, dict) or set(request) != {"wire", "operation", "world", "base_packet", "premises", "eps"}:
        return refuse("rejected", "request_shape")
    if request["wire"] != "CompanyEPSJoin/1" or request["operation"] != "report":
        return refuse("rejected", "operation")
    if list(REQUEST_VALIDATOR.iter_errors(request)):
        return refuse("rejected", "input_shape")
    if request["world"] not in ("conversion", "redemption"):
        return refuse("unsupported", "settlement_world")
    if not shape(request["base_packet"], BASE_REF) or not shape(request["premises"], PREMISES):
        return refuse("rejected", "input_shape")
    if request["base_packet"] != BASE_REF:
        return refuse("rejected", "base_binding")
    reader = resolve_bytes or (lambda path: path.read_bytes())
    for source, wanted in ((BASE_PACKET,BASE_REF["sha256"]),(OUT/"premises.json",SUPPORT["sha256"])):
        try:
            payload = reader(source)
        except OSError:
            return refuse("unresolved", "source_bytes_missing")
        if hashlib.sha256(payload).hexdigest() != wanted:
            return refuse("rejected", "source_bytes_changed")
    for item in json.loads((OUT / "preservation.json").read_text())["files"]:
        if item["path"] in {"docs/plans/accounting-company-eps-join-20261016.md", "docs/plans/accounting-master-checkpoint.md", "docs/plans/accounting-master-current.md", "data/accounting-master/next-plan.md"}:
            continue  # live routes are intentionally mutable and not calculation inputs
        source = ROOT / item["path"]
        if not source.is_file():
            return refuse("unresolved", "protected_input_missing")
        if hashlib.sha256(source.read_bytes()).hexdigest() != item["sha256"]:
            return refuse("rejected", "protected_input_changed")
    if contains_null(request["premises"]):
        return refuse("unresolved", "finding_missing")
    scope = request["premises"]["scope"]
    if not scope["complete_instrument_inventory"] or not scope["complete_ordinary_share_history"] or not request["premises"]["new_instrument"]["tax"]["complete_consequences"]:
        return refuse("unresolved", "incomplete_company_inputs")
    def reduced(node):
        return all(reduced(v) if isinstance(v,dict) else str(Q(v))==v if k in QUANTITIES else True for k,v in node.items())
    if not reduced(request["premises"]):
        return refuse("rejected", "noncanonical_rational")
    if request["premises"] != PREMISES:
        return refuse("unsupported", "outside_authored_company_subset")
    company = derive_company(request["world"], request["premises"], base)
    result["company"] = company
    expected_request = report_request(request["world"], company, request["premises"], SUPPORT)
    if request["eps"] != expected_request:
        return refuse("rejected", "company_eps_projection_mismatch")
    eps = eps_oracle.calculate(request["eps"])
    result.update(status=eps["status"], eps=eps)
    RESULT_VALIDATOR.validate(result)
    return result


def run():
    started = time.monotonic()
    attempt = OUT / ("attempt-%02d" % (len(list(OUT.glob("attempt-*")))+1))
    attempt.mkdir()
    (attempt/"inputs").mkdir()
    for source in OUT.iterdir():
        if source.is_file() and source.suffix in {".py",".json",".md"}:
            shutil.copy2(source,attempt/"inputs"/source.name)
    checks = []

    def check(name, value, detail=None):
        checks.append(dict(name=name, passed=bool(value), detail=detail))

    for item in json.loads((OUT / "authored-lock.json").read_text())["files"]:
        check("authored-lock/"+item["path"], hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"])
    if not all(c["passed"] for c in checks):
        write(attempt/"checks.json", checks)
        raise SystemExit("Protected authored inputs changed")
    base = replay_base()
    # Reproduce the protected company before introducing a new instrument.
    for key, expected in EXPECTED["baseline"].items():
        target = "profit" if key == "group_profit" else key
        check("base-company/"+key, base["annual"][target] == expected)
    for event, actual in zip(base_facts.EVENTS, base["journals"]):
        for owner in ("P", "S"):
            for key, value in actual["journal"][owner].items():
                check("base-journal/"+event["id"]+"/"+owner+"/"+key, Q(value) == Q(event["journals"].get(owner, {}).get(key, "0")))
    if not all(c["passed"] for c in checks):
        write(attempt/"checks.json", checks)
        raise SystemExit("Base replay failed; joined calculation stopped")
    requests, outputs = {}, {}
    for world in ("conversion", "redemption"):
        company = derive_company(world, PREMISES, base)
        eps = report_request(world, company, PREMISES, SUPPORT)
        request = dict(wire="CompanyEPSJoin/1", operation="report", world=world,
                       base_packet=BASE_REF, premises=PREMISES, eps=eps)
        requests[world] = deepcopy(request)
        before = canonical(request)
        result = bridge(request, base)
        outputs[world] = result
        write(attempt/(world+"-request.json"), request)
        write(attempt/(world+"-result.json"), result)
        check(world+"/status", result["status"] == "conditional_complete", result["issues"])
        check(world+"/determinism", bridge(request, base) == result)
        check(world+"/no-input-or-book-mutation", before == canonical(request) and result["mutations"] == [])
        financials = dict(company["financials"])
        diluted = result["eps"]["diluted"]
        financials.update(diluted_numerator=diluted["continuing_numerator"], diluted_denominator=diluted["denominator"], diluted_eps=diluted["continuing_eps"])
        for key, expected in EXPECTED[world].items():
            check(world+"/"+key, financials[key] == expected, dict(actual=financials[key], expected=expected))
        check(world+"/liability-after-coupon", company["liability_after_coupon"] == "92")
        for short in ("issue", "accrue", "coupon", world):
            event = next(e for e in company["timeline"] if e["id"] == "new."+short)
            actual = {k:v for k,v in event["journal"]["P"].items() if v != "0"}
            check(world+"/journal/"+short, actual == EXPECTED["journal_targets"][short])
        tax_event = next(e for e in company["timeline"] if e["id"] == "tax-h2")
        actual = {k:v for k,v in tax_event["journal"]["P"].items() if v != "0"}
        check(world+"/parent-merged-tax", actual == EXPECTED["journal_targets"]["parent_second_half_tax"])
        for day in company["daily_shares"]:
            added_actual = Q(day["actual"])-10
            check(world+"/no-overlap/"+day["date"], not (added_actual and Q(day["potential"])))
        check(world+"/no-discontinued-result", diluted["discontinued_eps"] == "0")
    cases = []

    def adverse(name, status, code, mutate):
        request = deepcopy(requests["conversion"])
        mutate(request)
        cases.append(dict(id=name, expected_status=status, expected_code=code, request=request))

    adverse("extra-field", "rejected", "request_shape", lambda r:r.__setitem__("commit", True))
    adverse("wrong-base-packet", "rejected", "base_binding", lambda r:r["base_packet"].__setitem__("sha256", "0"*64))
    for field in ("complete_consequences", "tax_bases_follow_book", "effective_interest_deductible_at_accrual"):
        adverse("missing-tax-"+field, "unresolved", "finding_missing", lambda r,field=field:r["premises"]["new_instrument"]["tax"].__setitem__(field,None))
    adverse("different-tax-base", "unsupported", "outside_authored_company_subset", lambda r:r["premises"]["new_instrument"]["tax"].__setitem__("initial_liability_tax_base","100"))
    adverse("early-conversion", "unsupported", "outside_authored_company_subset", lambda r:r["premises"]["new_instrument"].__setitem__("maturity_date","2026-01-01"))
    adverse("participating-rights", "unsupported", "outside_authored_company_subset", lambda r:r["premises"]["scope"].__setitem__("nonparticipating_rights",False))
    adverse("incomplete-inventory", "unresolved", "incomplete_company_inputs", lambda r:r["premises"]["scope"].__setitem__("complete_instrument_inventory",False))
    adverse("incomplete-share-history", "unresolved", "incomplete_company_inputs", lambda r:r["premises"]["scope"].__setitem__("complete_ordinary_share_history",False))
    adverse("missing-total-field", "rejected", "input_shape", lambda r:r["eps"]["series"][0].pop("total_increment"))
    adverse("malformed-premise-number", "rejected", "input_shape", lambda r:r["premises"].__setitem__("ordinary_opening_shares","10.0"))
    adverse("unreduced-premise-number", "rejected", "noncanonical_rational", lambda r:r["premises"].__setitem__("ordinary_opening_shares","20/2"))
    for field,value in (("continuing_numerator","99"),("total_numerator","99"),("continuing_numerator","93/2"),("denominator","16")):
        adverse("wrong-basic-"+field+"-"+value, "rejected", "company_eps_projection_mismatch", lambda r,field=field,value=value:r["eps"]["basic"].__setitem__(field,value))
    adverse("missing-tax-addback", "rejected", "company_eps_projection_mismatch", lambda r:r["eps"]["series"][0].__setitem__("continuing_increment","4"))
    adverse("double-weighting", "rejected", "company_eps_projection_mismatch", lambda r:r["eps"]["series"][0].__setitem__("share_increment","552/133225"))
    adverse("overlapping-potential", "rejected", "company_eps_projection_mismatch", lambda r:r["eps"]["series"][0]["potential_windows"][0].__setitem__("end_exclusive","2026-01-01"))
    adverse("missing-actual-window", "rejected", "company_eps_projection_mismatch", lambda r:r["eps"]["series"][0].__setitem__("actual_windows",[]))
    for field in ("entity","population","period","share_basis","head","view"):
        def mutate(r, field=field):
            r["eps"]["context"][field] = dict(start="2025-07-01",end_exclusive="2026-01-01") if field == "period" else "changed"
            binding = eps_oracle.digest(r["eps"]["context"])
            r["eps"]["context_ref"]=binding
            r["eps"]["basic"]["context_ref"]=binding
            r["eps"]["series"][0]["context_ref"]=binding
        adverse("self-consistent-wrong-"+field, "rejected", "company_eps_projection_mismatch", mutate)
    write(attempt/"adverse-authored-inputs.json", cases)
    write(attempt/"adverse-authored-lock.json", dict(sha256=hashlib.sha256((attempt/"adverse-authored-inputs.json").read_bytes()).hexdigest()))
    adverse_results=[]
    for case in cases:
        result=bridge(case["request"],base)
        adverse_results.append(dict(id=case["id"],result=result))
        check("adverse/"+case["id"]+"/status",result["status"]==case["expected_status"])
        check("adverse/"+case["id"]+"/reason",case["expected_code"] in result["issues"])
        check("adverse/"+case["id"]+"/no-eps-or-mutation",result["eps"] is None and result["mutations"]==[])
    write(attempt/"adverse-results.json",adverse_results)
    def missing(path):
        raise FileNotFoundError("independently injected resolver outage")
    for name,resolver,status,code in (("absent-source",missing,"unresolved","source_bytes_missing"),
        ("changed-source",lambda path:b"changed source bytes","rejected","source_bytes_changed")):
        result=bridge(requests["conversion"],base,resolve_bytes=resolver)
        check("resolver/"+name,result["status"]==status and code in result["issues"] and result["eps"] is None)
    write(attempt/"checks.json",checks)
    failures=[c for c in checks if not c["passed"]]
    summary=dict(started_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,
        checks=len(checks),failures=len(failures),failure_details=failures[:20],worlds=2,
        base_events=len(base["journals"]),joined_events_per_world=len(outputs["conversion"]["company"]["timeline"]),
        adverse_cases=len(cases),daily_observations=730,wall_seconds=round(time.monotonic()-started,3),
        cpu_only=os.environ.get("CUDA_VISIBLE_DEVICES")=="-1",python=sys.version.split()[0],platform=platform.platform(),
        git_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        scope="finite documentary company/earnings/tax/cash/share/EPS join; not runtime or actual-law admission")
    write(attempt/"summary.json",summary)
    print(json.dumps(summary))
    return 1 if failures else 0


if __name__=="__main__":
    raise SystemExit(run())
