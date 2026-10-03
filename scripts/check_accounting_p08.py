#!/usr/bin/env python3
"""Deterministic P08 checks for the bounded issuer compound-bond slice.

The checker keeps source admission, implementation invariants, independent
present-value/cash-flow arithmetic, matched-fact comparison, and deliverable
shape as separate checks.  It does not infer treatment for unavailable
standards and it does not write supervisor records.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/accounting-master/deliverables/P08"
REGISTER = ROOT / "docs/design/research/p08-v1/authority-register.json"
ENGINE = ROOT / "scripts/corporate_financing_v1.py"
TEST_FILE = ROOT / "tests/test_accounting_p08.py"
REQUIRED_CLAIMS = {
    "recognition", "classification", "split", "measurement", "interest",
    "redemption", "conversion", "note_carrying", "note_interest",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text())


def frac(value) -> Fraction:
    return Fraction(value)


def run_tests() -> dict:
    sys.path.insert(0, str(ROOT / "tests"))
    stream = io.StringIO()
    try:
        module = __import__("test_accounting_p08")
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
        return {
            "module": "test_accounting_p08",
            "methods": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skips": len(result.skipped),
            "passed": bool(result.wasSuccessful() and result.testsRun > 0 and not result.skipped),
            "output_tail": stream.getvalue()[-1200:],
        }
    except Exception as exc:  # pragma: no cover - diagnostic guard
        return {"module": "test_accounting_p08", "methods": 0, "failures": 0,
                "errors": 1, "skips": 0, "passed": False,
                "output_tail": repr(exc)}


def independent_case(contract, settlement, opening_cash, authority):
    """Check outputs against an oracle independent of ``run_case`` internals."""
    from corporate_financing_v1 import run_case

    result = run_case(contract, settlement=settlement, opening_cash=opening_cash,
                      authority=authority)
    principal = frac(contract.principal)
    proceeds = frac(contract.proceeds)
    coupon = frac(contract.annual_coupon)
    rate = frac(contract.comparable_yield)
    pv = sum((coupon / (1 + rate) ** n for n in range(1, contract.years + 1)), Fraction(0))
    pv += principal / (1 + rate) ** contract.years
    interest = coupon * contract.years + principal - pv
    expected_cash = frac(opening_cash) + proceeds - coupon * contract.years
    if settlement == "redeem":
        expected_cash -= principal
    expected = {
        "initial_liability": pv,
        "initial_equity": proceeds - pv,
        "interest_expense": interest,
        "cash": expected_cash,
        "shares": contract.conversion_shares if settlement == "convert" else 0,
        "share_equity": -principal if settlement == "convert" else Fraction(0),
    }
    observed = {
        "initial_liability": frac(result["initial_liability"]),
        "initial_equity": frac(result["notes"]["conversion_equity"]),
        "interest_expense": frac(result["state"]["ledger"]["interest_expense"]),
        "cash": frac(result["state"]["ledger"]["cash"]),
        "shares": result["state"]["shares"],
        "share_equity": frac(result["state"]["ledger"]["share_equity"]),
    }
    if observed != expected:
        raise AssertionError({"settlement": settlement, "expected": expected,
                              "observed": observed})
    journal = result["state"]["journal"]
    if len(journal) != 1 + 2 * contract.years + 1:
        raise AssertionError("unexpected journal length")
    for entry in journal:
        if sum(frac(v) for v in entry["postings_debit_positive"].values()) != 0:
            raise AssertionError("unbalanced journal")
        if sum(frac(v) for v in entry["state_after"].values()) != 0:
            raise AssertionError("unbalanced state")
    for period in result["notes"]["periods"]:
        lhs = (frac(period["opening_liability"]) + frac(period["issue_liability"])
               + frac(period["interest_expense"]) - frac(period["coupons"])
               - frac(period["settlement_liability"]))
        if lhs != frac(period["closing_liability"]):
            raise AssertionError("note roll-forward")
    return {
        "case_id": f"{settlement}-default",
        "settlement": settlement,
        "initial_liability": str(pv),
        "initial_equity": str(proceeds - pv),
        "total_interest": str(interest),
        "ending_cash": str(expected_cash),
        "ending_shares": contract.conversion_shares if settlement == "convert" else 0,
        "journal_entries": len(journal),
        "periods": len(result["notes"]["periods"]),
        "claims": sorted({claim for entry in journal for claim in entry["claims"]}),
    }


def check_deliverable(payload: dict, authority) -> list[str]:
    failures = []
    if payload.get("schema_version") != "accdsl.p08.authority-methods.v1":
        failures.append("authority-methods schema_version")
    if payload.get("authority_register_path") != "docs/design/research/p08-v1/authority-register.json":
        failures.append("authority register path")
    if payload.get("authority_register_sha256") != sha256(REGISTER):
        failures.append("authority register hash")
    if {x.get("id") for x in payload.get("authorities", [])} != set(authority.sources):
        failures.append("authority ids")
    if {x.get("id") for x in payload.get("claims", [])} != set(authority.claims):
        failures.append("claim ids")
    operations = payload.get("operations", [])
    if len(operations) != 1:
        failures.append("one supported operation")
    else:
        op = operations[0]
        for key in ("preconditions", "recognition", "measurement", "state_effects",
                    "posting_templates", "note_links", "excluded_features"):
            if not op.get(key):
                failures.append("operation " + key)
        if op.get("authority_claims", []) == [] or not set(op["authority_claims"]) <= set(authority.claims):
            failures.append("operation authority claims")
    cases = payload.get("cases", [])
    if {c.get("case_id") for c in cases} != {"redeem-default", "convert-default", "second-parameters-redeem"}:
        failures.append("case ids")
    comparison = payload.get("comparisons", {})
    rows = comparison.get("rows", [])
    if len(rows) != 4 or len({r.get("facts_sha256") for r in rows}) != 1:
        failures.append("matched comparison facts")
    if comparison.get("supported_difference") is not None:
        failures.append("unsupported comparison difference")
    for row in rows[1:]:
        if row.get("status") != "unresolved" or row.get("initial_liability") is not None or row.get("claims") != []:
            failures.append("unresolved comparison inheritance")
    queue = payload.get("method_queue", [])
    if {x.get("method") for x in queue} != {"revenue", "tax", "leases", "FX", "complex_groups", "bonds"}:
        failures.append("method queue")
    blocks = payload.get("access_blocks", [])
    if not blocks or not all(x.get("status") in {"unavailable", "uninspected"} for x in blocks):
        failures.append("access blocks")
    return failures


def check_result(path: Path) -> list[str]:
    if not path.exists():
        return ["result.md missing"]
    text = path.read_text()
    required = (
        "# P08 authority and corporate methods result",
        "## Supported operation",
        "## Authority and jurisdiction limits",
        "## Decision table",
        "## Inference status",
        "professional accounting validity",
        "empirical forecast validity",
        "human acceptance",
    )
    return [f"result.md missing text: {x}" for x in required if x not in text]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run deterministic checks")
    parser.add_argument("--output-dir", default=str(OUT))
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("--check is required")
    out = Path(args.output_dir).resolve()
    if out != OUT:
        parser.error("use the declared P08 output directory")
    started = datetime.now(timezone.utc)
    sys.path.insert(0, str(ROOT / "scripts"))
    from corporate_financing_v1 import AuthorityBook, Contract, compare_same_facts

    checks = []
    errors = []
    try:
        authority = AuthorityBook()
        checks.append({"id": "authority", "passed": True,
                       "observed": {"sources": len(authority.sources),
                                    "claims": len(authority.claims)}})
    except Exception as exc:
        authority = None
        errors.append("authority: " + repr(exc))
        checks.append({"id": "authority", "passed": False, "error": repr(exc)})

    tests = run_tests()
    checks.append({"id": "unit_tests", "passed": tests["passed"],
                   "observed": {k: tests[k] for k in ("methods", "failures", "errors", "skips")}})
    case_reports = []
    comparison = {}
    if authority is not None:
        try:
            base = Contract()
            case_reports.append(independent_case(base, "redeem", "20", authority))
            case_reports.append(independent_case(base, "convert", "20", authority))
            from dataclasses import replace
            second = replace(base, principal="240", proceeds="245", instrument_fair_value="245",
                             annual_coupon="12", comparable_yield="2/25", conversion_shares=24)
            report = independent_case(second, "redeem", "30", authority)
            report["case_id"] = "second-parameters-redeem"
            case_reports.append(report)
            checks.append({"id": "independent_oracles", "passed": True,
                           "observed": {"cases": len(case_reports)}})
        except Exception as exc:
            errors.append("independent_oracles: " + repr(exc))
            checks.append({"id": "independent_oracles", "passed": False, "error": repr(exc)})
        try:
            comparison = compare_same_facts(authority=authority)
            rows = comparison["rows"]
            passed = (len(rows) == 4 and len({r["facts_sha256"] for r in rows}) == 1
                      and rows[0]["status"] == "supported_bounded"
                      and all(r["status"] == "unresolved" and r["initial_liability"] is None
                              and r["claims"] == [] for r in rows[1:]))
            checks.append({"id": "matched_comparison", "passed": passed,
                           "observed": {"rows": len(rows), "criterion_status": comparison.get("criterion_status")}})
            if not passed:
                errors.append("matched comparison did not preserve unresolved cells")
        except Exception as exc:
            errors.append("matched_comparison: " + repr(exc))
            checks.append({"id": "matched_comparison", "passed": False, "error": repr(exc)})

    authority_payload = None
    authority_path = out / "authority-and-methods.json"
    if authority_path.exists():
        try:
            authority_payload = load_json(authority_path)
            failures = check_deliverable(authority_payload, authority) if authority else ["authority unavailable"]
            checks.append({"id": "authority_methods_deliverable", "passed": not failures,
                           "observed": {"failures": failures}})
            errors.extend("authority_methods: " + x for x in failures)
        except Exception as exc:
            errors.append("authority_methods: " + repr(exc))
            checks.append({"id": "authority_methods_deliverable", "passed": False, "error": repr(exc)})
    else:
        errors.append("authority_methods: file missing")
        checks.append({"id": "authority_methods_deliverable", "passed": False})
    result_failures = check_result(out / "result.md")
    checks.append({"id": "result_deliverable", "passed": not result_failures,
                   "observed": {"failures": result_failures}})
    errors.extend("result: " + x for x in result_failures)
    code_paths = [ENGINE, TEST_FILE, REGISTER, authority_path, out / "result.md"]
    file_status = {str(p.relative_to(ROOT)): p.exists() for p in code_paths}
    passed = bool(authority is not None and tests["passed"] and case_reports
                  and all(x["passed"] for x in checks) and not errors)
    payload = {
        "schema_version": "accdsl.p08.check.v1",
        "passed": passed,
        "checks": checks,
        "errors": errors,
        "cases": case_reports,
        "comparison": comparison,
        "files": file_status,
        "manifest": {
            "command": "python3 -B scripts/check_accounting_p08.py --check",
            "working_directory": str(ROOT),
            "python": platform.python_version(),
            "hardware": "CPU only; CUDA_VISIBLE_DEVICES=-1; no accelerator framework imported",
            "random_seeds": "N/A: exact deterministic fixtures",
            "started_utc": started.isoformat(),
            "authority_register_sha256": sha256(REGISTER),
            "engine_sha256": sha256(ENGINE),
            "test_sha256": sha256(TEST_FILE),
        },
        "acceptance": {
            "engineering": passed,
            "accounting_validity": "not established",
            "forecast_validity": "not established",
            "human_acceptance": "pending",
            "whole_gap_closure": False,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
