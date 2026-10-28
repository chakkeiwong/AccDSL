"""Exact transfer feasibility and independently expected native cash histories."""
import argparse
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import fixture as f
import z3
from rational_solver_v1 import Problem, Budget, q, solve
ROOT,H=f.ROOT,Path(__file__).resolve().parent
PLAN='docs/plans/company-state-location-timing-20261028.md'
BUDGET=Budget(0,10000,1,16,5000,1000,1000000)
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    out=ap.parse_args().output.resolve();out.mkdir(exist_ok=False);start=time.monotonic()
    checks=[];native=[];solver=[];formulae=[]
    def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
    def run(n,b):
        before=f.program.digest(b);r=f.program.run(b)
        ck(n+'/input preserved',f.program.digest(b),before);ck(n+'/replay',f.program.verify(b,r),True)
        native.append(dict(id=n,input=b,result=r));return r
    def state(n,r,b,m,cash,receivable,debt):
        expected=deepcopy(b['opening']['balances'])
        expected.update({m['cash']:f.fmt(Q(cash)),m['receivables']:f.fmt(Q(receivable)),m['debt']:f.fmt(Q(debt))})
        ck(n+'/all balances',r.get('current',{}).get('balances'),expected)
    def stopped(n,r,status):
        ck(n+'/stopped',r['status'],'stopped_provisional');stop=r.get('stop') or {}
        ck(n+'/stop outcome',stop.get('status'),status)
        prior=r['trace'][-1]['result']['transition']['after'] if r.get('trace') else next(x['input']['opening'] for x in native if x['id']==n)
        ck(n+'/no failed-event mutation',r['current'],prior)
    def sr(n,p,obj=None,budget=BUDGET):
        formulae.append(dict(id=n,constraints=[dict(label=k,expression=v.sexpr()) for k,v in p.constraints],provenance=p.provenance))
        r=solve(p,budget,obj);solver.append(dict(id=n,result=r));return r
    for cap in [0,10,Q(29,2),15,30]:
        x=z3.Real('transfer');p=Problem('Original SIM-F039 legal-entity liquidity','supplied cap, no other funding channel')
        p.variables={'transfer':x};p.add('nonnegative',x>=0);p.add('subsidiary_cash',x<=30)
        p.add('transfer_cap',x<=q(cap));p.add('parent_maturity',q(5)+x>=20)
        p.outputs={'parent_cash_before_payment':q(5)+x};p.provenance=dict(cap=str(cap),parent=5,subsidiary=30,maturity=20)
        r=sr('cap'+str(cap),p);ck('cap'+str(cap)+'/feasibility',r['feasibility'],'Feasible' if cap>=15 else 'Infeasible')
        ck('cap'+str(cap)+'/coverage',r['coverage'].get('complete'),True)
    x,c=z3.Reals('transfer cap');p=Problem('Conditional transfer authorization threshold','unknown actual cap remains an unresolved prerequisite')
    p.variables=dict(transfer=x,cap=c);p.add('nonnegative_transfer',x>=0);p.add('subsidiary_cash',x<=30)
    p.add('nonnegative_cap',c>=0);p.add('cap',x<=c);p.add('payment',5+x>=20);p.outputs=dict(cap=c)
    p.provenance=dict(actual_cap_known=False,source_admission=False)
    r=sr('unknown_cap_conditional_threshold',p,c)
    ck('threshold lower',r['bounds']['lower']['value'],'15');ck('threshold attained',r['bounds']['lower']['attained'],True)
    u=sr('zero_budget',p,budget=replace(BUDGET,max_cells=0))
    ck('budget remains unknown',u['feasibility'],'Unknown')
    ck('pooled original cash35 exceeds debt20',5+30>=20,True)
    ck('entity-specific original funding15 is insufficient',5+min(30,10)>=20,False)
    original=f.ex.native.Engine.apply
    f.ex.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('legacy fallback forbidden'))
    try:
        for owner in ['alpha','beta']:
            for label,cap,amounts,pay,success,cash,claim,debt in [
                ('cap10', '10/1',('10/1',),True,False,15,20,-20),
                ('cap15', '15/1',('15/1',),True,True,0,15,0),
                ('fractional_shortfall','15/1',('29/2',),True,False,Q(39,2),Q(31,2),-20),
                ('over_cap','10/1',('15/1',),True,False,5,30,-20),
                ('split_cap','10/1',('6/1','6/1'),False,False,11,24,-20),
                ('transfer_only','10/1',('10/1',),False,True,15,20,-20)]:
                n=owner+'/'+label;b,m=f.parent(owner,cap,amounts,pay);r=run(n,b)
                if success:ck(n+'/complete',r['status'],'complete_provisional')
                else:stopped(n,r,'unsupported' if label in ['over_cap','split_cap'] else 'invalid')
                state(n,r,b,m,cash,claim,debt)
                ck(n+'/debt memory',r['current']['memory']['finance']['debt'],f.fmt(Q(debt)))
            n=owner+'/unknown_cap';b,m=f.parent(owner)
            b['commands'][0]['event']['inputs']['cap']['value']=dict(status='unknown',reason='No admitted transfer permission')
            r=run(n,b);stopped(n,r,'unresolved');state(n,r,b,m,5,30,-20)
            n=owner+'/wrong_per_event_cap';b,m=f.parent(owner,amounts=('6/1','6/1'),pay=False)
            entry=b['registry']['entries']['collect'];rule=entry['method']['preconditions']['manifest']['requirements'][-1]
            rule['predicate']=f.f.binary('le',f.f.ref('amount'),f.f.ref('cap'));rule['requires']=['amount','cap']
            entry['method_sha256']=f.program.digest(entry['method']);r=run(n,b)
            ck(n+'/balanced mutation completes',r['status'],'complete_provisional')
            state(n,r,b,m,17,18,-20)
            ck(n+'/independent cumulative cap rejects',30-Q(r['current']['balances'][m['receivables']])<=10,False)
            ck(n+'/generic reconciliation',r['trace'][-1]['result']['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
            n=owner+'/subsidiary_leg';b,m=f.subsidiary(owner);r=run(n,b)
            ck(n+'/complete',r['status'],'complete_provisional')
            expected=deepcopy(b['opening']['balances']);expected.update({m['cash']:'20/1',m['payables']:'-20/1'})
            ck(n+'/all balances',r['current']['balances'],expected)
            parent=next(x for x in native if x['id']==owner+'/transfer_only')['result']
            parent_flow=parent['current']['flows'][0];sub_flow=r['current']['flows'][0]
            ck(n+'/paired gross cash sums zero',f.fmt(Q(parent_flow['amount'])+Q(sub_flow['amount'])),'0/1')
            ck(n+'/paired dates and currencies',(parent_flow['date'],parent_flow['currency']),(sub_flow['date'],sub_flow['currency']))
            ck(n+'/different legal entities',parent_flow['entity']!=sub_flow['entity'],True)
            for label,receipt,order,success,expected_cash,expected_claim,expected_debt in [
                ('late','2027-01-03','chronological',False,0,20,-20),
                ('early','2027-01-01','chronological',True,0,0,0),
                ('same_day_pay_first','2027-01-02','chronological',False,0,20,-20),
                ('same_day_receive_first','2027-01-02','receipt_first',True,0,0,0),
                ('future_reordered','2027-01-03','receipt_first',False,20,0,-20)]:
                n=owner+'/'+label;b,m=f.foreign(owner,receipt,order);r=run(n,b)
                if success:ck(n+'/complete',r['status'],'complete_provisional')
                else:stopped(n,r,'invalid')
                state(n,r,b,m,expected_cash,expected_claim,expected_debt)
                ck(n+'/EUR book',r['current']['context']['currency'],'EUR')
                ck(n+'/debt memory',r['current']['memory']['finance']['debt'],f.fmt(Q(expected_debt)))
                if label=='future_reordered':ck(n+'/chronology refusal',r['stop']['reason'],'event_chronology')
                if success:
                    report=r['trace'][-1]['result']
                    ck(n+'/operating receipt',report['cash_flows']['activities']['operating']['net'],'20/1')
                    ck(n+'/financing payment',report['cash_flows']['activities']['financing']['net'],'-20/1')
            for dimension in ['currency','entity']:
                n=owner+'/wrong_'+dimension;b,m=f.foreign(owner,receipt='2027-01-01')
                typ=b['commands'][1]['event']['inputs']['amount']['type']
                if dimension=='currency':typ['dimensions']={'currency:USD':1}
                else:typ['context']['entity']='Parent'
                r=run(n,b)
                ck(n+'/pre-execution refusal',r['status'],'invalid')
                ck(n+'/typed reason',r.get('reason'),'event_type_mismatch')
                ck(n+'/no trace or proposed current',bool(r.get('trace')) or 'current' in r,False)
            n=owner+'/pooled_foreign_cash';b,m=f.foreign(owner,opening='30/1');r=run(n,b)
            ck(n+'/supplied_EUR30_completes',r['status'],'complete_provisional')
            ck(n+'/reject_USD_or_other_entity_as_original_EUR_opening',b['opening']['balances'][m['cash']]=='0/1',False)
            ck(n+'/needs_explicit_fx_or_transfer',b['opening']['context']['currency'],'EUR')
    finally:f.ex.native.Engine.apply=original
    ck('late receipt end balance hides shortfall',Q(0)-20+20,Q(0))
    ck('late receipt cash prefix is negative',min(Q(0),Q(0)-20,Q(0)-20+20),Q(-20))
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    originals=[r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id'] in ['SIM-F039','SIM-F040']]
    ck('original targets',[r['discriminating_case'] for r in originals],['Parent cash5 maturity20; subsidiary30 but transfer cap10','Foreign receipt arrives after foreign debt payment'])
    for row in checks:
        for key in ['actual','expected']:
            if isinstance(row[key],Q):row[key]=f.fmt(row[key])
        if len(json.dumps(row))>1400:
            row['actual_sha256']=f.program.digest(row.pop('actual'));row['expected_sha256']=f.program.digest(row.pop('expected'))
    failed=[c for c in checks if not c['passed']]
    verdict=dict(status='fail' if failed else 'pass',checks=len(checks),native_cases=len(native),solver_cases=len(solver),failed=failed,
                 original_rows=['SIM-F039','SIM-F040'],actual_source_admission=False,cross_book_atomic_execution=False)
    for name,value in [('verification',verdict),('checks',checks),('solver-results',solver),('formulae',formulae),('original-rows',originals)]:dump(out/(name+'.json'),value)
    with gzip.open(out/'native-results.json.gz','wt') as fh:json.dump(native,fh)
    paths={Path(__file__),H/'fixture.py',ROOT/PLAN,fm}
    paths.update(Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT))
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],
        environment=dict(python=platform.python_version(),z3=z3.get_version_string()),cpu_gpu='CPU-only exact rational execution; no GPU framework imports',random_seeds='N/A deterministic',
        data_version='Original SIM-F039/040 plus explicitly supplied intercompany claims and dated EUR settlements',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,
        plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}))
    for name in ['check.py','fixture.py']:(out/name).write_bytes((H/name).read_bytes())
    print(json.dumps(dict(status=verdict['status'],checks=len(checks),native_cases=len(native),solver_cases=len(solver),failed=[r['name'] for r in failed])))
    return bool(failed)
if __name__=='__main__':raise SystemExit(main())
