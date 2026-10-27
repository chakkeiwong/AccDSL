"""Independent exact-finance, source, identity and store-world checks."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
from copy import deepcopy
import hashlib,json,subprocess,time
from jsonschema import Draft202012Validator
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];START=time.perf_counter()
checks=[]
def check(name,ok,detail=None):checks.append({"name":name,"passed":bool(ok),"detail":detail})
def enc(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def num(v):return F(int(v["n"]),int(v["d"]))
def nums(d):return {k:num(v) for k,v in d.items()}
def refs(x):
    if isinstance(x,dict):
        if set(x)=={"kind","schema","digest"}:yield x
        else:
            for v in x.values():yield from refs(v)
    elif isinstance(x,list):
        for v in x:yield from refs(v)
d=json.loads((OUT/"portable-exchanges.json").read_text());reg=d["record_registry"];aliases=d["aliases"]
s=json.loads((OUT/"record-schemas.json").read_text())
def record(r):return reg[r["digest"]]
def body(r):return record(r)["body"]
def named(k):return body(aliases[k])
for digest,r in reg.items():
    errors=list(Draft202012Validator(s["$defs"][r["kind"]]).iter_errors(r["body"]))
    check("shape:"+r["key"],not errors,[e.message[:160] for e in errors])
    actual=hashlib.sha256(("accdsl.portable.v1/"+r["schema"]).encode()+b"\0"+enc(r)).hexdigest()
    check("digest:"+r["key"],actual==digest)
    deps={enc(x) for x in refs(r["body"])}
    check("dependencies:"+r["key"],deps=={enc(x) for x in r["dependencies"]})
    for ref in r["dependencies"]:
        target=reg.get(ref["digest"])
        check("link:"+r["key"]+":"+ref["digest"][:8],target is not None and
              target["kind"]==ref["kind"] and target["schema"]==ref["schema"])
def closure(roots):
    complete=set();active=set()
    def visit(r):
        h=r["digest"]
        if h in active:raise ValueError("cyclic dependency")
        if h in complete:return
        active.add(h)
        for x in record(r)["dependencies"]:visit(x)
        active.remove(h);complete.add(h)
    for r in roots:visit(r)
    return complete
check("acyclic_closure",len(closure(list(aliases.values())))==len(reg))
for h,b in d["blobs"].items():
    p=ROOT/b["path"];check("blob:"+h[:10],sha(p)==h and p.stat().st_size==b["byte_length"])
for x in d["source_pins"]:check("protected:"+x["path"],sha(ROOT/x["path"])==x["sha256"])
for kind in ["OperationRequest","OperationResult"]:
    old=json.loads((ROOT/"data/accounting-master/corporate-portable-20261015/record-schemas.json").read_text())["$defs"][kind]
    check("common_envelope:"+kind,set(old["properties"])==set(s["$defs"][kind]["properties"]))
check("closed_group_profile",named("profile")["profile_id"]=="GroupForeignOperation/1"
      and named("profile")["schema_lock_ref"]==d["schema_lock_ref"])
check("same_labels_distinct_entities",named("Subsidiary-S")["display_name"]==named("Other-S")["display_name"]
      and named("Subsidiary-S")["entity_id"]!=named("Other-S")["entity_id"])
case=json.loads((ROOT/"data/accounting-master/p17-completion-20261014/P17-05/group-fx-disposal/group-cases.json").read_text())
f=case["facts"];q=lambda k:F(f[k])
r0,r1,r2=[q(k) for k in ["acquisition_rate","operation_rate","closing_disposal_rate"]]
own,nci=q("ownership"),q("nci")
na=q("sub_cash_eur")+q("sub_inventory_eur")-q("sub_payable_eur")
gw=q("consideration_eur")+nci*na-na
pcash=q("parent_opening_usd")-q("consideration_eur")*r0
subcash=q("sub_cash_eur")+q("sale_revenue_eur")-q("payable_paid_eur")
profit=(q("sale_revenue_eur")-q("cost_sold_eur"))*r1
cta_na=na*(r2-r0)+(q("sale_revenue_eur")-q("cost_sold_eur"))*(r2-r1)
cta_parent=own*cta_na+gw*(r2-r0);cta_nci=nci*cta_na
cfo=(q("sale_revenue_eur")-q("payable_paid_eur"))*r1
cfi=(q("sub_cash_eur")-q("consideration_eur"))*r0
cashfx=q("sub_cash_eur")*(r2-r0)+(q("sale_revenue_eur")-q("payable_paid_eur"))*(r2-r1)
accts=list(named("state.initial")["balances"]);perf=list(named("state.initial")["movements"])
def blank(values,keys):return {k:F(values.get(k,0)) for k in keys}
financial={}
financial["A"]=(blank({"Cash":pcash+q("sub_cash_eur")*r0,"Inventory":q("sub_inventory_eur")*r0,
    "Goodwill":gw*r0,"Payable":-q("sub_payable_eur")*r0,"NCI":-nci*na*r0,
    "Parent capital":-q("parent_opening_usd")},accts),blank({"cfi_acquisition":cfi,"nci_introduced":nci*na*r0},perf))
financial["O"]=(blank({"Cash":pcash+subcash*r1,"Goodwill":gw*r0,"NCI":-nci*na*r1,
    "Parent CTA":-own*na*(r1-r0),"Parent capital":-q("parent_opening_usd"),
    "Revenue":-q("sale_revenue_eur")*r1,"Cost of sales":q("cost_sold_eur")*r1},accts),
    blank({"profit":profit,"parent_profit":own*profit,"nci_profit":nci*profit,"oci":na*(r1-r0),
        "parent_oci":own*na*(r1-r0),"nci_oci":nci*na*(r1-r0),"cfo":cfo,"cfi_acquisition":cfi,
        "cash_fx":q("sub_cash_eur")*(r1-r0),"nci_introduced":nci*na*r0},perf))
financial["R"]=(blank({"Cash":pcash+subcash*r2,"Goodwill":gw*r2,"NCI":-nci*subcash*r2,
    "Parent CTA":-cta_parent,"Parent capital":-q("parent_opening_usd"),"Parent operating retained profit":-own*profit},accts),
    blank({"profit":profit,"parent_profit":own*profit,"nci_profit":nci*profit,"oci":cta_na+gw*(r2-r0),
        "parent_oci":cta_parent,"nci_oci":cta_nci,"cfo":cfo,"cfi_acquisition":cfi,"cash_fx":cashfx,"nci_introduced":nci*na*r0},perf))
for arm,a in case["alternatives"].items():
    cash,value=F(a["proceeds_usd"]),F(a["retained_fv_usd"])
    gain=cash+value+nci*subcash*r2-(subcash+gw)*r2+cta_parent
    financial[arm]=(blank({"Cash":pcash+cash,"Retained investment":value,"Parent capital":-q("parent_opening_usd"),
        "Parent operating retained profit":-own*profit,"Disposal gain":-gain},accts),
        blank({"profit":profit+gain,"parent_profit":own*profit+gain,"nci_profit":nci*profit,
        "oci":cta_nci,"nci_oci":cta_nci,"cfo":cfo,"cfi_acquisition":cfi,"cfi_disposal":cash-subcash*r2,
        "cash_fx":cashfx,"nci_introduced":nci*na*r0,"nci_removed":nci*subcash*r2},perf))
for key,(balances,mov) in financial.items():
    st=named("state."+key)
    check("independent_balances:"+key,nums(st["balances"])==balances)
    check("independent_movements:"+key,nums(st["movements"])==mov)
    check("balance:"+key,sum(balances.values())==0)
    check("cash_bridge:"+key,q("parent_opening_usd")+sum(mov[k] for k in ["cfo","cfi_acquisition","cfi_disposal","cff","cash_fx"])==balances["Cash"])
    total_equity=sum(balances[k] for k in ["Cash","Inventory","Goodwill","Retained investment","Payable"])
    check("equity_bridge:"+key,q("parent_opening_usd")+mov["profit"]+mov["oci"]+mov["nci_introduced"]-mov["nci_removed"]==total_equity)
    check("income_attribution:"+key,mov["profit"]==mov["parent_profit"]+mov["nci_profit"] and mov["oci"]==mov["parent_oci"]+mov["nci_oci"])

def financial_key(b):
    if b["stage"]!="D":return b["stage"]
    settle=body(b["settlement_ref"])
    return "full_sale" if num(settle["retained_fraction"])==0 else "retain_twenty_percent"
def inspect_request(req,before):
    op=req["operation"];args=req["arguments"]["value"];v=body(req["view_ref"])
    if req["arguments"]["tag"]!=op or body(req["signature_ref"])["operation"]!=op:return "signature_mismatch",False
    if op=="report.build@1":
        st=body(args["state_ref"])
        if body(v["control_ref"])["power"]=="unknown":return "control_assessment_unresolved",True
        if any(body(r)["quote_per_base"] is None for r in v["rate_refs"]):return "rate_measurement_unresolved",True
        if args["require_current"] and st["view_ref"]!=req["view_ref"]:return "stale_dependency_view",False
        return None,True
    b=body(args["basis_ref"]);opening=body(b["opening_ref"]);p=body(b["target_perimeter_ref"])
    if b["information_mode"]!="archival_synthetic":return "missing_public_time",False
    if b["identity"]["branch_key"]!=opening["branch_key"]:return "branch_mismatch",False
    entity_ids={body(body(r)["entity_ref"])["entity_id"] for r in b["entity_book_refs"]}
    if entity_ids!={"Parent-P","Subsidiary-S"}:return "entity_mismatch",False
    rs=[body(r) for r in b["rate_refs"]]
    if any(r["base"]!="EUR" or r["quote"]!="USD" for r in rs):return "currency_direction_mismatch",False
    if [r["instant"] for r in rs]!=[1,2,3]:return "rate_time_mismatch",False
    if b["rate_refs"]!=v["rate_refs"] or b["view_ref"]!=req["view_ref"]:return "dependency_view_mismatch",False
    if b["entity_book_refs"]!=p["entity_book_refs"]:return "book_selection_mismatch",False
    expected_time=3 if b["stage"]=="D" else p["instant"]
    if any(body(r)["instant"]!=expected_time for r in b["entity_book_refs"]):return "book_time_mismatch",False
    if p["includes_subsidiary"]!=(0<p["instant"]<4):return "control_interval_mismatch",False
    auth=body(args["authorization_ref"])
    if not auth["posting_permitted"] or auth["basis_ref"]!=args["basis_ref"]:return "authorization_mismatch",False
    values=nums(opening["balances"]);j=body(args["journal_ref"]);de=body(args["delta_ref"])
    if j["basis_ref"]!=args["basis_ref"] or de["basis_ref"]!=args["basis_ref"]:return "basis_mismatch",False
    for entry in j["entries"]:
        if sum(num(z["signed_amount"]) for z in entry["lines"])!=0:return "journal_unbalanced",False
        for line in entry["lines"]:values[line["account"]]+=num(line["signed_amount"])
        if values["Inventory"]<0 or values["Payable"]>0:return "wrong_intermediate_state",False
    key=financial_key(b);target,mov=financial[key]
    if values!=target:
        if values["Retained investment"]!=target["Retained investment"]:return "wrong_cash_target",False
        if values["Parent CTA"]!=target["Parent CTA"]:return "wrong_reserve_owner",False
        return "wrong_disposal_perimeter",False
    closing=body(de["closing_ref"])
    if nums(closing["balances"])!=target or nums(closing["movements"])!=mov:return "wrong_delta_target",False
    if nums(de["movement_change"])!={k:mov[k]-num(opening["movements"][k]) for k in perf}:return "wrong_movement_delta",False
    event="/".join(b["identity"].values())
    if event in before["event_receipts"]:return "lookup",True
    if req["expected_head"]!=before["head"]:return "stale_head",True
    return None,True
by={x["id"]:x for x in d["exchanges"]}
for x in d["exchanges"]:
    name=x["id"];rq=body(x["request_ref"]);res=body(x["response_ref"]);before=x["world_before"];after=x["world_after"]
    sub=body(x["submission_ref"]);bref=sub["blob_ref"];wire=(ROOT/d["blobs"][bref["digest"]]["path"]).read_bytes()
    check("wire:"+name,wire==enc(record(x["request_ref"])))
    code,valid=inspect_request(rq,before)
    if code=="lookup":
        basis=body(rq["arguments"]["value"]["basis_ref"]);event="/".join(basis["identity"].values())
        previous=before["event_receipts"][event]
        code=None if previous["request_ref"]==x["request_ref"] else "idempotency_conflict"
        disposition="replayed" if code is None else "rejected"
    elif code in ["control_assessment_unresolved","rate_measurement_unresolved"]:disposition="partial"
    else:disposition="rejected" if code else "completed"
    check("decision:"+name,res["disposition"]==disposition and
          ([z["code"] for z in res["diagnostics"]]==([code] if code else [])))
    check("validated_request:"+name,res["request_ref"]==(x["request_ref"] if valid else None))
    check("owners:"+name,before["unaffected_owners"]==after["unaffected_owners"])
    check("no_runtime_claim:"+name,res["statuses"]["capability_status"]=="specified_only_no_runtime" and
          res["statuses"]["product_readiness"]=="not_implemented")
    mutation=rq["operation"]=="accounting.commit@1" and disposition=="completed"
    if mutation:
        args=rq["arguments"]["value"];basis=body(args["basis_ref"]);rec=body(res["receipt_ref"]);delta=body(args["delta_ref"])
        expected=deepcopy(before)
        expected["head"]={"owner_key":body(delta["closing_ref"])["owner_key"],"state_ref":delta["closing_ref"],
            "generation":before["head"]["generation"]+1}
        event="/".join(basis["identity"].values())
        expected["event_receipts"][event]={"request_ref":x["request_ref"],"receipt_ref":res["receipt_ref"]}
        for dst,r in [("journals",args["journal_ref"]),("deltas",args["delta_ref"]),("receipts",res["receipt_ref"])]:expected[dst].append(r)
        expected["published_records"]=sorted(set(before["published_records"])|closure([res["receipt_ref"]]))
        check("atomic_world:"+name,after==expected)
        check("receipt:"+name,rec["request_ref"]==x["request_ref"] and rec["closing_ref"]==delta["closing_ref"]
              and rec["generation"]==expected["head"]["generation"])
        check("commit_status:"+name,res["commit_observation"]=="committed" and res["payload"]["additional_commit"])
    else:
        check("no_mutation:"+name,after==before and res["commit_observation"]=="not_committed")
        check("no_extra_commit:"+name,res["payload"] is None or not res["payload"]["additional_commit"])
    if not valid:check("invalid_payload:"+name,res["payload"] is None and res["coverage"] is None)
    else:
        cov=res["coverage"];regions=sum((cov[k] for k in ["completed","unresolved","unsupported","infeasible","cancelled"]),[])
        check("coverage:"+name,len(regions)==1 and body(regions[0])["domain_ref"]==cov["domain_ref"] and
              body(cov["domain_ref"])["request_ref"]==x["request_ref"])
    if rq["operation"]=="report.build@1" and disposition=="completed":
        output=body(res["payload"]["result_refs"][0]);key="full_sale" if name=="report-full" else "retain_twenty_percent"
        bal,mov=financial[key];actual=nums(output["values"])
        target={"cash":bal["Cash"],"assets":sum(bal[a] for a in ["Cash","Inventory","Goodwill","Retained investment"]),
            "liabilities":-bal["Payable"],"equity":bal["Cash"]+bal["Retained investment"],
            "goodwill":bal["Goodwill"],"retained_investment":bal["Retained investment"],"closing_nci":-bal["NCI"],**mov}
        check("full_report:"+name,actual==target)
for first,second in [("A","O"),("O","R")]:
    check("connected_store:"+second,by[first]["world_after"]==by[second]["world_before"])
for arm in case["alternatives"]:
    fork=named("fork."+arm)
    check("fork:"+arm,fork["forked_from_ref"]==aliases["state.R"] and fork["balances"]==named("state.R")["balances"] and
          fork["movements"]==named("state.R")["movements"] and fork["owner_key"]!=named("state.R")["owner_key"])
lost=d["lost_acknowledgement"];ob=body(lost["observation_ref"])
check("unknown_transport",ob["commit_observation"]=="unknown" and ob["receipt_ref"] is None)
check("lost_ack_worlds",lost["before_publication"]==by["retain_twenty_percent"]["world_before"] and
      lost["after_publication"]==by["retain_twenty_percent"]["world_after"]==by["replay"]["world_before"])
check("retry_exact_bytes",by["replay"]["request_ref"]==by["retain_twenty_percent"]["request_ref"] and
      by["replay"]["submission_ref"]==by["retain_twenty_percent"]["submission_ref"])
check("partial_publication_rejected",d["invalid_partial_publication"] not in
      [lost["before_publication"],lost["after_publication"]] and
      d["invalid_partial_publication"]["head"]==lost["before_publication"]["head"] and
      d["invalid_partial_publication"]["event_receipts"]==lost["after_publication"]["event_receipts"])
check("cash_fx_not_oci",cashfx!=financial["R"][1]["oci"])
check("remaining_nci_income",financial["full_sale"][0]["NCI"]==0 and financial["full_sale"][1]["nci_profit"]==5 and
      financial["full_sale"][1]["nci_oci"]==F("2.2"))
package=json.loads((OUT/"extension-package.json").read_text())
for x in [package["record_schemas"],package["packet"],*package["additional_sources"]]:
    check("package_pin:"+x["path"],sha(ROOT/x["path"])==x["sha256"])
check("package_operations",set(r["digest"] for r in package["operation_signatures"])==
      {aliases["signature.accounting.commit@1"]["digest"],aliases["signature.report.build@1"]["digest"]})
check("package_examples",[x["exchange_id"] for x in package["example_refs"]]==[x["id"] for x in d["exchanges"]])
for key in ["authority_refs","method_refs","operation_signatures"]:
    check("package_closure:"+key,all(r["digest"] in reg for r in package[key]))
check("unrelated_index",subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)==
      (ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes())
result={"passed":all(x["passed"] for x in checks),"check_count":len(checks),"checks":checks,
    "case_sha256":sha(OUT/"portable-exchanges.json"),"wall_seconds":time.perf_counter()-START,
    "scope":"Independent finite documentary arithmetic, closure and authored store worlds; no runtime/fault injection or real source admission."}
(OUT/"independent-checks.json").write_text(json.dumps(result,indent=2)+"\n")
(OUT/"independent-finances.json").write_text(json.dumps({k:{"balances":{a:str(v) for a,v in b.items()},
    "movements":{a:str(v) for a,v in m.items()}} for k,(b,m) in financial.items()},indent=2)+"\n")
print(json.dumps({"passed":result["passed"],"checks":len(checks),
    "failed":[{"name":x["name"],"detail":x["detail"]} for x in checks if not x["passed"]][:15]}))
if not result["passed"]:raise SystemExit(1)
