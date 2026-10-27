"""One-shot deterministic composition evidence in a new attempt directory."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import sys
import time
import compose
import independent_check

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "data/accounting-master"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    out = HERE / "attempt-01"
    out.mkdir(exist_ok=False)
    start = time.monotonic()
    checks, lock = [], {}

    def check(label, condition):
        checks.append({"label": label, "passed": bool(condition)})
        if not condition:
            raise AssertionError(label)

    def protect(path, expected=None):
        value = sha(path)
        if expected is not None:
            check("protected input " + str(path.relative_to(ROOT)), value == expected)
        lock[str(path.relative_to(ROOT))] = value

    def boundary(name, value):
        check(name + " no opening", value["executable_opening"] is None)
        check(name + " actual unknown", value["actual_history"] == "unknown")
        for flag in ["executed", "source_admission", "accounting_admission", "whole_statement_history_complete", "joint_cross_context_history"]:
            check(name + " false " + flag, value[flag] is False)

    try:
        previous_lock = BASE / "debt-reading-network-20261027/attempt-01/source-lock.json"
        protect(previous_lock)
        for name, expected in read(previous_lock).items():
            protect(ROOT / name, expected)
        previous_manifest = BASE / "retained-network-history-20261025/manifest.json"
        protect(previous_manifest)
        manifest = read(previous_manifest)
        for name, expected in manifest["inputs"].items():
            protect(ROOT / name, expected)
        for name, expected in manifest["outputs"].items():
            protect(ROOT / name, expected)
        source_path = BASE / "debt-reading-network-20261027/attempt-01/full-result.json"
        old_path = BASE / "retained-network-history-20261025/exchanges/full-unmapped.json"
        for path in [source_path, old_path, Path(__file__), HERE / "compose.py", HERE / "independent_check.py",
                     HERE / "expected.md", ROOT / "docs/plans/accounting-selected-reading-history-20261027.md"]:
            protect(path)
        source = read(source_path)
        old = read(old_path)
        body = {"profile": compose.PROFILE, "source_parent": source["source_parent"],
                "reading": source["reading"], "rounding": source["rounding_hypothesis"],
                "histories": old["request"]["histories"], "budget": old["budget"]}
        original = deepcopy(body)
        dump(out / "request.json", body)
        result = compose.assess(body)
        dump(out / "result.json", result)
        check("selected candidates", result["status"] == "conditional_candidates_with_unresolved_facts")
        boundary("selected", result)
        check("unchanged request", body == original)
        check("exact original parent", result["selected_source"]["source_parent"] == source["source_parent"])
        check("exact original budget", result["selected_source"]["source_parent"]["budget"]["max_formula_nodes"] == 20000)
        check("exact history budget", result["budget"]["max_formula_nodes"] == 10000)
        check("same selected definition", result["selected_source"]["definition"] == source["definition"])
        check("counts", (result["selected_observations"], result["selected_relations"], result["context_count"]) == (236, 101, 2))
        observation_union, relation_union, independent, obligations = {}, {}, {}, 0
        for context, child in result["attachments"].items():
            check("candidate " + context, child["status"] == "candidate_attachment_with_unresolved_obligations")
            definition = child["definition"]
            check("history preserved " + context, definition["history"] == body["histories"][context]["history"])
            check("bindings preserved " + context, definition["bindings"] == body["histories"][context]["bindings"])
            check("money scale preserved " + context, definition["history"]["value_type"]["scale"] == "1000000/1")
            independent[context] = independent_check.check(definition, child["witness"], child["replay"])
            expected_unmapped = set(definition["measurements"]["observations"]) - set(definition["bindings"])
            check("unmapped obligations " + context, set(child["unmapped_observations"]) == expected_unmapped)
            check("all obligations " + context, len(child["target_obligations"]) == len(expected_unmapped) + 2)
            check("actual history obligation " + context, {r["id"] for r in definition["obligations"]} == {"actual_history:" + context, "whole_source:" + context})
            check("target remains unknown " + context, child["target_existence"] == "unknown")
            obligations += len(child["target_obligations"])
            for name, value in definition["measurements"]["observations"].items():
                check("unique observation " + name, name not in observation_union)
                observation_union[name] = value
            for relation in definition["measurements"]["relations"]:
                check("unique relation " + relation["id"], relation["id"] not in relation_union)
                relation_union[relation["id"]] = relation
        check("every selected observation", observation_union == source["definition"]["observations"])
        check("every selected relation", relation_union == {r["id"]: r for r in source["definition"]["relations"]})
        check("all 180 target obligations", obligations == 180)
        dump(out / "independent-checks.json", independent)

        # Expected controls are declared in expected.md before this run.
        controls = []
        for name, expected in [
            ("missing_reading", "unresolved"), ("missing_rounding", "unresolved"),
            ("changed_parent_budget", "invalid"), ("dropped_equation", "invalid"),
            ("exact_zero_claim", "invalid"), ("missing_context", "invalid"),
            ("changed_context", "invalid"), ("zero_cells", "unknown"),
            ("missing_history_premise", "unresolved"),
            ("incompatible_opening_mapping", "supplied_history_incompatible"),
        ]:
            request = deepcopy(body)
            if name == "missing_reading": request["reading"] = None
            elif name == "missing_rounding": request["rounding"] = None
            elif name == "changed_parent_budget": request["source_parent"]["budget"]["max_formula_nodes"] = 10000
            elif name == "dropped_equation": request["source_parent"]["definition"]["relations"].pop()
            elif name == "exact_zero_claim": request["reading"]["exact_economic_zero"] = True
            elif name == "missing_context": request["histories"].pop(next(iter(request["histories"])))
            elif name == "changed_context": next(iter(request["histories"].values()))["history"]["value_type"]["context"]["basis"] = "Other"
            elif name == "zero_cells": request["budget"]["max_cells"] = 0
            elif name == "missing_history_premise": next(iter(request["histories"].values()))["history"]["balance_premise"] = None
            else:
                request["histories"] = read(BASE / "retained-network-history-20261025/exchanges/opening-mapped.json")["request"]["histories"]
            before = deepcopy(request)
            value = compose.assess(request)
            dump(out / (name + ".json"), {"request": request, "result": value})
            check(name + " status", value["status"] == expected)
            check(name + " immutable", request == before)
            boundary(name, value)
            if name in ["missing_reading", "missing_rounding"]:
                check(name + " no history assessment", value["history_assessment_started"] is False and value["attachments"] == {})
            controls.append({"name": name, "expected": expected, "status": value["status"], "reason": value.get("reason"),
                             "child_statuses": {k: v["status"] for k, v in value.get("attachments", {}).items()}})

        selected_child = next(iter(result["attachments"].values()))
        for category in ["history", "measurement"]:
            changed = deepcopy(selected_child["witness"])
            key = next(k for k in changed if json.loads(k)[0] == category)
            changed[key] = str(independent_check.Q(changed[key]) + 1)
            try:
                independent_check.check(selected_child["definition"], changed, selected_child["replay"])
            except AssertionError:
                check("independent checker rejects " + category, True)
            else:
                raise AssertionError("independent checker missed " + category)

        for module in list(sys.modules.values()):
            filename = getattr(module, "__file__", None)
            if filename:
                path = Path(filename).resolve()
                if path.suffix == ".py" and path.is_relative_to(ROOT): protect(path)
        for name, expected in lock.items():
            check("protected after " + name, sha(ROOT / name) == expected)
        dump(out / "controls.json", controls)
        dump(out / "source-lock.json", lock)
        summary = {"passed": True, "checks": len(checks), "contexts": 2, "observations": 236,
                   "relations": 101, "target_obligations": obligations, "controls": len(controls),
                   "independent_witness_checks": len(independent), "protected_files": len(lock)}
        dump(out / "checks.json", {**summary, "details": checks})
        dump(out / "run-manifest.json", {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "git_commit": "N/A: unusable .git marker; no repository initialized",
            "command": "CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/selected-reading-history-20261027/verify.py",
            "python": sys.version, "executable": sys.executable, "platform": platform.platform(),
            "z3": compose.native.attachment.z3.get_version_string(),
            "cpu_gpu": "CPU-only Python/Z3; GPU intentionally hidden; no GPU framework imported",
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "random_seeds": "N/A: deterministic exact constraints, no ranking",
            "wall_seconds": time.monotonic() - start, "data_version": sha(out / "source-lock.json"),
            "plan": "docs/plans/accounting-selected-reading-history-20261027.md",
            "result": str((HERE / "result.md").relative_to(ROOT)),
            "artifacts": ["request.json", "result.json", "independent-checks.json", "controls.json", "checks.json", "source-lock.json"],
            "dependency_limit": "Observed and declared exact local dependencies; full release packaging remains open"})
        print(json.dumps(summary))
    except Exception as exc:
        dump(out / "failure.json", {"error": str(exc), "checks": checks})
        raise


if __name__ == "__main__":
    main()
