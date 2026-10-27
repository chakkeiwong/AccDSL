"""Source accuracy metadata and explicitly conditional exact rounding preimages."""
from collections import Counter
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
import importlib.util
from pathlib import Path
import re
import xml.etree.ElementTree as ET

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / "data/accounting-master"


def imported(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = imported("accuracy_source_helpers", B / "r06-numeric-lexical-20261020/compare.py")
p = imported("accuracy_span_helpers", B / "r06-context-periods-20261020/compare.py")
load, bind, digest = m.load, m.bind, m.digest
UNITS = B / "r06-unit-measures-20261020/facts.json"
NUMERIC = B / "r06-numeric-lexical-20261020/occurrences.json"


def rat(value):
    return {"n": str(value.numerator), "d": str(value.denominator)}


def fraction(value):
    return Fraction(int(value["n"]), int(value["d"]))


def accuracy_attribute(raw, kind):
    assert kind in ("decimals", "precision")
    if raw == "INF":
        return {"status": "supported", "raw": raw, "value": "INF"}
    collapsed = m.collapse(raw)
    if collapsed == "INF":
        return {"status": "outside_scope", "raw": raw, "reason": "whitespace-bearing INF not interpreted by local union profile"}
    if re.fullmatch(r"[+-]?[0-9]+", collapsed) is None:
        return {"status": "invalid_attribute_lexical", "raw": raw}
    value = int(collapsed)
    if kind == "precision" and value < 0:
        return {"status": "invalid_attribute_value", "raw": raw}
    return {"status": "supported", "raw": raw, "collapsed": collapsed, "value": value}


def metadata(numeric, nil, attrs):
    present = [k for k in ("decimals", "precision") if k in attrs]
    if not numeric or nil:
        return {"status": "supported" if not present else "accuracy_prohibited",
                "kind": "nil_numeric" if numeric and nil else "nonnumeric",
                "accuracy": None}
    if len(present) != 1:
        return {"status": "missing_accuracy" if not present else "both_accuracy_attributes"}
    kind = present[0]
    parsed = accuracy_attribute(attrs[kind], kind)
    return {"status": parsed["status"], "kind": kind, "accuracy": parsed}


def round_even(value, step):
    scaled = value / step
    lower = scaled.numerator // scaled.denominator
    remainder = scaled - lower
    if remainder < Fraction(1,2):
        selected = lower
    elif remainder > Fraction(1,2):
        selected = lower+1
    else:
        selected = lower if lower % 2 == 0 else lower+1
    return selected * step


def conditional(value, decimals):
    if decimals == "INF":
        return {"status": "source_asserted_exact", "asserted_value": rat(value),
                "underlying_economic_truth_verified": False}
    # Avoid arbitrary unbounded powers for a documentary fixture; actual d in [-9,4].
    if abs(decimals) > 1000:
        return {"status": "outside_scope", "reason": "local exponent resource bound"}
    step = Fraction(10) ** (-decimals)
    scaled = value / step
    if scaled.denominator != 1:
        return {"status": "off_grid_inverse_withheld", "reported_value": rat(value),
                "step": rat(step), "reason": "No source value normalization or spurious-digit policy selected"}
    even = scaled.numerator % 2 == 0
    return {"status": "conditional_preimage", "condition": "value is output of nearest rounding with ties to even at this step",
            "reported_value": rat(value), "step": rat(step), "grid_integer": str(scaled.numerator),
            "lower": rat(value-step/2), "upper": rat(value+step/2),
            "lower_closed": even, "upper_closed": even,
            "financial_observation_constraint_admitted": False}


def membership(value, record):
    lower, upper = fraction(record["lower"]), fraction(record["upper"])
    return ((value > lower or (value == lower and record["lower_closed"])) and
            (value < upper or (value == upper and record["upper_closed"])))


def crosscheck(record, decimals):
    value, step = fraction(record["reported_value"]), fraction(record["step"])
    lower, upper = fraction(record["lower"]), fraction(record["upper"])
    samples = [lower-step/4, lower, lower+step/4, value, upper-step/4, upper, upper+step/4]
    for sample in samples:
        result = round_even(sample, step)
        with localcontext() as ctx:
            ctx.prec = len(str(abs(sample.numerator))) + len(str(sample.denominator)) + abs(decimals) + 32
            number = Decimal(sample.numerator) / Decimal(sample.denominator)
            quantum = Decimal(1).scaleb(-decimals)
            independent = Fraction(number.quantize(quantum, rounding=ROUND_HALF_EVEN))
        assert result == independent
        assert membership(sample, record) == (result == value)
    return len(samples)


def derive():
    coverage = load(m.COVERAGE)
    type_rows = {r["fact_id"]: r for r in load(UNITS)}
    numeric_rows = {r["fact_id"]: r for r in load(NUMERIC)}
    raw = m.INSTANCE.read_bytes()
    actual = {e.get("id"): e for e in ET.fromstring(raw) if e.get("id")}
    rows = []
    for row in coverage["occurrences"]:
        ident = row["fact_id"]
        source = actual[ident]
        p.span_check(row["source_span"], raw)
        assert source.attrib == row["source_attributes"] and source.tag == row["source_concept"]
        numeric = type_rows[ident]["numeric"]
        nil = source.get(m.XSI + "nil") in ("true","1")
        result = metadata(numeric, nil, source.attrib)
        assert result["status"] == "supported", ident
        record = {"fact_id": ident, "concept": row["source_concept"], "numeric": numeric, "nil": nil,
                  "source_accuracy": {k: source.get(k) for k in ("decimals", "precision")},
                  "source_span": {k: row["source_span"][k] for k in ("byte_start","byte_end","slice_sha256")},
                  "metadata": result, "source_value_unchanged": row["portable_candidate_value"],
                  "conditional_interpretation": None, "schema_validation": "not_run",
                  "financial_accuracy_admission": False}
        if numeric and not nil:
            prior = numeric_rows[ident]
            assert prior["status"] == "narrow_lexical_value_agreement"
            assert prior["source_attributes"] == row["source_attributes"]
            value = fraction(prior["lexical"]["rational"])
            assert prior["portable_candidate_value"] == row["portable_candidate_value"]
            assert result["kind"] == "decimals", "actual precision requires separate interpretation"
            interpreted = conditional(value, result["accuracy"]["value"])
            record["conditional_interpretation"] = interpreted
            if interpreted["status"] == "conditional_preimage":
                record["rounding_crosscheck_samples"] = crosscheck(interpreted, result["accuracy"]["value"])
            elif interpreted["status"] == "source_asserted_exact":
                record["rounding_crosscheck_samples"] = 0
            else:
                record["rounding_crosscheck_samples"] = 0
        rows.append(record)
    assert len(rows) == 1127
    return rows


def check():
    n = 0
    def require(value, label):
        nonlocal n
        assert value, label
        n += 1
    ledger = load(U / "source-ledger.json")
    for b in ledger["bindings"]:
        require(bind(R / b["path"]) == b, b["path"])
    for a in ledger["anchors"]:
        path = R / a["source"]["path"]
        require(bind(path) == a["source"], a["id"])
        require("\n".join(path.read_text().splitlines()[a["first_line"]-1:a["last_line"]]) == a["excerpt"], a["id"])
    rows = derive()
    require(rows == load(U / "occurrences.json"), "all exact metadata records")
    fixtures = load(U / "fixtures.json")
    for f in fixtures["metadata"]:
        observed = metadata(f["numeric"], f["nil"], f["attributes"])
        require(observed["status"] == f["expected_status"], f["id"])
        if "expected_value" in f:
            require(observed["accuracy"]["value"] == f["expected_value"], f["id"] + " value")
    round_samples = 0
    for f in fixtures["rounding"]:
        value = Fraction(f["reported"])
        observed = conditional(value, f["decimals"])
        for key, expected in f["expected"].items():
            require(observed[key] == expected, f["id"] + " " + key)
        if observed["status"] == "conditional_preimage":
            round_samples += crosscheck(observed, f["decimals"])
    mutation_count = 0
    for row in rows:
        numeric, nil = row["numeric"], row["nil"]
        original = {k:v for k,v in row["source_accuracy"].items() if v is not None}
        if numeric and not nil:
            bad = dict(original, precision="3")
            expected = "both_accuracy_attributes"
        else:
            bad = dict(original, decimals="0")
            expected = "accuracy_prohibited"
        require(metadata(numeric, nil, bad)["status"] == expected, row["fact_id"] + " mutation")
        mutation_count += 1
    conditional_rows = [r for r in rows if r["conditional_interpretation"] is not None]
    statuses = Counter(r["conditional_interpretation"]["status"] for r in conditional_rows)
    return {"assertions": n, "facts": len(rows), "numeric_nonnil": len(conditional_rows),
            "finite_grid_preimages": statuses["conditional_preimage"],
            "INF_assertions": statuses["source_asserted_exact"],
            "off_grid_inverses_withheld": statuses["off_grid_inverse_withheld"],
            "nil_numeric": sum(r["numeric"] and r["nil"] for r in rows),
            "nonnumeric": sum(not r["numeric"] for r in rows),
            "actual_rounding_crosscheck_samples": sum(r.get("rounding_crosscheck_samples",0) for r in rows),
            "fixture_rounding_crosscheck_samples": round_samples,
            "metadata_fixtures": len(fixtures["metadata"]), "rounding_fixtures": len(fixtures["rounding"]),
            "metadata_mutations_rejected": mutation_count,
            "source_anchors": len(ledger["anchors"]), "input_bindings": len(ledger["bindings"]),
            "new_acquisitions": 0, "upstream_executed": False, "financial_admission": False, "whole_rows_closed": 0}
