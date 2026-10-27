"""Independent authored balances, cash conservation and admission challenges."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
sys.dont_write_bytecode=True
from reference import OUT,ROOT,SHARED,ASSESS,SETTLE,calculate


def main():
    started=time.monotonic();nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for name in ('reference.py','verify.py','authored-cases.json','input-lock.json'):shutil.copy2(OUT/name,attempt/name)
    checks=[];exchanges=[];adverse=[]
    def check(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
    for row in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('locked/'+row['path'],hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'])
    assert all(x['passed'] for x in checks)
    cases=json.loads((OUT/'authored-cases.json').read_text())['cases']
    for c in cases:
        req=deepcopy(c['request']);before=deepcopy(req);r=calculate(req);prefix=c['id']+'/'
        exchanges.append(dict(id=c['id'],request=req,result=r))
        check(prefix+'status',r['status']=='conditional_complete',r['reason'])
        if r['status']!='conditional_complete':continue
        check(prefix+'readonly',req==before and r['mutations']==[] and r['report']['posts'] is False and r==calculate(req))
        states={x['id']:x['state'] for x in r['trace']}
        check(prefix+'stage-identities',set(states)==set(c['expected']))
        for id,e in c['expected'].items():
            for key,value in e.items():check(prefix+id+'/'+key,states[id][key]==value,dict(expected=value,actual=states[id][key]))
            s=states[id]
            check(prefix+id+'/equity',Q(s['cash'])+Q(s['asset'])-Q(s['provision'])==Q(s['equity']))
            check(prefix+id+'/profit-categories',Q(s['settlement_result'])-Q(s['asset_loss'])-Q(s['provision_expense'])-Q(s['admin_expense'])==Q(s['profit']))
        for n,j in enumerate(r['journals']):check(prefix+'journal/'+str(n),sum(Q(x) for x in j['entries'].values())==0)
        last=req['events'][-1];receipt=Q(last['receipt']);cost=Q(last['incremental_cash'])+Q(last['allocated_direct_cash'])+Q(last['exit_compensation'])+Q(last['unrelated_admin_cash'])
        f=r['report']['final']
        check(prefix+'direct-total-profit',Q(f['profit'])==receipt-cost-Q(req['original_unamortized_cost']))
        check(prefix+'direct-final-cash',Q(f['cash'])==Q(req['opening_cash'])+receipt-cost)
        check(prefix+'nothing-left',f['asset']==f['provision']=='0' and r['report']['closed'] is True)
        check(prefix+'cash-flow-sum',sum(Q(x['amount']) for x in r['cash_flows'])==receipt-cost)
    byid={x['id']:x['result'] for x in exchanges}
    def entry(case,id,kind):return next(x['entries'] for x in byid[case]['journals'] if x['id']==id and x['kind']==kind)
    if all(x['result']['status']=='conditional_complete' for x in exchanges):
        check('impairment-before-provision',[(x['kind'],x['entries']) for x in byid['fulfil-least-cost']['journals'][:2]]==[
            ('contract_cost_impairment_or_reversal',dict(asset='-20',asset_loss='20')),
            ('onerous_provision_remeasurement',dict(provision='-30',provision_expense='30'))])
        check('fulfilment-does-not-charge-loss-twice',entry('fulfil-least-cost','settlement','fulfilment_cost_and_provision_use')==dict(cash='-130',asset='0',provision='30',service_expense='100'))
        check('improved-cost-asset-reversal',entry('estimate-improves','review','contract_cost_impairment_or_reversal')==dict(asset='10',asset_loss='-10'))
        check('improved-obligation-release',entry('estimate-improves','review','onerous_provision_remeasurement')==dict(provision='30',provision_expense='-30'))
        check('admin-never-uses-contract-provision',entry('unrelated-admin-expense','settlement','unrelated_administration')==dict(cash='-15',admin_expense='15'))
        check('cancel-no-customer-revenue',all(x['origin']!='customer_receipt' for x in byid['cancel-cheaper-exit']['cash_flows']))
        check('incremental-cost-only-counterexample',max(Q(100)-Q(100),Q(0))!=Q(byid['fulfil-least-cost']['trace'][0]['state']['provision']))
        check('sunk-cost-double-charge-counterexample',Q(20)+Q(130)-Q(100)!=Q(byid['fulfil-least-cost']['trace'][0]['state']['provision']))
        check('gross-exit-comparison-counterexample',max(min(Q(130),Q(50))-Q(100),Q(0))!=Q(byid['fulfil-least-cost']['trace'][0]['state']['provision']))
    base=cases[0]['request']
    def add(id,status,reason,mutate):
        q=deepcopy(base);mutate(q);adverse.append(dict(id=id,request=q,expected_status=status,expected_reason=reason))
    for loc,fields in [('shared',SHARED),('assessment',ASSESS),('settlement',SETTLE)]:
        def flags(r,l):return r['findings'] if l=='shared' else r['events'][0 if l=='assessment' else -1]['findings']
        for key in sorted(fields):
            add(loc+'-missing-'+key,'unresolved','missing_'+key,lambda r,l=loc,k=key:flags(r,l).update({k:None}))
            add(loc+'-false-'+key,'unsupported','finding_'+key,lambda r,l=loc,k=key:flags(r,l).update({k:False}))
    add('integer-finding','rejected','finding_type',lambda r:r['findings'].update(contract_enforceable=1))
    add('wrong-contract','rejected','context_mismatch',lambda r:r['events'][0]['context'].update(contract='other'))
    add('wrong-rule','unsupported','different_rule_or_unit',lambda r:r['context'].update(rule='current-IFRS'))
    add('negative-cost','rejected','nonnegative_rational_encoding',lambda r:r['events'][0].update(incremental_cash='-1'))
    add('missing-cost','unresolved','missing_allocated_direct_cash',lambda r:r['events'][0].update(allocated_direct_cash=None))
    add('noncanonical-rational','rejected','nonnegative_rational_encoding',lambda r:r['events'][0].update(allocated_direct_cash='60/2'))
    add('future-information','rejected','information_cutoff',lambda r:r['events'][0].update(information_date='2025-01-02'))
    add('prior-information','rejected','information_cutoff',lambda r:r['events'][0].update(information_date='2024-12-31'))
    add('invalid-date','rejected','date_encoding',lambda r:r['events'][0].update(date='2025-02-30'))
    add('outside-period','rejected','event_date_or_period',lambda r:r['events'][-1].update(date='2026-01-01'))
    add('duplicate-id','rejected','event_identity',lambda r:r['events'][-1].update(id='assessment'))
    add('premature-cost-surprise','unsupported','actual_cost_or_receipt_requires_review',lambda r:r['events'][-1].update(incremental_cash='110'))
    add('unknown-settlement','unresolved','missing_receipt',lambda r:r['events'][-1].update(receipt=None))
    add('wrong-revenue','unsupported','actual_cost_or_receipt_requires_review',lambda r:r['events'][-1].update(receipt='101'))
    add('nonzero-penalty-on-performance','unsupported','actual_cost_or_receipt_requires_review',lambda r:r['events'][-1].update(exit_compensation='10'))
    add('insufficient-funding','unsupported','cash_funding_required',lambda r:r.update(opening_cash='100'))
    add('posting','rejected','report_only',lambda r:r.update(operation='post'))
    add('partial-performance','unsupported','different_operation',lambda r:r['events'][-1].update(operation='partial_fulfil'))
    add('caller-supplied-provision','rejected','event_shape',lambda r:r['events'][0].update(provision='50'))
    add('assessment-omitted','unresolved','assessment_required',lambda r:r['events'].pop(0))
    def change_price(r):
        e=deepcopy(r['events'][0]);e.update(id='changed',date='2025-06-01',information_date='2025-06-01',consideration='90');r['events'].insert(1,e)
    add('changed-price','unsupported','changed_consideration_method',change_price)
    def repeated(r):
        e=deepcopy(r['events'][-1]);e['id']='again';r['events'].append(e)
    add('repeat-settlement','rejected','already_closed',repeated)
    def bogus_cancel(r):r['events'][-1].update(operation='cancel')
    add('cancellation-receives-performance-price','rejected','cancellation_terms_mismatch',bogus_cancel)
    for case in adverse:
        before=deepcopy(case['request']);r=calculate(case['request']);case['actual']=dict(status=r['status'],reason=r['reason'])
        check(case['id']+'/refusal',(r['status'],r['reason'])==(case['expected_status'],case['expected_reason']),case['actual'])
        check(case['id']+'/atomic',r['report'] is None and r['trace']==r['journals']==r['cash_flows']==r['mutations']==[] and before==case['request'])
    source=ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
    def missing(p):
        if p==source:raise FileNotFoundError(p)
        return p.read_bytes()
    for id,reader,status in [('missing-source',missing,'unresolved'),('changed-source',lambda p:b'changed' if p==source else p.read_bytes(),'rejected')]:
        r=calculate(base,reader);check(id,r['status']==status and r['report'] is None and not r['journals'])
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not x['passed'] for x in checks),failed=[x for x in checks if not x['passed']],cases=len(cases),adverse_inputs=len(adverse),resolver_challenges=2,
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/onerous-contract-sequence-20261016/verify.py',
        environment=sys.executable+'; standard library/Fraction; no ML import',gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        data_version='input-lock.json; ten independently authored financial paths',random_seeds='N/A deterministic',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-onerous-contract-sequence-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ('summary.json','checks.json','exchanges.json','adverse.json')])
    for name,value in [('summary.json',summary),('checks.json',checks),('exchanges.json',exchanges),('adverse.json',adverse)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('attempt','checks','failures','failed','cases','adverse_inputs','wall_seconds')}))
    if summary['failures']:raise SystemExit(1)


if __name__=='__main__':main()
