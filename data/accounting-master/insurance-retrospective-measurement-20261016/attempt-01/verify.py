from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib,json,os,shutil,subprocess,sys,time
sys.dont_write_bytecode=True
from reference import ROOT,OUT,SOURCE,calculate

def main():
    started=time.monotonic();nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for n in ('reference.py','verify.py','authored-cases.json','input-lock.json'):shutil.copy2(OUT/n,attempt/n)
    checks=[];exchanges=[];adverse=[]
    def check(n,ok,detail=None):checks.append(dict(name=n,passed=bool(ok),detail=detail))
    def targets(n,a,e):
        if isinstance(e,dict):
            for k,v in e.items():targets(n+'/'+k,a.get(k),v)
        else:check(n,a==e,dict(expected=e,actual=a))
    for item in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('protected/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    cases=json.loads((OUT/'authored-cases.json').read_text())['cases']
    for c in cases:
        q=deepcopy(c['request']);before=deepcopy(q);r=calculate(q);n=c['id']
        exchanges.append(dict(id=n,request=q,result=r));check(n+'/status',r['status']=='conditional_complete',r['reason'])
        check(n+'/repeatable-readonly',before==q and r==calculate(q) and not r['posts'] and r['mutations']==[])
        if r['status']!='conditional_complete':continue
        x=r['report'];targets(n,x,c['expected']);s=x['transition'];ch={k:Q(v) for k,v in q['cash_history'].items()}
        cash=ch['capital']+ch['premium_received']-ch['acquisition_paid']-ch['claims_paid']-ch['reinsurance_premium_paid']+ch['recoveries_received']
        check(n+'/actual-cash',Q(s['cash'])==cash and x['transition_cash_flow']=='0')
        check(n+'/liability-no-double-loss',Q(s['liability'])==Q(s['fcf'])+Q(s['csm']))
        check(n+'/financial-equation',cash+Q(s['acquisition_asset'])+Q(s['held_asset'])-Q(s['liability'])==Q(s['equity']))
        check(n+'/equity-bridge',Q(s['equity'])-Q(x['prior_equity'])==Q(x['equity_adjustment']))
        check(n+'/balanced-transition',sum(Q(j['debit']) for j in x['transition_journals'])==0)
        check(n+'/cash-cost-not-erased',Q(x['known_acquisition_cash'])==ch['acquisition_paid'])
        check(n+'/csm-service',Q(s['csm'])==Q(x['initial']['csm'])*Q(2,3))
        if q['route']=='full':
            h=q['history'];check(n+'/full-uses-expected-not-actual',Q(x['initial']['expected_claims'])==Q(h['initial_claims']))
            if q['treaty'] is None:check(n+'/historical-profit',Q(s['equity'])==ch['capital']+Q(x['full_history_profit']))
        else:
            check(n+'/C12-known-history',Q(x['initial']['expected_claims'])==Q(q['measurement']['remaining_claims'])+ch['claims_paid'])
            check(n+'/C14-similar-contract',Q(x['initial']['ra'])==Q(q['measurement']['remaining_ra'])+Q(q['modified']['similar_contract_past_ra_release']))
        if q['acquisition']['allocation_mode']=='supported':check(n+'/acquisition-origins',Q(x['initial']['acquisition_adjustment'])+Q(s['acquisition_asset'])==ch['acquisition_paid'])
        else:check(n+'/nil-is-measurement-rule',x['initial']['acquisition_adjustment']==s['acquisition_asset']=='0' and x['known_acquisition_cash']=='10')
        if q['treaty']:
            t=q['treaty'];hh=x['held'];check(n+'/held-components',Q(s['held_asset'])==Q(s['held_fcf'])+Q(s['held_cost_csm']))
            check(n+'/recovery-inside-csm',Q(s['held_cost_csm'])==Q(hh['ordinary_remaining_cost_csm'])+Q(s['loss_recovery']))
            if t['recovery_mode']=='supported':check(n+'/covered-loss-recovery',Q(s['loss_recovery'])==Q(s['loss_component'])*Q(t['quota']))
            else:check(n+'/C16C-no-component',s['loss_recovery']=='0' and Q(s['held_asset'])>0)
    byid={x['id']:x['result']['report'] for x in exchanges}
    if all(byid.values()):
        check('same-history-route-agreement',byid['full-baseline']['transition']==byid['modified-baseline']['transition'])
        check('experience-full-csm-preserved',byid['full-different-claims-experience']['transition']['csm']==byid['full-baseline']['transition']['csm'])
        check('experience-modified-csm-differs',byid['modified-different-claims-experience']['transition']['csm']=='26/3')
        check('same-cash-different-route-equity',byid['full-different-claims-experience']['transition']['cash']==byid['modified-different-claims-experience']['transition']['cash'] and byid['full-different-claims-experience']['transition']['equity']!=byid['modified-different-claims-experience']['transition']['equity'])
        check('treaty-full-modified-agreement',byid['full-onerous-treaty']['transition']==byid['modified-onerous-treaty']['transition'])
    def add(n,change,base):
        q=deepcopy(base);change(q);before=deepcopy(q);r=calculate(q);adverse.append(dict(id=n,request=q,result=r))
        check('adverse/'+n,r['status'] in ('unresolved','unsupported','rejected'),r['reason'])
        check('atomic/'+n,r['report'] is None and r['mutations']==[] and before==q and not r['posts'])
    bases={c['id']:c['request'] for c in cases};full=bases['full-baseline'];modified=bases['modified-baseline'];treaty=bases['modified-onerous-treaty']
    for k in full['findings']:
        for v in (False,None):add('common/'+k+'/'+str(v),lambda q,k=k,v=v:q['findings'].update({k:v}),full)
    for name,base,path in [('full',full,'history'),('modified',modified,'modified'),('acquisition',modified,'acquisition'),('treaty',treaty,'treaty')]:
        for k in base[path]['findings']:
            for v in (False,None):add(name+'/'+k+'/'+str(v),lambda q,k=k,v=v,p=path:q[p]['findings'].update({k:v}),base)
    mods=[('wire',full,lambda q:q.update(wire='Transition/2')),('post',full,lambda q:q.update(operation='post')),('source-context',full,lambda q:q['context'].update(rule='AASB17')),
        ('nonzero-rate',full,lambda q:q['measurement'].update(rate='1/100')),('missing-rate',full,lambda q:q['measurement'].update(rate=None)),('decimal-cash',full,lambda q:q['cash_history'].update(claims_paid='30.0')),
        ('full-hindsight',full,lambda q:q['history'].update(information_date='2022-01-01')),('missing-full-history',full,lambda q:q.update(history=None)),('inconsistent-full-history',full,lambda q:q['history'].update(initial_claims='95')),
        ('wrong-transition',full,lambda q:q['dates'].update(transition='2023-01-01')),('late-acquisition',full,lambda q:q['dates'].update(acquisition_payment='2021-02-01')),
        ('missing-cash',full,lambda q:q['cash_history'].update(acquisition_paid=None)),('double-acquisition',full,lambda q:q['acquisition'].update(recognized_group='10')),
        ('unknown-modification',modified,lambda q:q['modified']['modifications'].append('C13')),('modified-late-info',modified,lambda q:q['modified'].update(information_date='2023-01-01')),
        ('missing-similar-RA',modified,lambda q:q['modified'].update(similar_contract_past_ra_release=None)),('wrong-coverage',modified,lambda q:q['measurement'].update(coverage_units_remaining='3')),
        ('unexplained-treaty-cash',full,lambda q:q['cash_history'].update(reinsurance_premium_paid='1')),('quota-mismatch',treaty,lambda q:q['treaty'].update(quota='3/4')),
        ('held-RA-copy',treaty,lambda q:q['treaty'].update(initial_ra='6')),('unknown-held-valuation',treaty,lambda q:q['treaty'].update(remaining_ra=None)),('unjustified-C16C',treaty,lambda q:q['treaty'].update(recovery_mode='C16C_none'))]
    for n,b,f in mods:add(n,f,b)
    nil=bases['modified-acquisition-information-nil'];add('nil-does-not-impute-values',lambda q:q['acquisition'].update(recognized_group='0'),nil)
    add('nil-needs-unavailability',lambda q:q['acquisition']['findings'].update(c14b_information_unavailable=False),nil)
    noR=bases['modified-unavailable-recovery-information'];add('C16C-needs-unavailability',lambda q:q['treaty']['findings'].update(c16a_information_unavailable=False),noR)
    def missing(_):raise FileNotFoundError(SOURCE)
    for n,reader,status in [('missing',missing,'unresolved'),('changed',lambda _:b'changed','rejected')]:
        r=calculate(full,reader);check('source/'+n,r['status']==status and r['report'] is None)
    manifest=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],cases=len(cases),adverse_inputs=len(adverse),source_challenges=2,
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-retrospective-measurement-20261016/verify.py',environment=sys.executable+'; standard-library Fraction; no framework import',gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',random_seeds='N/A deterministic',data_version='authored-cases.json/input-lock.json',wall_seconds=round(time.monotonic()-started,3),plan='docs/plans/accounting-insurance-retrospective-measurement-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),outputs=[str((attempt/n).relative_to(ROOT)) for n in ('checks.json','exchanges.json','adverse.json')])
    for name,value in [('checks.json',dict(summary=manifest,checks=checks)),('exchanges.json',exchanges),('adverse.json',adverse),('run-manifest.json',manifest)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ('attempt','checks','failures','failed','cases','adverse_inputs','wall_seconds')}))
    if manifest['failures']:raise SystemExit(1)
if __name__=='__main__':main()
