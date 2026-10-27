from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import importlib.util
import json
import sys

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import company_book_carry_v1 as carry
spec=importlib.util.spec_from_file_location('carry_report_examples',ROOT/'data/accounting-master/company-book-reports-20261025/examples.py')
reports=importlib.util.module_from_spec(spec);spec.loader.exec_module(reports)


def policies(book):
    return {k:{'kind':'preserve','provenance':'Explicit synthetic preservation across the recorded period boundary'} for k in book['memory_types']}


def fixture(owner='alpha',loss=False):
    body=reports.sale_and_equity(owner)
    # Explicit authored hypothetical period-end snapshot, not inferred elapsed events.
    book=body['closing'];book['date']='2027-12-31'
    if loss:
        book['balances'].update({'sales.'+owner:'5/1','cost.'+owner:'-2/1',book['cash_account']:'117/1'})
        book['flows'][0]['amount']='12/1'
    body['expected_closing_sha256']=carry.digest(book)
    retained=next(k for k,v in book['accounts'].items() if v['classification']=='equity')
    return carry.request(body,'close.2027',retained,'2029-01-01',policies(book))


def native_fixture():
    body,expected=reports.native_annual();book=body['closing'];p=policies(book)
    # Mirrors only the explicitly imported tax cursor; the native complement is outside this book.
    p['/tax_closed_until']={'kind':'next_period_start','provenance':'Explicit synthetic native tax cursor carry; not a legal tax-close finding'}
    return carry.request(body,'native-close.2025','retained','2027-01-01',p)


def compare():
    rows=[]
    for name,body in [('profit.alpha',fixture()),('profit.beta',fixture('beta')),('loss.alpha',fixture(loss=True)),('native_balances',native_fixture())]:
        original=deepcopy(body);result=carry.propose(body);before=body['report_request']['closing']
        report=carry.reports.report(body['report_request']);profit=carry.reports.number(report['income']['profit']);retained=body['retained_account']
        expected=deepcopy(before['balances'])
        for k,v in before['accounts'].items():
            if v['classification'] in ['income','expense']:expected[k]='0/1'
        expected[retained]=carry.reports.fmt(carry.reports.number(expected[retained])-profit)
        next_book=result.get('next_opening',{})
        checks={'proposed':result['status']=='proposed','all_balances':next_book.get('balances')==expected,
                'cash_unchanged':next_book.get('balances',{}).get(before['cash_account'])==before['balances'][before['cash_account']],
                'zero_cash_flows':result.get('cash_flows')==[] and next_book.get('flows')==[],
                'lifetime_ids':next_book.get('seen')==before['seen']+[body['close_id']],
                'journal_balanced':sum(carry.reports.number(x) for x in result.get('journal',{}).values())==0,
                'unchanged_input':body==original,'provisional_apply':carry.apply(body,result)['status']=='applied_provisional'}
        if result['status']=='proposed':
            new_report=carry.reports.report(carry.reports.request(next_book,next_book,body['report_request']['schemas'],body['report_request']['mapping']))
            checks['next_opening_report']=new_report['status']=='reported' and new_report['income']['profit']=='0/1'
            checks['equity_continuity']=new_report.get('equity',{}).get('opening')==report['equity']['closing']
        if name=='native_balances':
            path=ROOT/'data/accounting-master/company-return-execution-20261024/trace.json'
            expected_native=json.loads(path.read_text())['next_opening']
            checks['native_balances']=next_book.get('balances')==expected_native['balances']
            checks['native_period']=next_book.get('period')==expected_native['period']
            checks['native_lots']=next_book.get('memory',{}).get('lots')==expected_native['lots']
        rows.append({'case':name,'request':body,'result':result,'checks':checks})
    return {'cases':rows,'checks':[{'name':r['case']+':'+k,'passed':bool(v)} for r in rows for k,v in r['checks'].items()]}


if __name__=='__main__':
    r=compare();bad=[x['name'] for x in r['checks'] if not x['passed']]
    print(json.dumps({'cases':len(r['cases']),'checks':len(r['checks']),'failures':bad}))
    if bad:print(json.dumps([{'case':x['case'],'result':x['result']} for x in r['cases'] if not all(x['checks'].values())])[:1800])
    raise SystemExit(bool(bad))
