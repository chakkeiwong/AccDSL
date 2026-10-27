"""Retain acquisition origins while adding derivatives to one continuing hedge."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re
from types import ModuleType

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
LOCK=json.loads((OUT/'input-lock.json').read_text())['files']
HEDGE='data/accounting-master/repeated-rebalancing-20261016/reference.py'
OPEN={'legacy_single_whole_instrument','no_other_cash_or_earnings','pretax_scope'}
ADD={'objective_unchanged','changed_relationship','documentation_updated','ratio_eligible',
     'eligible_external_whole_nonoption','purchase_equals_fair_value','immediate_purchase_and_designation','no_fees'}
MEASURE={'zero_discount_admitted','complete_valuation_effects','forecast_highly_probable',
         'economic_relationship','credit_risk_not_dominant','ratio_eligible'}


class Refusal(Exception):
    def __init__(self,status,reason):self.status,self.reason=status,reason


def need(ok,reason,status='rejected'):
    if not ok:raise Refusal(status,reason)


def q(value):
    need(isinstance(value,str) and re.fullmatch(r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?',value),'rational_encoding')
    r=Q(value);need(str(r)==value,'rational_encoding');return r


def day(value):
    need(isinstance(value,str),'date_encoding')
    try:d=date.fromisoformat(value)
    except ValueError:raise Refusal('rejected','date_encoding')
    need(d.isoformat()==value,'date_encoding');return d


def findings(value,fields):
    need(isinstance(value,dict) and set(value)==fields,'findings_shape')
    for key in sorted(fields):
        need(value[key] is not None,'missing_'+key,'unresolved')
        need(type(value[key]) is bool,'finding_type')
        need(value[key],'finding_'+key,'unsupported')


def encode(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,list):return [encode(v) for v in value]
    return value


def calculate(request,resolve_bytes=None):
    result=dict(wire='AddedInstrumentLayers/1',status='rejected',reason=None,
                baseline=None,state=None,trace=[],journals=[],flows=[],mutations=[])
    try:
        need(isinstance(request,dict) and set(request)=={'wire','operation','baseline_hedge','context','opening_cash','findings','events'},'request_shape')
        need(request['wire']=='AddedInstrumentLayers/1' and request['operation']=='report','operation')
        findings(request['findings'],OPEN)
        reader=resolve_bytes or (lambda p:p.read_bytes());payloads={}
        for item in LOCK:
            try:payload=reader(ROOT/item['path'])
            except OSError:raise Refusal('unresolved','input_bytes_missing')
            need(isinstance(payload,bytes),'input_bytes_type')
            need(hashlib.sha256(payload).hexdigest()==item['sha256'],'input_bytes_changed')
            payloads[item['path']]=payload
        module=ModuleType('pinned_item_hedge');module.__file__=str(ROOT/HEDGE)
        exec(compile(payloads[HEDGE],module.__file__,'exec'),module.__dict__)
        baseline=module.calculate(request['baseline_hedge'])
        need(baseline['status']=='conditional_complete','baseline_'+str(baseline['reason']),baseline['status'])
        b=baseline['state'];need(b['last_operation']=='measure','baseline_measurement_required')
        need(request['context']==b['context'],'context_mismatch')
        # Original aggregate is admitted as one whole instrument by the opening finding.
        opening=q(request['opening_cash']);need(opening>=0,'negative_opening_cash')
        current=day(b['date']);maturity=day(b['context']['maturity_date'])
        price=Q(b['price']);H=Q(b['H']);D=Q(b['D']);R=Q(b['reserve']);I=Q(b['profit'])
        legs={'original':dict(id='original',designation_date=b['context']['designation_date'],
              nominal=None,origin_value=Q(0),value=D,origin='replayed_zero_value_instrument')}
        books=dict(cash=opening,capital=-opening,cf_reserve=-R,gains=-I)
        books['derivative:original']=D
        last_operation='measure'
        trace=[];journals=[];flows=[]

        def snapshot(id,operation,when):
            basis=sum(x['origin_value'] for x in legs.values())
            carrying=sum(x['value'] for x in legs.values())
            assets=sum(max(Q(0),x['value']) for x in legs.values())
            liabilities=-sum(min(Q(0),x['value']) for x in legs.values())
            need(carrying==basis+D,'origin_gain_bridge')
            need(sum(books.values())==0,'book_balance')
            need(books['cash']>=0,'funding_required','unsupported')
            need(books['cash']==opening-basis,'acquisition_cash_bridge')
            need(books['cash']+assets==liabilities+opening+R+I,'equity_bridge')
            return dict(id=id,operation=operation,date=when,price=price,cash=books['cash'],
                net_derivative=carrying,D=D,H=H,reserve=R,profit=I,acquisition_basis=basis,
                derivative_assets=assets,derivative_liabilities=liabilities,pretax_equity=opening+R+I,
                instruments=deepcopy(legs),item_layers=deepcopy(b['layers']),books=deepcopy(books))

        state=snapshot('baseline','baseline',b['date']);trace.append(state)
        events=request['events'];need(isinstance(events,list),'events_shape')
        ids={'baseline'}|{x['id'] for x in request['baseline_hedge']['events']}
        for event in events:
            need(isinstance(event,dict),'event_shape')
            operation=event.get('operation')
            need(operation in ('add_instrument','measure'),'different_instrument_or_item_method','unsupported')
            expected={'id','operation','date','context','findings'}|({'instrument'} if operation=='add_instrument' else {'price','values'})
            need(set(event)==expected,'event_shape')
            id=event['id'];need(isinstance(id,str) and bool(id) and id not in ids,'event_id');ids.add(id)
            need(event['context']==b['context'],'context_mismatch')
            when=day(event['date']);need(current<=when<maturity,'event_chronology')
            if operation=='add_instrument':
                findings(event['findings'],ADD)
                need(last_operation=='measure' and when==current,'measure_before_addition')
                instrument=event['instrument']
                need(isinstance(instrument,dict) and set(instrument)=={'id','nominal','acquisition_value'},'instrument_shape')
                name=instrument['id'];need(isinstance(name,str) and bool(name) and name not in legs,'instrument_id')
                nominal=q(instrument['nominal']);cost=q(instrument['acquisition_value'])
                need(nominal>0,'positive_nominal')
                need(cost>=0,'negative_acquisition_method','unsupported')
                legs[name]=dict(id=name,designation_date=event['date'],nominal=nominal,
                    origin_value=cost,value=cost,origin='cash_acquisition_at_fair_value')
                entries={'derivative:'+name:cost,'cash':-cost}
                flows.append(dict(id=id,date=event['date'],origin='derivative_acquisition',instrument=name,amount=-cost,
                                  classification='not_assessed_in_this_measurement_profile'))
            else:
                findings(event['findings'],MEASURE)
                price=q(event['price']);values=event['values']
                need(isinstance(values,dict) and set(values)==set(legs),'instrument_population')
                parsed={k:q(v) for k,v in values.items()}
                newD=sum(parsed[k]-leg['origin_value'] for k,leg in legs.items())
                newH=-sum(Q(x['quantity'])*(price-Q(x['price'])) for x in b['layers'])
                need(newD==0 or newH==0 or newD*newH<0,'nonoffsetting_cumulative_method','unsupported')
                newR=(Q(1) if newD>0 else Q(-1) if newD<0 else Q(0))*min(abs(newD),abs(newH))
                newI=newD-newR
                entries={'derivative:'+k:parsed[k]-leg['value'] for k,leg in legs.items()}
                entries.update(cf_reserve=-(newR-R),gains=-(newI-I))
                D,H,R,I=newD,newH,newR,newI
                for k in legs:legs[k]['value']=parsed[k]
            need(sum(entries.values())==0,'journal_balance')
            for account,value in entries.items():books[account]=books.get(account,Q(0))+value
            current=when;last_operation=operation
            journals.append(dict(id=id,operation=operation,date=event['date'],entries=entries))
            state=snapshot(id,operation,event['date']);trace.append(state)
        result.update(status='conditional_complete',baseline=baseline,state=encode(state),
                      trace=encode(trace),journals=encode(journals),flows=encode(flows))
    except Refusal as exc:result.update(status=exc.status,reason=exc.reason)
    return result
