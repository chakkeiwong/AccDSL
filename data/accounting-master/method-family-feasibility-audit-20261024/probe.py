"""Bounded engineering probes; no general method or solver promotion."""
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util,json,os,platform,subprocess,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import rational_solver_v1 as solver
import method_monetary_effects_v1 as effects
from test_method_monetary_effects_v1 import fixture
spec=importlib.util.spec_from_file_location('selected_method_programs',
    ROOT/'data/accounting-master/typed-monetary-effects-20261024/examples.py')
programs=importlib.util.module_from_spec(spec);spec.loader.exec_module(programs)
z3=solver.z3
PLAN='docs/plans/accounting-method-family-feasibility-audit-20261024.md'
SOURCES=[PLAN,'scripts/rational_solver_v1.py','scripts/method_monetary_effects_v1.py',
 'scripts/typed_return_transition_v1.py','scripts/typed_affine_history_v1.py',
 'scripts/history_measurement_attachment_v1.py','scripts/conditional_family_text_v1.py',
 'tests/test_method_monetary_effects_v1.py',
 'data/accounting-master/typed-monetary-effects-20261024/examples.py']
BUDGET={'max_slots':0,'max_formula_nodes':1000,'max_integer_assignments':1,'max_cells':1,
        'elapsed_ms':5000,'solver_timeout_ms':1000,'solver_rlimit':1000000}

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

def inspect(definition,pinned):
    symbols={k:{'symbolic':k not in pinned,'class':'fixed' if k in pinned else 'affine'}
             for k in definition['inputs']}
    rows=[]
    def walk(node,path):
        op=node['op']
        if op=='ref':answer=dict(symbols[node['id']])
        elif op=='const':answer={'symbolic':False,'class':'fixed'}
        else:
            a,b=walk(node['left'],path+'/left'),walk(node['right'],path+'/right')
            if 'nonlinear_product' in [a['class'],b['class']]:kind='nonlinear_product'
            elif op=='mul' and a['symbolic'] and b['symbolic']:kind='nonlinear_product'
            elif op=='min' and (a['symbolic'] or b['symbolic']):kind='piecewise_affine'
            elif 'piecewise_affine' in [a['class'],b['class']]:kind='piecewise_affine'
            else:kind='affine' if a['symbolic'] or b['symbolic'] else 'fixed'
            answer={'symbolic':a['symbolic'] or b['symbolic'],'class':kind}
        rows.append({'path':path,'op':op,**answer})
        return answer
    for group in ['calculations','postings','flows']:
        for row in definition[group]:
            answer=walk(row['expression'],group+'/'+row['id'])
            if group=='calculations':symbols[row['id']]=answer
    return rows

def run():
    checks=[];observations=[]
    def check(name,condition):checks.append({'name':name,'passed':bool(condition)})
    d,values=fixture();known=programs.run(d,values)
    check('known_native_monetary_comparator',known['status']=='derived' and known['journal']['inventory']=='19/1')
    inventory={}
    for kind in ['settle','sell']:
        definition=programs.program(kind,{'entity':'Audit','book_role':'authored','at':'2024-01-01'},list(d['accounts']))
        effects.compile_definition(definition)
        inventory[kind]={'definition':definition,'all_unknown':inspect(definition,set()),
                         'fixed_unit_coefficients':inspect(definition,{'p','c','d','h'})}
    check('settlement_has_genuine_unknown_product',any(r['class']=='nonlinear_product' for r in inventory['settle']['all_unknown']))
    check('pinned_settlement_is_piecewise_affine',any(r['class']=='piecewise_affine' for r in inventory['settle']['fixed_unit_coefficients']) and
          all(r['class']!='nonlinear_product' for r in inventory['settle']['fixed_unit_coefficients']))
    check('sale_formula_is_affine',all(r['class'] in ['fixed','affine'] for r in inventory['sell']['all_unknown']))
    x,y=z3.Reals('audit.x audit.y')
    for label,formula in [('unknown_product',y==x*x),('arithmetic_if',y==z3.If(x<=20,x,20))]:
        p=solver.Problem(label,'authored_probe',variables={'x':x,'y':y});p.add('definition',formula)
        r=solver.solve(p,solver.Budget(**BUDGET));check(label+'_unsupported',r['status']=='UnsupportedFragment')
        observations.append({'case':label,'status':r['status'],'reason':r.get('reason')})
    p=solver.Problem('min_disjunction','authored_probe',variables={'x':x,'y':y})
    p.add('min',z3.Or(z3.And(x<=20,y==x),z3.And(x>20,y==20)))
    r=solver.solve(p,solver.Budget(**BUDGET))
    check('generic_disjunction_exceeds_one_cell',r['coverage']['total']>1 and not r['coverage'].get('complete',False))
    observations.append({'case':'min_disjunction','status':r['status'],'coverage':r['coverage'],
                         'predicate_count':len(r.get('partition_predicates',[]))})
    branches=[]
    for cap in ['5/1','20/1','25/1']:
        outcomes=[]
        for arm in ['left','right']:
            p=solver.Problem('min_explicit_'+arm,'authored_probe',variables={'x':x,'y':y})
            p.add('cap',x==solver.q(cap))
            p.add('branch',20<=x if arm=='left' else x<20)
            p.add('value',y==20 if arm=='left' else y==x)
            r=solver.solve(p,solver.Budget(**BUDGET));outcomes.append(r['feasibility'])
            check('branch_complete_'+cap+'_'+arm,r['coverage'].get('complete',False))
            if r['feasibility']=='Feasible':
                w=next(c['witness'] for c in r['cells'] if c['feasibility']=='sat')
                check('exact_min_'+cap,Q(w['y'])==min(Q(20),Q(cap)))
                branches.append({'cap':cap,'arm':arm,'witness':w,'fraction_expected':str(min(Q(20),Q(cap)))})
        check('one_disjoint_arm_'+cap,outcomes.count('Feasible')==1)
    # Exact logical proof for the authored min split: tie belongs to left only.
    proof=z3.Solver();proof.add(z3.Xor(z3.Or(20<=x,x<20),z3.BoolVal(True)))
    check('minimum_arms_exhaustive',proof.check()==z3.unsat)
    proof=z3.Solver();proof.add(20<=x,x<20);check('minimum_arms_disjoint',proof.check()==z3.unsat)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'operators':inventory,
            'probes':observations,'branch_examples':branches,'budget':BUDGET,
            'source_lock':{n:sha(ROOT/n) for n in SOURCES},
            'scope':'Fixed authored diagnostic; no general compiler, accounting admission or performance ranking'}

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'audit.json').exists()
    start=time.monotonic();result=run();assert result['passed'],[c for c in result['checks'] if not c['passed']]
    if mode=='--record':
        dump(HERE/'audit.json',result)
        dump(HERE/'probe-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'probe.py')+' --record',
            'environment':platform.python_version()+'; Z3 '+z3.get_version_string(),
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic exact probes',
            'wall_seconds':time.monotonic()-start,'data_version':result['source_lock'],
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),
            'output':{'audit.json':sha(HERE/'audit.json'),'probe.py':sha(HERE/'probe.py')}})
    if mode=='--replay':assert result==json.loads((HERE/'audit.json').read_text())
    print(json.dumps({'mode':mode,'passed':True,'checks':len(result['checks']),
        'sources':len(result['source_lock']),'probes':result['probes']}))

if __name__=='__main__':main()
