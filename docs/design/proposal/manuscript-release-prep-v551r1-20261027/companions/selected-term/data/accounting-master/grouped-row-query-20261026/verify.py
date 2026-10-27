from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
import fixtures as f
import controls
import receivable_term_history_v1 as terms
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
q=f.q;p=f.p;HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(name,value):(HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
    assert not (HERE/'checks.json').exists(),'passing_evidence_frozen'
    start=time.monotonic();checks=[];cases=[];adverse=[];state_count=0
    def ensure(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    lock=read(HERE.parent/'nested-map-projection-20261026/source-lock.json')
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    for path in (HERE.parent/'nested-map-projection-20261026').iterdir():
        if path.is_file():lock[str(path.relative_to(ROOT))]=sha(path)
    for module in list(sys.modules.values()):
        file=getattr(module,'__file__',None)
        if not file:continue
        path=Path(file).resolve()
        if path.is_relative_to(ROOT) and path.is_file() and not path.is_relative_to(HERE):
            key=str(path.relative_to(ROOT))
            if key in lock:assert sha(path)==lock[key],key
            lock[key]=sha(path)
    if (HERE/'source-lock.json').exists():
        ensure(read(HERE/'source-lock.json')==lock,'frozen_dependencies_same_on_repair')
    else:dump('source-lock.json',lock)
    def compare(label,state,kind,decl):
        before=p.order_digest(state);d_before=p.order_digest(decl)
        actual=f.run(state,kind,decl);expected=f.reference(state,kind,decl)
        fields={'status','reason','group','count','candidate_indices','candidate_count','selected_indices',
            'selected','selected_lineage','failed_stage'}
        outcome={k:v for k,v in actual.items() if k in fields}
        ensure(p.core.canonical(outcome)==p.core.canonical(expected),label+':complete_outcome:'+actual.get('reason',''))
        ensure(p.order_digest(state)==before and p.order_digest(decl)==d_before,label+':inputs_unchanged')
        ensure(all(actual[k] is False for k in p.FLAGS),label+':no_admission')
        ensure(actual['projection']['status']=='projected',label+':fresh_projection')
        cases.append(dict(case=label,state_sha256=p.core.digest(state),query=deepcopy(decl),actual=actual,expected=expected))
        return actual
    saved=[]
    for module,names in [(native,('validate','control','claim_type','event_types','make_request','run','protected')),
                         (terms,('validate','step','carry','migrate')),(operating,('build',))]:
        for name in names:saved.append((module,name,getattr(module,name)))
    def disabled(*args,**kwargs):raise AssertionError('native_financial_callback_during_query')
    try:
        for module,name,_ in saved:setattr(module,name,disabled)
        evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases']
        for chart,case in evidence.items():
            states=[('migration',case['migration']['state'])]+[(f'event-{i}',r['result']['after']) for i,r in enumerate(case['steps'])]+[('carry',case['carry']['after'])]
            for label,state in states:
                state_count+=1
                for owner,claim in state['book']['memory']['claims'].items():
                    for kind,datefield in [('terms','effective'),('assessments','as_of')]:
                        prefix=chart+':'+label+':'+kind
                        compare(prefix+':count',state,kind,f.declaration(state,kind,owner,'count'))
                        compare(prefix+':latest',state,kind,f.declaration(state,kind,owner,'greatest',datefield))
                        for key,row in claim[kind].items():
                            compare(prefix+':id:'+key,state,kind,f.declaration(state,kind,owner,'match','identity',value=key))
                            for inclusive in (True,False):
                                compare(prefix+':boundary:'+key+':'+str(inclusive),state,kind,
                                  f.declaration(state,kind,owner,'greatest',datefield,bound=row[datefield],inclusive=inclusive))
                        compare(prefix+':absent',state,kind,f.declaration(state,kind,owner,'match','identity',value='not-present'))
                    for key,row in claim['assessments'].items():
                        actual=compare(chart+':'+label+':applicable:'+key,state,'terms',
                          f.declaration(state,'terms',owner,'greatest','effective',bound=row['as_of'],allow_empty=False))
                        ensure(actual['selected']['identity']['value']==row['term_id'],chart+':'+label+':retained_applicable_term')
        controls.exercise(evidence['alpha']['final'],ensure,compare,adverse)
    finally:
        for module,name,value in saved:setattr(module,name,value)
        dump('assertions.json',checks)
    for name,h in lock.items():ensure(sha(ROOT/name)==h,'protected:'+name)
    dump('cases.json',cases);dump('controls.json',adverse);dump('assertions.json',checks)
    summary=dict(passed=True,retained_states=state_count,complete_comparisons=len(cases),controls=len(adverse),
        assertions=len(checks),protected_files=len(lock),native_financial_callbacks_disabled=True,
        accounting_admission=False,actual_population_completeness=False,new_financial_validator=False)
    dump('checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/grouped-row-query-20261026/verify.py',
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',
      wall_seconds=time.monotonic()-start,data_version=sha(HERE/'source-lock.json'),
      plan_file='docs/plans/accounting-grouped-row-query-20261026.md',result_file='data/accounting-master/grouped-row-query-20261026/result.md',
      implementation_sha256={n:sha(HERE/n) for n in ('query.py','fixtures.py','controls.py','verify.py')},
      artifacts=['cases.json','controls.json','checks.json','assertions.json','source-lock.json','design.md'],
      timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

if __name__=='__main__':main()
