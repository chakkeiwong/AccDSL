"""Finite joint-stage observation refinement with explicit unassessed results."""
from pathlib import Path
from copy import deepcopy as cp
import importlib.util

H = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("joint_refinement_transport", H.parent / "joint-domain-transport-20261027/transport.py")
r = importlib.util.module_from_spec(s)
s.loader.exec_module(r)
f, b, c = r.f, r.b, r.c
identity, need = r.identity, r.need


def relation(x, xid, old, oid, new, nid, evidence):
    od, nd = b.derive(x, xid, old, oid, evidence), b.derive(x, xid, new, nid, evidence)
    skeletons = [cp(v) for v in (old, new)]
    for declaration in skeletons:
        for source in declaration["mapping"]["maps"]:
            for stage in ("first", "second"):
                for value in source[stage]:
                    value["token"] = None
    need(identity(skeletons[0]) == identity(skeletons[1]), "only_declared_tokens_change")
    erasures = {}
    for stage in ("first", "second"):
        erase, coarse = {}, set()
        for left, right in zip(old["mapping"]["maps"], new["mapping"]["maps"]):
            for a, z in zip(left[stage], right[stage]):
                ot, nt = a["token"], z["token"]
                need(nt not in erase or erase[nt] == ot, "global_token_erasure")
                erase[nt] = ot
                coarse.add(ot)
        need(set(erase.values()) == coarse, "surjective_token_erasure")
        erasures[stage] = sorted(erase.items())
    keyerase, old_rows, new_rows = {}, [], []
    for heads in od["source_head_triples"]:
        left, right = b.rows(x, old, evidence, heads), b.rows(x, new, evidence, heads)
        need(len(left) == len(right), "same_action_rows")
        for a, z in zip(left, right):
            need(all(a[key] == z[key] for key in ("id", "support", "mechanism", "a1", "a2", "status")), "same_financial_meaning")
            ak, zk = b.b.policy.keys(a, "never"), b.b.policy.keys(z, "never")
            for index, stage in enumerate(("first", "second")):
                if index == 1 and a["message2"] is None:
                    continue
                coarse, fine = (stage, ak[index]), (stage, zk[index])
                need(fine not in keyerase or keyerase[fine] == coarse, "functional_full_key_erasure")
                keyerase[fine] = coarse
        old_rows.extend(left)
        new_rows.extend(right)
    ok, nk = b.d.keys(old_rows), b.d.keys(new_rows)
    need(set(keyerase) == set(nk) and set(keyerase.values()) == set(ok), "surjective_full_key_erasure")
    return dict(profile="JointStageObservationRefinement/1", **b.b.FLAGS,
                input_sha256=xid, old_declaration_sha256=oid, new_declaration_sha256=nid,
                old_domain=od, new_domain=nd, message_erasures=b.b.canonical(erasures),
                new_to_old_positions=[ok.index(keyerase[key]) for key in nk],
                scope="same_joint_source_question_declared_refinement")


def known_rows(front, declaration, evidence):
    rows = []
    for pair in front["outcomes"]:
        if any(value["status"] != "selected_conditional" for value in pair):
            continue
        need(pair[0]["heads"]["financial_family"] == pair[1]["heads"]["financial_family"], "fixed_financial_family")
        heads = (pair[0]["heads"]["financial_family"], pair[0]["heads"]["observation_scheme"], pair[1]["heads"]["observation_scheme"])
        rows.extend(b.rows(front["input"], declaration, evidence, heads))
    return rows


def terms(rows, keys):
    positions = {key: i for i, key in enumerate(keys)}
    result = set()
    for row in rows:
        one, two = b.b.policy.keys(row, "never")
        term = ((positions[("first", one)], int(row["a1"] == "draw")),)
        if row["status"] == "refused2":
            term += ((positions[("second", two)], int(row["a2"] == "draw")),)
        elif row["status"] != "refused1":
            continue
        result.add(tuple(sorted(term)))
    return result


def reached(rule, keys, rows):
    actions = dict(zip(keys, rule))
    result = set()
    for row in rows:
        one, two = b.b.policy.keys(row, "never")
        if actions[("first", one)] != int(row["a1"] == "draw"):
            continue
        if row["message2"] is not None and actions[("second", two)] != int(row["a2"] == "draw"):
            continue
        result.add(row["id"])
    return tuple(sorted(result))


def evaluate(front, fid, xid, old, oid, new, nid, evidence, limit=4096):
    rel = relation(front["input"], xid, old, oid, new, nid, evidence)
    od, nd = rel["old_domain"], rel["new_domain"]
    a = f.partial_policy(front, fid, xid, old, oid, od, identity(od), evidence, limit)
    z = f.partial_policy(front, fid, xid, new, nid, nd, identity(nd), evidence, limit)
    c.verify(a, identity(a), front, fid, xid, old, oid, od, identity(od), evidence, limit)
    c.verify(z, identity(z), front, fid, xid, new, nid, nd, identity(nd), evidence, limit)
    for key in ("unknown_outcomes", "source_supports", "pending", "pending_domains", "complete", "known_row_ids"):
        need(identity(a[key]) == identity(z[key]), "preserved_" + key)
    base = dict(profile="JointStageRefinementResult/1", **b.b.FLAGS,
                relation=rel, relation_sha256=identity(rel), frontier_sha256=fid,
                old_result=a, new_result=z, actual_information_claim=False)
    if a["candidates"] is None or z["candidates"] is None:
        return dict(base, decision="unassessed_policy_relation", lifted_candidates=None,
                    constant_fiber_candidates=None, additional_candidates=None,
                    old_reached_behaviors=None, new_reached_behaviors=None,
                    additional_reached_behaviors=None,
                    behavior_scope="no_admissible_clock_assignment" if front["status"] == "inconsistent_clocks" else "unresolved_domain_budget")
    ok = [f.t.prior.tuples(k) for k in od["keys"]]
    nk = [f.t.prior.tuples(k) for k in nd["keys"]]
    ar, zr = known_rows(front, old, evidence), known_rows(front, new, evidence)
    erase = rel["new_to_old_positions"]
    erased_terms = {tuple(sorted(set((erase[i], bit) for i, bit in term))) for term in terms(zr, nk)}
    need(erased_terms == terms(ar, ok), "exact_erased_financial_refusals")
    lifts = {tuple(rule[i] for i in erase) for rule in a["candidates"]}
    fine = {tuple(rule) for rule in z["candidates"]}
    constant = set()
    for rule in fine:
        fibers = {}
        for i, old_index in enumerate(erase):
            fibers.setdefault(old_index, set()).add(rule[i])
        if all(len(values) == 1 for values in fibers.values()):
            constant.add(rule)
    need(lifts == constant and lifts <= fine, "exact_constant_fiber_lifts")
    for rule in a["candidates"]:
        lifted = tuple(rule[i] for i in erase)
        need(reached(rule, ok, ar) == reached(lifted, nk, zr), "each_rule_preserves_reached_rows")
    old_signatures = {reached(rule, ok, ar) for rule in a["candidates"]}
    lift_signatures = {reached(rule, nk, zr) for rule in lifts}
    new_signatures = {reached(rule, nk, zr) for rule in fine}
    need(old_signatures == lift_signatures and lift_signatures <= new_signatures, "exact_reached_row_lifts")
    scope = "no_selected_rows" if not ar else "selected_completed_histories_only" if front["pending"] or z["unknown_outcomes"] else "complete_selected_family"
    return dict(base, decision="exact_finite_refinement_verified",
                lifted_candidates=[list(v) for v in sorted(lifts)],
                constant_fiber_candidates=[list(v) for v in sorted(constant)],
                additional_candidates=[list(v) for v in sorted(fine - lifts)],
                old_reached_behaviors=[list(v) for v in sorted(old_signatures)],
                new_reached_behaviors=[list(v) for v in sorted(new_signatures)],
                additional_reached_behaviors=[list(v) for v in sorted(new_signatures - lift_signatures)],
                behavior_scope=scope)
