"""One-time duplicate-identity evidence construction."""
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
    assert not (U/"duplicate-facts.json").exists()
    spec=importlib.util.spec_from_file_location("duplicate_records",U/"compare.py")
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    result=m.derive();fixtures=m.fixture_checks()
    xbrl=B/"r06-enumeration-domain-20261020/sources/03-xbrl21.visible.txt"
    dims=B/"r06-enumeration-domain-20261020/sources/02-dimensions.visible.txt"
    sections=[
        ("node_and_structure_equality",xbrl,3641,3710),
        ("unit_context_item_equality",xbrl,3711,3808),
        ("V_Equal_wording_and_duplicate_identity",xbrl,3809,3900),
        ("calculation_binding_and_rounding",xbrl,5931,5998),
        ("dimensional_and_structural_equality",dims,1655,1681),
    ]
    anchors=[{"id":ident,"source":m.bind(path),"first_line":start,"last_line":end,
        "excerpt":"\n".join(path.read_text().splitlines()[start-1:end])}
        for ident,path,start,end in sections]
    inputs={m.PACKET,m.PERIODS,m.DIMENSIONS,m.UNITS,m.TYPES,m.NUMERIC,m.ACCURACY,m.m.INSTANCE,m.m.COVERAGE,xbrl,dims,
        B/"r06-enumeration-domain-20261020/sources/03-xbrl21.body",
        B/"r06-enumeration-domain-20261020/sources/02-dimensions.body",
        B/"r06-numeric-lexical-20261020/compare.py",
        B/"r06-context-periods-20261020/compare.py",
        B/"r06-numeric-accuracy-20261020/compare.py"}
    write("duplicate-facts.json",result)
    write("fixture-results.json",fixtures)
    write("source-ledger.json",{"bindings":[m.bind(p) for p in sorted(inputs)],"anchors":anchors,
        "new_acquisitions":0,"source_scope":"Finite duplicate identity, separate reported-value observations",
        "not_implemented":"generic S-Equals or V-Equals"})
    dup=[g for g in result["classes"] if g["is_duplicate_class"]]
    write("descriptive-inventory.json",{"role":"explanatory_only",
        "class_size_histogram":dict(Counter(str(len(g["members"])) for g in result["classes"])),
        "duplicate_classes":len(dup),"duplicate_facts":sum(len(g["members"]) for g in dup),
        "duplicate_pairs":sum(g["pair_count"] for g in dup),
        "different_reported_values":[g for g in dup if not g["reported_observations_agree"]],
        "different_decoded_spellings":[g["class_id"] for g in dup if not g["decoded_text_agrees"]],
        "coarse_rounding_witnesses":result["coarse_rounding_witnesses"],
        "not_concluded":"Duplicate identity is not an error finding; rounding compatibility is not V-Equals or deduplication authority."})
    write("acquisitions.json",{"new_acquisitions":0,
        "reused":m.bind(B/"r06-enumeration-domain-20261020/acquisitions.json")})
    write("source-support-ledger.json",{"classification":"PRIMARY_SPECIFICATION_AND_FINITE_INSTANCE",
        "identity":"source-ledger.json","technical_read":"Five equality/binding spans",
        "allowed":"Duplicate identity under this source profile; exact reported differences",
        "forbidden":["deduplication","V-Equals","financial truth","generic context equivalence"]})
    write("claim-support-ledger.json",{"claims":[
        {"claim":"Duplicate identity uses concept, parent, context and unit, not reported value.",
         "class":"SOURCE","anchors":["V_Equal_wording_and_duplicate_identity"]},
        {"claim":"Distinct necessary signatures exclude cross-ID equality in this finite source profile.",
         "class":"LOCAL_FINITE_ARGUMENT","evidence":"duplicate-facts.json"},
        {"claim":"Duplicate summations or contributing items prevent an XBRL2.1 calculation from binding.",
         "class":"SOURCE","anchors":["calculation_binding_and_rounding"]},
        {"claim":"The retained V-Equal row mixes significant-figure wording with a decimals-based N.",
         "class":"SOURCE_WORDING_OBSERVATION","anchors":["V_Equal_wording_and_duplicate_identity"]},
        {"claim":"Both differing value pairs have a finer number that rounds to the coarser one under the defined map.",
         "class":"EXACT_CONDITIONAL_DIAGNOSTIC","evidence":"duplicate-facts.json"}]})
    write("backward-snowball-ledger.json",{"leads":[
        {"source":"XBRL4.10 equality predicates","disposition":"Inspected; generic V-Equal wording ambiguity preserved"},
        {"source":"Dimensions3.2 d-equal and s-equal2","disposition":"Inspected; do not replace structural context equality by inferred dimensional equality"},
        {"source":"XBRL5.2.5.2 calculation binding","disposition":"Inspected; duplicate identity is a necessary successor input"}]})
    write("forward-snowball-ledger.json",{"queries":0,
        "scope":"Later duplicate-handling/calculation recommendations not selected or claimed"})
    write("citation-venue-ledger.json",{"sources":["XBRL2.1 corrected2013","Dimensions1.0 corrected2012"],
        "citation_metrics":"not applicable"})
    write("omission-risk-ledger.json",{"risks":[
        {"risk":"Same number used to erase duplicate occurrences","response":"All154 duplicates retained; value agreement is a separate field"},
        {"risk":"Different IDs assumed unequal","response":"193 distinct context signatures and seven distinct unit signatures checked"},
        {"risk":"Different precision mistaken for an accounting error","response":"Two exact conditional coarse-rounding witnesses; no accounting verdict"},
        {"risk":"Significant figures silently substituted for decimal places","response":"V-Equal not implemented and authored wording discriminator"},
        {"risk":"Duplicate exclusion bypassed in next calculation","response":"Per-fact duplicate flags preserved for binding checks"}]})
    print(json.dumps({"constructed":True,"duplicate_classes":len(dup),"duplicate_facts":sum(len(g["members"]) for g in dup),
        "anchors":len(anchors),"bindings":len(inputs),"fixtures":len(fixtures),
        "coarse_rounding_witnesses":result["coarse_rounding_witnesses"]}))


if __name__=="__main__":
    main()
