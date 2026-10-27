"""Finite document calculations for nine saved assessment examples; no runtime API.

Usage: PYTHONDONTWRITEBYTECODE=1 python3 <this-file> <fresh-report-path>
The explicit table below is an independent expected-outcome enumeration.
"""
from pathlib import Path
import hashlib
import json
import platform
import sys
import time

start = time.monotonic()
root = Path(__file__).resolve().parents[4]
directory = root / "docs/design/proposal/architecture"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda name: json.loads((directory / name).read_text())
saved = read("accounting-eligibility-decision-fixtures-v1.json")
previous = read("accounting-eligibility-fixtures-v1.json")
old = {c["id"]: c for c in previous["cases"]}
new = {c["id"]: c for c in saved["cases"]}
all_cases = dict(old, **new)
checks = []
def check(name, result):
    checks.append({"id": name, "passed": bool(result)})

order = [f"C{i:02}" for i in range(1, 11)]
precedence = ["ineligible", "outside_scope", "unresolved", "eligible"]
# Branch expectations transcribed explicitly from the stated logical cases,
# not computed by reading the fixtures' expected labels.
table = [
    (True, True, "B5.1.2A(a)", "outside_scope", "E09"),
    (True, False, "B5.1.2A(a)", "outside_scope", "E07"),
    (True, None, "B5.1.2A(a)", "outside_scope", "E10"),
    (False, True, "B5.1.2A(a)", "outside_scope", "E11"),
    (False, False, "B5.1.2A(b)", "outside_scope", "E08"),
    (False, None, "unknown", "unresolved", "E12"),
    (None, True, "B5.1.2A(a)", "outside_scope", "E13"),
    (None, False, "unknown", "unresolved", "E14"),
    (None, None, "unknown", "unresolved", "E06"),
]
check("six valuation and three combined cases", list(new) == [f"E{i:02}" for i in range(9, 18)])
check("ten conditions and fixed precedence", saved["condition_order"] == order and saved["status_precedence"] == precedence)
actual_table = [(r["quote"], r["observable_only"], r["branch"], r["summary"], r["case_id"]) for r in saved["valuation_table"]]
check("complete independent nine-pair table", actual_table == table)
fields = ["identical_instrument_active_market_quote", "technique_only_observable_market_data"]
losses = []
for q, o, branch, status, ident in table:
    c = all_cases[ident]
    values = {k: v["value"] for k, v in c["complete_inputs"].items()}
    check(ident + " valuation inputs", [values["C09"][f] for f in fields] == [q, o])
    check(ident + " same price and supplied fair value", values["C06"]["price"] == "100" and values["C06"]["fair_value"] == "105")
    check(ident + " expected branch", c["expected_assessment"]["valuation_branch"] == branch and values["C09"]["branch"] == branch)
    check(ident + " expected summary", c["expected_assessment"]["status"] == status)
    check(ident + " no available unequal-price method", values["C10"]["unequal_price_a_method_available"] is False and values["C10"]["unequal_price_b_method_available"] is False)
    coerced = "B5.1.2A(a)" if bool(q) or bool(o) else "B5.1.2A(b)"
    if coerced != branch:
        losses.append(ident)
    if ident not in new:
        continue
    differences = [k for k in order if c["complete_inputs"][k] != old["E06"]["complete_inputs"][k]]
    check(ident + " only C09 and dependent C10 change", differences == ["C09", "C10"] == c["declared_input_changes"])
    f9 = c["condition_findings"][8]
    check(ident + " conditional branch finding", f9["status"] == ("unresolved" if branch == "unknown" else "satisfied_conditionally"))
    check(ident + " two route findings", [f["field"] for f in f9["route_findings"]] == fields)
    for finding, value in zip(f9["route_findings"], [q, o]):
        check(ident + " route " + finding["field"], finding["value"] is value and finding["status"] == ("unknown" if value is None else "qualifies" if value else "does_not_qualify") and bool(finding["reason"]))
    unknown_fields = [f for f, v in zip(fields, [q, o]) if v is None]
    check(ident + " individual unknowns retained", [x["field"] for x in c["expected_assessment"]["open_evidence"]] == unknown_fields)
    check(ident + " unknown dependency stated", all(x["blocks_branch_selection"] == (branch == "unknown") and x["reason"] for x in c["expected_assessment"]["open_evidence"]))
    check(ident + " method finding", c["condition_findings"][9]["status"] == status)
check("unknown-to-false changes exactly three branches", sorted(losses) == ["E06", "E12", "E14"])

compositions = [
    ("E15", "E01", [("C03", "E03"), ("C05", "E02")], {"C03": "ineligible", "C05": "unresolved"}, "ineligible"),
    ("E16", "E04", [("C05", "E02")], {"C01": "outside_scope", "C05": "unresolved"}, "outside_scope"),
    ("E17", "E04", [("C03", "E03"), ("C05", "E02")], {"C01": "outside_scope", "C03": "ineligible", "C05": "unresolved"}, "ineligible"),
]
first_only = []
for ident, base, replacements, expected, summary in compositions:
    c = new[ident]
    target = dict(old[base]["complete_inputs"])
    for cond, donor in replacements:
        target[cond] = old[donor]["complete_inputs"][cond]
    check(ident + " exact expanded composition", c["complete_inputs"] == target)
    check(ident + " exact changed conditions", [k for k in order if c["complete_inputs"][k] != old[base]["complete_inputs"][k]] == c["declared_input_changes"])
    adverse = {f["condition"]: f["status"] for f in c["condition_findings"] if f["status"] in precedence}
    check(ident + " all adverse categories", adverse == expected)
    check(ident + " independent summary", c["expected_assessment"]["status"] == summary)
    values = {k: v["value"] for k, v in target.items()}
    date = "2026-07-03" if base == "E04" else "2024-06-03"
    check(ident + " coherent candidate dates", all(values["C04"][k] == date for k in ["trade_date", "settlement_date", "recognition_date"]) and values["C06"]["valuation_date"] == date)
    check(ident + " contractual date consistent", values["C03"]["contractual_date"] == (date if values["C03"]["party_to_contract"] else None))
    first = next(iter(adverse))
    first_only.append({"case": ident, "first_condition": first, "first_summary": adverse[first], "required_summary": summary, "lost_conditions": list(adverse)[1:]})

for ident, c in new.items():
    inputs = c["complete_inputs"]
    findings = c["condition_findings"]
    assessment = c["expected_assessment"]
    check(ident + " complete ordered inputs and findings", list(inputs) == order and [f["condition"] for f in findings] == order)
    for cond in order:
        packet = inputs[cond]
        check(ident + " provenance " + cond, all(k in packet for k in ["value", "unknown_reason", "provenance", "scope", "version"]) and all(packet["provenance"].get(k) for k in ["kind", "origin", "source_rule"]) and bool(packet["scope"]) and bool(packet["version"]))
    adverse = {f["condition"]: f["reason"] for f in findings if f["status"] in precedence}
    check(ident + " exact non-lossy reasons", assessment["reasons"] == adverse and all(f["reason"] for f in findings))
    statuses = [f["status"] for f in findings]
    check(ident + " precedence derived from all findings", assessment["status"] == next(s for s in precedence if s in statuses))
    check(ident + " no proposal, delta or permission", assessment["journal_proposal"] is None and assessment["state_delta"] is None and assessment["posting_permitted"] is False)
    check(ident + " four unchanged domains", c["no_mutation"] == dict.fromkeys(["posted_journals", "account_state", "event_identity_map", "committed_receipts"], "unchanged"))
    check(ident + " no fabricated exchange", not any(k in c for k in ["request", "receipt", "canonical_request_ref"]))
snapshot = read("accounting-eligibility-decision-inputs-v1.json")
for name, digest in snapshot["predecessor_files"].items():
    check("preserved " + name, sha(root / name) == digest)
for ref in saved["references"]:
    check("source reference " + ref["path"], sha(root / ref["path"]) == ref["sha256"])
source = root / "docs/design/research/p08-v1/aasb9.txt"
check("retained authority hash", sha(source) == "8d5315a45bc9e6f1918a8277d9954621927bc1583fe426bb20b4ebf6f3a0daa6")
segment = "\n".join(source.read_text().split("\n")[4393:4417])
check("paragraph distinction retained", all(x in segment for x in ["B5.1.2A", "an active market for an identical", "uses only data from observable markets", "in all other cases"]))
inputs = [Path(__file__).resolve(), source] + [directory / n for n in ["accounting-eligibility-decision-fixtures-v1.json", "accounting-eligibility-decision-supplement-v1.md", "accounting-eligibility-decision-inputs-v1.json", "accounting-eligibility-fixtures-v1.json", "accounting-eligibility-dossier-v1.md"]]
report = {"schema_version": "accdsl.eligibility.decision-verification.v1", "passed": all(x["passed"] for x in checks), "total": len(checks), "passed_count": sum(x["passed"] for x in checks), "checks": checks, "unknown_coercion_branch_changes": losses, "first_finding_comparison": first_only, "input_hashes": {str(p.relative_to(root)): sha(p) for p in inputs}, "manifest": {"command": ["PYTHONDONTWRITEBYTECODE=1", "python3", *sys.argv], "environment": {"python": sys.version, "executable": sys.executable, "platform": platform.platform(), "packages": "standard library only"}, "git_commit": "N/A: existing .git marker is not a usable repository; content hashes retained", "device_status": "CPU standard-library calculation; no GPU framework imported or device queried", "data_version": "pinned synthetic document fixtures", "seeds": "N/A: deterministic", "wall_seconds": time.monotonic() - start, "plan_file": "data/accounting-master/runs/20261005T150545-71a70996/P16/plan-0.response.json", "result_file": "data/accounting-master/deliverables/P16/result.md", "output_file": sys.argv[1]}, "limits": "Finite document calculations only; no runtime validator, source-completeness certification, accounting validity, scientific ranking, product readiness or human acceptance."}
with Path(sys.argv[1]).open("x") as stream:
    json.dump(report, stream, indent=2)
    stream.write("\n")
print(json.dumps({"passed": report["passed"], "total": report["total"], "failures": [c for c in checks if not c["passed"]]}))
sys.exit(0 if report["passed"] else 1)
