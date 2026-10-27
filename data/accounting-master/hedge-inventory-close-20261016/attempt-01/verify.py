"""Independent signed-basis targets, gross cash origins and wrong-release checks."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from reference import ROOT,OUT,calculate


def main():
    started=time.monotonic();indices=[int(p.name.split('-')[1]) for p in OUT.glob('attempt-[0-9][0-9]') if p.is_dir()]
    attempt=OUT/('attempt-%02d'%(max(indices,default=0)+1));attempt.mkdir()
    for name in ('reference.py','verify.py','authored-cases.json','input-lock.json'):shutil.copy2(OUT/name,attempt/name)
    authored=json.loads((OUT/'authored-cases.json').read_text());checks=[];exchanges=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for item in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('input/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    assert all(c['passed'] for c in checks),'Protected input changed'
    for case in authored['cases']:
        req=deepcopy(case['request']);before=deepcopy(req);result=calculate(req)
        exchanges.append(dict(id=case['id'],request=req,result=result))
        check(case['id']+'/status',result['status']=='conditional_complete',result['reason'])
        check(case['id']+'/read-only-deterministic',req==before and result['mutations']==[] and calculate(req)==result)
        for key,wanted in case['expected'].items():
            check(case['id']+'/'+key,result['report'][key]==wanted,dict(actual=result['report'][key],expected=wanted))
        for journal in result['journals']:
            check(case['id']+'/journal/'+journal['operation'],journal['entries']==case['journal_targets'][journal['operation']])
            check(case['id']+'/balance/'+journal['operation'],sum(Q(v) for v in journal['entries'].values())==0)
        for stage in result['stages']:
            check(case['id']+'/books/'+stage['operation'],sum(Q(v) for v in stage['books'].values())==0)
        check(case['id']+'/cash-origins',[f['origin'] for f in result['flows']]==['supplier','hedge_settlement','inventory_sale'])
        # Wrong reserve-to-income journal can preserve terminal total profit but not interim quantities.
        C=Q(case['expected']['supplier_cost']);R=Q(case['expected']['original_reserve']);I=Q(case['expected']['original_ineffectiveness'])
        wrong_inventory=C;wrong_profit=I+R
        check(case['id']+'/wrong-release-inventory-detected',wrong_inventory!=Q(case['expected']['inventory_after_basis']))
        check(case['id']+'/wrong-release-interim-profit-detected',wrong_profit!=Q(case['expected']['profit_before_sale']))
        check(case['id']+'/final-profit-alone-insufficient',Q(14500)-C+wrong_profit==Q(case['expected']['cumulative_pretax_profit']))
    cases=[];base=authored['cases'][0]['request']
    def adverse(name,status,reason,fn):
        req=deepcopy(base);fn(req);cases.append(dict(id=name,request=req,status=status,reason=reason))
    for key in base['findings']:
        adverse('missing-'+key,'unresolved','missing_'+key,lambda r,k=key:r['findings'].update({k:None}))
        adverse('false-'+key,'unsupported','finding_'+key,lambda r,k=key:r['findings'].update({k:False}))
    adverse('wrong-population','rejected','purchase_sale_population',lambda r:r['purchase'].update(quantity='100'))
    adverse('wrong-sale-population','rejected','purchase_sale_population',lambda r:r['sale'].update(quantity='129'))
    adverse('wrong-price','rejected','purchase_price',lambda r:r['purchase'].update(unit_price='95'))
    adverse('wrong-cost','rejected','supplier_cost',lambda r:r['purchase'].update(supplier_cash='12000'))
    adverse('wrong-settlement','rejected','settlement_carrying_value',lambda r:r['settlement'].update(cash='1810'))
    adverse('late-purchase','rejected','terminal_date_mismatch',lambda r:r['purchase'].update(date='2024-10-01'))
    adverse('wrong-context','rejected','context_mismatch',lambda r:r['context'].update(book='another-book'))
    adverse('wrong-sequence','rejected','sale_chronology',lambda r:r['sale'].update(date='2024-09-29'))
    adverse('funding-shortfall','unsupported','funding_required',lambda r:r.update(opening_cash='100'))
    adverse('bad-rational','rejected','rational_encoding',lambda r:r.update(opening_cash='40000/2'))
    adverse('post','rejected','operation',lambda r:r.update(operation='post'))
    adverse('double-basis-request','rejected','request_shape',lambda r:r.update(basis_already_applied=True))
    adverse('forged-terminal-reserve','rejected','request_shape',lambda r:r.update(terminal_reserve='2000'))
    adverse('wrong-origin-in-source-path','rejected','hedge_new_layer_origin',lambda r:r['hedge']['events'][1]['layer'].update(price='80'))
    for case in cases:
        before=deepcopy(case['request']);actual=calculate(case['request']);case['actual']=dict(status=actual['status'],reason=actual['reason'])
        check(case['id']+'/refusal',(actual['status'],actual['reason'])==(case['status'],case['reason']),case['actual'])
        check(case['id']+'/atomic',actual['report'] is actual['hedge'] is None and actual['stages']==actual['journals']==actual['flows']==actual['mutations']==[] and case['request']==before)
    def absent(p):raise FileNotFoundError(p)
    for name,reader,status in [('absent',absent,'unresolved'),('changed',lambda p:b'changed','rejected')]:
        actual=calculate(base,reader);check('resolver/'+name,actual['status']==status and actual['report'] is None)
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],
        terminal_cases=2,adverse_inputs=len(cases),resolver_challenges=2,
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/hedge-inventory-close-20261016/verify.py',
        interpreter=sys.executable,environment='tfgpu Python standard library/Fraction; no ML imports',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),data_version='input-lock.json and independent signed basis cases',
        random_seeds='N/A deterministic',wall_seconds=round(time.monotonic()-started,3),plan='docs/plans/accounting-hedge-inventory-close-20261016.md',
        result='data/accounting-master/hedge-inventory-close-20261016/result.md',
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ('summary.json','checks.json','exchanges.json','adverse.json')])
    for name,value in [('summary.json',summary),('checks.json',checks),('exchanges.json',exchanges),('adverse.json',cases)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('attempt','checks','failures','failed','adverse_inputs','wall_seconds')}))
    if summary['failures']:raise SystemExit(1)


if __name__=='__main__':main()
