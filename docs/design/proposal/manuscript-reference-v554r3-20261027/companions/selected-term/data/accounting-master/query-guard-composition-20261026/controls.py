from copy import deepcopy
import fixtures as f
c=f.c;p=f.p;core=f.core
def exercise(base,check,compare,records):
    owner='invoice/a~1';original=f.presence_spec(base,owner)
    def paired(label,state,spec,status):
        result=compare(label,state,spec);check(result['status']==status,label+':expected_status')
        records.append(dict(case=label,result=result));return result
    def refuse(label,spec=original,state=base,reason='',**kw):
        result=f.run(state,spec,**kw)
        check(result['status']=='invalid' and reason in result.get('reason',''),label+':reason:'+result.get('reason',''))
        records.append(dict(case=label,result=result));return result
    absent=f.presence_spec(base,owner,'absent')
    result=paired('allowed_absent',base,absent,'no_active_requirements')
    check(result['bound_values']['present']==dict(status='known',value=False),'none_is_known_absence')
    paired('absent_required_known',base,f.presence_spec(base,owner,'absent',required=True),'unresolved')
    s=deepcopy(absent);s['queries']['row']['query']['allow_empty']=False
    paired('required_row_absent',base,s,'invalid')
    empty=deepcopy(base);empty['book']['memory']['claims'][owner]['terms']={};f.f.configure(empty)
    paired('empty_group_guard',empty,f.presence_spec(empty,owner),'no_active_requirements')
    s=f.presence_spec(base,'missing');s['manifest']['requirements'][0]['guard']=f.const(core.BOOL,False)
    s['manifest']['requirements'][0]['guard_requires']=[];s['manifest']['required_known']=['present']
    paired('invalid_query_false_guard',base,s,'invalid')
    s=deepcopy(original);s['queries']['row']['query']['value']['binding']=dict(status='unknown',reason='Unknown selection')
    paired('unknown_match',base,s,'unresolved')
    s['manifest']['requirements'][0]['guard']={'op':'all','args':[f.const(core.BOOL,False),f.ref('present')]}
    result=paired('unknown_query_inactive_guard',base,s,'unresolved')
    check(result['assessment']['status']=='no_active_requirements','query_veto_survives_inactive_engine')
    s=deepcopy(original);s['queries']['row']['query']['field']='owner';s['queries']['row']['query']['value']['binding']['value']=owner
    paired('ambiguous_invalid',base,s,'invalid')
    s['queries']['row']['on_ambiguous']='unresolved'
    result=paired('ambiguous_unresolved',base,s,'unresolved')
    check(result['bound_values']['present']['status']=='unknown','ambiguous_is_not_absent')
    s['manifest']['requirements'][0]['guard']={'op':'all','args':[f.const(core.BOOL,False),f.ref('present')]}
    result=paired('ambiguous_inactive_guard',base,s,'unresolved')
    check(result['assessment']['status']=='no_active_requirements','ambiguous_veto_survives_inactive_engine')
    s=deepcopy(original);s['queries']['row']['on_ambiguous']='first'
    refuse('invented_tie_breaker',spec=s,reason='ambiguity_policy')
    for label,change,reason in [
      ('wrong_field_type',lambda s:s['manifest']['inputs']['due'].update(type=core.BOOL),'invariant_binding_type'),
      ('wrong_role',lambda s:s['manifest']['inputs']['due'].update(role='assumption'),'invariant_input_role'),
      ('missing_binding',lambda s:s['bindings'].pop('due'),'inexact_invariant_bindings'),
      ('extra_binding',lambda s:s['bindings'].update(extra=deepcopy(s['bindings']['due'])),'inexact_invariant_bindings'),
      ('undeclared_query',lambda s:s['bindings']['due'].update(query='absent'),'undeclared_query'),
      ('undeclared_field',lambda s:s['bindings']['due'].update(field='absent'),'undeclared_selected_field'),
      ('count_on_selection',lambda s:s['bindings']['due'].update(kind='count'),'fields:invariant_binding'),
      ('unused_query',lambda s:s['queries'].update(unused=deepcopy(s['queries']['row'])),'unused_invariant_query')]:
        s=deepcopy(original);change(s);refuse(label,spec=s,reason=reason)
    s=deepcopy(original);s['manifest']['inputs']['due']['type']=core.BOOL
    refuse('wrong_type_empty',state=empty,spec=s,reason='invariant_binding_type')
    coverage={'row':p.population(original['queries']['row']['projection'],base['book'],'partial','Explicit partial fixture')}
    result=f.run(base,original,coverage=coverage);check(result['status']=='unresolved','partial_population')
    check(result['bound_values']['present']['status']=='unknown','partial_not_absent')
    records.append(dict(case='partial_population',result=result))
    refuse('missing_coverage',coverage={},reason='inexact_query_coverages')
    s=deepcopy(original);s['queries']['row']['query']['allow_empty']=False
    refuse('stale_reviewed_selection',spec=s,selection=core.digest(original),reason='reviewed_invariant_selection')
    coverage={'row':p.population(original['queries']['row']['projection'],base['book'],'complete','Original supplied query-guard fixture')}
    call=c.make_call(original,base['book'],base['memory_definition'],base['schemas'],coverage,core.digest(original))
    changed=deepcopy(base);changed['book']['date']='2028-02-01'
    refuse('stale_bound_call',state=changed,coverage=coverage,call=call,reason='stale_invariant_call')
    changed=deepcopy(base);ts=changed['book']['memory']['claims'][owner]['terms']
    changed['book']['memory']['claims'][owner]['terms']=dict(reversed(list(ts.items())))
    refuse('stale_order_call',state=changed,coverage=coverage,call=call,reason='stale_invariant_call')
    paired('reordered_fresh',changed,original,'requirements_satisfied')
    h=f.history_spec(base,owner,'imported');changed=deepcopy(base)
    changed['book']['memory']['claims'][owner]['assessments']['imported']['overdue']='0/1'
    result=paired('historical_overdue_corruption',changed,h,'invalid')
    check(any(x['id']=='overdue_after_due' and x['consequence']=='invalid' for x in result['assessment']['findings']),'historical_due_discriminator')
    unicode_owner='公司/~é';changed=deepcopy(base);claims=changed['book']['memory']['claims']
    claims[unicode_owner]=deepcopy(claims[owner]);f.f.configure(changed)
    result=paired('unicode_parent',changed,f.history_spec(changed,unicode_owner,'imported'),'requirements_satisfied')
    check(result['lineage']['due']['parent_key']==unicode_owner,'lineage_owner_preserved')
    # Minimise declarations so the named-query limit, not a generic node limit, is tested.
    queries={};bindings={};rules=[]
    for i in range(c.MAX_QUERIES):
        name='n'+str(i);item=f.query_item(base,'terms',owner,'count')
        item['projection']['fields']={'identity':item['projection']['fields']['identity']}
        queries[name]=item;bindings[name]=dict(kind='count',query=name)
        rules.append(f.rule(name,f.binary('eq',f.ref(name),f.ref(name)),[name]))
    s=f.assemble(base,queries,bindings,rules)
    paired('exact_query_limit',base,s,'requirements_satisfied')
    s['queries']['overflow']=deepcopy(next(iter(queries.values())))
    refuse('query_overflow',spec=s,reason='invariant_query_limit')
