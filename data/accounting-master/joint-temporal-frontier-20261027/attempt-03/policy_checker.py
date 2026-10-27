"""Check saved joint-policy populations and refusal witnesses independently."""
from pathlib import Path
from fractions import Fraction
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("checked_joint_frontier", HERE / "frontier.py")
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


def verify(result, result_id, front, frontier_id, input_id,
           declaration, declaration_id, domain, domain_id, evidence, limit=4096):
    need, identity, fields = f.need, f.identity, f.t.fields
    need(identity(result) == result_id, "external_policy_result")
    frontier_audit = f.verify(front, frontier_id, input_id, limit)
    derived = f.b.derive(front["input"], input_id, declaration, declaration_id, evidence)
    need(identity(domain) == domain_id == identity(derived), "checked_fixed_domain")
    fields(result, ["profile", *f.b.b.FLAGS, "frontier_sha256", "input_sha256",
                   "declaration_sha256", "domain_sha256", "status", "candidates",
                   "rejections", "unknown_outcomes", "source_supports", "pending",
                   "pending_domains", "complete", "known_row_ids"], "policy_fields")
    need(result["profile"] == "PartialJointStagePolicy/1", "policy_profile")
    need(all(result[k] is False for k in f.b.b.FLAGS), "policy_nonadmission")
    for key, expected in [("frontier_sha256", frontier_id), ("input_sha256", input_id),
                          ("declaration_sha256", declaration_id), ("domain_sha256", domain_id)]:
        need(result[key] == expected, "binding_" + key)

    rows, unknown = [], []
    for pair in front["outcomes"]:
        if any(o["status"] != "selected_conditional" for o in pair):
            unknown.append(pair)
            continue
        need(pair[0]["heads"]["financial_family"] == pair[1]["heads"]["financial_family"],
             "fixed_financial_family")
        heads = (pair[0]["heads"]["financial_family"],
                 pair[0]["heads"]["observation_scheme"], pair[1]["heads"]["observation_scheme"])
        rows.extend(f.b.rows(front["input"], declaration, evidence, heads))

    if domain["keys"] is None or front["status"] == "inconsistent_clocks":
        need(result["candidates"] is None and result["rejections"] is None,
             "unassessed_population")
        status = "unresolved_domain_budget" if domain["keys"] is None else "inconsistent_clocks"
    else:
        keys = [f.t.prior.tuples(k) for k in domain["keys"]]
        need(set(f.b.d.keys(rows)) <= set(keys), "known_key_coverage")
        expected = f.b.p.oracle(rows, keys)
        candidates = result["candidates"]
        need(type(candidates) is list, "candidate_list")

        def assignment(policy):
            need(type(policy) is list and len(policy) == len(keys)
                 and all(type(v) is int and v in (0, 1) for v in policy), "total_assignment")
            return tuple(policy)

        actual = [assignment(p) for p in candidates]
        need(actual == sorted(expected), "exact_candidate_population")
        rejected = result["rejections"]
        need(type(rejected) is list, "rejection_list")
        by_id = {row["id"]: row for row in rows}
        need(len(by_id) == len(rows), "unique_known_rows")
        seen = set()
        for item in rejected:
            fields(item, ["policy", "row"], "rejection_fields")
            policy = assignment(item["policy"])
            need(policy not in seen and policy not in expected, "unique_rejected_assignment")
            need(item["row"] in by_id, "known_refusal_row")
            row = by_id[item["row"]]
            first, second = f.b.b.policy.keys(row, "never")
            actions = dict(zip(keys, policy))
            need(actions[("first", first)] == int(row["a1"] == "draw"), "first_action_witness")
            need(row["status"] == "refused1" or
                 row["status"] == "refused2" and
                 actions[("second", second)] == int(row["a2"] == "draw"), "refusal_witness")
            seen.add(policy)
        need(len(seen) + len(expected) == 2 ** len(keys), "complete_policy_universe")
        status = ("unresolved_source_family" if unknown else "conditionally_infeasible"
                  if not expected else "unresolved_pending" if front["pending"]
                  else "conditionally_feasible")

    for key, expected in [("status", status), ("unknown_outcomes", unknown),
                          ("source_supports", front["supports"]), ("pending", front["pending"]),
                          ("pending_domains", frontier_audit["pending_domains"]),
                          ("complete", front["complete"]), ("known_row_ids", [r["id"] for r in rows])]:
        need(identity(result[key]) == identity(expected), "checked_" + key)
    return True
