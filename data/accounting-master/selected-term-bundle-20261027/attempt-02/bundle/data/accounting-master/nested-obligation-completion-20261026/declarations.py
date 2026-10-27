"""Explicit financial predicates; generic evaluators contain no such policy."""
from copy import deepcopy
from pathlib import Path
import importlib.util,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'nested-query-template-20261026'))
import template as t
module_spec=importlib.util.spec_from_file_location('nested_template_reference',HERE.parent/'nested-query-template-20261026/fixtures.py')
f=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(f)
import collections_bridge as bridge
g=f.g;p=f.p;core=f.core

def term_declaration(state,owner,key):
    claim=state['book']['memory']['claims'][owner];term=claim['terms'][key]
    queries={'self':g.query_item(state,'terms',owner,'match','effective',value=term['effective'],allow_empty=False),
             'previous':g.query_item(state,'terms',owner,'greatest','effective',bound=term['effective'],inclusive=False)}
    bindings={'has_previous':dict(kind='has_row',query='previous'),
      'previous_id':dict(kind='selected_field',query='previous',field='identity')}
    for field in ('identity','predecessor','effective','due'):bindings[field]=dict(kind='selected_field',query='self',field=field)
    rules=[g.rule('unique_effective_identity',g.binary('eq',g.ref('identity'),g.const(p.guards.TEXT,key)),['identity']),
      g.rule('predecessor_chain',g.binary('eq',g.ref('predecessor'),g.ref('previous_id')),['predecessor','previous_id'],g.ref('has_previous'),['has_previous']),
      g.rule('initial_sentinel',g.binary('eq',g.ref('predecessor'),g.const(p.guards.TEXT,'none')),['predecessor'],
         {'op':'not','arg':g.ref('has_previous')},['has_previous']),
      g.rule('issued_before_effective',g.binary('le',g.const(p.guards.DATE,claim['issued']),g.ref('effective')),['effective']),
      g.rule('effective_by_book',g.binary('le',g.ref('effective'),g.const(p.guards.DATE,state['book']['date'])),['effective']),
      g.rule('effective_before_due',g.binary('le',g.ref('effective'),g.ref('due')),['effective','due'])]
    return g.assemble(state,queries,bindings,rules)

def term_template(state,owner='invoice/a~1',key='initial'):
    d=term_declaration(state,owner,key)
    captures={'key':dict(kind='child_key',type=p.guards.TEXT),
      'effective':dict(kind='child_field',pointer='/effective',type=p.guards.DATE),
      'issued':dict(kind='parent_field',pointer='/issued',type=p.guards.DATE),
      'now':dict(kind='book_field',pointer='/date',type=p.guards.DATE)}
    slots=[dict(kind='group',query=name) for name in d['queries']]
    for capture,target in [('key','/manifest/requirements/0/predicate/right/value'),
      ('effective','/queries/self/query/value/binding/value'),('effective','/queries/previous/query/upper_bound/binding/value'),
      ('issued','/manifest/requirements/3/predicate/left/value'),('now','/manifest/requirements/4/predicate/right/value')]:
        slots.append(dict(kind='scalar',capture=capture,target=target))
    return dict(profile=t.PROFILE,context=deepcopy(state['book']['context']),iteration=f.f.spec_for(state,'terms'),
       mode='rows',captures=captures,template=d,slots=slots,residuals=['Explicit term dates and chain; event membership and structural premises separate'])

def assessment_declaration(state,owner,key):
    d=f.row_declaration(state,owner,key);row=state['book']['memory']['claims'][owner]['assessments'][key]
    d['queries']['unique_date']=g.query_item(state,'assessments',owner,'match','as_of',value=row['as_of'],allow_empty=False)
    for name,query,field in [('unique_id','unique_date','identity'),('self_id','assessment','identity'),
                           ('origin','assessment','origin'),('event','assessment','event_id')]:
        d['bindings'][name]=dict(kind='selected_field',query=query,field=field)
        typ=d['queries'][query]['projection']['fields'][field]['type']
        d['manifest']['inputs'][name]=dict(type=deepcopy(typ),role='state',source_ref='explicit query binding:'+name)
    money=p.base.money_type(state['book']);imported=g.binary('eq',g.ref('origin'),g.const(p.guards.TEXT,'imported_snapshot'))
    recorded=g.binary('eq',g.ref('origin'),g.const(p.guards.TEXT,'recorded_event'))
    d['manifest']['requirements'].extend([
      g.rule('unique_assessment_date',g.binary('eq',g.ref('unique_id'),g.ref('self_id')),['unique_id','self_id']),
      g.rule('assessed_remaining_nonnegative',g.binary('le',g.const(money,'0/1'),g.ref('remaining')),['remaining']),
      g.rule('supported_origin',{'op':'any','args':[imported,recorded]},['origin']),
      g.rule('imported_event_unknown',g.binary('eq',g.ref('event'),g.const(p.guards.TEXT,'unknown')),['event'],deepcopy(imported),['origin'])])
    return d

def assessment_template(state,owner='invoice/a~1',key='imported'):
    s=f.row_spec(state,owner,key);s['template']=assessment_declaration(state,owner,key)
    s['slots'].append(dict(kind='group',query='unique_date'))
    s['slots'].append(dict(kind='scalar',capture='at',target='/queries/unique_date/query/value/binding/value'))
    return s

def event_collections(state):
    terms=f.f.spec_for(state,'terms');assessments=f.f.spec_for(state,'assessments')
    decl=lambda typ:dict(type=deepcopy(typ),role='state',source_ref='explicit supplied event membership')
    definition=dict(profile=bridge.engine.PROFILE,method_id='term.event.membership',version='1',inputs={},
      collections={name:dict(fields={'id':decl(p.guards.TEXT)}) for name in ('terms','recorded','seen')},
      constraints=[dict(id='term_events_seen',op='references',source='terms',field='id',target='seen',target_field='id'),
                   dict(id='recorded_events_seen',op='references',source='recorded',field='id',target='seen',target_field='id')],
      residual_prerequisites=['Supplied event membership; source completeness separate'])
    return dict(profile=bridge.PROFILE,context=deepcopy(state['book']['context']),definition=definition,
      sources=dict(terms=terms,assessments=assessments),
      bindings={'terms':dict(kind='projected',source='terms',fields={'id':'event_id'},filter=None),
       'recorded':dict(kind='projected',source='assessments',fields={'id':'event_id'},
          filter=dict(field='origin',type=p.guards.TEXT,value='recorded_event')),
       'seen':dict(kind='seen',fields={'id':'value'})},residuals=['Imported origin/event predicates are declared separately'])

def run_bridge(state,spec,coverages=None,selection=None,call=None):
    coverages={name:p.population(s,state['book'],'complete','Supplied event-membership source') for name,s in spec['sources'].items()} if coverages is None else coverages
    selection=core.digest(spec) if selection is None else selection
    args=(spec,state['book'],state['memory_definition'],state['schemas'],coverages,selection)
    return bridge.assess(*args,bridge.make_call(*args) if call is None else call)
