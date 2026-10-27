"""Constructed internal loan and external customer receipt across one period."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import group_period_report_v1 as group
spec=importlib.util.spec_from_file_location('paired_book_examples',ROOT/'data/accounting-master/compatible-book-composition-20261025/examples.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)

def fixture(chart='named',cross_activity=True):
    closing=base.fixture(chart)
    key=lambda owner,role:next(k for k,v in closing['account_maps'][owner].items() if v==role)
    sales='S.sales' if chart=='named' else 'S.199'
    closing['books']['S']['accounts'][sales]={'classification':'income'}
    closing['account_maps']['S'][sales]='sales';closing['chart']['sales']={'classification':'income'}
    for owner,amounts in [('P',{'cash':'70/1','investment':'100/1','receivable':'30/1','capital':'-200/1'}),
                          ('S',{'cash':'150/1','equipment':'0/1','payable':'-30/1','capital':'-100/1','sales':'-20/1'})]:
        closing['books'][owner]['balances']={key(owner,role):value for role,value in amounts.items()}
    for side,amount in [('positive','30/1'),('negative','-30/1')]:closing['eliminations'][0][side]['expected_balance']=amount
    closing['eliminations'][0]['premise']='Supplied matching internal principal30; no interest or impairment'
    opening=deepcopy(closing);opening['eliminations']=opening['eliminations'][1:]
    for owner,amounts in [('P',{'cash':'100/1','investment':'100/1','receivable':'0/1','capital':'-200/1'}),
                          ('S',{'cash':'100/1','equipment':'0/1','payable':'0/1','capital':'-100/1','sales':'0/1'})]:
        book=opening['books'][owner];book['balances']={key(owner,role):value for role,value in amounts.items()};book['date']='2025-01-01'
    def flow(owner,name,amount,activity):
        return {'id':name,'entity':owner,'book':'legal','currency':'USD','event_id':name+'-event',
                'date':'2025-06-30','activity':activity,'origin':'Constructed '+name,'amount':amount}
    closing['books']['P']['flows']=[flow('P','internal-out','-30/1','investing' if cross_activity else 'operating')]
    closing['books']['S']['flows']=[flow('S','internal-in','30/1','financing' if cross_activity else 'operating'),flow('S','customer','20/1','operating')]
    for book in closing['books'].values():book['seen'].extend(f['event_id'] for f in book['flows'])
    for body in [opening,closing]:base.rehash(body)
    legal={}
    for owner,book in opening['books'].items():
        mapping={'profile':group.reports.MAP,'context':deepcopy(book['context']),
                 'lines':[{'id':account,'label':account,'classification':row['classification'],'accounts':[account]} for account,row in book['accounts'].items()]}
        legal[owner]=group.reports.request(book,closing['books'][owner],opening['schemas'],mapping,
            notes=[{'id':'complete-note-package','label':'Notes','status':'missing','reason':'Constructed period does not supply complete notes'}])
    def ref(owner,index):
        flow=closing['books'][owner]['flows'][index]
        return {'owner':owner,'flow_id':flow['id'],'expected_flow_sha256':group.core.digest(flow)}
    return {'profile':group.PROFILE,'opening':opening,'closing':closing,'legal_reports':legal,
            'internal_cash_pairs':[{'id':'loan-transfer','payer':ref('P',0),'payee':ref('S',0),
                'premise':'Same constructed internal loan payment30, same date, P pays S; classifications may differ'}]}

def refresh(body):
    for name in ['opening','closing']:base.rehash(body[name])
    for owner,request in body['legal_reports'].items():
        for name in ['opening','closing']:
            request[name]=deepcopy(body[name]['books'][owner]);request['expected_'+name+'_sha256']=group.core.digest(request[name])

def cases():
    cases={}
    for chart in ['named','numbered']:
        for cross in [False,True]:
            body=fixture(chart,cross);before=deepcopy(body);r=group.report(body)
            assert r['status']=='period_reported',r
            assert body==before and group.verify(body,r)
            assert r['cash_flows']['opening_cash']=='200/1' and r['cash_flows']['closing_cash']=='220/1'
            assert r['cash_flows']['activities']=={'operating':{'receipts':'20/1','payments':'0/1','net':'20/1'},
                'investing':{'receipts':'0/1','payments':'0/1','net':'0/1'},'financing':{'receipts':'0/1','payments':'0/1','net':'0/1'}}
            assert r['equity']=={'opening':'200/1','direct_movements':'0/1','profit':'20/1','closing':'220/1'}
            assert r['opening_worksheet']['adjusted_totals']=={'assets':'200/1','liabilities':'0/1','equity_including_profit':'200/1','profit':'0/1','balance_check':'0/1'}
            assert r['closing_worksheet']['adjusted_totals']=={'assets':'220/1','liabilities':'0/1','equity_including_profit':'220/1','profit':'20/1','balance_check':'0/1'}
            assert all(v=='0/1' for v in r['reconciliations'].values())
            assert [row['flow']['id'] for row in r['cash_flows']['origins']]==['customer']
            for owner in body['legal_reports']:
                assert r['legal_reports'][owner]==group.reports.report(body['legal_reports'][owner])
            cases[chart+('-cross' if cross else '-operating')]={'request':body,'result':r}
    return cases
