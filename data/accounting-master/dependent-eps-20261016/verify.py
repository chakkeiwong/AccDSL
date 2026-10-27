"""Independent joint earnings, eligibility and atomic refusal evidence."""
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
from reference import OUT,ROOT,SOURCE,WORLD_FINDINGS,OPTION_FINDINGS,calculate

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
    authored=json.loads((OUT/'authored-cases.json').read_text())
    for case in authored['world_cases']:
        req=deepcopy(case['request']);before=deepcopy(req);r=calculate(req);prefix=case['id']+'/'
        exchanges.append(dict(id=case['id'],request=req,result=r))
        check(prefix+'status',r['status']=='conditional_worlds_complete',r['reason'])
        check(prefix+'readonly',before==req and r==calculate(req) and r['mutations']==[])
        if r['status']!='conditional_worlds_complete':continue
        check(prefix+'no-selection',r['diluted'] is None and r['selected'] is None and r['selection_status']=='not_evaluated')
        check(prefix+'world-inventory',{'+'.join(w['assumed']) for w in r['worlds']}==set(case['expected']))
        reverse=deepcopy(req);reverse['series'].reverse();check(prefix+'input-order',calculate(reverse)==r)
        series={x['id']:x for x in req['series']}
        for w in r['worlds']:
            key='+'.join(w['assumed']);expected=case['expected'][key]
            for field,value in expected.items():check(prefix+key+'/'+field,w[field]==value,dict(expected=value,actual=w[field]))
            p=Q(req['pretax_before_bonus'])+sum((Q(series[id]['interest_saved']) for id in w['assumed']),Q(0))
            H=Q(req['bonus_threshold']);q=Q(req['bonus_rate']);t=Q(req['tax_rate'])
            net=p if p<=H else H+(1-q)*(p-H)
            check(prefix+key+'/independent-after-bonus',net==Q(w['earnings'])+Q(w['tax']))
            check(prefix+key+'/conservation',Q(w['pretax_before_bonus'])==Q(w['bonus'])+Q(w['tax'])+Q(w['earnings']))
            check(prefix+key+'/tax',Q(w['tax'])==t*net)
            check(prefix+key+'/shares',Q(w['shares'])==Q(req['ordinary_shares'])+sum((Q(series[id]['incremental_shares']) for id in w['assumed']),Q(0)))
    for case in authored['option_cases']:
        req=deepcopy(case['request']);before=deepcopy(req);r=calculate(req);prefix=case['id']+'/'
        exchanges.append(dict(id=case['id'],request=req,result=r))
        check(prefix+'status',r['status']=='conditional_complete',r['reason'])
        check(prefix+'readonly',before==req and r==calculate(req) and r['mutations']==[])
        if r['status']!='conditional_complete':continue
        check(prefix+'expected-eps',r['diluted']['eps']==case['expected']['eps'])
        check(prefix+'expected-selection',r['selected']==case['expected']['selected'])
        check(prefix+'dependent-disposition',r['trace'][1]['reason']==case['expected']['contingent_reason'])
        check(prefix+'dependency',req['contingent']['id'] not in r['selected'] or req['similar']['id'] in r['selected'])
        check(prefix+'earnings-unchanged',r['basic']['earnings']==r['diluted']['earnings']==req['earnings'])
        increment=Q(0)
        for role in ('similar','contingent'):
            item=req[role];b=max(Q(0),Q(item['count'])-Q(item['count'])*Q(item['strike'])/Q(req['average_market_price']))
            row=next(x for x in r['trace'] if x['role']==role)
            check(prefix+'treasury/'+role,Q(row['incremental_shares'])==b)
            if row['reason']=='selected':increment+=b
        check(prefix+'denominator-conservation',Q(r['diluted']['shares'])==Q(req['ordinary_shares'])+increment)
    byid={x['id']:x['result'] for x in exchanges}
    joint={'+'.join(w['assumed']):w for w in byid['joint-threshold']['worlds']}
    check('nonadditive-four-unit-error',Q(joint['A']['earnings'])+Q(joint['B']['earnings'])-Q(joint['']['earnings'])-Q(joint['A+B']['earnings'])==4)
    check('marginal-twelve-then-eight',Q(joint['A']['earnings'])-Q(joint['']['earnings'])==12 and Q(joint['A+B']['earnings'])-Q(joint['A']['earnings'])==8)
    paradox={'+'.join(w['assumed']):w for w in byid['joint-minimum-is-not-selection']['worlds']}
    check('joint-minimum-does-not-override-individual-test',Q(paradox['A+B']['eps'])<Q(paradox['']['eps'])<Q(paradox['A']['eps']) and byid['joint-minimum-is-not-selection']['diluted'] is None)
    excluded=byid['similar-out-of-money']
    check('isolated-dilution-cannot-override-57',excluded['trace'][1]['if_assumed']['eps']=='10/11' and excluded['diluted']['eps']=='1')
    world=authored['world_cases'][0]['request'];option=authored['option_cases'][0]['request']
    def add(id,base,status,reason,change):
        r=deepcopy(base);change(r);adverse.append(dict(id=id,request=r,expected_status=status,expected_reason=reason))
    for kind,base,fields in [('world',world,WORLD_FINDINGS),('option',option,OPTION_FINDINGS)]:
        for field in sorted(fields):
            for val,status,stem in [(None,'unresolved','missing_'),(False,'unsupported','outside_')]:
                add(kind+'/'+field+'/'+str(val),base,status,stem+field,lambda r,k=field,v=val:r['findings'].update({k:v}))
        add(kind+'/context',base,'rejected','context',lambda r:r['context'].update(currency='USD'))
        add(kind+'/extra',base,'rejected','request_shape',lambda r:r.update(selected=['B']))
        add(kind+'/zero-shares',base,'rejected','number_domain',lambda r:r.update(ordinary_shares='0'))
        add(kind+'/missing-shares',base,'unresolved','missing_ordinary_shares',lambda r:r.update(ordinary_shares=None))
        add(kind+'/decimal',base,'rejected','number_encoding',lambda r:r.update(ordinary_shares='100.0'))
        add(kind+'/finding-encoding',base,'rejected','finding_encoding',lambda r:r['findings'].update(whole_period=1))
    add('nonadditive-selector',world,'unsupported','nonadditive_selection_not_specified',lambda r:r.update(operation='report'))
    add('bonus-over-one',world,'rejected','rate_domain',lambda r:r.update(bonus_rate='3/2'))
    add('tax-one',world,'rejected','rate_domain',lambda r:r.update(tax_rate='1'))
    add('loss-tax-asset',world,'unsupported','loss_tax_recognition_not_specified',lambda r:r.update(pretax_before_bonus='-10'))
    add('third-series',world,'unsupported','two_series_required',lambda r:r['series'].append(deepcopy(r['series'][0])))
    add('duplicate-world-id',world,'rejected','series_identity',lambda r:r['series'][1].update(id='A'))
    add('negative-interest',world,'rejected','number_domain',lambda r:r['series'][0].update(interest_saved='-1'))
    add('zero-increment',world,'rejected','number_domain',lambda r:r['series'][0].update(incremental_shares='0'))
    add('world-dependence',world,'rejected','series_shape',lambda r:r['series'][0].update(requires='B'))
    add('option-post',option,'rejected','report_only',lambda r:r.update(operation='post'))
    add('zero-market',option,'rejected','number_domain',lambda r:r.update(average_market_price='0'))
    add('negative-strike',option,'rejected','number_domain',lambda r:r['contingent'].update(strike='-1'))
    add('fractional-count',option,'rejected','number_domain',lambda r:r['similar'].update(count='3/2'))
    add('same-id',option,'rejected','series_identity',lambda r:r['contingent'].update(id='O'))
    add('future-observation',option,'rejected','period_end_observation',lambda r:r['condition'].update(observed_date='2026-01-01'))
    add('stale-observation',option,'rejected','period_end_observation',lambda r:r['condition'].update(observed_date='2025-12-30'))
    add('partial-agreement',option,'unsupported','partial_period_agreement',lambda r:r['condition'].update(agreement_start='2025-02-01'))
    add('expired-contingency',option,'unsupported','expired_contingency',lambda r:r['condition'].update(contingency_end='2025-12-31'))
    add('different-condition',option,'unsupported','condition_kind',lambda r:r['condition'].update(kind='earnings'))
    add('invalid-date',option,'rejected','date_encoding',lambda r:r['condition'].update(observed_date='2025-02-30'))
    add('missing-count',option,'unresolved','missing_observed',lambda r:r['condition'].update(observed=None))
    add('forecast-count',option,'rejected','condition_shape',lambda r:r['condition'].update(forecast='6'))
    for c in adverse:
        before=deepcopy(c['request']);r=calculate(c['request']);c['actual']=r
        check(c['id']+'/refusal',(r['status'],r['reason'])==(c['expected_status'],c['expected_reason']),r['reason'])
        check(c['id']+'/atomic',c['request']==before and r['basic'] is None and r['diluted'] is None and r['selected'] is None and r['worlds']==r['trace']==r['mutations']==[])
    def missing(_):raise FileNotFoundError(SOURCE)
    source_checks=[]
    for kind,base in [('world',world),('option',option)]:
        for name,reader,status in [('missing',missing,'unresolved'),('changed',lambda _:b'changed','rejected')]:
            r=calculate(base,reader);check(kind+'/source/'+name,r['status']==status and r['basic'] is None and r['worlds']==[] and r['diluted'] is None)
            source_checks.append(dict(profile=kind,challenge=name,result=r))
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],
        world_cases=len(authored['world_cases']),worlds=28,option_cases=len(authored['option_cases']),adverse_inputs=len(adverse),source_challenges=len(source_checks),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/dependent-eps-20261016/verify.py',environment=sys.executable+'; standard library/Fraction; no ML import',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',random_seeds='N/A deterministic',
        data_version='7 joint-world cases;8 option cases;input-lock.json',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-dependent-eps-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ('checks.json','exchanges.json','adverse.json','source-challenges.json')])
    for name,value in [('checks.json',dict(summary=summary,checks=checks)),('exchanges.json',exchanges),('adverse.json',adverse),('source-challenges.json',source_checks),('run-manifest.json',summary)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'run-manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('attempt','checks','failures','world_cases','worlds','option_cases','adverse_inputs','source_challenges','wall_seconds')}))
    if summary['failures']:raise SystemExit(1)

if __name__=='__main__':main()
