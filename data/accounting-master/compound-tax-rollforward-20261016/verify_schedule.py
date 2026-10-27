"""Compare separate authored amounts, component origins and refusal cases."""
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

from reference_tax import calculate, FINDINGS

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def request(values):
    r = dict(zip(['proceeds','liability','coupon','period_rate','tax_rate'],values))
    p,c = Q(r['proceeds']),Q(r['coupon'])
    r['fiscal'] = dict(initial_base=str(p),accrued_base=str(p+c),after_coupon_base=str(p),
                      deduction=str(c),settlement_taxable_income='0', **{k:True for k in FINDINGS})
    return r


def main():
    started = time.monotonic()
    attempt = OUT / 'schedule-attempt-01'
    attempt.mkdir(exist_ok=False)
    checks,exchanges = [],[]
    def check(name,ok):
        checks.append(dict(name=name,passed=bool(ok)))
    for item in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('input/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'])
    assert all(c['passed'] for c in checks), 'Protected input changed'
    cases = json.loads((OUT/'authored-schedules.json').read_text())
    for case in cases['cases']:
        req = request(case['values'])
        before = deepcopy(req)
        result = calculate(req)
        exchanges.append(dict(id=case['id'],request=req,result=result))
        check(case['id']+'/status',result['status'] == 'conditional_complete')
        for key,value in zip(cases['expected_fields'],case['expected']):
            check(case['id']+'/'+key,result['amounts'][key] == value)
        for journal in result['journals']:
            check(case['id']+'/'+journal['id']+'/balance',sum(Q(v) for v in journal['entries'].values()) == 0)
        check(case['id']+'/equity-origin','deferred_tax' not in result['journals'][1]['entries'] and 'current_tax' not in result['journals'][1]['entries'])
        check(case['id']+'/income-reversal',set(result['journals'][3]['entries']) == {'compound_dtl','deferred_tax'})
        check(case['id']+'/settlement-cleared',all(result['stages'][-1][k] == '0' for k in ('carrying','tax_base','dtl')))
        check(case['id']+'/read-only',req == before and result['mutations'] == [] and calculate(req) == result)
    base = request(cases['cases'][0]['values'])
    adverse = []
    for key in base['fiscal']:
        r = deepcopy(base);r['fiscal'][key] = None
        adverse.append((key+'-missing',r,'unresolved'))
    for key in FINDINGS:
        r = deepcopy(base);r['fiscal'][key] = False
        adverse.append((key+'-false',r,'unresolved' if key == 'complete_consequences' else 'unsupported'))
    for key,value in [('period_rate','1/23'),('tax_rate','-1/4'),('tax_rate','5/4'),('liability','101'),('coupon','-4'),('coupon',4),('coupon','8/2')]:
        r=deepcopy(base);r[key]=value
        adverse.append((key+'-'+str(value),r,'unsupported' if value == '5/4' else 'rejected'))
    for key,value in [('initial_base','92'),('accrued_base','100'),('deduction','12'),('settlement_taxable_income','8')]:
        r=deepcopy(base);r['fiscal'][key]=value
        adverse.append((key+'-different',r,'unsupported'))
    r=deepcopy(base);r['post']=True;adverse.append(('unknown-operation',r,'rejected'))
    for name,req,status in adverse:
        before=deepcopy(req);result=calculate(req)
        exchanges.append(dict(id=name,request=req,result=result))
        check(name+'/status',result['status']==status)
        check(name+'/empty',result['amounts'] is None and not result['journals'] and not result['stages'] and not result['mutations'])
        check(name+'/read-only',req == before)
    good=calculate(base)['amounts']
    check('coupon-only-addback-is-wrong',Q(good['after_tax_cost']) != Q(4)*(1-Q(1,4)))
    check('omitting-deferred-income-is-wrong',Q(good['after_tax_cost']) != Q(good['finance_expense'])+Q(good['current_tax_expense_delta']))
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),checks=len(checks),failures=sum(not c['passed'] for c in checks),
        failed=[c for c in checks if not c['passed']],positive_cases=len(cases['cases']),adverse_cases=len(adverse),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/compound-tax-rollforward-20261016/verify_schedule.py',
        interpreter=sys.executable,environment='tfgpu Python standard library; exact Fraction; no ML imports',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        data_version='input-lock.json and authored-schedules.json',random_seeds='N/A deterministic',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-compound-tax-rollforward-20261016.md',result='data/accounting-master/compound-tax-rollforward-20261016/result.md',
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ('checks.json','exchanges.json','summary.json')])
    for name,value in [('checks.json',checks),('exchanges.json',exchanges),('summary.json',summary)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('checks','failures','failed','positive_cases','adverse_cases','wall_seconds')}))
    if summary['failures']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
