from pathlib import Path
from copy import deepcopy
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import assessed_period_carry_v1 as m
def load(name,path):
    s=importlib.util.spec_from_file_location(name,ROOT/path);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
deferred=load('assessed_carry_deferred','data/accounting-master/shared-deferred-assessment-20261024/examples.py')
old=load('assessed_carry_old','data/accounting-master/provisional-period-carry-20261024/examples.py')
known=deferred.known;payment=old.payment;depreciation=old.depreciation
def request(prior=None,operations=None,findings=None):
    return m.request(deferred.scenario() if prior is None else prior,'assessed-carry-2026',
        {'profile':m.MODEL,'selected':known()},{'start':'2026-01-01','end_exclusive':'2027-01-01'},
        findings if findings is not None else {k:{'status':'unknown','reason':'No new admission evidence'} for k in m.FINDINGS},operations or [])

def cases():
    rows=[]
    def add(name,q,status='complete_provisional',stop=None):
        rows.append({'case':name,'request':deepcopy(q),'expected_status':status,'expected_stop':stop})
    base=request();add('assessed_opening',base);add('pay_carried_tax',request(operations=[payment()]))
    add('payment_and_depreciation',request(operations=[payment(),depreciation()]))
    add('zero_deferred',request(deferred.scenario(rate='0/1')))
    add('unchanged_deferred',request(deferred.scenario(ppe_base='84/1',recognized='40/1',capacity='40/1')))
    add('positive_profit',request(deferred.scenario(ppe_base='100/1',debt_base='0/1',recognized='100/1',capacity='100/1')))
    q=deferred.scenario(taxable='-19/1',paid=False,capacity='42/1')
    next(i for i in q['items'] if i['id'].startswith('loss/'))['recognized_deduction']=known('10/1')
    add('recognized_loss',request(q))
    for value,label in [(False,'false'),(True,'true')]:add('findings_'+label,request(findings={k:known(value) for k in m.FINDINGS}))
    for name,mutate,status in [('strict_annual',lambda q:q['model'].update(profile='strict_annual_close_v1'),'unsupported'),
        ('unselected_model',lambda q:q['model'].update(selected=known(False)),'unsupported'),
        ('unknown_model',lambda q:q['model'].update(selected={'status':'unknown','reason':'Unselected'}),'unresolved'),
        ('gap',lambda q:q['next_period'].update(start='2026-01-02'),'invalid'),
        ('overlap',lambda q:q['next_period'].update(start='2025-12-31'),'invalid'),
        ('empty_period',lambda q:q['next_period'].update(end_exclusive='2026-01-01'),'invalid'),
        ('duplicate_carry',lambda q:q.update(id='deferred-assessment'),'invalid'),
        ('stale_prior',lambda q:q.update(prior_sha256='0'*64),'invalid'),
        ('missing_finding',lambda q:q['findings'].pop('deferred_tax_assessment'),'invalid')]:
        q=deepcopy(base);mutate(q);add(name,q,status)
    q=deepcopy(base);q['prior_request']['recovery_capacity']={'status':'unknown','reason':'Missing capacity'}
    q['prior_sha256']=m.book.digest(q['prior_request']);add('prior_unknown',q,'unresolved')
    for name,op in [('duplicate_prior_event',payment(identity='deferred-assessment')),
        ('duplicate_carry_event',payment(identity='assessed-carry-2026')),
        ('before_opening',payment(day='2025-12-31')),('at_endpoint',payment(day='2027-01-01'))]:
        add(name,request(operations=[op]),'stopped_provisional','invalid')
    add('partial_prefix',request(operations=[payment('1/1'),payment('5/1',identity='excess')]),'stopped_provisional','invalid')
    add('cash_shortage',request(deferred.scenario(taxable='2000/1'),[payment('999/2')]),'stopped_provisional','funding_failure')
    return rows
