"""Compare new input-driven semantics to prior exact funded-year traces."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
import json
import os
import platform
import subprocess
import sys
import time
from jsonschema import Draft202012Validator, FormatChecker
from verify import ROOT, OUT, SOURCE, sha
from execute import execute


def convert(value):
    if isinstance(value,dict): return {k:convert(v) for k,v in value.items()}
    if isinstance(value,list): return [convert(v) for v in value]
    if isinstance(value,str):
        try: return Q(value)
        except ValueError: return value
    return value


def rational(value): return {'n':str(value.numerator),'d':str(value.denominator)}


def main():
    started=datetime.now(timezone.utc).isoformat(); timer=time.perf_counter()
    source=json.loads(SOURCE.read_text()); source_hash=sha(SOURCE)
    validator=Draft202012Validator(json.loads((OUT/'schema.json').read_text()),format_checker=FormatChecker())
    base=json.loads((OUT/'example.json').read_text())
    prior_path=ROOT/'data/accounting-master/funded-year-20261023/checks.json'
    prior=json.loads(prior_path.read_text()); prior_hash=sha(prior_path)
    checks=[]; results=[]
    def check(name,passed): checks.append({'name':name,'passed':bool(passed)})
    for scenario in ['stress7','stress9']:
        for share in [Q(0),Q(1,2),Q(1)]:
            for rate in [Q(0),Q(1,20),Q(7,100)]:
                body=deepcopy(base); alias='projection.'+scenario
                body['projection']={'alias':alias,'digest':source['aliases'][alias]['digest']}
                body['share']=rational(share); body['loan']['annual_rate']=rational(rate)
                before=deepcopy(body); actual=execute(body,validator,source)
                name=scenario+':share='+str(share)+':facility_rate='+str(rate)
                expected=next(r for r in prior['runs'] if r['name']==name)
                check(name+':success',actual['status']=='complete_conditional')
                check(name+':input_unchanged',body==before)
                check(name+':all_closing_accounts',actual['closing_balances']==convert(expected['closing_balances']))
                check(name+':all_statement_results',actual['statements']==convert(expected['statements']))
                check(name+':every_journal_and_cash_prefix',[(j['event'],j['date'],j['journal'],j['cash_class'],j['cash_after'],j['facility_principal_after']) for j in actual['journals']]==[(j['event'],j['date'],convert(j['journal']),j['cash_class'],Q(j['cash_after']),Q(j['facility_principal_after'])) for j in expected['journals']])
                check(name+':noncommit',actual['committed'] is False and actual['conditional_state'] is True)
                results.append({'name':name,'input':body,'result':actual})
    short=deepcopy(base); payroll=next(e for e in short['events'] if e['kind']=='payroll'); short['events'].remove(payroll); payroll['at']='2025-01-04T13:00:00Z'; short['events'].insert(4,payroll)
    failed=execute(short,validator,source)
    check('known_prefix_shortfall',failed['status']=='funding_failure' and failed['event']=='payroll' and failed['shortfall']==50)
    check('refused_payroll_atomic',failed['balances']['cash']==0 and failed['balances']['payroll']==0 and [j['event'] for j in failed['applied']]==['purchase','delivery','facility_draw','supplier_payment'])
    check('earlier_draw_retained_after_later_failure',failed['facility_drawn']==Q(427,5) and failed['balances']['debt']==-Q(927,5))
    unknown=deepcopy(base); next(e for e in unknown['events'] if e['kind']=='collection')['at']='unknown'; unresolved=execute(unknown,validator,source)
    check('unknown_not_default_or_zero',unresolved['status']=='unresolved' and unresolved['obligations']==['supply_event_instant:collection'] and 'closing_balances' not in unresolved)
    check('sources_unchanged',sha(SOURCE)==source_hash and sha(prior_path)==prior_hash)
    report={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'paths':results,
            'failure_case':failed,'unresolved_case':unresolved,
            'scope':'Input-driven documentary reference semantics, not product runtime or durable transactions'}
    (OUT/'execution-checks.json').write_text(json.dumps(report,indent=2,default=str)+chr(10))
    manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'command':'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/funded-authoring-20261023/verify_execution.py',
              'environment':{'executable':sys.executable,'python':platform.python_version()},'cpu_gpu':'CPU only; GPU intentionally hidden',
              'cuda_visible_devices':os.environ.get('CUDA_VISIBLE_DEVICES'),'random_seeds':'N/A: deterministic exact checks',
              'data_version':{'source':source_hash,'independent_trace':prior_hash},'started_utc':started,'wall_seconds':time.perf_counter()-timer,
              'plan_file':'docs/plans/accounting-funded-year-design-20261023.md','result_file':str((OUT/'result.md').relative_to(ROOT)),
              'artifacts':{p.name:sha(p) for p in [OUT/'execute.py',Path(__file__),OUT/'execution-checks.json',OUT/'example.json',OUT/'schema.json',OUT/'verify.py']}}
    (OUT/'execution-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
    print(json.dumps({'passed':report['passed'],'paths':len(results),'checks':len(checks),'failures':[c for c in checks if not c['passed']]}))
    if not report['passed']: raise SystemExit(1)


if __name__=='__main__': main()
