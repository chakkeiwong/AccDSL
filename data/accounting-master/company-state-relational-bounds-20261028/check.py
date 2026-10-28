"""Exact original projection/dependence/sample discriminators, no defaults."""
import argparse
from dataclasses import replace
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'scripts'))
import z3
from rational_solver_v1 import Problem,Budget,q,solve
BUDGET=Budget(10,10000,100,100,10000,1000,1000000)
PLAN='docs/plans/company-state-relational-bounds-20261028.md'
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    out=ap.parse_args().output.resolve();out.mkdir(exist_ok=False);start=time.monotonic()
    checks=[];results=[];formulas=[]
    def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
    def sr(n,p,obj=None,extra=(),budget=BUDGET):
        formulas.append(dict(id=n,constraints=[dict(label=k,expression=v.sexpr()) for k,v in p.constraints],extra=[x.sexpr() for x in extra],objective=obj.sexpr() if obj is not None else None,outputs={k:v.sexpr() for k,v in p.outputs.items()},provenance=p.provenance))
        r=solve(p,budget,obj,extra=extra);results.append(dict(id=n,result=r));return r
    def bounds(n,r,lower,upper):
        ck(n+'/feasible',r['feasibility'],'Feasible');ck(n+'/complete',r['coverage'].get('complete'),True)
        for side,value in [('lower',lower),('upper',upper)]:
            b=r.get('bounds',{}).get(side,{})
            ck(n+'/'+side+'/exact value',Q(b['value']) if b.get('status')=='Finite' else b.get('status'),Q(value))
            ck(n+'/'+side+'/certified',b.get('certified'),True);ck(n+'/'+side+'/attained',b.get('attained'),True)
    x,z=z3.Reals('x z');p=Problem('Original projection x=z+1,z in[0,2]','explicit affine example')
    p.variables=dict(x=x,z=z);p.add('link',x==z+1);p.add('z_lower',z>=0);p.add('z_upper',z<=2);p.outputs=dict(x=x)
    p.provenance=dict(original_row='SIM-F047',projection_target='x',probability=None)
    bounds('projection bounds',sr('projection bounds',p,x),1,3)
    for value,valid in [(0,False),(1,True),(2,True),(3,True),(4,False)]:
        r=sr('projection member'+str(value),p,extra=[x==value]);ck('projection member'+str(value),r['feasibility'],'Feasible' if valid else 'Infeasible')
    original=z3.And(*[v for _,v in p.constraints]);qe=z3.Tactic('qe')(z3.Exists([z],original)).as_expr()
    expected=z3.And(x>=1,x<=3);s=z3.Solver();s.add(z3.Xor(qe,expected));qe_result=str(s.check())
    ck('affine elimination equivalence',qe_result,'unsat')
    dump(out/'projection-equivalence.json',dict(original=original.sexpr(),quantified=z3.Exists([z],original).sexpr(),eliminated=qe.sexpr(),expected=expected.sexpr(),equivalence_counterexample=qe_result,scope='This affine example only; direct Z3 tactic, not generic native projection service'))
    wrong=Problem('Deliberately dropped relation and latent range','wrong projection control');wrong.variables=dict(x=x);wrong.outputs=dict(x=x);wrong.provenance=dict(negative_control=True)
    for value in [0,4]:ck('dropped constraints admit'+str(value),sr('dropped'+str(value),wrong,extra=[x==value])['feasibility'],'Feasible')
    a,b=z3.Ints('type1 type2')
    for persistent in [True,False]:
        p=Problem('Original persistent paths' if persistent else 'Rectangular enlargement control','unweighted finite alternatives')
        p.variables=dict(type1=a,type2=b);p.finite=dict(type1=[0,1],type2=[0,1])
        if persistent:p.add('persistent_type',a==b)
        first,second=10*a,10*(1-b);p.outputs=dict(first=first,second=second,total=first+second)
        p.provenance=dict(original_row='SIM-F048',persistent=persistent,probability=None)
        found=[]
        for u,v in product([0,10],repeat=2):
            n=f'paths{persistent}/{u},{v}';r=sr(n,p,extra=[first==u,second==v]);valid=(u+v==10) if persistent else True
            ck(n,r['feasibility'],'Feasible' if valid else 'Infeasible')
            if r['feasibility']=='Feasible':found.append([u,v])
        ck('exact support'+str(persistent),found,[[0,10],[10,0]] if persistent else [[0,0],[0,10],[10,0],[10,10]])
        bounds('path sum'+str(persistent),sr('path sum'+str(persistent),p,first+second),10 if persistent else 0,10 if persistent else 20)
    ck('sum of stagewise maxima is false persistent path',max(0,10)+max(10,0),20)
    x,y=z3.Reals('shared_x copied_y')
    p=Problem('Original shared x-x','same variable identity');p.variables=dict(x=x);p.add('lower',x>=0);p.add('upper',x<=1);p.outputs=dict(difference=x-x);p.provenance=dict(original_row='SIM-F050',shared_identity=True)
    bounds('shared subtraction',sr('shared subtraction',p,x-x),0,0)
    p=Problem('Independent interval-copy control','deliberate dependence loss');p.variables=dict(x=x,y=y)
    for key,var in [('x',x),('y',y)]:p.add(key+'_lower',var>=0);p.add(key+'_upper',var<=1)
    p.outputs=dict(difference=x-y);p.provenance=dict(original_row='SIM-F050',shared_identity=False,negative_control=True)
    bounds('independent subtraction',sr('independent subtraction',p,x-y),-1,1)
    p.add('restored_identity',x==y);bounds('restored subtraction',sr('restored subtraction',p,x-y),0,0)
    alpha=z3.Real('alpha');p=Problem('Full original alpha domain','exact rational endpoint example')
    p.variables=dict(alpha=alpha);p.add('lower',alpha>=0);p.add('upper',alpha<=1);p.outputs=dict(loss=1-alpha);p.provenance=dict(original_row='SIM-F051',sampled=False)
    bounds('full loss range',sr('full loss range',p,1-alpha),0,1)
    sample=[Q(i,10) for i in range(10)];losses=[1-a for a in sample]
    ck('sample maximum alpha',max(sample),Q(9,10));ck('sample minimum loss',min(losses),Q(1,10))
    ck('sample minimum is not full minimum',min(losses)==0,False)
    ck('endpoint witness',sr('unsampled endpoint',p,extra=[alpha==1])['feasibility'],'Feasible')
    remainder=sr('unsampled region',p,1-alpha,extra=[alpha>q(Q(9,10))])
    ck('remaining exact lower',Q(remainder['bounds']['lower']['value']),Q(0));ck('remaining lower attained',remainder['bounds']['lower']['attained'],True)
    ck('remaining upper sup',Q(remainder['bounds']['upper']['value']),Q(1,10));ck('remaining upper unattained',remainder['bounds']['upper']['attained'],False)
    u=sr('zero budget retains question',p,1-alpha,budget=replace(BUDGET,max_cells=0))
    ck('budget unknown',u['feasibility'],'Unknown');ck('budget incomplete',u['coverage'].get('complete'),False)
    ck('remaining formula retained',bool(u['coverage']['unvisited']['retained_formula']),True)
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    originals=[r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id'] in ['SIM-F047','SIM-F048','SIM-F050','SIM-F051']]
    ck('exact targets',[r['discriminating_case'] for r in originals],['x=z+1 with z in[0,2]','Paths(0,10),(10,0) become(10,10)','x-x or cash plus linked interest','Largest sampled alpha .9 misses true endpoint1'])
    for row in checks:
        for key in ['actual','expected']:
            if isinstance(row[key],Q):row[key]=str(row[key])
    failed=[c for c in checks if not c['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),solver_cases=len(results),failed=failed,original_rows=[r['id'] for r in originals],general_projection_service=False,empirical_sample_claim=False)
    for n,obj in [('verification',v),('checks',checks),('solver-results',results),('formulae',formulas),('original-rows',originals),('sample',dict(alpha=[str(x) for x in sample],loss=[str(x) for x in losses],probability=None))]:dump(out/(n+'.json'),obj)
    paths={Path(__file__),ROOT/PLAN,fm};paths.update(Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT))
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=dict(python=platform.python_version(),z3=z3.get_version_string()),cpu_gpu='CPU-only exact rational SMT; no GPU imports',random_seeds='N/A deterministic',data_version='Original four finite/affine scalar discriminators',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}))
    (out/'check.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(dict(status=v['status'],checks=len(checks),solver_cases=len(results),failed=[x['name'] for x in failed])));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
