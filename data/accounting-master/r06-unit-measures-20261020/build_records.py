"""Construct source-bound unit compatibility records once."""
from collections import Counter
import importlib.util
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / "data/accounting-master"


def write(name, value):
    with (U / name).open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2)
        f.write("\n")


def main():
    assert not (U / "units.json").exists()
    spec = importlib.util.spec_from_file_location("unit_measure_check", U / "compare.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    units, types, facts = m.derive()
    for name, value in (("units", units), ("types", types), ("facts", facts)):
        write(name + ".json", value)
    xbrl = B / "r06-enumeration-domain-20261020/sources/03-xbrl21.visible.txt"
    dtr20 = B / "taxonomy-reuse-20261007/sources/import-05-trusted.body"
    dtr22 = B / "taxonomy-reuse-20261007/sources/import-06-trusted.body"
    sections = [
        ("numeric_unit_presence", xbrl, 2529, 2567),
        ("unit_structure", xbrl, 3312, 3374),
        ("unit_type_and_simplest_rules", xbrl, 3375, 3418),
        ("unit_product_examples", xbrl, 3420, 3477),
        ("measure_identity", xbrl, 3730, 3750),
        ("monetary_shares_pure_semantics", xbrl, 4762, 4810),
        ("dtr20_percent_pershare", dtr20, 107, 144),
        ("dtr22_percent_pershare", dtr22, 107, 144),
    ]
    anchors = [{"id": ident, "source": m.bind(path), "first_line": first, "last_line": last,
                "excerpt": "\n".join(path.read_text().splitlines()[first-1:last])}
               for ident,path,first,last in sections]
    inputs = {m.m.COVERAGE, m.m.INSTANCE, m.PACKET, m.PORTABLE, xbrl, dtr20, dtr22,
              B / "r06-enumeration-domain-20261020/sources/03-xbrl21.body",
              B / "r06-numeric-lexical-20261020/compare.py",
              B / "r06-text-semantics-20261020/compare.py",
              B / "r06-context-periods-20261020/compare.py",
              B / "r06-typed-domain-dates-20261020/compare.py",
              B / "r06-context-periods-20261020/contexts.json"}
    coverage = m.load(m.m.COVERAGE)
    inputs.update(R / n["anchor"]["source_path"] for n in coverage["type_nodes"].values() if "anchor" in n)
    inputs.update(R / n["declaration_anchor"]["source_path"] for n in coverage["concepts"].values())
    write("source-ledger.json", {"date": "2026-10-20", "new_acquisitions": 0,
        "bindings": [m.bind(path) for path in sorted(inputs)], "anchors": anchors,
        "scope": "Finite source unit/type correspondence; historical ISO4217 designation validity remains unverified"})
    write("acquisitions.json", {"new_acquisitions": 0, "reused": m.bind(B / "r06-enumeration-domain-20261020/acquisitions.json")})
    def measure(token):
        return "<measure>" + token + "</measure>"
    def xml(n, d=None, extra=""):
        body = "".join(measure(x) for x in n)
        if d is not None:
            body = "<divide><unitNumerator>" + body + "</unitNumerator><unitDenominator>" + "".join(measure(x) for x in d) + "</unitDenominator></divide>"
        return ('<unit xmlns="http://www.xbrl.org/2003/instance" xmlns:i="http://www.xbrl.org/2003/instance" '
                'xmlns:c="http://www.xbrl.org/2003/iso4217" xmlns:alt="http://www.xbrl.org/2003/iso4217" '
                'xmlns:other="urn:other" id="u"' + extra + ">" + body + "</unit>")
    fixtures = [
        {"id":"currency","xml":xml(["c:USD"]),"expected_status":"supported","category":"monetary","expected_compatibility":"partial_currency_history_unverified"},
        {"id":"other_currency_prefix","xml":xml(["alt:USD"]),"expected_status":"supported","category":"monetary","expected_compatibility":"partial_currency_history_unverified"},
        {"id":"currency_namespace_only","xml":xml(["c:NotCheckedCode"]),"expected_status":"supported","category":"monetary","expected_compatibility":"partial_currency_history_unverified"},
        {"id":"wrong_currency_namespace","xml":xml(["other:USD"]),"expected_status":"supported","category":"monetary","expected_compatibility":"type_unit_mismatch"},
        {"id":"shares","xml":xml(["shares"]),"expected_status":"supported","category":"shares","expected_compatibility":"supported"},
        {"id":"pure","xml":xml(["pure"]),"expected_status":"supported","category":"pure","expected_compatibility":"supported"},
        {"id":"pershare","xml":xml(["c:USD"],["shares"]),"expected_status":"supported","category":"per_share","expected_compatibility":"partial_currency_history_unverified"},
        {"id":"ratio_not_monetary","xml":xml(["c:USD"],["shares"]),"expected_status":"supported","category":"monetary","expected_compatibility":"type_unit_mismatch"},
        {"id":"currency_not_pershare","xml":xml(["c:USD"]),"expected_status":"supported","category":"per_share","expected_compatibility":"type_unit_mismatch"},
        {"id":"issuer_count","xml":xml(["other:Vendor"]),"expected_status":"supported","category":"general_numeric","expected_compatibility":"supported"},
        {"id":"square_measure","xml":xml(["other:feet","other:feet"]),"expected_status":"supported",
         "expected_signature":{"numerator":{"{urn:other}feet":2},"denominator":{}}},
        {"id":"one_measure","xml":xml(["other:feet"]),"expected_status":"supported",
         "expected_signature":{"numerator":{"{urn:other}feet":1},"denominator":{}}},
        {"id":"product_order","xml":xml(["other:second","other:meter"]),"expected_status":"supported",
         "expected_signature":{"numerator":{"{urn:other}meter":1,"{urn:other}second":1},"denominator":{}}},
        {"id":"cross_side_same_name","xml":xml(["c:USD"],["alt:USD"]),"expected_status":"same_measure_on_both_sides"},
        {"id":"same_local_different_namespace","xml":xml(["c:USD"],["other:USD"]),"expected_status":"supported"},
        {"id":"reserved_invalid","xml":xml(["i:dollar"]),"expected_status":"invalid_reserved_xbrli_measure"},
        {"id":"unbound_prefix","xml":xml(["missing:USD"]),"expected_status":"unbound_measure_prefix"},
        {"id":"empty_product","xml":xml([]),"expected_status":"invalid_unit_shape"},
        {"id":"empty_denominator","xml":xml(["c:USD"],[]),"expected_status":"invalid_divide_shape"},
        {"id":"wrong_ratio_order","xml":xml(["c:USD"],["shares"]).replace("unitNumerator","swap").replace("unitDenominator","unitNumerator").replace("swap","unitDenominator"),"expected_status":"invalid_divide_shape"},
        {"id":"two_qnames_in_measure","xml":xml(["c:USD shares"]),"expected_status":"outside_scope"},
        {"id":"xml_whitespace","xml":xml([" \tc:USD\r\n"]),"expected_status":"supported","category":"monetary","expected_compatibility":"partial_currency_history_unverified"},
        {"id":"nonnumeric_unit","xml":xml(["pure"]),"expected_status":"supported","category":"nonnumeric","expected_compatibility":"unexpected_unit_on_nonnumeric"},
    ]
    write("fixtures.json", fixtures)
    write("percent-discriminator.json", {"kind":"authored_exact_example","reported_token":"0.25",
        "presentation_percent":"25%","incorrect_reported_token":"25",
        "rule":"DTR presentation type does not authorize multiplying the stored reported ratio by100.",
        "scope":"Neither rendering nor a check of the issuer's chosen display percentages."})
    write("descriptive-inventory.json", {"role":"explanatory_only",
        "unit_occurrence_counts":dict(Counter(f["source_unit_id"] or "absent" for f in facts)),
        "type_categories":dict(Counter(f["type_category"] for f in facts)),
        "percent_facts":sum(f["percent_presentation"] for f in facts),
        "nil_facts":[{"fact_id":f["fact_id"],"unit_id":f["source_unit_id"]} for f in facts if f["source_nil"] in ("true","1")],
        "currency_history_pending":sum(f["unit_compatibility"]["status"]=="partial_currency_history_unverified" for f in facts)})
    write("source-support-ledger.json", {"classification":"PRIMARY_SPECIFICATION_AND_RETAINED_SOURCE",
        "identity":"source-ledger.json","read_scope":"Eight technical/source spans",
        "allowed":"Finite measure/QName/product/type/presence account",
        "forbidden":["historical ISO4217 validity","full XBRL unit validation","financial unit mapping","currency conversion","current registry compliance"]})
    write("claim-support-ledger.json", {"claims":[
        {"claim":"Numeric items require unitRef; nonnumeric items prohibit it.","class":"PRIMARY_SOURCE","anchors":["numeric_unit_presence"]},
        {"claim":"Monetary/shares types constrain unit shape and namespace; currency validity also depends on the context period.","class":"PRIMARY_SOURCE","anchors":["unit_type_and_simplest_rules"]},
        {"claim":"Repeated measures represent products with multiplicity; matching opposite-side measures must not occur.","class":"PRIMARY_RULE_AND_EXAMPLE","anchors":["unit_structure","unit_type_and_simplest_rules","unit_product_examples"]},
        {"claim":"DTR percent values remain ratios; perShare is a monetary amount divided by shares, despite base decimal typing.","class":"PRIMARY_SOURCE","anchors":["dtr20_percent_pershare","dtr22_percent_pershare"]},
        {"claim":"All selected unit-presence and scoped shape/type checks pass; currency history remains unverified.","class":"FINITE_SOURCE_RESULT","evidence":"facts.json"},
    ]})
    write("backward-snowball-ledger.json", {"scope":"Unit/type normative prerequisites","leads":[
        {"source":"Historical ISO4217 designations","status":"Required for complete monetary validity; no authoritative period-specific registry inspected"},
        {"source":"DTR UTR or filing-specific unit guidance","status":"Broader registry/application rules not asserted; exact source annotations used"},
        {"source":"XML QName grammar","status":"Per-element names expanded within explicit ASCII subset; broader Unicode forms outside scope"},
    ]})
    write("forward-snowball-ledger.json", {"new_queries":0,"scope":"Retained-version source inquiry",
        "status":"Later registry updates and installed validation remain unverified"})
    write("citation-venue-ledger.json", {"sources":[
        {"title":"XBRL2.1","version":"2003-12-31 with2013-02-20 corrections"},
        {"title":"DTR types","versions":["2020-01-21","2022-03-31"]}],
        "citation_metrics":"not applicable"})
    write("omission-risk-ledger.json", {"risks":[
        {"risk":"Currency namespace pass mistaken for historical code validity","response":"Explicit partial result for all affected facts; arbitrary currency-name fixture also stays pending"},
        {"risk":"Product deduplication or silent cancellation","response":"Multiplicity-preserving signatures and source-invalid opposite-side fixture"},
        {"risk":"Numeric-looking strings treated as amounts","response":"Declared-type graph classifies all1,127 occurrences;164 nonnumeric unitless records retained"},
        {"risk":"Nil numeric facts lose unit requirement","response":"Both actual nil facts checked and presence mutation rejected"},
        {"risk":"Percent/perShare semantics reduced to decimal base","response":"Retained DTR annotations and separate semantic categories; exact100x discriminator"},
    ]})
    print(json.dumps({"constructed":True,"units":len(units),"facts":len(facts),"fixtures":len(fixtures),
                      "anchors":len(anchors),"bindings":len(inputs),
                      "categories":dict(Counter(f["type_category"] for f in facts))}))


if __name__ == "__main__":
    main()
