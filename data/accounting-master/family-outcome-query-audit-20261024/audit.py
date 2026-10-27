"""Bounded deterministic query probes; no public family interface or adoption."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import hashlib,json,os,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import sequential_return_state_family_v1 as seq
from test_sequential_return_state_family_v1 import fixture,observation
from test_piecewise_method_family_v1 import BUDGET
solver,z3=seq.solver,seq.z3
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def run():
    checks=[];out=[]
    def check(name,x):checks.append({'name':name,'passed':bool(x)})
    def inspect(name,d,prefix,account,value):
        branches,_,missing,_,_,stop=seq.compile_selection(d,BUDGET)
        assert not missing and stop is None
        rows=[];target=Q(value)
        for i,b in enumerate(branches):
            x=b['sale']['prefix'+str(prefix)][account]
            # Exact disjoint complement avoids treating only one sign cell as all !=.
            for sign,predicate in [('equal',x==solver.q(value)),('less',x<solver.q(value)),('greater',x>solver.q(value))]:
                r=solver.solve(b['problem'],solver.Budget(**BUDGET),extra=(predicate,))
                row={'branch':i,'region':sign,'feasibility':r['feasibility'],'coverage':r['coverage']}
                if r['feasibility']=='Feasible':
                    c=next(c for c in r['cells'] if c['feasibility']=='sat')
                    w={k:seq.native.monetary.fmt(Q(v)) for k,v in c['witness'].items()}
                    replay=seq.replay_witness(d,BUDGET,i,w)
                    state=replay['first']['after'] if prefix==1 else replay['after'];actual=Q(state['balances'][account])
                    check(name+'.'+str(i)+'.'+sign+'_original_predicate',{'equal':actual==target,'less':actual<target,'greater':actual>target}[sign])
                    row.update(witness=w,value=str(actual),original_full_replay_checked=True)
                elif r['feasibility']=='Infeasible':
                    check(name+'.'+str(i)+'.'+sign+'_checked_unsat',r['coverage']['complete'] and all(c['conflict']['rechecked']=='unsat' for c in r['cells']))
                rows.append(row)
        yes=any(r['region']=='equal' and r['feasibility']=='Feasible' for r in rows)
        no=any(r['region']!='equal' and r['feasibility']=='Feasible' for r in rows)
        all_equal_empty=all(r['feasibility']=='Infeasible' for r in rows if r['region']=='equal')
        all_complement_empty=all(r['feasibility']=='Infeasible' for r in rows if r['region']!='equal')
        verdict=('contingent' if yes and no else 'necessary' if yes and all_complement_empty
                 else 'impossible' if no and all_equal_empty else 'empty_family' if all_equal_empty and all_complement_empty else 'unknown')
        out.append({'name':name,'definition_sha256':seq.core.digest(d),'prefix':prefix,'account':account,'value':value,'verdict':verdict,'regions':rows})
        return verdict
    check('terminal_inventory_necessary',inspect('terminal_inventory',fixture(),2,'inventory','60/1')=='necessary')
    check('intermediate_inventory_contingent',inspect('intermediate_inventory',fixture(),1,'inventory','65/1')=='contingent')
    check('unattainable_intermediate_inventory',inspect('below_minimum',fixture(),1,'inventory','64/1')=='impossible')
    selected=fixture();selected['observations']=[observation(selected,1,'inventory','65/1')]
    check('observed_intermediate_necessary',inspect('selected_middle',selected,1,'inventory','65/1')=='necessary')
    unfunded=fixture();s=unfunded['first_family']['state'];cash=Q(s['balances']['cash']);s['balances']['cash']='1/1'
    s['balances']['original_equity']=seq.native.monetary.fmt(Q(s['balances']['original_equity'])+cash-1)
    check('empty_not_necessary',inspect('unfunded',unfunded,2,'inventory','60/1')=='empty_family')
    b,_,_,_,_,_=seq.compile_selection(fixture(),BUDGET);x=b[0]['sale']['prefix1']['inventory']
    small={**BUDGET,'max_cells':1}
    negated=solver.solve(b[0]['problem'],solver.Budget(**small),extra=(z3.Not(x==65),))
    check('negated_equality_partial_cells_not_empty',negated['feasibility']=='Unknown' and negated['coverage']['total']==3 and negated['coverage']['complete'] is False)
    out.append({'name':'negated_equality_one_cell','result':negated})
    open_family=fixture();dom=open_family['first_family']['event_domains']['inventory_nrv']['interval'];dom.update(upper='20/1',upper_inclusive=False)
    check('strict_upper_excluded',inspect('open_upper',open_family,1,'inventory','80/1')=='impossible')
    b,_,_,_,_,_=seq.compile_selection(fixture(),BUDGET)
    constant=solver.solve(b[0]['problem'],solver.Budget(**BUDGET),objective=b[0]['sale']['prefix2']['inventory'])
    check('constant_endpoint_proved',all(v['certified'] and v['value']=='60' and v['attained'] for v in constant['bounds'].values()))
    check('first_witness_not_whole_range',constant['coverage']['complete'])
    out.append({'name':'constant_endpoint','result':constant})
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'probes':out}
def main():
    mode=sys.argv[1] if len(sys.argv)>1 else '--check';assert mode in ['--check','--record','--replay']
    clock=time.monotonic()
    if mode=='--replay':
        for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(ROOT/n)==h,n
    result=run();assert result['passed'],[x['name'] for x in result['checks'] if not x['passed']]
    if mode=='--record':
        assert not (HERE/'audit.json').exists();dump(HERE/'audit.json',result)
        names=['scripts/sequential_return_state_family_v1.py','scripts/conditional_return_state_family_v2.py',
          'scripts/rational_solver_v1.py','tests/test_sequential_return_state_family_v1.py',
          'data/accounting-master/sequential-return-state-family-20261024/manifest.json',
          'docs/plans/accounting-family-outcome-query-audit-20261024.md']
        files={n:sha(ROOT/n) for n in names};files.update({str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.json','.md'] and p.name!='manifest.json'})
        import subprocess,platform
        dump(HERE/'manifest.json',{'files':files,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'command':'python3 -B '+str(HERE.relative_to(ROOT)/'audit.py')+' --record','environment':'Python '+platform.python_version()+'; Z3 '+z3.get_version_string(),
          'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: exact deterministic probes; no ranking',
          'wall_seconds':time.monotonic()-clock,'plan':names[-1],'result':str(HERE.relative_to(ROOT)/'result.md')})
    if mode=='--replay':assert result['checks']==json.loads((HERE/'audit.json').read_text())['checks']
    print(json.dumps({'mode':mode,'passed':True,'checks':len(result['checks']),'probes':len(result['probes']),'wall_seconds':time.monotonic()-clock}))
if __name__=='__main__':main()
