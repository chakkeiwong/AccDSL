"""Continuing cash-flow hedge with repeated additions to hedged-item volume."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
import re

CONTEXT={'entity','book','currency','quantity_unit','price_unit','risk','relationship','rule','maturity_date','designation_date'}
MEASURE={'zero_discount_admitted','complete_valuation_effects','forecast_highly_probable','economic_relationship','credit_risk_not_dominant','ratio_eligible'}
REBALANCE={'objective_unchanged','changed_relationship','documentation_updated','ratio_eligible'}


class Refusal(Exception):
    def __init__(self,status,reason):
        self.status,self.reason=status,reason


def need(ok,reason,status='rejected'):
    if not ok:raise Refusal(status,reason)


def rational(value):
    need(isinstance(value,str) and re.fullmatch(r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?',value),'rational_encoding')
    result=Q(value)
    need(str(result)==value,'rational_encoding')
    return result


def day(value):
    try:
        need(isinstance(value,str),'date_encoding')
        parsed=date.fromisoformat(value)
        need(parsed.isoformat()==value,'date_encoding')
        return parsed
    except ValueError:
        raise Refusal('rejected','date_encoding')


def findings(value,fields):
    need(isinstance(value,dict) and set(value)==fields,'findings_shape')
    for key in sorted(fields):
        need(value[key] is not None,'missing_'+key,'unresolved')
        need(type(value[key]) is bool,'finding_type')
        need(value[key],'finding_'+key,'unsupported')


def layer(value):
    need(isinstance(value,dict) and set(value)=={'id','quantity','price','date'},'layer_shape')
    need(isinstance(value['id'],str) and bool(value['id']),'layer_id')
    q,p=rational(value['quantity']),rational(value['price'])
    need(q>0,'positive_quantity')
    day(value['date'])
    return dict(value,quantity=q,price=p)


def encode(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,list):return [encode(v) for v in value]
    return value


def calculate(request):
    result=dict(wire='RepeatedItemRebalancing/1',status='rejected',reason=None,failed_event=None,
                state=None,trace=[],journals=[],mutations=[])
    event_index=None
    try:
        need(isinstance(request,dict) and set(request)=={'wire','operation','opening','events'},'request_shape')
        need(request['wire']=='RepeatedItemRebalancing/1' and request['operation']=='report','operation')
        op=request['opening']
        need(isinstance(op,dict) and set(op)=={'context','findings','layer'},'opening_shape')
        context=op['context']
        need(isinstance(context,dict) and set(context)==CONTEXT and all(isinstance(v,str) and v for v in context.values()),'context_shape')
        start,end=day(context['designation_date']),day(context['maturity_date'])
        need(start<end,'context_dates')
        findings(op['findings'],MEASURE)
        original=layer(op['layer'])
        need(original['date']==context['designation_date'],'original_layer_date')
        need(isinstance(request['events'],list),'events_shape')
        need(bool(request['events']),'observations_missing','unresolved')
        state=dict(context=deepcopy(context),date=context['designation_date'],price=original['price'],
            D=Q(0),H=Q(0),reserve=Q(0),profit=Q(0),layers=[original],revision=0,
            last_operation=None,books=dict(derivative=Q(0),cf_reserve=Q(0),gains=Q(0)))
        ids=set();trace=[];journals=[]
        for event_index,event in enumerate(request['events']):
            need(isinstance(event,dict),'event_shape')
            operation=event.get('operation')
            need(operation in ('measure','add_item'),'different_layer_or_settlement_method','unsupported')
            fields={'id','operation','date','context','findings'} | ({'price','derivative'} if operation=='measure' else {'layer'})
            need(set(event)==fields,'event_shape')
            need(isinstance(event['id'],str) and event['id'] and event['id'] not in ids,'event_id')
            ids.add(event['id'])
            need(event['context']==context,'context_mismatch')
            when=day(event['date'])
            need(day(state['date'])<=when<end,'event_date')
            entries=dict(derivative=Q(0),cf_reserve=Q(0),gains=Q(0))
            if operation=='measure':
                findings(event['findings'],MEASURE)
                p,D=rational(event['price']),rational(event['derivative'])
                H=-sum(x['quantity']*(p-x['price']) for x in state['layers'])
                need(D*H<=0,'nonoffsetting_cumulative_values','unsupported')
                R=(Q(1) if D>0 else Q(-1) if D<0 else Q(0))*min(abs(D),abs(H))
                I=D-R
                entries=dict(derivative=D-state['D'],cf_reserve=-(R-state['reserve']),gains=-(I-state['profit']))
                state.update(price=p,D=D,H=H,reserve=R,profit=I)
                journals.append(dict(id=event['id'],date=event['date'],entries=entries))
            else:
                findings(event['findings'],REBALANCE)
                need(state['date']==event['date'] and state['last_operation']=='measure','measure_immediately_before_rebalance')
                added=layer(event['layer'])
                need(added['date']==event['date'] and added['price']==state['price'],'new_layer_origin')
                need(added['id'] not in [x['id'] for x in state['layers']],'duplicate_layer')
                state['layers'].append(added)
                state['revision']+=1
            for key,value in entries.items():state['books'][key]+=value
            need(sum(entries.values())==0,'unbalanced_journal')
            need(sum(state['books'].values())==0,'unbalanced_books')
            need(state['books']==dict(derivative=state['D'],cf_reserve=-state['reserve'],gains=-state['profit']),'cumulative_book_mismatch')
            state.update(date=event['date'],last_operation=operation)
            trace.append(dict(event_id=event['id'],operation=operation,state=deepcopy(state),journal=entries))
        result.update(status='conditional_complete',state=encode(state),trace=encode(trace),journals=encode(journals))
    except Refusal as exc:
        result.update(status=exc.status,reason=exc.reason,failed_event=event_index)
    return result
