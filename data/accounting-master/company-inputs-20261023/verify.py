"""Independent stored-trace and economic-mutation checks; no old writers run."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from authoring import lower, schema
from semantics import execute
from reporting import build_report, LINES

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def convert(value):
    if isinstance(value, dict):
        return {k: convert(v) for k, v in value.items()}
    if isinstance(value, list):
        return [convert(v) for v in value]
    if isinstance(value, str):
        try:
            return Q(value)
        except ValueError:
            pass
    return value

def main():
    started, clock = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    base = json.loads((HERE / 'example.json').read_text())
    source_path = ROOT / base['source']['path']
    source = source_path.read_bytes()
    source_records = json.loads(source)
    prior_path = ROOT / 'data/accounting-master/funded-year-20261023/checks.json'
    prior = json.loads(prior_path.read_text())
    protected = {str(p.relative_to(ROOT)): sha(p) for p in [source_path, prior_path,
        ROOT / 'data/accounting-master/funded-authoring-20261023/execute.py',
        ROOT / 'data/accounting-master/funded-authoring-20261023/example.json']}
    checks, witnesses, paths, reports = [], {}, [], []
    def check(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})
    def run_case(name, change):
        body = deepcopy(base)
        change(body)
        before = deepcopy(body)
        got = execute(body, source)
        check(name + ':pure_input', body == before)
        witnesses[name] = {'body': body, 'result': got}
        return got
    check('schema_matches_published', schema() == json.loads((HERE / 'schema.json').read_text()))
    check('matched_text_typed_body', lower((HERE / 'example.accdsl').read_text()) == base)
    for stress, floating in [('stress7', '7/100'), ('stress9', '9/100')]:
        for share in ['0/1', '1/2', '1/1']:
            for rate in ['0/1', '1/20', '7/100']:
                body = deepcopy(base)
                body['debt']['floating_rate'] = floating
                body['debt']['floating_share'] = share
                body['loan']['annual_rate'] = rate
                before = deepcopy(body)
                actual = execute(body, source)
                name = stress + ':share=' + str(Q(share)) + ':facility_rate=' + str(Q(rate))
                expected = next(x for x in prior['runs'] if x['name'] == name)
                check(name + ':complete', actual['status'] == 'complete_conditional')
                if actual['status'] != 'complete_conditional':
                    raise AssertionError((name, actual))
                check(name + ':opening_to_all_closing_accounts', actual['closing_balances'] == convert(expected['closing_balances']))
                check(name + ':all_statements', actual['statements'] == convert(expected['statements']))
                keys = ['event', 'date', 'journal', 'cash_class', 'cash_after', 'facility_principal_after']
                check(name + ':every_journal_and_cash_prefix',
                      [{k: j[k] for k in keys} for j in actual['journals']] ==
                      [{k: convert(j[k]) for k in keys} for j in expected['journals']])
                check(name + ':claims_inventory_assets', actual['inventory_units'] == 8 and sum(Q(a['accumulated']) for a in actual['assets']) == 44 and actual['claims']['sales-ar']['outstanding'] == 30 and actual['claims']['purchase-ap']['outstanding'] == 10)
                check(name + ':lineage_noncommit_purity', all(j['method'] and j['input_paths'] for j in actual['journals']) and not actual['committed'] and body == before)
                check(name + ':indirect_cfo', actual['indirect_cfo'] == actual['statements']['cash_flows']['operating'])
                report = build_report(body, actual, source)
                check(name + ':report_complete_and_bound', report['status']=='complete_conditional' and report['annual_complete'] and report['input_sha256']==actual['input_sha256'])
                projection_ref = source_records['aliases']['projection.' + stress]['digest']
                projected = source_records['record_registry'][projection_ref]['body']['lines']
                expected_lines = {k: Q(v['constant']['n'])/Q(v['constant']['d']) + Q(share)*Q(v['coefficient_x']['n'])/Q(v['coefficient_x']['d']) for k,v in projected.items()}
                bridge = Q(427,5)*Q(rate)*Q(2,365)
                after_tax = bridge*Q(4,5)
                for k in ['cash','assets','retained','equity','profit','comprehensive_income','operating_cash','cash_change']:
                    expected_lines[k] -= after_tax
                expected_lines['interest'] += bridge
                expected_lines['profit_before_tax'] -= bridge
                expected_lines['tax'] -= bridge*Q(1,5)
                check(name + ':all_29_report_lines', {k:v['value'] for k,v in report['lines'].items()}==expected_lines and set(report['lines'])==set(LINES))
                check(name + ':gross_financing_preserved', report['gross_cash']['financing']=={'inflows':Q(427,5),'outflows':Q(427,5)+8})
                reports.append({'name':name,'report':report})
                paths.append({'name': name, 'input': body, 'result': actual})
    baseline = execute(base, source)
    price = run_case('price_changes_claims_tax_cash', lambda b: b['inventory'].update(price='11/1'))
    check('price_economic_consequences', price['income']['revenue']-baseline['income']['revenue'] == 30 and price['statements']['profit']-baseline['statements']['profit'] == 24 and price['statements']['cash']-baseline['statements']['cash'] == 21 and price['claims']['sales-ar']['outstanding'] == 33)
    demand = run_case('demand_changes_purchase_cost_sales', lambda b: b['inventory'].update(demand_units='31/1'))
    check('demand_economic_consequences', demand['journals'][0]['journal']['inventory'] == 175 and demand['income']['cost_of_sales'] == 155 and demand['inventory_units'] == 8 and demand['statements']['profit']-baseline['statements']['profit'] == 4 and demand['statements']['cash']-baseline['statements']['cash'] == 8)
    delayed = run_case('delay_unserved_opening_asset', lambda b: b['assets'][2].update(in_service='2026-01-01'))
    check('service_date_changes_depreciation', delayed['income']['depreciation'] == 12 and delayed['statements']['profit']-baseline['statements']['profit'] == Q(4,5) and delayed['statements']['cash']-baseline['statements']['cash'] == -Q(1,5))
    mid = run_case('midyear_service', lambda b: b['assets'][2].update(in_service='2025-07-01'))
    check('unsupported_midyear_not_full_year', mid['status']=='unsupported' and mid['reason']=='midyear_service_fraction')
    def early_payroll(b):
        e=next(e for e in b['events'] if e['kind']=='payroll');b['events'].remove(e);e['at']='2025-01-04T13:00:00Z';b['events'].insert(4,e)
    fail = run_case('payroll_shortfall', early_payroll)
    check('failure_preserves_prior_draw_payment', fail['status']=='funding_failure' and fail['shortfall']==50 and fail['balances']['payroll']==0 and fail['facility_drawn']==Q(427,5) and [j['event'] for j in fail['applied']]==['purchase','delivery','facility_draw','supplier_payment'])
    unknown = run_case('unknown_control_transfer', lambda b: b['inventory'].update(control_transferred='unknown'))
    check('unknown_preserved', unknown['status']=='unresolved' and unknown['obligations']==['supply:/inventory/control_transferred'] and 'closing_balances' not in unknown)
    false = run_case('control_transfer_false', lambda b: b['inventory'].update(control_transferred=False))
    check('no_sales_without_control_transfer', false['status']=='unsupported' and false['balances']['revenue']==0 and len(false['applied'])==1)
    bad_cases = [
        ('missing_field', lambda b: b['inventory'].pop('price'), 'invalid', 'schema'),
        ('noncanonical_amount', lambda b: b['inventory'].update(price='20/2'), 'invalid', 'rational'),
        ('unsupported_costing', lambda b: b['inventory'].update(method='fifo'), 'unsupported', 'method'),
        ('asset_control', lambda b: b['assets'][0].update(accumulated='29/1'), 'invalid', 'asset_control'),
        ('wrong_context', lambda b: b['context'].update(currency='EUR'), 'invalid', 'context_mismatch'),
        ('wrong_source', lambda b: b['source'].update(sha256='0'*64), 'invalid', 'source_digest'),
        ('over_settlement', lambda b: b['trade'].update(supplier_payment='171/1'), 'invalid', 'purchase_over_settlement'),
        ('duplicate_claim', lambda b: b['trade'].update(sales_claim_id='opening-ar'), 'invalid', 'duplicate_claim'),
        ('fee', lambda b: b['loan'].update(fee='1/1'), 'unsupported', 'loan_fee'),
        ('known_ineligible', lambda b: b['facility'].update(eligible=False), 'funding_failure', 'known_ineligible_facility'),
        ('insufficient_headroom', lambda b: b['facility'].update(limit='80/1'), 'funding_failure', 'facility_headroom'),
        ('loss_tax', lambda b: b['inventory'].update(price='7/1'), 'unsupported', 'loss_tax_method')]
    for name, change, status, reason in bad_cases:
        got=run_case(name,change);check(name+':expected_result',got['status']==status and got['reason']==reason)
    invalid_texts = [(HERE/'example.accdsl').read_text()+'name Duplicate;\n', (HERE/'example.accdsl').read_text()+'unknown_decl x;\n']
    for i,text in enumerate(invalid_texts):
        try:
            lower(text);rejected=False
        except ValueError:
            rejected=True
        check('invalid_text_'+str(i),rejected)
    trimmed=json.loads(source)
    trimmed['record_registry']={k:v for k,v in trimmed['record_registry'].items() if v['kind'] in ['CompanyState','Context']}
    trimmed['aliases']={}
    for v in trimmed['record_registry'].values():
        v['body'].pop('proposed_journals',None)
    minimal=json.dumps(trimmed,sort_keys=True).encode();b=deepcopy(base);b['source']['sha256']=hashlib.sha256(minimal).hexdigest()
    no_projection=execute(b,minimal)
    check('projection_records_removed_same_computation', no_projection['status']=='complete_conditional' and no_projection['closing_balances']==baseline['closing_balances'] and no_projection['journals']==baseline['journals'])
    corrupted = json.loads(source)
    corrupted['record_registry'][base['opening_digest']]['body']['sequence'] += 1
    raw = json.dumps(corrupted).encode(); b = deepcopy(base); b['source']['sha256'] = hashlib.sha256(raw).hexdigest()
    rejected = execute(b, raw)
    check('outer_hash_cannot_hide_corrupted_opening', rejected['status']=='invalid' and rejected['reason']=='opening_record_digest')
    missing_date=run_case('unknown_collection_instant', lambda b: next(e for e in b['events'] if e['kind']=='collection').update(at='unknown'))
    check('unknown_date_no_default',missing_date['status']=='unresolved' and 'closing_balances' not in missing_date)
    unknown_eligible=run_case('unknown_facility_eligibility',lambda b: b['facility'].update(eligible='unknown'))
    check('unknown_eligibility_not_economic_failure',unknown_eligible['status']=='unresolved')
    future_service=run_case('service_before_acquisition',lambda b:b['cash'].update(capex_service='2025-01-01'))
    check('service_before_acquisition_reject',future_service['status']=='invalid' and future_service['reason']=='service_before_acquisition')
    split_interest=run_case('bridge_interest_wrong_date',lambda b:next(e for e in b['events'] if e['kind']=='facility_interest').update(at='2025-01-05T10:00:00Z'))
    check('bridge_accrual_payment_boundary',split_interest['status']=='unsupported' and split_interest['reason']=='bridge_interest_settles_on_repayment_date')
    failure_report=build_report(witnesses['payroll_shortfall']['body'],fail,source)
    check('failed_path_prefix_is_not_annual', failure_report['status']=='partial' and not failure_report['annual_complete'] and failure_report['prefix_snapshot']['last_event']=='supplier_payment' and failure_report['prefix_snapshot']['balances']['cash']==0 and failure_report['lines']['cash']['status']=='unresolved' and failure_report['lines']['profit']['status']=='unresolved' and failure_report['lines']['opening_cash']['value']==Q(373,5))
    unknown_report=build_report(witnesses['unknown_collection_instant']['body'],missing_date,source)
    check('unknown_report_no_invented_prefix',unknown_report['status']=='partial' and 'prefix_snapshot' not in unknown_report and len(unknown_report['remaining_events'])==14 and all(v['status']=='unresolved' for k,v in unknown_report['lines'].items() if not k.startswith('opening_')))
    mismatch=deepcopy(base);mismatch['inventory']['price']='11/1'
    check('report_rejects_mixed_scenario',build_report(mismatch,baseline,source)=={'status':'invalid','reason':'report_run_binding'})
    for item in paths:
        check(item['name']+':source_and_input_binding',item['result']['source_sha256']==base['source']['sha256'] and bool(item['result']['input_sha256']))
    check('protected_inputs_unchanged', all(sha(ROOT/p)==digest for p,digest in protected.items()))
    report={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'paths':paths,'witnesses':witnesses,'reports':reports,'partial_reports':{'funding_failure':failure_report,'unknown_date':unknown_report},'scope':'Documentary operating-input closure for the synthetic company year; no product or whole-phase acceptance.'}
    (HERE/'checks.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
    manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'command':'env CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/company-inputs-20261023/verify.py',
              'environment':{'executable':sys.executable,'python':platform.python_version()},'cpu_gpu':'CPU only; GPU intentionally hidden',
              'cuda_visible_devices':os.environ.get('CUDA_VISIBLE_DEVICES'),'random_seeds':'N/A: deterministic exact arithmetic',
              'started_utc':started,'wall_seconds':time.perf_counter()-clock,'data_version':protected,
              'plan_file':'docs/plans/accounting-company-input-closure-20261023.md','result_file':'data/accounting-master/company-inputs-20261023/result.md',
              'artifacts':{p.name:sha(p) for p in HERE.iterdir() if p.is_file() and p.name!='manifest.json'}}
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'checks':len(checks),'paths':len(paths),'failures':[c for c in checks if not c['passed']]}))
    if not report['passed']:
        raise SystemExit(1)

if __name__=='__main__':
    main()
