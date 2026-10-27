"""One-time construction of retained accuracy evidence."""
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
    assert not (U / "occurrences.json").exists()
    spec = importlib.util.spec_from_file_location("accuracy_check", U / "compare.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rows = m.derive()
    write("occurrences.json", rows)
    xbrl = B / "r06-enumeration-domain-20261020/sources/03-xbrl21.visible.txt"
    xsd = B / "r06-context-periods-20261020/sources/xsd-part2.visible.txt"
    schema = B / "taxonomy-reuse-20261007/sources/import-03-trusted.body"
    sections = [
        ("accuracy_presence", xbrl, 2567, 2582),
        ("precision_meaning_examples", xbrl, 2583, 2691),
        ("decimals_meaning_examples_schema", xbrl, 2692, 2804),
        ("precision_inference_scope", xbrl, 2805, 2870),
        ("rounding_definition", xbrl, 2871, 2940),
        ("decimal_places_ties_even", xbrl, 2941, 2976),
        ("retained_accuracy_types", schema, 132, 167),
        ("nonnegative_integer_lexical", xsd, 2504, 2527),
    ]
    anchors = [{"id": ident, "source": m.bind(path), "first_line": first, "last_line": last,
                "excerpt": "\n".join(path.read_text().splitlines()[first-1:last])}
               for ident,path,first,last in sections]
    inputs = {m.m.COVERAGE, m.m.INSTANCE, m.UNITS, m.NUMERIC, xbrl, xsd, schema,
              B / "r06-enumeration-domain-20261020/sources/03-xbrl21.body",
              B / "r06-numeric-lexical-20261020/compare.py",
              B / "r06-context-periods-20261020/compare.py",
              R / "docs/design/proposal/manuscript-early-conversion-20261018/chapters/05-mathematics.tex"}
    write("source-ledger.json", {"date":"2026-10-20","new_acquisitions":0,
        "bindings":[m.bind(path) for path in sorted(inputs)],"anchors":anchors,
        "scope":"Exact retained metadata; nearest/ties-even inverse is conditional, never an admitted financial constraint",
        "source_tension":"Example GE/LT columns and spurious-digit readings are not silently promoted over corrected rounding definitions"})
    write("acquisitions.json", {"new_acquisitions":0,"reused":m.bind(B / "r06-enumeration-domain-20261020/acquisitions.json")})
    meta = [
        {"id":"finite","numeric":True,"nil":False,"attributes":{"decimals":"-6"},"expected_status":"supported","expected_value":-6},
        {"id":"exact","numeric":True,"nil":False,"attributes":{"decimals":"INF"},"expected_status":"supported","expected_value":"INF"},
        {"id":"xml_whitespace_integer","numeric":True,"nil":False,"attributes":{"decimals":" \t+002\r\n"},"expected_status":"supported","expected_value":2},
        {"id":"fractional_decimals","numeric":True,"nil":False,"attributes":{"decimals":"2.0"},"expected_status":"invalid_attribute_lexical"},
        {"id":"lowercase_inf","numeric":True,"nil":False,"attributes":{"decimals":"inf"},"expected_status":"invalid_attribute_lexical"},
        {"id":"nonxml_whitespace","numeric":True,"nil":False,"attributes":{"decimals":"\u00a02"},"expected_status":"invalid_attribute_lexical"},
        {"id":"union_inf_whitespace_not_implemented","numeric":True,"nil":False,"attributes":{"decimals":" INF "},"expected_status":"outside_scope"},
        {"id":"missing","numeric":True,"nil":False,"attributes":{},"expected_status":"missing_accuracy"},
        {"id":"both","numeric":True,"nil":False,"attributes":{"decimals":"2","precision":"3"},"expected_status":"both_accuracy_attributes"},
        {"id":"nil_no_accuracy","numeric":True,"nil":True,"attributes":{},"expected_status":"supported"},
        {"id":"nil_with_accuracy","numeric":True,"nil":True,"attributes":{"decimals":"0"},"expected_status":"accuracy_prohibited"},
        {"id":"nonnumeric_no_accuracy","numeric":False,"nil":False,"attributes":{},"expected_status":"supported"},
        {"id":"nonnumeric_with_accuracy","numeric":False,"nil":False,"attributes":{"precision":"INF"},"expected_status":"accuracy_prohibited"},
        {"id":"precision_zero","numeric":True,"nil":False,"attributes":{"precision":"0"},"expected_status":"supported","expected_value":0},
        {"id":"precision_negative_zero","numeric":True,"nil":False,"attributes":{"precision":"-0"},"expected_status":"supported","expected_value":0},
        {"id":"precision_negative","numeric":True,"nil":False,"attributes":{"precision":"-1"},"expected_status":"invalid_attribute_value"},
        {"id":"precision_exact","numeric":True,"nil":False,"attributes":{"precision":"INF"},"expected_status":"supported","expected_value":"INF"},
    ]
    rounding = [
        {"id":"even_integer","reported":"2","decimals":0,"expected":{"status":"conditional_preimage","lower_closed":True,"upper_closed":True}},
        {"id":"odd_integer","reported":"3","decimals":0,"expected":{"status":"conditional_preimage","lower_closed":False,"upper_closed":False}},
        {"id":"negative_even","reported":"-2","decimals":0,"expected":{"status":"conditional_preimage","lower_closed":True,"upper_closed":True}},
        {"id":"negative_odd","reported":"-3","decimals":0,"expected":{"status":"conditional_preimage","lower_closed":False,"upper_closed":False}},
        {"id":"zero","reported":"0","decimals":0,"expected":{"status":"conditional_preimage","lower_closed":True,"upper_closed":True}},
        {"id":"fraction_even","reported":"1.24","decimals":2,"expected":{"status":"conditional_preimage","lower_closed":True,"upper_closed":True}},
        {"id":"fraction_odd","reported":"1.25","decimals":2,"expected":{"status":"conditional_preimage","lower_closed":False,"upper_closed":False}},
        {"id":"large_even","reported":"2000","decimals":-3,"expected":{"status":"conditional_preimage","lower_closed":True,"upper_closed":True}},
        {"id":"large_odd","reported":"3000","decimals":-3,"expected":{"status":"conditional_preimage","lower_closed":False,"upper_closed":False}},
        {"id":"extra_digits","reported":"10.009","decimals":2,"expected":{"status":"off_grid_inverse_withheld"}},
        {"id":"source_negative_example","reported":"-205","decimals":-2,"expected":{"status":"off_grid_inverse_withheld"}},
        {"id":"exact_value","reported":"0.25","decimals":"INF","expected":{"status":"source_asserted_exact","underlying_economic_truth_verified":False}},
        {"id":"bounded_exponent","reported":"1","decimals":1001,"expected":{"status":"outside_scope"}},
    ]
    write("fixtures.json", {"metadata":meta,"rounding":rounding})
    finite = [r for r in rows if r["conditional_interpretation"] and r["conditional_interpretation"]["status"]=="conditional_preimage"]
    offgrid = [r["fact_id"] for r in rows if r["conditional_interpretation"] and r["conditional_interpretation"]["status"]=="off_grid_inverse_withheld"]
    write("descriptive-inventory.json", {"role":"explanatory_only",
        "decimals_frequencies":dict(Counter(r["source_accuracy"]["decimals"] or "absent" for r in rows)),
        "conditional_endpoint_parity":dict(Counter("even_closed" if r["conditional_interpretation"]["lower_closed"] else "odd_open" for r in finite)),
        "off_grid_facts":offgrid,"asserted_exact_fact_ids":[r["fact_id"] for r in rows if r["source_accuracy"]["decimals"]=="INF"],
        "not_concluded":"Counts and conditional preimages do not validate reported amounts or identify an actual measurement process."})
    write("source-support-ledger.json", {"classification":"PRIMARY_SPECIFICATION_AND_LOCAL_DERIVATION",
        "identity":"source-ledger.json","read_scope":"Eight technical/schema/lexical spans",
        "allowed":"Finite accuracy attribute consistency and conditional exact nearest/ties-even sets",
        "forbidden":["actual issuer rounding process","financial admissibility","confidence intervals","V-Equals","calculation-link consistency","generic precision inference"]})
    write("claim-support-ledger.json", {"claims":[
        {"claim":"Nil numeric and nonnumeric facts prohibit accuracy attributes; non-nil selected numeric facts require exactly one.","class":"PRIMARY_SOURCE","anchors":["accuracy_presence"]},
        {"claim":"Finite decimals are accuracy metadata, not a multiplier; INF asserts an exact represented value.","class":"PRIMARY_SOURCE","anchors":["precision_meaning_examples","decimals_meaning_examples_schema"]},
        {"claim":"The corrected decimal-place definition invokes nearest rounding with ties to even.","class":"PRIMARY_SOURCE","anchors":["decimal_places_ties_even"]},
        {"claim":"For grid output kq, inverse endpoints are both included for even k and both excluded for odd k.","class":"LOCAL_EXACT_DERIVATION","evidence":"derivation.md"},
        {"claim":"Off-grid lexical values cannot be outputs of the stated map; inverse construction is withheld without choosing a normalization policy.","class":"LOCAL_TARGET_DISTINCTION","evidence":"fixtures.json"},
    ]})
    write("backward-snowball-ledger.json", {"scope":"Accuracy/rounding prerequisites","leads":[
        {"source":"IEEE nearest/ties-even","status":"Retained XBRL definition explicitly states rule; no general IEEE arithmetic implementation or conformance claim"},
        {"source":"XSD integer/nonNegativeInteger unions","status":"Retained schema and bounded lexical rules inspected; whitespace-bearing INF union forms outside local profile"},
        {"source":"Precision inference and V-Equals/calculation links","status":"Relevant distinction read; no actual precision attributes; broader use not implemented"},
    ]})
    write("forward-snowball-ledger.json", {"new_queries":0,"scope":"Retained corrected specification",
        "status":"No claim about later calculation specifications or current installed rounding behavior"})
    write("citation-venue-ledger.json", {"sources":[
        {"title":"XBRL2.1","version":"2003-12-31 with2013-02-20 corrections"},
        {"title":"XML Schema Part2:Datatypes","version":"Second Edition2004-10-28"}],
        "citation_metrics":"not applicable"})
    write("omission-risk-ledger.json", {"risks":[
        {"risk":"Accuracy set promoted to economic truth","response":"Source assertion and conditional mathematical map have separate fields; financial admission remains false"},
        {"risk":"Generic half-open interval applied to ties-even","response":"Parity-derived endpoints and exact Decimal/rational cross-checks"},
        {"risk":"Off-grid digits silently rounded","response":"Explicit inverse-withheld status and source-table witnesses"},
        {"risk":"decimals used as multiplier","response":"Reported rational remains unchanged; step stored separately"},
        {"risk":"Nil numeric converted to zero","response":"No numeric inverse for nil; both actual nils retain distinct records"},
    ]})
    print(json.dumps({"constructed":True,"facts":len(rows),"finite_grid_preimages":len(finite),
                      "off_grid_facts":offgrid,"metadata_fixtures":len(meta),"rounding_fixtures":len(rounding),
                      "anchors":len(anchors),"bindings":len(inputs)}))


if __name__ == "__main__":
    main()
