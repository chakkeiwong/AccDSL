"""Exact authored fixture versus separate monthly and journal reconstructions."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,time
OUT=Path(__file__).resolve().parent
started=time.perf_counter()
fixture=json.loads((OUT/'fixture.json').read_text())
I={k:F(v) for k,v in fixture['inputs'].items()}
checks=[]
def check(name,ok,detail=None):
    checks.append(dict(name=name,passed=bool(ok),detail=detail))
def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def serial(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
    if isinstance(x,list):return [serial(v) for v in x]
    return x

# A separate monthly path carries each balance rather than using expected rows.
paths={}
for history in ['original','error','estimate']:
    ppe=I['cost'];taxbase=I['cost'];dtl=F(0);cash=I['capital']-ppe
    payable=F(0);equity=I['capital']; revised_monthly=None
    stop=2024 if history=='original' else 2028
    for year in range(2023,stop+1):
        opening_dtl=dtl; dep=F(0); tax_paid=F(0)
        for month in range(1,13):
            cash+=I['annual_cash_income']/12
            if month==3:
                cash-=payable;tax_paid=payable;payable=F(0)
            if history=='error':charge=I['cost']/I['correct_life_months']
            elif history=='estimate' and (year,month)>=(2025,4):
                if revised_monthly is None:revised_monthly=ppe/I['new_remaining_months']
                charge=revised_monthly
            else:charge=I['cost']/I['old_life_months']
            ppe-=charge;dep+=charge;taxbase-=I['tax_deduction']/12
        pretax=I['annual_cash_income']-dep
        current=(I['annual_cash_income']-I['tax_deduction'])*I['tax_rate']
        dtl=(ppe-taxbase)*I['tax_rate'];deferred=dtl-opening_dtl
        net=pretax-current-deferred;equity+=net;payable+=current
        row=dict(zip(fixture['columns'],[dep,ppe,taxbase,dtl,pretax,current,deferred,net,cash,payable,equity]))
        paths[f'{history}_{year}']=row
        check(f'balance:{history}:{year}',cash+ppe==payable+dtl+equity)
        # Indirect operating cash reconciliation includes accrued tax changes.
        previous_tax=F(0) if year==2023 else current
        check(f'cashflow:{history}:{year}',net+dep+deferred+(current-previous_tax)==I['annual_cash_income']-tax_paid)
        check(f'tax-origin:{history}:{year}',current+deferred==pretax*I['tax_rate'])
for key,expected in fixture['expected'].items():
    for col,value in zip(fixture['columns'],expected):
        check(f'expected:{key}:{col}',paths[key][col]==F(value),str(paths[key][col]))
for year in [2023,2024]:
    check(f'estimate-keeps-original:{year}',paths[f'estimate_{year}']==paths[f'original_{year}'])
for year in [2023,2024,2025]:
    check(f'common-cash:{year}',paths[f'error_{year}']['cash']==paths[f'estimate_{year}']['cash'])
    check(f'common-current-tax:{year}',paths[f'error_{year}']['current_payable']==paths[f'estimate_{year}']['current_payable'])
for opening,deltas in fixture['opening_adjustments'].items():
    year=int(opening[:4])-1
    for col,delta in deltas.items():
        actual_col='equity' if col=='retained_earnings' else col
        check(f'opening:{opening}:{col}',paths[f'error_{year}'][actual_col]-paths[f'original_{year}'][actual_col]==F(delta))
check('earliest-opening-plus-comparative-movement',F('-15/2')+(paths['error_2024']['net_profit']-paths['original_2024']['net_profit'])==F(-15))
check('discovery-after-prior-authorization',date.fromisoformat(fixture['discovery'])>date.fromisoformat(fixture['authorization']['2024']))
check('no-issued-current-interim',fixture['current_interim_issued'] is False)
check('future-allocation-exhausts-remaining',F('39/2')+3*F(26)==F('195/2'))
check('terminal-same-total-not-same-history',paths['error_2028']['equity']==paths['estimate_2028']['equity'] and paths['error_2025']['equity']!=paths['estimate_2025']['equity'])

# Signed debit ledger independently reconstructs discovery and current closing.
ledger={'ppe_cost':I['cost'],'accumulated_depreciation':F('-45/2'),'dtl':F('-45/8'),'retained_earnings':F(-60),'depreciation_expense':F('5/2'),'deferred_tax_expense':F('5/8')}
for j in fixture['discovery_journals']:
    check('journal-balanced:'+j['id'],sum(map(F,j['debits'].values()))==sum(map(F,j['credits'].values())))
    for account,value in j['debits'].items():ledger[account]=ledger.get(account,F(0))+F(value)
    for account,value in j['credits'].items():ledger[account]=ledger.get(account,F(0))-F(value)
check('discovery-carrying-75',ledger['ppe_cost']+ledger['accumulated_depreciation']==75)
check('discovery-dtl-zero',ledger['dtl']==0)
check('prior-retained-45',ledger['retained_earnings']==-45)
check('current-quarter-expense-five',ledger['depreciation_expense']==5)
check('current-quarter-deferred-net-zero',ledger['deferred_tax_expense']==0)
ledger['accumulated_depreciation']-=15;ledger['depreciation_expense']+=15
check('book-to-restated-ppe',ledger['ppe_cost']+ledger['accumulated_depreciation']==paths['error_2025']['ppe'])
check('book-to-current-profit',I['annual_cash_income']-ledger['depreciation_expense']-F('15/2')==paths['error_2025']['net_profit'])
check('book-to-ending-equity',I['capital']-ledger['retained_earnings']+paths['error_2025']['net_profit']==paths['error_2025']['equity'])
check('not-charge-prior-20-to-current-profit',paths['error_2025']['net_profit']!=F('15/2'))
check('estimate-no-retrospective-20',paths['estimate_2024']['ppe']==100 and paths['estimate_2025']['ppe']==78)

# Semantic contract oracle, not a portable exchange/runtime implementation.
def classify(c):
    if not c.get('authority'):return 'TREATMENT_UNSUPPORTED'
    if c.get('policy_change'):return 'POLICY_ROUTE_REQUIRED'
    if c.get('availability') is None:return 'CLASSIFICATION_UNRESOLVED'
    if c.get('hindsight_required') or not c.get('no_hindsight'):return 'HINDSIGHT_REFUSED'
    if not c.get('tax_admitted'):return 'TAX_UNSUPPORTED'
    if c.get('public_shares') or c.get('public_filing') or c.get('voluntary_eps'):return 'EPS_REQUIRED_NOT_IN_THIS_FIXTURE'
    if c.get('original_misapplication') and c['availability']:
        if c.get('material') is None:return 'MATERIALITY_UNRESOLVED'
        if not c.get('material'):return 'MATERIAL_RESTATEMENT_ROUTE_NOT_ESTABLISHED'
        if c.get('practicable') is None:return 'PRACTICABILITY_UNRESOLVED'
        if not c.get('practicable'):return 'IMPRACTICABILITY_ROUTE_REQUIRES_SEPARATE_EVIDENCE'
        return 'PRIOR_ERROR'
    if c.get('genuinely_new_information') and c.get('old_estimate_reasonable'):return 'ESTIMATE_CHANGE'
    return 'CLASSIFICATION_UNRESOLVED'
base=fixture['conditions']|{'original_misapplication':True}
cases=[('prior',{},'PRIOR_ERROR'),('estimate',{'original_misapplication':False,'genuinely_new_information':True,'old_estimate_reasonable':True},'ESTIMATE_CHANGE'),('availability',{'availability':None},'CLASSIFICATION_UNRESOLVED'),('missing-materiality',{'material':None},'MATERIALITY_UNRESOLVED'),('immaterial-not-auto-error-clearance',{'material':False},'MATERIAL_RESTATEMENT_ROUTE_NOT_ESTABLISHED'),('missing-practicability',{'practicable':None},'PRACTICABILITY_UNRESOLVED'),('impracticability-separate',{'practicable':False},'IMPRACTICABILITY_ROUTE_REQUIRES_SEPARATE_EVIDENCE'),('hindsight',{'hindsight_required':True},'HINDSIGHT_REFUSED'),('policy',{'policy_change':True},'POLICY_ROUTE_REQUIRED'),('tax',{'tax_admitted':False},'TAX_UNSUPPORTED'),('authority',{'authority':False},'TREATMENT_UNSUPPORTED'),('public-shares',{'public_shares':True},'EPS_REQUIRED_NOT_IN_THIS_FIXTURE'),('voluntary-eps',{'voluntary_eps':True},'EPS_REQUIRED_NOT_IN_THIS_FIXTURE'),('public-filing',{'public_filing':True},'EPS_REQUIRED_NOT_IN_THIS_FIXTURE'),('difference-alone',{'original_misapplication':False},'CLASSIFICATION_UNRESOLVED')]
classifications={}
cases.append(('estimate-independent-of-error-route',{'original_misapplication':False,'genuinely_new_information':True,'old_estimate_reasonable':True,'material':None,'practicable':None},'ESTIMATE_CHANGE'))
cases.append(('unavailable-old-fact-not-proven-error',{'availability':False},'CLASSIFICATION_UNRESOLVED'))
for name,patch,expected in cases:
    result=classify(base|patch);classifications[name]=result;check('classification:'+name,result==expected)

class Bridge:
    def __init__(self):self.receipts={};self.targets=set();self.postings=[];self.close=digest(fixture['expected']['original_2024'])
    def apply(self,key,payload,stale=False,view='book'):
        if key in self.receipts:
            old=self.receipts[key]
            return old['status'] if old['payload']==digest(payload) else 'IDENTITY_PAYLOAD_CONFLICT'
        if view!='book':return 'COMPARATIVE_VIEW_CANNOT_POST'
        if stale:return 'STALE_DEPENDENCY'
        target=digest(payload['identity'])
        if target in self.targets:return 'CORRECTION_TARGET_ALREADY_APPLIED'
        self.targets.add(target);self.postings.append(deepcopy(payload))
        self.receipts[key]={'payload':digest(payload),'status':'COMMITTED'}
        return 'COMMITTED'
b=Bridge();original=digest(fixture['expected']['original_2024']);payload={'identity':fixture['bridge_identity'],'journal':fixture['discovery_journals'][0]}
check('first-bridge',b.apply('bridge-1',payload)=='COMMITTED')
check('retry-before-staleness',b.apply('bridge-1',payload,stale=True)=='COMMITTED' and len(b.postings)==1)
changed=deepcopy(payload);changed['journal']['debits']['retained_earnings']='16'
check('same-identity-different-payload',b.apply('bridge-1',changed)=='IDENTITY_PAYLOAD_CONFLICT')
check('new-key-same-correction',b.apply('bridge-2',payload)=='CORRECTION_TARGET_ALREADY_APPLIED')
check('presentation-cannot-post',b.apply('view',payload,view='comparative')=='COMPARATIVE_VIEW_CANNOT_POST')
check('new-stale-refused',b.apply('stale',payload,stale=True)=='STALE_DEPENDENCY')
check('immutable-original',b.close==original and digest(fixture['expected']['original_2024'])==original)
check('one-prior-correction',len(b.postings)==1)
result={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'wall_seconds':time.perf_counter()-started,'fixture_sha256':hashlib.sha256((OUT/'fixture.json').read_bytes()).hexdigest()}
(OUT/'calculation-checks.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'computed.json').write_text(json.dumps(serial({'paths':paths,'discovery_and_close_ledger':ledger,'classifications':classifications,'bridge_receipts':b.receipts}),indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['passed','check_count','wall_seconds']}|{'failed':[c['name'] for c in checks if not c['passed']]}))
if not result['passed']:raise SystemExit(1)
