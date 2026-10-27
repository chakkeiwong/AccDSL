"""Keep financial assertion chronology separate from a supplied economic world."""
from pathlib import Path
from copy import deepcopy as cp
import importlib.util

H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("world_binding_source_family",H.parent/"joint-financial-source-20261027/joint.py")
j=importlib.util.module_from_spec(s);s.loader.exec_module(j)
identity,need=j.identity,j.need
FLAGS={**j.t.FLAGS,"posting_authorization":False}
PROFILE="SuppliedReceiptCorrectionWorld/1"


def prepare(family,fid,xid,declaration,did,evidence):
    j.verify(family,fid,xid)
    need(identity(declaration)==did,"external_interpretation")
    j.t.fields(declaration,["profile","input_sha256","interpretation","corrected_financial_head","world","provenance"],"world_declaration_fields")
    need(declaration["profile"]==PROFILE and declaration["input_sha256"]==xid,"world_request_binding")
    need(declaration["provenance"]=="supplied_synthetic_assumption_not_source_admission","synthetic_assumption_only")
    kind=declaration["interpretation"]
    need(kind in ("same_event_receipt_correction","unknown","actual_amendment"),"interpretation_kind")
    if kind!="same_event_receipt_correction":
        need(declaration["world"] is None and declaration["corrected_financial_head"] is None,"no_world_for_unresolved_interpretation")
        return "unresolved_interpretation",[],None
    registry=family["input"]["original"]["registry"]
    head=declaration["corrected_financial_head"]
    need(head in registry,"declared_head_exists")
    record=registry[head]
    need(record["slot"]=="financial_family" and record["disposition"]=="assertion","declared_financial_assertion")
    world=declaration["world"]
    j.t.fields(world,["receipt","family"],"fixed_world_fields")
    need(type(world["receipt"]) is int and world["receipt"] in (6,7) and world["family"] in ("committed","mixed"),"bounded_world_domain")
    need(world==record["payload"],"declared_head_matches_world")
    lineage=[];cursor=head
    while cursor is not None:
        need(cursor not in lineage and cursor in registry,"receipt_lineage")
        ancestor=registry[cursor]
        need(ancestor["slot"]=="financial_family" and ancestor["disposition"]=="assertion","assertion_lineage_only")
        if ancestor["payload"]["family"]!=world["family"]:
            return "unresolved_rights_change",lineage+[cursor],None
        lineage.append(cursor);cursor=ancestor["supersedes"]
    if not family["complete"]:
        return "unresolved_temporal_family",lineage,None
    if family["status"]=="inconsistent_clocks":
        return "inconsistent_clocks",lineage,None
    if any(value["status"]!="selected_conditional" for pair in family["outcomes"] for value in pair):
        return "unresolved_source_family",lineage,None
    selected={value["heads"]["financial_family"] for pair in family["outcomes"] for value in pair}
    if not selected<=set(lineage):
        return "unresolved_interpretation_coverage",lineage,None
    return "conditional_fixed_world",lineage,world


def result_base(family,fid,xid,declaration,did,evidence,status,lineage):
    return dict(profile="BoundReceiptCorrectionWorld/1",**FLAGS, input_sha256=xid,family_sha256=fid,
                declaration_sha256=did,evidence_identity=evidence.audit_identity,status=status,
                selected_source_pairs=cp(family["outcomes"]),source_supports=cp(family["supports"]),
                temporal_remainder=cp(family["remainder"]),temporal_complete=family["complete"],
                declared_lineage=lineage,world_assumption=cp(declaration["world"]),
                financial_row_ids=None,financial_policy="not_assessed_no_actor_message_binding")


def evaluate(family,fid,xid,declaration,did,evidence):
    status,lineage,world=prepare(family,fid,xid,declaration,did,evidence)
    out=result_base(family,fid,xid,declaration,did,evidence,status,lineage)
    if world is not None:
        out["financial_row_ids"]=sorted(row["row_id"] for row in evidence.rows
                                       if row["receipt"]==world["receipt"] and (world["family"]=="mixed" or row["right"]))
    verify(out,identity(out),family,fid,xid,declaration,did,evidence)
    return out


def verify(result,rid,family,fid,xid,declaration,did,evidence):
    need(identity(result)==rid,"external_world_result")
    status,lineage,world=prepare(family,fid,xid,declaration,did,evidence)
    base=result_base(family,fid,xid,declaration,did,evidence,status,lineage)
    j.t.fields(result,list(base),"bound_world_fields")
    for key,value in base.items():
        if key!="financial_row_ids":need(identity(result[key])==identity(value),"exact_"+key)
    if world is None:
        need(result["financial_row_ids"] is None,"unresolved_has_no_rows")
    else:
        old=evidence.numerical({**world,"view":"coarse"})
        fine=evidence.numerical({**world,"view":"refined"})
        need(sorted(old["row_ids"])==sorted(fine["row_ids"]),"protected_world_population_independent_of_observation")
        need(result["financial_row_ids"]==sorted(old["row_ids"]),"complete_protected_world_rows")
        need(len(result["financial_row_ids"])==len(set(result["financial_row_ids"])),"unique_world_rows")
    return True
