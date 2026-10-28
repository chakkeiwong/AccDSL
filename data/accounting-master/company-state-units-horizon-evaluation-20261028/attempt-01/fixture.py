"""Supplied year-end debt schedule through retained native financing methods."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
p=ROOT/'data/accounting-master/declared-financing-clock-20261025/examples.py'
s=importlib.util.spec_from_file_location('retained_horizon_examples',p);ex=importlib.util.module_from_spec(s);s.loader.exec_module(ex)
program,financing,fmt=ex.program,ex.financing,ex.fmt
POLICY=dict(profile=financing.POLICY,convention='actual_days/365_simple',annual_rate='73/62',interest_cash_activity='operating',provenance='Synthetic31-day cost2 on principal20; not a market rate or admitted contract')
def report(ident,day):return dict(kind='report',id=ident,cutoff=day,equity_movements=[],notes=[dict(id='maturity',label='Explicit supplied maturity',status='unresolved',reason='Borrow20 on2027-12-31; pay22 on2028-01-31. Schedule supplied, not inferred or admitted.')])
def rebuild(b,m,intervals):
 reg=financing.build(b['opening'],b['schemas'],{k:m[k] for k in financing.CLASSES},'/finance/cursor','/finance/debt',deepcopy(POLICY),intervals)
 reg['entries']={k:e for k,e in reg['entries'].items() if k in ['debt_issue','debt_redeem','interest_pay'] or k.startswith('interest_accrue.')}
 for e in reg['entries'].values():b['schemas'].update(deepcopy(e['schemas']))
 b['registry']=reg
def first(owner='alpha',cash=Q(3)):
 b,_,_,m=ex.fixture(owner);o=b['opening'];o['date']='2027-12-31';o['period']['start']='2027-12-31'
 o['balances']={k:'0/1' for k in o['balances']};o['balances'].update({m['cash']:fmt(cash),m['capital']:fmt(-cash)})
 o['memory']['finance']=dict(cursor='2027-12-31',debt='0/1')
 rebuild(b,m,[dict(start='2027-12-31',end_exclusive='2028-01-01')])
 annual=report('annual','2027-12-31')
 carry={**deepcopy(annual),'kind':'carry','id':'carry.2027','retained_account':m['retained'],'next_end_exclusive':'2029-01-01','memory_policies':{k:dict(kind='preserve',provenance='Preserve complete debt and complementary memory') for k in o['memory_types']}}
 b['commands']=[ex.event(b,'debt_issue','borrow.20','2027-12-31',{'amount':'20/1'}),ex.event(b,'interest_accrue.1','accrue.day1','2027-12-31',{}),annual,carry]
 b['name']='terminal-borrowing-'+owner
 return b,m
def second(previous,result,m):
 b=deepcopy(previous);b['opening']=deepcopy(result['trace'][-1]['result']['next_opening'])
 rebuild(b,m,[dict(start='2028-01-01',end_exclusive='2028-01-31')])
 b['commands']=[ex.event(b,'interest_accrue.1','accrue.days30','2028-01-30',{}),ex.event(b,'interest_pay','pay.interest2','2028-01-31',{'amount':'2/1'}),ex.event(b,'debt_redeem','repay20','2028-01-31',{'amount':'20/1'}),report('maturity.report','2028-01-31')]
 return b
