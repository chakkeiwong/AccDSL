"""Exact baseline, multiplicity and refusal conformance; read-only default."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
from operations import execute, schema, lower_annual, wire, digest
from semantics import execute as annual_execute


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


operation_reporting=load_module('operation_reporting',HERE/'reporting.py')
annual_reporting=load_module('annual_reporting',HERE.parent/'company-inputs-20261023'/'reporting.py')
from fixtures import split_operations


def conformance():
    annual=json.loads((HERE.parent/'company-inputs-20261023'/'example.json').read_text())
    source=(ROOT/annual['source']['path']).read_bytes()
    body=json.loads((HERE/'example.json').read_text())
    checks,witnesses,paths=[],{},[]
    def check(name,passed):checks.append({'name':name,'passed':bool(passed)})
    def case(name,value):
        before=deepcopy(value);run=execute(value,source)
        report=operation_reporting.build_report(value,run,source)
        check(name+':pure',before==value)
        witnesses[name]={'input':value,'run':run,'report':report}
        return run,report
    check('published_schema',schema()==json.loads((HERE/'schema.json').read_text()))
    check('authored_lowering_matches_example',lower_annual(annual,Q(4))==body)
    for stress in ['7/100','9/100']:
        for share in ['0/1','1/2','1/1']:
            for rate in ['0/1','1/20','7/100']:
                old_body=deepcopy(annual);old_body['debt'].update(floating_rate=stress,floating_share=share);old_body['loan']['annual_rate']=rate
                inp=lower_annual(old_body,Q(4));old=annual_execute(old_body,source);run=execute(inp,source)
                report=operation_reporting.build_report(inp,run,source);old_report=annual_reporting.build_report(old_body,old,source)
                name=stress+':'+share+':'+rate
                check(name+':complete',run['status']=='complete_conditional')
                keys=['closing_balances','claims','assets','inventory_units','facility_drawn','income','minimum_cash','indirect_cfo','statements']
                check(name+':all_state_income_statement_fields',all(run[k]==old[k] for k in keys))
                journal_keys=['at','date','journal','cash_class','cash_after','facility_principal_after']
                check(name+':all_journals_and_cash_prefixes',[{k:j[k] for k in journal_keys} for j in run['journals']]==[{k:j[k] for k in journal_keys} for j in old['journals']])
                check(name+':all_29_lines_and_gross_flows',report['lines']==old_report['lines'] and report['gross_cash']==old_report['gross_cash'])
                paths.append({'name':name,'input':inp,'run':run,'report':report})
    baseline,base_report=case('baseline',body)
    for share in [Q(0),Q(1,3),Q(1,2),Q(1)]:
        inp=split_operations(body,share);run,report=case('split_'+str(share),inp)
        check('split_'+str(share)+':complete',run['status']=='complete_conditional' and len(run['journals'])==21)
        check('split_'+str(share)+':all_accounts_income_statements',all(run[k]==baseline[k] for k in ['closing_balances','income','inventory_units','statements','indirect_cfo','minimum_cash']))
        check('split_'+str(share)+':all_report_lines',report['lines']==base_report['lines'] and report['gross_cash']==base_report['gross_cash'])
        for ledger in ['receivable','payable']:
            check('split_'+str(share)+':'+ledger+'_control',all(sum(c[k] for c in run['claims'].values() if c['ledger']==ledger)==sum(c[k] for c in baseline['claims'].values() if c['ledger']==ledger) for k in ['recognised','settled','outstanding']))
        for field in ['cost','accumulated']:
            check('split_'+str(share)+':asset_'+field,sum(Q(a[field]) for a in run['assets'])==sum(Q(a[field]) for a in baseline['assets']))
        check('split_'+str(share)+':gross_aggregate_journals',all({a:sum(j['journal'].get(a,Q(0)) for j in run['journals'] if j['kind']==kind) for a in baseline['closing_balances']}=={a:sum(j['journal'].get(a,Q(0)) for j in baseline['journals'] if j['kind']==kind) for a in baseline['closing_balances']} for kind in {j['kind'] for j in run['journals']}))
    from adverse import inspect
    inspect(body,source,baseline,base_report,check,case,witnesses,operation_reporting)
    check('wire_roundtrip',wire(witnesses)==json.loads(json.dumps(wire(witnesses))))
    protected=json.loads((HERE/'baseline.json').read_text())
    check('protected_sources_and_baselines_unchanged',all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in protected.items()))
    return {'checks':checks,'passed':all(x['passed'] for x in checks),'paths':paths,'witnesses':witnesses}


def main():
    p=argparse.ArgumentParser();p.add_argument('--record',action='store_true');args=p.parse_args()
    started=datetime.now(timezone.utc).isoformat();clock=time.perf_counter();evidence=wire(conformance())
    target=HERE/'checks.json'
    if args.record:
        if target.exists():raise RuntimeError('Refusing to overwrite evidence')
        target.write_text(json.dumps(evidence,indent=2)+'\n')
        manifest={'started_utc':started,'wall_seconds':time.perf_counter()-clock,
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-operations-20261023/verify.py --record',
            'environment':'system Python '+platform.python_version()+'; jsonschema; exact Fraction arithmetic',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),
            'data_version':json.loads((HERE/'example.json').read_text())['source'],'random_seeds':'N/A: deterministic',
            'plan':'docs/plans/accounting-company-operations-20261023.md',
            'result':'data/accounting-master/company-operations-20261023/result.md',
            'files':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in HERE.iterdir() if f.is_file()}}
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif target.exists() and evidence!=json.loads(target.read_text()):raise AssertionError('Evidence replay mismatch')
    failures=[x['name'] for x in evidence['checks'] if not x['passed']]
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failures,'failed':failures,'recorded':args.record}))
    return bool(failures)


if __name__=='__main__':raise SystemExit(main())
