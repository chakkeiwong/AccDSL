"""Finite XBRL2.1 calculation source/binding checks using exact arithmetic."""
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
import importlib.util
from pathlib import Path
import re
from urllib.parse import urljoin, urldefrag

U=Path(__file__).resolve().parent
R=U.parents[2]
B=R/"data/accounting-master"


def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


n=imported("calculation_network_helpers",B/"r06-dimensional-network-20261020/compare.py")
t=imported("calculation_declarations",B/"r06-typed-domain-dates-20261020/compare.py")
a=imported("calculation_rounding",B/"r06-numeric-accuracy-20261020/compare.py")
m=n.m
load,bind=m.load,m.bind
XL,LINK,X=n.XL,n.LINK,n.XBRLI
ARCROLE="http://www.xbrl.org/2003/arcrole/summation-item"
DUPLICATES=B/"r06-duplicate-facts-20261020/duplicate-facts.json"
ACCURACY=B/"r06-numeric-accuracy-20261020/occurrences.json"


def decimal(raw):
    value=m.collapse(raw)
    assert re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)",value)
    return Fraction(value)


def rat(value):
    return {"n":str(value.numerator),"d":str(value.denominator)}


def fraction(value):
    return Fraction(int(value["n"]),int(value["d"]))


def balance_weight(source,target,weight):
    if source is None or target is None:
        return "not_constrained_by_two_balances"
    assert source in ("credit","debit") and target in ("credit","debit")
    return "supported" if ((weight>0)==(source==target)) else "illegal_balance_weight"


def network():
    declarations={}
    for qname,items in t.global_index().items():
        assert len(items)==1
        resource,root,scopes,e=items[0]
        if e.get("id"):
            declarations[resource["logical_uri"]+"#"+e.get("id")]={
                "qname":qname,"attributes":dict(e.attrib),
                "substitution_group":m.expanded(e.get("substitutionGroup"),scopes[id(e)]) if e.get("substitutionGroup") else None,
                "type":m.expanded(e.get("type"),scopes[id(e)]) if e.get("type") else None}
    arcs,links=[],[]
    reviewed_types={X+k for k in ("monetaryItemType","decimalItemType","integerItemType","sharesItemType","pureItemType")}
    used=set()
    for resource in load(n.MAP):
        raw=(R/resource["retained_path"]).read_bytes()
        assert m.digest(raw)==resource["expected_blob"]["digest"]
        root,scopes=m.schema(resource["retained_path"])
        assert not any(n.XML+"base" in e.attrib for e in root.iter())
        uri=resource["logical_uri"]
        for li,link in enumerate(root.iter(LINK+"calculationLink")):
            assert link.get(XL+"type")=="extended"
            labels=defaultdict(list)
            for e in link:
                if e.tag==LINK+"loc":
                    assert e.get(XL+"type")=="locator"
                    base,frag=urldefrag(urljoin(uri,e.get(XL+"href")))
                    assert re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*",frag)
                    node=base+"#"+frag
                    assert node in declarations
                    labels[e.get(XL+"label")].append(node)
            assert all(len(v)==1 for v in labels.values())
            role=link.get(XL+"role");ids=[]
            for ci,e in enumerate(link):
                if e.tag!=LINK+"calculationArc":
                    continue
                raw_attrs=dict(e.attrib)
                allowed={XL+k for k in ("type","arcrole","from","to")}|{"order","weight"}
                assert set(raw_attrs)==allowed,"outside reviewed optional/priority-zero arc profile"
                assert e.get(XL+"arcrole")==ARCROLE and e.get(XL+"type")=="arc"
                weight=decimal(e.get("weight"));order=decimal(e.get("order"))
                assert weight and order.denominator==1 and abs(order)<=2**53
                source=labels[e.get(XL+"from")][0];target=labels[e.get(XL+"to")][0]
                s,d=declarations[source],declarations[target]
                assert s["substitution_group"]==d["substitution_group"]==X+"item"
                assert s["type"] in reviewed_types and d["type"] in reviewed_types,("endpoint type",s["type"],d["type"])
                sign=balance_weight(s["attributes"].get(X+"balance"),d["attributes"].get(X+"balance"),weight)
                assert sign!="illegal_balance_weight"
                record={"id":"calc-arc-%04d"%(len(arcs)+1),"source_file":resource["retained_path"],
                    "logical_uri":uri,"link_index":li,"child_index":ci,"link_name":link.tag,"arc_name":e.tag,
                    "role":role,"source_node":source,"target_node":target,
                    "source_qname":s["qname"],"target_qname":d["qname"],"raw_attributes":raw_attrs,
                    "weight":rat(weight),"balance_weight_check":sign,
                    "interpreted":{"arcrole":ARCROLE,"priority":0,"use":"optional",
                                   "nonexempt_attributes":{"order":str(order),"weight":str(weight)}}}
                arcs.append(record);ids.append(record["id"]);used.update((source,target))
            links.append({"source_file":resource["retained_path"],"link_index":li,"role":role,"arcs":ids})
    groups,effective=n.effective(arcs)
    endpoints=defaultdict(list)
    for arc in arcs:
        endpoints[(arc["role"],arc["source_node"],arc["target_node"])].append(arc["id"])
    return {"raw_arcs":arcs,"links":links,"equivalence_groups":groups,
            "effective_arc_ids":[e["id"] for e in effective],
            "same_base_endpoint_groups":[v for v in endpoints.values() if len(v)>1],
            "endpoint_declarations":{k:declarations[k] for k in sorted(used)}}


def rounded(value,decimals):
    return value if decimals=="INF" else a.round_even(value,Fraction(10)**(-int(decimals)))


def decimal_rounded(value,decimals):
    return value if decimals=="INF" else value.quantize(Decimal(1).scaleb(-int(decimals)),rounding=ROUND_HALF_EVEN)


def calculate(total,contributions):
    target=rounded(fraction(total["rational"]),total["decimals"])
    pieces=[];summed=Fraction(0)
    for c in contributions:
        value=rounded(fraction(c["rational"]),c["decimals"])
        weighted=value*fraction(c["weight"])
        summed+=weighted
        pieces.append({**c,"rounded_value":rat(value),"weighted_value":rat(weighted)})
    rounded_sum=rounded(summed,total["decimals"])
    rationals=[fraction(total["rational"])]
    rationals.extend(fraction(c[k]) for c in contributions for k in ("rational","weight"))
    # Conservative decimal precision for exact terminating inputs/products/sum;
    # includes negative decimal exponents and a carry allowance for term count.
    digits=sum(len(str(abs(v.numerator)))+len(str(v.denominator)) for v in rationals)
    exponents=sum(abs(int(c["decimals"])) for c in [total]+contributions if c["decimals"]!="INF")
    with localcontext() as context:
        context.prec=max(80,digits+exponents+32)
        def dec(r):
            return Decimal(r["n"])/Decimal(r["d"])
        independent_target=decimal_rounded(dec(total["rational"]),total["decimals"])
        independent_sum=sum((decimal_rounded(dec(c["rational"]),c["decimals"])*dec(c["weight"]) for c in contributions),Decimal(0))
        independent_rounded_sum=decimal_rounded(independent_sum,total["decimals"])
        assert Fraction(independent_target)==target
        assert Fraction(independent_sum)==summed
        assert Fraction(independent_rounded_sum)==rounded_sum
    return {"rounded_summation":rat(target),"contributions":pieces,"weighted_sum":rat(summed),
            "sum_rounded_to_summation_decimals":rat(rounded_sum),
            "comparison_residual":rat(rounded_sum-target),"consistent":target==rounded_sum,
            "independent_Decimal_agreement":True}


def bind_candidate(total,contributors):
    reasons=[]
    if not contributors:
        reasons.append("no_nonnil_contributors")
    if total["nil"]:
        reasons.append("nil_summation")
    if total["is_duplicate"]:
        reasons.append("duplicate_summation")
    if any(c["is_duplicate"] for c in contributors):
        reasons.append("duplicate_contributor")
    return reasons


def derive():
    net=network()
    arcs=[a for a in net["raw_arcs"] if a["id"] in set(net["effective_arc_ids"])]
    groups=defaultdict(list)
    for arc in arcs:
        groups[(arc["role"],arc["source_qname"])].append(arc)
    rows=load(DUPLICATES)["facts"]
    by_concept=defaultdict(list)
    for row in rows:
        assert row["parent_node"]=="/1"
        by_concept[row["concept"]].append(row)
    candidates=[];absent_summations=[]
    for (role,concept),relations in sorted(groups.items()):
        totals=by_concept.get(concept,[])
        if not totals:
            absent_summations.append({"role":role,"concept":concept,"arc_ids":[r["id"] for r in relations]})
        for total in totals:
            assert total["numeric"]
            contributions=[];nil_contributors=[];missing=[]
            for arc in relations:
                matched=[f for f in by_concept.get(arc["target_qname"],[]) if
                         (f["context_identity_class"],f["unit_identity_class"])==
                         (total["context_identity_class"],total["unit_identity_class"])]
                if not matched:
                    missing.append({"arc":arc["id"],"concept":arc["target_qname"]})
                for f in matched:
                    assert f["numeric"]
                    if f["nil"]:
                        nil_contributors.append({"arc":arc["id"],"fact_id":f["fact_id"]})
                    else:
                        contributions.append({"fact_id":f["fact_id"],"arc_id":arc["id"],
                            "rational":f["value_observation"]["rational"],
                            "decimals":f["source_accuracy"]["decimals"],"weight":arc["weight"],
                            "is_duplicate":f["is_duplicate"]})
            reasons=bind_candidate(total,contributions)
            arithmetic=None
            if not reasons:
                arithmetic=calculate({"rational":total["value_observation"]["rational"],
                                      "decimals":total["source_accuracy"]["decimals"]},contributions)
            candidates.append({"summation_fact":total["fact_id"],"summation_concept":concept,"role":role,
                "context_id":total["context_identity_class"],"unit_id":total["unit_identity_class"],
                "arc_ids":[r["id"] for r in relations],"contributing_facts":contributions,
                "nil_contributors":nil_contributors,"unreported_concept_edges":missing,
                "nonbinding_reasons":reasons,"binds":not reasons,"arithmetic":arithmetic})
    return {"network":net,"calculation_candidates":candidates,"unreported_summation_groups":absent_summations,
            "selected_specification":"XBRL2.1 corrected2013-02-20",
            "deduplication_applied":False,"financial_admission":False}


def fixture_checks():
    done=[]
    def expect(name,value):
        assert value,name
        done.append(name)
    ordinary={"nil":False,"is_duplicate":False}
    expect("binds_with_one",not bind_candidate(ordinary,[ordinary]))
    expect("no_contributors",bind_candidate(ordinary,[])==["no_nonnil_contributors"])
    expect("nil_total",bind_candidate(dict(ordinary,nil=True),[ordinary])==["nil_summation"])
    expect("duplicate_total",bind_candidate(dict(ordinary,is_duplicate=True),[ordinary])==["duplicate_summation"])
    expect("duplicate_component_even_if_values_agree",
           bind_candidate(ordinary,[dict(ordinary,is_duplicate=True)])==["duplicate_contributor"])
    for sb,tb,w,expected in [("debit","debit",1,"supported"),("credit","credit",-1,"illegal_balance_weight"),
                             ("debit","credit",-1,"supported"),("credit","debit",1,"illegal_balance_weight"),
                             (None,"debit",-1,"not_constrained_by_two_balances")]:
        expect("balance_%s_%s_%s"%(sb,tb,w),balance_weight(sb,tb,Fraction(w))==expected)
    def value(v,d):
        return {"rational":rat(Fraction(v)),"decimals":d}
    def term(v,d,w="1"):
        return dict(value(v,d),weight=rat(Fraction(w)))
    for label,total,terms,expected in [
        ("exact_positive",value("3","INF"),[term("1","INF"),term("2","INF")],True),
        ("negative_weight",value("2","INF"),[term("5","INF"),term("3","INF","-1")],True),
        ("inconsistent",value("4","INF"),[term("1","INF"),term("2","INF")],False),
        ("own_decimals_before_sum",value("2",0),[term("1.4",0),term("1.4",0)],True),
        ("round_before_weight",value("0",0),[term("0.5",0,"3")],True),
        ("negative_tie_even",value("-2",0),[term("-2.5",0)],True),
        ("negative_tie_odd",value("-4",0),[term("-3.5",0)],True),
        ("total_rounding",value("2",0),[term("1.2",1),term("1.2",1)],True),
        ("roles_separate",value("2",0),[term("2",0)],True),
        ("roles_wrongly_merged",value("2",0),[term("2",0),term("2",0)],False),
    ]:
        expect(label,calculate(total,terms)["consistent"]==expected)
    # These examples have a third linked concept unreported. The binding rule
    # still depends on actual contributors, not an invented zero or completeness.
    expect("missing_edge_does_not_prevent_binding",not bind_candidate(ordinary,[ordinary]))
    try:
        decimal("NaN")
    except AssertionError:
        expect("nondecimal_weight_rejected",True)
    else:
        raise AssertionError("NaN accepted")
    return done


def check():
    ledger=load(U/"source-ledger.json")
    count=0
    for b in ledger["bindings"]:
        assert bind(R/b["path"])==b
        count+=1
    for s in ledger["anchors"]:
        path=R/s["source"]["path"]
        assert bind(path)==s["source"]
        assert "\n".join(path.read_text().splitlines()[s["first_line"]-1:s["last_line"]])==s["excerpt"]
        count+=2
    result=derive()
    assert result==load(U/"calculation-bindings.json")
    fixtures=fixture_checks()
    assert fixtures==load(U/"fixture-results.json")
    count+=len(fixtures)+2
    rows=result["calculation_candidates"];bound=[r for r in rows if r["binds"]]
    return {"assertions":count,"source_arcs":len(result["network"]["raw_arcs"]),
            "effective_arcs":len(result["network"]["effective_arc_ids"]),
            "calculation_links":len(result["network"]["links"]),"candidates":len(rows),"bound":len(bound),
            "nonbinding":len(rows)-len(bound),"consistent_bound":sum(r["arithmetic"]["consistent"] for r in bound),
            "inconsistent_bound":sum(not r["arithmetic"]["consistent"] for r in bound),
            "nonbinding_reason_counts":dict(Counter(reason for r in rows for reason in r["nonbinding_reasons"])),
            "unreported_summation_groups":len(result["unreported_summation_groups"]),
            "bound_with_unreported_edges":sum(bool(r["unreported_concept_edges"]) for r in bound),
            "independent_Decimal_checks":len(bound),"source_anchors":len(ledger["anchors"]),
            "input_bindings":len(ledger["bindings"]),"fixture_checks":len(fixtures),"new_acquisitions":0,
            "deduplication_applied":False,"upstream_executed":False,"financial_admission":False,"whole_rows_closed":0}
