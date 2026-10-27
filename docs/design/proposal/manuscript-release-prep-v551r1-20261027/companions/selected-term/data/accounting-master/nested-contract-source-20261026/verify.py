"""Bounded exact correspondence against frozen typed-contract evidence."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,json,subprocess,sys,time
import contract_text as t

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=HERE.parent/'term-structural-admission-20261026'
s=t.s;p=s.p;core=s.core
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
prior=module('structural_source_comparator',BASE/'verify.py')
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+chr(10))

def main():
    assert len(sys.argv)==2,'provide fresh attempt directory'
    out=HERE/sys.argv[1];out.mkdir(exist_ok=False)
    start=time.monotonic();assertions=[];controls=[];counts=dict(full_comparisons=0,source_controls=0)
    def check(ok,label):
        assertions.append(dict(check=label,passed=bool(ok)))
        if not ok:raise AssertionError(label)
    lock=read(BASE/'source-lock.json')
    for n,h in lock.items():check(sha(ROOT/n)==h,'protected_before:'+n)
    for name in ['contracts.json','cases.json','checks.json','controls.json','run-manifest.json','structure.py','controls.py','verify.py']:
        q=BASE/name;lock[str(q.relative_to(ROOT))]=sha(q)
    for m in list(sys.modules.values()):
        file=getattr(m,'__file__',None)
        if not file:continue
        path=Path(file).resolve()
        if path.is_relative_to(ROOT) and path.is_file() and not path.is_relative_to(HERE):
            name=str(path.relative_to(ROOT))
            if name in lock:check(lock[name]==sha(path),'import_pin:'+name)
            lock[name]=sha(path)
    dump(out/'source-lock.json',lock)
    contracts=read(BASE/'contracts.json');evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases']
    expected={x['case']:x for x in read(BASE/'cases.json')}
    sources={};compiled={};retained=[]
    for chart,contract in contracts.items():
        source=t.render(contract);sources[chart]=source
        (out/(chart+'.accdsl')).write_text(source)
        definition=evidence[chart]['final']['memory_definition']
        c=t.compile_text(source,definition);compiled[chart]=c
        check(c['contract']==contract,chart+':full_typed_contract')
        check(c['contract_order_sha256']==p.order_digest(contract),chart+':exact_typed_order')
        check(c['source_sha256']==sha(out/(chart+'.accdsl')),chart+':source_hash')
        check(all(c[k] is False for k in ['executed','opening_admitted','future_commands_validated','source_admission','accounting_admission']),chart+':compilation_not_admission')
        dump(out/(chart+'-compiled.json'),c)
        case=evidence[chart]
        states=[('migration',case['migration']['state'])]+[(f'event-{i}',r['result']['after']) for i,r in enumerate(case['steps'])]+[('carry',case['carry']['after'])]
        retained.extend((chart+':'+label,state,chart) for label,state in states)
    base=evidence['alpha']['final'];contract=contracts['alpha'];source=sources['alpha'];definition=base['memory_definition']
    bad=prior.controls.structural_corruptions(base)
    semantic=module('nested_source_semantic_controls',HERE.parent/'nested-obligation-completion-20261026/controls.py')
    semantic_prior=module('nested_source_semantic_verifier',HERE.parent/'term-semantic-composition-20261026/verify.py')
    bad.extend((name,state) for name,state,_ in semantic.corruptions(base)+semantic_prior.common_corruptions(base))
    reordered=deepcopy(base);terms=reordered['book']['memory']['claims']['invoice/a~1']['terms']
    reordered['book']['memory']['claims']['invoice/a~1']['terms']=dict(reversed(list(terms.items())))
    candidates=retained+[(name,state,'alpha') for name,state in bad]+[('reordered_fresh',reordered,'alpha')]
    check(len(candidates)==len(expected)==74,'frozen_case_population')

    # Manually authored projection, independent of the renderer and contract.
    manual='''projection "NestedMapProjection/1";
context {"entity":"Operating-alpha","book":"legal-alpha","currency":"USD","case_id":"synthetic-cycle-alpha","mode":"synthetic"};
parent_pointer "/claims";
child_pointer "/terms";
fields;
field "所有者";
kind parent_key;
type {"kind":"text","context":{}};
end;
end;
residuals;
item "Manual supplied-population projection";
end;
end;
'''
    parser=t.Parser(manual);r,loc=parser.next();check(r.take('word')=='projection','manual_projection_keyword')
    actual=parser.item(t.block('projection'),r,loc,'',0)
    manual_expected=dict(profile='NestedMapProjection/1',context=deepcopy(contract['context']),parent_pointer='/claims',child_pointer='/terms',
      fields={'所有者':dict(kind='parent_key',type=dict(kind='text',context={}))},residuals=['Manual supplied-population projection'])
    check(actual==manual_expected and p.order_digest(actual)==p.order_digest(manual_expected),'manual_projection_exact')
    p.compile_spec(actual,definition);(out/'manual-projection.accdsl').write_text(manual)
    dump(out/'manual-projection-expected.json',manual_expected)

    def negative(name,text,reason,path=None):
        try:t.compile_text(text,definition)
        except t.Invalid as exc:
            check(reason in exc.reason,name+':reason:'+exc.reason)
            loc=exc.location;check(isinstance(loc,dict),name+':located')
            raw=text.encode();a,b=loc['byte_start'],loc['byte_end']
            check(0<=a<=b<=len(raw) and sha256(raw[a:b]).hexdigest()==loc['slice_sha256'],name+':exact_bytes')
            check(loc['line']==raw[:a].count(b'\n')+1,name+':line')
            if path is not None:
                expected_loc=t.lower(text)['source_locations'][path]
                check(loc==expected_loc,name+':narrow_component')
            controls.append(dict(case=name,status='rejected',reason=exc.reason,location=loc))
            counts['source_controls']+=1
        else:raise AssertionError(name+':accepted')

    saved=[]
    for m,names in [(prior.native,('validate','step','carry','migrate','protected','claim_type','term_type','assessment_type')),
      (prior.life,('validate','control','claim_type','event_types','make_request','run','protected')),(prior.operating,('build',))]:
        for name in names:saved.append((m,name,getattr(m,name)))
    def disabled(*a,**kw):raise AssertionError('native_financial_callback_in_source_candidate')
    try:
        for m,name,_ in saved:setattr(m,name,disabled)
        with (out/'results.jsonl').open('w') as stream:
            for label,state,chart in candidates:
                c=contracts[chart];cov=prior.coverage_for(state,c);selection=core.digest(c)
                call=s.contract_call(c,state,cov,selection);before=(p.order_digest(state),p.order_digest(c))
                result=t.assess_source(sources[chart],evidence[chart]['final']['memory_definition'],state,cov,selection,call)
                target=expected[label]
                check(core.digest(state)==target['state_sha256'],label+':exact_frozen_input')
                check(core.canonical(result)==core.canonical(target['result']),label+':complete_result')
                check(p.order_digest(result)==p.order_digest(target['result']),label+':result_order')
                check(before==(p.order_digest(state),p.order_digest(c)),label+':no_mutation')
                check(all(result[k] is False for k in s.FLAGS),label+':no_admission_promotion')
                stream.write(json.dumps(dict(case=label,result=result),ensure_ascii=False)+chr(10));stream.flush()
                counts['full_comparisons']+=1
                if counts['full_comparisons']%12==0:print(json.dumps(counts),flush=True)
        # Source changes cannot authorize themselves, even if the new text compiles.
        cov=prior.coverage_for(base,contract);selection=core.digest(contract)
        altered=deepcopy(contract);altered['residuals'].append('Changed declaration')
        revised=t.render(altered);call=s.contract_call(altered,base,cov,selection)
        refused=t.assess_source(revised,definition,base,cov,selection,call)
        check(refused['status']=='invalid' and refused['reason']=='reviewed_term_contract','changed_source_stale_selection')
        controls.append(dict(case='changed_source_stale_selection',result=refused))
        # Preserve exact Unicode, including separators which splitlines misreads.
        unicode_contract=deepcopy(contract);unicode_contract['residuals'].append('公司 café e\u0301 \u2028 \u2029 😀')
        unicode_source=t.render(unicode_contract)
        for label,text in [('unicode_lf',unicode_source),('unicode_crlf',unicode_source.replace('\n','\r\n'))]:
            x=t.compile_text(text,definition)
            check(x['contract_order_sha256']==p.order_digest(unicode_contract),label+':exact_unicode')
            for loc in x['source_locations'].values():
                raw=text.encode();a,b=loc['byte_start'],loc['byte_end']
                check(sha256(raw[a:b]).hexdigest()==loc['slice_sha256'] and loc['line']==raw[:a].count(b'\n')+1,label+':span')
            (out/(label+'.accdsl')).write_bytes(text.encode())
        negative('duplicate_context',source.replace('  context ', '  context {};\n  context ',1),'duplicate_declaration:context')
        negative('unknown_declaration',source.replace('  context ','  algorithm_import ',1),'unknown_declaration:contract')
        negative('opaque_contract', 'selected_term_state '+t.j(t.PROFILE)+' '+t.j(contract)+';\n','string_token')
        negative('trailing_source',source+'context {};\n','declaration_after_end')
        negative('truncated_source',source.rsplit('end;',1)[0],'incomplete_source')
        negative('bad_profile',source.replace('SelectedTermStateContract/1','SelectedTermStateContract/9',1),'profile:contract')
        negative('control_character',source+'\x00','source_control')
        negative('duplicate_json_key',source.replace('"entity":"Operating-alpha"','"entity":"Operating-alpha","entity":"other"',1),'duplicate_json_key:entity')
        negative('unknown_expression',source.replace('(lt ', '(mystery ',1),'unknown_operator:mystery')
        for label,mutate,reason,path in [
          ('wrong_projection_field',lambda c:c['semantics']['terms']['iteration']['fields']['effective'].update(pointer='/absent'),'','/semantics/terms/iteration'),
          ('wrong_capture',lambda c:c['semantics']['terms']['captures']['effective'].update(type={'kind':'text','context':{}}),'','/semantics/terms'),
          ('wrong_query_binding',lambda c:c['semantics']['terms']['template']['bindings']['identity'].update(field='absent'),'','/semantics/terms/template'),
          ('wrong_rule_reference',lambda c:c['semantics']['clock']['manifest']['requirements'][0]['predicate']['left'].update(id='missing'),'','/semantics/clock/manifest'),
          ('wrong_slot',lambda c:c['semantics']['terms']['slots'][0].update(query='missing'),'','/semantics/terms'),
          ('missing_required_component',lambda c:c['semantics'].pop('events'),'','/semantics'),
          ('unsupported_structure_operator',lambda c:c['structure']['checks'][0].update(op='custom_regex'),'structure_check_op','/structure'),
        ]:
            c=deepcopy(contract);mutate(c);negative(label,t.render(c),reason,path)
        check(t.lower(source)['contract']==contract,'baseline_source_unchanged')
    finally:
        for m,name,value in saved:setattr(m,name,value)
        dump(out/'assertions.json',assertions);dump(out/'controls.json',controls)
    for n,h in lock.items():check(sha(ROOT/n)==h,'protected_after:'+n)
    summary=dict(passed=True,**counts,retained_states=len(retained),corruptions=len(bad),
      assertions=len(assertions),protected_files=len(lock),native_financial_callbacks_disabled=True,
      future_commands_validated=False,opening_admission=False)
    dump(out/'checks.json',summary);dump(out/'assertions.json',assertions)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump(out/'run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/nested-contract-source-20261026/verify.py '+sys.argv[1],
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,
      data_version=sha(BASE/'cases.json'),plan_file='docs/plans/accounting-nested-contract-source-20261026.md',
      result_file=str((HERE/'result.md').relative_to(ROOT)),implementation_sha256={n:sha(HERE/n) for n in ['contract_text.py','verify.py']},
      artifact_paths=[str(x.relative_to(ROOT)) for x in out.iterdir() if x.is_file()],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
