"""Exact native conversion and finite shared-pool/election comparisons."""
import argparse
from copy import deepcopy
from dataclasses import replace
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import fixture as f
ROOT,H=f.ROOT,Path(__file__).resolve().parent
PLAN='docs/plans/company-state-claims-conversion-20261028.md'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output.resolve();out.mkdir(exist_ok=False);start=time.monotonic()
    checks=[];native=[];solvers=[];formulae=[]
    def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
    def run(n,b):
        before=deepcopy(b);r=f.program.run(b);ck(n+'/unchanged',b,before);ck(n+'/replay',f.program.verify(b,r),True)
        native.append(dict(id=n,input=b,result=r));return r
    def sr(n,p,obj=None,extra=(),budget=f.BUDGET):
        r=f.solve(p,budget,obj,extra=extra);solvers.append(dict(id=n,result=r));return r
    def preserve(n,p):formulae.append(dict(id=n,constraints=[dict(label=k,expression=v.sexpr()) for k,v in p.constraints],outputs={k:v.sexpr() for k,v in p.outputs.items()},provenance=p.provenance))
    legacy=f.base.native.Engine.apply;f.base.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('legacy fallback forbidden'))
    try:
        for owner in ['alpha','beta']:
            b,m=f.conversion(owner);r=run(owner+'/convert',b);ck(owner+'/complete',r['status'],'complete_provisional')
            if r['status']!='complete_provisional':continue
            balances=deepcopy(b['opening']['balances']);balances[m['debt']]='0/1';balances[m['capital']]='-170/1'
            memory=deepcopy(b['opening']['memory']);memory['terms'].update(face='0/1',new_shares='16/1',stage='4/1')
            ck(owner+'/all balances',r['current']['balances'],balances);ck(owner+'/all memory',r['current']['memory'],memory)
            ck(owner+'/no cash movement',r['current']['flows'],[])
            report=r['trace'][-1]['result'];ck(owner+'/balance sheet',report['balance_sheet'],dict(total_assets='170/1',total_liabilities='0/1',equity_including_profit='170/1'))
            ck(owner+'/income',report['income'],dict(income='0/1',expenses='0/1',profit='0/1'))
            ck(owner+'/noncash direct equity',report['equity']['direct_movements'],'160/1')
            ck(owner+'/cash unchanged',[report['cash_flows']['opening_cash'],report['cash_flows']['closing_cash'],report['cash_flows']['net_movement']],['10/1','10/1','0/1'])
            ck(owner+'/reconciliations',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
            ck(owner+'/postconversion denominator',Q(memory['terms']['old_shares'])+Q(memory['terms']['new_shares']),Q(116))
            ck(owner+'/new ownership',f.fmt(Q(16,116)),'4/29');ck(owner+'/old denominator wrong',Q(16,100)==Q(4,29),False)
            for name in ['duplicate','wrong_shares','unknown_shares','inconsistent_face']:
                b,m=f.conversion(owner)
                if name=='duplicate':b['commands'].insert(1,deepcopy(b['commands'][0]))
                if name=='wrong_shares':b['commands'][0]['event']['inputs']['shares']['value']=f.program.engine.known('15/1')
                if name=='unknown_shares':b['commands'][0]['event']['inputs']['shares']['value']=dict(status='unknown',reason='Conversion share count unavailable')
                if name=='inconsistent_face':b['opening']['memory']['terms']['face']='150/1'
                r=run(owner+'/'+name,b);ck(owner+'/'+name+'/stopped',r['status'],'stopped_provisional')
                ck(owner+'/'+name+'/outcome',r.get('stop',{}).get('status'),'unresolved' if name=='unknown_shares' else 'invalid')
                ck(owner+'/'+name+'/atomic',r['stop']['after_sha256'],r['stop']['before_sha256'])
            b,m=f.conversion(owner,clear_face=False);r=run(owner+'/stale_face',b)
            ck(owner+'/balanced stale contract accepted',r['status'],'complete_provisional')
            ck(owner+'/stale contract independent failure',[r['current']['balances'][m['debt']],r['current']['memory']['terms']['face']],['0/1','160/1'])
    finally:f.base.native.Engine.apply=legacy
    for priority in [None,0,1]:
        p=f.collateral(priority);name='priority/'+str(priority);preserve(name,p);admitted=[]
        for rank,oracle in [(0,[40,10]),(1,[20,30])]:
            r=sr(name+'/'+str(rank),p,extra=[p.variables['priority']==rank]);expected=priority is None or rank==priority
            ck(name+'/'+str(rank)+'/feasible',r['feasibility'],'Feasible' if expected else 'Infeasible')
            ck(name+'/'+str(rank)+'/complete',r['coverage']['complete'],True)
            if expected:admitted.append(oracle)
        ck(name+'/independent family',admitted,[[40,10],[20,30]] if priority is None else [[40,10] if priority==0 else [20,30]])
        r=sr(name+'/a bounds',p,p.outputs['recovery_a']);expected=[20,40] if priority is None else ([40,40] if priority==0 else [20,20])
        ck(name+'/bounds',[r['bounds'][k]['value'] for k in ['lower','upper']],[str(x) for x in expected])
    p=f.collateral(independent=True);preserve('independent double use',p);r=sr('independent double use',p)
    ck('independent claim payments overdraw pool',r['feasibility'],'Infeasible')
    ck('independent over-allocation',40+30-50,20)
    for value,choices,pay in [(40,[0],40),(100,[0],60),(240,[0,1],60),(400,[1],100)]:
        p=f.preference(value);name='preference/'+str(value);preserve(name,p);found=[]
        for choice in [0,1]:
            r=sr(name+'/'+str(choice),p,extra=[p.variables['election']==choice])
            ck(name+'/'+str(choice)+'/feasible',r['feasibility'],'Feasible' if choice in choices else 'Infeasible')
            if r['feasibility']=='Feasible':found.append(choice)
        ck(name+'/exclusive choice set',found,choices)
        r=sr(name+'/payment bounds',p,p.outputs['holder_payment'])
        ck(name+'/exact payoff',[r['bounds'][k]['value'] for k in ['lower','upper']],[str(pay)]*2)
        ck(name+'/independent conserved residual',pay+(value-pay),value)
        wrong=f.preference(value,both=True);preserve(name+'/both rights wrong',wrong);r=sr(name+'/both rights wrong',wrong,wrong.outputs['holder_payment'])
        over=min(60,value)+Q(value,4)
        ck(name+'/wrong combined feasibility',r['feasibility'],'Infeasible' if over>value else 'Feasible')
        ck(name+'/combined payoff violates exclusive right',over==pay,False)
        if over<=value:ck(name+'/pool balance alone misses rights error',[r['bounds'][k]['value'] for k in ['lower','upper']],[str(over)]*2)
    for name,p in [('priority',f.collateral()),('preference',f.preference(240))]:
        r=sr(name+'/zero budget',p,budget=replace(f.BUDGET,max_cells=0))
        ck(name+'/budget unknown',r['feasibility'],'Unknown');ck(name+'/budget incomplete',r['coverage']['complete'],False)
        ck(name+'/formula retained',bool(r['coverage']['unvisited']['retained_formula']),True)
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    originals=[r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id'] in ['SIM-F027','SIM-F031','SIM-F032']]
    ck('exact original targets',[r['id'] for r in originals],['SIM-F027','SIM-F031','SIM-F032'])
    for row in checks:
        for k in ['actual','expected']:
            if isinstance(row[k],Q):row[k]=str(row[k])
        if len(json.dumps(row))>1200:
            row['actual_sha256']=f.program.digest(row.pop('actual'));row['expected_sha256']=f.program.digest(row.pop('expected'))
    failed=[r for r in checks if not r['passed']]
    verdict=dict(status='fail' if failed else 'pass',checks=len(checks),native_cases=len(native),solver_cases=len(solvers),failed=failed,original_rows=[r['id'] for r in originals],source_admission=False)
    for name,value in [('verification',verdict),('checks',checks),('solver-results',solvers),('formulae',formulae),('original-rows',originals)]:dump(out/(name+'.json'),value)
    with gzip.open(out/'native-results.json.gz','wt') as z:json.dump(native,z)
    paths={Path(__file__),H/'fixture.py',ROOT/PLAN,fm}
    paths.update(Path(x.__file__).resolve() for x in list(sys.modules.values()) if getattr(x,'__file__',None) and Path(x.__file__).resolve().is_relative_to(ROOT))
    for name in ['fixture.py','check.py']:(out/name).write_bytes((H/name).read_bytes())
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=dict(python=platform.python_version(),z3=f.z3.get_version_string()),cpu_gpu='CPU-only exact native/rational solver; no GPU imports',random_seeds='N/A deterministic finite rights',data_version='Original SIM-F027/031/032; explicit synthetic terms and independent finite oracles',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}))
    print(json.dumps(verdict));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
