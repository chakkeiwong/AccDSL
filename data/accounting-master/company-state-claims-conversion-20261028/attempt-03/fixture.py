"""Explicit conversion method and finite rights problems; no actual admission."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import z3
from rational_solver_v1 import Problem,Budget,q,solve
p=ROOT/'data/accounting-master/company-state-gross-equity-history-20261028/fixture.py'
s=importlib.util.spec_from_file_location('claims_equity_fixture',p)
base=importlib.util.module_from_spec(s);s.loader.exec_module(base)
program,h=base.program,base.h
fmt,ref,binary,constant=base.fmt,base.ref,base.binary,base.constant
BUDGET=Budget(8,10000,50,50,10000,1000,1000000)

def conversion(owner='alpha',clear_face=True):
    b,m=base.make('issue_only',owner);book=b['opening']
    book['balances'].update({m['inventory']:'160/1',m['debt']:'-160/1'})
    book['memory']['terms']['face']='160/1'
    entry=deepcopy(b['registry']['entries']['equity_issue']);method=entry['method']
    identity='synthetic.fixed16.debt_conversion';method['id']=identity
    for key in ['preconditions','postconditions']:method[key]['manifest']['method_id']=identity
    money=program.engine.money_type(book);shares=entry['event_inputs']['shares']
    pre=method['preconditions']
    for name,binding in [('debt',{'kind':'account','role':'debt'}),('face',{'kind':'memory','pointer':'/terms/face'})]:
        pre['manifest']['inputs'][name]=h.declaration(money,name);pre['bindings'][name]=binding
    for name,predicate,deps in [
        ('fixed_conversion_shares',binary('eq',ref('shares'),constant(shares,'16/1')),['shares']),
        ('full_claim_conversion',binary('eq',ref('face'),binary('mul',ref('shares'),ref('price'))),['face','shares','price']),
        ('principal_equals_carrying',binary('eq',ref('face'),binary('sub',constant(money,'0/1'),ref('debt'))),['face','debt'])]:
        pre['manifest']['requirements'].append(dict(id=name,guard=constant(program.core.BOOL,True),guard_requires=[],
            predicate=predicate,requires=deps,admission_refs=[],on_false='invalid',on_unknown='unresolved'))
    method['account_map']['debt']=m['debt'];entry['account_classes']['debt']='liability'
    monetary=method['monetary']['definition'];monetary['method_id']=identity;monetary['accounts']['debt']=deepcopy(money)
    for row in monetary['postings']:
        if row['account']=='cash':row.update(account='debt',id='extinguish.converted.debt')
    monetary['flows']=[]
    if clear_face:method['memory']['definition']['operations'].append(dict(id='extinguish.face',op='replace',path=['terms','face'],value=dict(kind='literal',value='0/1')))
    method['residual_prerequisites']=['Authored full160 principal/carrying conversion into16 ordinary shares; no cash, gain/loss, fees or tax.',
        'Price input10 is the supplied debt-per-new-share conversion term, not an offer or economic equity price.',
        'No actual authority, contract, classification, accounting or complete share-population admission.']
    entry['method_sha256']=program.digest(method);b['registry']['entries']={'convert':entry}
    command=b['commands'][0];command['method_key']='convert';command['event']['id']='conversion.1'
    command['event']['inputs']['shares']['value']=program.engine.known('16/1')
    command['event']['inputs']['price']['value']=program.engine.known('10/1')
    report=b['commands'][-1];report['equity_movements']=[dict(id='debt.to.equity',event_id='conversion.1',date=command['event']['date'],account=m['capital'],amount='160/1',description='Synthetic noncash conversion of full debt')]
    report['notes']=[dict(id='conversion_terms',label='Conditional debt conversion',status='unresolved',reason='Supplied synthetic fixed terms, no actual source/accounting admission')]
    b['name']='claims-conversion-'+owner
    return b,m

def collateral(priority=None,independent=False):
    p=Problem('Original SIM-F027 one collateral pool','explicit unweighted priority alternatives')
    rank=z3.Int('priority');a,b=z3.Reals('recovery_a recovery_b')
    p.variables={'priority':rank,'recovery_a':a,'recovery_b':b};p.finite={'priority':[0,1]}
    if independent:
        p.add('independent_claim_a',a==40);p.add('independent_claim_b',b==30)
    else:
        p.add('a_first',z3.Implies(rank==0,z3.And(a==40,b==10)))
        p.add('b_first',z3.Implies(rank==1,z3.And(a==20,b==30)))
    p.add('sole_pool50',a+b<=50);p.add('nonnegative_a',a>=0);p.add('nonnegative_b',b>=0)
    if priority is not None:p.add('supplied_priority',rank==priority)
    p.outputs=dict(recovery_a=a,recovery_b=b,residual=q(50)-a-b)
    p.provenance=dict(claims=[40,30],collateral=50,priority_evidence=priority,independent_double_count_control=independent,
        probability=None,source_admission=False,scope='One pool, two strict ranks; no legal priority inference')
    return p

def preference(value,both=False):
    p=Problem('Original SIM-F032 nonparticipating preference','explicit terminal-value election')
    choice=z3.Int('election');pay=z3.Real('holder_payment')
    p.variables={'election':choice,'holder_payment':pay};p.finite={'election':[0,1]}
    pref=q(min(Q(value),Q(60)));conv=q(Q(value,4))
    if both:p.add('incorrect_combined_rights',pay==pref+conv)
    else:
        p.add('exclusive_preference',z3.Implies(choice==0,pay==pref))
        p.add('exclusive_conversion',z3.Implies(choice==1,pay==conv))
        p.add('rational_terminal_election',z3.And(pay>=pref,pay>=conv))
    p.add('pool_conservation_and_nonnegative_residual',pay<=q(value))
    p.add('nonnegative_payment',pay>=0)
    p.outputs=dict(holder_payment=pay,common_payment=q(value)-pay,preference=pref,conversion=conv)
    p.provenance=dict(exit_value=value,preference60=60,conversion_fraction='1/4',nonparticipating=not both,
        terminal_maximization=True,probability=None,source_admission=False)
    return p
