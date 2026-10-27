"""Exact authored Calculations1.1 examples under a declared source interpretation."""
from fractions import Fraction
from itertools import combinations
import hashlib
import importlib.util
import json
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
B=R/"data/accounting-master"


def load(path):
    return json.loads(path.read_text())


def bind(path):
    return {"path":str(path.relative_to(R)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}


def interval(lo,hi,lc=True,hc=True):
    lo,hi=Fraction(lo),Fraction(hi)
    if lo>hi or (lo==hi and not (lc and hc)):
        return None
    return (lo,hi,lc,hc)


def intersection(left,right):
    if left is None or right is None:
        return None
    lo,hi=max(left[0],right[0]),min(left[1],right[1])
    lc=all(x[2] for x in (left,right) if x[0]==lo)
    hc=all(x[3] for x in (left,right) if x[1]==hi)
    return interval(lo,hi,lc,hc)


def add(left,right):
    assert left is not None and right is not None
    return interval(left[0]+right[0],left[1]+right[1],left[2] and right[2],left[3] and right[3])


def scale(value,weight):
    assert value is not None
    weight=Fraction(weight)
    assert weight!=0,"calculation weights must be nonzero"
    if weight>0:
        return interval(value[0]*weight,value[1]*weight,value[2],value[3])
    return interval(value[1]*weight,value[0]*weight,value[3],value[2])


def fact(value,decimals):
    return {"value":None if value is None else Fraction(value),"decimals":decimals}


def value_interval(f,mode):
    assert mode in ("round-to-nearest","truncation")
    v,d=f["value"],f["decimals"]
    assert v is not None
    if d=="INF":
        return interval(v,v)
    assert isinstance(d,int) and abs(d)<=1000,"local exponent bound"
    q=Fraction(10)**(-d)
    if mode=="round-to-nearest":
        return interval(v-q/2,v+q/2)
    v=int(v/q)*q # Fraction.__int__ truncates towards zero.
    if v>0:
        return interval(v,v+q,True,False)
    if v<0:
        return interval(v-q,v,False,True)
    return interval(-q,q,False,False)


def excess(f):
    return f["value"] is not None and f["decimals"]!="INF" and (
        f["value"]/(Fraction(10)**(-f["decimals"]))).denominator!=1


def pair_consistent(left,right,mode):
    # Precondition: these facts have equal OIM dimensions and the same datatype.
    # Contextual reading of calc1.1 section5.4 uses OIM6.2, not its incorrect
    # duplicate-facts link target. No generic OIM processor is implemented.
    if left["value"] is None or right["value"] is None:
        return left["value"] is right["value"]
    if left["decimals"]==right["decimals"] and left["value"]!=right["value"]:
        return False
    return intersection(value_interval(left,mode),value_interval(right,mode)) is not None


def point(facts,mode):
    assert facts
    if all(f["value"] is None for f in facts):
        return {"status":"all_nil_ignored","interval":None}
    if any(not pair_consistent(l,r,mode) for l,r in combinations(facts,2)):
        return {"status":"inconsistent_duplicates","interval":None}
    if any(excess(f) for f in facts):
        return {"status":"excess_digits","interval":None}
    common=value_interval(facts[0],mode)
    for f in facts[1:]:
        common=intersection(common,value_interval(f,mode))
    assert common is not None,"pairwise intervals must share an intersection in one dimension"
    return {"status":"supported_under_contextual_reading","interval":common}


def binding(total,contributors,mode):
    # Every list is one authored OIM-aligned data point. Each contributor has
    # exactly one distinct concept; no relationship discovery happens here.
    if not any(f["value"] is not None for f in total):
        return {"status":"nonbinding_no_total"}
    nonnil=[(fs,w) for fs,w in contributors if any(f["value"] is not None for f in fs)]
    if not nonnil:
        return {"status":"nonbinding_no_contribution"}
    points=[point(total,mode)]+[point(fs,mode) for fs,w in nonnil]
    if any(p["status"]=="inconsistent_duplicates" for p in points):
        return {"status":"inconsistent_duplicates","code":
            "oime:disallowedDuplicateFacts" if mode=="round-to-nearest" else "calc11e:disallowedDuplicateFactsUsingTruncation"}
    if any(p["status"]=="excess_digits" for p in points):
        return {"status":"excess_digits","code":"calc11e:excessDigits"}
    calculated=interval(0,0)
    for p,(_,weight) in zip(points[1:],nonnil):
        calculated=add(calculated,scale(p["interval"],weight))
    shared=intersection(calculated,points[0]["interval"])
    return {"status":"consistent" if shared is not None else "inconsistent_calculation",
            "reported_interval":points[0]["interval"],"calculated_interval":calculated,"shared":shared}


def serial(value):
    if isinstance(value,Fraction):
        return {"n":str(value.numerator),"d":str(value.denominator)}
    if isinstance(value,(tuple,list)):
        return [serial(v) for v in value]
    if isinstance(value,dict):
        return {k:serial(v) for k,v in value.items()}
    return value


def examples():
    results=[]
    def expect(name,observed,expected):
        assert observed==expected,(name,observed,expected)
        results.append({"id":name,"observed":serial(observed),"expected":serial(expected)})
    nearest,trunc="round-to-nearest","truncation"
    for name,f,mode,wanted in [
        ("nearest_odd_includes_ties",fact(3,0),nearest,interval(Fraction(5,2),Fraction(7,2))),
        ("nearest_even_includes_ties",fact(2,0),nearest,interval(Fraction(3,2),Fraction(5,2))),
        ("source_5000_rounding",fact(5000,-3),nearest,interval(4500,5500)),
        ("positive_truncation",fact(5000,-3),trunc,interval(5000,6000,True,False)),
        ("negative_truncation",fact(-5000,-3),trunc,interval(-6000,-5000,False,True)),
        ("zero_truncation",fact(0,-3),trunc,interval(-1000,1000,False,False)),
        ("off_grid_positive_truncation",fact("1.9",0),trunc,interval(1,2,True,False)),
        ("off_grid_negative_truncation",fact("-1.9",0),trunc,interval(-2,-1,False,True)),
        ("off_grid_crosses_to_zero",fact("-0.9",0),trunc,interval(-1,1,False,False)),
        ("INF_singleton",fact("1.234","INF"),nearest,interval(Fraction("1.234"),Fraction("1.234"))),
    ]:
        expect(name,value_interval(f,mode),wanted)
    expect("closed_touch_overlap",intersection(interval(0,1),interval(1,2)),interval(1,1))
    expect("open_touch_disjoint",intersection(interval(0,1,True,False),interval(1,2)),None)
    expect("negative_weight_reverses_endpoints",scale(interval(1,2,True,False),-2),interval(-4,-2,False,True))
    expect("sum_open_endpoint",add(interval(0,1,False,True),interval(2,3,True,False)),interval(2,4,False,False))
    expect("same_precision_touch_is_inconsistent",pair_consistent(fact(5000,-3),fact(6000,-3),nearest),False)
    expect("source_duplicate_intersection",point([fact(5000,-3),fact(5500,-2)],nearest)["interval"],interval(5450,5500))
    expect("same_value_different_precision",pair_consistent(fact(5,0),fact(5,1),nearest),True)
    expect("same_precision_same_value",pair_consistent(fact(5,0),fact(5,0),nearest),True)
    broad,left,right=fact(5,0),fact("4.6",1),fact("5.4",1)
    expect("consistency_nontransitive",[pair_consistent(broad,left,nearest),pair_consistent(broad,right,nearest),pair_consistent(left,right,nearest)],[True,True,False])
    expect("check_every_duplicate_pair",point([broad,left,right],nearest)["status"],"inconsistent_duplicates")
    expect("all_nil_is_ignored",point([fact(None,None),fact(None,None)],nearest)["status"],"all_nil_ignored")
    expect("nil_mixed_with_value",point([fact(None,None),fact(0,0)],nearest)["status"],"inconsistent_duplicates")
    expect("excess_digits",point([fact("1.1",0)],nearest)["status"],"excess_digits")
    expect("no_excess_at_INF",excess(fact("1.1","INF")),False)
    expect("grid_value_not_excess",excess(fact(1100000,-5)),False)
    expect("inconsistent_pairs_before_excess",point([fact("1.1",0),fact("1.2",0)],nearest)["status"],"inconsistent_duplicates")
    for name,total,parts,mode,wanted in [
        ("rounded_sum_overlap",[fact(10,0)],[([fact(3,0)],1)]*3,nearest,"consistent"),
        ("rounded_sum_disjoint",[fact(20,0)],[([fact(3,0)],1)]*3,nearest,"inconsistent_calculation"),
        ("negative_contribution",[fact(-5,0)],[([fact(5,0)],-1)],nearest,"consistent"),
        ("truncation_open_touch",[fact(2,0)],[([fact(1,0)],1)],trunc,"inconsistent_calculation"),
        ("nearest_closed_touch",[fact(2,0)],[([fact(1,0)],1)],nearest,"consistent"),
        ("all_nil_total",[fact(None,None)],[([fact(1,0)],1)],nearest,"nonbinding_no_total"),
        ("all_nil_contributors",[fact(1,0)],[([fact(None,None)],1)],nearest,"nonbinding_no_contribution"),
        ("mixed_nil_total",[fact(None,None),fact(1,0)],[([fact(1,0)],1)],nearest,"inconsistent_duplicates"),
        ("mixed_nil_component",[fact(1,0)],[([fact(None,None),fact(1,0)],1)],nearest,"inconsistent_duplicates"),
        ("binding_excess_digits",[fact(1,0)],[([fact("1.1",0)],1)],nearest,"excess_digits"),
        ("consistent_duplicate_component",[fact(5500,-2)],[([fact(5000,-3),fact(5500,-2)],1)],nearest,"consistent"),
    ]:
        expect(name,binding(total,parts,mode)["status"],wanted)
    return results


def check():
    ledger=load(U/"source-ledger.json");count=0
    for b in ledger["bindings"]:
        assert bind(R/b["path"])==b
        count+=1
    for anchor in ledger["anchors"]:
        path=R/anchor["source"]["path"]
        assert bind(path)==anchor["source"]
        assert "\n".join(path.read_text().splitlines()[anchor["first_line"]-1:anchor["last_line"]])==anchor["excerpt"]
        count+=2
    actual=examples()
    assert actual==load(U/"examples.json");count+=len(actual)+1
    receipts=load(U/"acquisitions.json")["attempts"]
    for record in receipts:
        receipt=load(R/record["path"])
        for relative,expected in receipt["files"].items():
            path=U/relative
            assert path.stat().st_size==expected["bytes"] and hashlib.sha256(path.read_bytes()).hexdigest()==expected["sha256"]
            count+=1
    body=(U/"sources/02-calc11-trusted.body").read_text()
    start=body.index('<a name="calculation-1-1-consistent-duplicates">')
    end=body.index('</p>',start)
    assert '#term-duplicate-facts' in body[start:end]
    assert '#term-consistent-duplicates' not in body[start:end]
    count+=2
    assert not (U/"sources/05-schema-trusted.body").exists();count+=1
    return {"assertions":count,"exact_examples":len(actual),"source_anchors":len(ledger["anchors"]),
            "input_bindings":len(ledger["bindings"]),"acquisition_attempts":len(receipts),
            "successful_acquisitions":sum(load(R/r["path"])["exit_code"]==0 for r in receipts),
            "schema_publication_copy":"not_acquired_timeout","duplicate_crossreference":"contextual_reading_only",
            "actual_report_calc11":"not_run","rounding_policy_selected":False,
            "upstream_executed":False,"financial_admission":False,"whole_rows_closed":0}
