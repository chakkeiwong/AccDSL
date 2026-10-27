"""One-time construction of the retained context/fact evidence."""
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
    assert not (U/"dimensional-facts.json").exists()
    spec=importlib.util.spec_from_file_location("dimension_fact_records",U/"compare.py")
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    result=m.derive()
    fixtures=m.fixture_checks()
    source=B/"r06-enumeration-domain-20261020/sources/02-dimensions.visible.txt"
    sections=[
        ("closed_container_wording",629,695),
        ("role_partition_transitions",699,813),
        ("explicit_declarations_domain",919,976),
        ("usable_members",977,1026),
        ("primary_inheritance",1027,1102),
        ("default_members",1103,1190),
        ("fact_roles_conjunction",1191,1265),
        ("hypercube_and_context_rules",1266,1377),
        ("typed_content_and_explicit_values",1498,1654),
    ]
    anchors=[{"id":ident,"source":m.bind(source),"first_line":start,"last_line":end,
              "excerpt":"\n".join(source.read_text().splitlines()[start-1:end])}
             for ident,start,end in sections]
    inputs={R/x["retained_path"] for x in m.load(m.n.MAP)}
    inputs.update([m.n.MAP,m.NETWORK,m.TYPED,m.t.PACKET,m.t.PORTABLE,m.m.COVERAGE,m.m.INSTANCE,source,
        B/"r06-enumeration-domain-20261020/sources/02-dimensions.body",
        B/"r06-dimensional-network-20261020/compare.py",
        B/"r06-typed-domain-dates-20261020/compare.py",
        B/"r06-numeric-lexical-20261020/compare.py",
        B/"r06-text-semantics-20261020/compare.py",
        B/"r06-context-periods-20261020/compare.py"])
    write("dimensional-facts.json",result)
    write("fixture-results.json",fixtures)
    write("source-ledger.json",{"bindings":[m.bind(p) for p in sorted(inputs)],"anchors":anchors,
        "new_acquisitions":0,"source_scope":"Corrected Dimensions1.0, retained source network and original contexts",
        "unresolved_general_policy":"selected-container versus both-container closure; actual outcomes agree"})
    contexts={c["context_id"]:c for c in result["contexts"]}
    mixed=[f for f in result["facts"] if any(f["role_outcomes"].values()) and not all(f["role_outcomes"].values())]
    counts={
        "dimensioned_contexts":sum(bool(c["dimensions"]) for c in result["contexts"]),
        "scenario_containers":sum("scenario" in c["containers"] for c in result["contexts"]),
        "fact_statuses":dict(Counter(f["status"] for f in result["facts"])),
        "no_cube_facts_with_dimensions":sum(bool(contexts[f["context_id"]]["dimensions"]) for f in result["facts"]
            if f["status"]=="no_applicable_hypercube_in_retained_network"),
        "direct_cube_joins":sum(not x["inheritance_path"] for f in result["facts"] for x in f["applicable_hypercubes"]),
        "inherited_cube_joins":sum(bool(x["inheritance_path"]) for f in result["facts"] for x in f["applicable_hypercubes"]),
        "failed_alternative_roles":sum(not v for f in result["facts"] for v in f["role_outcomes"].values()),
        "dimension_check_value_sources":dict(Counter(d["value_source"] for f in result["facts"]
            for rs in f["role_checks"].values() for c in rs for d in c["dimension_checks"])),
    }
    write("descriptive-inventory.json",{"role":"explanatory_only",**counts,
        "mixed_role_witnesses":[{"fact_id":f["fact_id"],"concept":f["concept"],"context_id":f["context_id"],
                                 "role_outcomes":f["role_outcomes"]} for f in mixed[:5]],
        "counts_are_not":"whole-filing acceptance or installed validator output"})
    write("acquisitions.json",{"new_acquisitions":0,
        "reused":m.bind(B/"r06-enumeration-domain-20261020/acquisitions.json")})
    write("source-support-ledger.json",{"classification":"PRIMARY_SPECIFICATION_AND_RETAINED_INSTANCE",
        "identity":"source-ledger.json","read_scope":"Nine technical spans; inherited network and typed-content evidence",
        "allowed":"Scoped dimensional context and fact applicability in the retained network",
        "forbidden":["generic closure policy","full schema validity","installed DTS equality","financial-dimensional mapping"]})
    write("claim-support-ledger.json",{"claims":[
        {"claim":"Inherited hypercubes preserve origin role, DRS and context attributes.",
         "class":"SOURCE","anchors":["primary_inheritance"]},
        {"claim":"Hypercubes conjoin within a role; one valid applicable role suffices.",
         "class":"SOURCE","anchors":["fact_roles_conjunction"]},
        {"claim":"Default reporting and repeated dimensions are context errors.",
         "class":"SOURCE","anchors":["default_members","hypercube_and_context_rules"]},
        {"claim":"An explicit member must belong to this dimension's role-specific domain.",
         "class":"SOURCE","anchors":["explicit_declarations_domain","role_partition_transitions"]},
        {"claim":"All actual closure outcomes agree under two readings; a cross-container fixture differs.",
         "class":"FINITE_OBSERVATION_AND_AUTHORED_DISCRIMINATOR","evidence":["dimensional-facts.json","fixture-results.json"]},
    ]})
    write("backward-snowball-ledger.json",{"leads":[
        {"source":"Dimensions2.3.3 closure definitions","status":"Wording tension retained; general cross-container policy unresolved"},
        {"source":"Dimensions2.4/2.6 role-directed inheritance","status":"Inspected; origin-role witness and actual paths preserved"},
        {"source":"XML Schema typed content","status":"Inherited finite date evidence only; full schema not_run"}]})
    write("forward-snowball-ledger.json",{"queries":0,
        "scope":"No claim about later errata or installed dimensional validator behavior"})
    write("citation-venue-ledger.json",{"source":"XBRL Dimensions1.0",
        "version":"2006-09-18 corrected2012-01-25","citation_metrics":"not applicable"})
    write("omission-risk-ledger.json",{"risks":[
        {"risk":"Direct-only checking misses every actual applicable cube join",
         "response":"965 inherited joins retain paths; direct join count is zero"},
        {"risk":"One failed role interpreted as fact failure",
         "response":"All role outcomes retained and conjoined/disjoined at the stated levels"},
        {"risk":"No applicable cube called fully validated",
         "response":"Separate status for all 421 such facts; none has context dimensions"},
        {"risk":"Silent closure interpretation",
         "response":"Actual dual-reading agreement and synthetic difference"},
        {"risk":"Financial meaning inferred from a dimension QName",
         "response":"All original financial Unknowns and source Values preserved"}]})
    print(json.dumps({"constructed":True,"fixtures":len(fixtures),"anchors":len(anchors),
        "bindings":len(inputs),"fact_statuses":counts["fact_statuses"],
        "cube_joins":counts["inherited_cube_joins"],"failed_alternative_roles":counts["failed_alternative_roles"]}))


if __name__=="__main__":
    main()
