"""Geometry proof witnesses and static-source checks; no acquired code execution."""
import ast
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]


def validate_box(box):
    assert len(box) == 4 and all(type(x) is int for x in box), "integer witness domain"
    assert box[0] <= box[2] and box[1] <= box[3], "ordered coordinates"


def areas(a, b):
    validate_box(a); validate_box(b)
    area = lambda r: (r[2]-r[0]) * (r[3]-r[1])
    intersection = max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))
    union = area(a)+area(b)-intersection
    # Enclosure formula applies here to two nonempty rectangles; for a single
    # empty rectangle the documented include_rect result is the other rectangle.
    if not area(a):
        enclosure = area(b)
    elif not area(b):
        enclosure = area(a)
    else:
        enclosure = (max(a[2], b[2])-min(a[0], b[0])) * (max(a[3], b[3])-min(a[1], b[1]))
    squares = lambda r: {(x,y) for x in range(r[0],r[2]) for y in range(r[1],r[3])}
    sa, sb = squares(a), squares(b)
    assert len(sa & sb) == intersection and len(sa | sb) == union
    assert 0 <= intersection <= union <= enclosure
    iou = str(Fraction(intersection, union)) if union else "undefined"
    enclosure_ratio = str(Fraction(intersection, enclosure)) if enclosure else "undefined"
    if union and enclosure:
        assert Fraction(enclosure_ratio) <= Fraction(iou)
    return {"intersection": intersection, "union": union, "enclosure": enclosure,
            "iou": iou, "intersection_over_enclosure": enclosure_ratio,
            "strict_difference": bool(intersection and enclosure > union)}


def calculate():
    cases = [
        ("offset-squares", [0,0,2,2], [1,1,3,3]),
        ("crossing", [0,1,4,2], [1,0,2,4]),
        ("topology-spans", [0,-1,1,2], [-1,0,2,1]),
        ("contained", [0,0,2,2], [0,0,1,1]),
        ("disjoint", [0,0,1,1], [2,2,3,3]),
        ("touching", [0,0,1,1], [1,0,2,1]),
        ("same-height", [0,0,2,1], [1,0,3,1]),
        ("identical", [0,0,2,2], [0,0,2,2]),
        ("zero-width", [0,0,0,1], [0,0,1,1]),
    ]
    result = [{"name": name, "a": a, "b": b, **areas(a,b)} for name,a,b in cases]
    for r in result:
        assert areas(r["b"],r["a"]) == {k:v for k,v in r.items() if k not in ("name","a","b")}
    assert sum(r["strict_difference"] for r in result) == 3
    both_empty = areas([0,0,0,0], [0,0,0,0])
    assert both_empty["iou"] == "undefined"
    return {"cases": result, "both_empty_math": both_empty,
            "source_early_zero_convention": 0,
            "upstream_executed": False, "installed_equivalence": False,
            "historical_scores_reconstructed": False}


def check():
    count = 0
    def require(value,label):
        nonlocal count
        assert value,label
        count += 1
    def load(name):
        return json.loads((UNIT/name).read_text())
    ledger=load("source-ledger.json")
    require(len(ledger["acquisitions"])==6,"six requests")
    for r in ledger["acquisitions"]:
        for field in ("body","headers","receipt"):
            item=r[field]
            require(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest()==item["sha256"],field)
        receipt=json.loads((ROOT/r["receipt"]["path"]).read_text())
        require(receipt["exitcode"]==0 and receipt["http_code"]==200,"success")
        require(receipt["size_download"]==(ROOT/r["body"]["path"]).stat().st_size,"bytes")
        require(receipt["size_download"]<2097152 and receipt["time_total"]<35,"bounds")
    for r in ledger["blob_bindings"]:
        tree=json.loads((ROOT/r["tree"]).read_text())
        entry=next(x for x in tree["tree"] if x["path"]==r["source_path"])
        body=(ROOT/r["local_path"]).read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(body)).encode()+b"\0"+body).hexdigest()
        require(blob==entry["sha"] and len(body)==entry["size"],r["source_path"])
    for r in ledger["passages"]:
        lines=(ROOT/r["path"]).read_text().splitlines()
        require(r["quote"] in lines[r["line"]-1],r["id"])
    node=ast.parse((UNIT/'sources/02-bbox.body').read_text())
    cls=next(x for x in node.body if isinstance(x,ast.ClassDef) and x.name=='BBox')
    fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='__post_init__')
    comparisons=[x for x in ast.walk(fn) if isinstance(x,ast.Compare)]
    require(len(comparisons)==2 and all(isinstance(x.ops[0],ast.Gt) for x in comparisons),'axis-order checks')
    require(not any(isinstance(x,ast.Name) and x.id=='isfinite' for x in ast.walk(fn)),'no explicit finiteness guard')
    witness=calculate()
    require(witness==load('witnesses.json'),'finite independent set oracle')
    mutations=[
        ('union substituted by enclosure',lambda w:w['cases'][0].update(union=9)),
        ('geometry difference hidden',lambda w:w['cases'][2].update(iou='1/9')),
        ('empty convention called theorem',lambda w:w['both_empty_math'].update(iou='0')),
        ('upstream execution invented',lambda w:w.update(upstream_executed=True)),
        ('installed correspondence invented',lambda w:w.update(installed_equivalence=True)),
        ('historical score repair invented',lambda w:w.update(historical_scores_reconstructed=True)),
    ]
    for label,edit in mutations:
        changed=deepcopy(witness);edit(changed);require(changed!=witness,label)
    for name in ('source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omission-risk'):
        require(bool(load(name+'-ledger.json')),name)
    return {'status':'passed','acquisitions':6,'source_anchors':len(ledger['passages']),
            'assertions':count,'rectangle_cases':len(witness['cases']),'strict_differences':3,
            'rejected_controls':len(mutations),'whole_rows_closed':0}
