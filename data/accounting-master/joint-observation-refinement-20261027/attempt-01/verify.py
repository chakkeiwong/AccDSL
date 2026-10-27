"""Focused joint refinements against checked fresh coarse/fine policy results."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime, timezone
import importlib.util
import json
import os
import platform
import resource
import subprocess
import sys
import time
import traceback

H = Path(__file__).resolve().parent
R = H.parents[2]
spec = importlib.util.spec_from_file_location("own_joint_refinement", H / "refinement.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def coarse(declaration, stages):
    value = cp(declaration)
    for source in value["mapping"]["maps"]:
        for stage in stages:
            for token in source[stage]:
                token["token"] = "collapsed-" + stage
    return value


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
    attempt = sys.argv[1]
    assert attempt in ("01", "02", "03")
    A = H / ("attempt-" + attempt)
    A.mkdir(exist_ok=False)
    start, started = time.monotonic(), datetime.now(timezone.utc).isoformat()
    checks, controls, cases, pins = [], [], [], {}

    def save(name, value):
        (A / name).write_text(json.dumps(value, indent=2) + chr(10))

    def check(name, condition):
        checks.append(dict(name=name, passed=bool(condition)))
        if not condition:
            raise AssertionError(name)

    def reject(name, fn):
        try:
            fn()
        except (ValueError, KeyError, TypeError, AssertionError) as error:
            controls.append(dict(name=name, reason=str(error)))
            check("reject:" + name, True)
        else:
            check("reject:" + name, False)

    try:
        check("cpu_hidden", os.environ.get("CUDA_VISIBLE_DEVICES") == "-1")
        baseline = H.parent / "joint-domain-transport-20261027/attempt-01"
        check("accepted_renaming", json.loads((baseline / "verification.json").read_text())["status"] == "PASS")
        for name, digest in json.loads((baseline / "source-lock.json").read_text()).items():
            check("baseline_lock:" + name, sha256((R / name).read_bytes()).hexdigest() == digest)
            pins[name] = digest
        for path in baseline.iterdir():
            if path.is_file():
                pins[str(path.relative_to(R))] = sha256(path.read_bytes()).hexdigest()
        for path in [H / "refinement.py", H / "verify.py", H / "contract.md", R / "docs/plans/accounting-joint-observation-refinement-20261027.md"]:
            pins[str(path.relative_to(R))] = sha256(path.read_bytes()).hexdigest()
        save("source-lock.json", pins)
        for name in ("refinement.py", "verify.py", "contract.md"):
            (A / name).write_bytes((H / name).read_bytes())
        refs = {v["case"]: v for v in json.loads((H.parent / "joint-stage-policy-20261027/attempt-01/cases.json").read_text())}
        seqs = {v["case"]: v["checkpoints"] for v in json.loads((H.parent / "joint-temporal-frontier-20261027/attempt-02/sequences.json").read_text()) if v["step"] == 1}
        evidence = m.b.b.Evidence()
        specifications = [("between:original", "first", ("first",)), ("between:original", "second", ("second",)),
                          ("between:original", "both", ("first", "second"))]
        specifications += [(name, "both", ("first", "second")) for name in
                           ("before_both:original", "interval_both:original", "unknown_access:original", "late_retraction:original",
                            "late_conflict:original", "inconsistent:original", "before_both:domain_limit", "between:second_token")]
        specifications += [("between:original", "renaming", ())]
        plans = []
        for name, mode, stages in specifications:
            ref = refs[name]
            new = cp(ref["declaration"])
            old = coarse(new, stages)
            if mode == "renaming":
                for source in new["mapping"]["maps"]:
                    for stage in ("first", "second"):
                        for token in source[stage]:
                            token["token"] = "renamed:" + token["token"]
            seq = seqs[name.split(":")[0]]
            known = next((i for i, front in enumerate(seq[:-1]) if front["outcomes"]), None)
            indices = sorted({0, len(seq)//2, len(seq)-1} | ({known} if known is not None else set()))
            plans.append(dict(case=name + ":" + mode, source_case=name, old=old, new=new, indices=indices,
                              frontier_ids=[m.identity(seq[i]) for i in indices]))
        save("declarations-before-comparison.json", plans)
        for plan in plans:
            seq = seqs[plan["source_case"].split(":")[0]]
            old, new = plan["old"], plan["new"]
            for index in plan["indices"]:
                front = seq[index]
                prior_id = m.identity([front, old, new])
                got = m.evaluate(front, m.identity(front), front["input_sha256"], old, m.identity(old), new, m.identity(new), evidence)
                label = plan["case"] + ":" + str(index)
                check(label + ":pure", m.identity([front, old, new]) == prior_id)
                check(label + ":no_actual_access", got["actual_information_claim"] is False)
                if got["decision"] == "unassessed_policy_relation":
                    check(label + ":no_lifts", got["lifted_candidates"] is None and got["old_reached_behaviors"] is None)
                else:
                    check(label + ":constant_fibers", got["lifted_candidates"] == got["constant_fiber_candidates"])
                    if plan["case"].endswith(":renaming"):
                        check(label + ":same_reached_rows", got["additional_candidates"] == [] and got["additional_reached_behaviors"] == [])
                if front["status"] == "inconsistent_clocks":
                    check(label + ":inconsistent_unassessed", got["old_result"]["candidates"] is None and got["new_result"]["candidates"] is None)
                if front["complete"] and plan["source_case"] in ("late_retraction:original", "late_conflict:original"):
                    check(label + ":unresolved_sources", got["old_result"]["status"] == got["new_result"]["status"] == "unresolved_source_family")
                    check(label + ":no_selected_behaviors", got["behavior_scope"] == "no_selected_rows" and got["additional_reached_behaviors"] == [])
                cases.append(dict(case=plan["case"], index=index, complete=front["complete"], result=got))
        strict = next(v for v in cases if v["case"] == "between:original:first" and v["complete"])
        check("first_refinement_coarse_rejected", strict["result"]["old_result"]["candidates"] == [])
        check("first_refinement_fine_viable", bool(strict["result"]["new_result"]["candidates"]))
        check("first_refinement_distinct_reached_rows", bool(strict["result"]["additional_reached_behaviors"]))
        plan = plans[0]
        front = seqs["between"][-1]
        x, xid = front["input"], front["input_sha256"]
        old, new = plan["old"], plan["new"]
        reject("reverse_refinement", lambda: m.relation(x, xid, new, m.identity(new), old, m.identity(old), evidence))
        for name, change in [
            ("actor", lambda d: d["mapping"].update(actor="Bob")),
            ("time", lambda d: d["mapping"].update(second_at="2026-01-04T00:00:00Z")),
            ("actions", lambda d: d["mapping"]["actions"].update(first=["draw", "pay"])),
            ("budget", lambda d: d["mapping"].update(max_policy_keys=11)),
            ("source", lambda d: d["mapping"]["maps"][0].update(source_sha256="0"*64)),
            ("request", lambda d: d.update(joint_request_sha256="0"*64)),
            ("raw_key", lambda d: d["mapping"]["maps"][0]["first"].pop())]:
            bad = cp(new)
            change(bad)
            reject(name, lambda z=bad: m.relation(x, xid, old, m.identity(old), z, m.identity(z), evidence))
        merged = coarse(new, ("first",))
        reject("merge_wrong_direction", lambda: m.relation(x, xid, new, m.identity(new), merged, m.identity(merged), evidence))
        reject("stale_declaration", lambda: m.relation(x, xid, old, m.identity(old), new, "0"*64, evidence))
        for name, base, change in [
            ("drop_pending", seqs["between"][0], lambda q: q["pending"].pop()),
            ("false_complete", seqs["between"][0], lambda q: q.update(complete=True)),
            ("drop_support", front, lambda q: q["supports"].pop())]:
            bad = cp(base)
            change(bad)
            reject(name, lambda z=bad: m.evaluate(z, m.identity(z), xid, old, m.identity(old), new, m.identity(new), evidence))
        reject("stale_frontier", lambda: m.evaluate(front, "0"*64, xid, old, m.identity(old), new, m.identity(new), evidence))
        for path, digest in pins.items():
            check("preserved:" + path, sha256((R / path).read_bytes()).hexdigest() == digest)
        summary = dict(status="PASS", declarations=len(plans), comparisons=len(cases), assertions=len(checks), controls=len(controls),
                       protected_files=len(pins), unassessed=sum(v["result"]["decision"] == "unassessed_policy_relation" for v in cases),
                       scope="exact joint-stage erasure, per-rule lifts and selected reached rows; finite conditional design")
    except Exception:
        summary = dict(status="FAIL", error=traceback.format_exc(), assertions=len(checks))
        save("failure.json", summary)
    finally:
        for name, value in [("verification.json", summary), ("checks.json", checks), ("controls.json", controls), ("cases.json", cases)]:
            save(name, value)
        save("run-manifest.json", dict(command="env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 data/accounting-master/joint-observation-refinement-20261027/verify.py " + attempt,
             git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=R, text=True).strip(), environment=platform.python_version(),
             cpu_gpu="CPU; GPU intentionally hidden", started_utc=started, wall_seconds=time.monotonic()-start, seeds="N/A exact finite comparisons",
             data_version="source-lock.json", plan="docs/plans/accounting-joint-observation-refinement-20261027.md",
             result="data/accounting-master/joint-observation-refinement-20261027/result.md", artifacts=str(A.relative_to(R))))
        print(json.dumps(summary), flush=True)
    return summary["status"] != "PASS"


if __name__ == "__main__":
    sys.exit(main())
