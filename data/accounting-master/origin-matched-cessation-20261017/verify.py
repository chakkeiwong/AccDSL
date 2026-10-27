"""Frozen-accounting targets, independent ledger replay and atomic refusals."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

from reference import evaluate

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def reprice(r, row, price, stopped=False):
    """Construct an adverse input without a contradictory supplied mark."""
    p=Q(price); row['price']=str(p)
    for o in r['origins']:
        q=Q(o['quantity']); f=Q(o['price'])
        row['instrument_values'][o['instrument_id']]=str(q*(p-f))
        remaining=q-(Q(r['stop']['quantity']) if stopped and o['id']==r['stop']['origin_id'] else 0)
        row['item_changes'][o['item_id']]=str(-remaining*(p-f))


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--attempt',required=True)
    args=parser.parse_args()
    assert args.attempt.startswith('attempt-') and '/' not in args.attempt
    attempt=OUT/args.attempt; attempt.mkdir(exist_ok=False)
    started=time.monotonic()
    index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
    artifacts=[OUT/'reference.py',Path(__file__).resolve(),OUT/'contract-addendum.md',OUT/'input-lock.json']
    before_artifacts={str(p.relative_to(ROOT)):sha(p) for p in artifacts}
    frozen=json.loads((OUT/'authored-cases.json').read_text()); cases=frozen['cases']
    checks=[]; outputs=[]; adverse=[]

    def check(name, condition):
        checks.append(dict(name=name,passed=bool(condition)))

    def atomic(v):
        return (v['result'] is None and v['stopped'] is None and v['closing_bridge'] is None
            and all(v[k]==[] for k in ('stages','journals','flows','origins','mutations'))
            and v['posts'] is False and v['context'] is None)

    for case in cases:
        r=case['request']; before=deepcopy(r); v=evaluate(r); key=case['id']
        outputs.append(dict(id=key,output=v))
        check(key+'/accepted',v['status']=='conditional_complete')
        check(key+'/input-unchanged',r==before)
        check(key+'/read-only',v['posts'] is False and v['mutations']==[])
        if v['result'] is None:
            continue
        for k,want in case['expected'].items():
            check(key+'/final/'+k,v['result'][k]==want)
        stopped=next(s for s in v['stages'] if s['operation']=='stop')
        terminal=next(s for s in v['stages'] if s['id']=='terminal-mark')
        for label,stage,expected in [('stop',stopped,case['stop_expected']),('terminal',terminal,case['terminal_expected'])]:
            for k,want in expected.items():
                check(key+'/'+label+'/'+k,stage[k]==want)
        trace=v['stopped']
        check(key+'/frozen-gross',trace['gross']==case['frozen_gross'])
        check(key+'/trace-conservation',Q(trace['gross'])==Q(trace['released'])+Q(trace['basis_transfer']))
        check(key+'/closed-trace',trace['remaining']=='0')
        origin=next(o for o in r['origins'] if o['id']==r['stop']['origin_id'])
        check(key+'/stopped-identity',all(trace[k]==origin[j] for k,j in
            [('origin_id','id'),('item_id','item_id'),('instrument_id','instrument_id'),('original_date','date'),('original_price','price')]))
        check(key+'/origin-preservation',all(all(a[k]==b[k] for k in
            ('id','item_id','instrument_id','date','quantity','price')) for a,b in zip(v['origins'],r['origins'])))
        opening=Q(r['opening_cash']); supplier=Q(r['closing']['supplier_cash'])
        settlement=sum(Q(x) for x in r['closing']['settlements'].values())
        check(key+'/direct-cash',Q(v['result']['cash'])==opening-supplier+settlement)
        check(key+'/assets-equity',Q(v['result']['cash'])+Q(v['result']['inventory'])==opening+Q(v['result']['profit']))
        check(key+'/gross-flow-order',[f['id'] for f in v['flows']]==['supplier']+[o['instrument_id'] for o in r['origins']])
        check(key+'/gross-flow-values',[f['amount'] for f in v['flows']]==[str(-supplier)]+[
            r['closing']['settlements'][o['instrument_id']] for o in r['origins']])
        check(key+'/flow-sum',opening+sum(Q(f['amount']) for f in v['flows'])==Q(v['result']['cash']))
        replay={k:Q(x) for k,x in v['stages'][0]['balances'].items()}
        for i,journal in enumerate(v['journals']):
            entries={k:Q(x) for k,x in journal['entries'].items()}
            check(f'{key}/journal-{i}/balanced',sum(entries.values())==0)
            for k,x in entries.items():
                replay[k]+=x
            check(f'{key}/journal-{i}/cash-funded',replay['cash']>=0)
        check(key+'/full-ledger-replay',replay=={k:Q(x) for k,x in v['stages'][-1]['balances'].items()})
        for i,s in enumerate(v['stages']):
            b={k:Q(x) for k,x in s['balances'].items()}
            check(f'{key}/stage-{i}/balance-sheet',sum(b.values())==0)
            check(f'{key}/stage-{i}/profit-ledger',-b['profit']==Q(s['profit']))
            check(f'{key}/stage-{i}/reserve-ledger',-b['reserve_continuing']-b['reserve_stopped']==
                Q(s['continuing_reserve'])+Q(s['stopped_reserve']))
            if s['operation'] not in ('opening','purchase_and_settle'):
                check(f'{key}/stage-{i}/effective-gain-bridge',Q(s['derivative_total'])==
                    Q(s['continuing_reserve'])+Q(s['stopped_reserve'])+Q(s['profit']))
            if s['date'] is not None:
                active={o['id'] for o in r['origins'] if o['date']<=s['date']}
                check(f'{key}/stage-{i}/no-future-quantities',set(s['remaining_quantities'])==active)

    successful={o['id']:o['output'] for o in outputs}
    check('named-first-not-nominal',successful['cancel-first']['stopped']['gross']=='15')
    check('named-second-not-nominal',successful['cancel-second']['stopped']['gross']=='10')
    check('same-aggregate-different-origins',successful['cancel-first']['result']['inventory']=='130' and
          successful['cancel-second']['result']['inventory']=='125')
    base=cases[0]['request']

    def bad(name, change, status, reason, original=base):
        r=deepcopy(original); change(r); before=deepcopy(r); v=evaluate(r)
        adverse.append(dict(id=name,request=r,status=v['status'],reason=v['reason']))
        check('refusal/'+name,v['status']==status and v['reason']==reason and atomic(v) and r==before)

    bad('unknown-root',lambda r:r.update(extra=1),'rejected','fields')
    bad('unknown-method',lambda r:r.update(wire='Other/1'),'unsupported','method')
    bad('group-book',lambda r:r['context'].update(book='group'),'unsupported','context_profile')
    bad('unknown-rule',lambda r:r['context'].update(rule='current'),'unsupported','context_profile')
    bad('information-before-close',lambda r:r['context'].update(information_date='2025-11-01'),'rejected','information_cutoff')
    bad('invalid-date',lambda r:r['origins'][0].update(date='2025-02-30'),'rejected','date')
    bad('zero-quantity',lambda r:r['origins'][0].update(quantity='0'),'rejected','numeric_domain')
    bad('nonzero-entry-value',lambda r:r['origins'][0].update(initial_value='1'),'unsupported','nonzero_origin')
    bad('nonzero-entry-cash',lambda r:r['origins'][0].update(initial_cash='-1'),'unsupported','nonzero_origin')
    bad('duplicate-origin',lambda r:r['origins'][1].update(id='a'),'rejected','origin_collision')
    bad('duplicate-instrument',lambda r:r['origins'][1].update(instrument_id='forward-a'),'rejected','origin_collision')
    bad('duplicate-item',lambda r:r['origins'][1].update(item_id='item-a'),'rejected','origin_collision')
    bad('reset-origin-price',lambda r:r['origins'][0].update(price='9'),'rejected','origin_price_mismatch')
    bad('missing-origin-measurement',lambda r:r['history'].pop(1),'rejected','missing_origin_measurement')
    bad('future-entry-fact',lambda r:r['origins'][0].update(facts_available_on='2025-01-02'),'rejected','future_information')
    bad('opposed-origins',lambda r:reprice(r,r['history'][-1],'17/2'),'unsupported','opposed_origin_gains')
    bad('actual-unmatched',lambda r:r['history'][-1]['instrument_values'].update({'forward-a':'31'}),'unsupported','actual_value_not_matched')
    bad('item-unmatched',lambda r:r['history'][-1]['item_changes'].update({'item-a':'-29'}),'unsupported','item_change_not_matched')
    bad('unknown-instrument',lambda r:r['history'][-1]['instrument_values'].update({'unknown':'1'}),'rejected','fields')
    bad('elective-stop',lambda r:r['stop'].update(highly_probable=True),'unsupported','elective_cessation')
    bad('unknown-expectation',lambda r:r['stop'].update(expected=None),'unresolved','unknown_fact')
    bad('unknown-high-probability',lambda r:r['stop'].update(highly_probable=None),'unresolved','unknown_fact')
    bad('unknown-stopped-origin',lambda r:r['stop'].update(origin_id='x'),'rejected','stop_origin')
    bad('whole-origin-stop',lambda r:r['stop'].update(quantity='10'),'unsupported','stop_quantity')
    bad('zero-stop',lambda r:r['stop'].update(quantity='0'),'rejected','numeric_domain')
    bad('stop-without-mark',lambda r:r['stop'].update(date='2025-07-02',facts_available_on='2025-07-02'),'rejected','stop_without_measurement')
    bad('cancellation-plus-loss',lambda r:r['stop'].update(unrecoverable_loss='1'),'rejected','duplicate_cancellation_loss')
    bad('excess-loss',lambda r:r['stop'].update(unrecoverable_loss='6'),'rejected','loss_exceeds_remaining_reserve',cases[6]['request'])
    bad('loss-on-positive-reserve',lambda r:r['stop'].update(unrecoverable_loss='1'),'rejected','loss_exceeds_remaining_reserve',cases[2]['request'])
    bad('cancellation-reinstated',lambda r:r['after'].insert(0,dict(id='reinstate',operation='assess_stopped',
        date='2025-07-01',facts_available_on='2025-07-01',expected=True,unrecoverable_loss='0')),
        'unsupported','cancellation_reinstatement')
    bad('assessment-without-mark',lambda r:r['after'].insert(0,dict(id='late-fact',operation='assess_stopped',
        date='2025-10-01',facts_available_on='2025-10-01',expected=False,unrecoverable_loss='0')),
        'rejected','assessment_without_measurement')
    bad('reverse-date',lambda r:r['after'][-1].update(date='2025-06-01',facts_available_on='2025-06-01'),'rejected','measurement_date')
    bad('future-measurement-fact',lambda r:r['after'][-1].update(facts_available_on='2026-01-01'),'rejected','future_information')
    bad('second-stop-operation',lambda r:r['after'][-1].update(operation='stop'),'unsupported','operation')
    bad('duplicate-event',lambda r:r['after'][-1].update(id='named-stop'),'rejected','event_collision')
    bad('netted-supplier',lambda r:r['closing'].update(supplier_cash='110'),'rejected','supplier_cash')
    bad('wrong-purchase-count',lambda r:r['closing'].update(quantity='20'),'rejected','purchase_quantity')
    bad('missing-actual-settlement',lambda r:r['closing']['settlements'].pop('forward-b'),'rejected','fields')
    bad('wrong-settlement',lambda r:r['closing']['settlements'].update({'forward-b':'29'}),'rejected','settlement_mismatch')
    bad('wrong-closing-price',lambda r:r['closing'].update(unit_price='11'),'rejected','closing_price')
    bad('one-unit-supplier-shortfall',lambda r:r.update(opening_cash='179'),'unsupported','funding_shortfall')
    bad('gross-loss-settlement-shortfall',lambda r:r.update(opening_cash='150'),'unsupported','funding_shortfall',cases[6]['request'])
    bad('noncanonical-rational',lambda r:r.update(opening_cash='600/2'),'rejected','noncanonical_rational')
    bad('numeric-boolean',lambda r:r.update(opening_cash=True),'rejected','rational')
    bad('zero-denominator',lambda r:r.update(opening_cash='1/0'),'rejected','rational')
    bad('empty-history',lambda r:r.update(history=[]),'rejected','history')
    bad('invalid-after-type',lambda r:r.update(after={}), 'rejected','after')
    for finding in base['findings']:
        bad('false-'+finding,lambda r,k=finding:r['findings'].update({k:False}),'unsupported','scope_finding')
        bad('missing-'+finding,lambda r,k=finding:r['findings'].pop(k),'unresolved','missing_finding')

    def negative_basis(r):
        reprice(r,r['history'][-1],'50')
        reprice(r,r['after'][-1],'0',True)
        r['closing'].update(unit_price='0',supplier_cash='0',settlements=deepcopy(r['after'][-1]['instrument_values']))
    bad('negative-inventory-basis',negative_basis,'unsupported','negative_inventory_basis',cases[2]['request'])

    lock=json.loads((OUT/'input-lock.json').read_text())['files']
    with tempfile.TemporaryDirectory(prefix='accdsl-origin-cessation-') as tmp:
        root=Path(tmp)
        for row in lock:
            p=root/row['path']; p.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/row['path'],p)
        for row in lock:
            p=root/row['path']; original=p.read_bytes()
            p.write_bytes(original+b'\nchanged\n'); v=evaluate(base,source_root=root)
            check('changed-source/'+row['path'],v['status']=='rejected' and v['reason']=='source_changed' and atomic(v))
            p.unlink(); v=evaluate(base,source_root=root)
            check('missing-source/'+row['path'],v['status']=='unresolved' and v['reason']=='source_missing' and atomic(v))
            p.write_bytes(original)
    check('preserved-git-index',index==subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT))
    check('preserved-executed-bytes',all(sha(ROOT/p)==h for p,h in before_artifacts.items()))
    result=dict(checks=len(checks),failures=sum(not c['passed'] for c in checks),cases=len(cases),
        adverse_requests=len(adverse),source_challenges=2*len(lock),detail=checks)
    for name,value in [('checks.json',result),('outputs.json',outputs),('adverse.json',adverse)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 '+str(Path(__file__).relative_to(ROOT))+' --attempt '+args.attempt,
        environment='system Python standard library only; '+sys.version.split()[0],
        interpreter=sys.executable,gpu_status='intentionally hidden by CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),
        seeds='N/A: deterministic exact-rational checks',data_version='authored-cases.json '+sha(OUT/'authored-cases.json'),
        wall_seconds=time.monotonic()-started,plan='docs/plans/accounting-origin-matched-cessation-20261017.md',
        result=str((OUT/'result.md').relative_to(ROOT)),outputs=[str((attempt/n).relative_to(ROOT)) for n in
            ('checks.json','outputs.json','adverse.json')],executed_artifacts=before_artifacts)
    (attempt/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    failed=[c['name'] for c in checks if not c['passed']]
    print(json.dumps({k:v for k,v in result.items() if k!='detail'}))
    if failed:
        print(json.dumps(dict(first_failures=failed[:8])))
    assert not failed, 'Preserved failed attempt; repair before a new attempt'


if __name__=='__main__':
    main()
