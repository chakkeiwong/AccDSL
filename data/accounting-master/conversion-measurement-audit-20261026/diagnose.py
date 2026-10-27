"""Exact source-boundary discriminators; no proposed accounting treatment."""
from dataclasses import replace
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import os
import platform
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import corporate_financing_v1 as finance
OUT=HERE/'attempt-01'


def main():
    OUT.mkdir(exist_ok=False);start=time.monotonic();checks=[]
    def check(name,actual,expected):
        checks.append(dict(id=name,actual=str(actual),expected=str(expected),passed=actual==expected))
        if actual!=expected:raise AssertionError(name)
    sources=['scripts/corporate_financing_v1.py','docs/design/research/p08-v1/authority-register.json',
             'docs/design/research/standards/aasb132.txt','docs/design/research/p08-v1/aasb9.txt',
             'docs/plans/accounting-conversion-measurement-audit-20261026.md',str(Path(__file__).resolve().relative_to(ROOT))]
    locks={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}
    (OUT/'source-lock.json').write_text(json.dumps(locks,indent=2)+'\n')
    (OUT/'diagnose.py').write_bytes(Path(__file__).read_bytes())
    check('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1')
    check('bytecode_disabled',os.environ.get('PYTHONDONTWRITEBYTECODE'),'1')
    quote=F(17000,441);plain_pv=F(80)/F(21,20)**2
    check('different_plain_cash_pv',plain_pv,F(32000,441))
    check('negative_residual_from_wrong_comparator',quote-plain_pv,F(-5000,147))
    check('wrong_rate_terminal_accretion',quote*F(21,20)**2,F(85,2))
    check('wrong_rate_misses_face',quote*F(21,20)**2==80,False)
    authority=finance.AuthorityBook()
    def refused(name,operation,expected):
        try:operation()
        except finance.Unsupported as exc:actual=str(exc)
        else:actual='accepted'
        check(name,actual,expected)
    future=finance.Contract(issue_date='2027-01-01',years=2)
    refused('existing_authority_period',lambda:authority.admit(future),'edition outside reporting-period start')
    contingent=replace(future,conversion_right='signal_triggered_before_terminal_payment')
    refused('different_conversion_terms',contingent.validate,'unsupported conversion terms')
    wrong_split=replace(future,principal='80',proceeds=str(quote),instrument_fair_value=str(quote),annual_coupon='0',comparable_yield='1/20')
    refused('negative_residual_refused',wrong_split.validate,'negative residual equity: assumptions need reassessment')
    for path,digest in locks.items():check('preserved:'+path,sha256((ROOT/path).read_bytes()).hexdigest(),digest)
    result=dict(status='PASS',assertions=len(checks),checks=checks,
                interpretation='Reject silent reuse of the current package/rate; no correct classification or measurement of the contingent instrument inferred.')
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    manifest=dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/conversion-measurement-audit-20261026/diagnose.py',
                  git_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip(),python=platform.python_version(),executable=sys.executable,
                  environment='CPU only; GPU intentionally hidden; standard-library exact fractions',random_seed='N/A deterministic',data_version='source-lock.json',
                  wall_seconds=time.monotonic()-start,plan='docs/plans/accounting-conversion-measurement-audit-20261026.md',
                  result='data/accounting-master/conversion-measurement-audit-20261026/result.md',artifacts=['result.json','source-lock.json','diagnose.py'])
    (OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(status='PASS',assertions=len(checks),wall_seconds=manifest['wall_seconds'])))


if __name__=='__main__':main()
