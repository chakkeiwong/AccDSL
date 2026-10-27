"""Small independent arithmetic/shape diagnostic, preserving every attempt."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import re
import sys
import time
from jsonschema import Draft202012Validator,FormatChecker
from authored_cases import CASES
from financial_checks import evaluate,num,Refusal
from schema_design import schemas,METHODS
HERE=Path(__file__).resolve().parent
def wire(v):
 if isinstance(v,str) and re.fullmatch(r'-?[0-9]+(?:/[0-9]+)?',v):
  x=Fraction(v);return dict(n=str(x.numerator),d=str(x.denominator))
 if isinstance(v,dict):return {k:wire(x) for k,x in v.items()}
 if isinstance(v,list):return [wire(x) for x in v]
 return v
def main():
 started=time.monotonic();outcomes=[];prior={};s=schemas()['$defs'];checks=[]
 def check(name,ok,detail=''):checks.append(dict(check=name,passed=bool(ok),detail=detail))
 for c in CASES:
  expected=wire(c['expected']);facts=wire(c['input'])
  try:
   got=evaluate(facts,prior.get(c['prior']));prior[c['id']]=got
   check(c['id']+'.full-independent-finance',got==expected,'' if got==expected else json.dumps(dict(actual=got,expected=expected)))
   check(c['id']+'.input-shape',not list(Draft202012Validator(s['MethodInput'],format_checker=FormatChecker()).iter_errors(facts)))
   check(c['id']+'.result-shape',not list(Draft202012Validator(s['ComponentResult'],format_checker=FormatChecker()).iter_errors(dict(got,method_id=facts['method_id'],basis_ref=dict(kind='MethodBasis',schema='accdsl.group-components.methodbasis.v1',digest='0'*64)))))
   check(c['id']+'.journal-balanced',sum((num(x) for x in got['adjustment_journal'].values()),Fraction(0))==0)
   check(c['id']+'.authored-journal-balanced',sum((num(x) for x in expected['adjustment_journal'].values()),Fraction(0))==0)
   check(c['id']+'.unknown-nonposting',got['status']!='unresolved' or (not got['adjustment_journal'] and got['posting_effect']=='none'))
  except Exception as e:check(c['id']+'.exception',False,str(e))
 check('all-methods-represented',{c['input']['method_id'] for c in CASES}==set(METHODS))
 bad=wire(dict(next(c['input'] for c in CASES if c['id']=='outside-taxable'),difference='59'))
 try:evaluate(bad);check('tax-difference-adverse',False)
 except Refusal as e:check('tax-difference-adverse',e.code=='outside_basis_difference_mismatch')
 n=1
 while (HERE/f'diagnostic-{n:02}.json').exists():n+=1
 target=HERE/f'diagnostic-{n:02}.json'
 report=dict(status='passed' if all(c['passed'] for c in checks) else 'failed',case_count=len(CASES),checks=checks,wall_seconds=time.monotonic()-started,command='python3 '+str(Path(__file__).relative_to(HERE.parents[3])),interpreter=sys.executable,input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/'authored_cases.py',HERE/'financial_checks.py',HERE/'schema_design.py',Path(__file__))})
 target.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(artifact=str(target.relative_to(HERE.parents[3])),status=report['status'],cases=len(CASES),checks=len(checks),failures=[c['check'] for c in checks if not c['passed']])))
 return 0 if report['status']=='passed' else 1
if __name__=='__main__':sys.exit(main())
