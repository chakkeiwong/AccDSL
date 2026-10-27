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
import os
from pathlib import Path
import platform
import sys
from time import perf_counter
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/accounting-master/deliverables/P08"
REGISTER = ROOT / "docs/design/research/p08-v1/authority-register.json"
ENGINE = ROOT / "scripts/corporate_financing_v1.py"
TEST_FILE = ROOT / "tests/test_accounting_p08.py"
REQUIRED_CLAIMS = {
    "recognition", "fair_value", "classification", "split", "residual_equity",
    "measurement", "amortised_cost", "interest",
    "redemption", "conversion", "note_carrying", "note_interest",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text())


def frac(value) -> Fraction:
    return Fraction(value)


def check_manifest_pins(hashes, required_paths):
    """Validate the manifest itself, separately from authority admission.

    A valid source register cannot justify a conflicting or incomplete copy of
    its input hashes in the result manifest. Additional recorded inputs must
    also resolve to current repository files.
    """
    if not isinstance(hashes, dict):
        return ['source_hashes must be an object']
    failures = []
    missing = set(required_paths) - set(hashes)
    failures.extend('missing manifest input pin: ' + path for path in sorted(missing))
    for name, expected in hashes.items():
        try:
            relative = Path(name)
            path = ROOT / relative
            if (relative.is_absolute() or '..' in relative.parts
                    or relative.as_posix() != name
                    or not path.resolve().is_relative_to(ROOT.resolve())
                    or path.is_symlink()):
                failures.append('unsafe manifest input path: ' + name)
                continue
            if not path.is_file():
                failures.append('missing manifest input file: ' + name)
            elif expected != sha256(path):
                failures.append('stale manifest input hash: ' + name)
        except (TypeError, ValueError, OSError) as exc:
            failures.append('invalid manifest input: ' + str(name) + ': ' + str(exc))
    return failures


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
    carrying = pv
    for index, period in enumerate(result["notes"]["periods"]):
        expected_interest = carrying * rate
        accrued = journal[1 + 2 * index]
        paid = journal[2 + 2 * index]
        if (frac(accrued['postings_debit_positive']['interest_expense']) != expected_interest
                or frac(paid['postings_debit_positive']['cash']) != -coupon
                or frac(period['interest_expense']) != expected_interest
                or frac(period['coupons']) != coupon):
            raise AssertionError('independent annual interest/coupon oracle')
        carrying += expected_interest - coupon
        if index < contract.years - 1 and frac(period['closing_liability']) != carrying:
            raise AssertionError('independent annual carrying amount')
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


def check_comparison(comparison, authority):
    from corporate_financing_v1 import (comparison_cases, economics_hash, REQUIRED)
    failures = []
    economic = comparison.get('economic_facts', {})
    digest = economics_hash(economic)
    rows = comparison.get('rows', [])
    if len(rows) != 4 or {r.get('standard') for r in rows} != {'AASB', 'US GAAP', 'ASBE', 'EU-endorsed IFRS'}:
        failures.append('comparison regime coverage')
    supported = []
    for row in rows:
        label = row.get('standard', '?')
        if row.get('facts_sha256') != digest:
            failures.append(label + ': economic facts hash')
        if row.get('status') == 'unresolved':
            if (any(row.get(k) is not None for k in ('initial_liability', 'initial_equity', 'total_interest', 'cases'))
                    or row.get('claims') != [] or not row.get('missing')):
                failures.append(label + ': unresolved treatment contains results or lacks dependency')
        elif row.get('status') == 'supported_bounded':
            try:
                expected = comparison_cases(label, economic, authority)
                case = expected['redeem']
                if (row.get('cases') != expected or row.get('initial_liability') != case['initial_liability']
                        or row.get('initial_equity') != case['notes']['conversion_equity']
                        or row.get('total_interest') != case['state']['ledger']['interest_expense']
                        or set(row.get('claims', [])) != set(REQUIRED)
                        or row.get('jurisdiction') != case['contract']['jurisdiction']):
                    failures.append(label + ': supported treatment replay')
                else:
                    supported.append(label)
            except (ValueError, TypeError, KeyError) as exc:
                failures.append(label + ': unsupported treatment: ' + str(exc))
        else:
            failures.append(label + ': invalid treatment status')
    complete = len(supported) >= 2 and not failures
    if complete:
        if comparison.get('criterion_status') != 'complete_bounded' or not comparison.get('supported_difference'):
            failures.append('supported comparison lacks anchored interpretation')
    elif (not comparison.get('criterion_status', '').startswith('incomplete:')
          or comparison.get('supported_difference') is not None):
        failures.append('unsupported cross-standard acceptance')
    return failures


def check_deliverable(payload: dict, authority) -> list[str]:
    from corporate_financing_v1 import Contract, run_case, comparison_economics, EVENT_CLAIMS, wire
    failures = []
    try:
        authority.validate()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return ['invalid authority: ' + str(exc)]
    if payload.get('schema_version') != 'accdsl.p08.authority-methods.v1':
        failures.append('authority-methods schema_version')
    if payload.get('authority_register_path') != str(REGISTER.relative_to(ROOT)):
        failures.append('authority register path')
    if payload.get('authority_register_sha256') != sha256(REGISTER):
        failures.append('authority register hash')
    for key in ('authorities', 'claims', 'research', 'method_queue'):
        if payload.get(key) != authority.records[key]:
            failures.append('full embedded ' + key + ' differ from register')
    historical_access = load_json(ROOT / 'docs/design/research/p08-v1/access-records.json')
    historical_access += [load_json(ROOT / 'docs/design/research/p08-v1/eu-access.json')]
    if payload.get('source_access') != historical_access:
        failures.append('historical access evidence differs from retained records')
    preparation_path = ROOT / 'docs/design/research/p08-v2/source-inspection.json'
    preparation = load_json(preparation_path)
    if payload.get('authority_preparation') != preparation:
        failures.append('authority preparation differs from source inspection')
    if payload.get('authority_preparation_sha256') != sha256(preparation_path):
        failures.append('authority preparation hash')
    access_ref = preparation['source_access']
    access_path = ROOT / access_ref['path']
    if sha256(access_path) != access_ref['sha256']:
        failures.append('supplementary access record hash')
    if payload.get('source_access_recovery') != load_json(access_path):
        failures.append('supplementary access evidence differs from retained records')
    for research in authority.records['research']:
        if sha256(ROOT / research['source']) != research['sha256']:
            failures.append('deferred research source hash')
    source = preparation['source']
    for key in ('retained', 'text'):
        if sha256(ROOT / source[key]['path']) != source[key]['sha256']:
            failures.append('supplementary primary source hash')
    pages = (ROOT / source['text']['path']).read_text().split('\f')
    for anchor in preparation['anchors']:
        if ' '.join(anchor['quote'].split()) not in ' '.join(pages[anchor['pdf_page']-1].split()):
            failures.append('supplementary source anchor')
    from corporate_authority_eu_v1 import EUAuthorityPreparation, REGISTER as EU_REGISTER
    try:
        eu = EUAuthorityPreparation()
        if payload.get('eu_authority_preparation') != eu.records:
            failures.append('EU preparation differs from retained source inspection')
        if payload.get('eu_authority_preparation_sha256') != sha256(ROOT / EU_REGISTER):
            failures.append('EU preparation hash')
    except (ValueError, KeyError, TypeError, OSError) as exc:
        failures.append('invalid EU preparation: ' + str(exc))
        eu = None
    required_inputs = {
        str(path.relative_to(ROOT)) for path in
        (ENGINE, Path(__file__), TEST_FILE, REGISTER, preparation_path, access_path)
    }
    required_inputs.update({'scripts/corporate_authority_eu_v1.py', EU_REGISTER})
    from corporate_authority_eu_recovery_v1 import validate_recovery, REGISTER as RECOVERY_REGISTER
    try:
        recovery = validate_recovery(ROOT)
        if payload.get('eu_source_recovery') != recovery:
            failures.append('EU source recovery differs from retained inspection')
        if payload.get('eu_source_recovery_sha256') != sha256(ROOT / RECOVERY_REGISTER):
            failures.append('EU source recovery hash')
        required_inputs.update(pin['path'] for pin in recovery['source_pins'])
    except (ValueError, OSError, KeyError, TypeError) as exc:
        failures.append('invalid EU source recovery: ' + str(exc))
    required_inputs.update({RECOVERY_REGISTER, 'scripts/corporate_authority_eu_recovery_v1.py'})
    from corporate_authority_eu_current import validate_disposition, REGISTER as DISPOSITION_REGISTER
    try:
        disposition = validate_disposition(ROOT)
        if payload.get('eu_source_disposition') != disposition:
            failures.append('EU source disposition differs from validated preparation')
        if payload.get('eu_source_disposition_sha256') != sha256(ROOT / DISPOSITION_REGISTER):
            failures.append('EU source disposition hash')
        required_inputs.update(pin['path'] for pin in disposition['source_pins'])
    except (ValueError, OSError, KeyError, TypeError) as exc:
        failures.append('invalid EU source disposition: ' + str(exc))
    required_inputs.update({DISPOSITION_REGISTER, 'scripts/corporate_authority_eu_current.py'})
    from corporate_authority_eu_applicability_v1 import validate_applicability, REGISTER as APPLICABILITY_REGISTER
    try:
        applicability = validate_applicability(ROOT)
        if payload.get('eu_applicability_disposition') != applicability:
            failures.append('EU applicability differs from bounded record')
        if payload.get('eu_applicability_disposition_sha256') != sha256(ROOT / APPLICABILITY_REGISTER):
            failures.append('EU applicability hash')
    except (ValueError, OSError, KeyError, TypeError) as exc:
        failures.append('invalid EU applicability: ' + str(exc))
    required_inputs.update({APPLICABILITY_REGISTER, 'scripts/corporate_authority_eu_applicability_v1.py'})
    if eu is not None:
        required_inputs.update(pin['path'] for pin in eu.records['source_pins'])
    required_inputs.update({
        'docs/design/research/p08-v1/access-records.json',
        'docs/design/research/p08-v1/eu-access.json',
    })
    for registered_source in authority.sources.values():
        if registered_source['access_status'] == 'inspected_primary':
            required_inputs.update(registered_source[key]['path'] for key in ('retained', 'text'))
    required_inputs.update(source[key]['path'] for key in ('retained', 'text'))
    required_inputs.update(research['source'] for research in authority.records['research'])
    required_inputs.update(record['path'] for record in historical_access + load_json(access_path)
                           if record.get('path'))
    failures.extend(check_manifest_pins(payload.get('manifest', {}).get('source_hashes'), required_inputs))
    operations = payload.get('operations', [])
    if len(operations) != 1:
        failures.append('one supported operation')
    else:
        op = operations[0]
        for key in ('preconditions', 'recognition', 'measurement', 'state_effects', 'posting_templates', 'excluded_features'):
            if not op.get(key): failures.append('operation ' + key)
        if set(op.get('authority_claims', [])) != REQUIRED_CLAIMS:
            failures.append('operation lifecycle authority')
        if op.get('note_links') != authority.records['note_links']:
            failures.append('operation note links')
        if set(op.get('recognition', {}).get('authority_claims', [])) != set(EVENT_CLAIMS['issue']):
            failures.append('issuance authority dependencies')
        if op.get('event_authority_claims') != wire(EVENT_CLAIMS):
            failures.append('event authority dependencies')
        if set(op.get('measurement', {}).get('authority_claims', [])) != {'fair_value', 'measurement', 'interest', 'amortised_cost'}:
            failures.append('measurement authority dependencies')
    cases = payload.get('cases', [])
    if len(cases) != 3 or {c.get('case_id') for c in cases} != {'redeem-default', 'convert-default', 'second-parameters-redeem'}:
        failures.append('case ids')
    for case in cases:
        label = case.get('case_id', '?')
        try:
            contract = Contract(**case['facts'])
            result = run_case(contract, case['settlement'], case['opening_cash'], authority)
            state = dict(result['state']); journal = state.pop('journal')
            expected = {'facts': result['contract'], 'opening_cash': result['opening_cash'],
                        'settlement': result['settlement'], 'initial_liability': result['initial_liability'],
                        'journal': journal, 'final_state': state, 'notes': result['notes']}
            for key, value in expected.items():
                if case.get(key) != value: failures.append(label + ': replay ' + key)
            oracle = independent_case(contract, case['settlement'], case['opening_cash'], authority)
            oracle['case_id'] = label
            if case.get('independent_oracle') != oracle:
                failures.append(label + ': independent arithmetic')
        except (KeyError, ValueError, TypeError) as exc:
            failures.append(label + ': invalid case: ' + str(exc))
    comparison = payload.get('comparisons', {})
    failures.extend(check_comparison(comparison, authority))
    for case in cases:
        if case.get('case_id') in ('redeem-default', 'convert-default'):
            try:
                if comparison_economics(Contract(**case['facts']), case['opening_cash']) != comparison.get('economic_facts'):
                    failures.append('comparison economics differ from baseline case')
            except (TypeError, ValueError, KeyError): failures.append('invalid baseline economics')
    queue = payload.get('method_queue', [])
    if {x.get('method') for x in queue} != {'revenue', 'tax', 'leases', 'FX', 'complex_groups', 'bonds'}:
        failures.append('method queue')
    blocks = payload.get('access_blocks', [])
    if not blocks or not all(x.get('status') in {'unavailable', 'uninspected', 'partially_inspected'} for x in blocks):
        failures.append('access blocks')
    criteria = payload.get('acceptance', {}).get('criteria', {})
    comparison_complete = comparison.get('criterion_status') == 'complete_bounded' and not check_comparison(comparison, authority)
    expected = {'criterion_1': 'complete_bounded', 'criterion_2': 'complete_bounded',
                'criterion_3': 'complete_bounded' if comparison_complete else 'incomplete',
                'criterion_4': 'complete_bounded'}
    if criteria != expected or payload.get('acceptance', {}).get('phase_criteria_complete') is not comparison_complete:
        failures.append('criterion acceptance status')
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
    timer = perf_counter()
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
            findings = check_comparison(comparison, authority)
            checks.append({'id': 'matched_comparison', 'passed': not findings,
                           'observed': {'rows': len(rows), 'criterion_status': comparison.get('criterion_status'),
                                        'failures': findings}})
            errors.extend('matched comparison: ' + x for x in findings)
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
        "tests": tests["methods"],
        "checks": checks,
        "errors": errors,
        "cases": case_reports,
        "comparison": comparison,
        "files": file_status,
        "manifest": {
            "command": "python3 -B scripts/check_accounting_p08.py --check",
            "working_directory": str(ROOT),
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "python_prefix": sys.prefix,
            "conda_env": os.environ.get('CONDA_DEFAULT_ENV'),
            "hardware": "CPU only; no accelerator framework imported",
            "CUDA_VISIBLE_DEVICES": os.environ.get('CUDA_VISIBLE_DEVICES'),
            "random_seeds": "N/A: exact deterministic fixtures",
            "started_utc": started.isoformat(),
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "wall_seconds": round(perf_counter() - timer, 6),
            "authority_register_sha256": sha256(REGISTER),
            "engine_sha256": sha256(ENGINE),
            "test_sha256": sha256(TEST_FILE),
        },
        "acceptance": {
            "engineering": passed,
            "phase_criteria_complete": bool(passed and comparison.get("criterion_status") == "complete_bounded"),
            "criteria": (authority_payload or {}).get("acceptance", {}).get("criteria", {}),
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
