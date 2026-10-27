"""Authored financial targets, origin identities and atomic refusal examples."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib,json,os,shutil,subprocess,sys,time
sys.dont_write_bytecode=True
from reference import ROOT,OUT,SOURCE,calculate

def main():
    started=time.monotonic();numbers=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(numbers,default=0)+1));attempt.mkdir()
    for n in ('reference.py','verify.py','authored-cases.json','input-lock.json'):shutil.copy2(OUT/n,attempt/n)
    checks=[];exchanges=[];adverse=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    def targets(prefix,actual,expected):
        if isinstance(expected,dict):
            for k,v in expected.items():targets(prefix+'/'+k,actual.get(k),v)
        elif isinstance(expected,list):
            check(prefix+'/length',len(actual)==len(expected))
            for i,(a,e) in enumerate(zip(actual,expected)):targets(prefix+'/'+str(i),a,e)
        else:check(prefix,actual==expected,dict(expected=expected,actual=actual))
    for x in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('protected/'+x['path'],hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'])
    cases=json.loads((OUT/'authored-cases.json').read_text())['cases']
    for c in cases:
        q=deepcopy(c['request']);before=deepcopy(q);r=calculate(q);prefix=c['id']
        exchanges.append(dict(id=c['id'],request=q,result=r))
        check(prefix+'/status',r['status']=='conditional_complete',r['reason'])
        check(prefix+'/readonly-repeatable',before==q and r==calculate(q) and not r['posts'] and r['mutations']==[])
        if r['status']!='conditional_complete':continue
        x=r['report'];targets(prefix,x,c['expected']);d=q['data'];op=q['operation']
        if op=='loss_schedule':
            K=Q(d['loss_component']);L=Q(d['liability']);cash=Q(d['cash']);orig=K;ratio=K/L
            for i,(p,s) in enumerate(zip(d['periods'],x['rows'])):
                fin=Q(p['finance_expense']);release=Q(p['claim_release'])+Q(p['ra_release']);actual=Q(p['actual_claims'])
                L+=fin-release;K+=ratio*(fin-release);cash-=actual
                check(prefix+'/'+str(i)+'/independent-liability',Q(s['liability'])==L)
                check(prefix+'/'+str(i)+'/independent-loss',Q(s['loss_component'])==K)
                check(prefix+'/'+str(i)+'/independent-cash',Q(s['cash'])==cash)
                check(prefix+'/'+str(i)+'/service-allocation',Q(s['revenue'])+Q(s['loss_reversal'])==release)
                check(prefix+'/'+str(i)+'/equity',cash-L==Q(s['equity']))
            check(prefix+'/loss-exhaustion',orig+sum(Q(y['loss_change']) for y in x['loss_origins'])==0)
            check(prefix+'/finance-not-service',sum(Q(y['loss_change']) for y in x['loss_origins'] if y['kind']=='finance')==ratio*sum(Q(p['finance_expense']) for p in d['periods']))
            for i,j in enumerate(x['journals']):check(prefix+'/journal/'+str(i),sum(Q(v) for v in j.values())==0)
            check(prefix+'/cash-lifetime',cash-Q(x['opening_equity'])==Q(x['total_profit']))
            wrong=sum(Q(p['claim_release'])+Q(p['ra_release']) for p in d['periods'])+sum(Q(s['loss_reversal']) for s in x['rows'])-sum(Q(p['actual_claims'])+Q(p['finance_expense']) for p in d['periods'])
            if ratio:check(prefix+'/double-revenue-counterexample',wrong-Q(x['total_profit'])==21)
        elif op=='recovery_change':
            delta=Q(d['covered_claim_decrease']);quota=Q(d['quota']);chg=x['change'];close=x['closing']
            check(prefix+'/independent-held-fcf',Q(chg['held_profit'])==-delta*quota)
            check(prefix+'/recovery-not-second-asset',Q(chg['held_asset'])==(Q(d['covered_claims'])-delta)*quota+Q(d['held_ra'])+Q(d['held_cost_csm']))
            check(prefix+'/change-equity',Q(chg['equity'])-Q(x['opening_equity'])==delta*(1-quota))
            check(prefix+'/no-double-expense',Q(chg['additional_component_expense'])==0 and Q(chg['held_cost_csm'])==Q(d['held_cost_csm']))
            check(prefix+'/final-cash',Q(close['cash'])==Q(d['cash'])+sum(Q(y['amount']) for y in x['cash_flows']))
            check(prefix+'/cash-profit',Q(close['cash'])-Q(x['opening_equity'])==Q(x['total_profit']))
        elif op=='policy_switch':
            O=Q(d['old_oci']);newO=Q(0);initial=Q(x['initial_liability']);lastL=initial;profit=Q(0);oci=Q(0)
            for i,s in enumerate(x['rows'],1):
                current=Q(s['liability']);fp=Q(s['current_profit_expense']);rec=Q(s['old_reclassification_expense'])
                oldtarget=Q(d['old_allocation_carrying'])*(1+Q(d['old_allocation_rate']))**i-Q(d['terminal'])/(1+Q(d['old_current_rate']))**(d['years']-i)
                check(prefix+'/'+str(i)+'/frozen-direct-target',Q(s['old_oci'])==oldtarget and rec==oldtarget-O)
                check(prefix+'/'+str(i)+'/total-finance',Q(s['actual_total_finance'])==current-lastL)
                check(prefix+'/'+str(i)+'/split-finance',fp-Q(s['current_oci'])==current-lastL)
                if d['new_policy']=='89b':check(prefix+'/'+str(i)+'/separate-profit-matching',fp==Q(s['asset_profit']))
                newO+=Q(s['current_oci']);profit+=Q(s['profit']);oci+=Q(s['oci']);O=oldtarget;lastL=current
                check(prefix+'/'+str(i)+'/new-origin-history',newO==Q(s['new_oci']))
                check(prefix+'/'+str(i)+'/balance',Q(s['cash'])+Q(s['asset'])-current==Q(s['equity']))
                check(prefix+'/'+str(i)+'/total-equity',Q(x['opening_equity'])+profit+oci==Q(s['equity']))
            check(prefix+'/reclass-exhaustion',sum(Q(s['old_reclassification_expense']) for s in x['rows'])==-Q(d['old_oci']))
            check(prefix+'/frozen-bytes',x['frozen_assumptions']=={k:d[k] for k in x['frozen_assumptions']})
            check(prefix+'/closing-equity',Q(x['closing']['cash'])==Q(x['opening_equity'])+Q(x['total_profit'])+Q(x['total_oci']))
        else:
            check(prefix+'/equity-conserved',Q(x['profit_reclassification'])+Q(x['oci_reclassification'])==0)
            check(prefix+'/cash-origin',Q(x['closing']['cash'])==Q(d['cash'])-Q(d['transfer_cash']))
            check(prefix+'/original-policy',Q(x['profit_reclassification'])==(Q(d['accumulated_oci']) if d['origin_policy']=='88b' else 0))
    results={c['id']:c['result']['report'] for c in exchanges}
    if results.get('matching-lower-current') and results.get('matching-higher-current'):
        a=results['matching-lower-current'];b=results['matching-higher-current']
        check('changed-actual-measurement-preserves-old-schedule',[s['old_reclassification_expense'] for s in a['rows']]==[s['old_reclassification_expense'] for s in b['rows']])
        check('changed-actual-measurement-changes-new-origin',a['rows'][0]['new_oci']!=b['rows'][0]['new_oci'])
    def add(name,change,baseline):
        q=deepcopy(baseline);change(q);before=deepcopy(q);r=calculate(q)
        adverse.append(dict(id=name,request=q,result=r));check('adverse/'+name,r['status'] in ('rejected','unsupported','unresolved'),r['reason'])
        check('atomic/'+name,r['report'] is None and r['mutations']==[] and not r['posts'] and before==q)
    baseline=cases[0]['request']
    for k in baseline['findings']:
        for v in (False,None):add('common/'+k+'/'+str(v),lambda q,k=k,v=v:q['findings'].update({k:v}),baseline)
    for i in (0,2,4,7):
        base=cases[i]['request']
        for k in base['data']['findings']:
            for v in (False,None):add(base['operation']+'/'+k+'/'+str(v),lambda q,k=k,v=v:q['data']['findings'].update({k:v}),base)
    mods=[('wire',0,lambda q:q.update(wire='IFRS17')),('source-context',0,lambda q:q['context'].update(rule='AASB17')),
        ('number-encoding',0,lambda q:q['data'].update(cash='200.0')),('unknown-cash',0,lambda q:q['data'].update(cash=None)),
        ('loss-above-liability',0,lambda q:q['data'].update(loss_component='101')),('over-release',0,lambda q:q['data']['periods'][0].update(claim_release='120')),
        ('not-exhausted',0,lambda q:q['data']['periods'][1].update(claim_release='44')),('finance-exhaustion',0,lambda q:q['data']['periods'][0].update(finance_expense='-101')),
        ('early-coverage-end',0,lambda q:q['data']['periods'][0].update(coverage_end=True)),('future-information',0,lambda q:q['data']['periods'][0].update(information_date='2028-01-01')),
        ('loss-recovery-double',2,lambda q:q['data'].update(held_loss_recovery='8')),('uncovered-loss',2,lambda q:q['data'].update(covered_loss='21')),
        ('excess-favorable-change',2,lambda q:q['data'].update(covered_claim_decrease='9')),('quota-over-one',2,lambda q:q['data'].update(quota='2')),
        ('missing-oci-origin',4,lambda q:q['data'].update(old_policy='unknown')),('recomputed-old-reserve',4,lambda q:q['data'].update(old_oci='0')),
        ('reset-frozen-rate',4,lambda q:q['data'].update(old_allocation_rate='1/10')),('missing-old-rate',4,lambda q:q['data'].update(old_current_rate=None)),
        ('inferred-holdings',4,lambda q:q['data']['periods'][0].update(actual_holdings=False)),('copied-current-to-frozen',4,lambda q:q['data'].update(old_current_rate='0')),
        ('unbalanced-underlying',4,lambda q:q['data']['periods'][0].update(asset_oci_income='0')),('terminal-mismatch',4,lambda q:q['data']['periods'][1].update(current_liability='145')),
        ('unheld-return',6,lambda q:q['data']['periods'][0].update(asset_profit_income='1')),('transfer-consideration',7,lambda q:q['data'].update(transfer_cash='99')),
        ('mixed-origin-derecognition',7,lambda q:q['data'].update(origin_policy='mixed')),('with-pending-runoff',7,lambda q:q['data']['findings'].update(no_pending_policy_runoff=False))]
    for name,i,change in mods:add(name,change,cases[i]['request'])
    def missing(_):raise FileNotFoundError(SOURCE)
    for name,reader,status in [('missing',missing,'unresolved'),('changed',lambda _:b'changed','rejected')]:
        r=calculate(baseline,reader);check('source/'+name,r['status']==status and r['report'] is None)
    manifest=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],cases=len(cases),adverse_inputs=len(adverse),source_challenges=2,
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-service-finance-origins-20261016/verify.py',environment=sys.executable+'; standard library exact Fraction; no framework import',gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',random_seeds='N/A deterministic',data_version='authored-cases.json/input-lock.json',wall_seconds=round(time.monotonic()-started,3),plan='docs/plans/accounting-insurance-service-finance-origins-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),outputs=[str((attempt/n).relative_to(ROOT)) for n in ('checks.json','exchanges.json','adverse.json')])
    for name,value in [('checks.json',dict(summary=manifest,checks=checks)),('exchanges.json',exchanges),('adverse.json',adverse),('run-manifest.json',manifest)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ('attempt','checks','failures','failed','cases','adverse_inputs','wall_seconds')}))
    if manifest['failures']:raise SystemExit(1)
if __name__=='__main__':main()
