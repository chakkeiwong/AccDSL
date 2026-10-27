from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,json,subprocess,sys,time
import fixtures as f
import receivable_term_history_v1 as terms
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];c=f.c;p=f.p;core=f.core
module_spec=importlib.util.spec_from_file_location('query_guard_controls',HERE/'controls.py')
controls=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(controls)
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(name,value):(HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    assert not (HERE/'checks.json').exists(),'passing_evidence_frozen'
    start=time.monotonic();checks=[];pairs=[];adverse=[];states=0
    def check(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    audit=read(HERE/'guard-audit.json');assert audit['passed'] and len(audit['cases'])==18
    lock=read(HERE.parent/'grouped-row-query-20261026/source-lock.json')
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    for path in (HERE.parent/'grouped-row-query-20261026').iterdir():
        if path.is_file():lock[str(path.relative_to(ROOT))]=sha(path)
    for n,h in audit['source_hashes'].items():assert sha(ROOT/n)==h,n
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if not name:continue
        path=Path(name).resolve()
        if path.is_relative_to(ROOT) and path.is_file() and not path.is_relative_to(HERE):
            key=str(path.relative_to(ROOT))
            if key in lock:assert lock[key]==sha(path),key
            lock[key]=sha(path)
    if (HERE/'source-lock.json').exists():assert read(HERE/'source-lock.json')==lock,'dependency_drift'
    else:dump('source-lock.json',lock)
    def compare(label,state,spec):
        before=p.order_digest(state);d_before=p.order_digest(spec)
        actual=f.run(state,spec);expected=f.reference(state,spec)
        fields={'status','reason','query_vetoes','bound_values','lineage','assessment'}
        outcome={k:v for k,v in actual.items() if k in fields}
        check(core.canonical(outcome)==core.canonical(expected),label+':full_comparison:'+actual.get('reason',''))
        check(p.order_digest(state)==before and p.order_digest(spec)==d_before,label+':no_mutation')
        check(not actual['method_eligible'] and all(actual[k] is False for k in p.FLAGS),label+':no_admission')
        pairs.append(dict(case=label,state_sha256=core.digest(state),declaration=spec,actual=actual,expected=expected));return actual
    saved=[]
    for module,names in [(native,('validate','control','claim_type','event_types','make_request','run','protected')),
                         (terms,('validate','step','carry','migrate')),(operating,('build',))]:
        for name in names:saved.append((module,name,getattr(module,name)))
    def disabled(*a,**kw):raise AssertionError('native_financial_callback_during_composition')
    try:
        for module,name,_ in saved:setattr(module,name,disabled)
        evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases']
        for chart,case in evidence.items():
            retained=[('migration',case['migration']['state'])]+[(f'event-{i}',r['result']['after']) for i,r in enumerate(case['steps'])]+[('carry',case['carry']['after'])]
            for label,state in retained:
                states+=1
                for owner,claim in state['book']['memory']['claims'].items():
                    compare(chart+':'+label+':presence',state,f.presence_spec(state,owner))
                    for assessment in claim['assessments']:
                        actual=compare(chart+':'+label+':'+assessment,state,f.history_spec(state,owner,assessment))
                        check(actual['status']=='requirements_satisfied',chart+':'+label+':historical_relations')
        controls.exercise(evidence['alpha']['final'],check,compare,adverse)
    finally:
        for module,name,value in saved:setattr(module,name,value)
        dump('assertions.json',checks)
    for n,h in lock.items():check(sha(ROOT/n)==h,'protected:'+n)
    dump('cases.json',pairs);dump('controls.json',adverse);dump('assertions.json',checks)
    summary=dict(passed=True,guard_truth_table_cases=18,retained_states=states,complete_comparisons=len(pairs),
       controls=len(adverse),assertions=len(checks),protected_files=len(lock),native_financial_callbacks_disabled=True,
       new_financial_validator=False,actual_population_completeness=False)
    dump('checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/query-guard-composition-20261026/verify.py',
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',
      wall_seconds=time.monotonic()-start,data_version=sha(HERE/'source-lock.json'),
      plan_file='docs/plans/accounting-query-guard-composition-20261026.md',result_file='data/accounting-master/query-guard-composition-20261026/result.md',
      implementation_sha256={n:sha(HERE/n) for n in ('compose.py','fixtures.py','controls.py','verify.py','probe.py')},
      artifacts=['cases.json','controls.json','checks.json','assertions.json','source-lock.json','guard-audit.json','design.md'],
      timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))
if __name__=='__main__':main()
