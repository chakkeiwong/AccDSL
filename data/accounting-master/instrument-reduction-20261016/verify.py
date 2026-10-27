"""Independent stopped-origin identities and complete legal-book conservation."""
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
from reference import OUT,ROOT,SOURCE,FINDINGS,MEASURE,REDUCE,SETTLE,calculate

def main():
    started=time.monotonic();nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for name in ('reference.py','verify.py','authored-cases.json','input-lock.json'):shutil.copy2(OUT/name,attempt/name)
    checks=[];exchanges=[];adverse=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for row in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('protected/'+row['path'],hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'])
    if not all(c['passed'] for c in checks):
        (attempt/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');raise SystemExit('Protected input mismatch')
    cases=json.loads((OUT/'authored-cases.json').read_text())['cases']
    for c in cases:
        req=deepcopy(c['request']);before=deepcopy(req);r=calculate(req);prefix=c['id']+'/'
        exchanges.append(dict(id=c['id'],request=req,result=r))
        check(prefix+'status',r['status']=='conditional_complete',r['reason'])
        check(prefix+'readonly-repeatable',before==req and r==calculate(req) and r['mutations']==[])
        if r['status']!='conditional_complete':continue
        stages={x['id']:x['state'] for x in r['stages']}
        for name in ('pre','final','closing'):
            actual=r['closing'] if name=='closing' else stages[name]
            for key,value in c['expected'][name].items():check(prefix+name+'/'+key,actual[key]==value,dict(actual=actual[key],expected=value))
        reverse=deepcopy(req);reverse['instruments'].reverse();check(prefix+'instrument-order',calculate(reverse)==r)
        previous=None
        for step in r['stages']:
            s=step['state'];name=prefix+step['id']+'/'
            check(name+'item-origin',s['item']['quantity']==req['item']['quantity'] and s['item']['origin_price']==req['item']['origin_price'] and s['item']['designation_date']==req['context']['designation_date'])
            check(name+'book-balance',sum(Q(x) for x in s['books'].values())==0)
            check(name+'financial-equation',Q(s['cash'])+Q(s['inventory'])+Q(s['derivative_assets'])==Q(s['derivative_liabilities'])+Q(s['equity']))
            check(name+'gross-presentation',Q(s['derivative_assets'])-Q(s['derivative_liabilities'])==Q(s['derivative']))
            for id,x in s['instruments'].items():
                value=Q(x['value'])+Q(x['settled_cash']);frozen=sum((Q(z['portion_value']) for z in x['stops']),Q(0))
                derived_G=Q(x['fraction'])*value+frozen
                check(name+id+'/closed-form-G',derived_G==Q(x['G']))
                check(name+id+'/gain-conservation',Q(x['G'])+Q(x['U'])==value)
                check(name+id+'/quantity-conservation',Q(x['quantity'])*Q(x['fraction'])+sum((Q(z['quantity']) for z in x['stops']),Q(0))==Q(x['quantity']))
                for j,z in enumerate(x['stops']):check(name+id+'/stop/'+str(j),Q(z['quantity'])/Q(x['quantity'])*Q(z['whole_mark'])==Q(z['portion_value']))
            if not s['closed']:
                check(name+'profit-origins',Q(s['profit'])==Q(s['G'])-Q(s['reserve'])+Q(s['U']))
                check(name+'reserve-lower-of',abs(Q(s['reserve']))==min(abs(Q(s['G'])),abs(Q(s['H']))))
            if step['operation']=='reduce_instruments':
                check(name+'no-financial-jump',all(s[k]==previous[k] for k in ('G','U','H','derivative','reserve','profit','cash','inventory','equity','books','item')))
                check(name+'no-reduction-journal',all(j['event']!=step['id'] for j in r['journals']))
            previous=s
        reconstructed={k:Q(0) for k in r['state']['books']};reconstructed.update(cash=Q(req['opening_cash']),capital=-Q(req['opening_cash']))
        for i,j in enumerate(r['journals']):
            check(prefix+'journal/'+str(i),sum(Q(v) for v in j['entries'].values())==0)
            for key,value in j['entries'].items():reconstructed[key]+=Q(value)
        check(prefix+'reconstructed-book',all(v==Q(r['state']['books'][k]) for k,v in reconstructed.items()))
        check(prefix+'cash-origin-total',Q(r['closing']['cash'])==Q(req['opening_cash'])+sum(Q(f['amount']) for f in r['cash_flows']))
        check(prefix+'three-gross-flows',len(r['cash_flows'])==3 and r['cash_flows'][0]['kind']=='supplier_payment' and {f.get('instrument') for f in r['cash_flows'][1:]}=={'A','B'})
        check(prefix+'basis-identity',Q(r['closing']['inventory'])==Q(r['closing']['supplier_cost'])-Q(r['closing']['basis_transfer']))
        check(prefix+'closed-positions',Q(r['state']['reserve'])==Q(r['state']['derivative'])==0 and all(Q(x['value'])==0 for x in r['state']['instruments'].values()))
    byid={x['id']:x['result'] for x in exchanges}
    a=byid['remove-A']['closing']['before'];b=byid['remove-B-same-nominal']['closing']['before']
    check('same-nominal-different-gains',a['designated_quantity']==b['designated_quantity']=='70' and (a['G'],b['G'])==('190','205'))
    check('same-nominal-different-reserve',(a['reserve'],b['reserve'])==('190','200'))
    check('aggregate-stop-value-wrong',a['instruments']['A']['stops'][0]['portion_value']=='30' and Q(140)*Q(3,10)==42)
    check('aggregate-current-scaling-wrong',Q(a['G'])!=Q(a['derivative'])*Q(7,10))
    check('gross-asset-liability-visible',byid['gross-asset-liability']['closing']['before']['derivative_assets']=='120' and byid['gross-asset-liability']['closing']['before']['derivative_liabilities']=='20')
    base=cases[0]['request']
    def add(id,status,reason,change):
        r=deepcopy(base);change(r);adverse.append(dict(id=id,request=r,expected_status=status,expected_reason=reason))
    for group,fields in [('global',FINDINGS),('measure',MEASURE),('reduce',REDUCE),('settle',SETTLE)]:
        def destination(r,group=group):return r['findings'] if group=='global' else r['events'][{'measure':0,'reduce':1,'settle':3}[group]]['findings']
        for field in sorted(fields):
            for val,status,stem in [(None,'unresolved','missing_'),(False,'unsupported','outside_')]:
                add(group+'/'+field+'/'+str(val),status,stem+field,lambda r,k=field,v=val,d=destination:d(r).update({k:v}))
    add('context','rejected','context',lambda r:r['context'].update(currency='USD'))
    add('event-context','rejected','event_context',lambda r:r['events'][2].update(context=dict(r['context'],book='other')))
    add('post','rejected','report_only',lambda r:r.update(operation='post'))
    add('wire','rejected','wire',lambda r:r.update(wire='PartialHedgeDiscontinuation/1'))
    add('matched-shrink','rejected','event_shape',lambda r:r['events'][1].update(item_quantity='70'))
    add('missing-mark','rejected','mark_inventory',lambda r:r['events'][2]['marks'].pop('B'))
    add('unknown-mark','unresolved','missing_mark',lambda r:r['events'][2]['marks'].update(B=None))
    add('extra-mark','rejected','mark_inventory',lambda r:r['events'][2]['marks'].update(C='10'))
    add('over-reduction','rejected','reduction_exceeds_designated',lambda r:r['events'][1]['reductions'][0].update(quantity='61'))
    add('zero-reduction','rejected','number_domain',lambda r:r['events'][1]['reductions'][0].update(quantity='0'))
    add('unknown-instrument','rejected','reduction_identity',lambda r:r['events'][1]['reductions'][0].update(instrument='X'))
    add('duplicate-reduction','rejected','reduction_identity',lambda r:r['events'][1]['reductions'].append(deepcopy(r['events'][1]['reductions'][0])))
    add('full-discontinuation','unsupported','full_discontinuation',lambda r:r['events'][1].update(reductions=[dict(instrument='A',quantity='60'),dict(instrument='B',quantity='40')]))
    add('no-premeasurement','rejected','same_date_measurement_required',lambda r:r['events'].pop(0))
    add('later-rebalance','rejected','same_date_measurement_required',lambda r:r['events'][1].update(date='2025-04-01'))
    add('backwards-event','rejected','chronology',lambda r:r['events'][2].update(date='2025-01-01'))
    add('invalid-date','rejected','date_encoding',lambda r:r['events'][0].update(date='2025-02-30'))
    add('duplicate-event','rejected','duplicate_event',lambda r:r['events'][2].update(id='pre'))
    add('negative-quantity','rejected','number_domain',lambda r:r['item'].update(quantity='-1'))
    add('float-price','rejected','number_encoding',lambda r:r['events'][2].update(price=12.0))
    add('wrong-purchase','rejected','purchase_identity',lambda r:r['events'][3].update(quantity='70'))
    add('net-supplier-payment','rejected','purchase_identity',lambda r:r['events'][3].update(supplier_cash='980'))
    add('missing-settlement','rejected','settlement_inventory',lambda r:r['events'][3]['settlements'].pop('B'))
    add('changed-settlement','rejected','settlement_identity',lambda r:r['events'][3]['settlements'].update(B='101'))
    add('unfunded-supplier','unsupported','supplier_funding_required',lambda r:r.update(opening_cash='1000'))
    add('same-direction','unsupported','nonoffsetting_history',lambda r:r['events'][2].update(price='9'))
    add('no-close','unresolved','closing_required',lambda r:r['events'].pop())
    add('after-close','rejected','event_after_close',lambda r:r['events'].append(deepcopy(r['events'][2])))
    add('duplicate-instrument','rejected','duplicate_instrument',lambda r:r['instruments'][1].update(id='A'))
    add('initial-acquired-value','rejected','instrument_shape',lambda r:r['instruments'][0].update(initial_value='20'))
    add('finding-encoding','rejected','finding_encoding',lambda r:r['findings'].update(pretax_only=1))
    for c in adverse:
        before=deepcopy(c['request']);r=calculate(c['request']);c['actual']=r
        check(c['id']+'/refusal',(r['status'],r['reason'])==(c['expected_status'],c['expected_reason']),r['reason'])
        check(c['id']+'/atomic',before==c['request'] and r['state'] is None and r['closing'] is None and r['stages']==r['journals']==r['cash_flows']==r['mutations']==[])
    def missing(_):raise FileNotFoundError(SOURCE)
    source_checks=[]
    for name,reader,status in [('missing',missing,'unresolved'),('changed',lambda _:b'changed','rejected')]:
        r=calculate(base,reader);source_checks.append(dict(challenge=name,result=r))
        check('source/'+name,r['status']==status and r['state'] is None and r['closing'] is None and r['journals']==[])
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],
        cases=len(cases),adverse_inputs=len(adverse),source_challenges=len(source_checks),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/instrument-reduction-20261016/verify.py',environment=sys.executable+'; standard library/Fraction; no ML import',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',random_seeds='N/A deterministic',
        data_version='8 protected authored paths;input-lock.json',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-instrument-reduction-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ('checks.json','exchanges.json','adverse.json','source-challenges.json')])
    for name,value in [('checks.json',dict(summary=summary,checks=checks)),('exchanges.json',exchanges),('adverse.json',adverse),('source-challenges.json',source_checks),('run-manifest.json',summary)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'run-manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('attempt','checks','failures','cases','adverse_inputs','source_challenges','wall_seconds')}))
    if summary['failures']:raise SystemExit(1)

if __name__=='__main__':main()
