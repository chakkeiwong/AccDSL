"""Exact whole-domain financing regions, policy mismatch and external offer."""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'scripts'))
import z3
from rational_solver_v1 import Problem,Budget,q,solve
p=ROOT/'data/accounting-master/company-state-face-proceeds-failure-20261028/check.py'
s=importlib.util.spec_from_file_location('retained_face_proceeds_fixture',p);base=importlib.util.module_from_spec(s);s.loader.exec_module(base)
BUDGET=Budget(0,10000,1,16,5000,1000,1000000)
PLAN='docs/plans/company-state-pricing-policy-failures-20261028.md'
ANCHOR='docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation/26-finite-finance.tex'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def fmt(v):return base.fmt(v)

def price(face):return (min(Q(face),60)+min(Q(face),140))/2
def region(n,need=None):
    f=z3.Real('face');p=Problem('Original chapter26 whole nonnegative face partition','explicit synthetic price law')
    p.variables={'face':f}
    if n==0:p.add('safe_lower',f>=0);p.add('safe_upper',f<=60);proceeds=f
    elif n==1:p.add('risky_lower',f>60);p.add('risky_upper',f<=140);proceeds=q(30)+f/2
    else:p.add('flat_lower',f>140);proceeds=q(100)
    if need is not None:p.add('funding_need',proceeds==q(need))
    p.outputs=dict(proceeds=proceeds,face=f)
    p.provenance=dict(region=n,need=need,assets=[60,140],pricing_weights=['1/2','1/2'],gross_return=1,
        finite_upper_face_bound=None,source_admission=False,scope='Declared channel only; no claim that other funding channels fail')
    return p

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    out=ap.parse_args().output.resolve();out.mkdir(exist_ok=False);start=time.monotonic()
    checks=[];solver_results=[];formulae=[];native=[];policy=[]
    def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
    def sr(n,p,obj=None,extra=(),budget=BUDGET):
        r=solve(p,budget,obj,extra=extra);solver_results.append(dict(id=n,result=r));return r
    def preserve(n,p):formulae.append(dict(id=n,constraints=[dict(label=k,expression=v.sexpr()) for k,v in p.constraints],outputs={k:v.sexpr() for k,v in p.outputs.items()},provenance=p.provenance))
    text=(ROOT/ANCHOR).read_text()
    ck('retained need110 anchor','No face value raises 110 in this model' in text,True)
    ck('retained policy anchor','project R with assets zero or 180 equally likely' in text,True)
    for need,expected in [(0,[True,False,False]),(40,[True,False,False]),(60,[True,False,False]),(80,[False,True,False]),(100,[False,True,True]),(110,[False,False,False])]:
        found=[]
        for n in range(3):
            p=region(n,need);name=f'need{need}/region{n}';preserve(name,p);r=sr(name,p)
            ck(name+'/feasible',r['feasibility'],'Feasible' if expected[n] else 'Infeasible')
            ck(name+'/coverage',r['coverage'].get('complete'),True)
            found.append(r['feasibility']=='Feasible')
        ck(f'need{need}/all regions',found,expected)
    for face,expected in [(0,0),(40,40),(60,60),(100,80),(140,100),(1000000,100)]:
        matching=[]
        for n in range(3):
            p=region(n);r=sr(f'face{face}/region{n}',p,p.outputs['proceeds'],extra=[p.variables['face']==q(face)])
            member=(n==0 and face<=60) or (n==1 and 60<face<=140) or (n==2 and face>140)
            ck(f'face{face}/region{n}/membership',r['feasibility'],'Feasible' if member else 'Infeasible')
            if member:
                matching.append(n);ck(f'face{face}/price',[r['bounds'][k]['value'] for k in ['lower','upper']],[str(expected)]*2)
        ck(f'face{face}/one region',len(matching),1);ck(f'face{face}/independent payoff',fmt(price(face)),fmt(expected))
    p=region(2);r=sr('global flat capacity',p,p.outputs['proceeds']);ck('unbounded face has fixed proceeds',[r['bounds'][k]['value'] for k in ['lower','upper']],['100','100'])
    wrong=Problem('Deliberately wrong positive tail slope','negative control only');face=z3.Real('false_tail_face');wrong.variables={'face':face}
    wrong.add('flat-region domain',face>=140);wrong.add('false_110_root',q(100)+(face-140)/1000==110);wrong.outputs={'face':face}
    preserve('wrong positive tail',wrong);r=sr('wrong positive tail',wrong,face)
    ck('wrong tail root',[r['bounds'][k]['value'] for k in ['lower','upper']],['10140','10140'])
    ck('original law at false root',fmt(price(10140)),'100/1');ck('funding shortfall remains',fmt(110-price(10140)),'10/1')
    for label,assets,face in [('S fixed80',[100,100],80),('R fixed80',[0,180],80),('R committed160',[0,180],160)]:
        debt=sum((min(Q(face),a) for a in assets),Q())/2
        equity=sum((max(Q(a)-face,0) for a in assets),Q())/2
        policy.append(dict(id=label,assets=assets,face=face,debt_price=fmt(debt),equity_value=fmt(equity),weights=['1/2','1/2'],gross=1,source_admission=False))
        ck(label+'/conservation',fmt(debt+equity),fmt(Q(sum(assets),2)))
    ck('policy-dependent exact values',[[r['debt_price'],r['equity_value']] for r in policy],[['80/1','20/1'],['40/1','50/1'],['80/1','10/1']])
    ck('postissue residual favorsR',Q(50)>20,True);ck('committed same proceeds favorsS',Q(20)>10,True)
    ck('safe price wrong after asset substitution',fmt(Q(80)-40),'40/1')
    unknown=sr('zero budget does not reject offers',region(1,80),budget=replace(BUDGET,max_cells=0))
    ck('solver unavailable remainsUnknown',unknown['feasibility'],'Unknown');ck('unknown not complete',unknown['coverage']['complete'],False)
    ck('unknown formula retained',bool(unknown['coverage']['unvisited']['retained_formula']),True)
    legacy=base.native.Engine.apply;base.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('legacy fallback forbidden'))
    try:
        for owner in ['alpha','beta']:
            b,m=base.body_for(Q(100),Q(80),Q(4,5),owner);before=deepcopy(b);r=base.program.run(b)
            native.append(dict(id=owner,input=b,result=r,separate_endogenous_pricing=unknown,external_offer=dict(face='100/1',proceeds='80/1',quote='4/5',admitted=False)))
            ck(owner+'/offer executes',r['status'],'complete_provisional');ck(owner+'/input unchanged',b,before);ck(owner+'/full replay',base.program.verify(b,r),True)
            if r['status']!='complete_provisional':continue
            prior=r['trace'][2]['result']['transition']['after'];issued=r['trace'][3]['result']['transition']['after']
            balances=deepcopy(prior['balances']);balances[m['cash']]=fmt(Q(balances[m['cash']])+80);balances[m['debt']]=fmt(Q(balances[m['debt']])-80)
            memory=deepcopy(prior['memory']);memory['terms']['face']=fmt(Q(memory['terms']['face'])+100);memory['terms']['stage']='4/1'
            ck(owner+'/all issue balances',issued['balances'],balances);ck(owner+'/all issue memory',issued['memory'],memory)
            ck(owner+'/no invented default state',set(issued['memory']),set(prior['memory']))
            ck(owner+'/native completion does not changeUnknown',unknown['feasibility'],'Unknown')
    finally:base.native.Engine.apply=legacy
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json';originals=[x['original_row'] for x in json.loads(fm.read_text())['rows'] if x['original_row']['id'] in ['SIM-F025','SIM-F028','SIM-F029']]
    ck('original targets',[x['id'] for x in originals],['SIM-F025','SIM-F028','SIM-F029'])
    for row in checks:
        for k in ['actual','expected']:
            if isinstance(row[k],set):row[k]=sorted(row[k])
        if len(json.dumps(row))>1200:row['actual_sha256']=base.program.digest(row.pop('actual'));row['expected_sha256']=base.program.digest(row.pop('expected'))
    failed=[x for x in checks if not x['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),solver_cases=len(solver_results),native_cases=len(native),failed=failed,original_rows=[x['id'] for x in originals],source_admission=False)
    for name,value in [('verification',v),('checks',checks),('solver-results',solver_results),('formulae',formulae),('policy-comparison',policy),('original-rows',originals)]:dump(out/(name+'.json'),value)
    with gzip.open(out/'native-results.json.gz','wt') as z:json.dump(native,z)
    paths={Path(__file__),ROOT/PLAN,ROOT/ANCHOR,fm}
    paths.update(Path(x.__file__).resolve() for x in list(sys.modules.values()) if getattr(x,'__file__',None) and Path(x.__file__).resolve().is_relative_to(ROOT))
    (out/'check.py').write_bytes(Path(__file__).read_bytes())
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=dict(python=platform.python_version(),z3=z3.get_version_string()),cpu_gpu='CPU-only exact rational solver and native execution; no GPU imports',random_seeds='N/A deterministic',data_version='Retained chapter26 synthetic model and original SIM-F025/028/029',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}))
    print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
