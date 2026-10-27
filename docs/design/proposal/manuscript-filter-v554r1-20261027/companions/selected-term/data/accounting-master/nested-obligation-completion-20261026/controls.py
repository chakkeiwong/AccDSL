from copy import deepcopy
import declarations as d
p=d.p;core=d.core
def corruptions(base):
    rows=[];owner='invoice/a~1'
    def add(label,section,change):
        state=deepcopy(base);claim=state['book']['memory']['claims'][owner];change(claim)
        d.f.f.configure(state);rows.append((label,state,section))
    add('wrong_predecessor','terms',lambda c:c['terms']['extension2'].update(predecessor='initial'))
    add('wrong_initial_sentinel','terms',lambda c:c['terms']['initial'].update(predecessor='extension2'))
    add('tied_effective_date','terms',lambda c:c['terms']['extension2'].update(effective=c['terms']['extension1']['effective']))
    add('effective_before_issue','terms',lambda c:c['terms']['initial'].update(effective='2026-01-01'))
    add('effective_after_book','terms',lambda c:c['terms']['extension2'].update(effective='2029-01-01',due='2029-02-01'))
    add('due_before_effective','terms',lambda c:c['terms']['extension1'].update(due='2026-01-01'))
    add('term_event_missing','events',lambda c:c['terms']['initial'].update(event_id='absent'))
    add('negative_assessed_remaining','assessments',lambda c:c['assessments']['imported'].update(remaining='-20/1',overdue='-20/1'))
    add('wrong_historical_term','assessments',lambda c:c['assessments']['imported'].update(term_id='extension2'))
    add('wrong_historical_overdue','assessments',lambda c:c['assessments']['imported'].update(overdue='0/1'))
    add('unknown_origin','assessments',lambda c:c['assessments']['imported'].update(origin='assumed'))
    add('imported_event_not_unknown','assessments',lambda c:c['assessments']['imported'].update(event_id='other'))
    def duplicate_date(c):
        rows=list(c['assessments'].values());rows[1]['as_of']=rows[0]['as_of']
    add('duplicate_assessment_date','assessments',duplicate_date)
    def missing_recorded(c):
        row=next(r for r in c['assessments'].values() if r['origin']=='recorded_event');row['event_id']='absent'
    add('recorded_event_missing','events',missing_recorded)
    return rows

def bridge_controls(base,check,compare,records):
    original=d.event_collections(base)
    def refuse(label,s=original,state=base,status='invalid',reason='',**kwargs):
        actual=d.run_bridge(state,s,**kwargs)
        check(actual['status']==status and reason in actual.get('reason',''),label+':reason:'+actual.get('reason',''))
        check('values' not in actual,label+':no_partial_collections')
        records.append(dict(case=label,result=actual))
    for label,change,reason in [
      ('bad_filter_type',lambda s:s['bindings']['recorded']['filter'].update(type=p.guards.DATE),'filter_field_type'),
      ('bad_filter_field',lambda s:s['bindings']['recorded']['filter'].update(field='absent'),'filter_field_missing'),
      ('bad_filter_value',lambda s:s['bindings']['recorded']['filter'].update(value=None),'text:text'),
      ('missing_collection',lambda s:s['bindings'].pop('seen'),'exact_collection_bindings'),
      ('wrong_seen_target',lambda s:s['bindings']['seen']['fields'].update(id='other'),'seen_binding_value'),
      ('unused_source',lambda s:s['sources'].update(unused=deepcopy(s['sources']['terms'])),'unused_collection_source'),
      ('wrong_source',lambda s:s['bindings']['terms'].update(source='absent'),'collection_source_missing'),
      ('wrong_bound_field',lambda s:s['bindings']['terms']['fields'].update(id='absent'),'projection_field_missing')]:
        s=deepcopy(original);change(s);refuse(label,s=s,reason=reason)
    empty=deepcopy(base);empty['book']['memory']['claims']={};d.f.f.configure(empty)
    actual=compare('empty_projected_events',empty,original)
    check(actual['status']=='collection_requirements_satisfied','empty_complete_membership')
    records.append(dict(case='empty_projected_events',result=actual))
    s=deepcopy(original);s['bindings']['recorded']['filter']['field']='absent'
    refuse('bad_filter_empty',state=empty,s=s,reason='filter_field_missing')
    cov={name:p.population(source,base['book'],'partial','Explicit partial source') for name,source in original['sources'].items()}
    refuse('partial_projected_source',coverages=cov,status='unresolved',reason='collection_projection_unavailable')
    refuse('missing_source_coverage',coverages={},reason='exact_source_coverages')
    s=deepcopy(original);s['bindings']['recorded']['filter']['value']='imported_snapshot'
    refuse('changed_filter_stale_selection',s=s,selection=core.digest(original),reason='reviewed_collection_selection')
    changed=deepcopy(base);c=changed['book']['memory']['claims']['invoice/a~1'];c['terms']=dict(reversed(list(c['terms'].items())))
    cov={name:p.population(source,base['book'],'complete','Supplied event-membership source') for name,source in original['sources'].items()}
    call=d.bridge.make_call(original,base['book'],base['memory_definition'],base['schemas'],cov,core.digest(original))
    refuse('stale_collection_order',state=changed,coverages=cov,call=call,reason='stale_collection_call')
    actual=compare('fresh_reordered_membership',changed,original);records.append(dict(case='fresh_reordered_membership',result=actual))
    changed=deepcopy(base);claims=changed['book']['memory']['claims'];claims['公司/~é']=deepcopy(claims['invoice/a~1']);d.f.f.configure(changed)
    actual=compare('unicode_duplicate_local_events',changed,original);records.append(dict(case='unicode_duplicate_local_events',result=actual))
    # Sum-of-bound-collections limit, including the seen sequence.
    changed=deepcopy(base);existing=len(changed['book']['seen']);claim=changed['book']['memory']['claims']['invoice/a~1']
    extra=len(claim['terms'])+sum(r['origin']=='recorded_event' for r in claim['assessments'].values())
    target=d.bridge.engine.MAX_ROWS-extra
    changed['book']['seen'].extend('boundary-event-'+str(i) for i in range(target-existing))
    actual=d.run_bridge(changed,original)
    check(actual['status']=='collection_requirements_satisfied','exact_combined_collection_limit:'+actual.get('reason',''))
    check(sum(len(c['rows']) for c in actual['values']['collections'].values())==256,'exact_combined_rows')
    records.append(dict(case='exact_combined_collection_limit',result=actual))
    changed['book']['seen'].append('one-too-many')
    refuse('combined_collection_overflow',state=changed,reason='combined_collection_row_limit')
