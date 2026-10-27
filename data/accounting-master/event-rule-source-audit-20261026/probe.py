from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,sys,subprocess,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'invariant-source-authoring-20261026'))
import program_text as program
import invariant_text
requirements=program.prior.method_text.requirements
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+chr(10))
def main():
    start=time.monotonic();lock_path=HERE/'source-lock.json'
    if not lock_path.exists():
        paths=[HERE.parent/'invariant-source-authoring-20261026'/n for n in ('program_text.py','invariant_text.py')]
        paths += [HERE.parent/'common-program-authoring-20261026'/n for n in ('common_text.py','source_export.py')]
        paths += [HERE.parent/'complete-method-authoring-20261026/frontend.py',ROOT/'scripts/method_requirement_text_v2.py',ROOT/'scripts/method_requirement_text_v1.py']
        for owner in ('alpha','beta'):
            paths += [HERE.parent/f'invariant-source-authoring-20261026/examples/{owner}.{s}' for s in ('acc','resources.json','compiled.json')]
        dump('source-lock.json',{str(p.relative_to(ROOT)):sha(p) for p in paths if p.exists()})
    lock=read(lock_path)
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    probes=[]
    for owner in ('alpha','beta'):
        path=HERE.parent/f'invariant-source-authoring-20261026/examples/{owner}.acc';source=path.read_text()
        resources=read(path.with_suffix('.resources.json'));compiled=program.compile_text(source,resources)
        assert compiled['status']=='compiled_structural',compiled
        probes.append(dict(company=owner,case='current_source',source=str(path.relative_to(ROOT)),source_sha256=sha(path),status=compiled['status'],target=compiled['program']['profile'],native_contract_present='event_contract' in compiled['program']))
        for label,changed in [
            ('new_program_target',source.replace('ContractedAuthoredCompanyProgram/1','DeclarativeEventCompanyProgram/1',1)),
            ('new_bound_target',source.replace('ContractedAuthoredCompanyProgram/1','AdmittedDeclarativeProgram/1',1)),
            ('new_opening_source',source.replace('begin_invariant_source;','begin_opening_admission;\nend_opening_admission;\nbegin_invariant_source;',1)),
            ('new_eligibility_source',source.replace('begin_invariant_source;','begin_ordered_eligibility;\nend_ordered_eligibility;\nbegin_invariant_source;',1))]:
            result=program.compile_text(changed,resources);assert result['status']=='invalid',(label,result)
            (HERE/f'{owner}.{label}.acc').write_text(changed)
            probes.append(dict(company=owner,case=label,source=f'{owner}.{label}.acc',source_sha256=sha(HERE/f'{owner}.{label}.acc'),result=result))
    template=read(HERE.parent/'ordered-event-eligibility-20261026/templates/alpha.collect.json')
    reused=[]
    for stage in template['stages']:
        manifest=stage['manifest'];exchange={'profile':requirements.EXCHANGE,'definition':manifest,'selected_digest':program.prior.digest(manifest),'values':{},'available_capabilities':[]}
        source=requirements.render(exchange);lowered=requirements.lower(source)
        assert lowered==exchange
        reused.append(dict(stage=stage['id'],source=source,complete_exchange_equal=True))
    specs=[
      ('facts_resources','common-program-authoring-20261026/common_text.py','compile_text','Opening, schemas, mapping and memory definition are hash-checked imports','Reuse resource handling; these are facts/schema resources, not inferred algorithms'),
      ('full_method','complete-method-authoring-20261026/frontend.py','lower','Full instantiated pre/post predicates, monetary calculations, postings, flows and memory writes are visible','Reuse ordinary method syntax; explicit parameter/row recipe layer still absent'),
      ('predicate','../scripts/method_requirement_text_v2.py','lower','Guarded predicates and dimensional inputs already have source grammar','Reuse renderer/parser; four complete manifests roundtrip exactly'),
      ('invariant','invariant-source-authoring-20261026/invariant_text.py','lower','Finite invariant is directly authored, including row rules and totals','Reuse inline invariant source; do not re-import opaque invariant result'),
      ('opening','declared-opening-admission-20261026/admission.py','compile_template','21 typed/structural ordered opening stages exist only as typed data','Need direct ordered opening declarations with typed-source locations'),
      ('eligibility','ordered-event-eligibility-20261026/gate.py','compile_template','Typed sources, ordered manifests and safe map-field dependency exist as data','Need explicit stage and binding syntax around reused predicate blocks'),
      ('parameters','parameterized-method-construction-20261026/constructor.py','construct','Typed parameters and structural method AST exist as data','Need direct parameters/template nodes; no whole-method JSON blob'),
      ('rows','ordered-assessment-expansion-20261026/expander.py','construct','Ordered map expansion and typed row expressions exist as data','Need direct row expressions/operation declarations, including both branches'),
      ('selection_binding','admitted-program-binding-20261026/binding.py','execute','Selection matches full roles, policy, rules, invariant, facts and commands','Derive hashes from authored definitions, never silently skip binding'),
      ('program_target','invariant-source-authoring-20261026/program_text.py','compile_text','Latest source lowers to old native-contract/guarded targets','Add explicit target after component source contracts; source success not runtime admission')]
    mapping=[]
    for key,relative,function,current,next_step in specs:
        path=ROOT/'scripts/method_requirement_text_v2.py' if relative.startswith('../') else HERE.parent/relative
        functions={x.name:[x.lineno,x.end_lineno] for x in ast.parse(path.read_text()).body if isinstance(x,ast.FunctionDef)}
        mapping.append(dict(component=key,source=str(path.relative_to(ROOT)),source_sha256=sha(path),function=function,lines=functions[function],current=current,next=next_step))
    dump('probes.json',probes);dump('reused-requirements.json',reused);dump('authoring-map.json',mapping)
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    summary=dict(passed=True,current_source_programs=2,new_source_refusals=8,reused_requirement_manifests=4,mapped_components=10,protected_files=len(lock),new_source_frontend_implemented=False)
    dump('checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/event-rule-source-audit-20261026/probe.py',environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version=sha(lock_path),plan_file='docs/plans/accounting-event-rule-source-audit-20261026.md',result_file='data/accounting-master/event-rule-source-audit-20261026/result.md',artifacts=['authoring-map.json','probes.json','reused-requirements.json','checks.json'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))
if __name__=='__main__':main()
