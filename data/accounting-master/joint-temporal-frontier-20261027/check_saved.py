"""Finish the third bounded attempt using preserved successful checkpoints."""
from pathlib import Path
from copy import deepcopy
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
spec = importlib.util.spec_from_file_location("own_joint_policy_checker", H / "policy_checker.py")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
f = c.f


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
    out = H / "attempt-03"
    out.mkdir(exist_ok=False)
    start = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    checks, controls, cases, pins = [], [], [], {}

    def save(name, value):
        (out / name).write_text(json.dumps(value, indent=2) + "\n")

    def check(name, condition):
        checks.append(dict(name=name, passed=bool(condition)))
        if not condition:
            raise AssertionError(name)

    def pin(path):
        pins[str(path.relative_to(R))] = sha256(path.read_bytes()).hexdigest()

    try:
        check("cpu_hidden", os.environ.get("CUDA_VISIBLE_DEVICES") == "-1")
        old = H / "attempt-02"
        for name, digest in json.loads((old / "source-lock.json").read_text()).items():
            check("protected:" + name, sha256((R / name).read_bytes()).hexdigest() == digest)
            pins[name] = digest
        for path in old.iterdir():
            if path.is_file():
                pin(path)
        for name in ["policy_checker.py", "check_saved.py", "recovery-audit.md"]:
            pin(H / name)
            (out / name).write_bytes((H / name).read_bytes())
        save("source-lock.json", pins)
        saved = json.loads((old / "policy-checks.json").read_text())
        sequences = {v["case"]: v["checkpoints"] for v in
                     json.loads((old / "sequences.json").read_text()) if v["step"] == 1}
        refs = {v["case"]: v for v in json.loads((H.parent /
                "joint-stage-policy-20261027/attempt-01/cases.json").read_text())}
        e = f.b.b.Evidence()
        records = {}

        def audit(result, front, ref, result_id=None, frontier_id=None,
                  input_id=None, declaration_id=None, domain_id=None):
            return c.verify(result, f.identity(result) if result_id is None else result_id,
                            front, f.identity(front) if frontier_id is None else frontier_id,
                            f.identity(ref["input"]) if input_id is None else input_id,
                            ref["declaration"], f.identity(ref["declaration"]) if declaration_id is None else declaration_id,
                            ref["domain"], f.identity(ref["domain"]) if domain_id is None else domain_id, e)

        for value in saved:
            name = value["case"]
            ref = refs[name]
            seq = sequences[name.split(":")[0]]
            final = value["final"]
            check(name + ":saved_final", audit(final, seq[-1], ref))
            records[(name, "final")] = (final, seq[-1], ref)
            indices = {0, len(seq) // 2}
            first_known = next((i for i, front in enumerate(seq[:-1]) if front["outcomes"]), None)
            if first_known is not None:
                indices.add(first_known)
            for index in sorted(indices):
                front = seq[index]
                result = f.partial_policy(front, f.identity(front), f.identity(ref["input"]),
                                          ref["declaration"], f.identity(ref["declaration"]),
                                          ref["domain"], f.identity(ref["domain"]), e)
                check(name + ":prefix:" + str(index), audit(result, front, ref))
                cases.append(dict(case=name, index=index, result=result))
                records[(name, str(index))] = (result, front, ref)

        def reject(name, record, mutate=None, overrides=None):
            result, front, ref = deepcopy(record)
            if mutate is not None:
                mutate(result, front, ref)
            try:
                audit(result, front, ref, **(overrides or {}))
            except (ValueError, KeyError, TypeError, AssertionError) as error:
                controls.append(dict(name=name, reason=str(error)))
                check("reject:" + name, True)
            else:
                check("reject:" + name, False)

        feasible = records[("between:original", "final")]
        pending = records[("between:original", "0")]
        unknown = records[("late_conflict:original", "final")]
        infeasible = records[("before_both:original", "final")]
        budget = records[("before_both:domain_limit", "final")]
        inconsistent = records[("inconsistent:original", "final")]
        rows = f.b.rows(feasible[2]["input"], feasible[2]["declaration"], e,
                       tuple(feasible[0]["known_row_ids"][0].split("/")[:3]))
        good_row = next(row["id"] for row in rows if row["status"] not in ("refused1", "refused2"))
        reject("wrong_refusal_witness", feasible,
               lambda r, *_: r["rejections"][0].update(row=good_row))
        reject("missing_refusal_row", feasible,
               lambda r, *_: r["rejections"][0].update(row="not-a-known-row"))
        reject("drop_rejected_assignment", feasible, lambda r, *_: r["rejections"].pop())
        reject("duplicate_rejection", feasible,
               lambda r, *_: r["rejections"].append(deepcopy(r["rejections"][0])))
        reject("drop_candidate", feasible, lambda r, *_: r["candidates"].pop())
        reject("duplicate_candidate", feasible,
               lambda r, *_: r["candidates"].append(deepcopy(r["candidates"][0])))
        reject("boolean_assignment", feasible, lambda r, *_: r["candidates"][0].__setitem__(0, False))
        reject("false_feasible_pending", pending, lambda r, *_: r.update(status="conditionally_feasible"))
        reject("false_feasible_unknown", unknown, lambda r, *_: r.update(status="conditionally_feasible"))
        reject("false_feasible_infeasible", infeasible, lambda r, *_: r.update(status="conditionally_feasible"))
        reject("false_feasible_inconsistent", inconsistent, lambda r, *_: r.update(status="conditionally_feasible"))
        reject("false_feasible_domain_budget", budget, lambda r, *_: r.update(status="conditionally_feasible"))
        reject("false_complete", pending, lambda r, *_: r.update(complete=True))
        reject("drop_pending", pending, lambda r, *_: r["pending"].pop())
        reject("drop_pending_domain", pending, lambda r, *_: r["pending_domains"].pop())
        reject("drop_unknown", unknown, lambda r, *_: r["unknown_outcomes"].pop())
        reject("drop_support", feasible, lambda r, *_: r["source_supports"].pop())
        reject("drop_known_row", feasible, lambda r, *_: r["known_row_ids"].pop())
        reject("invent_budget_population", budget, lambda r, *_: r.update(candidates=[], rejections=[]))
        for flag in f.b.b.FLAGS:
            reject("admission:" + flag, feasible, lambda r, *_, k=flag: r.update({k: True}))
        for key in ("result_id", "frontier_id", "input_id", "declaration_id", "domain_id"):
            reject("external:" + key, feasible, overrides={key: "0" * 64})
        for key in ("frontier_sha256", "input_sha256", "declaration_sha256", "domain_sha256"):
            reject("embedded:" + key, feasible, lambda r, *_, k=key: r.update({k: "0" * 64}))
        for name, digest in pins.items():
            check("preserved:" + name, sha256((R / name).read_bytes()).hexdigest() == digest)
        summary = dict(status="PASS", saved_finals=len(saved), checked_prefixes=len(cases),
                       controls=len(controls), assertions=len(checks), protected_files=len(pins),
                       scope="saved-result populations, refusal witnesses, conclusion and evidence retention")
    except Exception:
        summary = dict(status="FAIL", error=traceback.format_exc(), assertions=len(checks))
        save("failure.json", summary)
    finally:
        for name, value in [("verification.json", summary), ("checks.json", checks),
                            ("controls.json", controls), ("prefix-results.json", cases)]:
            save(name, value)
        save("run-manifest.json", dict(command="env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 data/accounting-master/joint-temporal-frontier-20261027/check_saved.py",
             git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=R, text=True).strip(),
             environment=platform.python_version(), cpu_gpu="CPU; GPU intentionally hidden",
             started_utc=started, wall_seconds=time.monotonic()-start, seeds="N/A exact finite checks",
             data_version="source-lock.json", plan="docs/plans/accounting-joint-temporal-frontier-20261027.md",
             result="data/accounting-master/joint-temporal-frontier-20261027/result.md", artifacts=str(out.relative_to(R))))
        print(json.dumps(summary), flush=True)
    return summary["status"] != "PASS"


if __name__ == "__main__":
    sys.exit(main())
