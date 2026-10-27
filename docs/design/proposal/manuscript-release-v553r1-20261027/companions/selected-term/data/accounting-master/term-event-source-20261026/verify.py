"""Whole source/typed/result correspondence with Unicode and rejection controls."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
from hashlib import sha256
import importlib.util,json,subprocess,sys,time
import event_text as t
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];base=HERE.parent/'term-full-event-binding-20261026';m=t.full;core=t.core;p=t.ct.s.p
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,v):path.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);return v
population=load('source_event_population',HERE.parent/'term-semantic-composition-20261026/declaration.py')
import receivable_term_history_v1 as native

def main():
    assert len(sys.argv)==2,'fresh attempt required'
    out=HERE/sys.argv[1];out.mkdir(exist_ok=False);start=time.monotonic();checks=[];controls=[]
    def check(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    lock=read(base/'attempt-01/source-lock.json')
    for n,h in lock.items():check(sha(ROOT/n)==h,'protected_before:'+n)
    for name in ['full_composition.py','nested_gate.py','event_declarations.py','verify.py','date-boundary.py','date-boundary.json',
      'attempt-01/rules.json','attempt-01/checks.json','attempt-01/alpha-trace.jsonl','attempt-01/beta-trace.jsonl']:
        path=base/name;lock[str(path.relative_to(ROOT))]=sha(path)
    for mod in list(sys.modules.values()):
        file=getattr(mod,'__file__',None)
        if file:
            path=Path(file).resolve()
            if path.is_relative_to(ROOT) and path.is_file() and not path.is_relative_to(HERE):
                name=str(path.relative_to(ROOT))
                if name in lock:check(lock[name]==sha(path),'import_pin:'+name)
                lock[name]=sha(path)
    dump(out/'source-lock.json',lock)
    rules=read(base/'attempt-01/rules.json');contracts=read(HERE.parent/'term-structural-admission-20261026/contracts.json')
    evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases'];sources={};contract_sources={}
    for chart,rule in rules.items():
        sources[chart]={name:t.render(value,carry=name=='carry') for name,value in rule.items()}
        for name,source in sources[chart].items():
            lowered=t.lower(source,carry=name=='carry');check(p.order_digest(lowered['rule'])==p.order_digest(rule[name]),chart+name+':exact_typed_order')
            (out/(chart+'.'+name+'.accdsl')).write_text(source)
        contract_sources[chart]=(HERE.parent/'nested-contract-source-20261026/attempt-01'/(chart+'.accdsl')).read_text()
    # Manually authored nested binding, independent of the renderer.
    manual='''binding;
kind nested_map_field;
pointer "/claims";
key_input "claim_id";
parent_after_stage "claim_exists";
child_pointer "/terms";
child_key_input "prior_term";
field "effective";
after_stage "prior_exists";
end;
'''
    parser=t.Parser(manual);r,loc=parser.next();r.take('word','binding');actual=parser.item(t.B('event_binding_source'),r,loc,'',0)
    expected=dict(kind='nested_map_field',pointer='/claims',key_input='claim_id',parent_after_stage='claim_exists',child_pointer='/terms',child_key_input='prior_term',field='effective',after_stage='prior_exists')
    check(actual==expected and p.order_digest(actual)==p.order_digest(expected),'independent_nested_binding')
    (out/'manual-binding.accdsl').write_text(manual)
    def run(chart,state,request,src=None,selection=None):
        src=sources[chart] if src is None else src;rule=rules[chart];contract=contracts[chart]
        cov=population.populations(state,contract['semantics']);selection=m.selection_for(contract,rule) if selection is None else selection
        decoded={name:t.lower(text,carry=name=='carry')['rule'] for name,text in src.items()}
        call=m.make_call(contract,decoded,state,request,cov,selection)
        return t.execute_sources(contract_sources[chart],src,evidence[chart]['final']['memory_definition'],state,request,cov,selection,call)
    def reject(name,source,reason):
        try:t.lower(source)
        except t.Invalid as exc:
            check(reason in exc.reason,name+':reason:'+exc.reason);loc=exc.location
            check(isinstance(loc,dict),name+':location');raw=source.encode();a,b=loc['byte_start'],loc['byte_end']
            check(sha256(raw[a:b]).hexdigest()==loc['slice_sha256'] and loc['line']==raw[:a].count(b'\n')+1,name+':exact_span')
            controls.append(dict(case=name,reason=exc.reason,location=loc))
        else:raise AssertionError(name+':accepted')
    saved=[]
    for mod,names in [(native,('validate','step','carry','migrate','state_request','event_types','literal','protected','claim_type','term_type','assessment_type')),
      (native.life,('validate','control','claim_type','event_types','make_request','run','protected')),(native.life.operating,('build','conditions'))]:
        for name in names:saved.append((mod,name,getattr(mod,name)))
    def disabled(*a,**kw):raise AssertionError('native_callback_in_source_trace')
    comparisons=0;span_count=0
    try:
        for mod,name,_ in saved:setattr(mod,name,disabled)
        for chart,case in evidence.items():
            before=deepcopy(case['migration']['state']);expected=[json.loads(x) for x in (base/'attempt-01'/(chart+'-trace.jsonl')).read_text().splitlines()]
            with (out/(chart+'-trace.jsonl')).open('w') as stream:
                for item in expected:
                    name=item['command'];request=case['carry_request'] if name=='carry' else case['steps'][int(name.split('-')[1])]['request']
                    result=run(chart,before,request);execution=result['execution']
                    check(core.canonical(execution)==core.canonical(item['result']),chart+name+':complete_result')
                    check(p.order_digest(execution)==p.order_digest(item['result']),chart+name+':result_order')
                    check(not result['source_diagnostics'],chart+name+':no_source_error')
                    before=deepcopy(execution['after']);comparisons+=1
                    stream.write(json.dumps(dict(command=name,result=result),ensure_ascii=False)+chr(10));stream.flush()
            check(before==case['final'],chart+':whole_final')
        rule=deepcopy(rules['alpha']['assessment']);rule['construction']['residuals'].append('公司 café e\u0301 \u2028 \u2029 😀')
        source=t.render(rule)
        for label,text in [('unicode_lf',source),('unicode_crlf',source.replace('\n','\r\n'))]:
            lowered=t.lower(text);check(p.order_digest(lowered['rule'])==p.order_digest(rule),label+':unicode')
            for loc in lowered['locations'].values():
                raw=text.encode();a,b=loc['byte_start'],loc['byte_end'];check(sha256(raw[a:b]).hexdigest()==loc['slice_sha256'] and loc['line']==raw[:a].count(b'\n')+1,label+':span');span_count+=1
            (out/(label+'.accdsl')).write_bytes(text.encode())
        source=sources['alpha']['assessment']
        reject('unknown_row_operator',source.replace('(operation_id ', '(mystery ',1),'row_operator:mystery')
        reject('truncated_row',source.replace('(operation_id "term.")','(operation_id "term."',1),'token_kind:')
        reject('duplicate_row_field',source.replace('(field "op" ', '(field "id" ',1),'duplicate_row_field')
        reject('opaque_construction',source.replace('construction "OrderedNestedMethodExpansion/1";', 'construction {};',1),'construction_profile')
        reject('unknown_directive',source.replace('map_pointer ', 'resource_import ',1),'unknown_declaration:expansion')
        reject('unknown_parameter_expression',sources['alpha']['amendment'].replace('(parameter "due")','(missing "due")',1),'data_operator:missing')
        first=evidence['alpha']['steps'][0];state=first['before'];request=first['request']
        revised=deepcopy(sources['alpha']);rule=deepcopy(rules['alpha']['amendment']);rule['construction']['residuals'].append('changed');revised['amendment']=t.render(rule)
        result=run('alpha',state,request,revised)['execution'];check(result['status']=='invalid' and result['reason']=='reviewed_term_command','stale_source_selection');controls.append(dict(case='stale_source_selection',result=result))
        # A newly selected invalid constructor receives a source component span.
        rule=deepcopy(rules['alpha']['amendment']);rule['construction']['parameters'][-1]['source']['segments'][-1]={'parameter':'missing'}
        revised=deepcopy(sources['alpha']);revised['amendment']=t.render(rule);decoded=deepcopy(rules['alpha']);decoded['amendment']=rule
        result=run('alpha',state,request,revised,m.selection_for(contracts['alpha'],decoded))
        check(result['execution']['status']=='invalid' and result['execution']['failed_stage']=='construction','invalid_constructor_refusal')
        check(result['source_diagnostics'][0]['location']==t.lower(revised['amendment'])['locations']['/construction'],'constructor_location')
        controls.append(dict(case='invalid_constructor',result=result))
        # Invalid nested membership reference is located before execution.
        rule=deepcopy(rules['alpha']['amendment']);rule['eligibility']['stages'][-1]['bindings']['previous']['after_stage']='absent';source=t.render(rule)
        try:t.compile_rule(source,state['book'],state['memory_definition'])
        except t.Invalid as exc:
            check(exc.location==t.lower(source)['locations']['/eligibility'],'nested_eligibility_location');controls.append(dict(case='nested_eligibility',reason=exc.reason,location=exc.location))
        else:raise AssertionError('invalid_nested_eligibility_accepted')
    finally:
        for mod,name,value in saved:setattr(mod,name,value)
        dump(out/'assertions.json',checks);dump(out/'controls.json',controls)
    for n,h in lock.items():check(sha(ROOT/n)==h,'protected_after:'+n)
    summary=dict(passed=True,complete_comparisons=comparisons,sequential_traces=2,event_sources=6,carry_sources=2,controls=len(controls),unicode_span_checks=span_count,
      assertions=len(checks),protected_files=len(lock),native_callbacks_disabled=True,production_ready=False)
    dump(out/'checks.json',summary);dump(out/'assertions.json',checks);git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump(out/'run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/term-event-source-20261026/verify.py '+sys.argv[1],
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,
      data_version=sha(base/'attempt-01/rules.json'),plan_file='docs/plans/accounting-term-event-source-20261026.md',result_file=str((HERE/'result.md').relative_to(ROOT)),
      implementation_sha256={n:sha(HERE/n) for n in ['event_text.py','verify.py']},artifacts=[str(x.relative_to(ROOT)) for x in out.iterdir() if x.is_file()],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
