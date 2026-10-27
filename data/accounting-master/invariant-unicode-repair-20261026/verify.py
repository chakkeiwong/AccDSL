"""Full-program compatibility and Unicode data/physical-line regression."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
import complete_text_unicode as text
import invariant_text as old_invariant
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=HERE.parent/'complete-claims-source-20261026'
opening=text.opening;core=text.core
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def equal(a,b):return core.canonical(a)==core.canonical(b)

def main():
    started=time.monotonic();assertions=[];cases=[];controls=[]
    def ensure(ok,label):assertions.append(dict(check=label,passed=bool(ok)));assert ok,label
    for folder in ('examples','results','adverse'):(HERE/folder).mkdir(exist_ok=True)
    lock=read(HERE/'source-lock.json')
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    for row in read(HERE/'source-preservation.json'):
        value=(ROOT/row['source']).read_text()
        for edit in row['changes']:
            assert value.count(edit['old'])==1
            value=value.replace(edit['old'],edit['new'],1)
        ensure((HERE/row['target']).read_text()==value,'exact_allowed_delta:'+row['target'])
        ensure(sha(ROOT/row['source'])==row['source_sha256'],'original_preserved:'+row['source'])
    originals={n:getattr(native,n) for n in ('validate','control','claim_type','event_types','make_request','run','protected')}
    builder=operating.build
    def disabled(*args,**kwargs):raise AssertionError('native callback during Unicode source check')
    try:
        for n in originals:setattr(native,n,disabled)
        operating.build=disabled
        for i in range(8):
            key=f'{i:02d}';source=(PRIOR/f'examples/{key}.acc').read_text()
            resources=read(PRIOR/f'examples/{key}.resources.json');selection=read(PRIOR/f'examples/{key}.selection.json')
            expected=read(PRIOR/f'results/{key}.json')['actual']
            actual=text.execute_source(source,resources,selection)
            ensure(equal(actual,expected),key+':all_result_fields_exact')
            dump('results/'+key+'.json',dict(actual=actual,expected=expected,all_result_fields_exact=True))
            cases.append(dict(case=key,commands=actual['delegated']['execution']['successful_commands'],all_result_fields_exact=True))
        base=read(HERE.parent/'complete-claims-opening-20261026/cases.json')[0]
        from source_controls_unicode import run_controls
        run_controls(base,ensure,controls)
        ensure(equal(controls,read(PRIOR/'controls.json')),'all_32_retained_controls_exact')
        unicode_cases(base,ensure,cases,controls)
    finally:
        for n,v in originals.items():setattr(native,n,v)
        operating.build=builder
    for n,h in lock.items():ensure(sha(ROOT/n)==h,'protected:'+n)
    dump('cases.json',cases);dump('controls.json',controls);dump('assertions.json',assertions)
    summary=dict(passed=True,retained_programs=8,retained_commands=54,retained_controls=32,
                 unicode_cases=9,controls=len(controls),assertions=len(assertions),protected_files=len(lock),
                 financial_evaluators_unchanged=True,native_lifecycle_and_builder_disabled=True,
                 accounting_admission=False,production_ready=False)
    dump('checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/invariant-unicode-repair-20261026/verify.py',
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',
      wall_seconds=time.monotonic()-started,data_version=sha(HERE/'source-lock.json'),
      plan_file='docs/plans/accounting-invariant-unicode-repair-20261026.md',
      result_file='data/accounting-master/invariant-unicode-repair-20261026/result.md',
      artifacts=['cases.json','controls.json','checks.json','assertions.json','examples','results','adverse','source-preservation.json'],
      implementation_sha256={p.name:sha(p) for p in HERE.glob('*.py')},timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

def unicode_cases(base,ensure,cases,controls):
    for codepoint in (0x85,0x2028,0x2029):
        for place in ('outer_residual','rule_residual','source_ref'):
            label=f'U{codepoint:04X}_{place}';marker='Explicit 汉字/é '+chr(codepoint)+' provenance'
            program=deepcopy(base['program']);inv=program['state_invariant']
            row_rule=next(r for r in inv['definition']['snapshot']['constraints'] if r['op']=='each')['definition']
            if place=='outer_residual':inv['residual_prerequisites'].append(marker)
            elif place=='rule_residual':row_rule['residual_prerequisites'].append(marker)
            else:row_rule['inputs'][next(iter(row_rule['inputs']))]['source_ref']=marker
            try:old_invariant.render(inv)
            except Exception as exc:old_failure=dict(reason=str(exc),location=getattr(exc,'location',None))
            else:raise AssertionError(label+':old_bug_not_reproduced')
            program['invariant_sha256']=core.digest(inv)
            selection=deepcopy(base['selection']);selection['invariant_sha256']=core.digest(inv)
            contract=opening.make_contract(base['contract']['empty_template'],inv)
            source,resources=text.render(selection,contract,base['completeness'],program)
            lowered=text.lower(source,resources,selection)
            ensure(equal(lowered['program'],program),label+':program_roundtrip')
            ensure(marker in source,label+':literal_unicode_retained')
            actual=text.execute_source(source,resources,selection)
            expected=opening.execute(selection,contract,base['input'],base['completeness'],program,
                opening.make_program_call(selection,contract,base['input'],base['completeness'],program))
            ensure(actual['program_order_sha256']==opening.a.order_digest(lowered['program']),label+':outer_order')
            ensure(actual['delegated']['program_order_sha256']==opening.a.order_digest(lowered['program']),label+':delegated_order')
            compared=deepcopy(actual)
            compared['program_order_sha256']=expected['program_order_sha256']
            compared['delegated']['program_order_sha256']=expected['delegated']['program_order_sha256']
            ensure(equal(compared,expected),label+':full_typed_result')
            ensure(actual['status']=='complete_provisional',label+':executed')
            try:text.lower(source,resources,base['selection'])
            except text.Invalid as exc:ensure(exc.reason=='reviewed_selection_identity',label+':old_selection_refused')
            else:raise AssertionError(label+':old_selection_accepted')
            crlf=source.replace('\n','\r\n')
            crlf_lowered=text.lower(crlf,resources,selection)
            ensure(equal(crlf_lowered['program'],lowered['program']),label+':crlf_roundtrip')
            check_locations(crlf,crlf_lowered,ensure,label)
            # The bad declaration follows every edited string inside the invariant.
            for ending in ('\n','\r\n'):
                bad=source.replace('end_invariant;','@end_invariant;',1).replace('\n',ending)
                try:text.lower(bad,resources,selection)
                except text.Invalid as exc:
                    loc=exc.location;raw=bad.encode()
                    ensure(exc.reason=='unexpected_token',label+':bad_reason')
                    ensure(raw[loc['byte_start']:loc['byte_end']]==b'@end_invariant;',label+':exact_bad_declaration')
                    ensure(raw[:loc['byte_start']].count(b'\n')+1==loc['line'],label+':bad_line')
                    ensure(sha256(raw[loc['byte_start']:loc['byte_end']]).hexdigest()==loc['slice_sha256'],label+':bad_span')
                else:raise AssertionError(label+':bad_source_accepted')
            (HERE/f'examples/{label}.acc').write_text(source)
            dump(f'examples/{label}.resources.json',resources);dump(f'examples/{label}.selection.json',selection)
            dump(f'results/{label}.json',dict(actual=actual,expected=expected,old_failure=old_failure,
                exception_paths=['program_order_sha256','delegated.program_order_sha256']))
            cases.append(dict(case=label,all_remaining_result_fields_exact=True,old_failure=old_failure))
            controls.append(dict(case=label,passed=True))

def check_locations(source,lowered,ensure,label):
    raw=source.encode()
    for loc in lowered['source_spans']+lowered['nested_source_spans']+[b['location'] for b in lowered['blocks']]:
        ensure(0<=loc['byte_start']<=loc['byte_end']<=len(raw),label+':bounds')
        ensure(raw[:loc['byte_start']].count(b'\n')+1==loc['line'],label+':physical_line')
        ensure(sha256(raw[loc['byte_start']:loc['byte_end']]).hexdigest()==loc['slice_sha256'],label+':slice')

if __name__=='__main__':main()
