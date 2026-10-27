"""Explicit assessment declaration from inspected rules, not oracle requests."""
from copy import deepcopy
import nested_expander as e
c=e.c
BOOL={'kind':'boolean','context':{}}
TEXT=c.TEXT;DATE=c.DATE
IDENTITY='synthetic.receivable.term-history'

def literal(v,typ=TEXT):return dict(expr='literal',type=deepcopy(typ),value=v)
def obj(**fields):return dict(expr='object',fields=fields)
def array(*items):return dict(expr='array',items=list(items))
def row(name):return dict(expr='row',field=name)
def event(name):return dict(expr='event_metadata',field=name)
def wrap(v):return obj(kind=literal('literal'),value=v)
def write(op,path,value):
    return obj(id=dict(expr='operation_id',prefix='term.'),op=literal(op),path=array(*path),value=value)

def manifest(name,typ,predicate,reason):
    return dict(profile='MethodRequirements/3',method_id=IDENTITY,version='1',
      inputs={name:dict(type=deepcopy(typ),role='state',source_ref='declared-operating-premise:'+name)},
      requirements=[dict(id=reason,guard=dict(op='const',type=deepcopy(BOOL),value=True),guard_requires=[],
        predicate=predicate,requires=[name],admission_refs=[],on_false='unsupported' if name=='approved' else 'invalid',on_unknown='unresolved')],
      required_known=[],capabilities=[],residual_prerequisites=['Supplied synthetic term premise; no modification accounting admission'])

def build(state):
    book=state['book'];money=c.base.money_type(book)
    pre=manifest('approved',BOOL,dict(op='ref',id='approved'),'approved')
    post=manifest('written_date',DATE,dict(op='eq',left=dict(op='ref',id='written_date'),
      right=dict(op='const',type=deepcopy(DATE),value='2000-01-01')),'date_written')
    method=dict(profile='CompanyBookMethod/1',id=IDENTITY,version='1',context=deepcopy(book['context']),
      account_map={k:state['roles'][k] for k in ['cash','receivables']},
      preconditions=dict(manifest=pre,bindings={'approved':dict(kind='event',name='approved')}),
      postconditions=dict(manifest=post,bindings={'written_date':dict(kind='memory',pointer='/collection_clock/cursor')}),
      monetary=dict(definition=dict(profile='MethodMonetaryEffects/1',method_id=IDENTITY,version='1',inputs={},calculations=[],
        accounts={k:deepcopy(money) for k in ['cash','receivables']},cash_account='cash',postings=[],flows=[]),bindings={}),
      memory=dict(definition=dict(profile='MethodMemoryEffects/1',state_schema='',input_schema='',operations=[]),input_bindings={}),
      residual_prerequisites=['Date-only prospective terms under supplied assumptions; no modification gain/loss, interest or impairment'])
    tree=e.encode(method);fields=tree['fields']['memory']['fields']['definition']['fields']
    fields['state_schema']={'node':'parameter','name':'state_schema'}
    fields['input_schema']={'node':'parameter','name':'input_schema'}
    pred=tree['fields']['postconditions']['fields']['manifest']['fields']['requirements']['items'][0]['fields']['predicate']['fields']
    pred['right']['fields']['value']={'node':'parameter','name':'end_exclusive'}
    base=dict(profile=c.PROFILE,transition_profile=c.frontend.v2.PROFILE,context=deepcopy(book['context']),
      parameters=[dict(name='state_schema',type=TEXT,source=dict(kind='book_metadata',field='memory_schema')),
        dict(name='input_schema',type=TEXT,source=dict(kind='input_schema')),
        dict(name='end_exclusive',type=DATE,source=dict(kind='event_input',name='end_exclusive'))],
      method_template=tree,input_schema_definition=dict(profile=c.types.PROFILE,root=dict(node='record',fields={})),
      residuals=['Explicit bounded term assessment construction; event eligibility is separate'])
    overdue=dict(expr='if',condition=dict(expr='date_lt',left=row('due'),right=event('date')),
      then=row('remaining'),**{'else':literal('0/1',money)})
    values=dict(term_id=row('current_term'),as_of=event('date'),remaining=row('remaining'),overdue=overdue,
      origin=literal('recorded_event'),event_id=event('id'))
    prefix=[literal('claims'),dict(expr='key')]
    operations=[write('insert',prefix+[literal('assessments'),event('id')],
      obj(kind=literal('object'),fields=obj(**{k:wrap(v) for k,v in values.items()})))]
    for name,value in dict(latest_assessment=event('id'),assessed=literal(True,BOOL),assessment_date=event('date'),
      assessed_remaining=row('remaining'),overdue=overdue).items():
        operations.append(write('replace',prefix+[literal(name)],wrap(value)))
    suffix=[write('replace',[literal('collection_clock'),literal('cursor')],
      wrap(dict(expr='event_input',name='end_exclusive',type=DATE)))]
    return dict(profile=e.PROFILE,base_template=base,map_pointer='/claims',
      row_definition=deepcopy(state['memory_definition']['root']['fields']['claims']['values']),
      row_operations=operations,suffix_operations=suffix,
      residuals=['Exact supplied claim order; no eligibility or accounting admission'])
