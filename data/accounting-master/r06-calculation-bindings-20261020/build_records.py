"""One-time construction of retained calculation evidence."""
from collections import Counter
import importlib.util
import json
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
B=R/"data/accounting-master"


def write(name,value):
    with (U/name).open("x",encoding="utf-8") as f:
        json.dump(value,f,indent=2)
        f.write("\n")


def main():
    assert not (U/"calculation-bindings.json").exists()
    spec=importlib.util.spec_from_file_location("calculation_records",U/"compare.py")
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    result=m.derive();fixtures=m.fixture_checks()
    xbrl=B/"r06-enumeration-domain-20261020/sources/03-xbrl21.visible.txt"
    schema=B/"taxonomy-reuse-20261007/sources/import-04-trusted.body"
    sections=[
        ("relationship_equivalence_and_priority",xbrl,1885,1995),
        ("rounding_definition",xbrl,2871,2976),
        ("duplicate_item_identity",xbrl,3855,3900),
        ("balance_weight_constraints",xbrl,4566,4590),
        ("calculation_bindings_rounding",xbrl,5907,5998),
        ("roles_weights_ancestry",xbrl,6015,6088),
        ("calculation_arc_schema",schema,108,124),
    ]
    anchors=[{"id":ident,"source":m.bind(path),"first_line":start,"last_line":end,
        "excerpt":"\n".join(path.read_text().splitlines()[start-1:end])}
        for ident,path,start,end in sections]
    inputs={R/r["retained_path"] for r in m.load(m.n.MAP)}
    inputs.update([m.n.MAP,m.DUPLICATES,m.ACCURACY,m.m.COVERAGE,m.m.INSTANCE,xbrl,schema,
        B/"r06-enumeration-domain-20261020/sources/03-xbrl21.body",
        B/"r06-dimensional-network-20261020/compare.py",
        B/"r06-typed-domain-dates-20261020/compare.py",
        B/"r06-numeric-lexical-20261020/compare.py",
        B/"r06-numeric-accuracy-20261020/compare.py"])
    write("calculation-bindings.json",result)
    write("fixture-results.json",fixtures)
    write("source-ledger.json",{"bindings":[m.bind(p) for p in sorted(inputs)],"anchors":anchors,
        "new_acquisitions":0,"comparator":"Retained summation-item arcrole, XBRL2.1 corrected2013",
        "scope":"Exact source relationships, binding exclusions and rounded sums; no installed validator"})
    rows=result["calculation_candidates"];bound=[r for r in rows if r["binds"]]
    write("descriptive-inventory.json",{"role":"explanatory_only",
        "candidates":len(rows),"bound":len(bound),"nonbinding":len(rows)-len(bound),
        "consistent_bound":sum(r["arithmetic"]["consistent"] for r in bound),
        "inconsistent_bound":sum(not r["arithmetic"]["consistent"] for r in bound),
        "nonbinding_reason_counts":dict(Counter(x for r in rows for x in r["nonbinding_reasons"])),
        "reason_combinations":dict(Counter(" + ".join(r["nonbinding_reasons"]) for r in rows if not r["binds"])),
        "weights":dict(Counter(str(m.fraction(r["weight"])) for r in result["network"]["raw_arcs"])),
        "balance_checks":dict(Counter(r["balance_weight_check"] for r in result["network"]["raw_arcs"])),
        "bound_with_missing_edges":sum(bool(r["unreported_concept_edges"]) for r in bound),
        "nil_contributor_occurrences":sum(len(r["nil_contributors"]) for r in rows),
        "not_concluded":"Counts measure source-rule applicability; nonbinding cases are not calculation passes, and passing arithmetic is not complete financial validation."})
    write("acquisitions.json",{"new_acquisitions":0,
        "reused":m.bind(B/"r06-enumeration-domain-20261020/acquisitions.json")})
    write("source-support-ledger.json",{"classification":"PRIMARY_SPECIFICATION_AND_RETAINED_INSTANCE",
        "identity":"source-ledger.json","technical_read":"Seven relationship, rounding, binding and schema spans",
        "allowed":"Finite XBRL2.1 binding and calculation consistency under the retained resources",
        "forbidden":["later calculation-specification semantics","installed validator conformity","accounting correctness","disclosure completeness"]})
    write("claim-support-ledger.json",{"claims":[
        {"claim":"Calculation relationships remain separated by extended-link role.",
         "class":"SOURCE","anchors":["roles_weights_ancestry"]},
        {"claim":"A binding needs a nonnil, nonduplicate summation and at least one nonnil contributor with no duplicate contributors.",
         "class":"SOURCE","anchors":["calculation_bindings_rounding"]},
        {"claim":"Round each contribution before applying weight, then round the sum to the summation's decimals.",
         "class":"SOURCE","anchors":["calculation_bindings_rounding","rounding_definition"]},
        {"claim":"All110 binding candidates agree under the two arithmetic implementations;164 candidates do not bind.",
         "class":"FINITE_EXACT_RESULT","evidence":"calculation-bindings.json"},
        {"claim":"Matching balance signs require positive weights; opposite signs require negative weights where both balances are declared.",
         "class":"SOURCE","anchors":["balance_weight_constraints"]}]})
    write("backward-snowball-ledger.json",{"leads":[
        {"source":"XBRL2.1 3.5.3.9.7","disposition":"Inspected source relationship identity; actual arcs optional/priority zero"},
        {"source":"XBRL2.1 4.6.7","disposition":"Inspected corrected nearest/ties-even definition; exact/Decimal arithmetic checks"},
        {"source":"XBRL2.1 4.10","disposition":"Duplicate identity already checked; no generic V-Equals assumption used"}]})
    write("forward-snowball-ledger.json",{"queries":0,
        "scope":"Later calculation specifications not adopted; distinct primary clarification remains ready work"})
    write("citation-venue-ledger.json",{"source":"XBRL2.1",
        "version":"2003-12-31 corrected2013-02-20","citation_metrics":"not applicable"})
    write("omission-risk-ledger.json",{"risks":[
        {"risk":"164 nonbinding cases counted as successful calculations","response":"Separate outcomes and complete exclusion reasons"},
        {"risk":"Agreeing duplicates collapsed","response":"Source duplicate flags enforce binding exclusion without deduplication"},
        {"risk":"Different role decompositions summed together","response":"23 source roles retained; discriminating fixture"},
        {"risk":"Round after weighting","response":"0.5 at decimals0 times3 fixture separates operation order"},
        {"risk":"Passing arithmetic interpreted as financial validity","response":"Source-specific arithmetic only; full schema/DTS and financial admission withheld"}]})
    print(json.dumps({"constructed":True,"arcs":len(result["network"]["raw_arcs"]),"candidates":len(rows),
        "bound":len(bound),"anchors":len(anchors),"bindings":len(inputs),"fixtures":len(fixtures)}))


if __name__=="__main__":
    main()
