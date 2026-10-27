"""Exact global token renaming for the fixed two-decision source question."""
from pathlib import Path
from copy import deepcopy
import importlib.util

H = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("joint_transport_checker", H.parent / "joint-temporal-frontier-20261027/policy_checker.py")
c = importlib.util.module_from_spec(s)
s.loader.exec_module(c)
f = c.f
b = f.b
identity, need = f.identity, f.need


def relation(x, xid, old, oid, new, nid, evidence):
    od, nd = b.derive(x, xid, old, oid, evidence), b.derive(x, xid, new, nid, evidence)
    skeletons = [deepcopy(v) for v in (old, new)]
    for declaration in skeletons:
        for source in declaration["mapping"]["maps"]:
            for stage in ("first", "second"):
                for value in source[stage]:
                    value["token"] = None
    need(identity(skeletons[0]) == identity(skeletons[1]), "only_tokens_change")
    token_maps = {}
    for stage in ("first", "second"):
        forward, inverse = {}, {}
        for left, right in zip(old["mapping"]["maps"], new["mapping"]["maps"]):
            for one, two in zip(left[stage], right[stage]):
                a, z = one["token"], two["token"]
                need(a not in forward or forward[a] == z, "global_label_function")
                need(z not in inverse or inverse[z] == a, "global_label_injection")
                forward[a], inverse[z] = z, a
        token_maps[stage] = sorted(forward.items())
    need(od["status"] == nd["status"] and od["required_keys"] == nd["required_keys"], "same_domain_status")
    forward, inverse, old_rows, new_rows = {}, {}, [], []
    for heads in od["source_head_triples"]:
        left, right = b.rows(x, old, evidence, heads), b.rows(x, new, evidence, heads)
        need(len(left) == len(right), "same_row_count")
        for a, z in zip(left, right):
            need(all(a[key] == z[key] for key in ("id", "support", "mechanism", "a1", "a2", "status")), "same_financial_meaning")
            ak, zk = b.b.policy.keys(a, "never"), b.b.policy.keys(z, "never")
            for index, stage in enumerate(("first", "second")):
                if index == 1 and a["message2"] is None:
                    continue
                first, second = (stage, ak[index]), (stage, zk[index])
                need(first not in forward or forward[first] == second, "functional_full_key")
                need(second not in inverse or inverse[second] == first, "injective_full_key")
                forward[first], inverse[second] = second, first
        old_rows.extend(left)
        new_rows.extend(right)
    old_keys, new_keys = b.d.keys(old_rows), b.d.keys(new_rows)
    need(set(forward) == set(old_keys) and set(inverse) == set(new_keys), "full_key_bijection")
    positions = [new_keys.index(forward[key]) for key in old_keys]
    need(sorted(positions) == list(range(len(old_keys))), "position_permutation")
    return dict(profile="JointStagePolicyRenaming/1", **b.b.FLAGS,
                input_sha256=xid, old_declaration_sha256=oid, new_declaration_sha256=nid,
                old_domain=od, new_domain=nd, token_bijections=b.b.canonical(token_maps),
                old_to_new_positions=positions if od["keys"] is not None else None,
                required_keys=od["required_keys"], row_count=len(old_rows),
                scope="exact_global_two_stage_token_renaming",
                status="exact_bijection" if od["keys"] is not None else "unresolved_domain_budget")


def assignment(rule, positions):
    need(type(rule) is list and len(rule) == len(positions)
         and all(type(v) is int and v in (0, 1) for v in rule), "total_binary_assignment")
    moved = [None] * len(positions)
    for source, target in enumerate(positions):
        moved[target] = rule[source]
    return moved


def evaluate(front, fid, xid, old, oid, new, nid, result, rid, evidence, limit=4096):
    rel = relation(front["input"], xid, old, oid, new, nid, evidence)
    od, nd = rel["old_domain"], rel["new_domain"]
    c.verify(result, rid, front, fid, xid, old, oid, od, identity(od), evidence, limit)
    moved = deepcopy(result)
    moved.update(declaration_sha256=nid, domain_sha256=identity(nd))
    perm = rel["old_to_new_positions"]
    if result["candidates"] is not None:
        need(perm is not None, "assessed_domain_required")
        moved["candidates"] = sorted(assignment(rule, perm) for rule in result["candidates"])
        moved["rejections"] = [dict(policy=assignment(item["policy"], perm), row=item["row"])
                               for item in result["rejections"]]
    c.verify(moved, identity(moved), front, fid, xid, new, nid, nd, identity(nd), evidence, limit)
    fresh = f.partial_policy(front, fid, xid, new, nid, nd, identity(nd), evidence, limit)
    c.verify(fresh, identity(fresh), front, fid, xid, new, nid, nd, identity(nd), evidence, limit)
    need(identity(moved["candidates"]) == identity(fresh["candidates"]), "fresh_target_population")
    for field in ("status", "unknown_outcomes", "pending", "pending_domains", "source_supports", "complete", "known_row_ids"):
        need(identity(result[field]) == identity(moved[field]) == identity(fresh[field]), "preserved_" + field)
    if perm is not None and result["candidates"] is not None:
        inverse = [perm.index(i) for i in range(len(perm))]
        need(sorted(assignment(rule, inverse) for rule in moved["candidates"]) == result["candidates"], "candidate_roundtrip")
        need([dict(policy=assignment(item["policy"], inverse), row=item["row"]) for item in moved["rejections"]]
             == result["rejections"], "witness_roundtrip")
    return dict(profile="JointStagePolicyTransportResult/1", **b.b.FLAGS,
                relation=rel, relation_sha256=identity(rel), old_result_sha256=rid,
                transported=moved, transported_sha256=identity(moved),
                fresh_target_sha256=identity(fresh),
                decision="unresolved_domain_budget" if perm is None else "exact_finite_renaming_verified",
                refinement_claim=False)
