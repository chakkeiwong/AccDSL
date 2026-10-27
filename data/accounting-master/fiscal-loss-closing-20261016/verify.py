"""Independent period targets and legal/group/retained/tax-origin checks."""
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
from reference import OUT,ROOT,PACKET,SOURCE,FINDINGS,SHARES,PL,calculate,present_offset

def main():
    started=time.monotonic();nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for n in ('reference.py','verify.py','authored-cases.json','input-lock.json'):shutil.copy2(OUT/n,attempt/n)
    checks=[];exchanges=[];adverse=[];offset_results=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for row in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('protected/'+row['path'],hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'])
    assert all(c['passed'] for c in checks)
    authored=json.loads((OUT/'authored-cases.json').read_text());cases=authored['cases']
    for c in cases:
        req=deepcopy(c['request']);before=deepcopy(req);r=calculate(req);exchanges.append(dict(id=c['id'],request=req,result=r));prefix=c['id']+'/'
        check(prefix+'status',r['status']=='conditional_complete',r['reason'])
        check(prefix+'readonly-repeatable',r==calculate(req) and before==req and r['mutations']==[])
        if r['status']!='conditional_complete':continue
        check(prefix+'report-count',len(r['reports'])==len(c['expected']))
        last_p=Q('123/2');last_s=Q('105/2');last_geq=Q(724);last_peq=Q('2835/4');last_nci=Q('61/4')
        for n,(report,expected) in enumerate(zip(r['reports'],c['expected'])):
            name=prefix+report['id']+'/'
            for category,fields in expected.items():
                for key,value in fields.items():check(name+category+'/'+key,report[category][key]==value,dict(expected=value,actual=report[category][key]))
            p=report['P'];s=report['S'];g=report['group'];loss=report['loss']
            check(name+'P-close',Q(p['retained'])==last_p+Q(p['profit']))
            check(name+'S-close',Q(s['retained'])==last_s+Q(s['profit']))
            check(name+'group-equity-roll',Q(g['equity'])==last_geq+Q(g['profit']))
            check(name+'parent-equity-roll',Q(g['parent_equity'])==last_peq+Q(g['parent_profit']))
            check(name+'nci-roll',Q(g['nci'])==last_nci+Q(g['nci_profit']))
            check(name+'income-attribution',Q(g['profit'])==Q(p['profit'])+Q(s['profit'])==Q(g['parent_profit'])+Q(g['nci_profit']))
            check(name+'gross-tax-presentation',Q(g['dta'])==Q(p['dta']) and Q(g['current_tax_payable'])==Q(p['current_tax_payable'])+Q(s['current_tax_payable']))
            check(name+'loss-roll',Q(loss['remaining'])==Q(loss['opening'])+Q(loss['new'])-Q(loss['used'])-Q(loss['expired']))
            check(name+'loss-populations',Q(loss['remaining'])==Q(loss['recognised_quantity'])+Q(loss['unrecognised_quantity']))
            check(name+'deferred-origins',Q(p['deferred_tax_expense'])==sum(Q(loss[k]) for k in ('rate_effect','consumption_expense','expiry_expense','reassessment_expense')))
            check(name+'full-book-consolidation',Q(g['equity'])==Q(p['equity'])+Q(s['equity'])-100)
            check(name+'cash-flow-indirect',g['direct_operating_cash']==g['indirect_operating_cash'])
            check(name+'closed-income',all(Q(book.get(k,'0'))==0 for book in report['closed_books'].values() for k in PL))
            check(name+'calendar-length',report['days']==[181,365,366][n])
            check(name+'eps-no-annualising',Q(g['basic_eps'])==Q(g['parent_profit'])/Q(req['ordinary_shares'])==Q(g['diluted_eps']))
            for entity in ('P','S'):
                check(name+entity+'/book-balanced',sum(Q(x) for x in report['closed_books'][entity].values())==0)
            last_p=Q(p['retained']);last_s=Q(s['retained']);last_geq=Q(g['equity']);last_peq=Q(g['parent_equity']);last_nci=Q(g['nci'])
        for i,j in enumerate(r['journals']):check(prefix+'journal/'+str(i),sum(Q(x) for x in j['entries'].values())==0)
        final=r['reports'][-1];cash_net=sum(Q(x['amount']) for x in r['cash_flows'])
        check(prefix+'gross-cash-conservation',Q(final['group']['cash'])==644+cash_net)
        check(prefix+'profit-to-equity',sum(Q(x['group']['profit']) for x in r['reports'])==Q(final['group']['equity'])-724)
        check(prefix+'no-old-income-in-new',sum(Q(j['entries'].get('retained','0')) for j in r['journals'] if j['period']=='prior2025')==Q(-102))
    byid={x['id']:x['result'] for x in exchanges}
    if all(x['status']=='conditional_complete' for x in byid.values()):
        base=byid['supported-recovery']
        check('stub-prefix-preserved',byid['stub-only']['reports']==base['reports'][:1])
        check('future-recovery-cannot-rewrite-stub',byid['reduced-recovery']['reports'][0]==base['reports'][0])
        check('final-independent-of-earlier-recognition',all(byid[id]['reports'][-1]['group'][k]==base['reports'][-1]['group'][k] for id in ('no-deferred-asset','reduced-recovery') for k in ('cash','equity','parent_equity','nci')))
        check('base-complete-cash-origin',sum(Q(x['amount']) for x in base['cash_flows'] if x['kind']=='customer_receipt')==240 and sum(Q(x['amount']) for x in base['cash_flows'] if x['kind']=='operating_cost')==-150 and sum(Q(x['amount']) for x in base['cash_flows'] if x['kind']=='tax_payment')==-17)
        check('base-expiry-retains-lost-quantity',base['reports'][-1]['loss']['expired']=='20' and base['reports'][-1]['loss']['expiry_expense']=='3')
        check('base-rate-origin',base['reports'][1]['loss']['rate_effect']=='-2' and base['reports'][1]['P']['deferred_tax_expense']=='1')
        check('comparative-identities',[x['comparative_period'] for x in base['reports']]==['prior2025','stub2026','fy2027'])
    for c in authored['offsets']:
        r=present_offset(c['request']);offset_results.append(dict(id=c['id'],request=c['request'],result=r))
        check('offset/'+c['id'],r['status']=='conditional_complete' and r['presentation']==c['expected'])
        check('offset/'+c['id']+'/gross-preserved',r['gross']==dict(asset='10',liability='7') and r['mutations']==[])
    baseline=deepcopy(cases[0]['request'])
    def add(id,status,reason,change):
        req=deepcopy(baseline);change(req);adverse.append(dict(id=id,expected_status=status,expected_reason=reason,request=req))
    for k in sorted(FINDINGS):
        for v,st,tag in [(None,'unresolved','missing_'),(False,'unsupported','outside_')]:
            add('period-finding/'+k+'/'+str(v),st,tag+k,lambda r,k=k,v=v:r['periods'][1]['findings'].update({k:v}))
    for k in sorted(SHARES):
        for v,st,tag in [(None,'unresolved','missing_'),(False,'unsupported','outside_')]:
            add('share-finding/'+k+'/'+str(v),st,tag+k,lambda r,k=k,v=v:r['share_findings'].update({k:v}))
    add('unknown-recovery','unresolved','missing_convincing_next_period_evidence',lambda r:r['periods'][0]['recovery'].update(convincing_next_period_evidence=None))
    add('missing-assessment','unresolved','missing_assessment_complete',lambda r:r['periods'][0]['recovery'].update(assessment_complete=None))
    add('automatic-DTA','unsupported','unsupported_loss_recovery',lambda r:r['periods'][0]['recovery'].update(convincing_next_period_evidence=False))
    add('cross-entity-recovery','rejected','recovery_owner',lambda r:r['periods'][0]['recovery'].update(taxable_entity='S'))
    add('wrong-tax-authority','rejected','recovery_owner',lambda r:r['periods'][0]['recovery'].update(authority='S-tax'))
    add('excess-recovery','rejected','recovery_exceeds_usable_loss',lambda r:r['periods'][1]['recovery'].update(supported_loss='41'))
    add('expired-DTA','unsupported','unsupported_loss_recovery',lambda r:r['periods'][2]['recovery'].update(supported_loss='10'))
    def expired_positive(r):r['periods'][2]['recovery'].update(supported_loss='10',convincing_next_period_evidence=True)
    add('expired-supported-amount','rejected','recovery_exceeds_usable_loss',expired_positive)
    add('false-enactment','unsupported','outside_enacted',lambda r:r['periods'][1]['tax'].update(enacted=False))
    add('unknown-enactment','unresolved','missing_enacted',lambda r:r['periods'][1]['tax'].update(enacted=None))
    add('future-law','rejected','law_timing',lambda r:r['periods'][1]['tax'].update(law_date='2026-07-02'))
    add('future-effective','rejected','law_timing',lambda r:r['periods'][1]['tax'].update(effective_from='2027-07-01'))
    add('different-recovery-rates','unsupported','different_recovery_schedule',lambda r:r['periods'][1]['tax'].update(recovery_rate='1/4'))
    add('unknown-rate','unresolved','missing_current_rate',lambda r:r['periods'][0]['tax'].update(current_rate=None))
    add('bad-rate','unsupported','rate_domain',lambda r:r['periods'][0]['tax'].update(current_rate='2',recovery_rate='2'))
    add('duplicate-close','rejected','period_identity',lambda r:r['periods'][1].update(id='stub2026'))
    add('calendar-overlap','rejected','period_gap_overlap',lambda r:r['periods'][1].update(start='2026-06-30'))
    add('calendar-gap','rejected','period_gap_overlap',lambda r:r['periods'][1].update(start='2026-07-02'))
    add('changed-year-end','unsupported','fiscal_calendar',lambda r:r['periods'][1].update(end_exclusive='2027-01-01'))
    add('lookahead-information','rejected','information_cutoff',lambda r:r['periods'][0].update(information_date='2026-07-02'))
    add('missing-stub-reason','unresolved','missing_stub_reason',lambda r:r['calendar'].update(stub_reason=''))
    add('annualised-stub','unsupported','outside_short_comparatives_not_annualised',lambda r:r['calendar'].update(short_comparatives_not_annualised=False))
    add('changed-loss-law','unsupported','different_expiry_law',lambda r:r.update(loss_expiry_exclusive='2029-07-01'))
    add('tax-paid-more-than-due','unsupported','tax_overpayment',lambda r:r['periods'][0]['S'].update(tax_paid='6'))
    add('depreciation-exceeds-PPE','rejected','depreciation_exceeds_asset',lambda r:r['periods'][0]['P'].update(depreciation='81'))
    add('parent-second-loss','unsupported','multiple_loss_origins',lambda r:r['periods'][1]['P'].update(receipts='0'))
    add('subsidiary-loss','unsupported','subsidiary_loss_method',lambda r:r['periods'][0]['S'].update(cash_costs='21'))
    add('cash-funding','unsupported','cash_funding_required',lambda r:r['periods'][0]['P'].update(cash_costs='1000'))
    add('negative-cash-input','rejected','number_domain',lambda r:r['periods'][0]['P'].update(receipts='-1'))
    add('floating-input','rejected','number_encoding',lambda r:r['periods'][0]['P'].update(receipts=20.0))
    add('zero-shares','rejected','share_domain',lambda r:r.update(ordinary_shares='0'))
    add('wrong-opening-cash','rejected','opening_projection',lambda r:r['opening']['P'].update(cash='500'))
    add('old-retained-not-closed','rejected','opening_projection',lambda r:r['opening']['P'].update(retained='12'))
    add('netted-current-deferred','rejected','period_shape',lambda r:r['periods'][0].update(net_tax='5'))
    add('posting','rejected','report_only',lambda r:r.update(operation='post'))
    add('changed-reference','rejected','baseline_reference',lambda r:r.update(base_sha256='0'*64))
    add('four-periods','unsupported','period_list',lambda r:r['periods'].append(deepcopy(r['periods'][-1])))
    for c in adverse:
        before=deepcopy(c['request']);r=calculate(c['request']);c['actual']=dict(status=r['status'],reason=r['reason'])
        check(c['id']+'/refusal',(r['status'],r['reason'])==(c['expected_status'],c['expected_reason']),c['actual'])
        check(c['id']+'/atomic',c['request']==before and r['opening'] is None and r['closing_books'] is None and r['reports']==r['journals']==r['cash_flows']==r['mutations']==[])
    for name in (SOURCE,PACKET):
        target=ROOT/name
        def missing(p):
            if p==target:raise FileNotFoundError(p)
            return p.read_bytes()
        for id,reader,status in [('missing',missing,'unresolved'),('changed',lambda p:b'changed' if p==target else p.read_bytes(),'rejected')]:
            r=calculate(baseline,reader);check(id+'/'+name,r['status']==status and not r['reports'] and not r['journals'])
    offset_bad=[]
    for field,value,status in [('category','mixed','unsupported'),('legal_current_offset_right',None,'unresolved'),('same_authority',None,'unresolved')]:
        req=deepcopy(authored['offsets'][0]['request']);req[field]=value;r=present_offset(req)
        check('offset/refuse/'+field,r['status']==status and r['presentation'] is None and r['mutations']==[]);offset_bad.append(dict(request=req,result=r))
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not c['passed'] for c in checks),
        failed=[c for c in checks if not c['passed']],cases=len(cases),period_reports=sum(len(c['expected']) for c in cases),offset_cases=len(authored['offsets']),
        adverse_inputs=len(adverse),offset_adverse=len(offset_bad),resolver_challenges=4,
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/fiscal-loss-closing-20261016/verify.py',environment=sys.executable+'; standard library/Fraction; no ML import',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',random_seeds='N/A deterministic',
        data_version='input-lock.json; protected P5 closing; five authored paths and six offset cases',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-fiscal-loss-closing-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ('checks.json','exchanges.json','adverse.json','offsets.json')])
    for name,value in [('checks.json',dict(summary=summary,checks=checks)),('exchanges.json',exchanges),('adverse.json',adverse),('offsets.json',dict(cases=offset_results,adverse=offset_bad))]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'run-manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('attempt','checks','failures','cases','period_reports','offset_cases','adverse_inputs','wall_seconds')}))
    if summary['failures']:raise SystemExit(1)

if __name__=='__main__':main()
