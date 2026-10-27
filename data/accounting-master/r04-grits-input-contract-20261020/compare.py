"""Source-only input-domain checks and local mathematical illustrations."""
import ast
import copy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
METRIC=R/'data/accounting-master/r04-pubtablesv2-20261019/sources/05-metric.py'
CONVERSION=R/'data/accounting-master/r04-pubtablesv2-20261019/sources/06-conversion.py'
BBOX=R/'data/accounting-master/r04-grits-geometry-20261020/sources/02-bbox.body'

def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def area(b): return (b[2]-b[0])*(b[3]-b[1])

def local_float_iou(a,b):
    # Deliberately local transcription of the inspected elementary expressions.
    # No downloaded function, NumPy, SciPy or binding is imported or executed.
    if a[0]>a[2] or a[1]>a[3] or b[0]>b[2] or b[1]>b[3]:
        return {'constructor':'reversed_axes'}
    widths=[]
    for k in (0,1):
        widths.append(min(a[k+2],b[k+2])-max(a[k],b[k])
                      if a[k]<=b[k+2] and b[k]<=a[k+2] else 0.0)
    inter=widths[0]*widths[1]
    aa,ab=area(a),area(b)
    if inter==0:
        return {'constructor':'accepted','area_a':repr(aa),'area_b':repr(ab),
                'intersection':repr(inter),'union':'not computed','score':'0.0'}
    union=aa+ab-inter
    return {'constructor':'accepted','area_a':repr(aa),'area_b':repr(ab),
            'intersection':repr(inter),'union':repr(union),'score':repr(inter/union)}

def exact_iou(a,b):
    if not all(math.isfinite(x) for x in (*a,*b)):
        return 'undefined_nonfinite_coordinates'
    if a[0]>a[2] or a[1]>a[3] or b[0]>b[2] or b[1]>b[3]:
        return 'undefined_reversed_axes'
    a,b=tuple(map(Fraction,a)),tuple(map(Fraction,b))
    # Exact interval intersection independent of the conditional float helper.
    ix=max(Fraction(0),min(a[2],b[2])-max(a[0],b[0]))
    iy=max(Fraction(0),min(a[3],b[3])-max(a[1],b[1]))
    inter=ix*iy; union=area(a)+area(b)-inter
    return str(inter/union) if union else 'zero_area_convention_required'

def geometry_examples():
    unit=(0.,0.,1.,1.)
    cases=[('unit_identical',unit,unit),
        ('zero_area',(0.,0.,0.,1.),(0.,0.,0.,1.)),
        ('reversed',(2.,0.,1.,1.),unit),
        ('nan_x0',(float('nan'),0.,1.,1.),unit),
        ('infinite_x1',(0.,0.,float('inf'),1.),(0.,0.,float('inf'),1.)),
        ('width_overflow',(-1e308,0.,1e308,1.),(-1e308,0.,1e308,1.)),
        ('area_overflow',(0.,0.,1e200,1e200),(0.,0.,1e200,1e200)),
        ('union_overflow',(0.,0.,1e154,1e154),(0.,0.,1e154,1e154)),
        ('area_underflow',(0.,0.,1e-200,1e-200),(0.,0.,1e-200,1e-200))]
    return [{'id':name,'a':[repr(x) for x in a],'b':[repr(x) for x in b],
        'finite_inputs':all(math.isfinite(x) for x in (*a,*b)),
        'local_float':local_float_iou(a,b),'exact_stored_float_comparator':exact_iou(a,b)} for name,a,b in cases]

def precondition_decision(cells,rows,cols):
    # Small proposed-profile oracle, not an AccDSL runtime or complete adapter.
    if type(rows) is not int or type(cols) is not int or rows<0 or cols<0:
        return 'invalid_span'
    occupied=set()
    for c in cells:
        for k,bound in [('row_nums',rows),('column_nums',cols)]:
            xs=c.get(k)
            if type(xs) is not list or not xs or any(type(x) is not int or x<0 or x>=bound for x in xs):
                return 'invalid_span'
            if xs!=list(range(min(xs),max(xs)+1)):
                return 'invalid_span'
        if 'cell_text' not in c:
            return 'input_unresolved'
        t=c['cell_text']
        if type(t) is not str:
            return 'invalid_text'
        try: t.encode('utf-8','strict')
        except UnicodeEncodeError: return 'invalid_text'
        for rr in c['row_nums']:
            for cc in c['column_nums']:
                if (rr,cc) in occupied: return 'overlapping_cells'
                occupied.add((rr,cc))
    if len(occupied)!=rows*cols:
        return 'input_unresolved'
    return 'selected_preconditions_pass'

def input_fixtures():
    def c(text='A',rows=None,cols=None):
        return {'row_nums':[0] if rows is None else rows,'column_nums':[0] if cols is None else cols,'cell_text':text}
    missing=c();del missing['cell_text']
    return [
        {'id':'explicit_blank','cells':[c('')],'rows':1,'cols':1,'expected':'selected_preconditions_pass'},
        {'id':'embedded_nul','cells':[c('A\0B')],'rows':1,'cols':1,'expected':'selected_preconditions_pass'},
        {'id':'missing_text','cells':[missing],'rows':1,'cols':1,'expected':'input_unresolved'},
        {'id':'null_text','cells':[c(None)],'rows':1,'cols':1,'expected':'invalid_text'},
        {'id':'surrogate_text','cells':[c('\ud800')],'rows':1,'cols':1,'expected':'invalid_text'},
        {'id':'overlap','cells':[c('A'),c('B')],'rows':1,'cols':1,'expected':'overlapping_cells'},
        {'id':'negative_index','cells':[c(rows=[-1,0])],'rows':1,'cols':1,'expected':'invalid_span'},
        {'id':'duplicate_index','cells':[c(rows=[0,0])],'rows':1,'cols':1,'expected':'invalid_span'},
        {'id':'disjoint_index','cells':[c(rows=[0,2])],'rows':3,'cols':1,'expected':'invalid_span'},
        {'id':'empty_index','cells':[c(rows=[])],'rows':1,'cols':1,'expected':'invalid_span'},
        {'id':'boolean_index','cells':[c(rows=[True])],'rows':2,'cols':1,'expected':'invalid_span'},
        {'id':'unknown_hole','cells':[c()],'rows':1,'cols':2,'expected':'input_unresolved'},
        {'id':'empty_declared_grid','cells':[],'rows':0,'cols':0,'expected':'selected_preconditions_pass'},
        {'id':'merged_cell','cells':[c(rows=[0,1],cols=[0,1])],'rows':2,'cols':2,'expected':'selected_preconditions_pass'},
    ]

SUMMARY={
    'ragged_row_check_present':True,'cell_text_runtime_type_guard_present':False,
    'bbox_finiteness_guard_present':False,'finite_endpoints_sufficient':False,
    'overlap_overwrites_existing_slot':True,'missing_text_defaults_to_empty':True,
    'multi_metric_commit_atomic_in_inspected_method':False,
    'all_input_profiles_invalid':False,'adapter_implemented_or_default':False,
    'installed_runtime_validated':False,
}

def validate_summary(value): assert value==SUMMARY,'unsupported source conclusion'

def check():
    count=0
    def need(ok,label):
        nonlocal count
        assert ok,label
        count+=1
    source=load(U/'source-ledger.json')
    need(source['new_acquisitions']==0,'no downloads')
    for b in source['bindings']: need(sha(R/b['path'])==b['sha256'],'retained source identity')
    for a in source['anchors']:
        p=R/a['path'];need(sha(p)==a['sha256'],'anchored file')
        need('\n'.join(p.read_text().splitlines()[a['first_line']-1:a['last_line']])==a['excerpt'],'anchor text')
    tree=ast.parse(CONVERSION.read_text());t=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='TableCell')
    need(not any(isinstance(n,ast.FunctionDef) and n.name=='__post_init__' for n in t.body),'no cell post-init guard')
    f=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='from_dict')
    need(len(f.body)==2 and isinstance(f.body[-1],ast.Return),'direct constructor return')
    need("cell_text=d.get('cell_text', '')" in ast.unparse(f),'missing text default')
    btree=ast.parse(BBOX.read_text());bc=next(n for n in btree.body if isinstance(n,ast.ClassDef) and n.name=='BBox')
    post=next(n for n in bc.body if isinstance(n,ast.FunctionDef) and n.name=='__post_init__')
    need([type(n).__name__ for n in post.body]==['Expr','If','If'],'bbox has exactly two checks')
    need([ast.unparse(n.test) for n in post.body[1:]]==['self.x0 > self.x1','self.y0 > self.y1'],'only reversed checks')
    mtree=ast.parse(METRIC.read_text());functions={n.name:n for n in mtree.body if isinstance(n,ast.FunctionDef)}
    need('grid must have the same number of columns' in ast.unparse(functions['_get_n_cols']),'ragged check exists')
    need('isfinite' not in ast.unparse(functions['iou']),'no IoU finite check')
    need('dtype=object' in ast.unparse(functions['grits_con_matching']),'object text grid')
    geometry=geometry_examples();need(geometry==load(U/'geometry-examples.json'),'geometry artifact')
    g={r['id']:r for r in geometry}
    need(g['unit_identical']['local_float']['score']=='1.0','unit sanity')
    need(g['reversed']['local_float']['constructor']=='reversed_axes','reversed rejection')
    need(g['nan_x0']['local_float']['score']=='0.0','NaN masked as zero in local scalar expression')
    for name in ['infinite_x1','width_overflow','area_overflow']:
        need(g[name]['local_float']['score']=='nan',name)
    for name in ['width_overflow','area_overflow','union_overflow','area_underflow']:
        need(g[name]['finite_inputs'],name+' finite endpoints')
        need(g[name]['exact_stored_float_comparator']=='1',name+' exact identical boxes')
    need(g['union_overflow']['local_float']['score']=='0.0','finite area union overflow masks as zero')
    need(g['area_underflow']['local_float']['score']=='0.0','area underflow masks as zero')
    fixtures=load(U/'input-fixtures.json');need(fixtures==input_fixtures(),'fixture identity')
    for f in fixtures:
        need(precondition_decision(f['cells'],f['rows'],f['cols'])==f['expected'],f['id'])
    need(precondition_decision([{'row_nums':[0],'column_nums':[0],'cell_text':b'X'}],1,1)=='invalid_text','bytes rejected')
    contract=load(U/'contract.json')
    need(contract['status']=='proposed_optional_profile' and contract['default_selected'] is False,'proposal only')
    need(contract['budgets']=='unselected' and contract['normalization']=='unselected','no silent defaults')
    need(contract['failure_scores_assigned'] is False and contract['whole_rows_closed']==0,'no fabricated scores')
    validate_summary(load(U/'claim-support-ledger.json')['summary'])
    rejected=[]
    for key in SUMMARY:
        bad=copy.deepcopy(SUMMARY);bad[key]=not bad[key]
        try:validate_summary(bad)
        except AssertionError: rejected.append(key)
    need(len(rejected)==len(SUMMARY),'altered claims rejected')
    for name in ['source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omission-risk']:
        need((U/(name+'-ledger.json')).is_file(),'six ledgers')
    return {'assertions':count,'anchors':len(source['anchors']),'retained_source_files':3,
            'new_acquisitions':0,'geometry_cases':len(geometry),'input_fixtures':len(fixtures),
            'extra_bytes_precondition':1,'altered_controls_rejected':len(rejected),
            'upstream_executed':False,'whole_rows_closed':0}
