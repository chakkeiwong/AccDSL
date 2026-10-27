from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from datetime import date,timedelta,datetime,timezone
import json
import subprocess
import sys
import time
import expander as e
import declared_receivable_lifecycle_v1 as native
c=e.c
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def canonical(v):return c.core.canonical(v)

def main():
    start=time.monotonic();lock=json.loads((HERE/'source-lock.json').read_text())
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    templates={o:json.loads((HERE/f'templates/{o}.assess.json').read_text()) for o in ('alpha','beta')}
    rows=json.loads((HERE.parent/'event-specialization-audit-20261026/request-comparisons.json').read_text())
    params_cases=json.loads((HERE.parent/'parameterized-method-construction-20261026/cases.json').read_text())
    assertions=[];cases=[];controls=[]
    def ensure(ok,label):assertions.append({'check':label,'passed':bool(ok)});assert ok,label
    def compare(label,owner,book,event,params,order=None):
        t=templates[owner];order=list(book['memory']['claims']) if order is None else order
        stable=canonical([t,book,event,params,order])
        construction=e.construct(t,book,event,params['schemas'],params['memory_definition'],e.make_call(t,book,event,order))
        # Explicit comparator order preserves all bytes except object iteration.
        ordered=deepcopy(book);ordered['memory']['claims']={k:deepcopy(book['memory']['claims'][k]) for k in order}
        expected=native.make_request(ordered,params,{'kind':'event','method_key':'assess','event':deepcopy(event)})
        ensure(canonical(construction['construction']['request'])==canonical(expected),label+':full_request')
        result=c.frontend.v2.propose(book,construction['construction']['request'])
        comparator=c.frontend.v2.propose(ordered,expected)
        ensure(result['status']==comparator['status']=='proposed',label+':proposed')
        ensure(canonical(result)==canonical(comparator),label+':full_transition')
        native.control(result['after'],params['roles'])
        for k,row in book['memory']['claims'].items():
            after=result['after']['memory']['claims'][k]
            ensure(after['assessed_remaining']==row['remaining'] and after['assessment_date']==event['date'] and after['assessed'] is True,label+':snapshot:'+k)
            ensure(after['overdue']==(row['remaining'] if date.fromisoformat(row['due'])<date.fromisoformat(event['date']) else '0/1'),label+':strict_due:'+k)
        ensure(canonical([t,book,event,params,order])==stable,label+':inputs_preserved')
        item={'case':label,'company':owner,'before':deepcopy(book),'event':deepcopy(event),'parameters':deepcopy(params),'order':deepcopy(order),'construction':construction,'native_request':expected,'transition':result}
        cases.append(item);return item
    for row in rows:
        if row['method']=='assess':compare('retained_'+row['company']+'_'+str(row['index']),row['company'],row['before'],row['full_command']['event'],row['body_parameters'])
    for owner in ('alpha','beta'):
        saved=next(r for r in rows if r['company']==owner and r['method']=='assess')
        empty=next(r for r in rows if r['company']==owner and r['method']=='sale')['before']
        compare(owner+'_empty',owner,empty,saved['full_command']['event'],saved['body_parameters'])
        last=next(r for r in params_cases if r['case']==owner+'_new_collect_2')
        book=last['complete_transition']['after'];params=last['parameters']
        for day in ('2027-01-31','2027-02-01','2027-02-02'):
            ev=deepcopy(saved['full_command']['event']);ev.update(id='assessment.'+day,date=day)
            ev['inputs']['start']['value']=c.base.known(book['memory']['collection_clock']['cursor'])
            ev['inputs']['end_exclusive']['value']=c.base.known((date.fromisoformat(day)+timedelta(days=1)).isoformat())
            compare(owner+'_multi_'+day,owner,book,ev,params)
        ev=deepcopy(saved['full_command']['event']);ev.update(id='assessment.reordered',date='2027-02-02')
        ev['inputs']['start']['value']=c.base.known(book['memory']['collection_clock']['cursor']);ev['inputs']['end_exclusive']['value']=c.base.known('2027-02-03')
        forward=compare(owner+'_ordered_forward',owner,book,ev,params)
        reverse=compare(owner+'_ordered_reverse',owner,book,ev,params,list(reversed(book['memory']['claims'])))
        ensure(forward['construction']['state_sha256']==reverse['construction']['state_sha256'],owner+':canonical_state_ignores_map_order')
        ensure(forward['construction']['order_sha256']!=reverse['construction']['order_sha256'],owner+':order_identity_changes')
        ensure(canonical(forward['native_request'])!=canonical(reverse['native_request']),owner+':request_order_changes')
        ensure(canonical(forward['transition']['after'])==canonical(reverse['transition']['after']),owner+':financial_state_same_under_disjoint_writes')
    baseline=next(r for r in cases if r['case']=='alpha_multi_2027-02-01')
    t=templates['alpha'];b=baseline['before'];ev=baseline['event'];p=baseline['parameters'];order=baseline['order']
    def attempt(template=t,book=b,event=ev,ordered=order,call=None):
        return e.construct(template,book,event,p['schemas'],p['memory_definition'],call or e.make_call(template,book,event,ordered))
    def refuse(label,fn,reason,status='invalid'):
        try:fn()
        except c.Refusal as exc:
            ensure(exc.status==status and reason in exc.reason,label+':refusal');controls.append({'case':label,'status':exc.status,'reason':exc.reason})
        else:raise AssertionError('accepted_bad_case:'+label)
    refuse('missing_order_key',lambda:attempt(ordered=order[:-1]),'order_coverage')
    refuse('duplicate_order_key',lambda:attempt(ordered=order+[order[0]]),'duplicate_order_key')
    refuse('extra_order_key',lambda:attempt(ordered=order+['not-a-claim']),'order_coverage')
    for field in ('template_sha256','state_sha256','event_sha256','order_sha256'):
        call=e.make_call(t,b,ev,order);call[field]='0'*64
        refuse('stale_'+field,lambda call=call:attempt(call=call),'stale_'+field.split('_sha256')[0])
    call=e.make_call(t,b,ev,order);call['order']=list(reversed(order))
    refuse('changed_order_old_digest',lambda:attempt(call=call),'stale_order')
    changed=deepcopy(t);changed['row_types']['remaining']=c.TEXT
    refuse('wrong_row_type',lambda:attempt(changed),'row_type_mismatch')
    changed=deepcopy(t);del changed['row_types']['customer']
    refuse('missing_row_field',lambda:attempt(changed),'row_type_population')
    changed=deepcopy(t);changed['row_operations'][3]['fields']['value']['fields']['value']['else']={'expr':'row','field':'not-present'}
    refuse('bad_unselected_branch',lambda:attempt(changed),'row_field')
    changed=deepcopy(t);changed['row_operations'][3]['fields']['value']['fields']['value']['condition']['expr']='callback'
    refuse('unsupported_predicate',lambda:attempt(changed),'unsupported_expression')
    changed=deepcopy(t);changed['row_operations'][3]['fields']['value']['fields']['value']['else']={'expr':'literal','type':c.TEXT,'value':'zero'}
    refuse('branch_type_mismatch',lambda:attempt(changed),'branch_type')
    changed=deepcopy(t);changed['row_operations'][3]['fields']['value']['fields']['value']['condition']['left']={'expr':'row','field':'remaining'}
    refuse('nondate_comparison',lambda:attempt(changed),'date_comparison_type')
    changed=deepcopy(t);changed['map_pointer']='/claims~3bad'
    refuse('malformed_map_pointer',lambda:attempt(changed),'pointer_escape')
    changed=deepcopy(ev);changed['inputs']['end_exclusive']['value']={'status':'unknown','reason':'not supplied'}
    refuse('unknown_event_input',lambda:attempt(event=changed),'unknown_event_input:end_exclusive','unresolved')
    changed=deepcopy(t);changed['row_operations']=[{'expr':'literal','type':c.TEXT,'value':'oversized'}]*(c.base.memory.MAX_OPERATIONS//len(order)+1)
    refuse('operation_budget',lambda:attempt(changed),'operation_limit')
    changed=deepcopy(t);changed['base_template']['method_template']['fields']['memory']['fields']['definition']['fields']['operations']['items']=[{'node':'literal','value':'not empty'}]
    refuse('base_operation_override',lambda:attempt(changed),'base_operations_not_empty')
    # Even an empty map must check its row expression and declared row type.
    empty=next(r for r in cases if r['case']=='alpha_empty')
    changed=deepcopy(t);changed['row_operations'][0]['fields']['value']['fields']['value']={'expr':'row','field':'absent'}
    refuse('empty_map_bad_row_expression',lambda:attempt(changed,book=empty['before'],event=empty['event'],ordered=[]),'row_field')
    changed=deepcopy(t);changed['row_operations'][0]={'expr':'literal','type':c.TEXT,'value':'not an operation'}
    refuse('empty_map_malformed_operation',lambda:attempt(changed,book=empty['before'],event=empty['event'],ordered=[]),'operation_expression_shape')
    changed=deepcopy(t);changed['row_operations'][0]['fields']['path']['items'][-1]['value']='missing_field'
    refuse('empty_map_invalid_target',lambda:attempt(changed,book=empty['before'],event=empty['event'],ordered=[]),'row_write_field')
    original=native.make_request
    def disabled(*args,**kwargs):raise AssertionError('native_specializer_called')
    native.make_request=disabled
    try:ensure(canonical(attempt()['construction']['request'])==canonical(baseline['native_request']),'native_disabled_construction')
    finally:native.make_request=original
    variant=deepcopy(t);variant['row_operations'][3]['fields']['value']['fields']['value']['condition']['expr']='date_le'
    alt=attempt(variant);result=c.frontend.v2.propose(b,alt['construction']['request'])
    ensure(result['status']=='proposed','inclusive_variant_typed_execution')
    boundary=[k for k,v in b['memory']['claims'].items() if v['due']==ev['date']]
    ensure(len(boundary)==1,'single_equal_due_boundary')
    for k,row in b['memory']['claims'].items():
        expected=row['remaining'] if row['due']<=ev['date'] else '0/1'
        ensure(result['after']['memory']['claims'][k]['overdue']==expected,'inclusive_boundary:'+k)
    try:native.control(result['after'],p['roles'])
    except Exception as exc:ensure(str(exc)=='overdue_snapshot','selected_native_invariant_rejects_inclusive_variant')
    else:raise AssertionError('inclusive_variant_admitted_by_strict_contract')
    ensure(canonical(alt['construction']['request'])!=canonical(baseline['native_request']),'inclusive_request_differs')
    dump('inclusive-variant.json',{'template':variant,'construction':alt,'transition':result,'selected_native_contract':'rejected:overdue_snapshot'})
    dump('cases.json',cases);dump('controls.json',controls)
    for row in json.loads((HERE/'cases.json').read_text()):
        template=templates[row['company']];book=row['before'];event=row['event'];params=row['parameters']
        rebuilt=e.construct(template,book,event,params['schemas'],params['memory_definition'],e.make_call(template,book,event,row['order']))
        ensure(canonical(rebuilt)==canonical(row['construction']),'saved_construction:'+row['case'])
    for n,h in lock.items():ensure(sha(ROOT/n)==h,'protected:'+n)
    summary={'passed':True,'templates':2,'full_request_transition_cases':len(cases),'retained_assessments':sum(r['case'].startswith('retained_') for r in cases),'new_assessments':sum(not r['case'].startswith('retained_') for r in cases),'controls':len(controls),'checks':len(assertions),'protected_files':len(lock),'explicit_order_bound':True,'native_specializer_called_by_expander':False,'native_eligibility_required':True,'accounting_admission':False,'production_ready':False}
    dump('checks.json',summary);dump('check-detail.json',assertions)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',{'git_commit':git.stdout.strip() if git.returncode==0 else 'unavailable','command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/ordered-assessment-expansion-20261026/verify.py','environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'data_version':sha(HERE/'source-lock.json'),'implementation_sha256':{n:sha(HERE/n) for n in ['expander.py','prepare.py','verify.py','design.md']},'plan_file':'docs/plans/accounting-ordered-assessment-expansion-20261026.md','result_file':str((HERE/'result.md').relative_to(ROOT)),'artifacts':['cases.json','controls.json','checks.json','check-detail.json','inclusive-variant.json'],'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(summary))
if __name__=='__main__':main()
