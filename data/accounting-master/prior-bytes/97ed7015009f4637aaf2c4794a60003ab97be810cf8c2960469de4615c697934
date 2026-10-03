"""Independent input replay and exact algebra; P04 executed obligations."""
import copy
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import json
import hashlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import z3
from rational_solver_v1 import *
from reconstruction_v1 import *
from test_accounting_p03 import bindings, BASE
from core0_frontends_v1 import compile_source
ROOT=Path(__file__).resolve().parents[1]
OBSERVATIONS=[]
B=Budget(20,10000,500,500,20000,1000,1000000)


def spec():
    return json.loads((ROOT/'docs/design/fixtures/p04-reconstruction-cases-v1.json').read_text())['input_fixture']


def observation(s,amount):
    return {'id':'cash-note','context':copy.deepcopy(s['context']),'action':'Accept','source':['synthetic:cash-note'],
            'mapping':'cash','domain':{'lower':str(amount),'upper':str(amount),'lower_closed':True,'upper_closed':True}}


class ReconstructionTests(unittest.TestCase):
    def record(self,name,result):OBSERVATIONS.append({'obligation':name,'passed':True,'result':result})
    def test_independent_enumeration(self):
        evidence=[]
        # Oracle replays original template incidence; no production expressions or Z3.
        for opening,total,limit,coefficient in [(10,13,3,1),(4,8,4,1),(7,13,3,2)]:
            s=spec();s['opening']={'Cash':str(opening),'Equity':str(-opening)}
            s['templates']['sale']['postings']={'Cash':str(coefficient),'Equity':str(-coefficient)}
            for row in s['slots']:row['integer_bounds']=[0,limit]
            s['observations']=[observation(s,total)]
            p=construct(s);r=solve(p,B)
            actual={(int(F(c['witness']['a'])),int(F(c['witness']['b']))) for c in r['cells'] if c['feasibility']=='sat'}
            expected=set()
            for a,b in product(range(limit+1),repeat=2):
                cash=F(opening)
                for amount in (a,b):cash+=F(coefficient)*amount
                if cash==total:expected.add((a,b))
            self.assertEqual(actual,expected);self.assertEqual(r['status'],'ExactWithinScope')
            for c in r['cells']:
                if c['feasibility']=='sat':self.assertEqual(F(c['outputs']['cash'])+F(c['outputs']['equity']),0)
            s['slots'].reverse();rr=solve(construct(s),B)
            self.assertEqual({tuple(c['witness'][n] for n in ('a','b')) for c in rr['cells'] if c['feasibility']=='sat'},
                             {tuple(c['witness'][n] for n in ('a','b')) for c in r['cells'] if c['feasibility']=='sat'})
            evidence.append({'inputs':s,'oracle':sorted(expected),'actual':r})
        self.record('enumeration',evidence)
    def test_p03_parent_views(self):
        source=BASE.replace('alternative allFixed { assume alpha == 1; }','alternative allFixed { assume alpha <= 0.75; }').replace('alternative allFloating { assume alpha == 0; }','alternative allFloating { assume alpha >= 0.25; }')
        results=[]
        for text in (BASE,source):
            c=compile_source(text,bindings());self.assertTrue(c.ok)
            p=from_p03(c.ir,bindings(),{'DemoDebt@1/DebtMix':'fixed-floating-amounts-v1'})
            self.assertFalse(p.unsupported)
            r=solve(p,B,p.outputs['interest']);self.assertEqual(r['bounds']['lower']['value'],'5');self.assertEqual(r['bounds']['upper']['value'],'7')
            self.assertEqual(r['coverage']['total'],1)
            half=p.variables['alpha']==q('1/2')
            self.assertEqual(solve(p,B,extra=[half])['feasibility'],'Feasible')
            both=solve(p,B,selected_views=['allFixed','allFloating'],view_operator='intersection',extra=[half])
            self.assertEqual(both['feasibility'],'Infeasible' if text==BASE else 'Feasible')
            fixed=solve(p,B,selected_views=['allFixed'],extra=[half])
            self.assertEqual(fixed['feasibility'],'Infeasible' if text==BASE else 'Feasible')
            self.assertEqual(solve(p,B,extra=[half])['feasibility'],'Feasible')
            results.append({'parent':r,'intersection':both,'conditional':fixed})
        self.record('p03_views',results)
    def test_rounded_strict_and_unbounded(self):
        fixture=json.loads((ROOT/'docs/design/fixtures/borrowings.json').read_text())['rounded']
        p=Problem('rounded-debt','fixture');f,v=z3.Reals('F V');p.variables={'F':f,'V':v}
        p.add('amounts',z3.And(f>=0,v>=0));p.add('debt-note',z3.And(f+v>=q(fixture['debt'][0]),f+v<q(fixture['debt'][1])))
        p.add('interest-note',z3.And(q('.05')*(f+v)>=q(fixture['interest'][0]),q('.05')*(f+v)<q(fixture['interest'][1])))
        r=solve(p,B,q('.05')*f+q('.07')*v)
        self.assertEqual(r['bounds']['lower']['value'],'199/40');self.assertTrue(r['bounds']['lower']['attained'])
        self.assertEqual(r['bounds']['upper']['value'],'1407/200');self.assertFalse(r['bounds']['upper']['attained'])
        x=z3.Real('x');empty=Problem('empty','fixture',variables={'x':x});empty.add('strict',x>0);empty.add('closed',x<=0)
        self.assertEqual(solve(empty,B,x)['status'],'Infeasible')
        u=Problem('unbounded','fixture',variables={'x':x});u.add('positive',x>0)
        un=solve(u,B,x);self.assertEqual(un['bounds']['upper']['status'],'Unbounded');self.assertFalse(un['bounds']['lower']['attained'])
        const=solve(u,B,q(2));self.assertTrue(const['bounds']['lower']['attained'])
        self.record('strict_bounds',{'rounded':r,'unbounded':un,'constant':const})
    def test_rounding_and_integer_gaps(self):
        self.assertEqual([half_even(x,'1') for x in ['-2.5','-1.5','1.5','2.5']],[F(-2),F(-2),F(2),F(2)])
        self.assertTrue(disclosure_domain('2','1','half_even')['upper_closed']);self.assertFalse(disclosure_domain('3','1','half_even')['lower_closed'])
        self.assertEqual(half_even('.005','.01')+half_even('.005','.01'),0);self.assertEqual(half_even('.010','.01'),F('.01'))
        p=Problem('integer-gap','fixture',variables={'k':z3.Int('k')},finite={'k':range(0,3)})
        p.add('gap',z3.And(p.variables['k']>0,p.variables['k']<1));self.assertEqual(solve(p,B)['status'],'Infeasible')
        self.record('rounding_integer',{'negative_ties':'checked','posting_boundary':'checked','integer':solve(p,B)})
    def test_incomplete_unsupported_unknown(self):
        s=spec();p=construct(s)
        zero=solve(p,replace(B,max_cells=0));self.assertEqual(zero['coverage']['completed'],0)
        partial=solve(p,replace(B,max_cells=1),p.outputs['cash']);self.assertEqual(partial['status'],'PartialSearch');self.assertFalse(partial['bounds']['upper']['certified'])
        class UnknownBackend(Backend):
            def check(self,solver,stage):return z3.unknown
        unknown=solve(p,B,backend=UnknownBackend());self.assertEqual(unknown['feasibility'],'Unknown')
        x,y=z3.Reals('x y');p=Problem('nonlinear','fixture',variables={'x':x,'y':y});p.add('nonlinear',x*y==1)
        self.assertEqual(solve(p,B)['status'],'UnsupportedFragment')
        p=Problem('unbounded-int','fixture',variables={'k':z3.Int('k')});self.assertEqual(solve(p,B)['status'],'UnsupportedFragment')
        s['obligations']=['unmatched source'];self.assertEqual(solve(construct(s),B)['status'],'PartialSearch')
        self.record('coverage_unknown',{'zero':zero,'partial':partial,'unknown':unknown})
    def test_identity_context_conflicts(self):
        s=spec();s['observations']=[observation(s,13)];s['observations']*=2
        p=construct(s);self.assertEqual(sum(n=='observation:cash-note' for n,e in p.constraints),1)
        bad=copy.deepcopy(s);bad['observations'][1]=observation(bad,14)
        with self.assertRaises(ValueError):construct(bad)
        bad=copy.deepcopy(s);bad['observations'][0]['context']['currency']='EUR'
        with self.assertRaises(ValueError):construct(bad)
        s['constraints']=[{'id':'source:contradiction','expression':['<','cash','0']}]
        r=solve(construct(s),B);self.assertEqual(r['status'],'Infeasible')
        self.assertTrue(all(c['conflict']['rechecked']=='unsat' for c in r['cells']))
        self.record('identity_conflicts',r)
    def test_admission_measure_grouping(self):
        accepted=[]
        for kind,fields in ADMISSION_FIELDS.items():
            a={'id':kind,'scope':'synthetic','provenance':['synthetic'],'dependencies':[],'kind':kind}
            a.update({k:'declared' for k in fields})
            if kind=='ExtractionReading':a['review_decision']='Accept'
            if kind=='AccountingElection':a.update(permitted_treatments=['FIFO'],election='FIFO')
            accepted.append(admit(a));bad=dict(a);del bad[fields[0]]
            with self.assertRaises(ValueError):admit(bad)
        measure=FiniteMeasure([{'id':'fixed','hypothesis':{'economic_state':'fixed'},'weight':'3/5','status':'complete','outcome':'5'}, {'id':'floating','hypothesis':{'economic_state':'floating'},'weight':'2/5','status':'unsupported','outcome':None}], 'explicit synthetic joint prior')
        posterior=measure.update({'fixed':'1/5','floating':'4/5'},['new-note'])
        self.assertEqual([a['weight'] for a in posterior.atoms],['3/11','8/11']);self.assertIsNone(measure.summary()['mean'])
        with self.assertRaises(ValueError):posterior.update({'fixed':'1','floating':'1'},['new-note'])
        with self.assertRaises(ValueError):measure.update({'fixed':'0','floating':'0'},['zero'])
        with self.assertRaises(ValueError):weighted_summary([])
        contracts=[{'id':str(i),'principal':str(10+i),'rate':'1/20','reset':'fixed','maturity':'2030','hedge':'none'} for i in range(2)]
        scenario={'rate':'7/100','year_fraction':'1'};horizon=['2026','2027'];group=group_contracts(contracts,scenario,horizon)
        for key,value in [('rate','1/10'),('maturity','2031')]:
            altered=copy.deepcopy(contracts);altered[0][key]=value
            with self.assertRaises(ValueError):group_contracts(altered,scenario,horizon,group)
        with self.assertRaises(ValueError):group_contracts(contracts,dict(scenario,rate='8/100'),horizon,group)
        with self.assertRaises(ValueError):group_contracts(contracts,scenario,['2026','2028'],group)
        self.record('uncertainty_probability_grouping',{'admissions':accepted,'posterior':posterior.atoms,'mass':measure.summary(),'group':group})

    def test_view_union_order_and_joint_outputs(self):
        source=BASE.replace('alternative allFixed { assume alpha == 1; }','alternative allFixed { assume alpha <= 0.75; }').replace('alternative allFloating { assume alpha == 0; }','alternative allFloating { assume alpha >= 0.25; }')
        p=from_p03(compile_source(source,bindings()).ir,bindings(),{'DemoDebt@1/DebtMix':'fixed-floating-amounts-v1'})
        a=p.variables['alpha']; parent=solve(p,B,p.outputs['interest'])
        intersection=solve(p,B,p.outputs['interest'],selected_views=['allFixed','allFloating'],view_operator='intersection')
        self.assertEqual(intersection['coverage']['total'],1)
        self.assertEqual([intersection['bounds'][d]['value'] for d in ('lower','upper')],['11/2','13/2'])
        union=solve(p,B,selected_views=['allFixed','allFloating'],view_operator='union',extra=[a==q('1/2')])
        self.assertEqual(union['feasibility'],'Feasible')
        swapped=source.replace('alternative allFixed { assume alpha <= 0.75; }','TEMP').replace('alternative allFloating { assume alpha >= 0.25; }','alternative allFixed { assume alpha <= 0.75; }').replace('TEMP','alternative allFloating { assume alpha >= 0.25; }')
        pp=from_p03(compile_source(swapped,bindings()).ir,bindings(),{'DemoDebt@1/DebtMix':'fixed-floating-amounts-v1'})
        self.assertEqual(solve(pp,B,extra=[pp.variables['alpha']==q('1/2')])['feasibility'],'Feasible')
        joint=solve(p,B,extra=[p.outputs['fixed']==100,p.outputs['floating']==100])
        self.assertEqual(joint['status'],'Infeasible')
        with self.assertRaises(ValueError):solve(p,B,selected_views=['allFixed','allFloating'])
        self.record('view_union_joint',{'parent':parent,'intersection':intersection,'union':union,'incompatible_marginals':joint})

    def test_genuine_choice_and_activation(self):
        s=spec();s['choices']=[{'id':'policy','values':[0,1]}]
        s['constraints']=[{'id':'policy:a','expression':['==','a',['*','policy','2']]},
                          {'id':'policy:b','expression':['==','b',['-','3','a']]}]
        p=construct(s);r=solve(p,B)
        actual={(int(c['witness']['policy']),int(c['witness']['a']),int(c['witness']['b'])) for c in r['cells'] if c['feasibility']=='sat'}
        self.assertEqual(actual,{(0,0,3),(1,2,1)})
        s=spec();s['slots']=s['slots'][:1];s['slots'][0]['active']='choice'
        p=construct(s);a=solve(p,B)
        self.assertTrue(all(F(c['witness']['a'])==0 for c in a['cells'] if c['feasibility']=='sat' and not c['witness']['a:active']))
        self.record('genuine_choices',{'linked':r,'activation':a})

    def test_limits_and_unknown_bound_stages(self):
        p=construct(spec());out={}
        for field in B.__dict__:
            r=solve(p,replace(B,**{field:0}),p.outputs['cash'])
            self.assertNotEqual(r['status'],'ExactWithinScope');out[field]=r
        x=z3.Real('probe');p=Problem('unknown','test',variables={'probe':x});p.add('interval',z3.And(x>=0,x<=1))
        for target in ('optimize:lower','bound-proof:lower','attainment:lower'):
            class StageUnknown(Backend):
                def check(self,s,stage):return z3.unknown if stage==target else s.check()
                def optimize(self,s,stage):return z3.unknown if stage==target else s.check()
            r=solve(p,B,x,backend=StageUnknown());self.assertEqual(r['status'],'Unknown');self.assertFalse(r['bounds']['lower']['certified']);out[target]=r
        self.record('limits_bound_unknown',out)

    def test_posting_units_and_disclosure_rounding(self):
        s=spec();s['rounding_stage']='posting_half_even_quantized_units'
        for row in s['slots']:row['quantum']='1/100'
        s['observations']=[observation(s,'1003/100')]
        p=construct(s);r=solve(p,B)
        self.assertEqual({(int(c['witness']['a']),int(c['witness']['b'])) for c in r['cells'] if c['feasibility']=='sat'},{(0,3),(1,2),(2,1),(3,0)})
        obs=s['observations'][0];obs['domain']={'kind':'rounded','displayed':'10','quantum':'1','convention':'half_even'}
        rr=solve(construct(s),B);self.assertEqual(rr['coverage']['feasible'],16)
        obs['domain']['convention']=None
        self.assertEqual(solve(construct(s),B)['status'],'PartialSearch')
        s['rounding_stage']='unspecified'
        with self.assertRaises(ValueError):construct(s)
        self.record('posting_disclosure',{'quantized':r,'displayed':rr})

    def test_fraction_rewrite_and_nonlinearity(self):
        f,d=z3.Reals('num den');records=[]
        for sign in (1,-1):
            p=Problem('ratio','test',variables={'num':f,'den':d})
            p.add('denominator',d==sign*4)
            rewritten=fixed_fraction_constraint(f,d,'<=','1/2',[e for _,e in p.constraints],B)
            p.add('fraction',rewritten)
            good=solve(p,B,extra=[f==sign]);bad=solve(p,B,extra=[f==sign*3])
            self.assertEqual(good['feasibility'],'Feasible');self.assertEqual(bad['status'],'Infeasible');records.append(good)
        with self.assertRaises(UnsupportedFragment):fixed_fraction_constraint(f,d,'<=','1/2',[],B)
        s=spec();s['mappings']['unsupported']=['sin','a'];self.assertEqual(solve(construct(s),B)['status'],'UnsupportedFragment')
        s=spec();s['mappings']['unsupported']=['*','a','b'];self.assertEqual(solve(construct(s),B)['status'],'UnsupportedFragment')
        with self.assertRaises(ValueError):q(.1)
        self.record('fraction_fragment',records)

    def test_northstar_known_history_and_renaming(self):
        fixture=json.loads((ROOT/'docs/design/fixtures/northstar.json').read_text())
        events=[e for e in fixture['historical_events'] if e['id'] in ('2024H1.sale','2024H1.collect')]
        s=spec();s['scope']='Northstar selected receivables bridge';s['exclusions']=['all other Northstar events and full-company accounting']
        s['opening']={k:fixture['opening'].get(k,'0') for k in ('cash','receivables','revenue')};s['economic_opening']={}
        s['templates']={'sale':{'postings':{'receivables':'1','revenue':'-1'},'state':{},'provenance':['northstar.json:2024H1.sale']},'collect':{'postings':{'cash':'1','receivables':'-1'},'state':{},'provenance':['northstar.json:2024H1.collect']}}
        s['slots']=[{'id':'sales','date':'T1','template':'sale','kind':'Real','active':True},{'id':'collections','date':'T1','template':'collect','kind':'Real','active':True}]
        s['mappings']={'cash':'balance:T1:cash','receivables':'balance:T1:receivables','revenue':'balance:T1:revenue'}
        replay={k:F(v) for k,v in s['opening'].items()}
        for e in events:
            for posting in e['postings']:replay[posting['account']]+=F(posting['signed_amount'])
        self.assertEqual(len(events),2)
        s['observations']=[]
        for k,v in replay.items():
            o=observation(s,v);o.update(id='northstar:'+k,mapping=k,source=['docs/design/fixtures/northstar.json']);s['observations'].append(o)
        p=construct(s);r=solve(p,B,p.variables['sales']);self.assertEqual(r['status'],'ExactWithinScope')
        self.assertEqual(r['bounds']['lower']['value'],'110');self.assertEqual(r['bounds']['upper']['value'],'110')
        for c in r['cells']:
            if c['feasibility']=='sat':self.assertEqual({k:F(v) for k,v in c['outputs'].items()},replay)
        s['slots'][0]['id']='renamed-sales';s['slots'].reverse();rr=solve(construct(s),B)
        self.assertEqual(rr['cells'][0]['outputs'],r['cells'][0]['outputs'])
        self.record('northstar_bridge',{'inputs':s,'replayed':{k:str(v) for k,v in replay.items()},'result':r})

    def test_input_validation_and_probability_mass(self):
        for mutate in ('template','kind','balance','date'):
            s=spec()
            if mutate=='template':s['slots'][0]['template']='absent'
            elif mutate=='kind':s['slots'][0]['kind']='Float'
            elif mutate=='balance':s['templates']['sale']['postings']['Cash']='2'
            else:s['slots'][0]['date']='outside'
            with self.assertRaises(ValueError):construct(s)
        m=FiniteMeasure([{'id':'a','hypothesis':{'economic_state':'a'},'weight':'1/4','status':'default','outcome':None}, {'id':'b','hypothesis':{'economic_state':'b'},'weight':'1/4','status':'unresolved','outcome':None}, {'id':'c','hypothesis':{'economic_state':'c'},'weight':'1/2','status':'complete','outcome':'10'}], 'synthetic disjoint economic hypotheses')
        self.assertEqual(m.event(['a','b']),F(1,2))
        self.assertEqual(m.summary()['mass'],{'default':'1/4','unresolved':'1/4','complete':'1/2'});self.assertIsNone(m.summary()['mean'])
        with self.assertRaises(ValueError):FiniteMeasure([{'id':'same','weight':'1/2'},{'id':'same','weight':'1/2'}],'invalid duplicate')
        bad={'id':'x','scope':'test','provenance':['test'],'dependencies':[],'kind':'AccountingElection','package':'Demo','permitted_treatments':['FIFO'],'election':'LIFO'}
        with self.assertRaises(ValueError):admit(bad)
        with self.assertRaises(ValueError):
            FiniteMeasure([{'id':'one','hypothesis':{'x':1},'weight':'1/2'}, {'id':'two','hypothesis':{'x':1},'weight':'1/2'}],'overlap')
        with self.assertRaises(ValueError):m.update({'a':'1','b':'1','c':'1'},['same','same'])
        self.record('input_validation_mass',m.summary())

    def test_exact_input_boundaries(self):
        for value in ({'n':1.5,'d':2}, {'n':'3/2','d':2}, {'n':True,'d':2},
                      {'n':1,'d':0}, {'n':1,'d':2,'rounded':True}):
            with self.subTest(value=value), self.assertRaises(ValueError):q(value)
        self.assertEqual(rational({'n':'3','d':'-6'}),F(-1,2))
        x=z3.Real('domain-x')
        for d in ({}, {'kind':'interval'}, {'lower':'0','lower_closed':'false'},
                  {'kind':'exact','lower':'0','upper':'1','lower_closed':True,'upper_closed':True}):
            with self.subTest(domain=d), self.assertRaises(ValueError):domain_formula(x,d)
        with self.assertRaises(UnsupportedFragment):domain_formula(x,{'kind':'finite','values':[1,3]})
        s=spec();s['symbols']=[{'id':'balance:T2:Cash','kind':'Real','domain':{'lower':None,'upper':None}}]
        with self.assertRaises(ValueError):construct(s)
        s=spec();s['observations']=[observation(s,13)];s['observations'][0]['domain']={}
        with self.assertRaises(ValueError):construct(s)
        contracts=[{'id':'duplicate','principal':'10','rate':'1/20','reset':'fixed','maturity':'2030','hedge':'none'}]*2
        with self.assertRaises(ValueError):group_contracts(contracts,{'rate':'1/20','year_fraction':'1'},['2026','2027'])
        for values in ([0,0], [False,1], []):
            p=Problem('invalid-domain','test',variables={'k':z3.Int('k')},finite={'k':values})
            with self.assertRaises(ValueError):solve(p,B)
        self.record('exact_input_boundaries',{'rational_records':'reject lossy coercion',
                    'domains':'explicit flags and bounds required','identities':'collisions and duplicate contracts rejected'})

    def test_large_integer_domain_and_partition_oracle(self):
        k=z3.Int('large-k');size=10**30
        p=Problem('large bounded integer','test',variables={'k':k},finite={'k':range(size)})
        r=solve(p,replace(B,max_cells=1,max_integer_assignments=1),k)
        self.assertEqual(r['status'],'PartialSearch');self.assertEqual(r['coverage']['total'],size)
        self.assertEqual(r['coverage']['completed'],1)
        self.assertEqual(r['coverage']['unvisited']['stop_ordinal'],size)
        self.assertFalse(r['bounds']['upper']['certified'])
        self.assertEqual(list(lazy_product([range(2),range(3)])),list(product(range(2),range(3))))
        p=Problem('overlapping guards','test',variables={'k':k},finite={'k':range(-2,5)})
        p.add('overlap',z3.Or(k<=1,k>=0));p.add('hole',z3.Not(k==2))
        r2=solve(p,B,k)
        actual=[int(c['witness']['k']) for c in r2['cells'] if c['feasibility']=='sat']
        expected=[n for n in range(-2,5) if (n<=1 or n>=0) and n!=2]
        self.assertEqual(sorted(actual),expected);self.assertEqual(len(actual),len(set(actual)))
        self.assertEqual(r2['status'],'ExactWithinScope');self.assertEqual(r2['coverage']['unresolved'],0)
        self.record('large_domain_partition',{'large_domain':r,'independent_integer_oracle':expected,'partition':r2})

    def test_p03_changed_principal_and_rates(self):
        evidence=[]
        for principal,fixed,stress in ((150,'0.04','0.09'),(80,'0.06','0.03')):
            source=BASE.replace('100 USD',f'{principal} USD').replace('0.05 per year',fixed+' per year').replace('0.07 per year',stress+' per year')
            bound=bindings(principal);compiled=compile_source(source,bound)
            self.assertTrue(compiled.ok)
            p=from_p03(compiled.ir,bound,{'DemoDebt@1/DebtMix':'fixed-floating-amounts-v1'})
            result=solve(p,B,p.outputs['interest'])
            endpoints=sorted([F(principal)*F(fixed),F(principal)*F(stress)])
            self.assertEqual([F(result['bounds'][d]['value']) for d in ('lower','upper')],endpoints)
            conditional=solve(p,B,p.outputs['interest'],selected_views=['allFixed'])
            self.assertEqual([F(conditional['bounds'][d]['value']) for d in ('lower','upper')],[F(principal)*F(fixed)]*2)
            middle=solve(p,B,extra=[p.variables['alpha']==q('1/2')])
            self.assertEqual(middle['coverage']['total'],1)
            self.assertEqual(F(middle['cells'][0]['outputs']['interest']),F(principal)*(F(fixed)+F(stress))/2)
            evidence.append({'principal':principal,'rates':[fixed,stress],'oracle_endpoints':list(map(str,endpoints)),
                             'parent':result,'fixed':conditional,'interior':middle})
        self.record('p03_metamorphic_rates',evidence)


class CheckerProvenanceTests(unittest.TestCase):
    """Exercise checker admission and reporting in disposable repository trees."""
    CURRENT_PLAN='data/accounting-master/runs/recovery-test/P04/approved-plan.json'
    CURRENT_INVENTORY='data/accounting-master/runs/recovery-test/P04/execution-0/pre-edit-files.json'

    def setUp(self):
        import check_accounting_p04 as checker
        self.checker=checker
        self.temporary=tempfile.TemporaryDirectory(prefix='accdsl-p04-provenance-')
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        required=['docs/design/fixtures/borrowings.json','docs/design/fixtures/northstar.json',
                  'scripts/core0_ir_v1.py','protected.txt']
        for name in checker.SOURCES+checker.OUTPUTS+required:
            self.write(name,'existing content: '+name)
        for name,summary in ((checker.ORIGINAL_PLAN,'Original design'),(self.CURRENT_PLAN,'Recovery plan')):
            plan={k:[] for k in ('steps','assumptions','checks','evidence','issues','residuals','next_actions')}
            plan.update(verdict='PLAN',summary=summary)
            review=dict(plan,verdict='AGREE',summary='Reviewed')
            plan_hash=hashlib.sha256(json.dumps(plan,sort_keys=True,ensure_ascii=False,
                                               separators=(',',':')).encode()).hexdigest()
            self.write(name,json.dumps({'plan':plan,'review':review,'plan_hash':plan_hash}))
        self.approval=(self.root/self.CURRENT_PLAN).read_text()
        historical={p:checker.digest(self.root/p) for p in required}
        historical['protected.txt']=hashlib.sha256(b'older protected version').hexdigest()
        self.write(checker.HISTORICAL_INVENTORY,json.dumps(historical))
        self.baseline={p:checker.digest(self.root/p) for p in checker.SOURCES+checker.OUTPUTS+required}
        self.inventory=json.dumps(self.baseline)
        self.write(self.CURRENT_INVENTORY,self.inventory)
        self.output_before={p:(self.root/p).read_bytes() for p in checker.OUTPUTS}

    def write(self,name,content):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)

    def args(self,plan=None,inventory=None):
        return ['--output-dir',str(self.root/'data/accounting-master/deliverables/P04'),
                '--execution-inventory',inventory or self.CURRENT_INVENTORY,
                '--approved-plan',plan or self.CURRENT_PLAN]

    def assert_rejected_before_execution(self,args):
        with patch.object(self.checker,'ROOT',self.root), patch.object(self.checker,'execute_checks') as run:
            with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as exc:
                self.checker.main(args)
            self.assertEqual(exc.exception.code,2);run.assert_not_called()
        self.assertEqual({p:(self.root/p).read_bytes() for p in self.checker.OUTPUTS},self.output_before)

    def test_checker_rejects_bad_approvals_before_writes(self):
        self.assert_rejected_before_execution(self.args(plan=self.CURRENT_PLAN.replace('recovery-test','missing'),
                                                      inventory=self.CURRENT_INVENTORY.replace('recovery-test','missing')))
        cases=['{','[]','{}',self.approval.replace('"AGREE"','"REVISE"'),
               self.approval.replace('"plan_hash": "','"plan_hash": "bad'),
               '{"plan": {}, "plan": {}}']
        for field,value in [('issues',['unresolved']),('issues',None),('checks','not a list')]:
            record=json.loads(self.approval);record['review'][field]=value;cases.append(json.dumps(record))
        for content in cases:
            with self.subTest(content=content[:70]):
                self.write(self.CURRENT_PLAN,content)
                self.assert_rejected_before_execution(self.args())
        self.write(self.CURRENT_PLAN,self.approval)
        self.assert_rejected_before_execution(self.args(plan=str(self.root/self.CURRENT_PLAN)))
        self.assert_rejected_before_execution(self.args(plan='../outside.json'))
        OBSERVATIONS.append({'obligation':'checker_approval_rejection','passed':True,
                             'result':{'invalid_records':len(cases),'executed_checks':0,'existing_outputs_preserved':True}})

    def test_checker_rejects_bad_inventories_before_writes(self):
        missing=self.CURRENT_INVENTORY.replace('execution-0','execution-1')
        self.assert_rejected_before_execution(self.args(inventory=missing))
        self.assert_rejected_before_execution(self.args(inventory=self.checker.HISTORICAL_INVENTORY))
        self.assert_rejected_before_execution(self.args(inventory=self.CURRENT_INVENTORY.replace('recovery-test','other-run')))
        omitted=dict(self.baseline);omitted.pop('protected.txt')
        wrong=dict(self.baseline);wrong['protected.txt']='0'*64
        cases=['{','{}','[]','{"protected.txt":"invalid"}',json.dumps(omitted),json.dumps(wrong),
               '{"protected.txt":"'+('0'*64)+'","protected.txt":"'+('1'*64)+'"}']
        for content in cases:
            with self.subTest(content=content[:70]):
                self.write(self.CURRENT_INVENTORY,content)
                self.assert_rejected_before_execution(self.args())
        self.write(self.CURRENT_INVENTORY,self.inventory)
        self.write(self.checker.HISTORICAL_INVENTORY,'{}')
        self.assert_rejected_before_execution(self.args())
        OBSERVATIONS.append({'obligation':'checker_inventory_rejection','passed':True,
                             'result':{'invalid_records':len(cases),'historical_fallback_rejected':True,'existing_outputs_preserved':True}})

    def simulated_checks(self,passed=True):
        # Only reporting is stubbed here; the ordinary numerical tests run separately.
        report={'methods':1,'failures':0 if passed else 1,'errors':0,'skips':0,
                'passed':passed,'output':'simulated test outcome for checker reporting'}
        status={'required':1,'observed':1,'missing':[],'uncatalogued':[],
                'duplicate_ids':[],'failed_observations':[]}
        return {'P04':report,'P03_regression':dict(report)},[],status,{'unsupported':['outside test scope']}

    def run_checker(self,passed=True):
        with patch.object(self.checker,'ROOT',self.root),patch.object(self.checker,'execute_checks',return_value=self.simulated_checks(passed)):
            with redirect_stdout(io.StringIO()):code=self.checker.main(self.args())
        payload=json.loads((self.root/self.checker.OUTPUTS[0]).read_text())
        result=(self.root/self.checker.OUTPUTS[1]).read_text()
        return code,payload,result

    def test_checker_manifest_uses_current_provenance(self):
        changed=self.checker.SOURCES[0];self.write(changed,'changed implementation in disposable tree')
        code,payload,result=self.run_checker()
        self.assertEqual(code,0);self.assertTrue(payload['passed'])
        manifest=payload['manifest'];protection=payload['protection']
        for key,name in [('plan',self.CURRENT_PLAN),('original_design_plan',self.checker.ORIGINAL_PLAN),
                         ('execution_inventory',self.CURRENT_INVENTORY),('historical_inventory',self.checker.HISTORICAL_INVENTORY)]:
            self.assertEqual(manifest[key],name)
            self.assertEqual(manifest[key+'_sha256'],self.checker.digest(self.root/name))
            self.assertIn(name,payload['input_source_test_hashes'])
        self.assertNotEqual(manifest['plan_sha256'],manifest['original_design_plan_sha256'])
        self.assertEqual(manifest['approved_plan_hash'],json.loads(self.approval)['plan_hash'])
        self.assertEqual(manifest['changed_source_code_test_files'],[changed])
        self.assertEqual(manifest['changed_files'],[changed]+self.checker.OUTPUTS[:2])
        self.assertEqual(protection['excluded_phase_files'],self.checker.SOURCES+self.checker.OUTPUTS)
        self.assertEqual(protection['execution_inventory'],self.CURRENT_INVENTORY)
        self.assertEqual(protection['execution_baseline']['protected.txt'],self.baseline['protected.txt'])
        self.assertEqual([x['path'] for x in protection['historical_differences']],['protected.txt'])
        self.assertTrue(protection['passed']);self.assertIn(self.CURRENT_PLAN,result)
        OBSERVATIONS.append({'obligation':'checker_current_provenance','passed':True,
                             'result':{'current_approval_and_inventory_used':True,'historical_difference_retained':True,
                                       'unchanged_exclusions':True,'actual_change_selection':True}})

    def test_checker_failure_report_does_not_claim_success(self):
        code,payload,result=self.run_checker(passed=False)
        self.assertEqual(code,1);self.assertFalse(payload['passed']);self.assertFalse(payload['acceptance']['engineering'])
        self.assertIn('FAIL:',result);self.assertIn('No numerical certification',result)
        self.assertNotIn('Exact debt interest ranges',result)
        self.assertNotIn('This establishes these tested invariants',result)
        OBSERVATIONS.append({'obligation':'checker_failure_reporting','passed':True,
                             'result':{'failure_exit':code,'engineering_acceptance':False,'success_prose_absent':True}})
