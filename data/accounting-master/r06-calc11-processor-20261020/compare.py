"""Authored exact traces of selected inspected branches; never imports upstream."""
import ast
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2];B=R/'data/accounting-master'
SRC=B/'arelle-fact-identity-20261013/sources'
CALC=SRC/'ValidateXbrlCalcs.py';MODEL=SRC/'ModelInstanceObject.py'
s=importlib.util.spec_from_file_location('processor_math_comparator',B/'r06-calculations11-source-20261020/compare.py')
ref=importlib.util.module_from_spec(s);s.loader.exec_module(ref)
load,bind=ref.load,ref.bind

def source_range(f,mode):
    v,d=f['value'],f['decimals']
    if d=='INF':return ref.interval(v,v)
    step=Fraction(10)**(-d)
    if mode=='round-to-nearest':return ref.interval(v-step/2,v+step/2)
    if v>0:return ref.interval(v,v+step,True,False)
    if v<0:return ref.interval(v-step,v,False,True)
    return ref.interval(v-step,v+step,False,False)

def source_trace(facts,mode):
    """Hand-authored finite rational model of selected branches, not dynamic code."""
    events=[]
    if any(f['value'] is None for f in facts):
        status='all_nil_ignored' if all(f['value'] is None for f in facts) else 'inconsistent_duplicates'
        return {'status':status,'interval':None,'events':[{'nil_branch':status}]}
    a=b=None;lc=hc=False;bad=False;seen={};excess=[]
    for i,f in enumerate(facts):
        v,d=f['value'],f['decimals']
        # All witness values are finite, and Decimal values are ordinary normal
        # values or exact zero. The pinned helper bypasses d <= -28 entirely.
        ex=d!='INF' and d>-28 and ref.excess(f)
        if ex:excess.append(i);action='excess_bypasses_precision_and_range'
        elif d in seen:
            bad |= v!=seen[d];action='same_precision_updates_flag_only'
        else:
            seen[d]=v;x,y,xl,yh=source_range(f,mode)
            if a is None or x>=a:a=x;lc|=xl
            if b is None or y<=b:b=y;hc|=yh
            action='update_interval_flags_with_or'
        events.append({'fact':i,'action':action,'flag':bad,'a':a,'b':b,'lc':lc,'hc':hc})
    assert a is not None and b is not None,'witness outside nonempty retained branch'
    before=bad;bad=(a==b and not(lc and hc)) or a>b
    events.append({'action':'overwrite_inconsistent_flag','before':before,'after':bad})
    status='excess_digits' if excess else ('inconsistent_duplicates' if bad else 'supported_under_contextual_reading')
    return {'status':status,'interval':None if status!='supported_under_contextual_reading' else (a,b,lc,hc),'events':events}

def source_scale(iv,w):
    a,b=iv[0]*w,iv[1]*w
    if b<a:a,b=b,a
    return (a,b,iv[2],iv[3])

def source_overlap(x,y):
    a,b=max(x[0],y[0]),min(x[1],y[1]);lc=x[2] or y[2];hc=x[3] or y[3]
    return not((a==b and not(lc and hc)) or a>b)

def examples():
    F=ref.fact;N='round-to-nearest';T='truncation';rows=[]
    cases=[('same_precision_unequal',[F(1,0),F(3,0)],N,'supported_under_contextual_reading','inconsistent_duplicates'),
      ('same_precision_unequal_truncation',[F(1,0),F(3,0)],T,'supported_under_contextual_reading','inconsistent_duplicates'),
      ('same_precision_equal',[F(1,0),F(1,0)],N,'supported_under_contextual_reading','supported_under_contextual_reading'),
      ('closed_vs_open_exact_upper',[F(1,'INF'),F(0,0)],T,'supported_under_contextual_reading','inconsistent_duplicates'),
      ('closed_vs_open_exact_lower',[F(-1,'INF'),F(0,0)],T,'supported_under_contextual_reading','inconsistent_duplicates'),
      ('same_boundary_nearest',[F(1,'INF'),F(0,0)],N,'inconsistent_duplicates','inconsistent_duplicates'),
      ('excess_before_duplicate',[F('1.1',0),F(3,0)],N,'excess_digits','inconsistent_duplicates'),
      ('large_precision_guard',[F(1,-28)],N,'supported_under_contextual_reading','excess_digits'),
      ('ordinary_mixed_precision',[F(5000,-3),F(5500,-2)],N,'supported_under_contextual_reading','supported_under_contextual_reading'),
      ('nil_only',[F(None,None),F(None,None)],N,'all_nil_ignored','all_nil_ignored'),
      ('mixed_nil',[F(None,None),F(1,0)],N,'inconsistent_duplicates','inconsistent_duplicates')]
    for name,facts,mode,srcstatus,refstatus in cases:
        src=source_trace(facts,mode);target=ref.point(facts,mode)
        assert src['status']==srcstatus,(name,src)
        assert target['status']==refstatus,(name,target)
        rows.append({'name':name,'mode':mode,'facts':facts,'authored_source_trace':src,'target':target,
          'status_differs':srcstatus!=refstatus,'upstream_executed':False})
    iv=ref.value_interval(F(1,0),T);source=source_scale(iv,Fraction(-1));target=ref.scale(iv,-1)
    assert source==(Fraction(-2),Fraction(-1),True,False)
    assert target==(Fraction(-2),Fraction(-1),False,True)
    rows.append({'name':'negative_weight_flags','source_interval':source,'target_interval':target,'differs':True})
    total=ref.interval(2,2);computed=ref.interval(1,2,True,False)
    assert source_overlap(total,computed) and ref.intersection(total,computed) is None
    rows.append({'name':'final_open_touch','reported':total,'calculated':computed,'source_accepts':True,'target_accepts':False})
    # A forced collision demonstrates the information lost by using a hash only;
    # it is not evidence of an actual collision in the retained report.
    a=('parent',7,'USD');b=('parent',7,'USD')
    assert a==b and {'axis':'A'}!={'axis':'B'}
    rows.append({'name':'constructed_hash_collision','keys_equal':True,'underlying_contexts_equal':False,'actual_collision_observed':False})
    return ref.serial(rows)

def static_checks():
    out=[];source=CALC.read_text();tree=ast.parse(source)
    f=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='consistentFactValueInterval')
    outer=next(n for n in f.body if isinstance(n,ast.If));body=outer.orelse
    loop=next(n for n in body if isinstance(n,ast.For));after=body[body.index(loop)+1:]
    assign=next(n for n in after if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_inConsistent' for t in n.targets))
    assert not any(isinstance(n,ast.Name) and n.id=='_inConsistent' for n in ast.walk(assign.value));out.append('post_loop_assignment_discards_prior_flag')
    assert any(isinstance(n,ast.AugAssign) and isinstance(n.target,ast.Name) and n.target.id=='_inConsistent' for n in ast.walk(loop));out.append('same_precision_flag_is_set_inside_loop')
    for name in ('inclA','inclB'):
        assert any(isinstance(n,ast.AugAssign) and isinstance(n.op,ast.BitOr) and isinstance(n.target,ast.Name) and n.target.id==name for n in ast.walk(loop));out.append(name+'_OR_update')
    tests=[ast.unparse(n.test) for n in f.body if isinstance(n,ast.If)]
    assert tests.index('_excessDigitFacts')<tests.index('_inConsistent');out.append('excess_return_precedes_inconsistent_return')
    bindf=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='bindFacts')
    assignments={ast.unparse(n.targets[0]):ast.unparse(n.value) for n in ast.walk(bindf) if isinstance(n,ast.Assign) and len(n.targets)==1}
    assert assignments['contextHash']=='context.contextNonDimAwareHash if context is not None else hash(None)';out.append('context_component_is_integer_hash')
    assert 'sumBindingKeys & itemBindingKeys' in source;out.append('binding_uses_set_intersection')
    assert 'calcKey = (concept, ancestor, contextHash, unit)' in source;out.append('concept_key_keeps_ancestor_hash_unit')
    assert 'y1, y2 = y2, y1' in source and 'iY1, iY2 = iY2, iY1' not in source;out.append('weight_swap_does_not_swap_endpoint_flags')
    assert 'inclA = incls1 | inclx1' in source and 'inclB = incls2 | inclx2' in source;out.append('final_overlap_uses_OR')
    assert 'decimals <= -28' in source;out.append('excess_digits_guard')
    for name in ('Contexts','Units','Equivalence'):
        p=U/'sources'/(name+'-sandbox.body');ast.parse(p.read_text());out.append(name+'_complete_source_parses')
    c=(U/'sources/Contexts-sandbox.body').read_text();u=(U/'sources/Units-sandbox.body').read_text()
    assert 'self.context.isEqualTo(o.context, self.dimensionalAspectModel)' in c;out.append('context_partition_checks_equality')
    assert 'self.unit.isEqualTo(o.unit)' in u;out.append('unit_partition_checks_equality')
    assert 'd[key(item)].append(item)' in (U/'sources/Equivalence-sandbox.body').read_text();out.append('dictionary_equivalence_partition')
    model=MODEL.read_text();assert 'self.qnameDims.keys() != cntx2.qnameDims.keys()' in model;out.append('dimensional_context_equality_checks_both_key_sets')
    return out

def check():
    ledger=load(U/'source-ledger.json');count=0
    for b in ledger['bindings']:assert bind(R/b['path'])==b;count+=1
    for a in ledger['anchors']:
        p=R/a['source']['path'];assert bind(p)==a['source'];count+=1
        assert chr(10).join(p.read_text().splitlines()[a['first_line']-1:a['last_line']])==a['excerpt'];count+=1
    e=examples();assert e==load(U/'examples.json');count+=len(e)+1
    a=static_checks();assert a==load(U/'static-checks.json');count+=len(a)+1
    for name in ('Contexts','Units','Equivalence'):
        receipt=load(U/'sources'/(name+'-receipt.json'))
        r=receipt.get('result') or receipt['final_result']['value']
        meta=json.loads(r['output']);assert r['exit_code']==0 and meta['http_code']==200;count+=1
        assert (U/'sources'/(name+'-sandbox.body')).stat().st_size==meta['size_download'];count+=1
        assert receipt['commit'] in meta['url_effective'];count+=1
    return {'assertions':count,'authored_witnesses':len(e),'static_checks':len(a),
      'source_anchors':len(ledger['anchors']),'input_bindings':len(ledger['bindings']),
      'acquisitions':3,'source_commit':'01f6a4656c2c6551d2f05f31c9d74366d133ee7e',
      'alignment_implementation':'exact_binding_keys_with_context_hash',
      'authoritative_alignment_correction':False,'upstream_executed':False,'actual_filing_impact':'not_run',
      'whole_rows_closed':0}
