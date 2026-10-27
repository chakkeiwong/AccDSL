from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,json,subprocess,sys,time
import structure as s
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];p=s.p;core=s.core
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
controls=module('structural_controls',HERE/'controls.py')
semantic=module('semantic_bundle_declaration',HERE.parent/'term-semantic-composition-20261026/declaration.py')
import receivable_term_history_v1 as native
import declared_receivable_lifecycle_v1 as life
import declared_operating_methods_v1 as operating
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(name,value):(HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+chr(10))
def coverage_for(state,contract):return semantic.populations(state,contract['semantics'])

def main():
    assert not (HERE/'checks.json').exists(),'passing_evidence_frozen'
    started=time.monotonic();checks=[];pairs=[];adverse=[];oracle=[]
    def check(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    lock=read(HERE.parent/'term-semantic-composition-20261026/source-lock.json')
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    for path in (HERE.parent/'term-semantic-composition-20261026').iterdir():
        if path.is_file():lock[str(path.relative_to(ROOT))]=sha(path)
    for m in list(sys.modules.values()):
        file=getattr(m,'__file__',None)
        if not file:continue
        path=Path(file).resolve()
        if path.is_relative_to(ROOT) and path.is_file() and not path.is_relative_to(HERE):
            name=str(path.relative_to(ROOT))
            if name in lock:assert lock[name]==sha(path),name
            lock[name]=sha(path)
    if (HERE/'source-lock.json').exists():assert read(HERE/'source-lock.json')==lock,'dependency_drift'
    else:dump('source-lock.json',lock)
    contracts=read(HERE/'contracts.json');evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases']
    retained=[]
    for chart,case in evidence.items():
        states=[('migration',case['migration']['state'])]+[(f'event-{i}',r['result']['after']) for i,r in enumerate(case['steps'])]+[('carry',case['carry']['after'])]
        for label,state in states:retained.append((chart+':'+label,state,contracts[chart]))
    base=evidence['alpha']['final'];bad=controls.structural_corruptions(base)
    prior=module('semantic_bundle_verifier',HERE.parent/'term-semantic-composition-20261026/verify.py')
    nested=module('nested_semantic_controls',HERE.parent/'nested-obligation-completion-20261026/controls.py')
    semantic_bad=[(name,state) for name,state,_ in nested.corruptions(base)+prior.common_corruptions(base)]
    def native_check(name,state,expect):
        try:native.validate(state);status='valid';reason=None
        except Exception as exc:status='invalid';reason=str(exc)
        check(status==expect,name+':native:'+str(reason))
        oracle.append(dict(case=name,status=status,reason=reason,state_sha256=core.digest(state)))
    for name,state,_ in retained:native_check(name,state,'valid')
    for name,state in bad+semantic_bad:native_check(name,state,'invalid')
    alternate=deepcopy(base);typ=alternate['book']['memory_types'][alternate['unit_cost_pointer']]
    found,value=p.base.binding.located(alternate['book']['memory'],alternate['unit_cost_pointer']);assert found
    alternate['memory_definition']['root']['fields']['alternate_cost']={'node':'scalar','type':deepcopy(typ)}
    alternate['book']['memory']['alternate_cost']=value;alternate['unit_cost_pointer']='/alternate_cost';controls.retype(alternate)
    native_check('native_valid_unselected_cost',alternate,'valid');dump('native-oracle.json',oracle)
    def compare(label,state,contract,status):
        before=p.order_digest(state);c_before=p.order_digest(contract);coverage=coverage_for(state,contract)
        result=controls.run(contract,state,coverage)
        check(result['status']==status,label+':status:'+result.get('reason',''))
        if 'structure' in result and 'normalized_input' in result['structure']:
            normalized={('opening' if key=='book' else key):deepcopy(value) for key,value in state.items()}
            check(result['structure']['normalized_input']==normalized,label+':full_normalized_input')
            check(result['structure']['normalized_order_sha256']==p.order_digest(normalized),label+':normalized_order')
            stage=s.admission.assess(contract['structure']['template'],normalized,s.admission.make_call(contract['structure']['template'],normalized))
            check(core.canonical(result['structure']['stage_assessment'])==core.canonical(stage),label+':complete_stage_comparison')
        if 'semantics' in result:
            expected=semantic.run(state,contract['semantics'],coverage=coverage)
            check(core.canonical(result['semantics'])==core.canonical(expected),label+':full_semantics')
        check(p.order_digest(state)==before and p.order_digest(contract)==c_before,label+':no_mutation')
        check(all(result[key] is False for key in s.FLAGS),label+':no_execution_or_opening_admission')
        pairs.append(dict(case=label,state_sha256=core.digest(state),result=result))
        return result
    saved=[]
    for m,names in [(native,('validate','step','carry','migrate','protected','claim_type','term_type','assessment_type')),
       (life,('validate','control','claim_type','event_types','make_request','run','protected')),(operating,('build',))]:
        for name in names:saved.append((m,name,getattr(m,name)))
    def disabled(*a,**kw):raise AssertionError('native_financial_callback_in_structural_candidate')
    try:
        for m,name,_ in saved:setattr(m,name,disabled)
        for name,state,contract in retained:compare(name,state,contract,'selected_term_state_satisfied')
        for name,state in bad+semantic_bad:
            result=compare(name,state,contracts['alpha'],'invalid');adverse.append(dict(case=name,result=result))
        controls.contract_controls(base,contracts['alpha'],coverage_for,check,adverse,compare)
    finally:
        for m,name,value in saved:setattr(m,name,value)
        dump('assertions.json',checks)
    for name,h in lock.items():check(sha(ROOT/name)==h,'protected:'+name)
    dump('cases.json',pairs);dump('controls.json',adverse);dump('assertions.json',checks)
    summary=dict(passed=True,retained_states=len(retained),structural_corruptions=len(bad),semantic_corruptions=len(semantic_bad),
      full_comparisons=len(pairs),controls=len(adverse),assertions=len(checks),protected_files=len(lock),native_oracle_cases=len(oracle),
      native_financial_callbacks_disabled_during_candidate=True,future_commands_validated=False,opening_admission=False)
    dump('checks.json',summary);git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/term-structural-admission-20261026/verify.py',
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-started,
      data_version=sha(HERE/'source-lock.json'),plan_file='docs/plans/accounting-term-structural-admission-20261026.md',
      result_file='data/accounting-master/term-structural-admission-20261026/result.md',
      implementation_sha256={n:sha(HERE/n) for n in ('structure.py','prepare.py','controls.py','verify.py')},
      artifacts=['contracts.json','preparation.json','cases.json','controls.json','native-oracle.json','checks.json','assertions.json','source-lock.json'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))
if __name__=='__main__':main()
