"""Source-bound exact range probes on complete native sequence problems."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,os,platform,subprocess,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from test_sequential_outcome_query_v1 import query,fixture,profit,observation,BUDGET
family,solver,z3=query.family,query.solver,query.z3
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def run():
    checks=[];probes=[]
    def check(n,v):checks.append({'name':n,'passed':bool(v)})
    def inspect(name,request,expected):
        query.validate(request,BUDGET)
        branches,_,missing,_,_,stop=family.compile_selection(request['family'],BUDGET)
        assert not missing and not stop
        rows=[]
        for i,branch in enumerate(branches):
            expr=query.expression(request,branch)
            r=solver.solve(branch['problem'],solver.Budget(**BUDGET),objective=expr)
            row={'branch':i,'feasibility':r['feasibility'],'bounds':r['bounds'],'coverage':r['coverage']}
            if r['feasibility']=='Feasible':
                check(name+'.'+str(i)+'.local_certified',all(e['certified'] for e in r['bounds'].values()))
                for cell in r['cells']:
                    if cell['feasibility']!='sat':continue
                    for side,endpoint in cell['bounds'].items():
                        check(name+'.'+str(i)+'.'+side+'_finite',endpoint['status']=='Finite')
                        value=solver.q(endpoint['value']);engine=z3.Solver();engine.set(timeout=1000,rlimit=1000000)
                        original=[x for _,x in branch['problem'].constraints]
                        engine.add(*original,expr<value if side=='lower' else expr>value)
                        check(name+'.'+str(i)+'.'+side+'_no_better',engine.check()==z3.unsat)
                        engine=z3.Solver();engine.set(timeout=1000,rlimit=1000000);engine.add(*original,expr==value)
                        check(name+'.'+str(i)+'.'+side+'_attainment',(engine.check()==z3.sat)==endpoint['attained'])
                        if endpoint['attained']:
                            w={k:query.native.monetary.fmt(Q(v)) for k,v in endpoint['witness'].items()}
                            replay=family.replay_witness(request['family'],BUDGET,i,w)
                            state=replay['first']['after'] if request['prefix']==1 else replay['after']
                            actual=sum((Q(t['coefficient'])*Q(state['balances'][t['account']]) for t in request['terms']),Q(0))
                            check(name+'.'+str(i)+'.'+side+'_native_replay',actual==Q(endpoint['value']))
            else:check(name+'.'+str(i)+'.empty_rechecked',r['feasibility']=='Infeasible' and r['coverage']['complete'] and all(c['conflict']['rechecked']=='unsat' for c in r['cells']))
            rows.append(row)
        feasible=[r for r in rows if r['feasibility']=='Feasible'];bounds={}
        if feasible:
            for side in ['lower','upper']:
                value=(min if side=='lower' else max)(Q(r['bounds'][side]['value']) for r in feasible)
                attained=any(r['bounds'][side]['attained'] for r in feasible if Q(r['bounds'][side]['value'])==value)
                bounds[side]={'value':str(value),'attained':attained}
        check(name+'.expected',bounds==expected)
        probes.append({'name':name,'request_sha256':query.core.digest(request),'branches':rows,'global_expected_bounds':bounds})
    def bounds(lo,hi,lc=True,hc=True):return {'lower':{'value':lo,'attained':lc},'upper':{'value':hi,'attained':hc}}
    inspect('middle_inventory',fixture(1),bounds('65','80'))
    inspect('terminal_inventory',fixture(),bounds('60','60'))
    inspect('middle_profit',profit(1),bounds('-19','-4'))
    inspect('terminal_profit',profit(),bounds('16','16'))
    d=fixture(1);d['family']['first_family']['event_domains']['inventory_nrv']['interval'].update(upper='20/1',upper_inclusive=False,lower_inclusive=False)
    inspect('both_open_middle',d,bounds('65','80',False,False))
    d=fixture(1);d['family']['observations']=[observation(d['family'],1,'inventory','65/1')]
    inspect('selected_middle',d,bounds('65','65'))
    d=profit();d['family']['sale_event']['proceeds']='unknown'
    from test_conditional_history_family_v1 import domain
    d['family']['proceeds_domain']=domain('0/1','100/1')
    d['family']['proceeds_domain']['source_ref']=family.parent.source_ref(query.core.digest(d['family']['sale_event']),'/proceeds')
    inspect('variable_proceeds_profit',d,bounds('-24','76'))
    d=fixture();s=d['family']['first_family']['state'];cash=Q(s['balances']['cash']);s['balances']['cash']='1/1'
    s['balances']['original_equity']=query.native.monetary.fmt(Q(s['balances']['original_equity'])+cash-1)
    inspect('unfunded_empty',d,{})
    branches,_,_,_,_,_=family.compile_selection(fixture(1)['family'],BUDGET)
    r=solver.solve(branches[0]['problem'],solver.Budget(**BUDGET),objective=query.expression(fixture(1),branches[0]))
    check('first_branch_is_not_whole_family',r['bounds']['lower']['value']=='80')
    probes.append({'name':'first_branch_only','local_bounds':r['bounds'],'global_lower_is_65':True,'global_certification':False})
    r=solver.solve(branches[0]['problem'],solver.Budget(**{**BUDGET,'max_cells':0}),objective=query.expression(fixture(1),branches[0]))
    check('zero_cells_no_bounds',r['feasibility']=='Unknown' and r['bounds'] is None)
    probes.append({'name':'zero_cells','status':r['status'],'bounds':r['bounds']})
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'probes':probes}
def main():
    mode=sys.argv[1] if len(sys.argv)>1 else '--check';assert mode in ['--check','--record','--replay'];clock=time.monotonic()
    if mode=='--replay':
        for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items():assert sha(ROOT/n)==h,n
    result=run();assert result['passed'],[c['name'] for c in result['checks'] if not c['passed']]
    if mode=='--record':
        assert not (HERE/'audit.json').exists();dump(HERE/'audit.json',result)
        names=['scripts/rational_solver_v1.py','scripts/sequential_return_state_family_v1.py','scripts/sequential_outcome_query_v1.py',
          'tests/test_sequential_outcome_query_v1.py','docs/plans/accounting-sequential-range-audit-20261024.md']
        files={n:sha(ROOT/n) for n in names};files.update({str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md','.json'] and p.name!='manifest.json'})
        dump(HERE/'manifest.json',{'files':files,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'command':'python3 -B '+str(HERE.relative_to(ROOT)/'audit.py')+' --record','environment':'Python '+platform.python_version()+'; Z3 '+z3.get_version_string(),
          'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic exact probes','wall_seconds':time.monotonic()-clock,
          'plan':names[-1],'result':str(HERE.relative_to(ROOT)/'result.md')})
    if mode=='--replay':assert result==json.loads((HERE/'audit.json').read_text())
    print(json.dumps({'mode':mode,'passed':True,'checks':len(result['checks']),'probes':len(result['probes']),'wall_seconds':time.monotonic()-clock}))
if __name__=='__main__':main()
