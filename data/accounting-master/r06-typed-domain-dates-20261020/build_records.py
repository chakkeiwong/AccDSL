"""One-time typed-domain source record construction."""
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
    assert not (U / "declarations.json").exists()
    spec = importlib.util.spec_from_file_location("typed_domain_check", U / "compare.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    declaration, records = m.derive()
    write("declarations.json", declaration)
    write("occurrences.json", records)
    dim = B / "r06-enumeration-domain-20261020/sources/02-dimensions.visible.txt"
    xsd = B / "r06-context-periods-20261020/sources/xsd-part2.visible.txt"
    raw_schema = R / declaration["axis_anchor"]["source_path"]
    sections = [
        ("dimension_declaration", dim, 814, 847),
        ("typed_domain_reference", dim, 891, 919),
        ("typed_value_rules", dim, 1498, 1579),
        ("typed_child_erratum", dim, 2368, 2376),
        ("xsd_date_value", xsd, 1385, 1460),
        ("xsd_date_whitespace", xsd, 4958, 4978),
        ("retained_axis_and_domain", raw_schema, 15060, 15061),
    ]
    anchors = [{"id": ident, "source": m.bind(path), "first_line": first, "last_line": last,
                "excerpt": "\n".join(path.read_text().splitlines()[first-1:last])}
               for ident, path, first, last in sections]
    inputs = {m.MAP, m.PACKET, m.PORTABLE, m.m.INSTANCE, dim, xsd,
              B / "r06-enumeration-domain-20261020/sources/02-dimensions.body",
              B / "r06-unitless-semantics-20261019/sources/02-dated.body",
              B / "r06-numeric-lexical-20261020/compare.py",
              B / "r06-text-semantics-20261020/compare.py",
              B / "r06-context-periods-20261020/compare.py"}
    inputs.update(R / r["retained_path"] for r in m.load(m.MAP))
    write("source-ledger.json", {"date": "2026-10-20", "new_acquisitions": 0,
        "bindings": [m.bind(path) for path in sorted(inputs)], "anchors": anchors,
        "scope": "One unique abstract typed axis, its same-document nonabstract xs:date domain and four non-nil values",
        "limit": "Retained-map membership is checked; installed DTS/schema/hypercube validity remains not_run"})
    write("acquisitions.json", {"new_acquisitions": 0,
        "reused": [m.bind(B / "r06-enumeration-domain-20261020/acquisitions.json"),
                   m.bind(B / "r06-unitless-semantics-20261019/source-ledger.json")]})
    axis = m.AXIS_LOCAL
    domain = axis + ".domain"
    def xml(value="2024-09-29", child=None, axis_name=None, prefix="g", ns="http://fasb.org/us-gaap/2024", extra="", count=1, tail=""):
        child = child or domain
        axis_name = axis_name or axis
        return ('<i:typedMember xmlns:i="http://xbrl.org/2006/xbrldi" xmlns:' + prefix + '="' + ns
                + '" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" dimension="' + prefix + ':' + axis_name + '">'
                + ('<' + prefix + ':' + child + extra + '>' + value + '</' + prefix + ':' + child + '>') * count
                + tail + '</i:typedMember>')
    fixtures = [
        {"id": "ordinary", "xml": xml(), "expected_status": "supported", "expected_date": "2024-09-29"},
        {"id": "different_prefix_same_name", "xml": xml(prefix="tax"), "expected_status": "supported", "expected_date": "2024-09-29"},
        {"id": "whitespace", "xml": xml("\t2024-09-29\r\n"), "expected_status": "supported", "expected_date": "2024-09-29"},
        {"id": "leap", "xml": xml("2024-02-29"), "expected_status": "supported", "expected_date": "2024-02-29"},
        {"id": "invalid_leap", "xml": xml("2023-02-29"), "expected_status": "outside_lexical_space"},
        {"id": "year_zero", "xml": xml("0000-01-01"), "expected_status": "outside_lexical_space"},
        {"id": "wrong_child_valid_date", "xml": xml(child="OtherDate"), "expected_status": "wrong_domain_element"},
        {"id": "wrong_axis", "xml": xml(axis_name="OtherAxis"), "expected_status": "wrong_typed_axis"},
        {"id": "different_namespace", "xml": xml(ns="urn:other"), "expected_status": "wrong_typed_axis"},
        {"id": "zero_child", "xml": xml(count=0), "expected_status": "invalid_single_child_content"},
        {"id": "two_children", "xml": xml(count=2), "expected_status": "invalid_single_child_content"},
        {"id": "tail_text", "xml": xml(tail="not whitespace"), "expected_status": "invalid_single_child_content"},
        {"id": "nil_is_separate", "xml": xml("", extra=' xsi:nil="true"'), "expected_status": "outside_scope"},
        {"id": "xsi_type_is_separate", "xml": xml(extra=' xsi:type="g:OtherType"'), "expected_status": "outside_scope"},
        {"id": "complex_child", "xml": xml("<g:detail/>"), "expected_status": "outside_scope"},
        {"id": "timezone", "xml": xml("2024-09-29Z"), "expected_status": "outside_scope"},
        {"id": "datetime", "xml": xml("2024-09-29T00:00:00"), "expected_status": "outside_scope"},
        {"id": "explicit_instead_of_typed", "xml": xml().replace("typedMember", "explicitMember"), "expected_status": "outside_scope"},
    ]
    write("fixtures.json", fixtures)
    controls = [
        {"id": "nonabstract_axis", "target": "axis", "attribute": "abstract", "value": "false"},
        {"id": "ordinary_item_axis", "target": "axis", "attribute": "substitutionGroup", "value": "xbrli:item"},
        {"id": "empty_ref", "target": "axis", "attribute": m.D + "typedDomainRef", "value": ""},
        {"id": "missing_target", "target": "axis", "attribute": m.D + "typedDomainRef", "value": "#missing"},
        {"id": "external_ref_outside_scope", "target": "axis", "attribute": m.D + "typedDomainRef", "value": "other.xsd#value"},
        {"id": "xml_base_outside_scope", "target": "axis", "attribute": m.XMLBASE, "value": "https://example.org/"},
        {"id": "abstract_domain", "target": "domain", "attribute": "abstract", "value": "true"},
        {"id": "different_domain_type", "target": "domain", "attribute": "type", "value": "xs:string"},
        {"id": "fixed_value_outside_scope", "target": "domain", "attribute": "fixed", "value": "2024-01-01"},
        {"id": "ambiguous_id", "target": "domain", "duplicate": True},
    ]
    write("declaration-controls.json", controls)
    write("source-support-ledger.json", {"classification": "PRIMARY_SPECIFICATION_AND_RETAINED_DECLARATIONS",
        "identity": "source-ledger.json", "read_scope": "Seven bounded technical/erratum/declaration spans",
        "allowed": "Exact four-value typed-domain identity and finite xs:date interpretation",
        "forbidden": ["all-dimensional validity", "installed DTS admission", "forecast horizon semantics", "financial-time mapping"]})
    write("claim-support-ledger.json", {"claims": [
        {"claim": "A typed dimension uses a global element declaration and its XML instance, not an explicit member QName.",
         "class": "PRIMARY_SOURCE", "anchors": ["dimension_declaration", "typed_value_rules"]},
        {"claim": "A valid date under the wrong domain child name fails the typed-content identity rule.",
         "class": "PRIMARY_SOURCE_WITH_DISCRIMINATOR", "anchors": ["typed_value_rules", "typed_child_erratum"], "evidence": "fixtures.json"},
        {"claim": "The observed domain directly uses xs:date and is nillable but none of the four observed values is nil.",
         "class": "RETAINED_SOURCE_OBSERVATION", "anchors": ["retained_axis_and_domain"], "evidence": "occurrences.json"},
        {"claim": "The four date values receive no period-end/instant shift.",
         "class": "TYPE_AND_ROLE_DISTINCTION", "anchors": ["xsd_date_value", "retained_axis_and_domain"], "evidence": "occurrences.json"},
    ]})
    write("backward-snowball-ledger.json", {"scope": "Typed-domain normative dependencies",
        "leads": [
            {"source": "XML Schema 1.0 Second Edition", "status": "Retained date/value/whitespace rules used; full schema processor not implemented"},
            {"source": "XPointer / XML Base", "status": "Observed same-document bare ID resolved directly; all XML Base attributes absent in selected schema; broader forms refused"},
            {"source": "Dimensional relationship networks", "status": "Needed for fact dimensional validity; not supplied by a domain-value pass"},
        ]})
    write("forward-snowball-ledger.json", {"new_queries": 0, "scope": "Retained corrected Recommendation",
        "status": "Specific incorporated typed-content erratum inspected; later errata/current processor behavior unverified"})
    write("citation-venue-ledger.json", {"sources": [
        {"title": "XBRL Dimensions 1.0", "version": "2006-09-18 with 2012-01-25 corrections"},
        {"title": "XML Schema Part 2: Datatypes Second Edition", "version": "2004-10-28"},
        {"title": "US GAAP taxonomy element schema", "version": "2024 retained source"},
        ], "citation_metrics": "not applicable"})
    write("omission-risk-ledger.json", {"risks": [
        {"risk": "Valid text under wrong child name", "response": "Unique reference target and exact expanded-name checks; wrong-child fixture"},
        {"risk": "Typed date conflated with explicit QName or period instant", "response": "Preserved subtree/Unknown member QName and four separate role discriminators"},
        {"risk": "Attribute nil/type semantics silently ignored", "response": "Observed attribute-free non-nil profile only; nil/type fixtures outside scope"},
        {"risk": "Retained schema map promoted to DTS", "response": "Installed membership/hypercube/schema flags remain unverified"},
        {"risk": "Axis nillable/periodType confused with domain attributes", "response": "Dimension source says these have no significance; actual domain xs:date inspected separately"},
    ]})
    print(json.dumps({"constructed": True, "typed_values": len(records),
                      "fact_context_joins": sum(len(r["facts"]) for r in records),
                      "fixtures": len(fixtures), "declaration_controls": len(controls),
                      "anchors": len(anchors), "bindings": len(inputs)}))


if __name__ == "__main__":
    main()
