"""Bounded exact renaming comparisons against fresh joint policy evaluation."""
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
spec = importlib.util.spec_from_file_location("own_joint_transport", H / "transport.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def rename(declaration):
    target = cp(declaration)
    maps = target["mapping"]["maps"]
    for stage in ("first", "second"):
        values = sorted({v["token"] for source in maps for v in source[stage]})
        conversion = {v: stage + "-renamed-" + str(len(values) - i) for i, v in enumerate(values)}
        for source in maps:
            for value in source[stage]:
                value["token"] = conversion[value["token"]]
    return target


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
    attempt = sys.argv[1]
    assert attempt in ("01", "02", "03")
    A = H / ("attempt-" + attempt)
    A.mkdir(exist_ok=False)
    start = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
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
        check("CPU_only", os.environ.get("CUDA_VISIBLE_DEVICES") == "-1")
        prior = H.parent / "joint-temporal-frontier-20261027"
        for attempt_dir in (prior / "attempt-02", prior / "attempt-03"):
            check("prior_status:" + attempt_dir.name, json.loads((attempt_dir / "verification.json").read_text())["status"] == "PASS")
            for name, digest in json.loads((attempt_dir / "source-lock.json").read_text()).items():
                check("prior_lock:" + name, sha256((R / name).read_bytes()).hexdigest() == digest)
                pins[name] = digest
            for path in attempt_dir.iterdir():
                if path.is_file():
                    pins[str(path.relative_to(R))] = sha256(path.read_bytes()).hexdigest()
        for path in [H / "transport.py", H / "verify.py", H / "contract.md", R / "docs/plans/accounting-joint-domain-transport-20261027.md"]:
            pins[str(path.relative_to(R))] = sha256(path.read_bytes()).hexdigest()
        save("source-lock.json", pins)
        for name in ("transport.py", "verify.py", "contract.md"):
            (A / name).write_bytes((H / name).read_bytes())
        source = json.loads((H.parent / "joint-stage-policy-20261027/attempt-01/cases.json").read_text())
        refs = {x["case"]: x for x in source}
        sequences = {x["case"]: x["checkpoints"] for x in json.loads((prior / "attempt-02/sequences.json").read_text()) if x["step"] == 1}
        e = m.b.b.Evidence()
        names = ["between:original", "before_both:original", "interval_both:original", "unknown_access:original",
                 "late_retraction:original", "late_conflict:original", "inconsistent:original",
                 "before_both:domain_limit", "between:second_token"]
        retained = None
        for name in names:
            ref = refs[name]
            x, old = ref["input"], ref["declaration"]
            xid, oid = m.identity(x), m.identity(old)
            new = rename(old)
            nid = m.identity(new)
            seq = sequences[name.split(":")[0]]
            first_known = next((i for i, front in enumerate(seq[:-1]) if front["outcomes"]), None)
            indices = sorted({0, len(seq)//2, len(seq)-1} | ({first_known} if first_known is not None else set()))
            rel = m.relation(x, xid, old, oid, new, nid, e)
            if rel["old_to_new_positions"] is not None:
                check(name + ":nonidentity_permutation", rel["old_to_new_positions"] != list(range(len(rel["old_to_new_positions"]))))
                back = m.relation(x, xid, new, nid, old, oid, e)
                check(name + ":inverse_positions", all(back["old_to_new_positions"][v] == i for i, v in enumerate(rel["old_to_new_positions"])))
            for index in indices:
                front = seq[index]
                fid = m.identity(front)
                od = rel["old_domain"]
                old_result = m.f.partial_policy(front, fid, xid, old, oid, od, m.identity(od), e)
                got = m.evaluate(front, fid, xid, old, oid, new, nid, old_result, m.identity(old_result), e)
                check(name + ":frontier_immutable:" + str(index), m.identity(front) == fid)
                check(name + ":conclusion:" + str(index), got["transported"]["status"] == old_result["status"])
                cases.append(dict(case=name, index=index, old_declaration=old, new_declaration=new,
                                  frontier_sha256=fid, old_result_sha256=m.identity(old_result), result=got))
                if name == "between:original" and index == len(seq)-1:
                    retained = (front, x, old, new, old_result, got)
        front, x, old, new, old_result, got = retained
        xid, oid, nid, fid = [m.identity(v) for v in (x, old, new, front)]
        for label, change in [
            ("merge_labels", lambda d: [v.update(token="merged") for s in d["mapping"]["maps"] for v in s["first"]]),
            ("split_shared_label", lambda d: d["mapping"]["maps"][0]["second"][0].update(token="split-one-head")),
            ("changed_budget", lambda d: d["mapping"].update(max_policy_keys=11)),
            ("changed_date", lambda d: d["mapping"].update(second_at="2026-01-04T00:00:00Z")),
            ("changed_raw_key", lambda d: d["mapping"]["maps"][0]["first"][0].update(key=["changed"])),
            ("changed_source_binding", lambda d: d["mapping"]["maps"][0].update(source_sha256="0"*64)),
            ("changed_request", lambda d: d.update(joint_request_sha256="0"*64)),
            ("changed_actions", lambda d: d["mapping"]["actions"].update(first=["draw", "pay"]))]:
            bad = cp(new)
            change(bad)
            reject(label, lambda z=bad: m.relation(x, xid, old, oid, z, m.identity(z), e))
        reject("external_declaration_identity", lambda: m.relation(x, xid, old, oid, new, "0"*64, e))
        reject("external_old_result_identity", lambda: m.evaluate(front, fid, xid, old, oid, new, nid, old_result, "0"*64, e))
        nd = got["relation"]["new_domain"]

        def check_target(value):
            return m.c.verify(value, m.identity(value), front, fid, xid, new, nid, nd, m.identity(nd), e)

        bad = cp(got["transported"])
        bad["candidates"] = cp(old_result["candidates"])
        reject("reuse_unpermuted_population", lambda: check_target(bad))
        bad = cp(got["transported"])
        bad["rejections"][0]["policy"] = cp(bad["candidates"][0])
        reject("rejection_is_survivor", lambda: check_target(bad))
        bad = cp(got["transported"])
        bad["rejections"][0]["row"] = "unrelated"
        reject("changed_refusal_witness", lambda: check_target(bad))
        bad = cp(got["transported"])
        bad["source_supports"].pop()
        reject("drop_source_support", lambda: check_target(bad))
        for key in ("declaration_sha256", "domain_sha256"):
            bad = cp(got["transported"])
            bad[key] = old_result[key]
            reject("reuse_old_binding:" + key, lambda z=bad: check_target(z))
        for path, digest in pins.items():
            check("preserved:" + path, sha256((R / path).read_bytes()).hexdigest() == digest)
        summary = dict(status="PASS", declarations=len(names), comparisons=len(cases), assertions=len(checks),
                       controls=len(controls), protected_files=len(pins),
                       unassessed_comparisons=sum(z["result"]["decision"] == "unresolved_domain_budget" for z in cases),
                       scope="exact finite joint-stage global renaming; no refinement")
    except Exception:
        summary = dict(status="FAIL", error=traceback.format_exc(), assertions=len(checks))
        save("failure.json", summary)
    finally:
        for name, value in [("verification.json", summary), ("checks.json", checks), ("controls.json", controls), ("cases.json", cases)]:
            save(name, value)
        save("run-manifest.json", dict(command="env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 data/accounting-master/joint-domain-transport-20261027/verify.py " + attempt,
             git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=R, text=True).strip(), environment=platform.python_version(),
             cpu_gpu="CPU; GPU intentionally hidden", started_utc=started, wall_seconds=time.monotonic()-start,
             seeds="N/A exact finite comparison", data_version="source-lock.json", plan="docs/plans/accounting-joint-domain-transport-20261027.md",
             result="data/accounting-master/joint-domain-transport-20261027/result.md", artifacts=str(A.relative_to(R))))
        print(json.dumps(summary), flush=True)
    return summary["status"] != "PASS"


if __name__ == "__main__":
    sys.exit(main())
