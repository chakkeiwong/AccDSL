from copy import deepcopy
import fixtures as f
t=f.t;p=f.p;core=f.core
def exercise(base,check,compare,records):
    spec=f.row_spec(base);owner='invoice/a~1'
    def refuse(label,s=spec,state=base,status='invalid',reason='',**kwargs):
        result=f.run(state,s,**kwargs)
        check(result['status']==status and reason in result.get('reason',''),label+':reason:'+result.get('reason',''))
        check('instances' not in result,label+':no_partial_instance_output')
        records.append(dict(case=label,result=result));return result
    def paired(label,state,s,mode,status=None):
        result=compare(label,state,s,mode)
        if status:check(result['status']==status,label+':status')
        records.append(dict(case=label,result=result));return result
    empty=deepcopy(base);empty['book']['memory']['claims']={};f.f.configure(empty)
    paired('empty_parent_map',empty,spec,'rows','no_active_requirements')
    childempty=deepcopy(base);claim=childempty['book']['memory']['claims'][owner]
    claim['assessments']={};claim.update(assessed=False,latest_assessment='none',assessed_remaining='0/1',overdue='0/1')
    f.f.configure(childempty)
    paired('empty_child_rows',childempty,spec,'rows','no_active_requirements')
    result=paired('empty_child_group',childempty,f.group_spec(base),'groups','requirements_satisfied')
    check(result['instance_count']==1,'empty_group_still_instantiated')
    for label,change,reason in [
      ('wrong_capture_type',lambda s:s['captures']['at'].update(type=p.guards.TEXT),'capture_type'),
      ('wrong_capture_path',lambda s:s['captures']['at'].update(pointer='/missing'),'record_path'),
      ('wrong_book_path',lambda s:s['captures']['now'].update(pointer='/seen'),'book_capture_path'),
      ('unsafe_operator_slot',lambda s:s['slots'][-1].update(target='/manifest/requirements/7/predicate/op'),'unsafe_scalar_slot'),
      ('duplicate_scalar_slot',lambda s:s['slots'].append(deepcopy(s['slots'][-1])),'duplicate_scalar_slot'),
      ('duplicate_group_slot',lambda s:s['slots'].append(deepcopy(s['slots'][0])),'duplicate_group_slot'),
      ('missing_group_slot',lambda s:s['slots'].pop(0),'inexact_group_slots'),
      ('unused_capture',lambda s:s['captures'].update(unused=deepcopy(s['captures']['at'])),'unused_capture'),
      ('unknown_slot_capture',lambda s:s['slots'][-1].update(capture='missing'),'slot_capture_missing'),
      ('wrong_slot_type',lambda s:s['slots'][3].update(capture='at'),'slot_capture_type'),
      ('child_capture_group_mode',lambda s:s.update(mode='groups'),'child_capture_requires_rows')]:
        s=deepcopy(spec);change(s);refuse(label,s=s,reason=reason)
        if label in ('wrong_capture_path','unsafe_operator_slot'):refuse(label+'_empty',s=s,state=empty,reason=reason)
    s=deepcopy(spec);s['slots']=[deepcopy(s['slots'][0]) for _ in range(t.MAX_SLOTS+1)]
    refuse('slot_limit',s=s,reason='template_slot_limit')
    s=deepcopy(spec);s['template']['queries']['term']['query']['group']['parent_path']='/memory/claims/foreign'
    refuse('forged_group_template',s=s,reason='query_parent_path')
    cov=p.population(spec['iteration'],base['book'],'partial','Partial supplied fixture')
    refuse('partial_iteration',coverage=cov,status='unresolved',reason='complete_supplied_population_required')
    query_cov={name:p.population(item['projection'],empty['book'],'partial','Partial query fixture') for name,item in spec['template']['queries'].items()}
    refuse('partial_queries_empty_iteration',state=empty,query_coverages=query_cov,status='unresolved',reason='query_population_unavailable')
    refuse('missing_query_coverage',query_coverages={},reason='inexact_template_coverages')
    s=deepcopy(spec);s['residuals'].append('Changed declaration')
    refuse('stale_reviewed_template',s=s,selection=core.digest(spec),reason='reviewed_template_selection')
    cov=p.population(spec['iteration'],base['book'],'complete','Supplied iteration fixture')
    query_cov={name:p.population(item['projection'],base['book'],'complete','Supplied query fixture') for name,item in spec['template']['queries'].items()}
    call=t.make_call(spec,base['book'],base['memory_definition'],base['schemas'],cov,query_cov,core.digest(spec))
    changed=deepcopy(base);claim=changed['book']['memory']['claims'][owner]
    claim['assessments']=dict(reversed(list(claim['assessments'].items())))
    refuse('stale_input_order',state=changed,coverage=cov,query_coverages=query_cov,call=call,reason='stale_template_call')
    paired('fresh_reordered_rows',changed,spec,'rows','requirements_satisfied')
    changed=deepcopy(base);claims=changed['book']['memory']['claims'];claims['公司/~é']=deepcopy(claims[owner]);f.f.configure(changed)
    result=paired('two_unicode_owners',changed,spec,'rows','requirements_satisfied')
    check(len({(i['parent_key'],i['child_key']) for i in result['instances']})==result['instance_count'],'qualified_instance_keys')
    changed=deepcopy(base);changed['book']['memory']['claims'][owner]['assessments']['imported']['overdue']='0/1'
    paired('historical_overdue_corruption',changed,spec,'rows','invalid')
    changed=deepcopy(base);changed['book']['memory']['claims'][owner]['assessed']=False
    paired('parent_summary_corruption',changed,f.group_spec(base),'groups','invalid')
    limit_cases(base,check,refuse,records)

def limit_cases(base,check,refuse,records):
    # A small unrelated typed map isolates the generic template instance bound.
    state=deepcopy(base);text=p.guards.TEXT
    state['memory_definition']['root']['fields']['probe']={'node':'map','max_items':1,'values':{'node':'record','fields':{
      'children':{'node':'map','max_items':128,'values':{'node':'record','fields':{'value':{'node':'scalar','type':text}}}}}}}
    state['book']['memory']['probe']={'owner':{'children':{str(i):{'value':'v'} for i in range(t.MAX_INSTANCES)}}}
    f.f.configure(state)
    projection=dict(profile=p.PROFILE,context=state['book']['context'],parent_pointer='/probe',child_pointer='/children',
       fields={'identity':dict(kind='child_key',type=text)},residuals=['Synthetic limit fixture'])
    query=dict(profile=t.c.q.PROFILE,context=state['book']['context'],mode='match',field='identity',allow_empty=False,
       group=dict(parent_key='owner',parent_path='/memory/probe/owner',child_map_path='/memory/probe/owner/children'),
       value=dict(type=text,binding=dict(status='known',value='0')))
    item=dict(projection=projection,query=query,on_ambiguous='invalid')
    template=f.g.assemble(state,{'row':item},{'present':dict(kind='has_row',query='row')},[f.g.rule('present',f.g.ref('present'),['present'])])
    spec=dict(profile=t.PROFILE,context=state['book']['context'],iteration=projection,mode='rows',
      captures={'id':dict(kind='child_key',type=text)},template=template,
      slots=[dict(kind='group',query='row'),dict(kind='scalar',capture='id',target='/queries/row/query/value/binding/value')],
      residuals=['Synthetic template boundary fixture'])
    result=f.run(state,spec)
    check(result['status']=='requirements_satisfied' and result['instance_count']==t.MAX_INSTANCES,'exact_instance_limit')
    for i,item in enumerate(result['instances']):
        check(item['child_key']==str(i) and item['declaration']['queries']['row']['query']['value']['binding']['value']==str(i),'boundary_instance_identity:'+str(i))
    records.append(dict(case='exact_instance_limit',result=result))
    state['book']['memory']['probe']['owner']['children'][str(t.MAX_INSTANCES)]={'value':'v'};f.f.configure(state)
    refuse('instance_overflow',s=spec,state=state,reason='template_instance_limit')
