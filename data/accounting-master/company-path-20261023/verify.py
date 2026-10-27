"""Deterministic conformance; default replay writes nothing."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import subprocess
import time

from path_semantics import (execute, execute_year, build_report, digest, wire,
                            schema, verify_chain, report_view, revise)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def conformance():
    path = json.loads((HERE/'example.json').read_text())
    source = (ROOT/path['initial_year']['source']['path']).read_bytes()
    before = deepcopy(path)
    checks, witnesses = [], {}

    def check(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})

    def case(name, change):
        value = deepcopy(path)
        change(value)
        original = deepcopy(value)
        result = execute(value, source)
        check(name+':pure', original == value)
        witnesses[name] = {'path': value, 'result': result}
        return value, result

    check('published_schema', schema() == json.loads((HERE/'schema.json').read_text()))
    result = execute(path, source)
    check('two_complete_years', result['status']=='complete_conditional' and len(result['years'])==2)
    check('pure_path_input', path == before)
    check('complete_identity_chain', verify_chain(path, result))
    first, second = result['years']
    old = execute_year(path['initial_year'], source)
    check('year_one_every_journal_and_state_unchanged', first['annual_run']==old)
    check('year_one_all_29_report_lines', first['annual_report']==build_report(path['initial_year'], old, source))
    check('year_two_is_conditional_not_historical', second['origin']['kind']=='conditional_predecessor' and not second['origin']['historical_admission'])
    # Independent arithmetic: no second-year run values feed expectations.
    bridge = Q(427,5)*Q(1,20)*Q(2,365)
    tax1 = (300-150-50-13-6-bridge)/5
    profit1 = 300-150-50-13-6-bridge-tax1
    cash1 = Q(373,5)+280-160-50-20-6-bridge-tax1-8
    equity1 = Q(453,5)+profit1-8
    revenue2, cogs2, depreciation2, coupon2 = Q(352), Q(160), Q(15), Q(6)
    pbt2 = revenue2-cogs2-55-depreciation2-coupon2
    tax2, profit2 = pbt2/5, pbt2*Q(4,5)
    receipts2, payments2 = 55+revenue2*Q(9,10), Q(200)
    cfo2 = receipts2-payments2-55-coupon2-tax2
    cash2, equity2 = cash1+cfo2-20, equity1+profit2-10
    expected = {'cash':cash2,'receivables':Q(176,5),'inventory':Q(50),
        'plant_net':Q(93),'tax_prepaid':Q(0),'assets':cash2+Q(176,5)+50+93,
        'payables':Q(10),'debt':Q(100),'capital':Q(50),'retained':equity2-50,
        'equity':equity2,'revenue':revenue2,'cost_of_sales':cogs2,'payroll':Q(55),
        'depreciation':depreciation2,'interest':coupon2,'profit_before_tax':pbt2,
        'tax':tax2,'profit':profit2,'oci':Q(0),'comprehensive_income':profit2,
        'operating_cash':cfo2,'investing_cash':Q(-10),'financing_cash':Q(-10),
        'cash_change':cfo2-20,'opening_cash':cash1,'opening_equity':equity1,
        'dividends':Q(10),'plant_additions':Q(10)}
    check('independent_year_one_cash_profit_equity', old['statements']['cash']==cash1 and old['statements']['profit']==profit1 and old['statements']['equity']==equity1)
    actual = {k:v['value'] for k,v in second['annual_report']['lines'].items()}
    for key, value in expected.items():
        check('year_two_independent:'+key, actual.get(key)==value)
    check('year_two_report_line_set', set(actual)==set(expected))
    check('carried_units_change_purchase', second['annual_run']['journals'][0]['journal']=={'inventory':Q(170),'payables':Q(-170)} and second['closing_memory']['inventory_units']==10)
    check('asset_cohorts_continue_without_reset', [Q(a['accumulated']) for a in second['closing_memory']['assets']]==[50,5,2,2,0])
    check('collections_do_not_rebook_revenue', next(j['journal'] for j in second['annual_run']['journals'] if j['event']=='collection')=={'cash':receipts2,'receivables':-receipts2})
    check('lifetime_claims_retained', second['closing_memory']['claims']['sales-ar']=={'ledger':'receivable','recognised':Q(300),'settled':Q(300),'outstanding':Q(0)})
    check('all_claim_lifetime_identities', all(c['recognised']-c['settled']==c['outstanding'] for y in result['years'] for c in y['closing_memory']['claims'].values()))
    check('all_report_bridges', all(all(y['annual_report']['reconciliation'].values()) for y in result['years']))
    check('lifetime_cash_bridge', cash2==Q(373,5)+sum(sum(y['annual_run']['statements']['cash_flows'].values()) for y in result['years']))
    check('lifetime_equity_bridge', equity2==Q(453,5)+profit1+profit2-18)
    check('year_two_gross_financing', second['annual_report']['gross_cash']['financing']=={'inflows':Q(0),'outflows':Q(10)})
    from adverse import inspect_adverse
    inspect_adverse(path, source, result, check, case, witnesses, expected)
    baseline = json.loads((HERE/'baseline.json').read_text())
    check('protected_baseline_unchanged', all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in baseline.items()))
    check('diagnostic_wire_roundtrip', wire(witnesses)==json.loads(json.dumps(wire(witnesses))))
    return {'checks':checks,'passed':all(c['passed'] for c in checks),'baseline_path':path,
            'result':result,'independent_second_year_report':expected,'witnesses':witnesses}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--record',action='store_true')
    args=parser.parse_args(); start=datetime.now(timezone.utc).isoformat(); clock=time.perf_counter()
    evidence=wire(conformance()); output=HERE/'checks.json'
    if args.record:
        if output.exists(): raise RuntimeError('Refusing to overwrite existing evidence')
        output.write_text(json.dumps(evidence,indent=2)+'\n')
        manifest={'started_utc':start,'wall_seconds':time.perf_counter()-clock,
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-path-20261023/verify.py --record',
            'python':platform.python_version(),'environment':'system Python; jsonschema; exact Fraction arithmetic',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),
            'random_seeds':'N/A: deterministic','data_version':evidence['baseline_path']['initial_year']['source'],
            'plan':'docs/plans/accounting-company-path-20261023.md',
            'result':'data/accounting-master/company-path-20261023/result.md',
            'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}}
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif output.exists():
        if evidence!=json.loads(output.read_text()):
            raise AssertionError('Recorded evidence does not reproduce')
    failed=[c['name'] for c in evidence['checks'] if not c['passed']]
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failed,'failed':failed,'recorded':args.record}))
    return bool(failed)


if __name__=='__main__':
    raise SystemExit(main())
