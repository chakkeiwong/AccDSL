"""Original persistent-type paths and shock timing with exact independent checks."""
import argparse
from copy import deepcopy
from dataclasses import replace
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import fixture as f
import z3
from rational_solver_v1 import Problem,Budget,q,solve
ROOT,H=f.ROOT,Path(__file__).resolve().parent
PLAN='docs/plans/company-state-persistent-rate-failures-20261028.md'
SOURCES=['docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation/'+n for n in ['03-learning.tex','04-scenarios.tex','12-validation.tex']]
BUDGET=Budget(10,10000,100,100,10000,1000,1000000)
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))

def problem(persistent):
    a,b=z3.Ints('type_year1 type_year2');p=Problem('Original SIM-F011 two-year supplied loan','synthetic unweighted types')
    p.variables=dict(type_year1=a,type_year2=b);p.finite=dict(type_year1=[0,1],type_year2=[0,1])
    if persistent:p.add('no modification/type persists',a==b)
    i1,i2=q(5)+2*a,q(5)+2*b
    p.outputs=dict(interest1=i1,interest2=i2,total=i1+i2,cash_after_year1=20-i1,cash_after_year2=20-i1-i2)
    p.provenance=dict(principal='100',fixed_rate='1/20',floating_rate='7/100',no_modification=persistent,probability=None)
    return p

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    checks=[];solves=[];native=[];schedules=[];formulas=[];expectations=[]
    def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
    def sr(n,p,obj=None,extra=(),budget=BUDGET):
        r=solve(p,budget,obj,extra=extra);solves.append(dict(id=n,result=r));return r
    full=problem(True);wrong=problem(False)
    for name,p in [('persistent',full),('redrawn_mutation',wrong)]:
        formulas.append(dict(id=name,formulas=[dict(label=n,expression=e.sexpr()) for n,e in p.constraints],outputs={k:v.sexpr() for k,v in p.outputs.items()},provenance=p.provenance))
        feasible=[]
        for a,b in product([5,7],repeat=2):
            r=sr(f'{name}/{a},{b}',p,extra=[p.outputs['interest1']==q(a),p.outputs['interest2']==q(b)])
            expected='Feasible' if name=='redrawn_mutation' or a==b else 'Infeasible'
            ck(f'{name}/{a},{b}/feasible',r['feasibility'],expected)
            ck(f'{name}/{a},{b}/coverage',r['coverage']['complete'],True)
            if r['feasibility']=='Feasible':feasible.append([a,b])
        ck(name+'/complete original support',feasible,[[5,5],[7,7]] if name=='persistent' else [[5,5],[5,7],[7,5],[7,7]])
    r=sr('persistent/total bounds',full,full.outputs['total'])
    ck('total bounds',[r['bounds'][k]['value'] for k in ['lower','upper']],['10','14'])
    r=sr('persistent/interior12 not supported',full,extra=[full.outputs['total']==12]);ck('interval hull is not full support',r['feasibility'],'Infeasible')
    r=sr('redrawn/total12 supported',wrong,extra=[wrong.outputs['total']==12]);ck('redrawn adds unsupported sum',r['feasibility'],'Feasible')
    r=sr('persistent/year2cash',full,full.outputs['cash_after_year2']);ck('final cash bounds',[r['bounds'][k]['value'] for k in ['lower','upper']],['6','10'])
    r=sr('persistent/no cells',full,full.outputs['total'],budget=replace(BUDGET,max_cells=0))
    ck('budget unknown',r['feasibility'],'Unknown');ck('budget incomplete',r['coverage']['complete'],False)
    ck('budget formula retained',bool(r['coverage']['unvisited']['retained_formula']),True)
    ck('budget remainder',r['coverage']['unresolved']>0,True)
    def run(n,b):
        before=deepcopy(b);r=f.program.run(b);ck(n+'/input unchanged',b==before,True)
        ck(n+'/complete replay',f.program.verify(b,r),True);native.append(dict(id=n,input=b,result=r));return r
    old=f.native.Engine.apply;f.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('native fallback forbidden'))
    try:
        for owner,kind in product(['alpha','beta'],['fixed','floating']):
            name=owner+'/'+kind;b,m=f.make(kind,owner);r=run(name,b);i=Q(5 if kind=='fixed' else 7)
            ck(name+'/status',r['status'],'complete_provisional')
            if r['status']!='complete_provisional':continue
            opening=b['opening'];memory=deepcopy(opening['memory']);memory['terms']['stage']='1/1'
            for year,idx in [(1,0),(2,3)]:
                t=r['trace'][idx]['result']['transition'];balances=deepcopy(opening['balances'])
                balances[m['cash']]=f.h.fmt(20-year*i);balances[m['interest']]=f.h.fmt(i)
                balances[m['retained']]=f.h.fmt((year-1)*i)
                ck(name+f'/year{year}/all balances',t['after']['balances'],balances)
                ck(name+f'/year{year}/all memory',t['after']['memory'],memory)
                journal={a:'0/1' for a in balances};journal[m['cash']]=f.h.fmt(-i);journal[m['interest']]=f.h.fmt(i)
                ck(name+f'/year{year}/journal',t['journal'],journal)
                ck(name+f'/year{year}/cash flow',[x['amount'] for x in t['flows']],[f.h.fmt(-i)])
                report=r['trace'][idx+1]['result']
                ck(name+f'/year{year}/BS',report['balance_sheet'],dict(total_assets=f.h.fmt(120-year*i),total_liabilities='100/1',equity_including_profit=f.h.fmt(20-year*i)))
                ck(name+f'/year{year}/income',report['income'],dict(income='0/1',expenses=f.h.fmt(i),profit=f.h.fmt(-i)))
                ck(name+f'/year{year}/cash bridge',[report['cash_flows'][k] for k in ['opening_cash','closing_cash','net_movement']],[f.h.fmt(20-(year-1)*i),f.h.fmt(20-year*i),f.h.fmt(-i)])
                ck(name+f'/year{year}/equity bridge',[report['equity'][k] for k in ['opening','direct_movements','profit','closing']],[f.h.fmt(20-(year-1)*i),'0/1',f.h.fmt(-i),f.h.fmt(20-year*i)])
                ck(name+f'/year{year}/reconciliations',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
                ck(name+f'/year{year}/source and treatment',[report['source_admission'],report['accounting_admission']],[False,False])
                expectations.append(dict(id=name+f'/year{year}',balances=balances,memory=memory,journal=journal))
            carry=r['trace'][2]['result']['next_opening'];expected=deepcopy(opening['balances'])
            expected[m['cash']]=f.h.fmt(20-i);expected[m['retained']]=f.h.fmt(i)
            ck(name+'/carry full balances',carry['balances'],expected)
            ck(name+'/carry full memory',carry['memory'],opening['memory'])
            ck(name+'/carry annual period',carry['period'],dict(start='2028-01-01',end_exclusive='2029-01-01'))
            ck(name+'/archive retained',len(r['archives']),1)
        for control in ['redraw_type','redraw_type_and_coupon','drop_type_policy','repeat_coupon','skip_carry']:
            b,m=f.make('fixed');policies=b['commands'][2]['memory_policies']
            if control.startswith('redraw'):
                policies['/terms/rate_type']=dict(kind='reset',type=b['opening']['memory_types']['/terms/rate_type'],value='1/1',provenance='Deliberately wrong annual resampling')
                if control=='redraw_type_and_coupon':policies['/terms/coupon']=dict(kind='reset',type=b['opening']['memory_types']['/terms/coupon'],value='7/1',provenance='Deliberately wrong coupon redraw')
            if control=='drop_type_policy':del policies['/terms/rate_type']
            if control=='repeat_coupon':b['commands'].insert(1,deepcopy(b['commands'][0]));b['commands'][1]['event']['id']='coupon.again'
            if control=='skip_carry':del b['commands'][2]
            r=run(control,b);ck(control+'/refused',r['status'],'stopped_provisional')
            ck(control+'/refusal status',r['stop']['status'],'invalid')
            if r['trace']:
                last=r['trace'][-1];expected_hash=last['after_sha256']
            else:expected_hash=f.program.digest(b['opening'])
            ck(control+'/atomic refusal',f.program.digest(r['current']),expected_hash)
    finally:f.native.Engine.apply=old
    base=dict(kind='floating',principal='100',fixed_rate='1/20',reference_rate='3/100',spread='1/50',start='2027-01-01',maturity='2028-01-01',resets=['2027-01-01','2027-07-01'],convention='actual_days/365_simple')
    def shock(day,delta='1/50',ident='rates-up-200bp'):return dict(id=ident,target='reference_rate',effective=day,delta=delta)
    half=str(Q(5)+Q(2)*Q(184,365))
    cases=[('zero',base,[], '5'),('full-year',base,[shock('2027-01-01')],'7'),('after-first-reset',base,[shock('2027-01-02')],half),('at-july-reset',base,[shock('2027-07-01')],half),('before-july-reset',base,[shock('2027-06-30')],half),('after-july-reset',base,[shock('2027-07-02')],'5'),('at-maturity',base,[shock('2028-01-01')],'5'),('fixed-unchanged',{**base,'kind':'fixed'},[shock('2027-01-01')],'5'),('no-reset-before-maturity',{**base,'resets':['2027-01-01','2028-01-01']},[shock('2027-01-02')],'5'),('zero-delta',base,[shock('2027-01-01','0')],'5'),('double-principal',{**base,'principal':'200'},[shock('2027-01-01')],'14')]
    for name,c,s,expected in cases:
        r=f.schedule(c,s);oracle=f.daily_oracle(c,s)
        ck(name+'/independent daily sum',r['interest'],oracle);ck(name+'/expected',r['interest'],expected)
        ck(name+'/exact year days',sum(x['days'] for x in r['segments']),365)
        ck(name+'/not native schedule',r['native_schedule_admission'],False)
        schedules.append(dict(id=name,contract=c,shocks=s,result=r,independent_daily=oracle))
    ck('synthetic half-year illustration',str(Q(100)*Q(1,50)*Q(1,2)),'1')
    ck('actual July reset day count',[(x['days']) for x in f.schedule(base,[])['segments']],[181,184])
    ck('actual half-year not silently one half',Q(184,365)==Q(1,2),False)
    invalids=[('same-shock-twice',base,[shock('2027-01-01'),shock('2027-01-01')]),('wrong-shock-target',base,[{**shock('2027-01-01'),'target':'spread'}]),('float-shock',base,[shock('2027-01-01',0.02)]),('unsupported-daycount',{**base,'convention':'implicit'},[]),('unsorted-resets',{**base,'resets':['2027-07-01','2027-01-01']},[]),('reset-after-maturity',{**base,'resets':['2027-01-01','2028-02-01']},[])]
    for name,c,s in invalids:
        try:r=f.schedule(c,s);refused=False;detail=r
        except ValueError as e:refused=True;detail=str(e)
        ck(name+'/refusal',refused,True);schedules.append(dict(id=name,contract=c,shocks=s,refused=refused,detail=detail))
    duplicate=f.schedule(base,[shock('2027-01-01'),shock('2027-01-01',ident='renamed-same-source')])
    ck('distinct ids alone cannot prove independent shocks',duplicate['interest'],'9')
    ck('double reference or reference plus spread gives wrong cost',str(Q(100)*(Q(3,100)+Q(1,50)+2*Q(1,50))),'9')
    ck('fixed coupon incorrectly shocked gives wrong cost',str(Q(100)*(Q(1,20)+Q(1,50))),'7')
    schedules.append(dict(id='semantic-duplicate-negative-control',result=duplicate,interpretation='Caller must supply shock identity/meaning; different ids can encode same source twice'))
    originals=json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())
    rows=[x['original_row'] for x in originals['rows'] if x['original_row']['id'] in ['SIM-F011','SIM-F018']]
    ck('exact original rows',sorted(x['id'] for x in rows),['SIM-F011','SIM-F018'])
    paths=[Path(__file__),H/'fixture.py',ROOT/PLAN,*[ROOT/p for p in SOURCES],ROOT/'data/accounting-master/unified-program-20261028/failure-map.json']
    paths += [Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT)]
    hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
    failed=[c for c in checks if not c['passed']]
    v=dict(status='fail' if failed else 'pass',checks=len(checks),solver_cases=len(solves),native_cases=len(native),schedule_cases=len(schedules),failed=failed,original_rows=['SIM-F011','SIM-F018'],general_floating_execution=False)
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only exact rational/Z3/native execution; no accelerator imports',random_seeds='N/A deterministic enumeration',data_version='Original two-year loan plus explicitly dated synthetic reset schedule',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes=hashes)
    for name,obj in [('verification',v),('checks',checks),('solver-results',solves),('native-results',native),('schedule-results',schedules),('formulas',formulas),('expected-states',expectations),('original-rows',rows),('run-manifest',manifest)]:dump(out/(name+'.json'),obj)
    for name in ['fixture.py','check.py']:(out/name).write_bytes((H/name).read_bytes())
    print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())

