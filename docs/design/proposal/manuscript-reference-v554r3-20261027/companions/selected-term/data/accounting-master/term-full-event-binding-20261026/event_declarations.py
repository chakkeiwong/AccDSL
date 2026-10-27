"""Explicit amendment rules and reused selected assessment/collection rules."""
from copy import deepcopy
from pathlib import Path
import importlib.util,json
import full_composition as m
HERE=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);return x
a=load('assessment_declaration_for_terms',HERE.parent/'nested-assessment-construction-20261026/declaration.py')
c=m.expander.c;TEXT=c.TEXT;DATE=c.DATE;BOOL=a.BOOL
def read(path):return json.loads(path.read_text())
def literal(x):return {'node':'literal','value':x}
def parameter(x):return {'node':'parameter','name':x}
def object_node(fields):return {'node':'object','fields':fields}
def array_node(items):return {'node':'array','items':items}
def value_node(param):return object_node({'kind':literal('literal'),'value':parameter(param)})

def amendment_construction(state):
    base=deepcopy(a.build(state)['base_template']);tree=base['method_template']['fields']
    base['parameters']=[p for p in base['parameters'] if p['name']!='end_exclusive']
    for name,typ,source in [
      ('claim_id',TEXT,dict(kind='event_input',name='claim_id')),
      ('term_id',TEXT,dict(kind='event_input',name='term_id')),
      ('due',DATE,dict(kind='event_input',name='due')),
      ('day',DATE,dict(kind='event_metadata',field='date')),
      ('event_id',TEXT,dict(kind='event_metadata',field='id')),
      ('prior_term',TEXT,dict(kind='event_input',name='prior_term')),
      ('premise',TEXT,dict(kind='event_input',name='premise')),
      ('due_pointer',TEXT,dict(kind='pointer',segments=[{'literal':'claims'},{'parameter':'claim_id'},{'literal':'due'}])),
    ]:base['parameters'].append(dict(name=name,type=deepcopy(typ),source=source))
    post=tree['postconditions']['fields'];post['bindings']['fields']['written_date']['fields']['pointer']=parameter('due_pointer')
    post['manifest']['fields']['requirements']['items'][0]['fields']['predicate']['fields']['right']['fields']['value']=parameter('due')
    def operation(index,op,path,value):
        return object_node(dict(id=literal('term.'+str(index)),op=literal(op),path=array_node(path),value=value))
    prefix=[literal('claims'),parameter('claim_id')]
    term=object_node(dict(kind=literal('object'),fields=object_node({k:value_node(v) for k,v in
      [('due','due'),('effective','day'),('event_id','event_id'),('predecessor','prior_term'),('premise','premise')]})))
    operations=[operation(0,'insert',prefix+[literal('terms'),parameter('term_id')],term),
      operation(1,'replace',prefix+[literal('current_term')],value_node('term_id')),
      operation(2,'replace',prefix+[literal('due')],value_node('due'))]
    tree['memory']['fields']['definition']['fields']['operations']=array_node(operations)
    base['residuals']=['Explicit prospective term insertion; selected eligibility and snapshot checks are separate']
    return base

def stage(name,bindings,types,predicate,reason):
    manifest=dict(profile='MethodRequirements/3',method_id='term.eligibility.'+name,version='1',
      inputs={key:dict(type=deepcopy(typ),role='state',source_ref='Explicit term-event eligibility:'+key) for key,typ in types.items()},
      requirements=[dict(id=name,guard=dict(op='const',type=deepcopy(BOOL),value=True),guard_requires=[],predicate=predicate,
        requires=list(types),admission_refs=[],on_false='invalid',on_unknown='unresolved')],
      required_known=[],capabilities=[],residual_prerequisites=['Synthetic supplied prospective term only'])
    return dict(id=name,manifest=manifest,bindings=bindings,reason=reason)

def amendment_eligibility(collect):
    gate=deepcopy(collect);gate['profile']=m.gate.PROFILE;gate['operation']='amend'
    gate['input_types']={k:deepcopy(v) for k,v in [('approved',BOOL),('claim_id',TEXT),('customer',TEXT),('prior_term',TEXT),('term_id',TEXT),('due',DATE),('premise',TEXT)]}
    gate['stages']=gate['stages'][:4]
    event=lambda name:dict(kind='event_input',name=name)
    ref=lambda name:dict(op='ref',id=name)
    binary=lambda op,l,r:dict(op=op,left=ref(l),right=ref(r))
    field=lambda name:dict(kind='map_field',pointer='/claims',key_input='claim_id',field=name,after_stage='claim_exists')
    child=lambda name:dict(kind='nested_map_contains',pointer='/claims',key_input='claim_id',parent_after_stage='claim_exists',child_pointer='/terms',child_key_input=name)
    gate['stages'].append(stage('prior_matches',dict(prior=event('prior_term'),current=field('current_term')),dict(prior=TEXT,current=TEXT),binary('eq','prior','current'),'stale_current_term'))
    gate['stages'].append(stage('term_nonblank',dict(valid=dict(kind='text_nonblank',value=event('term_id'))),dict(valid=BOOL),ref('valid'),'term_id'))
    gate['stages'].append(stage('new_term',dict(exists=child('term_id')),dict(exists=BOOL),dict(op='not',arg=ref('exists')),'duplicate_term_id'))
    gate['stages'].append(stage('term_not_sentinel',dict(term=event('term_id')),dict(term=TEXT),dict(op='not',arg=dict(op='eq',left=ref('term'),right=dict(op='const',type=TEXT,value='none'))),'duplicate_term_id'))
    gate['stages'].append(stage('premise_nonblank',dict(valid=dict(kind='text_nonblank',value=event('premise'))),dict(valid=BOOL),ref('valid'),'term_premise'))
    gate['stages'].append(stage('due_after_effective',dict(day=dict(kind='event_metadata',field='date'),due=event('due')),dict(day=DATE,due=DATE),binary('le','day','due'),'due_before_effective'))
    gate['stages'].append(stage('prior_exists',dict(exists=child('prior_term')),dict(exists=BOOL),ref('exists'),'missing_prior_term'))
    previous=child('prior_term');previous.update(kind='nested_map_field',field='effective',after_stage='prior_exists')
    gate['stages'].append(stage('strict_effective',dict(previous=previous,day=dict(kind='event_metadata',field='date')),dict(previous=DATE,day=DATE),binary('lt','previous','day'),'ambiguous_term_effective_date'))
    gate['residuals']=['Explicit prospective term eligibility; no modification accounting admission']
    return gate

def build(chart,state):
    rules=read(HERE.parent/'term-event-carry-binding-20261026/attempt-01/rules.json')[chart]
    collect=read(HERE.parent/'ordered-event-eligibility-20261026/templates'/(chart+'.collect.json'))
    rules['assessment']['eligibility']['profile']=m.gate.PROFILE
    rules['amendment']=dict(eligibility=amendment_eligibility(collect),construction=amendment_construction(state))
    collect['profile']=m.gate.PROFILE
    rules['collection']=dict(eligibility=collect,construction=read(HERE.parent/'parameterized-method-construction-20261026/templates'/(chart+'.collect.json')))
    return rules
