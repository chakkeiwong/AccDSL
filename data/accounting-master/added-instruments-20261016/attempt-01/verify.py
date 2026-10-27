"""Independent acquired-value targets and adverse source-bound requests."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
sys.dont_write_bytecode=True
from reference import OUT,ROOT,HEDGE,calculate


def main():
    started=time.monotonic()
    nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for n in ['reference.py','verify.py','authored-cases.json','input-lock.json']:shutil.copy2(OUT/n,attempt/n)
    checks=[];exchanges=[];bad=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for item in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('input/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    assert all(c['passed'] for c in checks)
    authored=json.loads((OUT/'authored-cases.json').read_text())['cases']
    for case in authored:
        request=deepcopy(case['request']);before=deepcopy(request);actual=calculate(request)
        exchanges.append(dict(id=case['id'],request=request,result=actual))
        check(case['id']+'/status',actual['status']=='conditional_complete',actual['reason'])
        if actual['status']!='conditional_complete':continue
        check(case['id']+'/readonly',request==before and actual['mutations']==[] and calculate(request)==actual)
        trace={x['id']:x for x in actual['trace']}
        for id,wanted in case['targets'].items():
            for key,value in wanted.items():
                check(case['id']+'/'+id+'/'+key,trace[id][key]==value,dict(expected=value,actual=trace[id][key]))
        for j in actual['journals']:
            check(case['id']+'/journal/'+j['id'],sum(Q(v) for v in j['entries'].values())==0)
        for s in actual['trace']:
            check(case['id']+'/books/'+s['id'],sum(Q(v) for v in s['books'].values())==0)
        if case['id']=='two_acquisitions':
            js={j['id']:j['entries'] for j in actual['journals']}
            check('acquire-A-exact',js['a1']=={'derivative:A':'200','cash':'-200'})
            check('acquire-B-exact',js['a2']=={'derivative:B':'50','cash':'-50'})
            check('m2-cumulative-reversal',js['m2']=={'derivative:original':'200','derivative:A':'20','cf_reserve':'-420','gains':'200'})
            check('mixed-gross-values',trace['m5']['derivative_assets']=='120' and trace['m5']['derivative_liabilities']=='200')
            # Naive carrying-value input to the lower-of test fails both reserve and profit.
            wrongR=min(Q('1620'),Q('1500'));wrongI=Q('1620')-wrongR
            check('wrong-carrying-minimum',wrongR==1500 and wrongI==120 and str(wrongR)!=trace['m2']['reserve'] and str(wrongI)!=trace['m2']['profit'])
    base=authored[0]['request'];full=calculate(base)
    repeat=deepcopy(base);e=deepcopy(repeat['events'][1]);e['id']='same_mark';repeat['events'].insert(2,e)
    repeated=calculate(repeat)
    check('same-mark-cadence',repeated['state']==full['state'] and repeated['trace'][3]==dict(repeated['trace'][2],id='same_mark'))
    unchanged=deepcopy(base);unchanged['events']=unchanged['events'][:1]
    unchanged['events'].append(dict(id='mark_at_acquisition',operation='measure',date='2024-03-31',context=deepcopy(base['context']),findings=deepcopy(base['baseline_hedge']['opening']['findings']),price='90',values={'original':'1200','A':'200'}))
    s=calculate(unchanged)['state'];check('acquisition-zero-gain',s['D']=='1200' and s['reserve']=='1000' and s['profit']=='200')
    def adverse(id,status,reason,mutate):
        r=deepcopy(base);mutate(r);bad.append(dict(id=id,request=r,status=status,reason=reason))
    for key in base['findings']:
        adverse('missing-'+key,'unresolved','missing_'+key,lambda r,k=key:r['findings'].update({k:None}))
        adverse('false-'+key,'unsupported','finding_'+key,lambda r,k=key:r['findings'].update({k:False}))
    for key in base['events'][0]['findings']:
        adverse('add-missing-'+key,'unresolved','missing_'+key,lambda r,k=key:r['events'][0]['findings'].update({k:None}))
        adverse('add-false-'+key,'unsupported','finding_'+key,lambda r,k=key:r['events'][0]['findings'].update({k:False}))
    for key in base['events'][1]['findings']:
        adverse('measure-missing-'+key,'unresolved','missing_'+key,lambda r,k=key:r['events'][1]['findings'].update({k:None}))
        adverse('measure-false-'+key,'unsupported','finding_'+key,lambda r,k=key:r['events'][1]['findings'].update({k:False}))
    adverse('wrong-context','rejected','context_mismatch',lambda r:r['context'].update(book='other'))
    adverse('late-addition','rejected','measure_before_addition',lambda r:r['events'][0].update(date='2024-04-01'))
    adverse('duplicate-instrument','rejected','instrument_id',lambda r:r['events'][2]['instrument'].update(id='A'))
    adverse('missing-original','rejected','instrument_population',lambda r:r['events'][1]['values'].pop('original'))
    adverse('missing-new-leg','rejected','instrument_population',lambda r:r['events'][1]['values'].pop('A'))
    adverse('extra-leg','rejected','instrument_population',lambda r:r['events'][1]['values'].update(Z='1'))
    adverse('forged-D','rejected','event_shape',lambda r:r['events'][1].update(D='1420'))
    adverse('forged-basis','rejected','instrument_shape',lambda r:r['events'][0]['instrument'].update(origin_value='0'))
    adverse('negative-nominal','rejected','positive_nominal',lambda r:r['events'][0]['instrument'].update(nominal='-1'))
    adverse('negative-acquisition','unsupported','negative_acquisition_method',lambda r:r['events'][0]['instrument'].update(acquisition_value='-1'))
    adverse('noncanonical','rejected','rational_encoding',lambda r:r['events'][0]['instrument'].update(acquisition_value='400/2'))
    adverse('boolean-value','rejected','rational_encoding',lambda r:r['events'][1]['values'].update(A=True))
    adverse('insufficient-funding','unsupported','funding_required',lambda r:r.update(opening_cash='100'))
    adverse('backdate','rejected','event_chronology',lambda r:r['events'][1].update(date='2024-03-30'))
    adverse('beyond-maturity','rejected','event_chronology',lambda r:r['events'][1].update(date='2025-01-01'))
    adverse('duplicate-event','rejected','event_id',lambda r:r['events'][1].update(id='a1'))
    adverse('remove-instrument','unsupported','different_instrument_or_item_method',lambda r:r['events'][0].update(operation='remove_instrument'))
    adverse('add-item','unsupported','different_instrument_or_item_method',lambda r:r['events'][0].update(operation='add_item'))
    adverse('nonoffsetting','unsupported','nonoffsetting_cumulative_method',lambda r:r['events'][1].update(price='79'))
    adverse('forged-state','rejected','request_shape',lambda r:r.update(state={'D':'1200'}))
    adverse('post','rejected','operation',lambda r:r.update(operation='post'))
    for case in bad:
        before=deepcopy(case['request']);a=calculate(case['request']);case['actual']=dict(status=a['status'],reason=a['reason'])
        check(case['id']+'/refusal',(a['status'],a['reason'])==(case['status'],case['reason']),case['actual'])
        check(case['id']+'/atomic',a['baseline'] is a['state'] is None and a['trace']==a['journals']==a['flows']==a['mutations']==[] and case['request']==before)
    def missing(p):
        if str(p.relative_to(ROOT))==HEDGE:raise FileNotFoundError(p)
        return p.read_bytes()
    def corrupt(p):return b'changed' if str(p.relative_to(ROOT))==HEDGE else p.read_bytes()
    for id,reader,status,reason in [('missing-module',missing,'unresolved','input_bytes_missing'),('changed-module',corrupt,'rejected','input_bytes_changed')]:
        a=calculate(base,reader);check(id,(a['status'],a['reason'])==(status,reason) and a['state'] is None)
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),
        failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],cases=len(authored),
        adverse_inputs=len(bad),resolver_challenges=2,command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/added-instruments-20261016/verify.py',
        interpreter=sys.executable,environment='tfgpu Python standard library/Fraction; no ML import',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        data_version='input-lock.json and independent per-instrument acquisition-origin targets',random_seeds='N/A: deterministic',
        wall_seconds=round(time.monotonic()-started,3),plan='docs/plans/accounting-added-instruments-20261016.md',
        result='data/accounting-master/added-instruments-20261016/result.md',
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ['summary.json','checks.json','exchanges.json','adverse.json']])
    for n,v in [('summary.json',summary),('checks.json',checks),('exchanges.json',exchanges),('adverse.json',bad)]:
        (attempt/n).write_text(json.dumps(v,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['attempt','checks','failures','failed','adverse_inputs','wall_seconds']}))
    if summary['failures']:raise SystemExit(1)


if __name__=='__main__':main()
