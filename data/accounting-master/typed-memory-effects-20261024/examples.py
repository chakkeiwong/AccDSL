"""Memory-layer comparisons; the test harness explicitly supplies derived amounts."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import importlib.util, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_memory_effects_v1 as memory
import native_return_state_structure_v1 as structure
spec=importlib.util.spec_from_file_location('memory_monetary_examples',HERE.parent/'typed-monetary-effects-20261024/examples.py')
monetary=importlib.util.module_from_spec(spec);spec.loader.exec_module(monetary)
core=memory.core


def record(fields):
    return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}


def literal(value):return {'kind':'literal','value':value}
def read(pointer,source='inputs'):return {'kind':'read','source':source,'pointer':pointer}
def obj(fields):return {'kind':'object','fields':fields}


def program(kind):
    state=structure.schema();p=state['properties']
    text={'type':'string','minLength':1,'maxLength':4096}
    rational=deepcopy(p['other_inventory'])
    fields={'event_id':text,'date':p['date'],'lot_id':text,'balances':p['balances'],'flows':p['flows']}
    if kind=='settle':
        fields.update(component_id=text,units=rational,carrying=rational,tax_adjustment=rational)
    input_shape=record(fields)
    operations=[]
    def add(kind,path,value):
        operations.append({'id':'op.'+str(len(operations)),'op':kind,'path':path,'value':value})
    lot=['lots',{'input_pointer':'/lot_id'}]
    if kind=='settle':
        for key in ['refund','recovery']:add('replace',['component',key],literal('0/1'))
        add('replace',['component','settled'],literal(True))
        add('insert',lot,obj({'id':read('/lot_id'),'component_id':read('/component_id'),
            'units':read('/units'),'carrying':read('/carrying'),'tax_base':read('/carrying'),
            'acquired':read('/date'),'disposed':literal(False)}))
        add('append',['tax_adjustments'],obj({'event_id':read('/event_id'),'date':read('/date'),
                                            'amount':read('/tax_adjustment')}))
    elif kind=='sell':
        for key in ['units','carrying','tax_base']:add('replace',lot+[key],literal('0/1'))
        add('replace',lot+['disposed'],literal(True))
    else:raise ValueError('unsupported test method')
    add('replace',['balances'],read('/balances'))
    add('replace',['date'],read('/date'))
    add('append',['seen'],read('/event_id'))
    for i in range(2 if kind=='settle' else 1):add('append',['flows'],read('/flows/'+str(i)))
    h,k=core.digest(state),core.digest(input_shape)
    return {'profile':memory.PROFILE,'state_schema':h,'input_schema':k,'operations':operations},{h:state,k:input_shape}


def inputs_for(state,event,derived):
    # Explicit harness arithmetic; complete bound transition remains a later layer.
    balances={k:monetary.effects.fmt(Q(v)+Q(derived['journal'][k])) for k,v in state['balances'].items()}
    flows=[{'entity':state['context']['entity'],'activity':f['activity'],'origin':f['origin'],
            'amount':f['amount'],'date':event['date'],'event_id':event['id']} for f in derived['flows']]
    inputs={'event_id':event['id'],'date':event['date'],'lot_id':event['lot_id'],'balances':balances,'flows':flows}
    if event['kind']=='settle':
        amounts={x['id']:x['binding']['value'] for x in derived['diagnostics']['calculations']}
        inputs.update(component_id=state['component']['id'],units=event['actual_units'],
                      carrying=amounts['carrying'],tax_adjustment=amounts['tax_adjustment'])
    return inputs


def comparisons():
    rows=[]
    for name,state,event in monetary.selected_cases():
        original=deepcopy((state,event))
        context={'entity':state['context']['entity'],'book_role':'retained-conditional-example','at':event['date']}
        amounts=monetary.run(monetary.program(event['kind'],context,structure.native.ACCOUNTS),monetary.project(state,event))
        if amounts['status']!='derived':
            rows.append({'case':name,'status':'unresolved_before_staging','passed':amounts['status']=='unresolved',
                         'monetary_result':amounts,'staged':False})
            continue
        definition,schemas=program(event['kind']);inputs=inputs_for(state,event,amounts)
        h=core.digest(definition);result=memory.stage({h:definition},h,schemas,state,inputs)
        after,journal,flows=structure.native.transition(state,event)
        rows.append({'case':name,'definition':definition,'schemas':schemas,'inputs':inputs,'result':result,
                     'before_sha256':core.digest(state),'event_sha256':core.digest(event),
                     'native_after_sha256':core.digest(after),'passed':result.get('after')==after and (state,event)==original,
                     'staged':True,'provenance':'constructed memory inputs from recorded monetary interpreter plus explicit test-harness balance addition'})
    return rows
