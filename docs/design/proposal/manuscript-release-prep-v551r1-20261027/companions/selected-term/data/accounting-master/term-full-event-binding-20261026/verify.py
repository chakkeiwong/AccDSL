"""Full chronological retained traces with independently selected event rules."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,json,subprocess,sys,time
import event_declarations as d
m=d.m;core=m.core;p=m.p
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,v):path.write_text(json.dumps(v,ensure_ascii=False,indent=2)+chr(10))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);return x
population=load('full_event_population',HERE.parent/'term-semantic-composition-20261026/declaration.py')
import receivable_term_history_v1 as native

def main():
    assert len(sys.argv)==2,'fresh attempt name required'
    out=HERE/sys.argv[1];out.mkdir(exist_ok=False);start=time.monotonic();checks=[];records=[];traces=[]
    def check(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    lock=read(HERE.parent/'term-event-carry-binding-20261026/attempt-01/source-lock.json')
    for name,h in lock.items():check(sha(ROOT/name)==h,'protected_before:'+name)
    for directory,names in [('term-event-carry-binding-20261026',['composition.py','verify.py','attempt-01/checks.json','attempt-01/rules.json']),
      ('ordered-event-eligibility-20261026',['templates/alpha.collect.json','templates/beta.collect.json']),
      ('parameterized-method-construction-20261026',['templates/alpha.collect.json','templates/beta.collect.json'])]:
        for name in names:
            path=HERE.parent/directory/name;lock[str(path.relative_to(ROOT))]=sha(path)
    for module in list(sys.modules.values()):
        file=getattr(module,'__file__',None)
        if file:
            path=Path(file).resolve()
            if path.is_relative_to(ROOT) and path.is_file() and not path.is_relative_to(HERE):
                name=str(path.relative_to(ROOT))
                if name in lock:check(lock[name]==sha(path),'loaded_pin:'+name)
                lock[name]=sha(path)
    dump(out/'source-lock.json',lock)
    evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases']
    contracts=read(HERE.parent/'term-structural-admission-20261026/contracts.json')
    rules={chart:d.build(chart,case['migration']['state']) for chart,case in evidence.items()};dump(out/'rules.json',rules)
    def run(chart,state,request,rule=None,selection=None,call=None,coverage=None):
        contract=contracts[chart];rule=rules[chart] if rule is None else rule
        cov=population.populations(state,contract['semantics']) if coverage is None else coverage
        selected=m.selection_for(contract,rule) if selection is None else selection
        args=(contract,rule,state,request,cov,selected)
        return m.execute(*args,m.make_call(*args) if call is None else call)
    first=evidence['alpha']['steps'][0];state=first['before'];request=first['request']
    adverse=[]
    for name,mutate in [
      ('stale_prior',lambda q:q['event']['inputs']['prior_term']['value'].update(value='absent')),
      ('missing_claim',lambda q:q['event']['inputs']['claim_id']['value'].update(value='absent')),
      ('wrong_customer',lambda q:q['event']['inputs']['customer']['value'].update(value='other')),
      ('duplicate_term',lambda q:q['event']['inputs']['term_id']['value'].update(value='initial')),
      ('sentinel_term',lambda q:q['event']['inputs']['term_id']['value'].update(value='none')),
      ('blank_term',lambda q:q['event']['inputs']['term_id']['value'].update(value='   ')),
      ('blank_premise',lambda q:q['event']['inputs']['premise']['value'].update(value='   ')),
      ('early_due',lambda q:q['event']['inputs']['due']['value'].update(value='2027-03-01')),
      ('sealed_day',lambda q:q['event'].update(date='2027-02-28')),
      ('unknown_input',lambda q:q['event']['inputs']['premise'].update(value=dict(status='unknown',reason='missing'))),
      ('unapproved',lambda q:q['event']['inputs']['approved']['value'].update(value=False)),
      ('replayed_id',lambda q:q['event'].update(id=state['book']['seen'][0])),
      ('stale_state',lambda q:q.update(expected_state_sha256='0'*64)),
      ('extra_input',lambda q:q['event']['inputs'].update(extra=deepcopy(q['event']['inputs']['approved']))),
    ]:
        q=deepcopy(request);mutate(q);oracle=native.step(state,q)
        check(oracle['status']!='proposed',name+':native_refusal');adverse.append((name,state,q,oracle))
    # Isolate equality of the next effective date while keeping earlier clocks legal.
    same=deepcopy(state);same['book']['date']='2027-01-02';same['book']['memory']['collection_clock']['cursor']='2027-01-01'
    claim=same['book']['memory']['claims']['invoice/a~1'];claim['assessments']={};claim.update(assessed=False,assessment_date='2027-01-02',assessed_remaining='0/1',overdue='0/1',latest_assessment='none')
    # Use native validity only as a pre-run check; do not silently force this synthetic discriminator.
    try:native.validate(same);same_valid=True
    except Exception:same_valid=False
    if same_valid:
        q=deepcopy(request);q['expected_state_sha256']=core.digest(same);q['event']['date']='2027-01-02'
        oracle=native.step(same,q);check(oracle['status']=='invalid','same_effective:native_refusal');adverse.append(('same_effective',same,q,oracle))
    dump(out/'native-controls.json',[dict(case=n,before=b,request=q,result=r) for n,b,q,r in adverse])
    saved=[]
    for module,names in [(native,('validate','step','carry','migrate','state_request','event_types','literal','protected','claim_type','term_type','assessment_type')),
      (native.life,('validate','control','claim_type','event_types','make_request','run','protected')),(native.life.operating,('build','conditions'))]:
        for name in names:saved.append((module,name,getattr(module,name)))
    def disabled(*a,**kw):raise AssertionError('native_financial_callback_in_full_trace')
    complete=0
    try:
        for module,name,_ in saved:setattr(module,name,disabled)
        for chart,case in evidence.items():
            current=deepcopy(case['migration']['state']);cov=population.populations(current,contracts[chart]['semantics'])
            candidates=[('event-'+str(i),r['before'],r['request'],r['result']) for i,r in enumerate(case['steps'])]
            positions=[i for i,r in enumerate(case['steps']) if r['before']==case['carry']['after']]
            check(len(positions)==1,chart+':unique_carry_position');i=positions[0]
            check(i>0 and case['steps'][i-1]['result']['after']==case['carry_before'],chart+':carry_predecessor')
            candidates.insert(i,('carry',case['carry_before'],case['carry_request'],case['carry']))
            trace=[]
            with (out/(chart+'-trace.jsonl')).open('w') as stream:
                for name,before,q,oracle in candidates:
                    check(current==before and p.order_digest(current)==p.order_digest(before),chart+name+':continuous_input')
                    original=deepcopy((current,q,rules[chart]));result=run(chart,current,q,coverage=cov)
                    check(result['status']=='proposed',chart+name+':'+result.get('reason','status'))
                    check(result['after']==oracle['after'] and p.order_digest(result['after'])==p.order_digest(oracle['after']),chart+name+':full_ordered_after')
                    if 'operation' in q:
                        check(core.canonical(result['typed_request'])==core.canonical(oracle['typed_request']),chart+name+':full_request')
                        check(core.canonical(result['transition'])==core.canonical(oracle['transition']),chart+name+':full_transition')
                    else:check(core.canonical(result['carry'])==core.canonical(oracle['carry']),chart+name+':full_carry')
                    check(result['before_assessment']['status']==result['after_assessment']['status']=='selected_term_state_satisfied',chart+name+':pre_post')
                    check(original==(current,q,rules[chart]),chart+name+':no_mutation')
                    check(all(result[k] is False for k in m.FLAGS),chart+name+':scope')
                    stream.write(json.dumps(dict(command=name,result=result),ensure_ascii=False)+chr(10));stream.flush()
                    trace.append(dict(command=name,before_sha256=core.digest(current),after_sha256=core.digest(result['after'])))
                    current=deepcopy(result['after']);cov=result['coverage_after'];complete+=1
            check(current==case['final'],chart+':whole_final');traces.append(dict(chart=chart,commands=trace,final_sha256=core.digest(current)))
        for name,before,q,oracle in adverse:
            result=run('alpha',before,q);check(result['status']==oracle['status'],name+':native_status')
            check('after' not in result and not result['provisional_transition'],name+':no_after')
            records.append(dict(case=name,result=result))
        # Nested accesses must be rejected if prior presence evidence is absent.
        for label,mutate in [
          ('unproved_parent',lambda g:g['stages'][-1]['bindings']['previous'].update(parent_after_stage='missing')),
          ('unproved_child',lambda g:g['stages'][-1]['bindings']['previous'].update(after_stage='missing')),
          ('unknown_nested_field',lambda g:g['stages'][-1]['bindings']['previous'].update(field='missing')),
        ]:
            altered=deepcopy(rules['alpha']);mutate(altered['amendment']['eligibility'])
            result=run('alpha',state,request,rule=altered);check(result['status']=='invalid' and result['failed_stage']=='eligibility',label)
            records.append(dict(case=label,result=result))
        changed=deepcopy(rules['alpha']);changed['amendment']['construction']['residuals'].append('changed')
        result=run('alpha',state,request,rule=changed,selection=m.selection_for(contracts['alpha'],rules['alpha']))
        check(result['status']=='invalid' and result['reason']=='reviewed_term_command','stale_selected_rules');records.append(dict(case='stale_selected_rules',result=result))
        # Correctly typed changed predecessor must be caught by after-state checks.
        changed=deepcopy(rules['alpha']);tree=changed['amendment']['construction']['method_template']['fields']
        term=tree['memory']['fields']['definition']['fields']['operations']['items'][0]['fields']['value']['fields']['fields']['fields']
        term['predecessor']['fields']['value']={'node':'parameter','name':'term_id'}
        changed['amendment']['construction']['parameters']=[x for x in changed['amendment']['construction']['parameters'] if x['name']!='prior_term']
        result=run('alpha',state,request,rule=changed)
        check(result['status']=='invalid' and result['failed_stage']=='after_state' and 'after' not in result,'wrong_term_postcondition')
        records.append(dict(case='wrong_term_postcondition',result=result))
    finally:
        for module,name,value in saved:setattr(module,name,value)
        dump(out/'assertions.json',checks);dump(out/'controls.json',records)
    for name,h in lock.items():check(sha(ROOT/name)==h,'protected_after:'+name)
    dump(out/'traces.json',traces);dump(out/'assertions.json',checks)
    summary=dict(passed=True,complete_comparisons=complete,sequential_traces=len(traces),events=18,carries=2,controls=len(records),
      assertions=len(checks),protected_files=len(lock),native_financial_callbacks_disabled=True,same_effective_discriminator_admitted=same_valid,
      source_for_new_profiles=False,production_ready=False)
    dump(out/'checks.json',summary);git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump(out/'run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/term-full-event-binding-20261026/verify.py '+sys.argv[1],
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,
      data_version=sha(HERE.parent/'receivable-term-history-20261025/evidence.json'),plan_file='docs/plans/accounting-term-event-carry-binding-20261026.md',
      result_file=str((HERE/'result.md').relative_to(ROOT)),implementation_sha256={n:sha(HERE/n) for n in ['full_composition.py','nested_gate.py','event_declarations.py','verify.py']},
      artifacts=[str(x.relative_to(ROOT)) for x in out.iterdir() if x.is_file()],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
