from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import sys

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import company_book_reports_v1 as reports
import native_company_sale_v1 as adapter
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
book_ex=load('report_book_examples','data/accounting-master/company-book-transition-20261025/examples.py')


def mapping(book):
    return {'profile':reports.MAP,'context':deepcopy(book['context']),
            'lines':[{'id':'line.'+str(i),'label':key,'classification':row['classification'],'accounts':[key]}
                     for i,(key,row) in enumerate(book['accounts'].items())]}


def payment(owner='alpha'):
    opening,request=book_ex.fixture(owner);result=book_ex.engine.propose(opening,request);assert result['status']=='proposed'
    notes=[{'id':'debt_terms','label':'Debt terms and maturity','status':'missing','reason':'No disclosure schedule supplied for this synthetic payment'}]
    return reports.request(opening,result['after'],request['schemas'],mapping(opening),notes=notes)


def sale_and_equity(owner='alpha'):
    opening,unused=book_ex.fixture(owner);ids=list(opening['accounts']);inventory='stock.'+owner;revenue='sales.'+owner;cost='cost.'+owner
    opening['accounts'].update({inventory:{'classification':'asset'},revenue:{'classification':'income'},cost:{'classification':'expense'}})
    opening['balances'].update({inventory:'20/1',revenue:'0/1',cost:'0/1'});capital=ids[3];opening['balances'][capital]='-100/1'
    closing=deepcopy(opening);cash=opening['cash_account'];closing['date']='2027-01-05'
    closing['balances'].update({cash:'145/1',inventory:'5/1',revenue:'-40/1',cost:'15/1',capital:'-105/1'})
    closing['seen']=['sale','capital_contribution']
    def flow(identity,day,amount,activity,origin):
        return {'id':identity,'entity':opening['context']['entity'],'book':opening['context']['book'],
                'currency':'USD','event_id':identity,'date':day,'activity':activity,'origin':origin,'amount':amount}
    closing['flows']=[flow('sale','2027-01-02','40/1','operating','inventory_sale'),flow('capital_contribution','2027-01-05','5/1','financing','owner_contribution')]
    movements=[{'id':'capital.1','event_id':'capital_contribution','date':'2027-01-05','account':capital,'amount':'5/1','description':'Authored owner cash contribution'}]
    return reports.request(opening,closing,unused['schemas'],mapping(opening),movements)


def native_annual():
    folder=ROOT/'data/accounting-master/company-return-execution-20261024';sys.path.insert(0,str(folder))
    context=load('report_native_context','data/accounting-master/company-return-execution-20261024/retained_execution_context.py')
    author,packet,item,financial=context.load();initial=item('opening')
    opening_native=adapter.native.initialize(author,initial['books']['P'],initial['compound']['prior_interest_expensed'])
    trace=json.loads((folder/'trace.json').read_text());closing_native=trace['trace'][-1]['proposal']['after']
    opening,shape0=adapter.import_book(opening_native);closing,shape1=adapter.import_book(closing_native)
    body=reports.request(opening,closing,{reports.digest(shape0):shape0,reports.digest(shape1):shape1},mapping(opening))
    native_reports=load('report_native_annual','data/accounting-master/company-return-execution-20261024/native_reports.py')
    expected=native_reports.report(opening_native,closing_native);assert expected==trace['annual']
    return body,expected


def compare():
    from fractions import Fraction as Q
    rows=[]
    for name,body in [('payment.alpha',payment()),('payment.beta',payment('beta')),('sale.alpha',sale_and_equity()),('sale.beta',sale_and_equity('beta'))]:
        before=deepcopy(body);result=reports.report(body);is_sale=name.startswith('sale')
        checks={'reported':result['status']=='reported','profit':result.get('income',{}).get('profit')==('25/1' if is_sale else '0/1'),
                'cash':result.get('cash_flows',{}).get('closing_cash')==('145/1' if is_sale else '193/2'),
                'equity':result.get('equity',{}).get('closing')==('130/1' if is_sale else '80/1'),
                'all_reconciliations':set(result.get('reconciliations',{}).values())=={'0/1'},
                'unchanged':body==before,'replay':reports.verify(body,result),
                'no_completeness':result['fiscal_complete'] is False and result['notes_complete'] is False}
        rows.append({'case':name,'request':body,'result':result,'checks':checks})
    body,native=native_annual();result=reports.report(body)
    checks={'reported':result['status']=='reported','profit':result.get('income',{}).get('profit')==native['income']['profit'],
            'all_asset_lines':{r['accounts'][0]:r['closing'] for r in result.get('statement_lines',{}).get('asset',[])}==native['balance_sheet']['assets'],
            'all_liability_lines':{r['accounts'][0]:r['closing'] for r in result.get('statement_lines',{}).get('liability',[])}==native['balance_sheet']['liabilities'],
            'all_income_expense_lines':{r['accounts'][0]:r['closing'] for k in ['income','expense'] for r in result.get('statement_lines',{}).get(k,[])}=={k:v for k,v in native['income'].items() if k!='profit'},
            'all_direct_cash_flows':result.get('cash_flows',{}).get('activities')==native['cash_flows'],
            'opening_equity':result.get('equity',{}).get('opening')==native['opening_equity'],
            'closing_equity':result.get('equity',{}).get('closing')==native['balance_sheet']['equity'],
            'cash':result.get('cash_flows',{}).get('closing_cash')==native['closing_cash'],
            'reconciliations':set(result.get('reconciliations',{}).values())=={'0/1'}}
    rows.append({'case':'native_annual','request':body,'native':native,'result':result,'checks':checks})
    return {'cases':rows,'checks':[{'name':r['case']+':'+k,'passed':bool(v)} for r in rows for k,v in r['checks'].items()]}


if __name__=='__main__':
    x=compare();bad=[c['name'] for c in x['checks'] if not c['passed']]
    print(json.dumps({'cases':len(x['cases']),'checks':len(x['checks']),'failures':bad}))
    if bad:print(json.dumps([{'case':r['case'],'result':r['result']} for r in x['cases'] if not all(r['checks'].values())])[:1600])
    raise SystemExit(bool(bad))
