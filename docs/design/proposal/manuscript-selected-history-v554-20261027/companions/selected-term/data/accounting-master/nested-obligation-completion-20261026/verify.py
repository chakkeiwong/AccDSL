from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,json,subprocess,sys,time
import declarations as d
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];t=d.t;p=d.p;core=d.core
import receivable_term_history_v1 as terms
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bridge_expected(state,spec):
    values={'globals':{},'collections':{}};lineage={}
    for name,b in spec['bindings'].items():
        rows=[];origins=[]
        if b['kind']=='seen':
            for i,value in enumerate(state['book']['seen']):
                rows.append({field:dict(status='known',value=value) for field in b['fields']})
                origins.append(dict(source_index=i,fields={field:dict(path='/seen/'+str(i),kind='seen',type=p.guards.TEXT) for field in b['fields']}))
        else:
            kind=spec['sources'][b['source']]['child_pointer'][1:];index=0
            for owner,claim in state['book']['memory']['claims'].items():
                for key,row in claim[kind].items():
                    condition=b['filter'];include=condition is None or row[condition['field']]==condition['value']
                    if include:
                        rows.append({field:dict(status='known',value=row[target]) for field,target in b['fields'].items()})
                        path='/memory'+d.f.f.pointer(['claims',owner,kind,key])
                        origins.append(dict(source_index=index,parent_key=owner,child_key=key,fields={field:
                            dict(path=path+'/'+target,kind='child_field',type=state['book']['memory_types'][path[len('/memory'):]+'/'+target]) for field,target in b['fields'].items()}))
                    index+=1
        values['collections'][name]=dict(status='complete',rows=rows)
        lineage[name]=dict(binding=deepcopy(b),rows=origins,completeness='Explicit predicate over complete supplied source' if b['kind']=='projected' else 'Complete supplied book seen sequence')
    result=d.bridge.engine.assess(spec['definition'],values,[])
    return dict(status=result['status'],values=values,lineage=lineage,assessment=result)

def main():
    assert not (HERE/'checks.json').exists(),'passing_evidence_frozen'
    started=time.monotonic();checks=[];cases=[];adverse=[];oracle=[]
    def check(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    lock=read(HERE.parent/'nested-query-template-20261026/source-lock.json')
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    for path in (HERE.parent/'nested-query-template-20261026').iterdir():
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
    evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases'];retained=[]
    for chart,case in evidence.items():
        states=[('migration',case['migration']['state'])]+[(f'event-{i}',r['result']['after']) for i,r in enumerate(case['steps'])]+[('carry',case['carry']['after'])]
        for label,state in states:
            terms.validate(state);oracle.append(dict(case=chart+':'+label,status='valid',state_sha256=core.digest(state)))
            retained.append((chart+':'+label,state))
    spec_mod=importlib.util.spec_from_file_location('nested_obligation_controls',HERE/'controls.py')
    controls=importlib.util.module_from_spec(spec_mod);spec_mod.loader.exec_module(controls)
    mutations=controls.corruptions(evidence['alpha']['final'])
    for label,state,section in mutations:
        try:terms.validate(state);verdict='valid';reason=None
        except Exception as exc:verdict='invalid';reason=str(exc)
        check(verdict=='invalid',label+':native_oracle_rejects')
        oracle.append(dict(case=label,status=verdict,reason=reason,state_sha256=core.digest(state)))
    dump('native-oracle.json',oracle)
    def compare_template(label,state,spec,kind):
        before=p.order_digest(state);actual=d.f.run(state,spec);check('instances' in actual,label+':instances:'+actual.get('reason',''))
        expected=[];childmap='terms' if kind=='terms' else 'assessments'
        for owner,claim in state['book']['memory']['claims'].items():
            for key in claim[childmap]:
                declaration=d.term_declaration(state,owner,key) if kind=='terms' else d.assessment_declaration(state,owner,key)
                coverage={name:p.population(item['projection'],state['book'],'complete','Supplied query fixture') for name,item in declaration['queries'].items()}
                result=d.g.run(state,declaration,coverage=coverage)
                expected.append(dict(parent_key=owner,child_key=key,declaration=declaration,result=result))
        for a,b in zip(actual['instances'],expected):
            check(all(core.canonical(a[k])==core.canonical(v) for k,v in b.items()),label+':full_instance')
        check(len(actual['instances'])==len(expected),label+':all_instances')
        check(p.order_digest(state)==before,label+':no_mutation')
        check(all(actual[k] is False for k in p.FLAGS),label+':no_admission')
        cases.append(dict(case=label,kind=kind,actual=actual,expected_instances=expected));return actual
    def compare_bridge(label,state,spec):
        before=p.order_digest(state);actual=d.run_bridge(state,spec);expected=bridge_expected(state,spec)
        check(all(core.canonical(actual.get(k))==core.canonical(v) for k,v in expected.items()),label+':complete_rows_lineage_assessment:'+actual.get('reason',''))
        check(p.order_digest(state)==before,label+':no_mutation')
        check(all(actual[k] is False for k in p.FLAGS),label+':no_admission')
        cases.append(dict(case=label,kind='events',actual=actual,expected=expected));return actual
    saved=[]
    for module,names in [(native,('validate','control','claim_type','event_types','make_request','run','protected')),
                         (terms,('validate','step','carry','migrate')),(operating,('build',))]:
        for name in names:saved.append((module,name,getattr(module,name)))
    def disabled(*a,**kw):raise AssertionError('native_callback_during_declarative_evaluation')
    templates={chart:dict(terms=d.term_template(case['final']),assessments=d.assessment_template(case['final']),events=d.event_collections(case['final'])) for chart,case in evidence.items()}
    try:
        for module,name,_ in saved:setattr(module,name,disabled)
        for label,state in retained:
            selected=templates[label.split(':')[0]]
            for kind in ('terms','assessments'):
                result=compare_template(label+':'+kind,state,selected[kind],kind)
                check(result['status'] in ('requirements_satisfied','no_active_requirements'),label+':'+kind+':valid')
            result=compare_bridge(label+':events',state,selected['events']);check(result['status']=='collection_requirements_satisfied',label+':events:valid')
        for label,state,section in mutations:
            selected=templates['alpha'][section]
            result=compare_bridge(label,state,selected) if section=='events' else compare_template(label,state,selected,section)
            check(result['status']=='invalid',label+':candidate_rejects')
            adverse.append(dict(case=label,section=section,result=result))
        controls.bridge_controls(evidence['alpha']['final'],check,compare_bridge,adverse)
    finally:
        for module,name,value in saved:setattr(module,name,value)
        dump('assertions.json',checks)
    for n,h in lock.items():check(sha(ROOT/n)==h,'protected:'+n)
    dump('declarations.json',templates);dump('cases.json',cases);dump('controls.json',adverse);dump('assertions.json',checks)
    summary=dict(passed=True,retained_states=len(retained),complete_runs=len(cases),controls=len(adverse),
       assertions=len(checks),protected_files=len(lock),native_oracle_cases=len(oracle),
       native_financial_callbacks_disabled_during_candidate=True,full_native_validator_replacement=False)
    dump('checks.json',summary);git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/nested-obligation-completion-20261026/verify.py',
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-started,
      data_version=sha(HERE/'source-lock.json'),plan_file='docs/plans/accounting-nested-obligation-completion-20261026.md',
      result_file='data/accounting-master/nested-obligation-completion-20261026/result.md',
      implementation_sha256={n:sha(HERE/n) for n in ('collections_bridge.py','declarations.py','controls.py','verify.py')},
      artifacts=['declarations.json','cases.json','controls.json','native-oracle.json','checks.json','assertions.json','source-lock.json'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))
if __name__=='__main__':main()
