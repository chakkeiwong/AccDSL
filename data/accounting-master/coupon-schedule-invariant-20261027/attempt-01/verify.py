"""Match the selected method to an independent affine induction and exact cases."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as Q
from hashlib import sha256
from datetime import datetime, timezone
import importlib.util, json, os, platform, resource, subprocess, sys, time, traceback
H=Path(__file__).resolve().parent; R=H.parents[2]
P=H.parent/'coupon-partial-settlement-20261027'
sys.path.insert(0,str(P))
spec=importlib.util.spec_from_file_location('partial_schedule_predecessor',P/'verify.py')
prior=importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)
s=prior.s
def digest(p):return sha256(p.read_bytes()).hexdigest()
def fmt(v):return prior.fmt(v)
def tidy(d):return {k:v for k,v in sorted(d.items()) if v}
def add(a,b,sign=1):
    out=dict(a)
    for k,v in b.items():out[k]=out.get(k,Q(0))+sign*v
    return tidy(out)
def affine(node):
    op=node['op']
    if op=='ref':assert set(node)=={'op','id'};return {node['id']:Q(1)}
    if op=='const':assert node['type']['kind']=='rational';return tidy({'1':Q(node['value'])})
    assert op in ('add','sub') and set(node)=={'op','left','right'}
    return add(affine(node['left']),affine(node['right']),1 if op=='add' else -1)
def bind(kind,key):return dict(kind=kind,**{('pointer' if kind=='memory' else 'name' if kind=='event' else 'role'):key})

def inspect(selection):
    book=selection['opening'];entry=selection['registry']['entries']['partial_coupon'];m=entry['method']
    assert entry['method_sha256']==s.identity(m)
    monetary=m['monetary'];d=monetary['definition']
    assert monetary['bindings']=={'amount':{'kind':'event','name':'amount'},'paid2':{'kind':'memory','pointer':'/paid2'}}
    assert set(d['inputs'])=={'amount','paid2'}
    assert len(d['calculations'])==1 and d['calculations'][0]['id']=='new_paid2'
    assert affine(d['calculations'][0]['expression'])=={'amount':Q(1),'paid2':Q(1)}
    assert set(d['calculations'][0]['requires'])=={'amount','paid2'}
    assert {v['account']:affine(v['expression']) for v in d['postings']}=={'cash':{'amount':Q(-1)},'interest_payable':{'amount':Q(1)}}
    assert len(d['postings'])==2 and all(v['requires']==['amount'] for v in d['postings'])
    assert len(d['flows'])==1 and d['flows'][0]['activity']=='operating'
    assert d['flows'][0]['id']==d['flows'][0]['origin']=='late_coupon_payment'
    assert affine(d['flows'][0]['expression'])=={'amount':Q(-1)} and d['flows'][0]['requires']==['amount']
    mem=m['memory'];assert mem['input_bindings']=={'new_paid2':{'kind':'calculation','name':'new_paid2'}}
    ops=mem['definition']['operations'];assert len(ops)==2
    assert [(v['op'],v['path'],v['value']) for v in ops]==[
        ('replace',['paid2'],{'kind':'read','source':'inputs','pointer':'/new_paid2'}),
        ('replace',['phase'],{'kind':'literal','value':'partial2'})]
    assert mem['definition']['state_schema']==book['memory_schema']
    assert entry['event_inputs']=={'amount':s.rt.engine.money_type(book)}
    assert entry['metadata_bindings']=={'event_date':'date'} and entry['clock']=={'kind':'direct_event_date'}
    original=('mode','right','source','clause','action1','action2','due1','due2','paid1')
    common={'payable_matches_unpaid','cash_nonnegative','partial_claim_positive','used_stays_used','facility_repaid'}|{'origin_'+v for v in original}
    for part in ('preconditions','postconditions'):
        rows=m[part]['manifest']['requirements']; rowsby={v['id']:v for v in rows}
        extra={'supported_phase','strictly_late','positive_amount','cash_available','partial_only'} if part=='preconditions' else {'partial_phase'}
        assert len(rows)==len(common|extra) and set(rowsby)==common|extra
        for row in rows:
            assert row['guard']==dict(op='const',type={'kind':'boolean','context':{}},value=True)
            assert row['guard_requires']==[] and row['on_false']=='invalid' and row['on_unknown']=='unresolved'
        f=lambda key: rowsby[key]['predicate']
        for key,op,left,right in [('payable_matches_unpaid','eq',{'payable':Q(-1)},{'due2':Q(1),'paid2':Q(-1)}),('cash_nonnegative','le',{}, {'cash':Q(1)}),('partial_claim_positive','lt',{}, {'due2':Q(1),'paid2':Q(-1)}),('facility_repaid','eq',{'facility':Q(1)},{})]:
            x=f(key);assert x['op']==op and affine(x['left'])==left and affine(x['right'])==right
        assert f('used_stays_used')==dict(op='ref',id='used')
        for name in original:
            x=f('origin_'+name);assert x['op']=='eq' and x['left']==dict(op='ref',id=name)
            assert x['right']==dict(op='const',type=book['memory_types']['/'+name],value=book['memory'][name])
        for name,v in m[part]['bindings'].items():
            if name in ('cash','payable','facility'):
                assert v=={'kind':'account','role':{'cash':'cash','payable':'interest_payable','facility':'facility_debt'}[name]}
            elif name in ('amount','event_date'):assert v=={'kind':'event','name':name}
            else:assert v=={'kind':'memory','pointer':'/'+name}
        if part=='preconditions':
            for key,op,left,right in [('positive_amount','lt',{}, {'amount':Q(1)}),('cash_available','le',{'amount':Q(1)},{'cash':Q(1)}),('partial_only','lt',{'amount':Q(1)},{'due2':Q(1),'paid2':Q(-1)})]:
                x=f(key);assert x['op']==op and affine(x['left'])==left and affine(x['right'])==right
            x=f('strictly_late'); assert x==dict(op='lt',left=dict(op='const',type={'kind':'date','context':{}},value='2027-12-31'),right=dict(op='ref',id='event_date'))
            x=f('supported_phase');assert x['op']=='any' and len(x['args'])==2
            assert x['args']==[dict(op='eq',left=dict(op='ref',id='phase'),right=dict(op='const',type={'kind':'text','context':{}},value=v)) for v in ('due2','partial2')]
        else:assert f('partial_phase')==dict(op='eq',left=dict(op='ref',id='phase'),right=dict(op='const',type={'kind':'text','context':{}},value='partial2'))
    return dict(method_sha256=s.identity(m),recurrence=dict(cash={'C':'1/1','q':'-1/1'},unpaid={'U':'1/1','q':'-1/1'},paid={'P':'1/1','q':'1/1'}),frame='all other balances and memory unchanged; dates, seen and flows append')

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120)); attempt=sys.argv[1];assert attempt in ('01','02','03')
    A=H/('attempt-'+attempt);A.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat();start=time.monotonic();checks=[];controls=[];cases=[];pins={}
    def save(n,v):(A/n).write_text(json.dumps(v,indent=2)+'\n')
    def ck(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v:raise AssertionError(n)
    def reject(n,fn):
        try:fn()
        except (AssertionError,ValueError,KeyError,TypeError) as e: controls.append(dict(name=n,reason=str(e)));ck('reject:'+n,True)
        else:ck('reject:'+n,False)
    old_native=prior.prior.prior.native.Engine.apply
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1');B=P/'attempt-01'
        ck('upstream_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
        for n,v in json.loads((B/'source-lock.json').read_text()).items():ck('source:'+n,digest(R/n)==v);pins[n]=v
        mods=[Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(R)]
        for p in mods+list(B.glob('*.json'))+[H/'verify.py',H/'contract.md',R/'docs/plans/accounting-coupon-schedule-invariant-20261027.md']:pins[str(p.relative_to(R))]=digest(p)
        save('source-lock.json',pins)
        for n in ('verify.py','contract.md'):(A/n).write_bytes((H/n).read_bytes())
        carrypath=H.parent/'coupon-carry-20261027/attempt-01/cases.json'
        records=[v for v in json.loads(carrypath.read_text()) if ':R6:draw:' in v['case']]
        epsilon=Q(1,2**64);c0=Q(85,16);u0=Q(43,8)
        amounts={'nonuniform':[Q(1,16),Q(1,2),Q(19,4)],'same_day':[Q(1,16),Q(1,2),Q(19,4)],'unequal_rationals':[Q(1,3),Q(2,7),Q(1577,336)],'tiny_then_rest':[epsilon,c0-epsilon],'near_exhaustion':[c0-epsilon]}
        schedules={k:[dict(id=k+'-'+str(i+1),date='2028-01-'+str(2 if k=='same_day' else i+2).zfill(2),amount=fmt(q)) for i,q in enumerate(xs)] for k,xs in amounts.items()}
        save('inputs-and-expectations.json',dict(origins=[dict(case=v['case'],sha256=s.identity(v)) for v in records],schedules=schedules,C0=fmt(c0),U0=fmt(u0),invariant_gap='1/16',claim='algebraic induction plus finite runtime conformance'))
        limits=dict(commands=s.rt.MAX_COMMANDS,trace_bytes=s.rt.MAX_TRACE_BYTES,record_bytes=s.rt.core.MAX_BYTES,rational_bits=s.rt.engine.monetary.MAX_BITS,scalar_characters=s.rt.core.MAX_SCALAR,expression_nodes=s.rt.core.MAX_NODES,expression_depth=s.rt.core.MAX_DEPTH)
        ck('inspected_limits',limits==dict(commands=64,trace_bytes=8388608,record_bytes=1000000,rational_bits=4096,scalar_characters=4096,expression_nodes=4096,expression_depth=48));save('runtime-limits.json',limits)
        # Independent coefficient identities implement the induction step.
        C={'C0':Q(1),'S':Q(-1)};U={'U0':Q(1),'S':Q(-1)};Ppaid={'S':Q(1)};q={'q':Q(1)}
        Cn=add(C,q,-1);Un=add(U,q,-1);Pn=add(Ppaid,q)
        ck('gap_coefficients',add(Un,Cn,-1)=={'C0':Q(-1),'U0':Q(1)})
        ck('claim_coefficients',add(Un,Pn)=={'U0':Q(1)})
        ck('positive_gap',u0-c0==Q(1,16)>0)
        ck('cash_plus_payment',add(Cn,Pn)=={'C0':Q(1)})
        save('coefficient-identities.json',{k:{x:fmt(y) for x,y in v.items()} for k,v in dict(C_next=Cn,U_next=Un,P_next=Pn,gap=add(Un,Cn,-1),claim=add(Un,Pn)).items()})
        inspections=[]
        prior.prior.prior.native.Engine.apply=lambda *a,**k: (_ for _ in ()).throw(AssertionError('native fallback forbidden'))
        for source in records:
            sid=s.identity(source);sel=s.select(source,sid);ident=s.identity(sel)
            inspection=inspect(sel);inspections.append(dict(case=source['case'],**inspection))
            ck('method_shape:'+source['case'],bool(inspection))
            for name,instructions in schedules.items():
                result=s.run(source,sid,sel,ident,instructions)
                ck('full:'+source['case']+':'+name,prior.verify(result,source,sid,sel,ident,instructions))
                cur=result['execution']['current'];S=sum(amounts[name]);payable=sel['registry']['entries']['partial_coupon']['method']['account_map']['interest_payable']
                ck('recurrence:'+name,Q(cur['balances'][cur['cash_account']])==c0-S and -Q(cur['balances'][payable])==u0-S and Q(cur['memory']['paid2'])==S)
                ck('gap:'+name,-Q(cur['balances'][payable])-Q(cur['balances'][cur['cash_account']])==Q(1,16))
                ck('no_rounding:'+name,Q(cur['balances'][cur['cash_account']])==(epsilon if name=='near_exhaustion' else 0))
                ck('frame:'+name,cur['memory']['action2']=='none' and cur['memory']['used'] is True)
                cases.append(dict(case=source['case']+':'+name,source_carry_sha256=sid,selection_sha256=ident,instructions=instructions,result=result))
        save('method-inspection.json',inspections)
        source=records[0];sid=s.identity(source);sel=s.select(source,sid);ident=s.identity(sel)
        too_many=[dict(id='cap-'+str(i),date='2028-01-02',amount=fmt(c0/65)) for i in range(65)]
        out=s.run(source,sid,sel,ident,too_many)['execution']
        ck('command_limit_not_infeasibility',out['status']=='invalid' and out['reason']=='command_limit' and 'current' not in out)
        controls.append(dict(name='economically_affordable_65_commands',result=out,interpretation='unsupported execution budget, not economic infeasibility'))
        for name,date in [('period_end_excluded','2029-01-01'),('pre_opening','2027-12-31')]:
            out=s.run(source,sid,sel,ident,[dict(id=name,date=date,amount='1/1')])['execution']
            ck(name,out['status']=='stopped_provisional' and out['current']==sel['opening'] and out['trace']==[])
            controls.append(dict(name=name,reason=out['stop']['reason']))
        reject('rational_bit_limit',lambda:s.rt.engine.monetary.rational(fmt(Q(1,2**4096))))
        for name,change in [('overwrite_paid',lambda m:m['monetary']['definition']['calculations'][0].update(expression={'op':'ref','id':'amount'})),('flow_financing',lambda m:m['monetary']['definition']['flows'][0].update(activity='financing')),('erase_origin_action',lambda m:m['memory']['definition']['operations'].append(dict(id='bad',op='replace',path=['action2'],value=dict(kind='literal',value='pay')))),('reverse_cash_posting',lambda m:m['monetary']['definition']['postings'][0].update(expression={'op':'ref','id':'amount'}))]:
            bad=cp(sel);entry=bad['registry']['entries']['partial_coupon'];change(entry['method']);entry['method_sha256']=s.identity(entry['method'])
            reject(name,lambda v=bad:inspect(v))
        for n,v in pins.items():ck('preserved:'+n,digest(R/n)==v)
        summary=dict(status='PASS',cases=len(cases),method_inspections=len(inspections),assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='exact algebraic induction; finite runtime cases; resource limits retained')
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
    finally:
        prior.prior.prior.native.Engine.apply=old_native
        for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,v)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+attempt,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact algebraic and conformance checks',data_version='source-lock.json',plan='docs/plans/accounting-coupon-schedule-invariant-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')
if __name__=='__main__':main()
