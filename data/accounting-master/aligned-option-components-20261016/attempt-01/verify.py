"""Independent component targets, target-error counterexamples and gross cash."""
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
from reference import OUT,ROOT,SOURCE,FINDINGS,CLOSING_FINDINGS,calculate

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
        check(prefix+'readonly-repeatable',req==before and r==calculate(req) and r['mutations']==[])
        if r['status']!='conditional_complete':continue
        check(prefix+'quote-count',len(r['measurements'])==len(c['expected']['quotes'])==len(req['quotes']))
        for i,(m,expected) in enumerate(zip(r['measurements'],c['expected']['quotes'])):
            name=prefix+'q'+str(i+1)+'/'
            for key,value in expected.items():check(name+key,m[key]==value,dict(expected=value,actual=m[key]))
            check(name+'actual-decomposition',Q(m['actual_value'])==Q(m['actual_intrinsic'])+Q(m['actual_time_value']))
            check(name+'hypothetical-decomposition',Q(m['aligned_value'])==Q(m['aligned_intrinsic'])+Q(m['aligned_time_value']))
            check(name+'hedge-risk-payoff',Q(m['aligned_intrinsic'])==Q(req['item']['quantity'])*max(Q(0),Q(m['price'])-Q(req['item']['hedged_price'])))
            check(name+'intrinsic-conservation',Q(m['actual_intrinsic'])==Q(m['intrinsic_reserve'])+Q(m['intrinsic_profit']))
            check(name+'time-conservation',Q(m['actual_time_value'])-Q(req['actual']['initial_time_value'])==Q(m['cost_reserve'])+Q(m['time_profit']))
            check(name+'total-value-change',Q(m['actual_value'])-Q(req['premium_cash'])==Q(m['intrinsic_reserve'])+Q(m['cost_reserve'])+Q(m['profit']))
            check(name+'financial-equation',Q(m['cash'])+Q(m['actual_value'])==Q(m['equity']))
            check(name+'balanced-book',sum(Q(v) for v in m['books'].values())==0)
            check(name+'actual-asset-only',Q(m['books']['option'])==Q(m['actual_value']) and set(m['books'])=={'cash','capital','option','inventory','intrinsic_reserve','cost_reserve','earnings'})
        for key,value in c['expected']['closing'].items():check(prefix+'closing/'+key,r['closing'][key]==value)
        closed=r['closing'];books=closed['books']
        check(prefix+'both-basis-transfers',Q(closed['inventory'])==Q(closed['supplier_cost'])-Q(closed['intrinsic_basis_transfer'])-Q(closed['cost_basis_transfer']))
        check(prefix+'three-actual-cash-flows',[f['kind'] for f in r['cash_flows']]==['actual_premium','supplier_payment','actual_option_settlement'])
        check(prefix+'actual-premium-cash',r['cash_flows'][0]['amount']==str(-Q(req['premium_cash'])))
        check(prefix+'cash-origin-total',Q(closed['cash'])==Q(req['opening_cash'])+sum(Q(f['amount']) for f in r['cash_flows']))
        check(prefix+'economic-cost-bridge',Q(closed['inventory'])-Q(closed['profit'])==Q(req['premium_cash'])+Q(req['closing']['supplier_cash'])-Q(req['closing']['actual_settlement']))
        check(prefix+'closing-equity',Q(closed['cash'])+Q(closed['inventory'])==Q(closed['equity'])==Q(req['opening_cash'])+Q(closed['profit']))
        check(prefix+'closed-positions',all(Q(books[k])==0 for k in ('option','intrinsic_reserve','cost_reserve')))
        rebuilt={k:Q(0) for k in books};rebuilt.update(cash=Q(req['opening_cash']),capital=-Q(req['opening_cash']))
        for i,j in enumerate(r['journals']):
            check(prefix+'journal/'+str(i),sum(Q(x) for x in j['entries'].values())==0)
            for key,value in j['entries'].items():rebuilt[key]+=Q(value)
        check(prefix+'independent-ledger',all(rebuilt[k]==Q(v) for k,v in books.items()))
    byid={x['id']:x['result'] for x in exchanges}
    check('lower-actual-profit-reversal',[x['time_profit'] for x in byid['lower-actual']['measurements']]==['-1/2','0','0'])
    check('lower-actual-period-only-rule-wrong',byid['lower-actual']['measurements'][1]['cost_reserve']=='-3/2' and -min(Q(1),Q(1,2))-min(Q(1,2),Q(3,2))==Q(-1))
    wrong=dict(inventory='104',profit='-2',cash='94',equity='198',reason='Actual intrinsic30 substituted for hedged-item intrinsic20.')
    check('wrong-target-can-balance',Q(wrong['cash'])+Q(wrong['inventory'])==Q(wrong['equity'])==200+Q(wrong['profit']))
    check('wrong-target-refuted-by-independent-values',byid['higher-actual']['closing']['inventory']=='114' and byid['higher-actual']['closing']['profit']=='8')
    check('quantity-scaling',all(Q(byid['double-quantity']['closing'][k])==2*Q(byid['higher-actual']['closing'][k]) for k in ('cash','inventory','profit','equity')))
    base=cases[0]['request']
    def add(id,status,reason,change,baseline=base):
        r=deepcopy(baseline);change(r);adverse.append(dict(id=id,request=r,expected_status=status,expected_reason=reason))
    for group,fields in [('global',FINDINGS),('closing',CLOSING_FINDINGS)]:
        for field in sorted(fields):
            for val,status,stem in [(None,'unresolved','missing_'),(False,'unsupported','outside_')]:
                add(group+'/'+field+'/'+str(val),status,stem+field,lambda r,k=field,v=val,g=group:(r['findings'] if g=='global' else r['closing']['findings']).update({k:v}))
    add('mixed-rule','rejected','context',lambda r:r['context'].update(rule='AASB9'))
    add('quote-context','rejected','quote_context',lambda r:r['quotes'][0].update(context=dict(r['context'],currency='USD')))
    add('wrong-wire','rejected','wire',lambda r:r.update(wire='InstrumentReduction/1'))
    add('post','rejected','report_only',lambda r:r.update(operation='post'))
    add('hypothetical-cash','rejected','request_shape',lambda r:r.update(aligned_premium_cash='4'))
    add('same-contract-id','rejected','contract_identity',lambda r:r['aligned'].update(id='actual-call'))
    add('wrong-contract-kind','unsupported','contract_kind',lambda r:r['actual'].update(kind='written_call'))
    add('quantity-mismatch','rejected','quantity_binding',lambda r:r['aligned'].update(quantity='2'))
    add('expiry-mismatch','rejected','expiry_binding',lambda r:r['aligned'].update(expiry='2026-12-31'))
    add('actual-strike-copied-to-item','rejected','aligned_item_terms',lambda r:r['aligned'].update(strike='100'))
    add('nonzero-initial-intrinsic','unsupported','nonzero_initial_intrinsic',lambda r:r.update(opening_price='105'))
    add('equal-initial-unmatched','unsupported','equal_initial_unmatched_terms',lambda r:r['aligned'].update(initial_time_value='6'))
    add('omitted-premium','rejected','actual_premium_identity',lambda r:r.update(premium_cash='0'))
    add('aligned-premium-paid','rejected','actual_premium_identity',lambda r:r.update(premium_cash='4'))
    add('premium-funding','unsupported','premium_funding_required',lambda r:r.update(opening_cash='5'))
    add('supplier-funding','unsupported','supplier_funding_required',lambda r:r.update(opening_cash='130'))
    add('opposed-cumulative-change','unsupported','outside_common_loss_profile',lambda r:r['quotes'][0].update(aligned_time_value='5'))
    add('negative-time-value','rejected','number_domain',lambda r:r['quotes'][0].update(actual_time_value='-1'))
    add('unknown-component','unresolved','missing_aligned_time_value',lambda r:r['quotes'][0].update(aligned_time_value=None))
    add('decimal-input','rejected','number_encoding',lambda r:r['quotes'][0].update(actual_time_value='3.0'))
    add('actual-total-as-time','rejected','component_decomposition',lambda r:r['quotes'][0].update(actual_option_value='21'))
    add('actual-value-as-hypothetical','rejected','component_decomposition',lambda r:r['quotes'][0].update(aligned_option_value='18'))
    add('swapped-quote-identity','rejected','quote_contract_binding',lambda r:r['quotes'][0].update(aligned_id='actual-call'))
    add('duplicate-quote','rejected','duplicate_quote',lambda r:r['quotes'][1].update(id='q1'))
    add('quote-time-reversal','rejected','quote_chronology',lambda r:r['quotes'][1].update(date='2025-01-01'))
    add('invalid-date','rejected','date_encoding',lambda r:r['quotes'][0].update(date='2025-02-30'))
    add('no-expiry-quote','unresolved','expiry_measurement_required',lambda r:r['quotes'].pop())
    add('nonzero-expiry-time','rejected','nonzero_expiry_time_value',lambda r:r['quotes'][2].update(actual_time_value='1',actual_option_value='31'))
    add('closing-date','rejected','closing_date',lambda r:r['closing'].update(date='2025-12-30'))
    add('netted-supplier-payment','rejected','purchase_identity',lambda r:r['closing'].update(supplier_cash='100'))
    add('hypothetical-settlement','rejected','actual_settlement_identity',lambda r:r['closing'].update(actual_settlement='20'))
    add('finding-encoding','rejected','finding_encoding',lambda r:r['findings'].update(pretax_only=1))
    add('matched-values-diverge','rejected','matched_component_values',lambda r:r['quotes'][0].update(aligned_time_value='1'),baseline=cases[2]['request'])
    for c in adverse:
        before=deepcopy(c['request']);r=calculate(c['request']);c['actual']=r
        check(c['id']+'/refusal',(r['status'],r['reason'])==(c['expected_status'],c['expected_reason']),r['reason'])
        check(c['id']+'/atomic',before==c['request'] and r['closing'] is None and r['measurements']==r['journals']==r['cash_flows']==r['mutations']==[])
    def missing(_):raise FileNotFoundError(SOURCE)
    source_checks=[]
    for name,reader,status in [('missing',missing,'unresolved'),('changed',lambda _:b'changed','rejected')]:
        r=calculate(base,reader);source_checks.append(dict(challenge=name,result=r));check('source/'+name,r['status']==status and r['closing'] is None and r['journals']==[])
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],
        cases=len(cases),measurements=18,adverse_inputs=len(adverse),source_challenges=len(source_checks),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/aligned-option-components-20261016/verify.py',environment=sys.executable+'; standard library/Fraction; no ML import',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',random_seeds='N/A deterministic',
        data_version='6 protected paths/18 observations;input-lock.json',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-aligned-option-components-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ('checks.json','exchanges.json','adverse.json','source-challenges.json','wrong-target-counterexample.json')])
    for name,value in [('checks.json',dict(summary=summary,checks=checks)),('exchanges.json',exchanges),('adverse.json',adverse),('source-challenges.json',source_checks),('wrong-target-counterexample.json',wrong),('run-manifest.json',summary)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'run-manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('attempt','checks','failures','cases','measurements','adverse_inputs','source_challenges','wall_seconds')}))
    if summary['failures']:raise SystemExit(1)

if __name__=='__main__':main()
