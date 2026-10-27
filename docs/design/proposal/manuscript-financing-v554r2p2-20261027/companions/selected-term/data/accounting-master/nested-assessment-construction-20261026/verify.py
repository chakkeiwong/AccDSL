"""Exact retained assessment requests/transitions and nested-write controls."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,json,subprocess,sys,time
import declaration as d
e=d.e;c=e.c;core=c.core
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+chr(10))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
native=__import__('receivable_term_history_v1');life=native.life

def main():
    assert len(sys.argv)==2,'fresh attempt name required'
    out=HERE/sys.argv[1];out.mkdir(exist_ok=False);start=time.monotonic();checks=[];controls=[];results=[]
    def check(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    lock=read(HERE.parent/'nested-contract-source-20261026/attempt-01/source-lock.json')
    for name,h in lock.items():check(sha(ROOT/name)==h,'protected_before:'+name)
    for directory,names in [('nested-contract-source-20261026',['contract_text.py','verify.py','attempt-01/checks.json','attempt-01/run-manifest.json']),
      ('ordered-assessment-expansion-20261026',['expander.py','checks.json']),('receivable-term-history-20261025',['evidence.json'])]:
        for name in names:
            p=HERE.parent/directory/name;lock[str(p.relative_to(ROOT))]=sha(p)
    for m in list(sys.modules.values()):
        file=getattr(m,'__file__',None)
        if file:
            path=Path(file).resolve()
            if path.is_relative_to(ROOT) and path.is_file() and not path.is_relative_to(HERE):
                name=str(path.relative_to(ROOT))
                if name in lock:check(lock[name]==sha(path),'loaded_pin:'+name)
                lock[name]=sha(path)
    dump(out/'source-lock.json',lock)
    evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases']
    cases=[(chart,str(i),row) for chart,case in evidence.items() for i,row in enumerate(case['steps']) if row['request']['operation']=='assess']
    templates={chart:d.build(next(row['before'] for row in case['steps'] if row['request']['operation']=='assess')) for chart,case in evidence.items()}
    dump(out/'templates.json',templates)
    first=cases[0][2];state=first['before'];book=state['book'];event=first['request']['event'];template=templates['alpha']
    def construct(t=template,state=state,event=event,order=None,call=None):
        b=state['book'];order=list(b['memory']['claims']) if order is None else order
        return e.construct(t,b,event,state['schemas'],state['memory_definition'],e.make_call(t,b,event,order) if call is None else call)
    def refuse(name,t=template,state=state,event=event,order=None,call=None,reason='',status='invalid'):
        before=deepcopy((t,state,event))
        try:construct(t,state,event,order,call)
        except c.Refusal as exc:
            check(exc.status==status and reason in exc.reason,name+':'+exc.reason)
            check(before==(t,state,event),name+':no_mutation')
            controls.append(dict(case=name,status=exc.status,reason=exc.reason))
        else:raise AssertionError(name+':accepted')
    saved=[]
    for m,names in [(native,('validate','step','carry','migrate','state_request','event_types','literal','protected','claim_type','term_type','assessment_type')),
      (life,('validate','control','claim_type','event_types','make_request','run','protected')),(life.operating,('build','conditions'))]:
        for name in names:saved.append((m,name,getattr(m,name)))
    def disabled(*a,**kw):raise AssertionError('native_financial_builder_in_candidate')
    try:
        for m,name,_ in saved:setattr(m,name,disabled)
        for chart,index,row in cases:
            state_i=row['before'];event_i=row['request']['event'];t=templates[chart];before=deepcopy((state_i,event_i,t))
            result=construct(t,state_i,event_i);request=result['construction']['request'];target=row['result']['typed_request']
            check(core.canonical(request)==core.canonical(target),chart+index+':full_request')
            check(result['operations']==target['method']['memory']['definition']['operations'],chart+index+':exact_operations')
            transition=c.frontend.v2.propose(state_i['book'],request)
            check(core.canonical(transition)==core.canonical(row['result']['transition']),chart+index+':full_transition')
            check(transition['after']==row['result']['after']['book'],chart+index+':complete_after')
            check(before==(state_i,event_i,t),chart+index+':no_mutation')
            check(not result['source_admission'] and not result['accounting_admission'] and not result['production_ready'],chart+index+':scope')
            results.append(dict(case=chart+':'+index,construction=result,transition=transition))
        # Primitive typing and complete-record controls.
        for name,mutate,reason in [
          ('missing_record_field',lambda x:x['row_operations'][0]['fields']['value']['fields']['fields']['fields'].pop('origin'),'complete_record_fields'),
          ('extra_record_field',lambda x:x['row_operations'][0]['fields']['value']['fields']['fields']['fields'].update(extra=d.wrap(d.literal('x'))),'complete_record_fields'),
          ('wrong_insert_target',lambda x:x['row_operations'][0]['fields']['path']['items'].__setitem__(-2,d.literal('due')),'scalar_write_parent'),
          ('wrong_nested_value_type',lambda x:x['row_operations'][0]['fields']['value']['fields']['fields']['fields'].__setitem__('as_of',d.wrap(d.literal('wrong'))),'write_value_type'),
          ('wrong_conditional_branch',lambda x:x['row_operations'][-1]['fields']['value']['fields']['value'].__setitem__('else',d.literal('wrong')),'branch_type'),
          ('wrong_declared_row',lambda x:x['row_definition']['fields'].pop('terms'),'row_definition_mismatch'),
          ('nested_scalar_read',lambda x:x['row_operations'][3]['fields']['value']['fields'].__setitem__('value',d.row('terms')),'row_field'),
          ('unknown_write_operation',lambda x:x['row_operations'][0]['fields'].__setitem__('op',d.literal('delete')),'declared_write_operation'),
        ]:
            t=deepcopy(template);mutate(t);refuse(name,t=t,reason=reason)
        refuse('missing_order',order=[],reason='order_coverage')
        refuse('duplicate_order',order=list(book['memory']['claims'])*2,reason='duplicate_order_key')
        call=e.make_call(template,book,event,list(book['memory']['claims']));call['order'].reverse();call['order'].append('absent')
        refuse('stale_order',call=call,reason='stale_order')
        changed=deepcopy(event);changed['inputs']['end_exclusive']['value']=dict(status='unknown',reason='missing')
        refuse('unknown_event_input',event=changed,reason='unknown_event_input',status='unresolved')
        # Empty claims still require every nested operation to be well typed.
        empty=deepcopy(state);empty['book']['memory']['claims']={}
        derived=c.types.derive(empty['memory_definition'],empty['book']['memory'],empty['book']);check(derived['status']=='typed','empty_derived')
        empty['book'].update(memory_schema=derived['schema_sha256'],memory_types=derived['memory_types'])
        empty['schemas'][derived['schema_sha256']]=derived['schema']
        empty_result=construct(state=empty,order=[])
        check(len(empty_result['operations'])==1 and empty_result['operations'][0]['id']=='term.0','empty_suffix_only')
        invalid=deepcopy(template);invalid['row_operations'][0]['fields']['value']['fields']['fields']['fields'].pop('origin')
        refuse('empty_invalid_template',t=invalid,state=empty,order=[],reason='complete_record_fields')
        # Validate ordered writes on a second actual row, with different history.
        multiple=deepcopy(state);original=multiple['book']['memory']['claims']['invoice/a~1']
        multiple['book']['memory']['claims']['second/claim~']=deepcopy(original)
        derived=c.types.derive(multiple['memory_definition'],multiple['book']['memory'],multiple['book']);check(derived['status']=='typed','multiple_derived')
        multiple['book'].update(memory_schema=derived['schema_sha256'],memory_types=derived['memory_types']);multiple['schemas'][derived['schema_sha256']]=derived['schema']
        order=list(reversed(multiple['book']['memory']['claims']))
        result=construct(state=multiple,order=order);ops=result['operations']
        check(len(ops)==13 and [x['id'] for x in ops]==['term.'+str(i) for i in range(13)],'global_operation_ids')
        check([ops[i]['path'][1] for i in (0,6)]==order,'explicit_reversed_order')
        transition=c.frontend.v2.propose(multiple['book'],result['construction']['request'])
        check(transition['status']=='proposed','multiple_transition')
        results.append(dict(case='multiple_reversed',construction=result,transition=transition))
        # The operation cap refuses before producing a partial request.
        four=deepcopy(multiple)
        for key in ('third','fourth'):four['book']['memory']['claims'][key]=deepcopy(original)
        derived=c.types.derive(four['memory_definition'],four['book']['memory'],four['book']);check(derived['status']=='typed','four_rows_derived')
        four['book'].update(memory_schema=derived['schema_sha256'],memory_types=derived['memory_types']);four['schemas'][derived['schema_sha256']]=derived['schema']
        overflow=deepcopy(template);overflow['row_operations']=[overflow['row_operations'][2]]*64
        refuse('operation_limit',t=overflow,state=four,reason='operation_limit')
    finally:
        for m,name,value in saved:setattr(m,name,value)
        dump(out/'assertions.json',checks);dump(out/'controls.json',controls)
    for name,h in lock.items():check(sha(ROOT/name)==h,'protected_after:'+name)
    dump(out/'results.json',results);dump(out/'assertions.json',checks)
    summary=dict(passed=True,retained_assessments=len(cases),complete_transitions=len(results),controls=len(controls),
      assertions=len(checks),protected_files=len(lock),native_financial_callbacks_disabled=True,
      event_eligibility_validated=False,full_program_composed=False)
    dump(out/'checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump(out/'run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/nested-assessment-construction-20261026/verify.py '+sys.argv[1],
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,
      data_version=sha(HERE.parent/'receivable-term-history-20261025/evidence.json'),plan_file='docs/plans/accounting-term-event-carry-binding-20261026.md',
      result_file=str((HERE/'result.md').relative_to(ROOT)),implementation_sha256={n:sha(HERE/n) for n in ['nested_expander.py','declaration.py','verify.py']},
      artifacts=[str(x.relative_to(ROOT)) for x in out.iterdir() if x.is_file()],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
