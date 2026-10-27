"""Check frozen finances, reserve origins and atomic refusals independently."""
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
from reference import OUT,ROOT,BASELINE,GLOBAL,STOP,MEASURE,CLOSE,calculate


def main():
    started=time.monotonic();nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for name in ['reference.py','verify.py','authored-cases-v2.json','input-lock-v2.json']:
        shutil.copy2(OUT/name,attempt/name)
    checks=[];exchanges=[];adverses=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for item in json.loads((OUT/'input-lock-v2.json').read_text())['files']:
        check('input/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    assert all(c['passed'] for c in checks)
    cases=json.loads((OUT/'authored-cases-v2.json').read_text())['cases']
    for case in cases:
        req=deepcopy(case['request']);before=deepcopy(req);a=calculate(req)
        exchanges.append(dict(id=case['id'],request=req,result=a))
        prefix=case['id']+'/'
        check(prefix+'status',a['status']=='conditional_complete',a['reason'])
        if a['status']!='conditional_complete':continue
        check(prefix+'readonly',req==before and a['mutations']==[] and a['report']['posts'] is False and a==calculate(req))
        stages={x['id']:x['state'] for x in a['trace']}
        check(prefix+'stage-identities',set(stages)==set(case['expected']))
        for id,expected in case['expected'].items():
            for key,value in expected.items():check(prefix+id+'/'+key,stages[id][key]==value,dict(actual=stages[id][key],expected=value))
            row=stages[id]
            check(prefix+id+'/equity',Q(row['cash'])+Q(row['inventory'])+Q(row['derivative'])==Q(row['equity']))
            check(prefix+id+'/reserve-split',Q(row['reserve'])==Q(row['continuing_reserve'])+Q(row['stopped_reserve']))
            check(prefix+id+'/capital-profit-reserve',Q(row['equity'])==Q(req['opening_cash'])+Q(row['profit'])+Q(row['reserve']))
        check(prefix+'independent-close',a['report']['close']==case['close_expected'],a['report']['close'])
        check(prefix+'exact-module',a['report']['baseline_module_sha256']==hashlib.sha256((ROOT/BASELINE).read_bytes()).hexdigest())
        for j,entry in enumerate(a['journals']):check(prefix+'journal/'+str(j),sum(Q(x) for x in entry['entries'].values())==0)
        final=stages['close'];close=case['close_expected']
        check(prefix+'direct-cash',Q(final['cash'])==Q('20000')-Q(close['supplier_cost'])+Q(req['events'][-1]['settlement_cash']))
        check(prefix+'inventory-cost',Q(final['inventory'])==Q(close['supplier_cost'])-Q(close['basis_transferred']))
        check(prefix+'no-double-release',Q(a['report']['stopped_reserve_at_discontinuation'])==Q(stages['mark']['stopped_reserve'])+Q(stages['mark']['released']))
    byid={x['id']:x['result'] for x in exchanges}
    def entry(case,id,operation):return next(x['entries'] for x in byid[case]['journals'] if x['event_id']==id and x['operation']==operation)
    if all(x['result']['status']=='conditional_complete' for x in exchanges):
        check('gain-mark-independent-journal',entry('gain-still-expected','mark','measure')==dict(derivative='200',cf_reserve='-320',gains='120'))
        check('gain-cancel-independent-journal',entry('gain-cancel-at-stop','stop','reserve_to_profit')==dict(cf_reserve='200',gains='-200'))
        check('loss-mark-independent-journal',entry('loss-still-expected','mark','measure')==dict(derivative='-200',cf_reserve='320',gains='-120'))
        check('loss-unrecoverable-independent-journal',entry('loss-partly-unrecoverable','assessment','reserve_to_profit')==dict(cf_reserve='-60',gains='60'))
        check('loss-cancel-only-remaining-journal',entry('loss-unrecoverable-then-cancel','cancel','reserve_to_profit')==dict(cf_reserve='-140',gains='140'))
        check('fractional-mark-independent-journal',entry('fractional-portion','mark','measure')==dict(derivative='200',cf_reserve='-350',gains='150'))
        check('same-mark-no-journal-movement',all(Q(x)==0 for x in entry('same-mark-after-split','same','measure').values()))
        check('cadence-final-conservation',byid['same-mark-after-split']['report']['final']==byid['gain-still-expected']['report']['final'])
        check('cancellation-time-final-conservation',byid['gain-cancel-at-stop']['report']['final']==byid['gain-cancel-later']['report']['final'])
        mark=next(x['state'] for x in byid['gain-still-expected']['trace'] if x['id']=='mark')
        check('whole-position-clip-counterexample',mark['reserve']=='1320' and mark['profit']=='80' and min(Q('1400'),Q('1500'))!=Q(mark['reserve']))
    base=deepcopy(cases[0]['request'])
    def adverse(id,status,reason,mutate,seed=None):
        req=deepcopy(seed or base);mutate(req)
        adverses.append(dict(id=id,request=req,expected_status=status,expected_reason=reason))
    for location,fields in [('global',GLOBAL),('stop',STOP),('measure',MEASURE),('close',CLOSE)]:
        def mapping(r,loc):
            return r['findings'] if loc=='global' else r['discontinuation']['findings'] if loc=='stop' else r['events'][0 if loc=='measure' else -1]['findings']
        for key in sorted(fields):
            adverse(location+'-unknown-'+key,'unresolved','missing_'+key,lambda r,k=key,l=location:mapping(r,l).update({k:None}))
            adverse(location+'-false-'+key,'unsupported','finding_'+key,lambda r,k=key,l=location:mapping(r,l).update({k:False}))
    adverse('homogeneity-integer','rejected','finding_type',lambda r:r['findings'].update(homogeneous_paired_portions=1))
    adverse('unknown-probability','unresolved','missing_stopped_highly_probable',lambda r:r['discontinuation'].update(highly_probable=None))
    adverse('still-qualifying','unsupported','still_qualifying_cannot_stop',lambda r:r['discontinuation'].update(highly_probable=True))
    adverse('unknown-expectation','unresolved','missing_stopped_expected',lambda r:r['discontinuation'].update(expected=None))
    adverse('no-reduction','rejected','partial_quantity',lambda r:r['discontinuation'].update(quantity='0'))
    adverse('negative-reduction','rejected','partial_quantity',lambda r:r['discontinuation'].update(quantity='-20'))
    adverse('full-cessation','rejected','partial_quantity',lambda r:r['discontinuation'].update(quantity='100'))
    adverse('excess-reduction','rejected','partial_quantity',lambda r:r['discontinuation'].update(quantity='101'))
    adverse('unreduced-fraction','rejected','rational_encoding',lambda r:r['discontinuation'].update(quantity='40/2'))
    adverse('stale-split-mark','rejected','stop_measurement_date',lambda r:r['discontinuation'].update(date='2024-04-01'))
    adverse('gain-cannot-be-unrecoverable-loss','rejected','loss_exceeds_remaining_reserve',lambda r:r['discontinuation'].update(unrecoverable_loss='1'))
    adverse('negative-loss','rejected','negative_unrecoverable_loss',lambda r:r['discontinuation'].update(unrecoverable_loss='-1'))
    adverse('excess-unrecoverable-loss','rejected','loss_exceeds_remaining_reserve',lambda r:r['events'][1].update(unrecoverable_loss='201'),cases[4]['request'])
    adverse('cancellation-double-loss','rejected','cancellation_loss_double_count',lambda r:r['discontinuation'].update(expected=False,unrecoverable_loss='10'))
    adverse('wrong-context','rejected','context_mismatch',lambda r:r['context'].update(currency='EUR'))
    adverse('event-context','rejected','context_mismatch',lambda r:r['events'][0]['context'].update(relationship='other'))
    adverse('reverse-time','rejected','event_date',lambda r:r['events'][0].update(date='2024-03-30'))
    adverse('invalid-calendar','rejected','date_encoding',lambda r:r['events'][0].update(date='2024-02-30'))
    adverse('changed-operation','unsupported','different_operation',lambda r:r['events'][0].update(operation='add_instrument'))
    adverse('same-sign-continuing-values','unsupported','nonoffsetting_cumulative_values',lambda r:r['events'][0].update(derivative='-1400'))
    adverse('wrong-purchase-population','rejected','purchase_population',lambda r:r['events'][-1].update(quantity='80'))
    adverse('changed-price','rejected','purchase_price',lambda r:r['events'][-1].update(unit_price='96'))
    adverse('wrong-cost','rejected','supplier_cost',lambda r:r['events'][-1].update(supplier_cash='9400'))
    adverse('settle-only-continuing-part','rejected','settlement_carrying_value',lambda r:r['events'][-1].update(settlement_cash='1120'))
    adverse('stale-close','rejected','measure_immediately_before_close',lambda r:r['events'][-1].update(date='2024-07-01'))
    adverse('unknown-field','rejected','request_shape',lambda r:r.update(reserve='1400'))
    adverse('posting-request','rejected','report_only',lambda r:r.update(operation='post'))
    adverse('same-event-id','rejected','event_id',lambda r:r['events'][-1].update(id='mark'))
    adverse('funding-shortfall','unsupported','funding_required',lambda r:r.update(opening_cash='100'))
    def again(r):
        extra=deepcopy(r['events'][-1]);extra['id']='again';r['events'].append(extra)
    adverse('repeat-purchase','rejected','already_closed',again)
    def reforecast(r):
        x=deepcopy(cases[2]['request']['events'][1]);x.update(id='reforecast',expected=True)
        r['events'].insert(1,x)
    adverse('reforecast-not-continuation','unsupported','new_forecast_requires_separate_method',reforecast,cases[1]['request'])
    for case in adverses:
        before=deepcopy(case['request']);a=calculate(case['request'])
        case['actual']=dict(status=a['status'],reason=a['reason'])
        check(case['id']+'/refusal',(a['status'],a['reason'])==(case['expected_status'],case['expected_reason']),case['actual'])
        check(case['id']+'/atomic',a['report'] is None and a['trace']==a['journals']==a['flows']==a['mutations']==[] and before==case['request'])
    def absent(p):
        if str(p.relative_to(ROOT))==BASELINE:raise FileNotFoundError(p)
        return p.read_bytes()
    def changed(p):return b'changed' if str(p.relative_to(ROOT))==BASELINE else p.read_bytes()
    for name,reader,status,reason in [('missing-module',absent,'unresolved','input_bytes_missing'),('changed-module',changed,'rejected','input_bytes_changed')]:
        a=calculate(base,reader);check(name,(a['status'],a['reason'])==(status,reason) and a['report'] is None)
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),
        failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],cases=len(cases),
        adverse_inputs=len(adverses),resolver_challenges=2,
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/partial-hedge-discontinuation-20261016/verify.py',
        interpreter=sys.executable,environment='tfgpu Python standard library/Fraction; no ML import',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        data_version='input-lock-v2.json; independently authored eight paths',random_seeds='N/A deterministic',
        wall_seconds=round(time.monotonic()-started,3),plan='docs/plans/accounting-partial-hedge-discontinuation-20261016.md',
        result=str((OUT/'result.md').relative_to(ROOT)),outputs=[str((attempt/n).relative_to(ROOT)) for n in ['summary.json','checks.json','exchanges.json','adverse.json']])
    for n,v in [('summary.json',summary),('checks.json',checks),('exchanges.json',exchanges),('adverse.json',adverses)]:
        (attempt/n).write_text(json.dumps(v,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['attempt','checks','failures','failed','cases','adverse_inputs','wall_seconds']}))
    if summary['failures']:raise SystemExit(1)


if __name__=='__main__':main()
