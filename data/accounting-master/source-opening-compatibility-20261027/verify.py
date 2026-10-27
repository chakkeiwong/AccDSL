"""One bounded conformance run over retained complete exchanges.

No accepted writer is imported or run. Existing evidence is read-only.
"""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = ROOT / "data/accounting-master"
sys.path.insert(0, str(ROOT / "scripts"))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def dump(path, value):
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    out = HERE / "attempt-01"
    out.mkdir(exist_ok=False)
    start = time.monotonic()
    checks, cases, lock = [], [], {}

    def check(label, actual, expected=True):
        passed = actual == expected
        checks.append({"label": label, "passed": passed})
        if not passed:
            raise AssertionError(label)

    def protect(path, expected=None):
        path = path.resolve()
        key = str(path.relative_to(ROOT))
        current = digest(path)
        if expected is not None:
            check("inherited identity " + key, current, expected)
        if key in lock:
            check("consistent identity " + key, current, lock[key])
        lock[key] = current

    def record(name, request, result, expected_status):
        check(name + " status", result["status"], expected_status)
        for flag in opening.FLAGS:
            if flag in result:
                check(name + " false flag " + flag, result[flag] is False)
        cases.append({"case": name, "request": request, "result": result})

    try:
        for folder, leaf in [
            ("history-to-opening-20261025", "source-lock.json"),
            ("conditional-continuation-20261025", "source-lock.json"),
            ("company-book-carry-20261025", "source-lock.json"),
            ("debt-reading-network-20261027", "attempt-01/source-lock.json"),
        ]:
            source_lock = BASE / folder / leaf
            protect(source_lock)
            for name, expected in read(source_lock).items():
                protect(ROOT / name, expected)
        for path in [Path(__file__), HERE / "compatibility.md", HERE / "expected.md",
                     ROOT / "docs/plans/accounting-source-opening-compatibility-20261027.md"]:
            protect(path)
        selected_paths = [
            BASE / "history-to-opening-20261025/comparison.json",
            BASE / "conditional-continuation-20261025/comparison.json",
            BASE / "company-book-carry-20261025/comparison.json",
            BASE / "debt-reading-network-20261027/attempt-01/full-result.json",
            BASE / "debt-reading-network-20261027/attempt-01/witnesses.json",
            BASE / "debt-reading-network-20261027/attempt-01/controls.json",
            BASE / "company-return-execution-20261024/trace.json",
        ]
        for path in selected_paths:
            protect(path)
        import conditional_company_opening_v1 as opening
        import conditional_company_continuation_v1 as continuation
        import company_book_carry_v1 as carry
        import z3
        check("CPU-only declaration", os.environ.get("CUDA_VISIBLE_DEVICES"), "-1")
        check("retained solver version", z3.get_version_string(), "4.16.0")

        opening_rows = read(selected_paths[0])["cases"]
        continuation_rows = read(selected_paths[1])["cases"]
        carry_rows = read(selected_paths[2])["cases"]
        check("retained case populations", [len(x) for x in [opening_rows, continuation_rows, carry_rows]], [4, 4, 4])

        for row in opening_rows:
            req = deepcopy(row["request"])
            before = deepcopy(req)
            result = opening.map_opening(req)
            name = "opening:" + row["case"]
            record(name, req, result, "conditional_opening")
            check(name + " complete replay", result, row["result"])
            check(name + " input preserved", req, before)
            book = result["opening"]
            cash = book["cash_account"]
            equity = next(k for k, v in book["accounts"].items() if v["classification"] == "equity")
            check(name + " complete balances", book["balances"], {cash: "15/1", equity: "-15/1"})
            expected_sales = "5/1" if "(10, 2, 3)" in row["case"] else "7/1"
            check(name + " complete memory", book["memory"], {"history": {"sales/a~1": expected_sales}})
            check(name + " event history", book["seen"], ["early", "late"])
            check(name + " empty opening flows", book["flows"], [])
            check(name + " opening date", book["date"], "2025-01-01")
            check(name + " full parent", result["provenance"]["attachment_definition"], req["attachment"])

        for row in continuation_rows:
            req = deepcopy(row["request"])
            before = deepcopy(req)
            result = continuation.run(req)
            name = "continuation:" + row["case"]
            record(name, req, result, "conditional_continuation")
            check(name + " complete replay", result, row["result"])
            check(name + " input preserved", req, before)
            initial = req["opening_result"]["opening"]
            current = result["current"]
            cash = initial["cash_account"]
            equity = next(k for k, v in initial["accounts"].items() if v["classification"] == "equity")
            check(name + " complete balances", current["balances"], {cash: "14/1", equity: "-14/1"})
            check(name + " complete journal", result["transition"]["journal"], {cash: "-1/1", equity: "1/1"})
            check(name + " memory retained", current["memory"], initial["memory"])
            check(name + " full source result", result["opening_result"], req["opening_result"])
            report = result["report"]
            check(name + " income", report["income"], {"income": "0/1", "expenses": "0/1", "profit": "0/1"})
            check(name + " financing", report["cash_flows"]["activities"]["financing"], {"receipts": "0/1", "payments": "1/1", "net": "-1/1"})
            check(name + " reported equity movement", report["equity"]["direct_movements"], "-1/1")
            check(name + " equity closing", report["equity"]["closing"], "14/1")
            check(name + " full reconciliation", set(report["reconciliations"].values()), {"0/1"})

        for row in carry_rows:
            req = deepcopy(row["request"])
            before_req = deepcopy(req)
            result = carry.propose(req)
            name = "carry:" + row["case"]
            record(name, req, result, "proposed")
            check(name + " complete replay", result, row["result"])
            check(name + " input preserved", req, before_req)
            old = req["report_request"]["closing"]
            new = result["next_opening"]
            check(name + " zero cash effect", result["journal"][old["cash_account"]], "0/1")
            check(name + " balanced journal", sum(map(Q, result["journal"].values())), Q(0))
            check(name + " lifetime IDs", new["seen"], old["seen"] + [req["close_id"]])
            check(name + " reset current flows", new["flows"], [])
            if row["case"] != "native_balances":
                expected = "-102/1" if row["case"] == "loss.alpha" else "-130/1"
                change = "3/1" if row["case"] == "loss.alpha" else "-25/1"
                check(name + " independent retained", new["balances"][req["retained_account"]], expected)
                check(name + " independent closing", result["journal"][req["retained_account"]], change)
                check(name + " memory preserved", new["memory"], old["memory"])
                for account, info in old["accounts"].items():
                    value = "0/1" if info["classification"] in ["income", "expense"] else expected if account == req["retained_account"] else old["balances"][account]
                    check(name + " account " + account, new["balances"][account], value)
            else:
                native = read(selected_paths[6])["next_opening"]
                check(name + " complete native balances", new["balances"], native["balances"])
                check(name + " native period", new["period"], native["period"])
                check(name + " imported lots", new["memory"]["lots"], native["lots"])
            report_req = carry.reports.request(new, new, req["report_request"]["schemas"], req["report_request"]["mapping"])
            new_report = carry.reports.report(report_req)
            check(name + " next opening report", new_report["status"], "reported")
            check(name + " next equity continuity", new_report["equity"]["opening"], result["report"]["equity"]["closing"])

        source_result = read(selected_paths[3])
        witnesses = read(selected_paths[4])
        check("source conditional status", source_result["status"], "conditionally_feasible")
        check("source is not opening", source_result["executable_opening"] is None)
        check("source not whole history", source_result["whole_statement_history_complete"] is False)
        parent = source_result["source_parent"]
        retained = parent["preserved_report"]
        check("complete selected source", [len(source_result["definition"][k]) for k in ["observations", "relations"]], [236, 101])
        check("complete retained source", [len(retained[k]) for k in ["observations", "relations", "requirements"]], [256, 143, 15])
        check("original relations retained", source_result["definition"]["relations"], parent["definition"]["relations"])
        obs = source_result["interpretation"]["observation"]
        check("original dash unknown", parent["definition"]["observations"][obs]["interval"] is None)
        check("selected rounded interval", source_result["definition"]["observations"][obs]["interval"],
              {"lower": "-1/2", "upper": "1/2", "lower_inclusive": False, "upper_inclusive": False})
        for key, item in parent["definition"]["observations"].items():
            if key != obs:
                check("unchanged source observation " + key, source_result["definition"]["observations"][key], item)
        independent_path = BASE / "debt-reading-network-20261027/independent_check.py"
        spec = importlib.util.spec_from_file_location("source_opening_independent", independent_path)
        independent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(independent)
        for name in ["primary", "nonzero"]:
            check("independent retained witness " + name,
                  independent.check(source_result["definition"], witnesses[name]),
                  {"complete_values": 236, "checked_intervals": 236, "checked_equations": 101})
        check("nonzero issuance remains possible", witnesses["nonzero"][obs], "1/4")
        controls = {r["name"]: r for r in read(selected_paths[5])}
        for name, expected in [("missing_reading", "unresolved"), ("missing_rounding", "unresolved"),
                               ("zero_budget", "unknown"), ("exact_zero_claim", "invalid")]:
            check("retained source control " + name, controls[name]["status"], expected)

        for variant, status in [
            ("temporal_definition_is_not_history", "invalid"),
            ("missing_premise", "unresolved"), ("missing_memory", "invalid"),
            ("wrong_entity", "invalid"), ("wrong_scale", "invalid"),
            ("target_obligation", "candidate_opening_with_unresolved_obligations"),
            ("unmapped_observation", "candidate_opening_with_unresolved_obligations"),
        ]:
            req = deepcopy(opening_rows[0]["request"])
            if variant == "temporal_definition_is_not_history":
                req["attachment"] = deepcopy(source_result["definition"])
            elif variant == "missing_premise":
                req["attachment"]["history"]["balance_premise"] = None
            elif variant == "missing_memory":
                req["mapping"]["memory"].clear()
            elif variant == "wrong_entity":
                req["mapping"]["context"]["entity"] = "Other"
            elif variant == "wrong_scale":
                req["attachment"]["history"]["value_type"]["scale"] = "1000000/1"
            elif variant == "target_obligation":
                req["attachment"]["obligations"].append({"id": "missing_terms", "meaning": "Actual contract terms not identified", "affects": ["execution"]})
            else:
                req["attachment"]["bindings"].pop("opening")
            before = deepcopy(req)
            result = opening.map_opening(req)
            record("boundary:" + variant, req, result, status)
            check(variant + " input preserved", req, before)
            if status in ["invalid", "unresolved"]:
                check(variant + " no opening", "opening" not in result)
            else:
                check(variant + " obligations retained", bool(result["target_obligations"]))
                body = deepcopy(continuation_rows[0]["request"])
                body["opening_request"], body["opening_result"] = req, result
                current = continuation.run(body)
                record("blocked_continuation:" + variant, body, current, "unresolved")
                check(variant + " no current", "current" not in current)

        for variant in ["stale_result", "stale_state", "missing_equity_movement"]:
            req = deepcopy(continuation_rows[0]["request"])
            if variant == "stale_result":
                req["opening_result"]["opening"]["memory"]["history"]["sales/a~1"] = "0/1"
            elif variant == "stale_state":
                req["transition_request"]["expected_state_sha256"] = "0" * 64
            else:
                req["equity_movements"] = []
            before = deepcopy(req)
            result = continuation.run(req)
            record("boundary:" + variant, req, result, "invalid")
            check(variant + " no current", "current" not in result)
            check(variant + " input preserved", req, before)

        selected_continuation = continuation_rows[0]["result"]
        early_book = selected_continuation["current"]
        equity = next(k for k, v in early_book["accounts"].items() if v["classification"] == "equity")
        early_request = carry.request(selected_continuation["report_request"], "early.close", equity, "2027-01-01",
                                      {k: {"kind": "preserve", "provenance": "Explicit diagnostic policy"} for k in early_book["memory_types"]})
        early = carry.propose(early_request)
        record("boundary:early_carry", early_request, early, "invalid")
        check("early carry exact reason", early["reason"], "last_period_day_required")
        check("early carry no next opening", "next_opening" not in early)
        incomplete = deepcopy(carry_rows[0]["request"])
        incomplete["memory_policies"].pop(next(iter(incomplete["memory_policies"])))
        bad_carry = carry.propose(incomplete)
        record("boundary:missing_carry_policy", incomplete, bad_carry, "invalid")
        check("missing carry policy exact reason", bad_carry["reason"], "complete_memory_policies")
        check("missing carry policy no next opening", "next_opening" not in bad_carry)

        # Verify frozen network/history evidence, without rerunning its writer.
        old_manifest_path = BASE / "retained-network-history-20261025/manifest.json"
        protect(old_manifest_path)
        old_manifest = read(old_manifest_path)
        for name, expected in old_manifest["outputs"].items():
            protect(ROOT / name, expected)
        semantic = read(BASE / "retained-network-history-20261025/semantic-summary.json")
        observed = {r["case"]: r["status"] for r in semantic}
        check("old PDF network unresolved", observed["full-unmapped"], "unresolved")
        check("old mapped opening rejected", observed["opening-mapped"], "supplied_history_incompatible")
        check("old mapped equity rejected", observed["equity-mapped"], "supplied_history_incompatible")

        module_paths = []
        for module in list(sys.modules.values()):
            filename = getattr(module, "__file__", None)
            if filename:
                path = Path(filename).resolve()
                if path.suffix == ".py" and path.is_relative_to(ROOT):
                    protect(path)
                    module_paths.append(str(path.relative_to(ROOT)))
        protect(ROOT / "scripts/retained_network_history_v1.py")
        for name, expected in list(lock.items()):
            check("protected after " + name, digest(ROOT / name), expected)
        dump(out / "cases.json", cases)
        dump(HERE / "dependency-lock.json", lock)
        summary = {"passed": True, "checks": len(checks), "full_replayed_cases": 12,
                   "boundary_cases": len(cases) - 12, "protected_files": len(lock),
                   "candidate": "5.53;not_ready", "no_manuscript_change": True,
                   "claim": "bounded exact-profile compatibility only"}
        dump(out / "checks.json", {**summary, "details": checks})
        dump(out / "run-manifest.json", {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "git_commit": "N/A: unusable .git marker; no repository initialized",
            "command": "CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/source-opening-compatibility-20261027/verify.py",
            "python": sys.version, "executable": sys.executable, "platform": platform.platform(),
            "z3": z3.get_version_string(),
            "cpu_gpu": "CPU-only Python/Z3; GPU intentionally hidden; no GPU framework imported",
            "random_seeds": "N/A: deterministic exact conformance and source checks",
            "wall_seconds": time.monotonic() - start,
            "data_version": digest(HERE / "dependency-lock.json"),
            "plan": "docs/plans/accounting-source-opening-compatibility-20261027.md",
            "result": str((HERE / "result.md").relative_to(ROOT)),
            "artifacts": ["cases.json", "checks.json", "../dependency-lock.json"],
            "observed_local_modules": sorted(set(module_paths)),
            "dependency_limit": "Bounded observed modules and inherited declared files; not proof of universal runtime or distributable-package dependency closure",
        })
        print(json.dumps(summary))
    except Exception as exc:
        dump(out / "failure.json", {"error": str(exc), "checks": checks})
        raise


if __name__ == "__main__":
    main()
