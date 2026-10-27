"""Scoped synthetic methods executed by the unchanged declared company runtime.
No source/accounting admission, stochastic calibration or production default.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util,json,platform,sys,time

START=time.monotonic(); B=Path(__file__).resolve().parent; ROOT=B.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import declared_company_program_v2 as program
import declared_financing_methods_v1 as h
import company_execution_v1 as native
s=importlib.util.spec_from_file_location('base_examples',ROOT/'data/accounting-master/declared-operating-cycle-20261025/examples.py')
ex=importlib.util.module_from_spec(s);s.loader.exec_module(ex)
ref,bin,c=h.ref,h.binary,h.constant
fmt=h.fmt
rows=[]
def check(name,actual,expected):
    ok=actual==expected
    rows.append(dict(id=name,actual=actual,expected=expected,passed=ok))
    if not ok: raise AssertionError((name,actual,expected))
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def make(kind,owner='alpha'):
    body,_,_,mapping=ex.fixture(owner);book=body['opening'];money=program.engine.money_type(book)
    unit={**deepcopy(money),'dimensions':{}}
    shares={**deepcopy(money),'dimensions':{'equity:share':1}}
    price={**deepcopy(money),'dimensions':{'currency:USD':1,'equity:share':-1}}
    types={'face':money,'old_shares':shares,'new_shares':shares,'coupon':money,'covenant_cash':money,'stage':unit}
    state={'face':'100/1','old_shares':'100/1','new_shares':'0/1','coupon':fmt(5 if kind=='fixed' else 7),'covenant_cash':'0/1','stage':'0/1'}
    shape=deepcopy(body['schemas'][book['memory_schema']]);shape['properties']['terms']=h.record({k:h.scalar('rational') for k in state});shape['required'].append('terms')
    book['memory']['terms']=state;book['memory_schema']=program.digest(shape)
    book['memory_types'].update({'/terms/'+k:v for k,v in types.items()})
    book['balances']={v:'0/1' for v in mapping.values()}
    book['balances'].update({mapping[k]:v for k,v in dict(cash='16/1',inventory='104/1',debt='-100/1',capital='-20/1').items()})
    schemas={program.digest(shape):shape}; entries={}
    # Each method is immutable data consumed by the common typed evaluator.
    def method(key,stage,next_stage,inputs,binds,postings,flows,changes,extra=()):
        identity='literature.synthetic.'+key
        monetary_types={k:v[0] for k,v in binds.items()}; bindings={k:v[1] for k,v in binds.items()}
        pre_types={'stage':unit,'cash_control':money,**monetary_types}
        pre_bind={'stage':h.memory('/terms/stage'),'cash_control':h.account('cash'),**bindings}
        pre=[('correct_stage',bin('eq',ref('stage'),c(unit,fmt(stage))),['stage'],'invalid'),
             ('cash_nonnegative',bin('le',c(money,'0/1'),ref('cash_control')),['cash_control'],'invalid')]
        for k,t in inputs.items():pre.append((k+'_nonnegative',bin('le',c(t,'0/1'),ref(k)),[k],'invalid'))
        pre+=list(extra)
        used_pre={k for _,_,deps,_ in pre for k in deps}
        pre_types={k:v for k,v in pre_types.items() if k in used_pre}
        pre_bind={k:v for k,v in pre_bind.items() if k in used_pre}
        calculations=[];fields={}; ib={};operations=[]
        for key_,(typ,expression,deps) in changes.items():
            name='next_'+key_; calculations.append(dict(id=name,type=typ,expression=expression,requires=deps))
            fields[name]=h.scalar('rational');ib[name]={'kind':'calculation','name':name}
            operations.append(dict(id='write.'+key_,op='replace',path=['terms',key_],value={'kind':'read','source':'inputs','pointer':'/'+name}))
        operations.append(dict(id='advance',op='replace',path=['terms','stage'],value={'kind':'literal','value':fmt(next_stage)}))
        ishape=h.record(fields);ss={**schemas,program.digest(ishape):ishape}
        post_types={'cash_control':money,'stage':unit};post_bind={'cash_control':h.account('cash'),'stage':h.memory('/terms/stage')}
        post=[('cash_nonnegative',bin('le',c(money,'0/1'),ref('cash_control')),['cash_control'],'invalid'),('stage_advanced',bin('eq',ref('stage'),c(unit,fmt(next_stage))),['stage'],'invalid')]
        used_monetary={k for _,_,deps in postings+flows for k in deps}|{k for row in calculations for k in row['requires']}
        monetary_types={k:v for k,v in monetary_types.items() if k in used_monetary}
        bindings={k:v for k,v in bindings.items() if k in used_monetary}
        roles={'cash'}|{r for r,_,_ in postings}|{v[1]['role'] for v in binds.values() if v[1]['kind']=='account'}
        m={'profile':program.engine.METHOD,'id':identity,'version':'1','context':deepcopy(book['context']),
           'account_map':{r:mapping[r] for r in sorted(roles)},
           'preconditions':{'manifest':h.conditions(identity,pre_types,pre),'bindings':pre_bind},
           'postconditions':{'manifest':h.conditions(identity,post_types,post),'bindings':post_bind},
           'monetary':{'definition':{'profile':program.engine.monetary.PROFILE,'method_id':identity,'version':'1','inputs':{k:h.declaration(t,k) for k,t in monetary_types.items()},'calculations':calculations,'accounts':{r:money for r in sorted(roles)},'cash_account':'cash',
             'postings':[dict(id=r,account=r,expression=e,requires=d) for r,e,d in postings],
             'flows':[dict(id=key,activity=a,origin=key,expression=e,requires=d) for a,e,d in flows]},'bindings':bindings},
           'memory':{'definition':{'profile':program.engine.memory.PROFILE,'state_schema':book['memory_schema'],'input_schema':program.digest(ishape),'operations':operations},'input_bindings':ib},
           'residual_prerequisites':['Authored one-period initial measurement at proceeds; face is contractual memory.','Coupon and external valuation are declared conditional inputs. No source, GAAP, price-equilibrium or legal admission.']}
        entries[key]={'method_sha256':program.digest(m),'method':m,'schemas':ss,'account_classes':{r:book['accounts'][mapping[r]]['classification'] for r in roles},'event_inputs':inputs,'metadata_bindings':{},'clock':{'kind':'direct_event_date'}}
        schemas.update(ss)
    neg=lambda e:bin('sub',c(money,'0/1'),e)
    method('coupon',0,1,{}, {'coupon':(money,h.memory('/terms/coupon'))}, [('cash',neg(ref('coupon')),['coupon']),('interest',ref('coupon'),['coupon'])],[('operating',neg(ref('coupon')),['coupon'])],{})
    method('operate',1,2,{}, {},[('cash',c(money,'-6/1'),[]),('payroll',c(money,'6/1'),[])],[('operating',c(money,'-6/1'),[])],{})
    method('covenant',2,3,{}, {'cash':(money,h.account('cash'))},[],[],{'covenant_cash':(money,ref('cash'),['cash'])})
    inputs={'face':money,'proceeds':money,'quote':unit}
    binds={k:(t,h.event(k)) for k,t in inputs.items()}
    binds.update(face_before=(money,h.memory('/terms/face')),measured=(money,h.memory('/terms/covenant_cash')))
    extra=[('debt_permission',bin('le',c(money,'5/1'),ref('measured')),['measured'],'unsupported'),('quoted_proceeds',bin('eq',ref('proceeds'),bin('mul',ref('face'),ref('quote'))),['proceeds','face','quote'],'invalid'),('positive_face',bin('lt',c(money,'0/1'),ref('face')),['face'],'invalid')]
    method('discounted_issue',3,4,inputs,binds,[('cash',ref('proceeds'),['proceeds']),('debt',neg(ref('proceeds')),['proceeds'])],[('financing',ref('proceeds'),['proceeds'])],{'face':(money,bin('add',ref('face_before'),ref('face')),['face_before','face'])},extra)
    inputs={'shares':shares,'price':price};binds={k:(t,h.event(k)) for k,t in inputs.items()};binds['existing_new']=(shares,h.memory('/terms/new_shares'))
    amount=bin('mul',ref('shares'),ref('price'))
    method('equity_issue',3,4,inputs,binds,[('cash',amount,['shares','price']),('capital',neg(deepcopy(amount)),['shares','price'])],[('financing',amount,['shares','price'])],{'new_shares':(shares,bin('add',ref('existing_new'),ref('shares')),['existing_new','shares'])},[('price_positive',bin('lt',c(price,'0/1'),ref('price')),['price'],'invalid')])
    method('equity_fee',4,5,{}, {},[('cash',c(money,'-1/1'),[]),('capital',c(money,'1/1'),[])],[('financing',c(money,'-1/1'),[])],{})
    body.update(profile=program.PROFILE,name='literature-'+kind+'-'+owner,schemas=schemas,registry={'profile':program.methods.REGISTRY,'context':deepcopy(book['context']),'entries':entries},commands=[])
    def event(key,day,values=None):
        vals=values or {};return {'kind':'event','method_key':key,'event':{'id':key,'date':day,'inputs':{k:{'type':deepcopy(entries[key]['event_inputs'][k]),'value':program.engine.known(v),'provenance':'Authored diagnostic terms'} for k,v in vals.items()}}}
    body['commands']=[event('coupon','2027-01-02'),event('operate','2027-01-03'),event('covenant','2027-01-04')]
    movements=[]
    if kind=='fixed':body['commands'].append(event('discounted_issue','2027-01-05',dict(face='315/88',proceeds='3/1',quote='88/105')))
    else:
        body['commands'] += [event('equity_issue','2027-01-05',dict(shares='600/19',price='19/100')),event('equity_fee','2027-01-06')]
        movements=[dict(id='movement.'+k,event_id=k,date=day,account=mapping['capital'],amount=v,description='Synthetic subscription or direct equity issue cost') for k,day,v in [('equity_issue','2027-01-05','6/1'),('equity_fee','2027-01-06','-1/1')]]
    body['commands'].append(dict(kind='report',id='closing',cutoff='2027-01-07',equity_movements=movements,notes=[dict(id='valuation',label='Synthetic measurement',status='unresolved',reason='Contract and standards admission, maturity amortisation and valuation remain outside this example')]))
    return body,mapping

def run():
    outputs=[]
    original=native.Engine.apply
    native.Engine.apply=lambda *a,**k: (_ for _ in ()).throw(AssertionError('Native fallback forbidden'))
    try:
        for owner in ['alpha','beta']:
            for kind in ['fixed','floating']:
                body,mapping=make(kind,owner);before=deepcopy(body);r=program.run(body);tag=kind+'.'+owner
                check(tag+'.complete',r['status'],'complete_provisional')
                check(tag+'.input_unchanged',body,before)
                check(tag+'.replay',program.verify(body,r),True)
                expected_cash=[16,11,5,5,8] if kind=='fixed' else [16,9,3,3,9,8]
                expected_deltas=[-5,-6,0,3] if kind=='fixed' else [-7,-6,0,6,-1]
                state=body['opening']
                for i,row in enumerate(r['trace'][:-1]):
                    trans=row['result']['transition'];after=trans['after']
                    check(tag+f'.{i}.balance',sum(Q(v) for v in trans['journal'].values()),Q(0))
                    check(tag+f'.{i}.cash',Q(after['balances'][mapping['cash']]),Q(expected_cash[i+1]))
                    check(tag+f'.{i}.flows',sum(Q(v['amount']) for v in trans['flows']),Q(expected_deltas[i]))
                    check(tag+f'.{i}.memory_complement',after['memory']['complement'],body['opening']['memory']['complement'])
                    check(tag+f'.{i}.stage',Q(after['memory']['terms']['stage']),Q(i+1))
                    state=after
                terms=r['current']['memory']['terms'];balances=r['current']['balances']
                check(tag+'.face',Q(terms['face']),Q(9115,88) if kind=='fixed' else Q(100))
                check(tag+'.carrying',Q(balances[mapping['debt']]),Q(-103) if kind=='fixed' else Q(-100))
                check(tag+'.old_shares',Q(terms['old_shares']),Q(100))
                fraction=Q(terms['new_shares'])/(Q(terms['old_shares'])+Q(terms['new_shares']))
                check(tag+'.dilution',fraction,Q(0) if kind=='fixed' else Q(6,25))
                check(tag+'.dated_covenant',Q(terms['covenant_cash']),Q(5) if kind=='fixed' else Q(3))
                report=r['trace'][-1]['result'];check(tag+'.report',report['status'],'reported')
                check(tag+'.reported_assets',Q(report['balance_sheet']['total_assets']),Q(112))
                check(tag+'.reported_liabilities',Q(report['balance_sheet']['total_liabilities']),Q(103) if kind=='fixed' else Q(100))
                check(tag+'.reported_equity',Q(report['equity']['closing']),Q(9) if kind=='fixed' else Q(12))
                outputs.append(dict(case=tag,program=body,result=r))
        fixed,_=make('fixed');floating,_=make('floating')
        bad=[]
        x=deepcopy(floating);x['commands'][3]=deepcopy(fixed['commands'][3]);bad.append(('covenant_blocks_debt',x,3))
        x=deepcopy(fixed);x['commands'][3]['event']['inputs']['proceeds']['value']=program.engine.known('315/88');bad.append(('face_is_not_proceeds',x,3))
        x=deepcopy(fixed);x['commands'][0],x['commands'][2]=x['commands'][2],x['commands'][0];bad.append(('covenant_cannot_precede_payment',x,0))
        x=deepcopy(floating);x['commands'][3]['event']['inputs']['price']['value']=program.engine.known('0/1');bad.append(('zero_share_price',x,3))
        x=deepcopy(fixed);x['opening']['balances']['cash']='4/1';x['opening']['balances']['inventory']='116/1';bad.append(('insufficient_coupon_cash',x,0))
        x=deepcopy(fixed);x['commands'].insert(4,deepcopy(x['commands'][3]));bad.append(('duplicate_issue',x,4))
        for name,x,n in bad:
            r=program.run(x);check(name+'.stopped',r['status'],'stopped_provisional');check(name+'.prefix_only',len(r['trace']),n)
            if n:check(name+'.atomic_refusal',r['current'],r['trace'][-1]['result']['transition']['after'])
            else:check(name+'.atomic_refusal',r['current'],x['opening'])
            outputs.append(dict(case=name,result=r))
        # Independent complete accounting expectations, not only cash comparisons.
        for x in outputs[:4]:
            b=x['program'];m={line['id']:line['accounts'][0] for line in b['mapping']['lines']};kind=x['case'].split('.')[0]
            expected={a:'0/1' for a in b['opening']['accounts']}
            expected.update({m[k]:v for k,v in dict(cash='8/1',inventory='104/1',debt='-103/1' if kind=='fixed' else '-100/1',capital='-20/1' if kind=='fixed' else '-25/1',interest='5/1' if kind=='fixed' else '7/1',payroll='6/1').items()})
            check(x['case']+'.all_balances',x['result']['current']['balances'],expected)
        # I1: replay each admissible economic history under a policy constrained
        # by actor information. The wrapper is finite and explicitly unweighted.
        def information_path(kind,hedge):
            b,m=make(kind);b['opening']['balances'][m['cash']]='6/1';b['opening']['balances'][m['inventory']]='114/1'
            e=deepcopy(b['registry']['entries']['operate']);method=e['method']
            for phase,expected in [('preconditions','0/1'),('postconditions','0/1')]:
                for req in method[phase]['manifest']['requirements']:
                    if req['id'] in ['correct_stage','stage_advanced']:req['predicate']['right']['value']=expected
            md=method['monetary']['definition']
            md['postings'][0]['expression']['value']='-1/1';md['postings'][1]['expression']['value']='1/1'
            md['flows'][0]['expression']['value']='-1/1';md['flows'][0]['origin']='hedge'
            method['memory']['definition']['operations']=[dict(id='keep_stage',op='replace',path=['terms','stage'],value={'kind':'literal','value':'0/1'}),dict(id='cap_coupon',op='replace',path=['terms','coupon'],value={'kind':'literal','value':'5/1'})]
            e['method_sha256']=program.digest(method);b['registry']['entries']['hedge']=e
            coupon=deepcopy(b['commands'][0]);coupon['event']['date']='2027-01-03'
            commands=([dict(kind='event',method_key='hedge',event=dict(id='hedge',date='2027-01-02',inputs={}))] if hedge else [])+[coupon]
            commands.append(dict(kind='report',id='after_coupon',cutoff='2027-01-04',equity_movements=[],notes=[]));b['commands']=commands
            return b,program.run(b),m
        def family(revision,admitted,informed,policy):
            required=set(admitted) if informed else {'unknown'}
            if set(policy)!=required:return {'status':'invalid_policy','reason':'actor_information'}
            branches={}
            for kind in admitted:
                b,r,m=information_path(kind,policy[kind if informed else 'unknown'])
                branches[kind]={'status':r['status'],'cash':r['current']['balances'][m['cash']],'program_sha256':program.digest(b),'result':r}
            return dict(status='conditional_results',revision=revision,admitted=admitted,actor_information='type' if informed else 'unknown',weights=None,dependencies=program.digest(dict(revision=revision,admitted=admitted,informed=informed,policy=policy)),branches=branches)
        v1=family('v1',['fixed'],False,{'unknown':False})
        v2=family('v2',['fixed','floating'],False,{'unknown':False})
        check('I1.old_complete',v1['branches']['fixed']['status'],'complete_provisional')
        check('I1.corrected_fixed_cash',v2['branches']['fixed']['cash'],'1/1')
        check('I1.corrected_floating_refusal',v2['branches']['floating']['status'],'stopped_provisional')
        check('I1.correction_invalidates_dependency',v1['dependencies']!=v2['dependencies'],True)
        check('I1.family_unweighted',v2['weights'],None)
        check('I1.correction_reopens_type',sorted(v2['branches']),['fixed','floating'])
        informed=family('v2',['fixed','floating'],True,{'fixed':False,'floating':True})
        safe=family('v2',['fixed','floating'],False,{'unknown':True})
        check('I1.informed_cash',[informed['branches'][k]['cash'] for k in ['fixed','floating']],['1/1','0/1'])
        check('I1.uninformed_cash',[safe['branches'][k]['cash'] for k in ['fixed','floating']],['0/1','0/1'])
        check('I1.safe_complete',all(v['status']=='complete_provisional' for f in [safe,informed] for v in f['branches'].values()),True)
        check('I1.anticipation_rejected',family('v2',['fixed','floating'],False,{'fixed':False,'floating':True})['status'],'invalid_policy')
        check('I1.information_dependency',informed['dependencies']!=safe['dependencies'],True)
        # The oracle's -1 denotes unmet cash, not an admissible negative-cash book.
        check('I1.refused_coupon_atomic',v2['branches']['floating']['cash'],'6/1')
        outputs.extend([dict(case='I1_revision1',family=v1),dict(case='I1_revision2',family=v2),dict(case='I1_informed',family=informed),dict(case='I1_common_safe_policy',family=safe)])
        # Remove the new-share memory update: a plausible accounting-only method
        # can finish, but the independent ownership criterion detects the defect.
        x=deepcopy(floating);e=x['registry']['entries']['equity_issue'];e['method']['memory']['definition']['operations']=[o for o in e['method']['memory']['definition']['operations'] if o['id']!='write.new_shares'];e['method_sha256']=program.digest(e['method'])
        r=program.run(x);check('ownership_omission_not_detected_by_balancing',r['status'],'complete_provisional')
        check('independent_ownership_check_detects_omission',Q(r['current']['memory']['terms']['new_shares'])!=Q(600,19),True)
    finally:native.Engine.apply=original
    def enc(x):
        if isinstance(x,Q):return fmt(x)
        if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [enc(v) for v in x]
        return x
    # Bulky equal whole-program snapshots need not be repeated for passing checks.
    compact=[]
    for r in rows:
        if r['id'].endswith(('.input_unchanged','.atomic_refusal')):r={**r,'actual':'full structured comparison','expected':'identical'}
        compact.append(enc(r))
    payload=dict(status='PASS',checks=compact,count=len(compact),scope='Scoped synthetic typed-method runtime integration; production scripts unchanged; native fallback disabled.',cases=outputs)
    (B/'runtime-integration-results.json').write_text(json.dumps(enc(payload),indent=2)+'\n')
    files={str(Path(m.__file__).relative_to(ROOT)):sha256(Path(m.__file__).read_bytes()).hexdigest() for m in [program,h,ex,native]}
    (B/'runtime-integration-manifest.json').write_text(json.dumps(dict(command='python3 data/accounting-master/literature-closure-20261026/runtime-integration.py',git_commit='Unavailable: unusable .git',environment=sys.version,platform=platform.platform(),cpu_gpu='CPU-only; no GPU detection or ML import',data='Authored synthetic I2 terms; no calibration',random_seeds='N/A exact deterministic execution',wall_seconds=time.monotonic()-START,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),dependencies=files,plan='docs/plans/accounting-literature-closure-20261026.md',result='data/accounting-master/literature-closure-20261026/runtime-integration-results.json'),indent=2)+'\n')
    print(json.dumps(dict(status='PASS',checks=len(compact),cases=len(outputs))))
if __name__=='__main__':run()
