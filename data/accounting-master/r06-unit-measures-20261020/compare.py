"""Finite unit structure and declared-type checks; no currency registry admission."""
from collections import Counter
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


m = imported("unit_source_helpers", B / "r06-numeric-lexical-20261020/compare.py")
p = imported("unit_span_helpers", B / "r06-context-periods-20261020/compare.py")
t = imported("unit_fixture_namespaces", B / "r06-typed-domain-dates-20261020/compare.py")
load, bind, digest = m.load, m.bind, m.digest
PACKET = B / "native-full-portable-20261018/native-packet.json"
PORTABLE = B / "native-full-portable-20261018/portable-records.json"
X = "{http://www.xbrl.org/2003/instance}"
CURRENCY = "{http://www.xbrl.org/2003/iso4217}"
ASCII_QNAME = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*(?::[A-Za-z_][A-Za-z0-9_.-]*)?")


def measures(elements, scopes):
    result = []
    for element in elements:
        if element.tag != X + "measure" or element.attrib or len(element):
            return {"status": "invalid_measure_shape"}
        token = m.collapse(element.text or "")
        if ASCII_QNAME.fullmatch(token) is None:
            return {"status": "outside_scope", "reason": "outside selected ASCII QName profile"}
        try:
            name = m.expanded(token, scopes[id(element)])
        except KeyError:
            return {"status": "unbound_measure_prefix"}
        if name.startswith(X) and name not in (X + "pure", X + "shares"):
            return {"status": "invalid_reserved_xbrli_measure"}
        result.append({"raw_token": element.text, "token": token, "expanded_name": name})
    return {"status": "supported", "measures": result}


def unit(element, scopes):
    if element.tag != X + "unit" or set(element.attrib) != {"id"} or not element.get("id"):
        return {"status": "invalid_unit_shape"}
    if (element.text or "").strip() or any((e.tail or "").strip() for e in element):
        return {"status": "invalid_unit_shape"}
    children = list(element)
    if children and all(e.tag == X + "measure" for e in children):
        numerator, denominator = children, []
        form = "product"
    elif len(children) == 1 and children[0].tag == X + "divide":
        divide = children[0]
        if divide.attrib or (divide.text or "").strip() or [e.tag for e in divide] != [X + "unitNumerator", X + "unitDenominator"]:
            return {"status": "invalid_divide_shape"}
        if any(e.attrib or (e.text or "").strip() or (e.tail or "").strip() or len(e) == 0 for e in divide):
            return {"status": "invalid_divide_shape"}
        numerator, denominator = list(divide[0]), list(divide[1])
        form = "ratio"
    else:
        return {"status": "invalid_unit_shape"}
    for e in numerator + denominator:
        if (e.tail or "").strip():
            return {"status": "invalid_measure_shape"}
    n, d = measures(numerator, scopes), measures(denominator, scopes)
    if n["status"] != "supported":
        return n
    if d["status"] != "supported":
        return d
    ns = Counter(x["expanded_name"] for x in n["measures"])
    ds = Counter(x["expanded_name"] for x in d["measures"])
    if ns.keys() & ds.keys():
        return {"status": "same_measure_on_both_sides", "source_was_not_cancelled": True}
    return {"status": "supported", "form": form, "numerator": n["measures"], "denominator": d["measures"],
            "product_signature": {"numerator": dict(sorted(ns.items())), "denominator": dict(sorted(ds.items()))},
            "meaning": "exact source measure names and multiplicities; no financial mapping"}


def classify(name, nodes):
    seen = set()
    def visit(key):
        assert key not in seen, "nonlinear/cyclic selected type chain"
        seen.add(key)
        node = nodes[key]
        for edge in node.get("edges", []):
            assert edge["role"] == "base", "outside selected simple base-chain profile"
            visit(edge["target"])
    visit(name)
    terminals = sorted(k for k in seen if nodes[k]["status"] == "builtin_reference_only")
    assert len(terminals) == 1
    numeric = terminals[0] in (m.XS + "decimal", m.XS + "integer")
    if X + "monetaryItemType" in seen:
        category = "monetary"
    elif X + "sharesItemType" in seen:
        category = "shares"
    elif any(k.startswith("{http://www.xbrl.org/dtr/type/") and k.endswith("}perShareItemType") for k in seen):
        category = "per_share"
    elif X + "pureItemType" in seen:
        category = "pure"
    elif numeric:
        category = "general_numeric"
    else:
        category = "nonnumeric"
    return {"declared_type": name, "base_chain_members": sorted(seen), "terminal": terminals[0],
            "numeric": numeric, "category": category,
            "percent_presentation": any(k.endswith("}percentItemType") for k in seen)}


def compatibility(category, parsed_unit):
    if category == "nonnumeric":
        return {"status": "supported" if parsed_unit is None else "unexpected_unit_on_nonnumeric"}
    if parsed_unit is None:
        return {"status": "missing_numeric_unit"}
    if parsed_unit["status"] != "supported":
        return {"status": "invalid_unit", "unit_status": parsed_unit["status"]}
    n = [x["expanded_name"] for x in parsed_unit["numerator"]]
    d = [x["expanded_name"] for x in parsed_unit["denominator"]]
    if category == "monetary":
        valid = len(n) == 1 and not d and n[0].startswith(CURRENCY)
    elif category == "shares":
        valid = n == [X + "shares"] and not d
    elif category == "pure":
        valid = n == [X + "pure"] and not d
    elif category == "per_share":
        valid = len(n) == 1 and n[0].startswith(CURRENCY) and d == [X + "shares"]
    else:
        assert category == "general_numeric"
        valid = True
    if not valid:
        return {"status": "type_unit_mismatch"}
    if category in ("monetary", "per_share"):
        return {"status": "partial_currency_history_unverified", "checked": "shape and currency namespace",
                "currency_code": n[0][len(CURRENCY):],
                "currency_code_valid_during_context_period": None}
    return {"status": "supported"}


def derive():
    coverage = load(m.COVERAGE)
    for node in coverage["type_nodes"].values():
        if "anchor" in node:
            m.checked_anchor(node["anchor"])
    source = m.INSTANCE.read_bytes()
    root, scopes = m.schema(str(m.INSTANCE.relative_to(R)))
    packet = load(PACKET)
    packet_units = {r["id"]: r for r in packet["units"]}
    portable = load(PORTABLE)
    portable_units = {r["body"]["xml_id"]: r["body"] for r in portable if r["kind"] == "XbrlUnitEvidence"}
    units = []
    for element in root.findall(X + "unit"):
        ident = element.get("id")
        original = packet_units[ident]
        p.span_check(original["span"], source)
        interpreted = unit(element, scopes)
        assert interpreted["status"] == "supported"
        for side in ("numerator", "denominator"):
            source_side = [{"token": r["token"], "expanded_name": r["expanded_name"]} for r in interpreted[side]]
            assert original[side] == source_side
            expected = [{"token": r["token"], "qname": {"namespace_uri": r["expanded_name"][1:].split("}",1)[0],
                        "local_name": r["expanded_name"].split("}",1)[1]}} for r in interpreted[side]]
            assert portable_units[ident][side] == expected
        units.append({"unit_id": ident, "source_span": original["span"], "interpretation": interpreted,
                      "full_unit_validation": "not_run", "portable_records_changed": False})
    assert len(units) == len(packet_units) == len(portable_units) == 7
    by_unit = {r["unit_id"]: r["interpretation"] for r in units}
    types = {name: classify(name, coverage["type_nodes"]) for name in sorted({r["declared_type"] for r in coverage["concepts"].values()})}
    actual = {e.get("id"): e for e in root if e.get("id")}
    facts = []
    for row in coverage["occurrences"]:
        ident = row["fact_id"]
        p.span_check(row["source_span"], source)
        element = actual[ident]
        assert element.tag == row["source_concept"] and element.attrib == row["source_attributes"]
        concept = coverage["concepts"][row["source_concept"]]
        m.checked_anchor(concept["declaration_anchor"])
        type_info = types[concept["declared_type"]]
        uid = row["source_unit_id"]
        assert element.get("unitRef") == uid
        parsed = by_unit[uid] if uid is not None else None
        verdict = compatibility(type_info["category"], parsed)
        assert verdict["status"] in ("supported", "partial_currency_history_unverified"), ident
        assert type_info["numeric"] == (uid is not None)
        if type_info["percent_presentation"]:
            assert X + "pureItemType" in type_info["base_chain_members"]
            number = m.lexical(row["decoded_text"], "decimal")
            assert number["status"] == "member"
            assert row["portable_candidate_value"]["tag"] == "Decimal"
        facts.append({"fact_id": ident, "concept": row["source_concept"], "declared_type": concept["declared_type"],
                      "type_category": type_info["category"], "numeric": type_info["numeric"],
                      "source_unit_id": uid, "source_context_id": row["source_context_id"],
                      "source_nil": element.get(m.XSI + "nil"),
                      "unit_compatibility": verdict, "percent_presentation": type_info["percent_presentation"],
                      "source_value_unchanged": row["portable_candidate_value"], "full_validation": "not_run"})
    assert len(facts) == 1127
    return units, types, facts


def check():
    n = 0
    def require(test, label):
        nonlocal n
        assert test, label
        n += 1
    ledger = load(U / "source-ledger.json")
    for binding in ledger["bindings"]:
        require(bind(R / binding["path"]) == binding, binding["path"])
    for a in ledger["anchors"]:
        path = R / a["source"]["path"]
        require(bind(path) == a["source"], a["id"])
        require("\n".join(path.read_text().splitlines()[a["first_line"]-1:a["last_line"]]) == a["excerpt"], a["id"])
    units, types, facts = derive()
    for name, data in (("units",units),("types",types),("facts",facts)):
        require(data == load(U / (name+".json")), name)
    fixtures = load(U / "fixtures.json")
    for f in fixtures:
        node, scopes = t.parse_fixture(f["xml"])
        result = unit(node, scopes)
        require(result["status"] == f["expected_status"], f["id"])
        if "category" in f:
            require(compatibility(f["category"], result)["status"] == f["expected_compatibility"], f["id"] + " type")
        if "expected_signature" in f:
            require(result["product_signature"] == f["expected_signature"], f["id"] + " product")
    for f in facts:
        altered = compatibility(f["type_category"], None) if f["numeric"] else compatibility("nonnumeric", units[0]["interpretation"])
        require(altered["status"] == ("missing_numeric_unit" if f["numeric"] else "unexpected_unit_on_nonnumeric"), f["fact_id"] + " presence")
    nils = [f for f in facts if f["source_nil"] in ("true","1")]
    require(len(nils) == 2 and all(f["numeric"] and f["source_unit_id"] for f in nils), "nil numeric still has unit")
    # Exact, authored distinction between reported ratio and presentation percent.
    example = load(U / "percent-discriminator.json")
    q = Fraction(example["reported_token"])
    require(q == Fraction(1,4), "reported ratio value")
    require(q * 100 == Fraction(25), "presentation percentage")
    require(Fraction(example["incorrect_reported_token"]) != q, "100x mutation changes source value")
    return {"assertions": n, "units": len(units), "facts": len(facts),
            "numeric_facts_with_unit": sum(f["numeric"] for f in facts),
            "nonnumeric_facts_without_unit": sum(not f["numeric"] for f in facts),
            "nil_numeric_facts_with_unit": len(nils), "fixtures": len(fixtures),
            "unit_presence_mutations_rejected": len(facts),
            "currency_history_pending_facts": sum(f["unit_compatibility"]["status"] == "partial_currency_history_unverified" for f in facts),
            "source_anchors": len(ledger["anchors"]), "input_bindings": len(ledger["bindings"]),
            "new_acquisitions": 0, "upstream_executed": False,
            "full_validation": "not_run", "whole_rows_closed": 0}
