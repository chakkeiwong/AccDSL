"""Independent stage targets, limiting cases, partition equivalence and refusals."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
sys.dont_write_bytecode = True
from reference import OUT, ROOT, HEDGE, calculate


def main():
    started = time.monotonic()
    indices = [int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt = OUT / ('attempt-%02d' % (max(indices, default=0) + 1))
    attempt.mkdir()
    for name in ['reference.py','verify.py','authored-cases.json','input-lock.json']:
        shutil.copy2(OUT/name, attempt/name)
    checks, exchanges, adverse_cases = [], [], []
    def check(name, ok, detail=None):
        checks.append(dict(name=name, passed=bool(ok), detail=detail))
    cases = json.loads((OUT/'authored-cases.json').read_text())['cases']
    for item in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('lock/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    assert all(c['passed'] for c in checks), 'Protected inputs changed'
    for case in cases:
        req = deepcopy(case['request']); before = deepcopy(req)
        actual = calculate(req)
        exchanges.append(dict(id=case['id'],request=req,result=actual))
        check(case['id']+'/status',actual['status']=='conditional_complete',actual['reason'])
        if actual['status'] != 'conditional_complete':
            continue
        check(case['id']+'/read-only-repeatable',req==before and actual['mutations']==[] and calculate(req)==actual)
        by_id = {s['id']:s for s in actual['stages']}
        for id, target in case['targets'].items():
            for key, expected in target.items():
                value=by_id[id][key]
                check(case['id']+'/'+id+'/'+key,value==expected,dict(expected=expected,actual=value))
        for j in actual['journals']:
            check(case['id']+'/balanced/'+j['id'],sum(Q(x) for x in j['entries'].values())==0)
        for s in actual['stages']:
            check(case['id']+'/book/'+s['id'],sum(Q(x) for x in s['books'].values())==0)
        check(case['id']+'/unit-cost',actual['report']['unit_cost']=='1080/13')
        check(case['id']+'/no-recreated-reserve',all(s['reserve']==s['derivative']=='0' for s in actual['stages'][2:]))
        check(case['id']+'/gross-flow-origins',[x['origin'] for x in actual['flows']]==['supplier','hedge_settlement']+['inventory_sale']*sum(e['kind']=='sale' for e in req['events']))
        if 'write_down_sale_recovery' in case['id']:
            js = {j['id']:j['entries'] for j in actual['journals']}
            check(case['id']+'/sale-removes-allowance',js['s2']==dict(cash='2900',revenue='-2900',cogs='1820',inventory_gross='-2160',inventory_allowance='340'))
            check(case['id']+'/reversal-only-held',js['v2']==dict(nrv_expense='-680',inventory_allowance='680'))
            check(case['id']+'/final-total-cost',actual['report']['total_inventory_expense']=='10800')
            check(case['id']+'/wrong-original-reversal',Q('3640')+Q('1020')-Q(by_id['v2']['inventory'])==340)
    prior=json.loads((ROOT/'data/accounting-master/hedge-inventory-close-20261016/attempt-01/exchanges.json').read_text())
    for old in prior:
        new=next(x['result']['report'] for x in exchanges if x['id']==old['id']+'_all')
        r=old['result']['report']
        check(old['id']+'/all-sold-predecessor',new['closing']['cash']==r['closing_cash'] and
              new['closing']['cumulative_pretax_profit']==r['cumulative_pretax_profit'] and
              new['total_inventory_expense']==r['cost_of_sales'] and new['operating_receipts']==r['operating_receipts'] and
              new['operating_payments']==r['operating_payments'])
    base=next(x['request'] for x in cases if x['id']=='gain_write_down_sale_recovery')
    partition=deepcopy(base)
    first=deepcopy(base['events'][0]);second=deepcopy(first)
    first.update(id='s1a',quantity='13',cash='1450');second.update(id='s1b',quantity='39',cash='4350')
    partition['events']=[first,second]+deepcopy(base['events'][1:])
    check('same-date-sale-partition',calculate(partition)['report']==calculate(base)['report'])
    def adverse(id,status,reason,mutate):
        req=deepcopy(base);mutate(req)
        adverse_cases.append(dict(id=id,request=req,status=status,reason=reason))
    for key in base['findings']:
        adverse('missing-'+key,'unresolved','missing_'+key,lambda r,k=key:r['findings'].update({k:None}))
        adverse('false-'+key,'unsupported','finding_'+key,lambda r,k=key:r['findings'].update({k:False}))
    for name,value,status,reason in [('missing',None,'unresolved','missing_recovery_conditions_met'),('false',False,'unsupported','finding_recovery_conditions_met'),('wrong-type',1,'rejected','finding_type')]:
        adverse(name+'-recovery',status,reason,lambda r,v=value:r['events'][3].update(recovery_conditions_met=v))
    adverse('missing-nrv','unresolved','missing_nrv_valuation_satisfied',lambda r:r['events'][1].update(valuation_satisfied=None))
    adverse('nonuniform-nrv','unsupported','finding_uniform_unit_nrv',lambda r:r['events'][1].update(uniform_unit_nrv=False))
    adverse('missing-sale-recognition','unresolved','missing_sale_recognition_satisfied',lambda r:r['events'][0].update(recognition_satisfied=None))
    adverse('oversell-first','rejected','sale_quantity',lambda r:r['events'][0].update(quantity='131'))
    adverse('oversell-after-valuation','rejected','sale_quantity',lambda r:r['events'][2].update(quantity='79'))
    adverse('zero-sale','rejected','sale_quantity',lambda r:r['events'][0].update(quantity='0'))
    adverse('negative-cash','rejected','negative_cash_input',lambda r:r['events'][0].update(cash='-1'))
    adverse('negative-nrv','unsupported','negative_nrv_method',lambda r:r['events'][1].update(per_unit='-1'))
    adverse('fraction-encoding','rejected','rational_encoding',lambda r:r['events'][0].update(quantity='104/2'))
    adverse('numeric-encoding','rejected','rational_encoding',lambda r:r['events'][1].update(per_unit=70))
    adverse('invalid-date','rejected','date_encoding',lambda r:r['events'][1].update(date='2024-02-31'))
    adverse('backward-event','rejected','event_chronology',lambda r:r['events'][2].update(date='2024-10-01'))
    adverse('sale-before-acquisition','rejected','event_chronology',lambda r:r['events'][0].update(date='2024-09-01'))
    adverse('duplicate-id','rejected','event_id',lambda r:r['events'][2].update(id='s1'))
    adverse('forged-cost','rejected','event_shape',lambda r:r['events'][0].update(cost_of_sales='4320'))
    adverse('forced-reversal','rejected','event_shape',lambda r:r['events'][3].update(reversal='1020'))
    adverse('new-purchase','unsupported','event_method',lambda r:r['events'][0].update(kind='purchase'))
    adverse('wrong-formula','unsupported','cost_formula_method',lambda r:r.update(cost_formula='specific_identification'))
    adverse('forged-opening','rejected','request_shape',lambda r:r.update(initial_inventory='10800'))
    adverse('post-request','rejected','operation',lambda r:r.update(operation='post'))
    adverse('wrong-context','rejected','context_mismatch',lambda r:r['context'].update(currency='USD'))
    adverse('partial-purchase','rejected','purchase_population',lambda r:r['purchase'].update(quantity='52'))
    adverse('wrong-settlement','rejected','settlement_carrying_value',lambda r:r['settlement'].update(cash='1810'))
    adverse('insufficient-funding','unsupported','funding_required',lambda r:r.update(opening_cash='100'))
    adverse('wrong-layer-origin','rejected','hedge_new_layer_origin',lambda r:r['hedge']['events'][1]['layer'].update(price='80'))
    adverse('valuation-after-exhaustion','unsupported','inventory_exhausted',lambda r:r['events'].append(dict(id='too_late',kind='nrv',date='2024-12-31',per_unit='90',valuation_satisfied=True,uniform_unit_nrv=True,recovery_conditions_met=True)))
    for case in adverse_cases:
        before=deepcopy(case['request']);a=calculate(case['request'])
        case['actual']=dict(status=a['status'],reason=a['reason'])
        check(case['id']+'/refusal',(a['status'],a['reason'])==(case['status'],case['reason']),case['actual'])
        check(case['id']+'/atomic',a['report'] is a['hedge'] is None and a['stages']==a['journals']==a['flows']==a['mutations']==[] and case['request']==before)
    def missing(p):
        if str(p.relative_to(ROOT))==HEDGE:raise FileNotFoundError(p)
        return p.read_bytes()
    def corrupt(p):
        return b'changed' if str(p.relative_to(ROOT))==HEDGE else p.read_bytes()
    for name,reader,status,reason in [('missing-module',missing,'unresolved','input_bytes_missing'),('corrupt-module',corrupt,'rejected','input_bytes_changed')]:
        a=calculate(base,reader)
        check(name,(a['status'],a['reason'])==(status,reason) and a['report'] is None)
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),
        failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],
        cases=len(cases),adverse_inputs=len(adverse_cases),resolver_challenges=2,
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/hedge-inventory-subsequent-20261016/verify.py',
        interpreter=sys.executable,environment='tfgpu Python standard library/Fraction; no ML import',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        data_version='source/fixture bytes in input-lock.json; nine independent stage-target cases',
        random_seeds='N/A: deterministic',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-hedge-inventory-subsequent-20261016.md',
        result='data/accounting-master/hedge-inventory-subsequent-20261016/result.md',
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ['summary.json','checks.json','exchanges.json','adverse.json']])
    for name,value in [('summary.json',summary),('checks.json',checks),('exchanges.json',exchanges),('adverse.json',adverse_cases)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['attempt','checks','failures','failed','cases','adverse_inputs','wall_seconds']}))
    if summary['failures']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
