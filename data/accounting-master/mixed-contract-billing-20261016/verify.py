"""Check frozen monetary targets, independent identities and atomic refusals."""
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
from reference import OUT,ROOT,calculate,GLOBAL,FINDINGS

def main():
    started=time.monotonic();nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for n in ('reference.py','verify.py','authored-cases.json','input-lock.json'):shutil.copy2(OUT/n,attempt/n)
    checks=[];exchanges=[];adverse=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for row in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('protected/'+row['path'],hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'])
    assert all(x['passed'] for x in checks)
    cases=json.loads((OUT/'authored-cases.json').read_text())['cases']
    for case in cases:
        req=deepcopy(case['request']);saved=deepcopy(req);r=calculate(req);prefix=case['id']+'/'
        exchanges.append(dict(id=case['id'],request=req,result=r))
        check(prefix+'status',r['status']=='conditional_complete',r['reason'])
        check(prefix+'readonly-repeatable',req==saved and r==calculate(req) and r['mutations']==[])
        if r['status']!='conditional_complete':continue
        states={x['id']:x['state'] for x in r['trace']}
        check(prefix+'stage-ids',set(states)==set(case['expected']))
        for id,expected in case['expected'].items():
            state=states[id]
            for key,value in expected.items():check(prefix+id+'/'+key,state[key]==value,dict(expected=value,actual=state[key]))
            s={k:Q(v) for k,v in state.items()}
            check(prefix+id+'/balance',s['cash']+s['receivable']+s['contract_asset']-s['contract_liability']==s['equity'])
            check(prefix+id+'/right',s['receivable']==s['gross_invoices']-s['credits']-s['collections'])
            check(prefix+id+'/performance',s['revenue']==s['construction_revenue']+s['visit_revenue'])
            check(prefix+id+'/presentation',s['contract_asset']*s['contract_liability']==0 and s['revenue']-s['paid_or_due']==s['contract_asset']-s['contract_liability'])
        rep=r['report'];f=rep['final'];flows=r['cash_flows']
        check(prefix+'cash-conservation',Q(f['cash'])==Q(req['opening_cash'])+sum(Q(x['amount']) for x in flows))
        check(prefix+'direct-indirect',rep['direct_operating_cash']==rep['indirect_operating_cash']==str(Q(f['cash'])-Q(req['opening_cash'])))
        check(prefix+'no-post',rep['posts'] is False)
        check(prefix+'receivables-by-id',sum(Q(i['gross'])-Q(i['credited'])-Q(i['collected']) for i in rep['invoices'].values())==Q(f['receivable']))
        check(prefix+'credits-by-advance',all(Q(a['credited'])==sum(Q(k['amount']) for k in rep['credits'].values() if k['advance_id']==aid) for aid,a in rep['advances'].items()))
        check(prefix+'credits-by-invoice',all(Q(i['credited'])==sum(Q(k['amount']) for k in rep['credits'].values() if k['invoice_id']==iid) for iid,i in rep['invoices'].items()))
        check(prefix+'collections-by-invoice',all(Q(i['collected'])==sum(Q(s['amount']) for s in rep['settlements'].values() if s['invoice_id']==iid) for iid,i in rep['invoices'].items()))
        opening=dict(cash=Q(req['opening_cash']),capital=-Q(req['opening_cash']))
        for j in r['journals']:
            check(prefix+j['id']+'/journal-balance',sum(Q(v) for v in j['entries'].values())==0)
            for k,v in j['entries'].items():opening[k]=opening.get(k,Q(0))+Q(v)
        expected_book={k:Q(f[k]) for k in ('cash','receivable','contract_asset','expense')}
        expected_book.update(contract_liability=-Q(f['contract_liability']),income=-Q(f['revenue']),capital=-Q(req['opening_cash']))
        check(prefix+'journals-to-final-book',all(opening.get(k,Q(0))==v for k,v in expected_book.items()))
    results={x['id']:x['result'] for x in exchanges}
    if all(r['status']=='conditional_complete' for r in results.values()):
        partial=results['partial-billing'];states={x['id']:x['state'] for x in partial['trace']}
        check('protected-mixed-revenues',[states[x]['revenue'] for x in ('p1','amend','p2','p3')]==['55','61','71','170'])
        check('protected-mixed-costs',[states[x]['expense'] for x in ('p1','amend','p2','p3')]==['42','42','46','112'])
        check('final-billing-order-invariance',all(results[x]['report']['final'][k]==partial['report']['final'][k] for x in ('fully-prepaid','invoice-before-performance') for k in ('cash','receivable','contract_asset','contract_liability','revenue','expense','profit','equity')))
        check('gross-origins',all(partial['report']['final'][k]==v for k,v in dict(advances='80',gross_invoices='170',credits='80',collections='90').items()))
        journals={x['id']:x['entries'] for x in partial['journals']}
        check('invoice-is-reclassification',journals['i1']==dict(receivable='50',contract_asset='-25',contract_liability='-25'))
        check('amendment-only-catchup',journals['amend']==dict(contract_liability='6',income='-6'))
        check('completion-no-second-billing',journals['p3']==dict(cash='-66',contract_liability='99',income='-99',expense='66'))
        check('fully-prepaid-invoice-empty-journal',results['fully-prepaid']['journals'][-1]['entries']=={})
        for name,n in [('before-amendment-cutoff',4),('after-visits-cutoff',7),('before-final-collection',10)]:
            check(name+'/prefix-no-lookahead',results[name]['trace']==partial['trace'][:n])
    base=deepcopy(cases[0]['request'])
    def add(id,status,reason,change):
        req=deepcopy(base);change(req);adverse.append(dict(id=id,expected_status=status,expected_reason=reason,request=req))
    for key in sorted(GLOBAL):
        for v,st,tag in [(None,'unresolved','missing_'),(False,'unsupported','outside_')]:
            add('global/'+key+'/'+str(v),st,tag+key,lambda r,k=key,v=v:r['findings'].update({k:v}))
    positions={'advance':0,'perform':1,'invoice':2,'collect':3,'amend':4}
    for op,pos in positions.items():
        for key in sorted(FINDINGS[op]):
            for v,st,tag in [(None,'unresolved','missing_'),(False,'unsupported','outside_')]:
                add(op+'/'+key+'/'+str(v),st,tag+key,lambda r,p=pos,k=key,v=v:r['events'][p]['findings'].update({k:v}))
    add('duplicate-event','rejected','event_identity',lambda r:r['events'][-1].update(id='a1'))
    add('duplicate-advance','rejected','advance_identity',lambda r:r['events'][5].update(advance_id='a1'))
    add('duplicate-invoice','rejected','invoice_identity',lambda r:r['events'][7].update(invoice_id='i1'))
    add('duplicate-credit','rejected','credit_identity',lambda r:r['events'][7]['credits'][0].update(credit_id='k1'))
    add('wrong-contract-credit','rejected','credit_contract',lambda r:r['events'][2]['credits'][0].update(contract='other'))
    add('unknown-advance','rejected','unknown_advance',lambda r:r['events'][2]['credits'][0].update(advance_id='other'))
    add('used-advance-credit','rejected','advance_overcredit',lambda r:r['events'][7]['credits'][0].update(advance_id='a1'))
    add('advance-credit-too-large','rejected','advance_overcredit',lambda r:r['events'][2]['credits'][0].update(amount='31'))
    add('invoice-overcredit','rejected','invoice_overcredit',lambda r:r['events'][2].update(gross='20'))
    add('duplicate-settlement','rejected','settlement_identity',lambda r:r['events'][-1].update(settlement_id='c1'))
    add('wrong-invoice','rejected','unknown_invoice',lambda r:r['events'][3].update(invoice_id='other'))
    add('overcollection','rejected','overcollection',lambda r:r['events'][3].update(amount='51'))
    add('overbilling','rejected','entitlement_exceeds_price',lambda r:r['events'][7].update(gross='91'))
    add('advance-over-entitlement','rejected','entitlement_exceeds_price',lambda r:r['events'][5].update(amount='91'))
    add('uncredited-overlap','rejected','entitlement_exceeds_price',lambda r:r['events'][7].update(credits=[]))
    add('construction-overrun','rejected','performance_exceeds_obligation',lambda r:r['events'][9].update(construction_cash_cost='61'))
    add('too-many-visits','rejected','performance_exceeds_obligation',lambda r:r['events'][6].update(visits='6'))
    add('fractional-visits','rejected','amount_domain',lambda r:r['events'][6].update(visits='1/2'))
    add('cost-without-visits','unsupported','visit_cost_without_performance',lambda r:r['events'][6].update(visits='0'))
    add('unfunded-cost','unsupported','cash_funding_required',lambda r:r.update(opening_cash='0'))
    add('unknown-cost','unresolved','missing_construction_cash_cost',lambda r:r['events'][1].update(construction_cash_cost=None))
    add('negative-cash','rejected','amount_domain',lambda r:r['events'][0].update(amount='-1'))
    add('numeric-float','rejected','amount_encoding',lambda r:r['events'][0].update(amount=30.0))
    add('noncanonical-number','rejected','amount_encoding',lambda r:r['events'][0].update(amount='30.0'))
    add('invalid-date','rejected','date_encoding',lambda r:r['events'][0].update(date='2024-02-30'))
    add('event-out-of-order','rejected','event_date_or_cutoff',lambda r:r['events'][3].update(date='2024-04-01'))
    add('future-event','rejected','event_date_or_cutoff',lambda r:r.update(as_of='2024-06-30'))
    add('information-lookahead','rejected','information_cutoff',lambda r:r['events'][4].update(information_date='2024-05-02'))
    add('source-outside-period','unsupported','source_interval',lambda r:r.update(annual_start='2027-01-01'))
    add('calendar-unsupported','unsupported','annual_calendar',lambda r:r.update(annual_start='2024-04-01'))
    add('wrong-book','rejected','context',lambda r:r['events'][1]['context'].update(book='group'))
    add('posting-request','rejected','report_only',lambda r:r.update(operation='post'))
    add('supplied-revenue','rejected','event_shape',lambda r:r['events'][1].update(earned_revenue='55'))
    add('unknown-operation','unsupported','different_operation',lambda r:r['events'][1].update(operation='cancel'))
    add('new-cost-below-incurred','unsupported','mixed_amendment_stage',lambda r:r['events'][4].update(new_expected_cost='40'))
    def repeated(r):
        e=deepcopy(r['events'][4]);e.update(id='amend-again');r['events'].insert(5,e)
    add('repeat-amendment','unsupported','repeated_amendment',repeated)
    for c in adverse:
        saved=deepcopy(c['request']);r=calculate(c['request']);c['actual']=dict(status=r['status'],reason=r['reason'])
        check(c['id']+'/refusal',(r['status'],r['reason'])==(c['expected_status'],c['expected_reason']),c['actual'])
        check(c['id']+'/atomic',c['request']==saved and r['report'] is None and r['trace']==r['journals']==r['cash_flows']==r['mutations']==[])
    source=ROOT/'docs/design/proposal/methods/sources/aasb15-compiled-dec2022.txt'
    def missing(p):
        if p==source:raise FileNotFoundError(p)
        return p.read_bytes()
    for id,reader,status in [('missing-source',missing,'unresolved'),('changed-source',lambda p:b'changed' if p==source else p.read_bytes(),'rejected')]:
        r=calculate(base,reader);check(id,r['status']==status and r['report'] is None and not r['journals'])
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not x['passed'] for x in checks),
        failed=[x for x in checks if not x['passed']],cases=len(cases),adverse_inputs=len(adverse),resolver_challenges=2,
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/mixed-contract-billing-20261016/verify.py',
        environment=sys.executable+'; standard library/Fraction; no ML import',gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        data_version='input-lock.json; seven independently authored paths/cutoffs',random_seeds='N/A deterministic',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-mixed-contract-billing-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),
        outputs=[str((attempt/x).relative_to(ROOT)) for x in ('checks.json','exchanges.json','adverse.json')])
    for name,value in [('checks.json',dict(summary=summary,checks=checks)),('exchanges.json',exchanges),('adverse.json',adverse)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'run-manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('attempt','checks','failures','cases','adverse_inputs','resolver_challenges','wall_seconds')}))
    if summary['failures']:raise SystemExit(1)

if __name__=='__main__':main()
