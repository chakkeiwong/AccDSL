"""Independent payoff, mark witnesses, ledger replay and adverse requests."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile,time
from reference import evaluate

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]


def main():
    started=time.monotonic();attempt=OUT/'attempt-01';attempt.mkdir(exist_ok=False)
    checks=[];outputs=[];adverse=[]
    def check(n,v):checks.append(dict(name=n,passed=bool(v)))
    authored=json.loads((OUT/'authored-cases.json').read_text());cases=authored['cases']
    for case in cases:
        r=case['request'];before=deepcopy(r);v=evaluate(r);id=case['id'];outputs.append(dict(id=id,output=v))
        check(id+'/accepted',v['status']=='conditional_complete');check(id+'/unchanged',r==before)
        check(id+'/no-posts',v['posts'] is False and v['mutations']==[])
        if not v['result']:continue
        for k,expected in case['expected'].items():check(id+'/'+k,v['result'][k]==expected)
        for i,expected in enumerate(case['interim_expected']):
            for k,value in expected.items():check(f'{id}/interim-{i}/{k}',v['stages'][i+1][k]==value)
        q=Q(r['quantity']);s=Q(r['quotes'][-1]['spot']);lo=Q(r['put']['strike']);hi=Q(r['call']['strike'])
        bounded=q*(lo if s<lo else hi if s>hi else s)
        check(id+'/independent-price-band',Q(v['result']['inventory'])==bounded)
        check(id+'/cash-cost',Q(v['result']['cash'])==Q(r['opening_cash'])-bounded)
        check(id+'/gross-flow-ids',[f['id'] for f in v['flows']]==['call-premium','put-premium','supplier','call-settlement','put-settlement'])
        check(id+'/gross-premiums',Q(v['flows'][0]['amount'])<0 and Q(v['flows'][1]['amount'])>0)
        check(id+'/cash-flow-sum',Q(r['opening_cash'])+sum(Q(f['amount']) for f in v['flows'])==Q(v['result']['cash']))
        bal=dict(cash=Q(r['opening_cash']),capital=-Q(r['opening_cash']),call_asset=Q(0),put_liability=Q(0),
            inventory=Q(0),intrinsic_reserve=Q(0),time_reserve=Q(0))
        for j,entry in enumerate(v['journals']):
            amounts={k:Q(x) for k,x in entry['entries'].items()}
            check(f'{id}/journal-{j}',sum(amounts.values())==0)
            for k,x in amounts.items():bal[k]+=x
            check(f'{id}/ledger-{j}',sum(bal.values())==0)
        check(id+'/replay',all(str(val)==v['stages'][-1]['balances'][k] for k,val in bal.items()))
        for i,stage in enumerate(v['stages']):
            b={k:Q(x) for k,x in stage['balances'].items()}
            check(f'{id}/stage-{i}/conservation',sum(b.values())==0)
            check(f'{id}/stage-{i}/cash-nonnegative',b['cash']>=0)
        for i,m in enumerate(r['quotes']):
            stage=v['stages'][i+1]
            check(f'{id}/stage-{i}/net-components',Q(stage['call'])-Q(stage['put'])==Q(stage['intrinsic'])+Q(stage['time']))

    # Independent local convex-combination witnesses for the synthetic marks.
    w=authored['mark_witness'];prices=list(map(Q,w['terminal_prices']))
    for name,spot,call,put in [('inception',Q(10),Q(6),Q(6)),('positive',Q(117,10),Q(15),Q(3)),('negative',Q(83,10),Q(3),Q(15))]:
        weights=list(map(Q,w[name+'_weights']))
        check(name+'/weights',sum(weights)==1 and min(weights)>0)
        check(name+'/spot-witness',sum(a*b for a,b in zip(prices,weights))==spot)
        check(name+'/call-witness',sum(max(p-11,0)*a*10 for p,a in zip(prices,weights))==call)
        check(name+'/put-witness',sum(max(9-p,0)*a*10 for p,a in zip(prices,weights))==put)

    base=cases[0]['request']
    def bad(id,change,status,reason):
        r=deepcopy(base);change(r);before=deepcopy(r);v=evaluate(r)
        check(id+'/status',v['status']==status);check(id+'/reason',v['reason']==reason)
        check(id+'/atomic',v['result'] is None and v['stages']==[] and v['journals']==[] and v['flows']==[])
        check(id+'/unchanged',r==before and v['posts'] is False and v['mutations']==[])
        adverse.append(dict(id=id,request=r,output=v))
    for name in base['findings']:
        bad('missing-'+name,lambda r,n=name:r['findings'].update({n:None}),'unresolved','missing_finding/'+name)
        bad('false-'+name,lambda r,n=name:r['findings'].update({n:False}),'unsupported','unsupported_finding/'+name)
    bad('extra-field',lambda r:r.update(net_settle=True),'rejected','request_fields')
    bad('unknown-amount',lambda r:r.update(quantity=None),'unresolved','unknown_amount')
    bad('noncanonical',lambda r:r.update(quantity='20/2'),'rejected','noncanonical_rational')
    bad('float-amount',lambda r:r.update(quantity=10.0),'rejected','rational_type')
    bad('wrong-rule',lambda r:r['context'].update(rule='current'),'rejected','source_profile')
    bad('bad-date',lambda r:r['context'].update(expiry='2025-02-30'),'rejected','date')
    bad('quantity-mismatch',lambda r:r['put'].update(quantity='9'),'unsupported','leg_alignment')
    bad('expiry-mismatch',lambda r:r['put'].update(expiry='2026-01-01'),'unsupported','leg_alignment')
    bad('underlying-mismatch',lambda r:r['put'].update(underlying='Y'),'unsupported','leg_alignment')
    bad('duplicate-legs',lambda r:r['put'].update(id='actual-call'),'rejected','leg_collision')
    bad('unequal-premiums',lambda r:r['put'].update(premium='7'),'unsupported','nonzero_net_premium')
    bad('unfunded-premium',lambda r:r.update(opening_cash='5'),'unsupported','funding_shortfall')
    bad('unfunded-supplier',lambda r:r.update(opening_cash='50'),'unsupported','funding_shortfall')
    bad('strike-order',lambda r:r['put'].update(strike='12'),'unsupported','strike_opening_domain')
    bad('no-quotes',lambda r:r.update(quotes=[]),'rejected','quotes')
    bad('reversed-dates',lambda r:r['quotes'][1].update(date='2025-03-01'),'rejected','quote_date')
    bad('future-information',lambda r:r['quotes'][1].update(facts_available_on='2026-03-01'),'rejected','quote_information')
    bad('unidentified-quote',lambda r:r['quotes'][1].update(call_id='unknown'),'rejected','quote_leg')
    bad('negative-time',lambda r:r['quotes'][0].update(call_time='-1'),'rejected','quote_domain')
    bad('wrong-component',lambda r:r['quotes'][0].update(call_value='16'),'rejected','component_value_mismatch')
    bad('wrong-item',lambda r:r['quotes'][0].update(item_change='7'),'unsupported','hedged_item_not_matched')
    bad('nonzero-expiry-time',lambda r:r['quotes'][-1].update(call_time='1',call_value='1'),'rejected','expiry_time_value')
    bad('missing-expiry',lambda r:r['quotes'].pop(),'unsupported','missing_expiry')
    bad('net-supplier-payment',lambda r:r['closing'].update(supplier_cash='90'),'rejected','supplier_cash_mismatch')
    bad('wrong-put-sign',lambda r:r['closing'].update(put_payment='-30'),'rejected','settlement_mismatch')
    bad('wrong-closing-quantity',lambda r:r['closing'].update(quantity='9'),'rejected','purchase_quantity')
    lock=json.loads((OUT/'input-lock.json').read_text())['files']
    with tempfile.TemporaryDirectory(prefix='accdsl-collar-') as tmp:
        root=Path(tmp)
        for row in lock:
            p=root/row['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/row['path'],p)
        for row in lock:
            p=root/row['path'];old=p.read_bytes();p.write_bytes(old+b'\nchanged\n');v=evaluate(base,source_root=root)
            check('source/'+row['path'],v['status']=='rejected' and v['reason']=='source_changed' and v['result'] is None and v['journals']==[])
            p.write_bytes(old)
    result=dict(checks=len(checks),failures=sum(not c['passed'] for c in checks),detail=checks,
        cases=len(cases),adverse_requests=len(adverse),source_challenges=len(lock),outputs=outputs,adverse=adverse)
    (attempt/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='python3 data/accounting-master/zero-cost-collar-20261017/verify.py',
        environment='system Python; standard library fractions',hardware='CPU only; no GPU or numerical framework import',
        random_seeds='N/A: deterministic rational cases',wall_seconds=time.monotonic()-started,
        data_version='authored-cases.json/input-lock.json',plan='docs/plans/accounting-zero-cost-collar-20261017.md',
        result=str((OUT/'result.md').relative_to(ROOT)),files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            for p in (OUT/'reference.py',OUT/'semantic-contract.md',Path(__file__).resolve(),attempt/'checks.json')])
    (attempt/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('checks','failures','cases','adverse_requests','source_challenges')}))
    if result['failures']:raise SystemExit(1)


if __name__=='__main__':main()
