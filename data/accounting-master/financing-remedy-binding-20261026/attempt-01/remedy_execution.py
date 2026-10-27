"""Record resolved conditional findings with unchanged generic typed transitions."""
from copy import deepcopy
import typed_conditions as t
import declared_financing_methods_v1 as h
core=t.core;engine=t.engine
PROFILE='SelectedConditionalRemedy/1'
TEXT={'kind':'text','context':{}}
FIELDS=['series','clause_status','clause_date','acceleration_status','last_action','evidence_digest']
FLAGS=dict(source_admission=False,accounting_admission=False,production_ready=False,durable=False)

def extended_state(book,schemas,initial,provenance):
    """Explicit supplied schema extension, never inferred legal state."""
    core.closed(initial,FIELDS,'supplied_initial_contract_memory');engine.text(provenance,'initial_provenance')
    for value in initial.values():engine.text(value,'initial_contract_value')
    core.need(initial['clause_status'] in ('unknown','satisfied','not_satisfied'),'initial_clause_status')
    core.need(initial['acceleration_status'] in ('unknown','satisfied','not_satisfied'),'initial_acceleration_status')
    after=deepcopy(book);ss=deepcopy(schemas);shape=deepcopy(ss[book['memory_schema']])
    core.need('contract_status' not in shape['properties'],'existing_contract_memory')
    shape['properties']['contract_status']=h.record({n:h.scalar('text') for n in FIELDS})
    shape['required'].append('contract_status');key=core.digest(shape);ss[key]=shape
    after['memory']['contract_status']=deepcopy(initial);after['memory_schema']=key
    after['memory_types'].update({'/contract_status/'+n:deepcopy(TEXT) for n in FIELDS})
    engine.validate_book(after,ss)
    return after,ss,dict(before_sha256=core.digest(book),after_sha256=core.digest(after),supplied_initial=initial,provenance=provenance,**FLAGS)

def make_selection(book,schemas,series):
    return dict(profile=PROFILE,context=deepcopy(book['context']),series=series,memory_schema=book['memory_schema'],
      memory_types=deepcopy(book['memory_types']),schemas_sha256=core.digest(schemas),
      routes=['event_clause','new_acceleration','after_rescission'],
      principal_pointer='/debt_terms/outstanding',
      scope=t.SCOPE+'; recording conditional status only; economic effects remain separate')

def make_call(selection,book,event,schemas,reviewed):
    return dict(profile=PROFILE,selection_sha256=core.digest(selection),book_sha256=core.digest(book),
                event_sha256=core.digest(event),schemas_sha256=core.digest(schemas),reviewed=reviewed)

def method(book,schemas,writes):
    identity='conditional.remedy.record';money=engine.money_type(book);true=t.const(core.BOOL,True)
    rows=[('record_resolved_condition',true,[],'invalid')]
    condition=dict(manifest=h.conditions(identity,{},rows),bindings={})
    # Empty numerical inputs and zero cash posting preserve monetary state.
    numerical=dict(profile=engine.monetary.PROFILE,method_id=identity,version='1',inputs={},calculations=[],
      accounts={'cash':money},cash_account='cash',postings=[dict(id='cash',account='cash',expression=t.const(money,'0/1'),requires=[])],flows=[])
    empty=h.record({});ss=deepcopy(schemas);ss[core.digest(empty)]=empty
    definition=dict(profile=engine.METHOD,id=identity,version='1',context=deepcopy(book['context']),
      account_map={'cash':book['cash_account']},preconditions=deepcopy(condition),postconditions=deepcopy(condition),
      monetary=dict(definition=numerical,bindings={}),memory=dict(definition=dict(profile=engine.memory.PROFILE,
        state_schema=book['memory_schema'],input_schema=core.digest(empty),
        operations=[dict(id='write.'+n,op='replace',path=['contract_status',n],value=dict(kind='literal',value=value)) for n,value in writes.items()]),
        input_bindings={}),residual_prerequisites=[t.SCOPE])
    return definition,ss

def execute(selection,book,event,schemas,reviewed,call):
    stage='selection';result=dict(profile=PROFILE,**FLAGS)
    try:
        core.need(call==make_call(selection,book,event,schemas,reviewed),'stale_remedy_call')
        core.need(reviewed==core.digest(selection),'independent_remedy_selection')
        core.need(selection['profile']==PROFILE,'selection_profile')
        engine.validate_book(book,schemas)
        core.need(book['context']==selection['context'],'selected_context')
        core.need(book['memory_schema']==selection['memory_schema'] and book['memory_types']==selection['memory_types'],'selected_memory')
        core.need(core.digest(schemas)==selection['schemas_sha256'],'selected_schemas')
        core.closed(event,['id','date','series','method','facts','provenance'],'remedy_event')
        engine.text(event['provenance'],'event_provenance')
        core.need(event['series']==selection['series']==book['memory']['contract_status']['series'],'selected_series')
        core.need(event['method'] in selection['routes'],'selected_route')
        stage='conditional_facts';facts=event['facts'];status=book['memory']['contract_status']
        core.need(type(facts) is dict,'facts_record')
        if event['method']=='event_clause' and facts.get('kind')=='principal':
            found,remaining=engine.binding.located(book['memory'],selection['principal_pointer'])
            core.need(found,'selected_principal_leaf');money=engine.money_type(book)
            core.need(book['memory_types'][selection['principal_pointer']]==money,'principal_money_type')
            unpaid=facts.get('unpaid');core.need(unpaid is None or type(unpaid) is bool,'unpaid_boolean')
            inputs={'remaining':h.declaration(money,'remaining'),'unpaid':h.declaration(core.BOOL,'unpaid')}
            inputs['unpaid']['role']='caller_finding'
            manifest=h.conditions('conditional.principal.binding',{'remaining':money,'unpaid':core.BOOL},[
              ('unpaid_matches_claim',t.op('eq',dict(op='ref',id='unpaid'),
                 t.op('lt',t.const(money,'0/1'),dict(op='ref',id='remaining'))),['remaining','unpaid'],'invalid')])
            manifest['inputs']=inputs;key=core.digest(manifest)
            binding=t.guarded.assess({key:manifest},key,dict(remaining=engine.known(remaining),
               unpaid=engine.known(unpaid) if unpaid is not None else dict(status='unknown',reason='Unpaid finding missing')),[])
            result['principal_binding']=binding
            if binding['status']!='requirements_satisfied':return dict(result,status=binding['status'],failed_stage='principal_binding')
        if event['method']=='new_acceleration':
            if status['clause_status']=='unknown' or status['clause_date']!=event['date']:
                return dict(result,status='unresolved',failed_stage='current_clause_binding',reason='same_date_clause_finding_required')
            supplied=facts.get('event_occurs_and_continues')
            if supplied is None:return dict(result,status='unresolved',failed_stage='current_clause_binding',reason='continuing_event_finding_required')
            core.need(type(supplied) is bool and supplied is (status['clause_status']=='satisfied'),'continuing_event_binding')
        if event['method']=='after_rescission':
            old={'satisfied':True,'not_satisfied':False,'unknown':None}[status['acceleration_status']]
            core.need(facts.get('existing_acceleration') is old,'existing_acceleration_binding')
        finding=t.assess(event['method'],facts);result['finding']=finding
        if finding['status'] not in ('satisfied','not_satisfied'):
            return dict(result,status=finding['status'],failed_stage=stage)
        writes=dict(last_action=event['method'],evidence_digest=core.digest(event))
        if event['method']=='event_clause':writes.update(clause_status=finding['status'],clause_date=event['date'])
        elif event['method']=='after_rescission':writes['acceleration_status']=finding['status']
        elif finding['status']=='satisfied':writes['acceleration_status']='satisfied'
        # An unsatisfied new trigger does not revoke an existing acceleration.
        stage='typed_transition';definition,ss=method(book,schemas,writes)
        request=dict(profile=engine.PROFILE,expected_state_sha256=core.digest(book),expected_method_sha256=core.digest(definition),
                     method=definition,event=dict(id=event['id'],date=event['date'],inputs={}),schemas=ss)
        proposed=engine.propose(book,request);result.update(request=request,transition=proposed)
        if proposed['status']!='proposed':return dict(result,status=proposed['status'],failed_stage=stage)
        stage='economic_frame';after=proposed['after']
        core.need(after['balances']==book['balances'] and after['flows']==book['flows'],'no_economic_effect')
        for n in book['memory']:
            if n!='contract_status':core.need(after['memory'][n]==book['memory'][n],'economic_history_preserved:'+n)
        core.need(after['memory']['contract_status']['series']==status['series'],'series_preserved')
        return dict(result,status='proposed_conditional_status',failed_stage=None,after=after,selected_event=deepcopy(event))
    except (ValueError,KeyError,TypeError,RecursionError,OverflowError) as exc:
        return dict(result,status='invalid',reason=str(exc)[:300],failed_stage=stage)
