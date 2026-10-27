"""Bounded selected assessment/carry composition and contrary-binding controls."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,json,subprocess,sys,time
import composition as m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];core=m.core;p=m.p
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);return x
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+chr(10))
population=load('term_command_population',HERE.parent/'term-semantic-composition-20261026/declaration.py')
import receivable_term_history_v1 as native

def main():
    assert len(sys.argv)==2,'fresh attempt name required'
    out=HERE/sys.argv[1];out.mkdir(exist_ok=False);start=time.monotonic();checks=[];controls=[];pairs=[]
    def check(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    lock=read(HERE.parent/'nested-assessment-construction-20261026/attempt-02/source-lock.json')
    for name,h in lock.items():check(sha(ROOT/name)==h,'protected_before:'+name)
    for path in (HERE.parent/'nested-assessment-construction-20261026').glob('*.py'):lock[str(path.relative_to(ROOT))]=sha(path)
    for name in ['checks.json','run-manifest.json','templates.json','results.json']:
        path=HERE.parent/'nested-assessment-construction-20261026/attempt-02'/name;lock[str(path.relative_to(ROOT))]=sha(path)
    for module in list(sys.modules.values()):
        file=getattr(module,'__file__',None)
        if file:
            path=Path(file).resolve()
            if path.is_relative_to(ROOT) and path.is_file() and not path.is_relative_to(HERE):
                name=str(path.relative_to(ROOT))
                if name in lock:check(lock[name]==sha(path),'loaded_pin:'+name)
                lock[name]=sha(path)
    evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases']
    contracts=read(HERE.parent/'term-structural-admission-20261026/contracts.json')
    constructions=read(HERE.parent/'nested-assessment-construction-20261026/attempt-02/templates.json');rules={}
    for chart in contracts:
        path=HERE.parent/'ordered-event-eligibility-20261026/templates'/(chart+'.assess.json');lock[str(path.relative_to(ROOT))]=sha(path)
        rules[chart]=dict(assessment=dict(eligibility=read(path),construction=constructions[chart]),
          carry=dict(mode='preserve_terms_reset_cursor',cursor='/collection_clock/cursor',
            preserve_provenance='Preserve immutable terms and assessment basis',cursor_provenance='New period opens a contiguous assessment window'))
    dump(out/'source-lock.json',lock);dump(out/'rules.json',rules)
    cases=[]
    for chart,case in evidence.items():
        cases.extend((chart+':'+str(i),chart,x['before'],x['request'],x['result']) for i,x in enumerate(case['steps']) if x['request']['operation']=='assess')
        cases.append((chart+':carry',chart,case['carry_before'],case['carry_request'],case['carry']))
    def run(chart,state,request,rules_arg=None,selection=None,coverage=None,call=None):
        contract=contracts[chart];rule=rules[chart] if rules_arg is None else rules_arg
        cov=population.populations(state,contract['semantics']) if coverage is None else coverage
        selected=m.selection_for(contract,rule) if selection is None else selection
        return m.execute(contract,rule,state,request,cov,selected,m.make_call(contract,rule,state,request,cov,selected) if call is None else call)
    # Record native controls before disabling every native financial callback.
    label,chart,state,request,_=cases[0];adverse=[]
    for name,mutate in [
      ('stale_state',lambda q:q.update(expected_state_sha256='0'*64)),
      ('wrong_cursor',lambda q:q['event']['inputs']['start']['value'].update(value='2027-01-01')),
      ('wrong_window',lambda q:q['event'].update(date='2027-03-30')),
      ('unapproved',lambda q:q['event']['inputs']['approved']['value'].update(value=False)),
      ('unknown_input',lambda q:q['event']['inputs']['end_exclusive'].update(value=dict(status='unknown',reason='unavailable'))),
      ('duplicate_event',lambda q:q['event'].update(id=state['book']['seen'][0])),
      ('unknown_input_field',lambda q:q['event']['inputs'].update(extra=deepcopy(q['event']['inputs']['approved']))),
    ]:
        q=deepcopy(request);mutate(q);oracle=native.step(state,q);check(oracle['status']!='proposed',name+':native_refusal')
        adverse.append((name,q,oracle))
    dump(out/'native-controls.json',[dict(case=n,request=q,result=r) for n,q,r in adverse])
    saved=[]
    for module,names in [(native,('validate','step','carry','migrate','state_request','event_types','literal','protected','claim_type','term_type','assessment_type')),
      (native.life,('validate','control','claim_type','event_types','make_request','run','protected')),(native.life.operating,('build','conditions'))]:
        for name in names:saved.append((module,name,getattr(module,name)))
    def disabled(*a,**kw):raise AssertionError('native_financial_callback_in_composition')
    try:
        for module,name,_ in saved:setattr(module,name,disabled)
        with (out/'results.jsonl').open('w') as stream:
            for name,chart,before,req,oracle in cases:
                original=deepcopy((before,req,rules[chart],contracts[chart]));result=run(chart,before,req)
                check(result['status']=='proposed',name+':'+result.get('reason','status'))
                check(result['after']==oracle['after'],name+':complete_after')
                check(p.order_digest(result['after'])==p.order_digest(oracle['after']),name+':after_order')
                if req['profile']=='ReceivableTermEvent/1':
                    check(core.canonical(result['construction']['construction']['request'])==core.canonical(oracle['typed_request']),name+':complete_request')
                    check(core.canonical(result['transition'])==core.canonical(oracle['transition']),name+':complete_transition')
                else:check(core.canonical(result['carry'])==core.canonical(oracle['carry']),name+':complete_carry')
                check(result['before_assessment']['status']==result['after_assessment']['status']=='selected_term_state_satisfied',name+':pre_post')
                check(original==(before,req,rules[chart],contracts[chart]),name+':no_mutation')
                check(all(result[k] is False for k in m.FLAGS),name+':scope')
                stream.write(json.dumps(dict(case=name,result=result),ensure_ascii=False)+chr(10));stream.flush();pairs.append(name)
        _,chart,state,request,_=cases[0]
        for name,q,oracle in adverse:
            result=run(chart,state,q);check(result['status']==oracle['status'],name+':native_status')
            check('after' not in result and not result['provisional_transition'],name+':no_published_after')
            controls.append(dict(case=name,result=result))
        cov=population.populations(state,contracts[chart]['semantics']);cov['terms']['status']='partial'
        result=run(chart,state,request,coverage=cov);check(result['status']=='unresolved' and 'construction' not in result,'partial_population_before_execution')
        controls.append(dict(case='partial_population',result=result))
        changed=deepcopy(rules[chart]);changed['assessment']['construction']['residuals'].append('changed')
        result=run(chart,state,request,rules_arg=changed,selection=m.selection_for(contracts[chart],rules[chart]))
        check(result['status']=='invalid' and result['reason']=='reviewed_term_command','stale_rule_selection');controls.append(dict(case='stale_rule_selection',result=result))
        # A newly selected incorrect rule must fail post-state invariants.
        changed=deepcopy(rules[chart]);operations=changed['assessment']['construction']['row_operations']
        operations[-1]['fields']['value']['fields']['value']={'expr':'literal','type':deepcopy(state['book']['memory_types']['/claims/invoice~1a~01/remaining']),'value':'1/1'}
        result=run(chart,state,request,rules_arg=changed)
        check(result['status']=='invalid' and result['failed_stage']=='after_state' and 'after' not in result and not result['provisional_transition'],'postcondition_blocks_publication')
        controls.append(dict(case='postcondition_blocks_publication',result=result))
        for chart in contracts:
            case=evidence[chart];q=deepcopy(case['carry_request']);q['report_request']['closing']['date']='2027-01-01'
            result=run(chart,case['carry_before'],q)
            check(result['status']=='invalid' and result['reason']=='carry_closing_binding',chart+':wrong_report_binding')
            controls.append(dict(case=chart+':wrong_report_binding',result=result))
    finally:
        for module,name,value in saved:setattr(module,name,value)
        dump(out/'assertions.json',checks);dump(out/'controls.json',controls)
    for name,h in lock.items():check(sha(ROOT/name)==h,'protected_after:'+name)
    summary=dict(passed=True,complete_comparisons=len(pairs),assessment_commands=10,carry_commands=2,
      controls=len(controls),assertions=len(checks),protected_files=len(lock),native_financial_callbacks_disabled=True,
      amendment_binding=False,full_program_composed=False,source_admission=False,accounting_admission=False)
    dump(out/'checks.json',summary);dump(out/'assertions.json',checks)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump(out/'run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/term-event-carry-binding-20261026/verify.py '+sys.argv[1],
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,
      data_version=sha(HERE.parent/'receivable-term-history-20261025/evidence.json'),plan_file='docs/plans/accounting-term-event-carry-binding-20261026.md',
      result_file=str((HERE/'result.md').relative_to(ROOT)),implementation_sha256={n:sha(HERE/n) for n in ['composition.py','verify.py']},
      artifacts=[str(x.relative_to(ROOT)) for x in out.iterdir() if x.is_file()],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
