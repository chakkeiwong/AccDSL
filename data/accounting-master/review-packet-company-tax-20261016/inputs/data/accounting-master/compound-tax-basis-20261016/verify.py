"""Exact documentary issue-date tax method; no subsequent schedule inferred."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
FIELDS={'gross_proceeds','liability','equity','tax_base','rate'}


def calculate(request):
    result=dict(status='rejected',reason=None,amounts=None,journals=[],mutations=[],scope='issue_date_only')
    def refuse(status,reason):
        result.update(status=status,reason=reason)
        return result
    if not isinstance(request,dict) or set(request)!=FIELDS:
        return refuse('rejected','request_shape')
    missing={'tax_base':'tax_base_missing','rate':'tax_rate_missing','equity':'equity_component_missing',
             'gross_proceeds':'proceeds_missing','liability':'liability_component_missing'}
    for key,value in request.items():
        if value is None:return refuse('unresolved',missing[key])
    values={}
    for key,value in request.items():
        if not isinstance(value,str) or re.fullmatch(r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?',value) is None:
            return refuse('rejected','malformed_rational')
        number=Q(value)
        if str(number)!=value:return refuse('rejected','malformed_rational')
        values[key]=number
    p,l,e,tax_base,rate=(values[k] for k in ('gross_proceeds','liability','equity','tax_base','rate'))
    if min(p,l,e)<0:return refuse('rejected','invalid_component')
    if tax_base<0:return refuse('rejected','invalid_tax_base')
    if rate<0:return refuse('rejected','invalid_tax_rate')
    if rate>1:return refuse('unsupported','tax_rate_outside_profile')
    if l+e!=p:return refuse('rejected','component_total_mismatch')
    if tax_base not in (l,p):return refuse('unsupported','tax_base_outside_subset')
    dtl=(tax_base-l)*rate
    result.update(status='conditional_complete',amounts={k:str(v) for k,v in dict(dtl=dtl,
        equity_after_tax=e-dtl,current_tax=Q(0),tax_expense=Q(0),assets=p,liabilities=l+dtl,equity_total=e-dtl).items()},
        journals=[{k:str(v) for k,v in dict(cash=p,debt=-l,conversion_equity=-e,dtl=Q(0),current_tax=Q(0),tax_expense=Q(0)).items()},
                  {k:str(v) for k,v in dict(cash=Q(0),debt=Q(0),conversion_equity=dtl,dtl=-dtl,current_tax=Q(0),tax_expense=Q(0)).items()}])
    return result


def main():
    started=time.monotonic();utc=datetime.now(timezone.utc).isoformat()
    indices=[int(p.name.split('-')[1]) for p in OUT.glob('attempt-[0-9][0-9]') if p.is_dir()]
    attempt=OUT/('attempt-%02d'%(max(indices,default=0)+1));attempt.mkdir()
    facts=json.loads((OUT/'premises.json').read_text());checks=[];results=[]
    def check(name,value):checks.append(dict(name=name,passed=bool(value)))
    for item in json.loads((OUT/'authored-lock.json').read_text())['files']:
        check('locked/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    source=facts['source'];check('source-bytes',hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256'])
    if not all(c['passed'] for c in checks):raise SystemExit('Protected input changed')
    for case in facts['bases']:
        request={k:v for k,v in case.items() if k in FIELDS}; before=deepcopy(request);result=calculate(request)
        results.append(dict(id=case['id'],request=request,result=result))
        check(case['id']+'/status',result['status']=='conditional_complete')
        for key,wanted in case['expected'].items():check(case['id']+'/'+key,result['amounts'][key]==wanted)
        for i,journal in enumerate(result['journals']):
            check(case['id']+'/journal-balance/'+str(i),sum(Q(v) for v in journal.values())==0)
        check(case['id']+'/equity-origin',Q(result['journals'][1]['conversion_equity'])==Q(result['amounts']['dtl']) and result['journals'][1]['tax_expense']=='0')
        check(case['id']+'/balance-sheet',Q(result['amounts']['assets'])==Q(result['amounts']['liabilities'])+Q(result['amounts']['equity_total']))
        check(case['id']+'/read-only-deterministic',request==before and result==calculate(request) and result['mutations']==[])
    for case in facts['adverse']:
        request={k:v for k,v in facts['bases'][0].items() if k in FIELDS};request.update(case['changes']);result=calculate(request)
        results.append(dict(id=case['id'],request=request,result=result))
        check(case['id']+'/status',result['status']==case['expected_status'])
        check(case['id']+'/reason',result['reason']==case['expected_code'])
        check(case['id']+'/no-calculation',result['amounts'] is None and result['journals']==[] and result['mutations']==[])
    check('unknown-field',calculate(dict(gross_proceeds='100',liability='92',equity='8',tax_base='100',rate='1/4',post=True))['reason']=='request_shape')
    failures=[c for c in checks if not c['passed']]
    summary=dict(started_utc=utc,attempt=attempt.name,checks=len(checks),failures=len(failures),failed=failures,
        valid_cases=len(facts['bases']),adverse_cases=len(facts['adverse'])+1,wall_seconds=round(time.monotonic()-started,3),
        python=sys.version.split()[0],interpreter=sys.executable,cpu_only=os.environ.get('CUDA_VISIBLE_DEVICES')=='-1',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scope='conditional issue-date tax only')
    for name,value in [('checks.json',checks),('exchanges.json',results),('summary.json',summary)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(summary))
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
