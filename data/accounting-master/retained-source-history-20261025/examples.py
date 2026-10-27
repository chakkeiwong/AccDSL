"""Explicit hypothetical histories constrained only by selected retained cash."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import retained_source_history_v1 as adapter
attachment=adapter.attachment
BUDGET={'max_slots':4,'max_formula_nodes':10000,'max_integer_assignments':1,
        'max_cells':1,'elapsed_ms':5000,'solver_timeout_ms':1000,'solver_rlimit':1000000}

def rat(q):
    q=Q(q);return str(q.numerator)+'/'+str(q.denominator)

def premise(name,meaning):
    return {'id':'constructed:'+name,'status':'proposed','meaning':meaning}

def domain(lo,hi=None):
    return {'interval':{'lower':rat(lo),'upper':rat(lo if hi is None else hi),
        'lower_inclusive':True,'upper_inclusive':True},
        'premise':premise('bounded_domains','Explicit finite domains for a hypothetical selected-cash example; not source-derived amounts.'),
        'source_ref':'constructed:selected_cash_counterexample'}

def coefficient(value,context):
    return {'value':rat(value),'type':{'kind':'rational','context':deepcopy(context),
            'dimensions':{},'scale':'1/1'}}

def fixture(selected=None,source_result=None):
    selected=list(adapter.source.SUPPORTED if selected is None else selected)
    request=adapter.source.fixture(selected,True)
    retained=source_result or adapter.source.assess(request,attachment.measurement_budget(BUDGET))
    assert retained['status']=='conditionally_feasible',retained.get('reason')
    histories={}
    for relation in retained['definition']['relations']:
        name=relation['id'];opening=relation['opening'];closing=relation['closing']
        movement=relation['movements'][0]['observation']
        obs=retained['definition']['observations'];money=deepcopy(obs[opening]['type']['value_type'])
        context=money['context']
        a=retained['preserved_report']['observations'][retained['source_mapping'][opening]['alias']]['observation']['record']['body']['value']['amount']
        cash=Q(int(a['n']),int(a['d']));start=obs[opening]['type']['time']['at'];end=obs[closing]['type']['time']['at']
        first=relation['period']['start']
        def c(value):return coefficient(value,context)
        h={'profile':attachment.history.PROFILE,
            'scope':{'name':'hypothetical_cash_history:'+name,'exclusions':[
                'actual transactions and legal accounts','full filing consistency','cash classifications and standards admission']},
            'value_type':money,'opening_date':start,'dates':[first,end],
            'accounts':{'Cash':domain(cash),'Debt':domain(-1000),'Capital':domain(1000-cash)},
            'memory':{},'balance_premise':premise('opening','Hypothetical balanced opening for a cash-only counterexample.'),
            'templates':{
                'borrow':{'event_type':deepcopy(money),'postings':{'Cash':c(1),'Debt':c(-1)},'memory':{},
                    'premise':premise('borrow','Hypothetical cash borrowing; no disclosed borrowing is inferred.'),'provenance':'constructed:borrow'},
                'repay':{'event_type':deepcopy(money),'postings':{'Cash':c(-1),'Debt':c(1)},'memory':{},
                    'premise':premise('repay','Hypothetical principal repayment; no disclosed repayment is inferred.'),'provenance':'constructed:repay'}},
            'events':[{'id':'borrow','date':first,'template':'borrow','amount':domain(0,2000)},
                      {'id':'repay','date':end,'template':'repay','amount':domain(0,2000)}],
            'measurements':[{'id':'opening_cash','date':start,'value_type':deepcopy(money),
                'terms':[{'kind':'account','field':'Cash','coefficient':c(1)}],'domain':domain(cash)}],
            'obligations':[], 'state_constraints':[]}
        bindings={}
        for key in [opening,movement,closing]:
            bindings[key]={'kind':'movement' if key==movement else 'snapshot',
                'quantity':obs[key]['type']['quantity'],
                'terms':[{'kind':'account','field':'Cash','coefficient':c(1)}],
                'premise':premise('cash_mapping:'+name,'The hypothetical Cash field is identified with this selected source cash population solely for a conditional compatibility test.')}
        histories[name]={'history':h,'bindings':bindings}
    return {'profile':adapter.PROFILE,'source_request':request,'histories':histories}

def witness(definition,borrow,repay):
    h=definition['history'];key=attachment.key;identifier=attachment.history.identifier
    out={key('history',identifier('opening_account',name)):row['interval']['lower'] for name,row in h['accounts'].items()}
    out[key('history',identifier('event_amount','borrow'))]=rat(borrow)
    out[key('history',identifier('event_amount','repay'))]=rat(repay)
    cash=Q(h['accounts']['Cash']['interval']['lower']);change=Q(borrow)-Q(repay)
    relation=definition['measurements']['relations'][0]
    for name,value in [(relation['opening'],cash),(relation['movements'][0]['observation'],change),(relation['closing'],cash+change)]:
        out[key('measurement',name)]=rat(value)
    return out
