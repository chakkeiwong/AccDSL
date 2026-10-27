"""Full-company expectations and rejected fiscal/share/earnings projections."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from reference_company import ROOT, OUT, replay_base, base_facts, derive_company, report_request, canonical
from company_bridge import bridge, PREMISES, BASE_REF, SUPPORT


def main():
    started=time.monotonic()
    existing=[int(p.name.rsplit('-',1)[-1]) for p in OUT.glob('company-attempt-[0-9][0-9]') if p.is_dir()]
    attempt=OUT/('company-attempt-%02d'%(max(existing,default=0)+1));attempt.mkdir()
    import shutil
    code=attempt/'implementation';code.mkdir()
    for filename in ('reference_company.py','reference_tax.py','company_bridge.py','verify_company.py','runtime-input-lock.json'):
        shutil.copy2(OUT/filename,code/filename)
    expected=json.loads((OUT/'authored-expectations.json').read_text())
    checks=[];outputs={};requests={}
    def check(name,ok,detail=None):
        checks.append(dict(name=name,passed=bool(ok),detail=detail))
    def write(name,value):
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    for item in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('input/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    assert all(c['passed'] for c in checks),'Protected input changed'
    base=replay_base()
    base_before=canonical(base)
    for key,wanted in expected['baseline'].items():
        check('baseline/'+key,base['annual']['profit' if key=='group_profit' else key]==wanted)
    for event,actual in zip(base_facts.EVENTS,base['journals']):
        for owner in ('P','S'):
            check('baseline-journal/'+event['id']+'/'+owner,
                all(Q(v)==Q(event['journals'].get(owner,{}).get(k,'0')) for k,v in actual['journal'][owner].items()))
    assert all(c['passed'] for c in checks),'Base replay failed'
    for world in ('conversion','redemption'):
        company=derive_company(world,PREMISES,base)
        eps=report_request(world,company,PREMISES,SUPPORT)
        req=dict(wire='CompanyTaxEPS/1',operation='report',world=world,base_packet=BASE_REF,premises=PREMISES,eps=eps)
        requests[world]=deepcopy(req);before=canonical(req)
        result=bridge(req);outputs[world]=result
        check(world+'/status',result['status']=='conditional_complete',result['reason'])
        check(world+'/deterministic',bridge(req)==result)
        check(world+'/read-only',canonical(req)==before and canonical(base)==base_before and result['mutations']==[])
        financials=dict(company['financials']);diluted=result['eps']['diluted']
        financials.update(diluted_numerator=diluted['continuing_numerator'],diluted_denominator=diluted['denominator'],diluted_eps=diluted['continuing_eps'])
        for key,wanted in expected[world].items():
            check(world+'/'+key,financials[key]==wanted,dict(actual=financials[key],expected=wanted))
        for short in ('issue','issue_tax','accrue','accrue_tax','coupon',world):
            event=next(e for e in company['timeline'] if e['id']=='new.'+short)
            actual={k:v for k,v in event['journal']['P'].items() if v!='0'}
            check(world+'/journal/'+short,actual==expected['journal_targets'][short],actual)
        tax=next(e for e in company['timeline'] if e['id']=='tax-h2')['journal']['P']
        check(world+'/second-half-current-tax',all(tax[k]==v for k,v in expected['journal_targets']['parent_second_half_tax'].items()))
        for event in company['timeline']:
            check(world+'/'+event['id']+'/journal-balance',all(sum(Q(v) for v in b.values())==0 for b in event['journal'].values()))
        check(world+'/initial-tax-origin',company['tax_schedule']['stages'][0]['dtl']=='2')
        check(world+'/tax-cleared-before-settlement',company['tax_schedule']['stages'][2]['dtl']=='0')
        check(world+'/principal-after-coupon',company['liability_after_coupon']=='100')
        check(world+'/19-events',len(company['timeline'])==19)
        check(world+'/365-share-days',len(company['daily_shares'])==365)
        check(world+'/no-share-overlap',all(not(Q(d['actual'])>10 and Q(d['potential'])>0) for d in company['daily_shares']))
        check(world+'/no-double-equity-tax',Q(financials['parent_profit'])+Q(financials['potential_numerator_increment'])==Q(expected['baseline']['parent_profit']))
        write(world+'-request.json',req);write(world+'-result.json',result)
    cases=[]
    def adverse(name,status,code,fn):
        r=deepcopy(requests['conversion']);fn(r);cases.append(dict(id=name,status=status,code=code,request=r))
    adverse('post-operation','rejected','operation',lambda r:r.update(operation='post'))
    adverse('base-binding','rejected','base_binding',lambda r:r['base_packet'].update(sha256='0'*64))
    for key in PREMISES['new_instrument']['tax']:
        adverse('missing-'+key,'unresolved','missing_premise',lambda r,k=key:r['premises']['new_instrument']['tax'].update({k:None}))
    adverse('different-fiscal-base','unsupported','outside_company_profile',lambda r:r['premises']['new_instrument']['tax'].update(initial_liability_tax_base='92'))
    adverse('old-principal','unsupported','outside_company_profile',lambda r:r['premises']['new_instrument'].update(principal='92'))
    adverse('early-conversion','unsupported','outside_company_profile',lambda r:r['premises']['new_instrument'].update(maturity_date='2026-01-01'))
    adverse('incomplete-inventory','unresolved','incomplete_premises',lambda r:r['premises']['scope'].update(complete_instrument_inventory=False))
    adverse('incomplete-tax','unresolved','incomplete_premises',lambda r:r['premises']['new_instrument']['tax'].update(complete_consequences=False))
    adverse('malformed-shares','rejected','noncanonical_rational',lambda r:r['premises'].update(ordinary_opening_shares='20/2'))
    for value in ('3','11','12','7'):
        adverse('wrong-addback-'+value,'rejected','company_eps_projection_mismatch',lambda r,v=value:r['eps']['series'][0].update(continuing_increment=v,total_increment=v))
    for key,value in [('continuing_numerator','93'),('total_numerator','81/2'),('denominator','16')]:
        adverse('wrong-'+key,'rejected','company_eps_projection_mismatch',lambda r,k=key,v=value:r['eps']['basic'].update({k:v}))
    adverse('wrong-period','rejected','company_eps_projection_mismatch',lambda r:r['eps']['context']['period'].update(end_exclusive='2025-10-01'))
    adverse('overlap','rejected','company_eps_projection_mismatch',lambda r:r['eps']['series'][0]['potential_windows'][0].update(end_exclusive='2026-01-01'))
    for case in cases:
        before=canonical(case['request']);result=bridge(case['request'])
        case['actual']=dict(status=result['status'],reason=result['reason'])
        check(case['id']+'/refusal',(result['status'],result['reason'])==(case['status'],case['code']))
        check(case['id']+'/empty-read-only',result['company'] is None and result['eps'] is None and not result['mutations'] and canonical(case['request'])==before)
    def absent(path):
        raise FileNotFoundError(path)
    for name,resolver,status in [('missing',absent,'unresolved'),('corrupt',lambda p:b'changed','rejected')]:
        result=bridge(requests['conversion'],resolve_bytes=resolver)
        check('resolver/'+name,result['status']==status and result['company'] is None)
    write('adverse-cases.json',cases);write('checks.json',checks)
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not c['passed'] for c in checks),
        failed=[c for c in checks if not c['passed']],company_worlds=2,events_per_world=19,share_days=730,adverse_inputs=len(cases),resolver_challenges=2,
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/compound-tax-rollforward-20261016/verify_company.py',
        interpreter=sys.executable,environment='tfgpu Python; Fraction and existing jsonschema; no ML imports',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        data_version='input-lock.json; unchanged P5 base and new authored expectations',random_seeds='N/A deterministic',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-compound-tax-rollforward-20261016.md',result='data/accounting-master/compound-tax-rollforward-20261016/result.md',
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ('checks.json','conversion-result.json','redemption-result.json','adverse-cases.json','summary.json')])
    write('summary.json',summary)
    print(json.dumps({k:summary[k] for k in ('attempt','checks','failures','failed','adverse_inputs','wall_seconds')}))
    if summary['failures']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
