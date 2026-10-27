from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
import company_text as text
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PRIOR=HERE.parent/'admitted-program-binding-20261026';binding=text.binding
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def equal(x,y):return binding.core.canonical(x)==binding.core.canonical(y)

def main():
    start=time.monotonic();assertions=[];comparisons=[];controls=[]
    for folder in ('examples','results','adverse'):(HERE/folder).mkdir(exist_ok=True)
    lockpath=HERE/'source-lock.json'
    if not lockpath.exists():
        lock=read(PRIOR/'source-lock.json');paths=[]
        for folder in (PRIOR,HERE.parent/'method-recipe-source-20261026',HERE.parent/'opening-admission-source-20261026',HERE.parent/'ordered-eligibility-source-20261026'):
            paths.extend(p for p in folder.iterdir() if p.is_file() and p.name!='refresh.py')
        paths.extend(HERE.parent/'invariant-source-authoring-20261026'/n for n in ('invariant_text.py','program_text.py'))
        for p in paths:
            name=str(p.relative_to(ROOT));h=sha(p);assert name not in lock or lock[name]==h,name;lock[name]=h
        dump('source-lock.json',lock)
    lock=read(lockpath)
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    def ensure(ok,label):assertions.append(dict(check=label,passed=bool(ok)));assert ok,label
    cases=read(PRIOR/'cases.json')
    selections={o:read(PRIOR/f'selections/{o}.json') for o in ('alpha','beta')}
    opening={o:read(HERE.parent/f'declared-opening-admission-20261026/templates/{o}.json') for o in ('alpha','beta')}
    originals={n:getattr(native,n) for n in ('validate','control','claim_type','event_types','make_request','run','protected')};builder=operating.build
    def disabled(*args,**kwargs):raise AssertionError('native callback on direct company source path')
    try:
        for n in originals:setattr(native,n,disabled)
        operating.build=disabled
        for index,row in enumerate(cases):
            owner=row['company'];source,resources=text.render(selections[owner],opening[owner],row['program'])
            lowered=text.lower(source,resources);label=row['case']
            ensure(equal(lowered['program'],row['program']),label+':complete_program')
            ensure(equal(lowered['input'],row['input']),label+':complete_input')
            ensure(equal(lowered['selection'],selections[owner]),label+':complete_selection')
            ensure(binding.admission.order_digest(lowered['input'])==binding.admission.order_digest(row['input']),label+':input_order')
            ensure(not lowered['executed'] and not lowered['opening_admitted'],label+':lowering_status')
            actual=text.execute_source(source,resources);expected=row['result']
            ensure(expected['program_order_sha256']==binding.admission.order_digest(row['program']),label+':original_order_identity')
            ensure(actual['program_order_sha256']==binding.admission.order_digest(lowered['program']),label+':lowered_order_identity')
            compared=deepcopy(actual);compared['program_order_sha256']=expected['program_order_sha256']
            ensure(equal(compared,expected),label+':complete_result_except_declared_order_identity')
            filename=f'{index:02d}';(HERE/f'examples/{filename}.acc').write_text(source);dump(f'examples/{filename}.resources.json',resources)
            dump(f'results/{filename}.json',dict(case=label,actual=actual,expected=expected,original_program_order=expected['program_order_sha256'],
                lowered_program_order=actual['program_order_sha256'],exception_paths=['program_order_sha256'],full_remaining_result_equal=True))
            comparisons.append(dict(case=label,company=owner,status=actual['status'],source=f'examples/{filename}.acc',
                source_sha256=sha(HERE/f'examples/{filename}.acc'),result=f'results/{filename}.json',result_sha256=sha(HERE/f'results/{filename}.json'),
                successful_commands=actual['execution']['successful_commands'],full_remaining_result_equal=True))
        run_controls(cases[0],selections['alpha'],opening['alpha'],ensure,controls)
    finally:
        for n,v in originals.items():setattr(native,n,v)
        operating.build=builder
    dump('comparisons.json',comparisons);dump('controls.json',controls)
    for n,h in lock.items():ensure(sha(ROOT/n)==h,'protected:'+n)
    complete=[r for r in comparisons if r['status']=='complete_provisional']
    summary=dict(passed=True,complete_programs=len(complete),complete_commands=sum(r['successful_commands'] for r in complete),
        adverse_programs=len(comparisons)-len(complete),controls=len(controls),assertions=len(assertions),protected_files=len(lock),
        native_lifecycle_and_builder_disabled=True,allowed_result_difference=['program_order_sha256'],
        all_other_result_fields_exact=True,accounting_admission=False,production_ready=False,independent_reader_pending=True)
    dump('checks.json',summary);dump('assertions.json',assertions)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
        command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/selected-company-source-20261026/verify.py',
        environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,
        data_version=sha(lockpath),plan_file='docs/plans/accounting-selected-company-source-20261026.md',
        result_file='data/accounting-master/selected-company-source-20261026/result.md',
        artifacts=['examples','results','comparisons.json','controls.json','checks.json','assertions.json'],
        implementation_sha256={n:sha(HERE/n) for n in ('company_text.py','verify.py','design.md')},timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

def run_controls(row,selection,opening,ensure,controls):
    source,resources=text.render(selection,opening,row['program'])
    def rejected(label,changed,reason,imports=resources):
        (HERE/f'adverse/{label}.acc').write_bytes(changed.encode())
        try:text.lower(changed,imports)
        except text.Invalid as exc:
            ensure(reason in exc.reason,label+':reason:'+exc.reason);loc=exc.location;raw=changed.encode()
            ensure(loc is not None,label+':location');ensure(0<=loc['byte_start']<=loc['byte_end']<=len(raw),label+':bounds')
            ensure(sha256(raw[loc['byte_start']:loc['byte_end']]).hexdigest()==loc['slice_sha256'],label+':span')
            ensure(raw[:loc['byte_start']].count(b'\n')+1==loc['line'],label+':line')
            controls.append(dict(case=label,reason=exc.reason,location=loc));return loc
        raise AssertionError(label+':accepted')
    rejected('wrong_target',source.replace('AdmittedDeclarativeProgram/1','WrongProgram/1',1),'selected_profiles')
    rejected('missing_resource',source,'missing_resource',{})
    changed=deepcopy(resources);key=next(iter(changed));changed[key]['date']='2027-02-01'
    rejected('resource_digest',source,'resource_digest',changed)
    changed=deepcopy(resources);extra={'unused':True};changed[binding.core.digest(extra)]=extra
    rejected('unused_resource',source,'exact_resource_population',changed)
    first=source.index('begin_opening;');last=source.index('end_opening_source;')+len('end_opening_source;')
    rejected('missing_opening',source[:first]+source[last:],'required_component')
    rejected('duplicate_opening',source[:last]+'\n'+source[first:last]+source[last:],'duplicate_opening')
    rejected('mismatched_operation',source.replace('rule "sale";','rule "different";',1),'rule_operation')
    rejected('unknown_recipe_kind',source.replace('begin_recipe scalar;','begin_recipe callback;',1),'recipe_kind')
    rejected('duplicate_role',source.replace('role "cash" "cash";','role "cash" "cash";\nrole "cash" "cash";',1),'duplicate_declaration')
    rejected('missing_command_order',source.replace('order null;','',1),'incomplete_command')
    rejected('unterminated_recipe',source.replace('end_recipe_source;','',1),'declaration_after_end')
    bad=source.replace('begin_opening;','selection_residual "汉字/é";\nbegin_opening;',1).replace('opening_admission ','@opening_admission ',1)
    crlf=bad.replace('\n','\r\n');loc=rejected('embedded_utf8_crlf',crlf,'unexpected_token')
    ensure(crlf.encode()[loc['byte_start']:loc['byte_end']]==b'@','embedded_exact_bad_token')
    # Alter an event premise directly in the full source after the definitions.
    prefix,commands=source.split('event "sale.1"',1)
    changed=prefix+'event "sale.1"'+commands.replace('known true','known false',1)
    result=text.execute_source(changed,resources)
    ensure(result['status']=='stopped_provisional' and result['execution']['successful_commands']==0 and result['execution']['stop']['reason']=='applicability_not_selected','edited_full_intent')
    controls.append(dict(case='edited_full_intent',result=result));(HERE/'examples/edited-full-intent.acc').write_text(changed)
    crlf='\r\n'.join('  '+line for line in source.split('\n'))
    lowered=text.lower(crlf,resources);original=text.lower(source,resources)
    ensure(equal(lowered['program'],original['program']) and lowered['source_sha256']!=original['source_sha256'],'full_crlf_semantics')
    ensure(equal(text.execute_source(crlf,resources),text.execute_source(source,resources)),'full_crlf_execution')
    controls.append(dict(case='full_crlf_execution',passed=True));(HERE/'examples/alpha-crlf.acc').write_bytes(crlf.encode())
    changed=deepcopy(row['program']);event=changed['commands'][0]['event'];event['inputs']=dict(reversed(list(event['inputs'].items())))
    reordered,imports=text.render(selection,opening,changed);lowered=text.lower(reordered,imports)
    ensure(list(lowered['program']['commands'][0]['event']['inputs'])==list(event['inputs']),'input_order_preserved')
    ensure(binding.composer.make_call(lowered['program'])['input_order_sha256']!=binding.composer.make_call(row['program'])['input_order_sha256'],'input_order_identity_changes')
    controls.append(dict(case='input_order_preserved',passed=True))

if __name__=='__main__':main()
