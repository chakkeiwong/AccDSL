from copy import deepcopy
import importlib.util
import template as t
spec=importlib.util.spec_from_file_location('query_guard_reference',t.HERE.parent/'query-guard-composition-20261026/fixtures.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
f=g.f;p=t.p;core=t.core

def row_declaration(state,owner,key):
    d=g.history_spec(state,owner,key);claim=state['book']['memory']['claims'][owner]
    d['manifest']['requirements'].extend([
       g.rule('issued_before_assessment',g.binary('le',g.const(p.guards.DATE,claim['issued']),g.ref('as_of')),['as_of']),
       g.rule('assessment_by_book',g.binary('le',g.ref('as_of'),g.const(p.guards.DATE,state['book']['date'])),['as_of']),
       g.rule('assessment_before_cursor',g.binary('lt',g.ref('as_of'),g.const(p.guards.DATE,state['book']['memory']['collection_clock']['cursor'])),['as_of'])])
    return d

def row_spec(state,owner='invoice/a~1',key='imported'):
    d=row_declaration(state,owner,key)
    captures={'identity':dict(kind='child_key',type=p.guards.TEXT),
      'at':dict(kind='child_field',pointer='/as_of',type=p.guards.DATE),
      'issued':dict(kind='parent_field',pointer='/issued',type=p.guards.DATE),
      'now':dict(kind='book_field',pointer='/date',type=p.guards.DATE),
      'cursor':dict(kind='book_field',pointer='/memory/collection_clock/cursor',type=p.guards.DATE)}
    slots=[dict(kind='group',query=name) for name in d['queries']]
    for capture,target in [('identity','/queries/assessment/query/value/binding/value'),
       ('at','/queries/term/query/upper_bound/binding/value'),
       ('issued','/manifest/requirements/5/predicate/left/value'),
       ('now','/manifest/requirements/6/predicate/right/value'),
       ('cursor','/manifest/requirements/7/predicate/right/value')]:
        slots.append(dict(kind='scalar',capture=capture,target=target))
    return dict(profile=t.PROFILE,context=deepcopy(state['book']['context']),iteration=f.spec_for(state,'assessments'),
      mode='rows',captures=captures,template=d,slots=slots,residuals=['Explicit assessment relation template; remaining native obligations separate'])

def group_declaration(state,owner):
    row=state['book']['memory']['claims'][owner];money=p.base.money_type(state['book'])
    queries={'current':g.query_item(state,'terms',owner,'greatest','effective',allow_empty=False),
             'latest':g.query_item(state,'assessments',owner,'greatest','as_of'),
             'count':g.query_item(state,'assessments',owner,'count')}
    bindings={'has_latest':dict(kind='has_row',query='latest'),'count':dict(kind='count',query='count')}
    for name,query,field in [('term_id','current','identity'),('due','current','due'),
       ('latest_id','latest','identity'),('as_of','latest','as_of'),('remaining','latest','remaining'),('overdue','latest','overdue'),
       ('owner','current','owner')]:bindings[name]=dict(kind='selected_field',query=query,field=field)
    rules=[g.rule('current_term',g.binary('eq',g.ref('term_id'),g.const(p.guards.TEXT,row['current_term'])),['term_id']),
      g.rule('current_due',g.binary('eq',g.ref('due'),g.const(p.guards.DATE,row['due'])),['due']),
      g.rule('assessed_flag',g.binary('eq',g.ref('has_latest'),g.const(core.BOOL,row['assessed'])),['has_latest']),
      g.rule('count_presence',g.binary('eq',g.binary('lt',g.const(t.c.COUNT_TYPE,'0/1'),g.ref('count')),g.ref('has_latest')),['count','has_latest'])]
    for name,field,typ in [('latest_id','latest_assessment',p.guards.TEXT),('as_of','assessment_date',p.guards.DATE),
      ('remaining','assessed_remaining',money),('overdue','overdue',money)]:
        rules.append(g.rule('summary_'+field,g.binary('eq',g.ref(name),g.const(typ,row[field])),[name],g.ref('has_latest'),['has_latest']))
    for field,typ,expected in [('latest_assessment',p.guards.TEXT,'none'),('assessed_remaining',money,'0/1'),('overdue',money,'0/1')]:
        rules.append(g.rule('empty_'+field,g.binary('eq',g.const(typ,row[field]),g.const(typ,expected)),[],
          {'op':'not','arg':g.ref('has_latest')},['has_latest']))
    rules.append(g.rule('owner',g.binary('eq',g.ref('owner'),g.const(p.guards.TEXT,owner)),['owner']))
    return g.assemble(state,queries,bindings,rules)

def group_spec(state,owner='invoice/a~1'):
    d=group_declaration(state,owner);parent=state['memory_definition']['root']['fields']['claims']['values']['fields']
    captures={field:dict(kind='parent_field',pointer='/'+field,type=deepcopy(parent[field]['type']))
      for field in ('current_term','due','assessed','latest_assessment','assessment_date','assessed_remaining','overdue')}
    captures['owner']=dict(kind='parent_key',type=p.guards.TEXT)
    slots=[dict(kind='group',query=name) for name in d['queries']]
    for field,row,side in [('current_term',0,'right'),('due',1,'right'),('assessed',2,'right'),
      ('latest_assessment',4,'right'),('assessment_date',5,'right'),('assessed_remaining',6,'right'),('overdue',7,'right'),
      ('latest_assessment',8,'left'),('assessed_remaining',9,'left'),('overdue',10,'left'),('owner',11,'right')]:
        slots.append(dict(kind='scalar',capture=field,target='/manifest/requirements/'+str(row)+'/predicate/'+side+'/value'))
    return dict(profile=t.PROFILE,context=deepcopy(state['book']['context']),iteration=f.spec_for(state,'assessments'),
      mode='groups',captures=captures,template=d,slots=slots,residuals=['Explicit per-parent summaries; full term-state validator separate'])

def run(state,spec,coverage=None,query_coverages=None,selection=None,call=None):
    coverage=p.population(spec['iteration'],state['book'],'complete','Supplied iteration fixture') if coverage is None else coverage
    query_coverages={name:p.population(item['projection'],state['book'],'complete','Supplied query fixture') for name,item in spec['template']['queries'].items()} if query_coverages is None else query_coverages
    selection=core.digest(spec) if selection is None else selection
    args=(spec,state['book'],state['memory_definition'],state['schemas'],coverage,query_coverages,selection)
    return t.evaluate(*args,t.make_call(*args) if call is None else call)

def original_captures(state,spec,owner,childkey):
    parent=state['book']['memory']['claims'][owner];kind=spec['iteration']['child_pointer'][1:]
    path='/memory'+f.pointer(['claims',owner]);child=parent[kind].get(childkey) if childkey is not None else None
    found={}
    for name,b in spec['captures'].items():
        k=b['kind']
        if k=='parent_key':value=owner;source=path
        elif k=='child_key':value=childkey;source=path+'/'+kind+f.pointer([childkey])
        elif k=='parent_field':value=parent[b['pointer'][1:]];source=path+b['pointer']
        elif k=='child_field':value=child[b['pointer'][1:]];source=path+'/'+kind+f.pointer([childkey])+b['pointer']
        elif b['pointer']=='/date':value=state['book']['date'];source='/date'
        else:value=state['book']['memory']['collection_clock']['cursor'];source='/memory/collection_clock/cursor'
        found[name]=dict(value=deepcopy(value),type=deepcopy(b['type']),kind=k,path=source)
    return found
