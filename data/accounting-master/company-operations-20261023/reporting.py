"""Annual or dated-prefix reporting for CompanyOperationsDraft/1."""
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from operations import digest, record_digest, result

LINES=['cash','receivables','inventory','plant_net','tax_prepaid','assets',
    'payables','debt','capital','retained','equity','revenue','cost_of_sales',
    'payroll','depreciation','interest','profit_before_tax','tax','profit','oci',
    'comprehensive_income','operating_cash','investing_cash','financing_cash',
    'cash_change','opening_cash','opening_equity','dividends','plant_additions']


def build_report(body,run,source):
    sh=hashlib.sha256(source).hexdigest()
    if run.get('input_sha256')!=digest(body) or run.get('source_sha256')!=sh or body['source']['sha256']!=sh:
        return result('invalid',reason='report_input_binding')
    if run['status']=='invalid':return result('invalid',reason='invalid_run')
    try:
        entry=json.loads(source)['record_registry'][body['opening_digest']]
        if record_digest(entry)!=body['opening_digest']:return result('invalid',reason='opening_record')
        opening={k:Q(v['n'])/Q(v['d']) for k,v in entry['body']['balances'].items()}
    except (ValueError,KeyError,TypeError,ZeroDivisionError):
        return result('invalid',reason='opening_structure')
    report={'profile':'CompanyOperationsReportDraft/1','input_sha256':digest(body),
        'run_sha256':digest(run),'source_sha256':sh,'period':deepcopy(body['period']),
        'context':deepcopy(body['context']),'information':body['information'],
        'committed':False,'run_status':run['status']}
    if run['status']!='complete_conditional':
        reason=run.get('reason','missing_required_inputs')
        report.update(status='partial',annual_complete=False,
            lines={k:{'status':'unresolved','reason':reason} for k in LINES},
            stopped_before=run.get('event'),obligations=run.get('obligations',[])+['complete_remaining_operations'])
        report['lines']['opening_cash']={'status':'known','value':opening['cash']}
        report['lines']['opening_equity']={'status':'known','value':-opening['capital']-opening['retained']}
        if run.get('applied'):
            report['prefix_snapshot']={'as_of':run['applied'][-1]['at'],'last_event':run['applied'][-1]['event'],
                'balances':deepcopy(run['balances']),'cash_flows_to_date':deepcopy(run['flows']),
                'is_annual_result':False}
        return report
    b,inc,s=run['closing_balances'],run['income'],run['statements']
    lines={k:b[k] for k in ['cash','receivables','inventory','tax_prepaid']}
    lines.update(plant_net=b['plant_cost']+b['accum_depreciation'],assets=s['assets'],
        payables=-b['payables'],debt=-b['debt'],capital=-b['capital'],retained=-b['retained'],
        equity=s['equity'],**inc)
    lines.update(profit_before_tax=s['profit']+inc['tax'],profit=s['profit'],oci=Q(0),
        comprehensive_income=s['profit'],**{k+'_cash':v for k,v in s['cash_flows'].items()},
        cash_change=b['cash']-opening['cash'],opening_cash=opening['cash'],
        opening_equity=-opening['capital']-opening['retained'],dividends=run['dividends'],
        plant_additions=run['plant_additions'])
    gross={k:{'inflows':Q(0),'outflows':Q(0)} for k in ['operating','investing','financing']}
    for j in run['journals']:
        cash=j['journal'].get('cash',Q(0))
        if cash:gross[j['cash_class']]['inflows' if cash>0 else 'outflows']+=abs(cash)
    checks={'balance_sheet':lines['assets']==lines['payables']+lines['debt']+lines['equity'],
        'cash_bridge':lines['opening_cash']+sum(s['cash_flows'].values())==lines['cash'],
        'equity_bridge':lines['opening_equity']+lines['profit']-lines['dividends']==lines['equity'],
        'indirect_cfo':run['indirect_cfo']==lines['operating_cash'],
        'gross_net':all(gross[k]['inflows']-gross[k]['outflows']==s['cash_flows'][k] for k in gross),
        'report_line_set':set(lines)==set(LINES)}
    if not all(checks.values()):return result('invalid',reason='report_reconciliation',checks=checks)
    report.update(status='complete_conditional',annual_complete=True,
        lines={k:{'status':'known','value':v} for k,v in lines.items()},gross_cash=gross,reconciliation=checks)
    return report
