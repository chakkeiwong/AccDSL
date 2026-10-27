from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib,json,os,shutil,subprocess,sys,time
sys.dont_write_bytecode=True
from reference import ROOT,OUT,calculate

def main():
    started=time.monotonic();nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for n in ('reference.py','verify.py','authored-cases.json','input-lock.json'):shutil.copy2(OUT/n,attempt/n)
    checks=[];exchanges=[];adverse=[]
    def check(n,ok,detail=None):checks.append(dict(name=n,passed=bool(ok),detail=detail))
    def targets(n,a,e):
        if isinstance(e,dict):
            for k,v in e.items():targets(n+'/'+k,a.get(k) if isinstance(a,dict) else None,v)
        elif isinstance(e,list):
            check(n+'/length',isinstance(a,list) and len(a)==len(e))
            if isinstance(a,list):
                for i,v in enumerate(e):targets(n+'/'+str(i),a[i] if i<len(a) else None,v)
        else:check(n,a==e,dict(expected=e,actual=a))
    lock=json.loads((OUT/'input-lock.json').read_text())['files']
    for item in lock:check('protected/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    cases=json.loads((OUT/'authored-cases.json').read_text())['cases']
    for c in cases:
        q=deepcopy(c['request']);before=deepcopy(q);r=calculate(q);n=c['id']
        exchanges.append(dict(id=n,request=q,result=r));check(n+'/status',r['status']=='conditional_complete',r['reason'])
        check(n+'/repeatable-readonly',before==q and r==calculate(q) and not r['posts'] and r['mutations']==[])
        if r['status']!='conditional_complete':continue
        x=r['report'];targets(n,x,c['expected']);prev=x['opening'];loss={k:Q(0) for k in ('P','B','I')};last_dta=loss.copy()
        check(n+'/worksheet-only',x['worksheet_only'] and x['legal_mutations']==[])
        check(n+'/opening-no-component-capital',Q(prev['equity'])==Q(prev['parent_equity'])+Q(prev['nci']) and prev['equity']=='694')
        for j,row in enumerate(x['rows']):
            p=n+'/'+str(j+1);g=row['group'];l=row['legal'];cf=row['cash_flow'];tx=row['tax'];own=row['ownership'];de=row['deposit_elimination'];gt=row['guarantee']
            P,B,I=[{k:Q(v) for k,v in l[e].items()} for e in ('P','B','I')]
            check(p+'/legal-P',P['cash']+P['investments']+P['dta']==P['guarantee']+P['equity'])
            check(p+'/legal-B',B['cash']+B['loan']+B['dta']==B['deposits']+B['equity'])
            check(p+'/legal-I',I['cash']+I['dta']==I['insurance_liability']+I['equity'])
            for k,t in tx.items():
                pretax=Q(t['pretax']);used=min(loss[k],max(pretax,Q(0)));expected_loss=loss[k]-used+max(-pretax,Q(0))
                check(p+'/tax/'+k,Q(t['current'])==(max(pretax,Q(0))-used)/5 and Q(t['loss'])==expected_loss and Q(t['dta'])==expected_loss/5 and Q(t['deferred_expense'])==last_dta[k]-Q(t['dta']) and Q(t['aftertax'])==pretax-Q(t['current'])-Q(t['deferred_expense']))
                loss[k]=expected_loss;last_dta[k]=Q(t['dta'])
            check(p+'/guarantee-higher-of',Q(gt['liability'])==max(Q(gt['ecl']),Q(gt['unamortized'])) and Q(gt['pretax'])==Q(gt['service_income'])-Q(gt['impairment']))
            check(p+'/financial-equation',Q(g['assets'])==Q(g['liabilities'])+Q(g['equity']) and Q(g['equity'])==Q(g['parent_equity'])+Q(g['nci']))
            check(p+'/group-equity-bridge',Q(prev['equity'])+Q(g['profit'])+Q(g['oci'])+Q(own['cash'])==Q(g['equity']))
            check(p+'/parent-equity-bridge',Q(prev['parent_equity'])+Q(g['parent_profit'])+Q(g['parent_oci'])+Q(own['parent_equity_transaction'])==Q(g['parent_equity']))
            check(p+'/nci-bridge',Q(prev['nci'])+Q(g['nci_profit'])+Q(g['nci_oci'])-Q(own['nci_removed'])==Q(g['nci']))
            interval=Q(q['ownership']['bank_initial' if j==0 else 'bank_after']);io=Q(q['ownership']['insurer'])
            check(p+'/attribution-interval',Q(g['nci_profit'])==(1-interval)*Q(g['bank_profit'])+(1-io)*Q(g['insurer_profit']) and Q(g['nci_oci'])==(1-interval)*Q(g['bank_oci'])+(1-io)*Q(g['insurer_oci']))
            rate=Q(q['rates']['period1_close' if j==0 else 'period2_close'])
            check(p+'/matched-elimination',Q(de['cash'])==Q(de['deposits'])==20*rate and de['id']=='D1')
            check(p+'/gross-legal-to-net-group',Q(g['cash'])==P['cash']+(B['cash']+I['cash'])*rate-Q(de['cash']) and B['deposits']==200)
            check(p+'/no-guarantee-elimination',Q(g['liabilities'])==(B['deposits']+I['insurance_liability'])*rate-Q(de['deposits'])+P['guarantee'])
            operating=sum(Q(f['amount'])*Q(f['rate']) for f in cf['origins'] if f['kind']!='nci_purchase')
            financing=sum(Q(f['amount'])*Q(f['rate']) for f in cf['origins'] if f['kind']=='nci_purchase')
            check(p+'/direct-cash-origin-sum',operating==Q(cf['operating']) and financing==Q(cf['financing']))
            check(p+'/cash-bridge',sum(Q(cf[k]) for k in ('opening','operating','financing','fx'))==Q(cf['closing'])==Q(g['cash']))
            if c['id']=='constant-fx':check(p+'/zero-currency-effects',g['oci']==cf['fx']=='0')
            prev=g
        flows=x['cash_origins'];total=lambda kind:sum(Q(f['amount']) for f in flows if f['kind']==kind)
        check(n+'/contractual-principal',total('advance')+total('principal_receipt')==0)
        check(n+'/cash-interest-not-eir',total('coupon_interest_receipt')+total('integral_fee')==Q(31,2) and total('coupon_interest_receipt')!=Q(31,2))
        check(n+'/external-claim-payments',total('claim_payment')==-95)
    by={e['id']:e['result']['report'] for e in exchanges}
    if all(by.values()):
        a=by['joined-sector-group'];b=by['unchanged-ownership']
        check('purchase-no-subsidiary-book-entry',all(a['rows'][j]['legal'][k]==b['rows'][j]['legal'][k] for j in range(2) for k in ('B','I')))
        check('purchase-no-retroactive-profit',a['rows'][0]['group']['nci_profit']==b['rows'][0]['group']['nci_profit'] and a['rows'][1]['group']['nci_profit']!=b['rows'][1]['group']['nci_profit'])
        check('unchanged-component-oracles',exchanges[0]['result']['components']==exchanges[1]['result']['components']==exchanges[2]['result']['components'])
    base=cases[0]['request']
    def add(n,change):
        q=deepcopy(base);change(q);before=deepcopy(q);r=calculate(q);adverse.append(dict(id=n,request=q,result=r))
        check('adverse/'+n,r['status'] in ('unresolved','unsupported','rejected'),r['reason'])
        check('atomic/'+n,r['report'] is None and r['components'] is None and r['mutations']==[] and before==q and not r['posts'])
    for k in base['findings']:
        for v in (False,None):add(k+'/'+str(v),lambda q,k=k,v=v:q['findings'].update({k:v}))
    mods=[('wire',lambda q:q.update(wire='SectorCompany/2')),('post',lambda q:q.update(operation='post')),('rule',lambda q:q['context'].update(rule='AASB')),
        ('period',lambda q:q['context'].update(periods=['2025','2026'])),('extra-field',lambda q:q.update(plug='0')),('opening-bank',lambda q:q['opening'].update(bank_cash='301')),
        ('missing-parent-cash',lambda q:q['opening'].update(parent_cash=None)),('investment',lambda q:q['opening'].update(parent_investment_bank='81')),
        ('zero-rate',lambda q:q['rates'].update(period1_event='0')),('missing-rate',lambda q:q['rates'].update(period2_close=None)),('decimal-rate',lambda q:q['rates'].update(period1_close='1.2')),
        ('tax-rate',lambda q:q.update(tax_rate='1/4')),('missing-tax-rate',lambda q:q.update(tax_rate=None)),('lost-control',lambda q:q['ownership'].update(bank_after='2/5')),
        ('purchase-timing',lambda q:q['ownership'].update(purchase_timing='before_period1')),('no-consideration',lambda q:q['ownership'].update(purchase_price='0')),
        ('no-share-change',lambda q:q['ownership'].update(bank_after='4/5')),('over-funded-purchase',lambda q:q['ownership'].update(purchase_price='600')),
        ('deposit-id',lambda q:q['deposit']['insurer_record'].update(id='D2')),('deposit-counterpart',lambda q:q['deposit']['bank_record'].update(debtor='P')),
        ('deposit-currency',lambda q:q['deposit']['insurer_record'].update(currency='USD')),('deposit-amount',lambda q:q['deposit']['insurer_record'].update(amount='21')),
        ('deposit-cutoff',lambda q:q['deposit']['bank_record'].update(cutoff='opening')),('internal-guarantee',lambda q:q['guarantee'].update(beneficiary='B')),
        ('guarantee-ecl',lambda q:q['guarantee'].update(ecl=['8','3'])),('guarantee-release',lambda q:q['guarantee'].update(income_releases=['3','3'])),
        ('missing-principal',lambda q:q['loan_cash_allocation'][0].pop('principal')),('coupon-eir-confusion',lambda q:q['loan_cash_allocation'][0].update(coupon_interest='10')),
        ('missing-allocation',lambda q:q.update(loan_cash_allocation=None)),('leaked-capital',lambda q:q['component_maps']['bank'].update(opening_capital_action='post_capital')),
        ('wrong-entity-map',lambda q:q['component_maps']['insurance'].update(target_entity='B')),('wrong-unit',lambda q:q['component_maps']['bank'].update(unit_scale='1000')),
        ('nonboolean-finding',lambda q:q['findings'].update(control_retained='yes'))]
    for n,f in mods:add(n,f)
    challenges=[]
    for item in lock:
        for mode in ('changed','missing'):
            def reader(p,target=item['path'],mode=mode):
                if p==target:
                    if mode=='missing':raise FileNotFoundError(p)
                    return b'changed'
                return (ROOT/p).read_bytes()
            r=calculate(base,reader);challenges.append(dict(path=item['path'],mode=mode,result=r))
            check('input-challenge/'+mode+'/'+item['path'],r['status']==('unresolved' if mode=='missing' else 'rejected') and r['report'] is None and r['components'] is None and not r['posts'])
    manifest=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],cases=len(cases),adverse_inputs=len(adverse),input_challenges=len(challenges),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/sector-company-composition-20261016/verify.py',environment=sys.executable+'; standard-library Fraction; no framework import',gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',random_seeds='N/A deterministic',data_version='authored-cases.json/input-lock.json',wall_seconds=round(time.monotonic()-started,3),plan='docs/plans/accounting-sector-company-composition-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),outputs=[str((attempt/n).relative_to(ROOT)) for n in ('checks.json','exchanges.json','adverse.json','input-challenges.json')])
    for name,value in [('checks.json',dict(summary=manifest,checks=checks)),('exchanges.json',exchanges),('adverse.json',adverse),('input-challenges.json',challenges),('run-manifest.json',manifest)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ('attempt','checks','failures','failed','cases','adverse_inputs','input_challenges','wall_seconds')}))
    if manifest['failures']:raise SystemExit(1)
if __name__=='__main__':main()
