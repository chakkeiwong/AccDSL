"""Independent POCI stage, interest/impairment, cash and admission checks."""
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
from reference import OUT,ROOT,ACQUIRE,ADVANCE,REVISE,CLOSE,calculate


def main():
    started=time.monotonic();nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for name in ['reference.py','verify.py','authored-cases-v2.json','input-lock-v2.json','admission-repair.md']:shutil.copy2(OUT/name,attempt/name)
    checks=[];exchanges=[];adverses=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for item in json.loads((OUT/'input-lock-v2.json').read_text())['files']:
        check('input/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    assert all(c['passed'] for c in checks)
    cases=json.loads((OUT/'authored-cases-v2.json').read_text())['cases']
    for case in cases:
        req=deepcopy(case['request']);before=deepcopy(req);a=calculate(req);prefix=case['id']+'/'
        exchanges.append(dict(id=case['id'],request=req,result=a))
        check(prefix+'status',a['status']=='conditional_complete',a['reason'])
        if a['status']!='conditional_complete':continue
        check(prefix+'readonly',before==req and a['mutations']==[] and a['report']['posts'] is False and a==calculate(req))
        states={x['id']:x['state'] for x in a['trace']}
        check(prefix+'stage-identities',set(states)==set(case['expected']))
        for id,expected in case['expected'].items():
            actual=states[id]
            for key,value in expected.items():check(prefix+id+'/'+key,actual[key]==value,dict(actual=actual[key],expected=value))
            check(prefix+id+'/net-allowance',Q(actual['gross'])-Q(actual['allowance'])==Q(actual['net']))
            check(prefix+id+'/income-origin',Q(actual['interest'])+Q(actual['impairment_gain'])==Q(actual['profit']))
            check(prefix+id+'/equity',Q(actual['cash'])+Q(actual['net'])==Q(req['opening_cash'])+Q(actual['profit'])==Q(actual['equity']))
            check(prefix+id+'/original-rate-origin',actual['credit_adjusted_rate']==req['acquisition']['credit_adjusted_rate'] and actual['poci_origin'] is True)
        for i,j in enumerate(a['journals']):check(prefix+'journal/'+str(i),sum(Q(v) for v in j['entries'].values())==0)
        report=a['report'];final=report['final']
        check(prefix+'initial-allowance-zero',report['initial_loss_allowance']=='0')
        check(prefix+'contract-and-legal-rights',report['uncollected_contractual_amount']==case['uncollected_contractual'] and report['legal_release']=='not_assessed' and report['financial_asset_derecognized'] is True)
        cash=Q(req['events'][-1]['cash']);price=Q(req['acquisition']['price'])
        check(prefix+'direct-profit',Q(final['profit'])==cash-price)
        check(prefix+'direct-cash',Q(final['cash'])==Q(req['opening_cash'])+cash-price)
        check(prefix+'cash-origins',[x['origin'] for x in a['flows']]==['asset_purchase','confirmed_collection'])
    byid={x['id']:x['result'] for x in exchanges}
    def journal(case,id,operation):return next(x['entries'] for x in byid[case]['journals'] if x['event_id']==id and x['operation']==operation)
    if all(x['result']['status']=='conditional_complete' for x in exchanges):
        check('favorable-revision-journal',journal('improve-then-adverse-collection','better','credit_remeasurement')==dict(allowance='25',impairment='-25'))
        check('net-interest-positive-allowance-unwind',journal('deteriorate','y2','interest_and_allowance_unwind')==dict(gross='11/2',allowance='-3/2',interest='-4'))
        check('net-interest-negative-allowance-unwind',journal('improve-then-adverse-collection','y2','interest_and_allowance_unwind')==dict(gross='11/2',allowance='5/2',interest='-8'))
        check('terminal-adverse-loss-journal',journal('improve-then-adverse-collection','close','credit_remeasurement')==dict(allowance='-18',impairment='18'))
        check('signed-allowance-close-journal',journal('improve-then-adverse-collection','close','collection_and_financial_derecognition')==dict(cash='70',gross='-121/2',allowance='-19/2'))
        check('initial-credit-loss-not-second-allowance',byid['unchanged']['report']['initial_credit_shortfall_present_value']=='50' and byid['unchanged']['report']['initial_loss_allowance']=='0')
        protected=json.loads((ROOT/'docs/design/proposal/methods/standards-fixtures-v1.json').read_text())
        old=next(x for x in protected['credit_impaired'] if x['id']=='A07')
        a07=byid['A07-rate-base-limit'];year1=next(x['state'] for x in a07['trace'] if x['id']=='y1')
        check('protected-A07-comparator',year1['interest']==old['expected_interest'] and a07['report']['acquisition_value']==old['amortised_cost'] and a07['report']['original_credit_adjusted_rate']==old['rate'])
        state=next(x['state'] for x in byid['improve-then-adverse-collection']['trace'] if x['id']=='y2')
        check('gross-interest-counterexample',Q(state['interest'])-5==8 and Q('55')*Q('1/10')!=8)
        state=next(x['state'] for x in byid['improve-then-adverse-collection']['trace'] if x['id']=='better')
        check('allowance-floor-counterexample',state['net']=='80' and Q(state['gross'])-max(Q(state['allowance']),Q(0))!=80)
    base=deepcopy(cases[1]['request'])
    def adverse(id,status,reason,mutate,seed=None):
        req=deepcopy(seed or base);mutate(req);adverses.append(dict(id=id,request=req,expected_status=status,expected_reason=reason))
    for loc,fields in [('acquire',ACQUIRE),('advance',ADVANCE),('revise',REVISE),('close',CLOSE)]:
        def mapping(r,where):return r['acquisition']['findings'] if where=='acquire' else r['events'][{'advance':0,'revise':1,'close':-1}[where]]['findings']
        for key in sorted(fields):
            adverse(loc+'-unknown-'+key,'unresolved','missing_'+key,lambda r,k=key,l=loc:mapping(r,l).update({k:None}))
            adverse(loc+'-false-'+key,'unsupported','finding_'+key,lambda r,k=key,l=loc:mapping(r,l).update({k:False}))
    adverse('wrong-original-rate','rejected','initial_rate_value_mismatch',lambda r:r['acquisition'].update(credit_adjusted_rate='1/5'))
    adverse('unknown-original-rate','unresolved','missing_credit_adjusted_rate',lambda r:r['acquisition'].update(credit_adjusted_rate=None))
    adverse('zero-discount-base','unsupported','positive_discount_base',lambda r:r['acquisition'].update(credit_adjusted_rate='-1'))
    adverse('negative-discount-base','unsupported','positive_discount_base',lambda r:r['acquisition'].update(credit_adjusted_rate='-2'))
    adverse('unreduced-rate','rejected','rational_encoding',lambda r:r['acquisition'].update(credit_adjusted_rate='2/20'))
    adverse('integer-finding','rejected','finding_type',lambda r:r['acquisition']['findings'].update(poci_at_initial_recognition=1))
    adverse('term-boolean','rejected','positive_integer_term',lambda r:r['acquisition'].update(term_years=True))
    adverse('term-zero','rejected','positive_integer_term',lambda r:r['acquisition'].update(term_years=0))
    adverse('unknown-forecast','unresolved','missing_expected_receipt',lambda r:r['events'][1].update(expected_receipt=None))
    adverse('forecast-over-contract','rejected','receipt_exceeds_contract_or_negative',lambda r:r['events'][1].update(expected_receipt='122'))
    adverse('negative-forecast','rejected','receipt_exceeds_contract_or_negative',lambda r:r['events'][1].update(expected_receipt='-1'))
    adverse('early-zero-forecast','unsupported','early_zero_recovery_method',lambda r:r['events'][1].update(expected_receipt='0'))
    adverse('initial-forecast-over-contract','rejected','initial_amounts',lambda r:r['acquisition'].update(expected_receipt='122'))
    adverse('wrong-rule','unsupported','different_rule',lambda r:r['context'].update(rule='current-IFRS'))
    adverse('wrong-scale','unsupported','different_units_calendar',lambda r:r['context'].update(unit='thousands'))
    adverse('wrong-event-context','rejected','context_mismatch',lambda r:r['events'][1]['context'].update(contract='other'))
    adverse('invalid-date','rejected','date_encoding',lambda r:r['events'][0].update(date='2025-02-30'))
    adverse('fractional-year-step','rejected','annual_step_date',lambda r:r['events'][0].update(date='2024-07-01'))
    adverse('skipped-year','rejected','annual_step_date',lambda r:r['events'][0].update(date='2026-01-01'))
    adverse('off-date-assessment','rejected','assessment_date',lambda r:r['events'][1].update(date='2025-01-02'))
    adverse('future-information','rejected','future_or_preacquisition_information',lambda r:r['events'][1].update(information_date='2025-01-02'))
    adverse('old-information','rejected','future_or_preacquisition_information',lambda r:r['events'][1].update(information_date='2023-12-31'))
    adverse('unknown-credit-state','unresolved','missing_credit_improved',lambda r:r['events'][1].update(credit_improved=None))
    adverse('credit-state-integer','rejected','finding_type',lambda r:r['events'][1].update(credit_improved=1))
    adverse('replace-rate-after-cure','rejected','event_shape',lambda r:r['events'][1].update(new_rate='1/5'))
    adverse('supplied-opening-allowance','rejected','acquisition_shape',lambda r:r['acquisition'].update(allowance='50'))
    adverse('receipt-over-contract','rejected','receipt_exceeds_contract_or_negative',lambda r:r['events'][-1].update(cash='122'))
    adverse('negative-receipt','rejected','receipt_exceeds_contract_or_negative',lambda r:r['events'][-1].update(cash='-1'))
    adverse('unknown-receipt','unresolved','missing_receipt_cash',lambda r:r['events'][-1].update(cash=None))
    adverse('funding-shortfall','unsupported','funding_required',lambda r:r.update(opening_cash='49'))
    adverse('posting-request','rejected','report_only',lambda r:r.update(operation='post'))
    adverse('unsupported-operation','unsupported','different_operation',lambda r:r['events'][0].update(operation='modify'))
    adverse('duplicate-event','rejected','event_id',lambda r:r['events'][1].update(id='y1'))
    def early(r):
        r['events']=r['events'][:2]+[r['events'][-1]];r['events'][-1].update(date='2025-01-01',information_date='2025-01-01')
    adverse('early-collection','unsupported','terminal_collection_only',early)
    def repeat(r):
        x=deepcopy(r['events'][-1]);x['id']='repeat';r['events'].append(x)
    adverse('repeat-collection','rejected','already_closed',repeat)
    for case in adverses:
        before=deepcopy(case['request']);a=calculate(case['request']);case['actual']=dict(status=a['status'],reason=a['reason'])
        check(case['id']+'/refusal',(a['status'],a['reason'])==(case['expected_status'],case['expected_reason']),case['actual'])
        check(case['id']+'/atomic',a['report'] is None and a['trace']==a['journals']==a['flows']==a['mutations']==[] and before==case['request'])
    source=ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
    def absent(p):
        if p==source:raise FileNotFoundError(p)
        return p.read_bytes()
    def changed(p):return b'changed' if p==source else p.read_bytes()
    for name,reader,status,reason in [('missing-source',absent,'unresolved','input_bytes_missing'),('changed-source',changed,'rejected','input_bytes_changed')]:
        a=calculate(base,reader);check(name,(a['status'],a['reason'])==(status,reason) and a['report'] is None)
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),
        failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],cases=len(cases),
        adverse_inputs=len(adverses),resolver_challenges=2,
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/bank-poci-rollforward-20261016/verify.py',
        interpreter=sys.executable,environment='tfgpu Python standard library/Fraction; no ML import',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),data_version='input-lock-v2.json; eight independent paths; tightened partial-write-off admission',
        random_seeds='N/A deterministic',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-bank-poci-rollforward-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ['summary.json','checks.json','exchanges.json','adverse.json']])
    for n,v in [('summary.json',summary),('checks.json',checks),('exchanges.json',exchanges),('adverse.json',adverses)]:
        (attempt/n).write_text(json.dumps(v,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['attempt','checks','failures','failed','cases','adverse_inputs','wall_seconds']}))
    if summary['failures']:raise SystemExit(1)


if __name__=='__main__':main()
