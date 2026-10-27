from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
import opening_text as text
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=HERE.parent/'declared-opening-admission-20261026';a=text.admission
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def equal(x,y):return a.core.canonical(x)==a.core.canonical(y)

def main():
    start=time.monotonic();checks=[];comparisons=[];controls=[]
    for name in ('examples','adverse'):(HERE/name).mkdir(exist_ok=True)
    lockpath=HERE/'source-lock.json'
    if not lockpath.exists():
        lock=read(PRIOR/'source-lock.json')
        paths=[p for p in PRIOR.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
        p=HERE.parent/'ordered-eligibility-source-20261026'
        paths += [p/n for n in ('eligibility_text.py','verify.py','checks.json','source-lock.json','result.md')]
        paths += [ROOT/'scripts'/n for n in ('method_requirement_text_v1.py','method_requirement_text_v2.py')]
        for path in paths:
            name=str(path.relative_to(ROOT));digest=sha(path)
            assert name not in lock or lock[name]==digest,name;lock[name]=digest
        dump('source-lock.json',lock)
    lock=read(lockpath)
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    def ensure(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    templates={owner:read(PRIOR/f'templates/{owner}.json') for owner in ('alpha','beta')}
    sources={}
    for owner,t in templates.items():
        source=text.render(t);sources[owner]=source;compiled=text.compile_text(source)
        ensure(equal(compiled['template'],t),owner+':exact_template')
        ensure(text.render(compiled['template'])==source,owner+':source_roundtrip')
        ensure(not compiled['opening_admitted'] and not compiled['executed'],owner+':compile_status')
        (HERE/f'examples/{owner}.acc').write_text(source);dump(f'examples/{owner}.compiled.json',compiled)
    def evaluate(source,body,call=None):
        t=text.lower(source)['template']
        return text.assess_source(source,body,a.make_call(t,body) if call is None else call)
    originals={n:getattr(native,n) for n in ('validate','control','claim_type','event_types','make_request','run','protected')}
    builder=operating.build
    def disabled(*args,**kwargs):raise AssertionError('native callback from source path')
    try:
        for n in originals:setattr(native,n,disabled)
        operating.build=disabled
        cases=read(PRIOR/'cases.json')
        for row in cases:
            before=a.order_digest(row);result=evaluate(sources[row['company']],row['input'],row['call'])
            ensure(equal(result,row['result']),row['case']+':full_result')
            ensure(a.order_digest(row)==before,row['case']+':preserved_input')
            comparisons.append(dict(case=row['case'],company=row['company'],input_sha256=before,expected=row['result'],actual=result,complete_equal=True))
        run_controls(templates,sources,cases,evaluate,ensure,controls)
    finally:
        for n,v in originals.items():setattr(native,n,v)
        operating.build=builder
    dump('comparisons.json',comparisons);dump('controls.json',controls)
    for n,h in lock.items():ensure(sha(ROOT/n)==h,'protected:'+n)
    summary=dict(passed=True,templates=2,stages_per_template=21,complete_cases=len(comparisons),controls=len(controls),
        assertions=len(checks),protected_files=len(lock),native_lifecycle_and_builder_disabled=True,
        admitted=sum(r['actual']['status']=='opening_admitted' for r in comparisons),future_commands_validated=False,
        accounting_admission=False,production_ready=False,independent_reader_pending=True)
    dump('checks.json',summary);dump('assertions.json',checks)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
        command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/opening-admission-source-20261026/verify.py',
        environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',
        wall_seconds=time.monotonic()-start,data_version=sha(lockpath),plan_file='docs/plans/accounting-opening-admission-source-20261026.md',
        result_file='data/accounting-master/opening-admission-source-20261026/result.md',
        artifacts=['examples','adverse','comparisons.json','controls.json','checks.json','assertions.json'],
        implementation_sha256={n:sha(HERE/n) for n in ('opening_text.py','verify.py','design.md')},timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

def run_controls(templates,sources,cases,evaluate,ensure,controls):
    source=sources['alpha'];template=templates['alpha'];body=cases[0]['input']
    def rejected(label,changed,reason,granularity=None):
        (HERE/f'adverse/{label}.acc').write_bytes(changed.encode())
        try:text.compile_text(changed)
        except text.Invalid as exc:
            ensure(reason in exc.reason,label+':reason:'+exc.reason);loc=exc.location;raw=changed.encode()
            ensure(loc is not None,label+':location')
            ensure(0<=loc['byte_start']<=loc['byte_end']<=len(raw),label+':bounds')
            ensure(sha256(raw[loc['byte_start']:loc['byte_end']]).hexdigest()==loc['slice_sha256'],label+':span')
            ensure(raw[:loc['byte_start']].count(b'\n')+1==loc['line'],label+':line')
            if granularity:ensure(loc['granularity']==granularity,label+':granularity')
            controls.append(dict(case=label,status='invalid',reason=exc.reason,location=loc));return loc
        raise AssertionError(label+':accepted')
    rejected('unknown_operation',source.replace('stage "envelope" record_fields','stage "envelope" callback',1),'unsupported_stage','token')
    rejected('missing_check',source.replace(next(l for l in source.split('\n') if l.startswith('check ')),'',1),'stage_body_required','declaration')
    rejected('duplicate_stage',source.replace('stage "name"','stage "profile"',1),'duplicate_stage','declaration')
    line=next(l for l in source.split('\n') if l.startswith('context '))
    rejected('duplicate_context',source.replace(line,line+'\n'+line,1),'duplicate_declaration','declaration')
    line=next(l for l in source.split('\n') if l.startswith('record_value '))
    rejected('duplicate_record_value',source.replace(line,line+'\n'+line,1),'duplicate_declaration','declaration')
    line=next(l for l in source.split('\n') if l.startswith('bind '))
    rejected('missing_binding',source.replace(line,'',1),'exact_bindings','stage')
    rejected('unknown_binding',source.replace('(memory_pointer ','(literal ',1),'unsupported_binding_source','token')
    rejected('missing_end',source.replace('end_opening;',''),'incomplete_source','token')
    rejected('trailing_token',source.replace('end_stage;','end_stage; true',1),'trailing_tokens','token')
    changed=deepcopy(template);changed['dependency_pins'][0]['sha256']='short'
    rejected('bad_dependency_digest',text.render(changed),'dependency_digest','document')
    changed=deepcopy(template);next(s for s in changed['stages'] if s['op']=='commands')['maximum']=0
    rejected('invalid_late_stage',text.render(changed),'command_maximum','stage')
    try:evaluate(text.render(changed),{})
    except text.Invalid as exc:
        ensure(exc.reason=='command_maximum','compile_before_bad_envelope');controls.append(dict(case='compile_before_bad_envelope',reason=exc.reason))
    else:raise AssertionError('malformed skipped stage accepted')
    changed=deepcopy(template);p=next(s for s in changed['stages'] if s['id']=='cursor');p['bindings']['day']['type']=a.gate.TEXT
    rejected('binding_type',text.render(changed),'binding_type_mismatch','stage')
    changed=deepcopy(template);p=next(s for s in changed['stages'] if s['id']=='cursor');p['manifest']['requirements'][0]['guard']['value']=False
    rejected('conditional_opening_rule',text.render(changed),'unconditional_opening_predicate','stage')
    changed=source.replace('(lt (const','(le (const',1)
    zero=next(r for r in cases if r['case']=='alpha:audit:zero_cost')
    result=evaluate(changed,zero['input'])
    ensure(result['status']=='opening_admitted' and zero['result']['reason']=='positive_unit_cost','nonnegative_cost_edit')
    (HERE/'examples/nonnegative-cost.acc').write_text(changed);controls.append(dict(case='nonnegative_cost_variant',result=result,native_equivalent=False))
    changed=deepcopy(template);commands=changed['stages'].pop();changed['stages'].insert(1,commands)
    competing=next(r for r in cases if r['case']=='alpha:new:policy_before_roles_and_count')
    result=evaluate(text.render(changed),competing['input'])
    ensure(result['failed_stage']=='commands' and competing['result']['failed_stage']=='policy','stage_order_edit')
    (HERE/'examples/commands-first.acc').write_text(text.render(changed));controls.append(dict(case='stage_order_variant',result=result,previous=competing['result']))
    changed=deepcopy(template);changed['dependency_pins'][0]['sha256']='0'*64
    result=evaluate(text.render(changed),body);ensure(result['failed_stage']=='dependencies','stale_dependency')
    controls.append(dict(case='stale_dependency',result=result))
    result=evaluate(source.replace('(lt (const','(le (const',1),body,a.make_call(template,body))
    ensure(result['reason']=='stale_template','stale_selection');controls.append(dict(case='stale_selection',result=result))
    changed=deepcopy(template);changed['residuals'].append('审计/é/\u2028')
    unicode_source=text.render(changed);crlf='\r\n'.join('  '+l for l in unicode_source.split('\n'))
    first=text.compile_text(unicode_source);second=text.compile_text(crlf)
    ensure(equal(first['template'],second['template']) and first['source_sha256']!=second['source_sha256'],'unicode_crlf_identity')
    for loc in second['source_spans']+second['stage_spans']:
        ensure(sha256(crlf.encode()[loc['byte_start']:loc['byte_end']]).hexdigest()==loc['slice_sha256'],'unicode_span')
    (HERE/'examples/unicode-crlf.acc').write_bytes(crlf.encode())
    loc=rejected('unicode_bad_token',crlf.replace('end_opening;','end_opening; @'),'unexpected_token','token')
    controls.append(dict(case='unicode_crlf_identity',passed=True))

if __name__=='__main__':main()
