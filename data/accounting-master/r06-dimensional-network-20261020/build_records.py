"""One-time construction; retained primary specifications only."""
from collections import Counter
import importlib.util
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / "data/accounting-master"


def write(name, value):
    with (U / name).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    assert not (U / "network.json").exists(), "one-time construction"
    spec = importlib.util.spec_from_file_location("dimension_comparison", U / "compare.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    network = m.derive()
    fixtures = m.fixture_checks()
    xbrl = B / "r06-enumeration-domain-20261020/sources/03-xbrl21.visible.txt"
    dims = B / "r06-enumeration-domain-20261020/sources/02-dimensions.visible.txt"
    xl = B / "taxonomy-reuse-20261007/sources/dep-53c316b3dbf3-trusted.body"
    link = B / "taxonomy-reuse-20261007/sources/import-04-trusted.body"
    dt = B / "taxonomy-reuse-20261007/sources/import-07-trusted.body"
    sections = [
        ("base_set_equivalence_priority", xbrl, 1885, 1995),
        ("order_semantics", xbrl, 1848, 1866),
        ("node_identity_and_typed_equality", xbrl, 3646, 3703),
        ("arc_schema_attributes", xl, 132, 160),
        ("definition_arc_type", link, 77, 84),
        ("dimension_schema_attributes", dt, 36, 50),
        ("dimension_hypercube_endpoint_rules", dims, 550, 607),
        ("has_hypercube_context_closed", dims, 629, 698),
        ("target_role_and_cycles", dims, 699, 813),
        ("domains_usable_inheritance", dims, 959, 1102),
        ("global_default_rules", dims, 1143, 1190),
        ("fact_hypercube_scope", dims, 1191, 1225),
        ("context_dimension_constraints", dims, 1320, 1377),
    ]
    anchors = [{"id": ident, "source": m.bind(path), "first_line": start, "last_line": end,
                "excerpt": "\n".join(path.read_text().splitlines()[start-1:end])}
               for ident,path,start,end in sections]
    inputs = {R / row["retained_path"] for row in m.load(m.MAP)}
    inputs.update([m.MAP, xbrl, dims, xl, link, dt,
                   B / "r06-enumeration-domain-20261020/sources/03-xbrl21.body",
                   B / "r06-enumeration-domain-20261020/sources/02-dimensions.body",
                   B / "r06-enumeration-domain-20261020/network.json",
                   B / "r06-numeric-lexical-20261020/compare.py"])
    write("network.json", network)
    write("fixture-results.json", fixtures)
    write("source-ledger.json", {"bindings":[m.bind(p) for p in sorted(inputs)],
        "anchors":anchors, "source_scope":"Retained corrected XBRL2.1/Dimensions1.0 and actual schema declarations",
        "no_generic_PSVi_claim":True, "new_acquisitions":0})
    write("acquisitions.json", {"new_acquisitions":0,
        "retained_receipts":m.bind(B / "r06-enumeration-domain-20261020/acquisitions.json")})
    write("descriptive-inventory.json", {
        "role":"explanatory_only",
        "arcrole_counts":dict(Counter(a["interpreted"]["arcrole"] for a in network["raw_arcs"])),
        "priority_counts":dict(Counter(str(a["interpreted"]["priority"]) for a in network["raw_arcs"])),
        "use_counts":dict(Counter(a["interpreted"]["use"] for a in network["raw_arcs"])),
        "unique_roles":len({a["role"] for a in network["raw_arcs"]}),
        "same_base_endpoint_collisions":len(network["same_base_and_endpoint_groups"]),
        "nonempty_target_transitions":sum(bool(t["next_arcs"]) for t in network["target_role_transitions"]),
        "not_concluded":"Raw link inventory is neither installed DTS discovery nor whole-fact validation."})
    write("source-support-ledger.json", {"classification":"PRIMARY_SPECIFICATION",
        "identity":"source-ledger.json", "technical_read":"13 selected rule and schema spans",
        "allowed":"Finite retained dimensional relationship reconstruction",
        "forbidden":["generic PSVI equivalence","installed DTS membership","whole-fact dimensional validity","financial correctness"]})
    write("claim-support-ledger.json", {"claims":[
        {"claim":"Base-set and identical endpoint boundaries precede non-exempt attribute comparison.",
         "class":"SOURCE", "anchors":["base_set_equivalence_priority","node_identity_and_typed_equality"]},
        {"claim":"The highest-priority prohibition removes the equivalence class; a lower prohibition can be overridden.",
         "class":"SOURCE", "anchors":["base_set_equivalence_priority"]},
        {"claim":"A targetRole changes the role selected for consecutive relationships.",
         "class":"SOURCE", "anchors":["target_role_and_cycles"]},
        {"claim":"An unusable member does not prune descendants; a false path excludes the member within the effective domain.",
         "class":"SOURCE", "anchors":["domains_usable_inheritance"]},
        {"claim":"Global default assignment does not create domain membership.",
         "class":"SOURCE", "anchors":["global_default_rules"]},
        {"claim":"No retained base-set/endpoint pair repeats, so actual equivalence groups are singleton before attribute comparison.",
         "class":"FINITE_SOURCE_OBSERVATION", "evidence":"network.json"},
    ]})
    write("backward-snowball-ledger.json", {"scope":"Relationship prerequisites",
        "leads":[{"source":"XBRL2.1 section4.10 and XPath1.0 numeric equality",
                  "disposition":"Retained equality definition read; order reconstruction restricted to exact integers within binary64 range"},
                 {"source":"XML Schema PSVI defaults",
                  "disposition":"Actual schema and attribute presence inspected; no same-base endpoint collisions, generic augmentation withheld"},
                 {"source":"Dimensions1.0 context/hypercube rules",
                  "disposition":"Read to delimit network prerequisite; full fact applicability is the next distinct unit"}]})
    write("forward-snowball-ledger.json", {"queries":0,
        "scope":"Retained corrected specifications; no latest-version or installed conformance claim"})
    write("citation-venue-ledger.json", {"sources":[
        {"title":"XBRL2.1","version":"2003-12-31 corrected2013-02-20"},
        {"title":"Dimensions1.0","version":"2006-09-18 corrected2012-01-25"}],
        "citation_metrics":"not applicable; primary standards"})
    write("omission-risk-ledger.json", {"risks":[
        {"risk":"Global reachability conflates roles","response":"Base-set keys and targetRole-specific consecutive transitions"},
        {"risk":"Priority suppresses unrelated relationships","response":"Only equivalent classes compete; all actual classes singleton"},
        {"risk":"PSVI support implied by parser","response":"Restricted attribute interpretation and exact source evidence; no full schema claim"},
        {"risk":"Default arc becomes domain membership","response":"Separate default and domain maps; discriminating fixture"},
        {"risk":"Network check becomes fact acceptance","response":"All fact/financial admission remains withheld"}]})
    print(json.dumps({"constructed":True,"raw_arcs":len(network["raw_arcs"]),
        "effective_arcs":len(network["effective_arc_ids"]),
        "same_base_endpoint_collisions":len(network["same_base_and_endpoint_groups"]),
        "fixtures":len(fixtures),"anchors":len(anchors),"bindings":len(inputs)}))


if __name__ == "__main__":
    main()
