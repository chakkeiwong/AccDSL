"""Original SIM-F036: separate native accrued-interest and settlement methods."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
SOURCE=ROOT/'data/accounting-master/declared-financing-clock-20261025/examples.py'
spec=importlib.util.spec_from_file_location('retained_accrual_examples',SOURCE)
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
program,financing=ex.program,ex.financing
fmt=ex.fmt


def make(owner='alpha',activity='operating',cash='20/1'):
    body,_,_,mapping=ex.fixture(owner,activity)
    book=body['opening']
    book['balances']={key:'0/1' for key in book['balances']}
    book['balances'].update({mapping['cash']:cash,mapping['inventory']:'100/1',
        mapping['debt']:'-100/1',mapping['capital']:fmt(-financing.Q(cash))})
    book['memory']['finance']={'cursor':'2027-01-01','debt':'-100/1'}
    policy=dict(profile=financing.POLICY,convention='actual_days/365_simple',
        annual_rate='1/20',interest_cash_activity=activity,
        provenance='Explicit synthetic100 principal and5 percent annual rate for original SIM-F036; cash classification supplied')
    intervals=[dict(start='2027-01-01',end_exclusive='2028-01-01')]
    registry=financing.build(book,body['schemas'],{k:mapping[k] for k in financing.CLASSES},
        '/finance/cursor','/finance/debt',policy,intervals)
    registry['entries']={key:registry['entries'][key] for key in ['interest_accrue.1','interest_pay']}
    for entry in registry['entries'].values():body['schemas'].update(deepcopy(entry['schemas']))
    body['registry']=registry;body['name']='accrual-then-settlement-'+owner+'-'+activity
    notes=[dict(id='coupon',label='Supplied accrued coupon',status='unresolved',
        reason='Synthetic policy and balances; no source or treatment admission.2028 report covers only settlement on January1.')]
    first=dict(kind='report',id='report.2027',cutoff='2027-12-31',equity_movements=[],notes=deepcopy(notes))
    carry={**deepcopy(first),'kind':'carry','id':'close.2027','retained_account':mapping['retained'],
        'next_end_exclusive':'2029-01-01','memory_policies':{key:dict(kind='preserve',
        provenance='Preserve outstanding contract and complementary memory') for key in book['memory_types']}}
    second=dict(kind='report',id='settlement.2028',cutoff='2028-01-01',equity_movements=[],notes=deepcopy(notes))
    body['commands']=[ex.event(body,'interest_accrue.1','accrue.2027','2027-12-31',{}),first,carry,
        ex.event(body,'interest_pay','pay.2028','2028-01-01',{'amount':'5/1'}),second]
    return body,mapping


def reexpense_mutation(body,mapping):
    """Deliberately invalid economic mapping; balanced entries are insufficient."""
    entry=body['registry']['entries']['interest_pay'];method=entry['method']
    monetary=method['monetary']['definition']
    monetary['accounts']['interest']=deepcopy(monetary['accounts']['interest_payable'])
    method['account_map']['interest']=mapping['interest']
    entry['account_classes']['interest']='expense'
    posting=next(x for x in monetary['postings'] if x['account']=='interest_payable')
    posting['account']='interest';posting['id']='deliberate.second.expense'
    method['residual_prerequisites'].append('Deliberately wrong payment debit; negative control, never an admitted method')
    entry['method_sha256']=program.digest(method)

