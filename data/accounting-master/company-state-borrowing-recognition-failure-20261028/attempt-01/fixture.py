"""Native borrowing and a deliberately wrong revenue-credit control."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
source=ROOT/'data/accounting-master/declared-financing-clock-20261025/examples.py'
spec=importlib.util.spec_from_file_location('retained_borrowing_examples',source)
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
program,financing,fmt=ex.program,ex.financing,ex.fmt


def make(owner='alpha'):
    b,_,_,m=ex.fixture(owner);book=b['opening']
    book['balances']={k:'0/1' for k in book['balances']}
    book['balances'].update({m['cash']:'20/1',m['capital']:'-20/1'})
    b['registry']['entries']={k:b['registry']['entries'][k] for k in ['debt_issue','debt_redeem']}
    notes=[dict(id='debt',label='Supplied borrowing example',status='unresolved',reason='Synthetic borrowing100 and repayment40; no source, valuation or recognition admission')]
    def report(ident):return dict(kind='report',id=ident,cutoff='2027-01-01',equity_movements=[],notes=deepcopy(notes))
    b['commands']=[ex.event(b,'debt_issue','borrow.1','2027-01-01',{'amount':'100/1'}),report('after.borrow'),ex.event(b,'debt_redeem','repay.1','2027-01-01',{'amount':'40/1'}),report('after.repay')]
    b['name']='borrowing-recognition-'+owner
    return b,m


def revenue_mutation(body,mapping,activity):
    entry=body['registry']['entries']['debt_issue'];method=entry['method'];money=method['monetary']['definition']
    money['accounts']['revenue']=deepcopy(money['accounts']['debt'])
    method['account_map']['revenue']=mapping['revenue'];entry['account_classes']['revenue']='income'
    posting=next(row for row in money['postings'] if row['account']=='debt')
    posting.update(account='revenue',id='deliberate.borrowing.revenue')
    method['memory']['definition']['operations']=[]
    for flow in money['flows']:flow['activity']=activity
    method['residual_prerequisites'].append('Deliberately wrong borrowing revenue and omitted debt memory; negative control only')
    entry['method_sha256']=program.digest(method)
    body['commands']=body['commands'][:2]

