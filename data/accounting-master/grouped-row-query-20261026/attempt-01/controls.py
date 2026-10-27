from copy import deepcopy
import fixtures as f
q=f.q;p=f.p

def exercise(base,check,compare,records):
    owner='invoice/a~1';kind='terms'
    decl=f.declaration(base,kind,owner,'greatest','effective')
    def refuse(label,d=decl,state=base,status='invalid',reason='',**kwargs):
        actual=f.run(state,kind,d,**kwargs)
        check(actual['status']==status and reason in actual.get('reason',''),label+':status:'+actual.get('reason',''))
        check(actual.get('selected') is None and actual.get('selected_lineage') is None,label+':no_selected_row')
        records.append(dict(case=label,result=actual))
    def paired(label,state,d):
        actual=compare(label,state,kind,d)
        records.append(dict(case=label,result=actual));return actual
    spec=f.spec_for(base,kind);coverage=p.population(spec,base['book'],'complete','Original supplied fixture dictionaries')
    pc=p.make_call(spec,base['book'],base['memory_definition'],base['schemas'],coverage)
    call=q.make_call(decl,spec,base['book'],base['memory_definition'],base['schemas'],coverage,pc)
    for status in ('partial','unknown'):
        pop=deepcopy(coverage);pop['status']=status
        refuse('population_'+status,coverage=pop,status='unresolved',reason='complete_supplied_population_required')
    d=deepcopy(decl);d['allow_empty']=False
    refuse('stale_query',d=d,projection_call=pc,coverage=coverage,call=call,reason='stale_query_call')
    changed=deepcopy(base);terms=changed['book']['memory']['claims'][owner]['terms']
    terms['initial']['due']='2027-01-19'
    refuse('stale_book',state=changed,projection_call=pc,coverage=coverage,call=call,reason='stale_query_call')
    refuse('stale_projection',state=changed,projection_call=pc,reason='stale_projection_call')
    changed=deepcopy(base);terms=changed['book']['memory']['claims'][owner]['terms']
    changed['book']['memory']['claims'][owner]['terms']=dict(reversed(list(terms.items())))
    refuse('stale_order',state=changed,projection_call=pc,coverage=coverage,call=call,reason='stale_query_call')
    original=paired('original_order',base,decl);reordered=paired('reordered',changed,decl)
    check(original['selected']==reordered['selected'],'reorder_same_selected_row')
    check(original['selected_indices']!=reordered['selected_indices'],'reorder_indices_visible')
    check(original['projection']['book_order_sha256']!=reordered['projection']['book_order_sha256'],'reorder_digest_visible')
    d=f.declaration(base,kind,'missing','greatest','effective')
    refuse('missing_group',d=d,reason='query_group_missing')
    d=deepcopy(decl);d['group']['parent_path']='/memory/claims/other'
    refuse('foreign_parent_path',d=d,reason='query_parent_path')
    d=deepcopy(decl);d['group']['child_map_path']+='/other'
    refuse('foreign_child_map',d=d,reason='query_child_map_path')
    d=deepcopy(decl);d['context']={}
    refuse('wrong_context',d=d,reason='query_context')
    d=deepcopy(decl);d['field']='identity'
    refuse('nonorderable_field',d=d,reason='query_nonorderable_field')
    d=deepcopy(decl);d['field']='absent'
    refuse('missing_field',d=d,reason='query_field_missing')
    d=deepcopy(decl);del d['upper_bound']
    refuse('missing_bound_declaration',d=d,reason='fields:query_fields')
    d=f.declaration(base,kind,owner,'greatest','effective',bound='2027-03-01')
    d['upper_bound']['binding']={'status':'unknown','reason':'No observation'}
    refuse('unknown_bound',d=d,status='unresolved',reason='query_input_unknown')
    d=f.declaration(base,kind,owner,'match','identity',value='initial')
    d['value']['binding']={'status':'unknown','reason':'No observation'}
    refuse('unknown_match',d=d,status='unresolved',reason='query_input_unknown')
    for label,patch,reason in [
      ('wrong_bound_type',{'type':p.guards.TEXT},'query_input_type'),
      ('wrong_bound_context',{'type':{'kind':'date','context':{'calendar':'other'}}},'query_input_type'),
      ('bad_date',{'binding':{'status':'known','value':'2027-02-30'}},'day is out of range'),
      ('missing_bound_value',{'binding':{'status':'known'}},'fields:known_query_input'),
      ('bad_inclusive',{'inclusive':1},'query_bound_inclusive')]:
        d=f.declaration(base,kind,owner,'greatest','effective',bound='2027-03-01');d['upper_bound'].update(patch)
        refuse(label,d=d,reason=reason)
    empty=deepcopy(base);empty['book']['memory']['claims'][owner]['terms']={};f.configure(empty)
    for mode in ('count','greatest','match'):
        d=f.declaration(empty,kind,owner,mode,None if mode=='count' else 'identity' if mode=='match' else 'effective',value='initial')
        paired('empty_'+mode,empty,d)
    d=deepcopy(decl);d['allow_empty']=False
    refuse('empty_required',state=empty,d=d,reason='required_row_missing')
    d=deepcopy(decl);d['field']='identity'
    refuse('bad_field_on_empty',state=empty,d=d,reason='query_nonorderable_field')
    d=f.declaration(empty,kind,owner,'greatest','effective',bound='2027-03-01');d['upper_bound']['binding']={'status':'unknown','reason':'Missing cutoff'}
    refuse('unknown_bound_empty',state=empty,d=d,status='unresolved',reason='query_input_unknown')
    changed=deepcopy(base);changed['book']['memory']['claims'][owner]['terms']['tied']=deepcopy(terms['extension2']);f.configure(changed)
    tied=paired('duplicate_greatest',changed,decl);check(tied['status']=='ambiguous','ties_do_not_select_first')
    d=f.declaration(base,kind,owner,'match','owner',value=owner)
    duplicate=paired('duplicate_match',base,d);check(duplicate['status']=='ambiguous','all_matching_rows_retained')
    unicode_owner='汉字/é~ ';changed=deepcopy(base);claims=changed['book']['memory']['claims']
    claims[unicode_owner]=deepcopy(claims[owner]);claims[unicode_owner]['terms']['initial']['due']='2027-01-18';f.configure(changed)
    d=f.declaration(changed,kind,unicode_owner,'match','identity',value='initial')
    selected=paired('unicode_same_local_key',changed,d)
    check(selected['selected']['due']['value']=='2027-01-18','selected_correct_owner_value')
    numeric=deepcopy(base);claims=numeric['book']['memory']['claims']
    typ={'kind':'rational','context':{},'dimensions':{'USD':1},'scale':'1/1'}
    numeric['memory_definition']['root']['fields']['claims']['values']['fields'][kind]['values']['fields']['metric']={'node':'scalar','type':typ}
    for row,value in zip(claims[owner][kind].values(),('10/1','2/1','-1/3')):row['metric']=value
    f.configure(numeric)
    for bound,inclusive in [(None,True),('2/1',True),('2/1',False),('-1/3',False)]:
        d=f.declaration(numeric,kind,owner,'greatest','metric',bound=bound,inclusive=inclusive)
        paired('exact_rational_'+str(bound)+'_'+str(inclusive),numeric,d)
    for label,key,value in [('scale','scale','100/1'),('units','dimensions',{'EUR':1})]:
        d=f.declaration(numeric,kind,owner,'greatest','metric',bound='2/1');d['upper_bound']['type'][key]=value
        refuse('rational_'+label,state=numeric,d=d,reason='query_input_type')
