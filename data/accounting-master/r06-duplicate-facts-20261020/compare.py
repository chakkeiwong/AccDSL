"""Duplicate identity is separate from value agreement and V-Equals."""
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
B=R/"data/accounting-master"


def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m=imported("duplicate_source_helpers",B/"r06-numeric-lexical-20261020/compare.py")
p=imported("duplicate_span_helpers",B/"r06-context-periods-20261020/compare.py")
a=imported("duplicate_rounding_helper",B/"r06-numeric-accuracy-20261020/compare.py")
load,bind=m.load,m.bind
PACKET=B/"native-full-portable-20261018/native-packet.json"
PERIODS=B/"r06-context-periods-20261020/contexts.json"
DIMENSIONS=B/"r06-dimensional-facts-20261020/dimensional-facts.json"
UNITS=B/"r06-unit-measures-20261020/units.json"
TYPES=B/"r06-unit-measures-20261020/facts.json"
NUMERIC=B/"r06-numeric-lexical-20261020/occurrences.json"
ACCURACY=B/"r06-numeric-accuracy-20261020/occurrences.json"
X="{http://www.xbrl.org/2003/instance}"


def token(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"))


def context_signature(context,period,dimensions):
    identity=context["identifier"]
    assert identity["name"]==X+"identifier" and not identity["children"]
    pi=period["interpretation"]
    assert pi["status"]=="supported"
    if pi["form"]=="duration":
        boundaries=[pi[k]["implied_boundary"] for k in ("start","end")]
    else:
        assert pi["form"]=="instant"
        boundaries=[pi["instant"]["implied_boundary"]]
    reported=[]
    for d in dimensions["dimensions"]:
        if d["kind"]=="explicit":
            value=d["member_qname"]
        else:
            # Checked typed dates have canonical YYYY-MM-DD character content;
            # identity here comes from the preserved source subtree.
            candidates=[x for x in context["dimensions_and_qualifiers"]
                if x["container"]==d["container"] and x["reading"]["attributes"].get("dimension")==d["axis_token"]]
            assert len(candidates)==1
            child=candidates[0]["reading"]["children"][0]
            value={"element":child["name"],"text":child["text"],"attributes":child["attributes"]}
        reported.append({"container":d["container"],"kind":d["kind"],"axis":d["axis_qname"],"value":value})
    assert not dimensions["qualifiers"] and "scenario" not in dimensions["containers"]
    return {"identifier":identity["text"],"identifier_attributes":identity["attributes"],
            "period_kind":pi["form"],"implied_boundaries":boundaries,"timezone":"absent_not_inferred",
            "reported_dimensions":sorted(reported,key=token)}


def unit_signature(unit):
    value=unit["interpretation"]
    assert value["status"]=="supported"
    return value["product_signature"]


def duplicate_key(fact):
    return (fact["concept"],fact["parent_node"],fact["context_identity_class"],fact["unit_identity_class"])


def derive():
    packet=load(PACKET)
    periods={c["context_id"]:c for c in load(PERIODS)}
    dimension_contexts={c["context_id"]:c for c in load(DIMENSIONS)["contexts"]}
    signatures=[{"context_id":c["id"],"necessary_signature":context_signature(c,periods[c["id"]],dimension_contexts[c["id"]])}
                for c in packet["contexts"]]
    context_classes=defaultdict(list)
    for row in signatures:
        context_classes[token(row["necessary_signature"])].append(row["context_id"])
    collisions=[ids for ids in context_classes.values() if len(ids)>1]
    assert not collisions,"necessary context collision requires separate structural inspection"
    unit_signatures=[{"unit_id":u["unit_id"],"necessary_signature":unit_signature(u)} for u in load(UNITS)]
    unit_classes=defaultdict(list)
    for row in unit_signatures:
        unit_classes[token(row["necessary_signature"])].append(row["unit_id"])
    unit_collisions=[ids for ids in unit_classes.values() if len(ids)>1]
    assert not unit_collisions,"unit collision requires separate equality inspection"
    types={f["fact_id"]:f for f in load(TYPES)}
    numeric={f["fact_id"]:f for f in load(NUMERIC)}
    accuracy={f["fact_id"]:f for f in load(ACCURACY)}
    source=m.INSTANCE.read_bytes()
    root,scopes=m.schema(str(m.INSTANCE.relative_to(R)))
    actual={e.get("id"):e for e in root if e.get("id")}
    all_items={e.get("id") for e in root.iter() if e.get("contextRef")}
    rows=[]
    for fact in load(m.COVERAGE)["occurrences"]:
        ident=fact["fact_id"]
        node=actual[ident]
        assert node.get("contextRef")==fact["source_context_id"] and node.tag==fact["source_concept"]
        p.span_check(fact["source_span"],source)
        assert fact["source_context_id"] in periods
        numeric_kind=types[ident]["numeric"]
        assert (fact["source_unit_id"] is not None)==numeric_kind
        nil=fact["portable_candidate_value"]["tag"]=="Nil"
        if nil:
            value={"kind":"nil_observation"}
        elif numeric_kind:
            value={"kind":"exact_reported_numeric_candidate","rational":numeric[ident]["lexical"]["rational"]}
        else:
            value={"kind":"decoded_source_text","text":fact["decoded_text"]}
        row={"fact_id":ident,"concept":fact["source_concept"],"parent_node":"/1",
             "source_element_path":fact["source_span"]["element_path"],
             "context_identity_class":fact["source_context_id"],
             "unit_identity_class":fact["source_unit_id"] if numeric_kind else "all_nonnumeric",
             "numeric":numeric_kind,"nil":nil,"value_observation":value,
             "decoded_text":fact["decoded_text"],"source_accuracy":accuracy[ident]["source_accuracy"]}
        assert row["source_element_path"].count("/")==2
        rows.append(row)
    assert all_items=={r["fact_id"] for r in rows} and len(rows)==1127
    groups=defaultdict(list)
    for row in rows:
        groups[duplicate_key(row)].append(row)
    classes=[]
    rounding_witnesses={}
    for i,(key,members) in enumerate(groups.items(),1):
        cls={"class_id":"duplicate-class-%04d"%i,"concept":key[0],"parent_node":key[1],
             "context_identity_class":key[2],"unit_identity_class":key[3],
             "members":[r["fact_id"] for r in members],"is_duplicate_class":len(members)>1,
             "pair_count":len(members)*(len(members)-1)//2,
             "reported_observations_agree":len({token(r["value_observation"]) for r in members})==1,
             "decoded_text_agrees":len({r["decoded_text"] for r in members})==1,
             "source_accuracy_agrees":len({token(r["source_accuracy"]) for r in members})==1,
             "V_Equal":"not_implemented","deduplication_applied":False}
        classes.append(cls)
        for row in members:
            row["duplicate_class"]=cls["class_id"]
            row["is_duplicate"]=cls["is_duplicate_class"]
        if len(members)>1 and not cls["reported_observations_agree"]:
            for left in members:
                for right in members:
                    ld,rd=left["source_accuracy"]["decimals"],right["source_accuracy"]["decimals"]
                    if not left["numeric"] or not right["numeric"] or left["nil"] or right["nil"]:
                        continue
                    if ld in (None,"INF") or rd in (None,"INF") or int(ld)>=int(rd):
                        continue
                    lr=left["value_observation"]["rational"];rr=right["value_observation"]["rational"]
                    lv,rv=Fraction(int(lr["n"]),int(lr["d"])),Fraction(int(rr["n"]),int(rr["d"]))
                    coarse=a.round_even(rv,Fraction(10)**(-int(ld)))
                    key=(cls["class_id"],token(lr),token(rr),ld,rd)
                    rounding_witnesses[key]={"class_id":cls["class_id"],"coarse_reported":lr,
                        "fine_reported":rr,"coarse_decimals":ld,"fine_decimals":rd,
                        "fine_rounds_to_coarse_under_defined_map":coarse==lv,
                        "V_Equal_admitted":False,"issuer_rounding_process_verified":False}
    return {"context_signatures":signatures,"context_signature_collisions":collisions,
            "unit_signatures":unit_signatures,"unit_signature_collisions":unit_collisions,
            "facts":rows,"classes":classes,"coarse_rounding_witnesses":list(rounding_witnesses.values())}


def fixture_checks():
    results=[]
    def expect(name,value):
        assert value,name
        results.append(name)
    base={"concept":"{urn:c}amount","parent_node":"/1","context_identity_class":"c1",
          "unit_identity_class":"u1","value":"10","accuracy":"-3","nil":False,"id":"one"}
    for field,replacement in [("value","11"),("accuracy","0"),("nil",True),("id","two")]:
        expect("duplicate_ignores_"+field,duplicate_key(base)==duplicate_key(dict(base,**{field:replacement})))
    for field,replacement in [("concept","{urn:other}amount"),("parent_node","/1/tuple"),
                              ("context_identity_class","different_context"),("unit_identity_class","different_unit")]:
        expect("identity_separates_"+field,duplicate_key(base)!=duplicate_key(dict(base,**{field:replacement})))
    packet=load(PACKET)["contexts"]
    contexts={c["id"]:c for c in packet}
    periods={c["context_id"]:c for c in load(PERIODS)}
    ds={c["context_id"]:c for c in load(DIMENSIONS)["contexts"]}
    original=context_signature(contexts["c-2"],periods["c-2"],ds["c-2"])
    renamed=deepcopy(contexts["c-2"]);renamed["id"]="renamed"
    expect("context_id_not_signature",original==context_signature(renamed,periods["c-2"],ds["c-2"]))
    changed=deepcopy(ds["c-2"]);changed["dimensions"][0]["member_qname"]="{urn:other}member"
    expect("member_changes_necessary_signature",original!=context_signature(contexts["c-2"],periods["c-2"],changed))
    # A pairwise dimension key is deliberately not a generic structural comparator.
    one={"interpretation":{"status":"supported","product_signature":{"numerator":{"{urn:u}m":1},"denominator":{}}}}
    square=deepcopy(one);square["interpretation"]["product_signature"]["numerator"]["{urn:u}m"]=2
    inverse=deepcopy(one);inverse["interpretation"]["product_signature"]={"numerator":{},"denominator":{"{urn:u}m":1}}
    expect("measure_multiplicity",unit_signature(one)!=unit_signature(square))
    expect("measure_denominator",unit_signature(one)!=unit_signature(inverse))
    x,y=Fraction("1.234"),Fraction("1.235")
    places=[a.round_even(v,Fraction(1,100)) for v in (x,y)]
    figures=[a.round_even(v,Fraction(1,10)) for v in (x,y)] # Both values are in [1,10).
    expect("V_Equal_wording_discriminator",places==[Fraction("1.23"),Fraction("1.24")] and figures==[Fraction("1.2")]*2)
    return results


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
    assert result==load(U/"duplicate-facts.json")
    fixtures=fixture_checks()
    assert fixtures==load(U/"fixture-results.json")
    count+=len(fixtures)+2
    duplicates=[c for c in result["classes"] if c["is_duplicate_class"]]
    return {"assertions":count,"facts":len(result["facts"]),"context_signatures":len(result["context_signatures"]),
            "unit_signatures":len(result["unit_signatures"]),"identity_classes":len(result["classes"]),
            "duplicate_classes":len(duplicates),"duplicate_facts":sum(len(c["members"]) for c in duplicates),
            "duplicate_pairs":sum(c["pair_count"] for c in duplicates),
            "reported_observation_disagreements":sum(not c["reported_observations_agree"] for c in duplicates),
            "accuracy_disagreements":sum(not c["source_accuracy_agrees"] for c in duplicates),
            "coarse_rounding_witnesses":len(result["coarse_rounding_witnesses"]),
            "source_anchors":len(ledger["anchors"]),"input_bindings":len(ledger["bindings"]),
            "fixture_checks":len(fixtures),"new_acquisitions":0,"deduplication_applied":False,
            "V_Equal":"not_implemented","upstream_executed":False,"financial_admission":False,"whole_rows_closed":0}
