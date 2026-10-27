from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
import recipe_text as recipe
import expansion_text as expansion
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];c=recipe.c
SCALAR=HERE.parent/'parameterized-method-construction-20261026'
ROWS=HERE.parent/'ordered-assessment-expansion-20261026'
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def equal(a,b):return c.core.canonical(a)==c.core.canonical(b)

def main():
    start=time.monotonic();assertions=[];comparisons=[];controls=[];roundtrips=[]
    for n in ('examples','adverse'):(HERE/n).mkdir(exist_ok=True)
    lockpath=HERE/'source-lock.json'
    if not lockpath.exists():
        lock=read(ROWS/'source-lock.json');paths=[]
        for folder in (SCALAR,ROWS):
            paths += [p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
        for folder,names in [('ordered-eligibility-source-20261026',['eligibility_text.py','verify.py','result.md','checks.json']),('opening-admission-source-20261026',['opening_text.py','verify.py','result.md','checks.json'])]:
            paths += [HERE.parent/folder/n for n in names]
        paths += [ROOT/'scripts'/n for n in ('method_requirement_text_v1.py','method_requirement_text_v2.py')]
        for p in paths:
            n=str(p.relative_to(ROOT));h=sha(p);assert n not in lock or lock[n]==h,n;lock[n]=h
        dump('source-lock.json',lock)
    lock=read(lockpath)
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    def ensure(ok,label):assertions.append(dict(check=label,passed=bool(ok)));assert ok,label
    templates={};sources={}
    for owner in ('alpha','beta'):
        for kind in ('sale','collect','assess'):
            module=expansion if kind=='assess' else recipe
            template=read((ROWS if kind=='assess' else SCALAR)/f'templates/{owner}.{kind}.json')
            source=module.render(template);compiled=module.lower(source)
            templates[owner,kind]=template;sources[owner,kind]=source
            ensure(equal(compiled['template'],template),owner+kind+':complete_template')
            ensure(module.render(compiled['template'])==source,owner+kind+':source_roundtrip')
            ensure(not compiled['contextually_compiled'],owner+kind+':syntax_only')
            (HERE/f'examples/{owner}.{kind}.acc').write_text(source);dump(f'examples/{owner}.{kind}.lowered.json',compiled)
            roundtrips.append(dict(company=owner,method=kind,template_sha256=compiled['template_sha256'],source_sha256=compiled['source_sha256']))
    cases=[dict(row,kind=row['method']) for row in read(SCALAR/'cases.json')]+[dict(row,kind='assess') for row in read(ROWS/'cases.json')]
    def construct(source,row):
        module=expansion if row['kind']=='assess' else recipe;t=module.lower(source)['template'];p=row['parameters']
        call=expansion.expand.make_call(t,row['before'],row['event'],row['order']) if row['kind']=='assess' else c.make_call(t,row['before'],row['event'])
        return module.construct_source(source,row['before'],row['event'],p['schemas'],p['memory_definition'],call)
    originals={n:getattr(native,n) for n in ('validate','control','claim_type','event_types','make_request','run','protected')};builder=operating.build
    def disabled(*args,**kwargs):raise AssertionError('native construction callback')
    try:
        for n in originals:setattr(native,n,disabled)
        operating.build=disabled
        for row in cases:
            before=recipe.c.core.digest(row);result=construct(sources[row['company'],row['kind']],row)
            ensure(equal(result,row['construction']),row['case']+':complete_construction')
            request=result['construction']['request'] if row['kind']=='assess' else result['request']
            ensure(equal(request,row['native_request']),row['case']+':complete_request')
            transition=c.frontend.v2.propose(row['before'],request)
            ensure(equal(transition,row['transition'] if row['kind']=='assess' else row['complete_transition']),row['case']+':complete_transition')
            ensure(recipe.c.core.digest(row)==before,row['case']+':inputs_preserved')
            comparisons.append(dict(case=row['case'],company=row['company'],method=row['kind'],input_sha256=before,
                expected=row['construction'],actual=result,request=request,transition=transition,complete_equal=True))
        run_controls(templates,sources,cases,construct,ensure,controls)
    finally:
        for n,v in originals.items():setattr(native,n,v)
        operating.build=builder
    dump('comparisons.json',comparisons);dump('controls.json',controls);dump('roundtrips.json',roundtrips)
    for n,h in lock.items():ensure(sha(ROOT/n)==h,'protected:'+n)
    summary=dict(passed=True,templates=6,scalar_cases=18,ordered_cases=20,controls=len(controls),assertions=len(assertions),protected_files=len(lock),
        native_lifecycle_and_builder_disabled=True,source_admission=False,accounting_admission=False,production_ready=False,independent_reader_pending=True)
    dump('checks.json',summary);dump('assertions.json',assertions)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
        command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/method-recipe-source-20261026/verify.py',
        environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,
        data_version=sha(lockpath),plan_file='docs/plans/accounting-method-recipe-source-20261026.md',
        result_file='data/accounting-master/method-recipe-source-20261026/result.md',
        artifacts=['examples','adverse','comparisons.json','controls.json','roundtrips.json','checks.json','assertions.json'],
        implementation_sha256={n:sha(HERE/n) for n in ('recipe_text.py','expansion_text.py','verify.py','design.md')},timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

def run_controls(templates,sources,cases,construct,ensure,controls):
    sale=next(r for r in cases if r['company']=='alpha' and r['kind']=='sale')
    collect=next(r for r in cases if r['company']=='alpha' and r['kind']=='collect')
    assessed=next(r for r in cases if r['company']=='alpha' and r['kind']=='assess')
    def rejected(label,source,row,reason,lower_only=False):
        module=expansion if row['kind']=='assess' else recipe
        (HERE/f'adverse/{label}.acc').write_bytes(source.encode())
        try:module.lower(source) if lower_only else construct(source,row)
        except recipe.Invalid as exc:
            ensure(reason in exc.reason,label+':reason:'+exc.reason);loc=exc.location;raw=source.encode()
            ensure(loc is not None,label+':location')
            ensure(0<=loc['byte_start']<=loc['byte_end']<=len(raw),label+':bounds')
            ensure(sha256(raw[loc['byte_start']:loc['byte_end']]).hexdigest()==loc['slice_sha256'],label+':span')
            ensure(raw[:loc['byte_start']].count(b'\n')+1==loc['line'],label+':line')
            controls.append(dict(case=label,reason=exc.reason,location=loc));return loc
        raise AssertionError(label+':accepted')
    source=sources['alpha','sale']
    rejected('unknown_source',source.replace('(event_input ','(callback ',1),sale,'parameter_source',True)
    rejected('missing_end',source.replace('end_recipe;',''),sale,'incomplete_source',True)
    line=next(l for l in source.split('\n') if l.startswith('parameter '))
    rejected('duplicate_parameter',source.replace(line,line+'\n'+line),sale,'duplicate_parameter',True)
    rejected('unbound_parameter',source.replace('(parameter "customer")','(parameter "absent")',1),sale,'unbound_parameter')
    unused='parameter "unused" '+recipe.j(c.TEXT)+' (event_input "claim_id");\n'
    rejected('unused_parameter',source.replace('begin_method;',unused+'begin_method;'),sale,'unused_parameters')
    changed=deepcopy(templates['alpha','collect']);p=next(p for p in changed['parameters'] if p['source']['kind']=='pointer');changed['parameters'].remove(p);changed['parameters'].insert(0,p)
    rejected('forward_pointer_parameter',recipe.render(changed),collect,'forward_or_missing_parameter')
    changed=deepcopy(templates['alpha','sale']);next(p for p in changed['parameters'] if p['name']=='customer')['type']=c.DATE
    rejected('parameter_type',recipe.render(changed),sale,'parameter_type')
    changed=source.replace('(event_input "customer")','(event_input "claim_id")',1)
    result=construct(changed,sale)
    ensure(not equal(result['request'],sale['native_request']),'parameter_source_edit:consequence')
    ensure(result['parameters']['customer']==sale['event']['inputs']['claim_id']['value']['value'],'parameter_source_edit:value')
    controls.append(dict(case='parameter_source_edit',result=result,native_equivalent=False));(HERE/'examples/changed-customer-source.acc').write_text(changed)
    source=sources['alpha','assess'];changed=source.replace('(operation_id "assess.")','(operation_id "authored.")',1)
    ensure(changed!=source,'row_edit_applied');result=construct(changed,assessed)
    ensure(not equal(result,assessed['construction']),'row_id_edit:consequence')
    controls.append(dict(case='row_id_edit',result=result,native_equivalent=False));(HERE/'examples/changed-row-id.acc').write_text(changed)
    rejected('unknown_row_operator',source.replace('(operation_id ','(execute ',1),assessed,'row_expression:',True)
    empty=next(r for r in cases if r['kind']=='assess' and not r['order'])
    bad=deepcopy(templates[empty['company'],'assess'])
    bad['row_operations'][0]['fields']['value']['fields']['value']={'expr':'row','field':'absent'}
    rejected('empty_map_invalid_row',expansion.render(bad),empty,'row_field')
    bad=deepcopy(templates['alpha','assess'])
    def corrupt_else(value):
        if type(value) is dict:
            if value.get('expr')=='if':value['else']={'expr':'row','field':'absent'};return True
            return any(corrupt_else(v) for v in value.values())
        if type(value) is list:return any(corrupt_else(v) for v in value)
        return False
    ensure(corrupt_else(bad['row_operations']),'conditional_branch_exists')
    rejected('invalid_conditional_branch',expansion.render(bad),assessed,'row_field')
    bad=deepcopy(templates['alpha','assess']);bad['suffix_operations'][0]['fields']['value']['fields']['value']={'expr':'key'}
    rejected('key_outside_row',expansion.render(bad),assessed,'key_scope')
    bad=deepcopy(templates['alpha','assess']);bad['row_types']['due']=c.TEXT
    rejected('row_type_mismatch',expansion.render(bad),assessed,'row_type_mismatch')
    reordered=deepcopy(assessed);reordered['order']=assessed['order']+assessed['order'][:1]
    if assessed['order']:rejected('duplicate_order',source,reordered,'duplicate_order_key')
    for kind,module,row in [('sale',recipe,sale),('assess',expansion,assessed)]:
        original=sources['alpha',kind]
        variant=original.replace('residual ', 'residual ',1)
        variant=variant.replace('end_recipe;' if kind=='sale' else 'end_expansion;', 'residual "资料/é\u2028";\n'+('end_recipe;' if kind=='sale' else 'end_expansion;'))
        crlf='\r\n'.join('  '+l for l in variant.split('\n'))
        first=module.lower(variant);second=module.lower(crlf)
        ensure(equal(first['template'],second['template']) and first['source_sha256']!=second['source_sha256'],kind+':crlf_semantics')
        for loc in second['source_spans']:ensure(sha256(crlf.encode()[loc['byte_start']:loc['byte_end']]).hexdigest()==loc['slice_sha256'],kind+':source_span')
        controls.append(dict(case=kind+'_unicode_crlf',passed=True));(HERE/f'examples/{kind}.unicode-crlf.acc').write_bytes(crlf.encode())
    bad=source.replace('begin_method;','residual "汉字";\nbegin_method;',1).replace('company_method ','@company_method ',1)
    loc=rejected('embedded_error_location',bad,assessed,'unexpected_token',True)
    ensure(bad.encode()[loc['byte_start']:loc['byte_end']]==b'@','embedded_exact_token')
    nested='(array '*(c.core.MAX_DEPTH+2)+'true'+')'*(c.core.MAX_DEPTH+2)
    rejected('data_depth',sources['alpha','sale'].replace('(parameter "customer")',nested,1),sale,'data_limit',True)
    nested='(path '*(c.core.MAX_DEPTH+2)+'(key)'+')'*(c.core.MAX_DEPTH+2)
    rejected('row_depth',source.replace('(operation_id "assess.")',nested,1),assessed,'row_expression_limit',True)

if __name__=='__main__':main()
