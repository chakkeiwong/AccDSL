"""One company/period report; incomplete paths never become annual totals."""
from fractions import Fraction as Q
import hashlib
import json
from jsonschema import Draft202012Validator, FormatChecker
from authoring import q, schema
from semantics import input_digest, record_digest

LINES = ['cash', 'receivables', 'inventory', 'plant_net', 'tax_prepaid', 'assets',
         'payables', 'debt', 'capital', 'retained', 'equity', 'revenue', 'cost_of_sales',
         'payroll', 'depreciation', 'interest', 'profit_before_tax', 'tax', 'profit',
         'oci', 'comprehensive_income', 'operating_cash', 'investing_cash', 'financing_cash',
         'cash_change', 'opening_cash', 'opening_equity', 'dividends', 'plant_additions']


def build_report(body, run, source_bytes):
    if list(Draft202012Validator(schema(), format_checker=FormatChecker()).iter_errors(body)):
        return {'status': 'invalid', 'reason': 'report_input_schema'}
    digest = input_digest(body)
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    if run.get('input_sha256') != digest or run.get('source_sha256') != source_hash or body['source']['sha256'] != source_hash:
        return {'status': 'invalid', 'reason': 'report_run_binding'}
    registry = json.loads(source_bytes)['record_registry']
    entry = registry.get(body['opening_digest'])
    if not entry or entry['kind'] != 'CompanyState' or record_digest(entry) != body['opening_digest']:
        return {'status': 'invalid', 'reason': 'report_opening_binding'}
    opening = {k: Q(v['n']) / Q(v['d']) for k, v in entry['body']['balances'].items()}
    report = {'profile': 'CompanyYearReportDraft/1', 'input_sha256': digest,
              'source_sha256': source_hash, 'opening_digest': body['opening_digest'],
              'context': body['context'].copy(), 'period': body['period'].copy(),
              'information': body['information'], 'committed': False,
              'run_status': run['status']}
    if run['status'] == 'invalid':
        return {'status': 'invalid', 'reason': 'invalid_run', 'run_reason': run.get('reason')}
    if run['status'] != 'complete_conditional':
        reason = run.get('reason', 'missing_required_inputs')
        report.update(status='partial', annual_complete=False,
                      lines={k: {'status': 'unresolved', 'reason': reason} for k in LINES},
                      obligations=run.get('obligations', []) + ['complete_remaining_operations'],
                      stopped_before=run.get('event'),
                      remaining_events=[e['kind'] for e in body['events'] if e['kind'] not in [j['event'] for j in run.get('applied', [])]])
        report['lines']['opening_cash'] = {'status': 'known', 'value': opening['cash']}
        report['lines']['opening_equity'] = {'status': 'known', 'value': -opening['capital'] - opening['retained']}
        if run.get('applied'):
            report['prefix_snapshot'] = {'as_of': run['applied'][-1]['at'],
                                         'last_event': run['applied'][-1]['event'],
                                         'balances': run['balances'].copy(),
                                         'cash_flows_to_date': run['flows'].copy(),
                                         'is_annual_result': False}
        return report
    b, income, statements = run['closing_balances'], run['income'], run['statements']
    lines = {k: b[k] for k in ['cash', 'receivables', 'inventory', 'tax_prepaid']}
    lines.update(plant_net=b['plant_cost'] + b['accum_depreciation'], assets=statements['assets'],
                 payables=-b['payables'], debt=-b['debt'], capital=-b['capital'], retained=-b['retained'],
                 equity=statements['equity'], **income)
    lines.update(profit_before_tax=statements['profit'] + income['tax'], profit=statements['profit'],
                 oci=Q(0), comprehensive_income=statements['profit'],
                 **{k + '_cash': v for k, v in statements['cash_flows'].items()},
                 cash_change=b['cash'] - opening['cash'], opening_cash=opening['cash'],
                 opening_equity=-opening['capital'] - opening['retained'],
                 dividends=q(body['cash']['dividend']), plant_additions=q(body['cash']['capex']))
    gross = {k: {'inflows': Q(0), 'outflows': Q(0)} for k in ['operating', 'investing', 'financing']}
    for j in run['journals']:
        cash = j['journal'].get('cash', Q(0))
        if cash:
            gross[j['cash_class']]['inflows' if cash > 0 else 'outflows'] += abs(cash)
    if set(lines) != set(LINES):
        return {'status': 'invalid', 'reason': 'report_line_set'}
    checks = {'balance_sheet': lines['assets'] == lines['payables'] + lines['debt'] + lines['equity'],
              'cash_bridge': lines['opening_cash'] + lines['operating_cash'] + lines['investing_cash'] + lines['financing_cash'] == lines['cash'],
              'equity_bridge': lines['opening_equity'] + lines['comprehensive_income'] - lines['dividends'] == lines['equity'],
              'indirect_cfo': run['indirect_cfo'] == lines['operating_cash'],
              'gross_net': all(gross[k]['inflows'] - gross[k]['outflows'] == statements['cash_flows'][k] for k in gross)}
    if not all(checks.values()):
        return {'status': 'invalid', 'reason': 'report_reconciliation', 'checks': checks}
    report.update(status='complete_conditional', annual_complete=True,
                  lines={k: {'status': 'known', 'value': lines[k]} for k in LINES},
                  gross_cash=gross, reconciliation=checks,
                  equity_bridge={'opening': lines['opening_equity'], 'profit': lines['profit'], 'oci': lines['oci'],
                                 'dividends': lines['dividends'], 'closing': lines['equity']})
    return report
