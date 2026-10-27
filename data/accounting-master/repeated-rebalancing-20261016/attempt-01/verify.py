"""Independent cumulative targets, incremental layer oracle and adverse events."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from reference import calculate

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def main():
    started=time.monotonic()
    indices=[int(p.name.split('-')[1]) for p in OUT.glob('attempt-[0-9][0-9]') if p.is_dir()]
    attempt=OUT/('attempt-%02d'%(max(indices,default=0)+1));attempt.mkdir()
    for filename in ('reference.py','verify.py','authored-cases.json','input-lock.json'):
        shutil.copy2(OUT/filename,attempt/filename)
    authored=json.loads((OUT/'authored-cases.json').read_text());checks=[];exchanges=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for item in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('input/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    assert all(c['passed'] for c in checks),'Protected input changed'
    request=dict(wire='RepeatedItemRebalancing/1',operation='report',opening=deepcopy(authored['opening']),
        events=[{k:v for k,v in event.items() if k!='expected'} for event in deepcopy(authored['events'])])
    before=deepcopy(request);result=calculate(request)
    exchanges.append(dict(id='authored-path',request=request,result=result))
    check('conditional-complete',result['status']=='conditional_complete',result['reason'])
    check('read-only-deterministic',request==before and result['mutations']==[] and calculate(request)==result)
    quantity=Q(100);last_price=Q(80);incremental_H=Q(0)
    for event,trace in zip(authored['events'],result['trace']):
        state=trace['state']
        if event['operation']=='measure':
            for key in ('H','reserve','profit'):
                check(event['id']+'/'+key,state[key]==event['expected'][key],dict(actual=state[key],expected=event['expected'][key]))
            check(event['id']+'/exact-journal',[trace['journal'][k] for k in authored['journal_fields']]==event['expected']['journal'])
            # Independent path integration, without access to stored layer origins.
            p=Q(event['price']);incremental_H-=quantity*(p-last_price);last_price=p
            check(event['id']+'/independent-incremental-item',Q(state['H'])==incremental_H)
        else:
            quantity+=Q(event['layer']['quantity'])
            check(event['id']+'/zero-new-origin',state['layers'][-1]['price']==event['layer']['price'])
            check(event['id']+'/no-reset-journal',all(v=='0' for v in trace['journal'].values()))
        check(event['id']+'/journal-balance',sum(Q(v) for v in trace['journal'].values())==0)
        check(event['id']+'/book-balance',sum(Q(v) for v in state['books'].values())==0)
    # Deliberately wrong segment minimum after first rebalance, independently computed.
    wrong_R=Q(1000)+min(Q(1400)-1200,Q(1550)-1000)
    wrong_I=Q(1400)-wrong_R
    check('wrong-reset-fixture',str(wrong_R)==authored['wrong_reset_expected']['reserve_at_m2'] and str(wrong_I)==authored['wrong_reset_expected']['profit_at_m2'])
    check('wrong-reset-rejected-by-source-target',str(wrong_R)!=authored['events'][2]['expected']['reserve'])
    check('old-ineffectiveness-reversed',result['trace'][2]['state']['profit']=='0' and result['trace'][2]['journal']['gains']=='200')
    # Removing intermediate observations must not change final cumulative state.
    sparse=deepcopy(request);sparse['events']=[e for e in sparse['events'] if e['id'] not in ('m3','m4','m5')]
    other=calculate(sparse);exchanges.append(dict(id='sparse-observation',request=sparse,result=other))
    check('observation-cadence-invariance',other['state']==result['state'])
    check('two-rebalances',result['state']['revision']==2)
    cases=[]
    def adverse(name,status,reason,fn):
        r=deepcopy(request);fn(r);cases.append(dict(id=name,status=status,reason=reason,request=r))
    adverse('wrong-layer-origin','rejected','new_layer_origin',lambda r:r['events'][1]['layer'].update(price='80'))
    adverse('wrong-layer-date','rejected','new_layer_origin',lambda r:r['events'][1]['layer'].update(date='2024-01-01'))
    adverse('duplicate-layer','rejected','duplicate_layer',lambda r:r['events'][1]['layer'].update(id='initial'))
    adverse('zero-layer','rejected','positive_quantity',lambda r:r['events'][1]['layer'].update(quantity='0'))
    adverse('stale-measurement','rejected','measure_immediately_before_rebalance',lambda r:r['events'][1].update(date='2024-04-01'))
    adverse('measure-missing','rejected','measure_immediately_before_rebalance',lambda r:r['events'].pop(0))
    adverse('second-measure-missing','rejected','measure_immediately_before_rebalance',lambda r:r['events'].pop(2))
    adverse('context-change','rejected','context_mismatch',lambda r:r['events'][2]['context'].update(book='another-book'))
    adverse('nonoffsetting','unsupported','nonoffsetting_cumulative_values',lambda r:r['events'][0].update(derivative='-1200'))
    adverse('fraction-not-reduced','rejected','rational_encoding',lambda r:r['events'][0].update(price='180/2'))
    adverse('unknown-operation','unsupported','different_layer_or_settlement_method',lambda r:r['events'][1].update(operation='remove_item'))
    adverse('instrument-addition','unsupported','different_layer_or_settlement_method',lambda r:r['events'][1].update(operation='add_instrument'))
    adverse('unmodeled-settlement','unsupported','different_layer_or_settlement_method',lambda r:r['events'][1].update(operation='settle'))
    adverse('late-observation','rejected','event_date',lambda r:r['events'][-1].update(date='2025-01-01'))
    adverse('duplicate-event','rejected','event_id',lambda r:r['events'][2].update(id='m1'))
    adverse('posting-request','rejected','operation',lambda r:r.update(operation='post'))
    for index in (0,1):
        for key in request['events'][index]['findings']:
            adverse('missing-'+str(index)+'-'+key,'unresolved','missing_'+key,lambda r,i=index,k=key:r['events'][i]['findings'].update({k:None}))
            adverse('false-'+str(index)+'-'+key,'unsupported','finding_'+key,lambda r,i=index,k=key:r['events'][i]['findings'].update({k:False}))
    for case in cases:
        before=deepcopy(case['request']);actual=calculate(case['request']);case['actual']=actual
        check(case['id']+'/refusal',(actual['status'],actual['reason'])==(case['status'],case['reason']),dict(status=actual['status'],reason=actual['reason']))
        check(case['id']+'/atomic',actual['state'] is None and actual['trace']==actual['journals']==actual['mutations']==[] and before==case['request'])
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],
        authored_observations=6,authored_additions=2,adverse_inputs=len(cases),cadence_comparisons=1,
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/repeated-rebalancing-20261016/verify.py',
        interpreter=sys.executable,environment='tfgpu Python standard library, exact Fraction; no ML imports',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),data_version='input-lock.json and independent authored-cases.json',
        random_seeds='N/A deterministic',wall_seconds=round(time.monotonic()-started,3),plan='docs/plans/accounting-repeated-rebalancing-20261016.md',
        result='data/accounting-master/repeated-rebalancing-20261016/result.md',
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ('summary.json','checks.json','exchanges.json','adverse.json')])
    for filename,value in [('summary.json',summary),('checks.json',checks),('exchanges.json',exchanges),('adverse.json',cases)]:
        (attempt/filename).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('attempt','checks','failures','failed','adverse_inputs','wall_seconds')}))
    if summary['failures']:raise SystemExit(1)


if __name__=='__main__':main()
