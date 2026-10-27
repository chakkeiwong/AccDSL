from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,json,subprocess,sys,time
import fixtures as f
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];t=f.t;p=f.p;core=f.core
module_spec=importlib.util.spec_from_file_location('nested_template_controls',HERE/'controls.py')
controls=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(controls)
import receivable_term_history_v1 as terms
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    assert not (HERE/'checks.json').exists(),'passing_evidence_frozen'
    started=time.monotonic();checks=[];cases=[];adverse=[];state_count=0
    def check(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    lock=read(HERE.parent/'query-guard-composition-20261026/source-lock.json')
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    for path in (HERE.parent/'query-guard-composition-20261026').iterdir():
        if path.is_file():lock[str(path.relative_to(ROOT))]=sha(path)
    for module in list(sys.modules.values()):
        file=getattr(module,'__file__',None)
        if not file:continue
        path=Path(file).resolve()
        if path.is_relative_to(ROOT) and path.is_file() and not path.is_relative_to(HERE):
            key=str(path.relative_to(ROOT))
            if key in lock:assert lock[key]==sha(path),key
            lock[key]=sha(path)
    if (HERE/'source-lock.json').exists():assert read(HERE/'source-lock.json')==lock,'dependency_drift'
    else:dump('source-lock.json',lock)
    def compare(label,state,spec,mode):
        before=p.order_digest(state);s_before=p.order_digest(spec)
        actual=f.run(state,spec)
        check('instances' in actual,label+':instances:'+actual.get('reason',''))
        expected=[]
        for owner,claim in state['book']['memory']['claims'].items():
            keys=[None] if mode=='groups' else list(claim['assessments'])
            for key in keys:
                declaration=f.group_declaration(state,owner) if mode=='groups' else f.row_declaration(state,owner,key)
                coverage={name:p.population(item['projection'],state['book'],'complete','Supplied query fixture')
                    for name,item in declaration['queries'].items()}
                result=f.g.run(state,declaration,coverage=coverage)
                independent=f.g.reference(state,declaration)
                check(all(core.canonical(result[k])==core.canonical(v) for k,v in independent.items()),label+':original_dictionary_reference')
                expected.append(dict(index=len(expected),parent_key=owner,child_key=key,
                    captures=f.original_captures(state,spec,owner,key),declaration=declaration,
                    derived_selection=core.digest(declaration),
                    selection_basis='Deterministic substitution from reviewed template; not independent instance review',result=result))
        statuses=[x['result']['status'] for x in expected]
        status=next((s for s in ('invalid','unsupported','unresolved') if s in statuses),
            'requirements_satisfied' if 'requirements_satisfied' in statuses else 'no_active_requirements')
        check(core.canonical(actual['instances'])==core.canonical(expected),label+':all_declarations_captures_results')
        check(actual['status']==status and actual['instance_count']==len(expected),label+':aggregate_status_count')
        check(p.order_digest(state)==before and p.order_digest(spec)==s_before,label+':no_mutation')
        check(not actual['method_eligible'] and all(actual[k] is False for k in p.FLAGS),label+':no_admission')
        cases.append(dict(case=label,state_sha256=core.digest(state),template=deepcopy(spec),actual=actual,expected_instances=expected));return actual
    saved=[]
    for module,names in [(native,('validate','control','claim_type','event_types','make_request','run','protected')),
                         (terms,('validate','step','carry','migrate')),(operating,('build',))]:
        for name in names:saved.append((module,name,getattr(module,name)))
    def disabled(*a,**kw):raise AssertionError('native_financial_callback_during_template')
    try:
        for module,name,_ in saved:setattr(module,name,disabled)
        evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases']
        templates={}
        for chart,case in evidence.items():
            templates[chart]={'rows':f.row_spec(case['final']),'groups':f.group_spec(case['final'])}
            retained=[('migration',case['migration']['state'])]+[(f'event-{i}',r['result']['after']) for i,r in enumerate(case['steps'])]+[('carry',case['carry']['after'])]
            for label,state in retained:
                state_count+=1
                for mode,spec in templates[chart].items():
                    result=compare(chart+':'+label+':'+mode,state,spec,mode)
                    check(result['status'] in ('requirements_satisfied','no_active_requirements'),chart+':'+label+':retained_status')
        controls.exercise(evidence['alpha']['final'],check,compare,adverse)
    finally:
        for module,name,value in saved:setattr(module,name,value)
        dump('assertions.json',checks)
    for n,h in lock.items():check(sha(ROOT/n)==h,'protected:'+n)
    dump('templates.json',templates);dump('cases.json',cases);dump('controls.json',adverse);dump('assertions.json',checks)
    count=sum(len(x['expected_instances']) for x in cases)
    summary=dict(passed=True,retained_states=state_count,complete_runs=len(cases),complete_instance_comparisons=count,
      controls=len(adverse),assertions=len(checks),protected_files=len(lock),native_financial_callbacks_disabled=True,
      new_financial_validator=False,actual_population_completeness=False)
    dump('checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/nested-query-template-20261026/verify.py',
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',
      wall_seconds=time.monotonic()-started,data_version=sha(HERE/'source-lock.json'),
      plan_file='docs/plans/accounting-nested-query-template-20261026.md',result_file='data/accounting-master/nested-query-template-20261026/result.md',
      implementation_sha256={n:sha(HERE/n) for n in ('template.py','fixtures.py','controls.py','verify.py')},
      artifacts=['templates.json','cases.json','controls.json','checks.json','assertions.json','source-lock.json'],
      timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))
if __name__=='__main__':main()
