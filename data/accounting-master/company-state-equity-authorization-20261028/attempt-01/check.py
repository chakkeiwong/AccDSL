"""Independent financial, refusal and ownership/value discriminators."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import fixture as f

ROOT,H=f.ROOT,Path(__file__).resolve().parent
PLAN='docs/plans/company-state-equity-authorization-20261028.md'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    out=ap.parse_args().output.resolve();out.mkdir(exist_ok=False);start=time.monotonic()
    checks=[];cases=[];values=[]
    def ck(name,a,e):checks.append(dict(name=name,passed=a==e,actual=a,expected=e))
    def run(name,body):
        before=deepcopy(body);r=f.program.run(body)
        ck(name+'/input unchanged',body,before);ck(name+'/full replay',f.program.verify(body,r),True)
        cases.append(dict(id=name,input=body,result=r));return r
    legacy=f.base.native.Engine.apply
    f.base.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('legacy fallback forbidden'))
    try:
        for owner in ['alpha','beta']:
            for shares,price in [(14,10),(15,10),(15,8)]:
                b,m=f.make(owner,shares,price);name=f'{owner}/settled{shares}at{price}';r=run(name,b)
                ck(name+'/success',r['status'],'complete_provisional')
                if r['status']!='complete_provisional':continue
                expected=deepcopy(b['opening']['balances']);expected[m['cash']]=f.fmt(10+shares*price);expected[m['capital']]=f.fmt(-10-shares*price)
                memory=deepcopy(b['opening']['memory']);memory['terms'].update(new_shares=f.fmt(shares),stage='4/1')
                ck(name+'/all balances',r['current']['balances'],expected);ck(name+'/all memory',r['current']['memory'],memory)
                report=r['trace'][-1]['result'];ck(name+'/profit0',report['income']['profit'],'0/1')
                ck(name+'/financing receipt',report['cash_flows']['activities']['financing']['receipts'],f.fmt(shares*price))
                ck(name+'/equity movement',report['equity']['direct_movements'],f.fmt(shares*price))
                ck(name+'/reconciliations',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
                ck(name+'/total shares',f.fmt(Q(r['current']['memory']['terms']['old_shares'])+Q(r['current']['memory']['terms']['new_shares'])),f.fmt(100+shares))
                ck(name+'/boundary flags',[report[k] for k in ['source_admission','accounting_admission','fiscal_complete','notes_complete']],[False]*4)
            for label,field,value,unknown in [('no_approval','approved',False,False),('offer_failed','offer_accepted',False,False),
                    ('subscription_failed','settled',False,False),('zero_receipt','cash_received','0/1',False),
                    ('short_receipt','cash_received','149/1',False),('wrong_offer_price','offer_price','8/1',False),
                    ('approval_unknown','approved',None,True),('offer_unknown','offer_accepted',None,True),
                    ('settlement_unknown','settled',None,True),('receipt_unknown','cash_received',None,True)]:
                b,m=f.make(owner);f.supplied(b,field,value,unknown);name=owner+'/'+label;r=run(name,b)
                ck(name+'/stopped',r['status'],'stopped_provisional')
                ck(name+'/outcome',r.get('stop',{}).get('status'),'unresolved' if unknown else 'invalid')
                ck(name+'/full atomic opening',r['current'],b['opening'])
                ck(name+'/no successful event',len(r['trace']),0)
            b,m=f.make(owner,16);name=owner+'/cap16';r=run(name,b)
            ck(name+'/cap refused',[r['status'],r.get('stop',{}).get('status')],['stopped_provisional','invalid'])
            ck(name+'/atomic',r['current'],b['opening'])
            b,m=f.make(owner);b['commands'].insert(1,deepcopy(b['commands'][0]));name=owner+'/duplicate';r=run(name,b)
            ck(name+'/duplicate stopped',r['status'],'stopped_provisional');ck(name+'/one issue only',r['current']['memory']['terms']['new_shares'],'15/1')
            ck(name+'/cash once',r['current']['balances'][m['cash']],'160/1')
            b,m=f.make(owner,16,10,guarded=False);name=owner+'/unguarded16';r=run(name,b)
            ck(name+'/generic accepts',r['status'],'complete_provisional');ck(name+'/independent cap fails',Q(r['current']['memory']['terms']['new_shares'])<=15,False)
            # Delete receipt checks while retaining false/zero inputs: balanced cash can be fabricated.
            b,m=f.make(owner);f.supplied(b,'settled',False);f.supplied(b,'cash_received','0/1')
            entry=b['registry']['entries']['equity_issue'];pre=entry['method']['preconditions']['manifest']
            pre['requirements']=[x for x in pre['requirements'] if x['id'] not in ['subscription_settled','receipt_matches']]
            entry['method_sha256']=f.program.digest(entry['method']);name=owner+'/deleted_receipt_rules';r=run(name,b)
            ck(name+'/generic accepts',r['status'],'complete_provisional')
            ck(name+'/false cash created',r['current']['balances'][m['cash']],'160/1')
            ck(name+'/independent receipt mismatch',Q(r['current']['balances'][m['cash']])-10==0,False)
        for price,expected in [(10,dict(old_value='1000/1',new_value='150/1',old_value_change='0/1',new_value_less_contribution='0/1')),
                              (8,dict(old_value='22400/23',new_value='3360/23',old_value_change='-600/23',new_value_less_contribution='600/23'))]:
            v=f.valuation(100,15,1000,price);values.append(dict(assumptions=dict(old_shares=100,new_shares=15,economic_assets=1000,price=price,fees=0,tax=0,debt=0),result=v))
            for k,e in expected.items():ck(f'value{price}/'+k,v[k],e)
            ck(f'value{price}/same ownership',v['old_ownership'],'20/23')
            ck(f'value{price}/value conservation',f.fmt(Q(v['old_value'])+Q(v['new_value'])),f.fmt(1000+15*price))
            ck(f'value{price}/transfer conservation',f.fmt(Q(v['old_value_change'])+Q(v['new_value_less_contribution'])),'0/1')
        ck('percentage dilution alone does not imply value loss',[values[0]['result']['old_value_change'],values[1]['result']['old_value_change']],['0/1','-600/23'])
        ck('book per old share distinct from assumed economic price',[f.fmt(Q(10,100)),f.fmt(Q(1000,100))],['1/10','10/1'])
        b,m=f.make('alpha',15,Q(1,10));r=run('book_price_shortcut',b)
        ck('book price accepted under explicit offer',r['status'],'complete_provisional')
        low=f.valuation(100,15,1000,Q(1,10));values.append(dict(assumptions='Deliberate book-price shortcut with same economic assets1000',result=low))
        ck('book price does not preserve old economic value',low['old_value_change'],'-2970/23')
    finally:f.base.native.Engine.apply=legacy
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    originals=[r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id'] in ['SIM-F030','SIM-F033','SIM-F034']]
    ck('exact original targets',[r['id'] for r in originals],['SIM-F030','SIM-F033','SIM-F034'])
    paths={Path(__file__),H/'fixture.py',ROOT/PLAN,fm}
    paths.update(Path(x.__file__).resolve() for x in list(sys.modules.values()) if getattr(x,'__file__',None) and Path(x.__file__).resolve().is_relative_to(ROOT))
    for row in checks:
        if len(json.dumps(row))>1200:
            row['actual_sha256']=f.program.digest(row.pop('actual'));row['expected_sha256']=f.program.digest(row.pop('expected'))
    failed=[r for r in checks if not r['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),native_cases=len(cases),failed=failed,original_rows=[r['id'] for r in originals],source_admission=False)
    for name,value in [('verification',v),('checks',checks),('valuation',values),('original-rows',originals)]:dump(out/(name+'.json'),value)
    with gzip.open(out/'native-results.json.gz','wt') as z:json.dump(cases,z)
    for name in ['fixture.py','check.py']:(out/name).write_bytes((H/name).read_bytes())
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only exact native execution and rational valuation; no GPU imports',random_seeds='N/A deterministic',data_version='Original SIM-F030/033/034; explicit synthetic share/offer/receipt and economic-value premises',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}))
    print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
