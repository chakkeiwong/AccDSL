from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
import admission as a
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_text())
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def sha(p):return sha256(p.read_bytes()).hexdigest()
def equal(x,y):return a.core.canonical(x)==a.core.canonical(y)
def main():
    start=time.monotonic();lock=read(HERE/'source-lock.json');cases=[];controls=[];assertions=[]
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    templates={o:read(HERE/f'templates/{o}.json') for o in ('alpha','beta')}
    def ensure(ok,name):assertions.append(dict(check=name,passed=bool(ok)));assert ok,name
    originals={k:getattr(native,k) for k in ('validate','control','claim_type','event_types','make_request','run','protected')};builder=operating.build
    def disabled(*args,**kwargs):raise AssertionError('native admission callback')
    def candidate(t,b,call=None):
        before=a.order_digest([t,b])
        try:
            for k in originals:setattr(native,k,disabled)
            operating.build=disabled
            result=a.assess(t,b,a.make_call(t,b) if call is None else call)
        finally:
            for k,v in originals.items():setattr(native,k,v)
            operating.build=builder
        ensure(a.order_digest([t,b])==before,'input_unchanged');return result
    def baseline(body):
        try:native.validate(body);return dict(status='accepted',reason=None)
        except Exception as exc:return dict(status='invalid',reason=str(exc))
    def compare(label,owner,body,expected=None):
        t=templates[owner];b=baseline(body);result=candidate(t,body)
        if expected is not None:ensure(b==expected,label+':frozen_baseline')
        ensure(result['status']==('opening_admitted' if b['status']=='accepted' else 'invalid'),label+':status:'+result.get('reason',''))
        ensure(result.get('reason')==b['reason'],label+':reason:'+result.get('reason',''))
        cases.append(dict(case=label,company=owner,input=deepcopy(body),call=a.make_call(t,body),native=b,result=result))
        return result
    previous=read(HERE.parent/'opening-admission-audit-20261026/cases.json')
    for row in previous:
        compare(row['company']+':audit:'+row['case'],row['company'],row['input'],
                dict(status=row['validation_status'],reason=row['validation_reason']))
    bodies={o:read(HERE.parent/f'declarative-event-program-20261026/examples/{o}.native-input.json') for o in ('alpha','beta')}
    for owner,original in bodies.items():
        def test(label,mutate):
            body=deepcopy(original);mutate(body);return compare(owner+':new:'+label,owner,body)
        def rederive(b):
            x=a.typed.types.derive(b['memory_definition'],b['opening']['memory'],b['opening']);assert x['status']=='typed',x
            b['opening'].update(memory_schema=x['schema_sha256'],memory_types=x['memory_types']);b['schemas'][x['schema_sha256']]=x['schema']
        def money_dimension(b):
            parts=a.base.binding.pointer_parts(b['unit_cost_pointer']);node=b['memory_definition']['root']
            for p in parts:node=node['fields'][p]
            node['type']['dimensions']={'currency:'+b['opening']['context']['currency']:1};rederive(b)
        test('wrong_cost_dimensions',money_dimension)
        def cash_swap(b):b['roles']['cash'],b['roles']['inventory']=b['roles']['inventory'],b['roles']['cash']
        test('cash_role_identity',cash_swap)
        test('extra_policy_field',lambda b:b['policy'].update(extra='x'))
        test('empty_name',lambda b:b.update(name=''))
        test('whitespace_name',lambda b:b.update(name='   '))
        test('bad_policy_type',lambda b:b['policy'].update(carry=False))
        test('bad_command_container',lambda b:b.update(commands={'one':{}}))
        def temporary(b):
            b['opening']['balances'][b['roles']['revenue']]='-1/1';b['opening']['balances'][b['roles']['cash']]=a.base.monetary.fmt(a.base.monetary.rational(b['opening']['balances'][b['roles']['cash']])+1)
        test('opening_temporary_balance',temporary)
        def valid_flow(b):
            b['opening']['seen']=['prior'];b['opening']['flows']=[dict(id='prior.flow',entity=b['opening']['context']['entity'],book=b['opening']['context']['book'],currency=b['opening']['context']['currency'],event_id='prior',date=b['opening']['date'],activity='operating',origin='prior',amount='0/1')]
        test('opening_flows',valid_flow)
        def bad_clock_shape(b):
            b['memory_definition']['root']['fields']['collection_clock']['fields']['extra']={'node':'scalar','type':a.gate.TEXT}
            b['opening']['memory']['collection_clock']['extra']='x';rederive(b)
        test('clock_extra_field',bad_clock_shape)
        def competing(b):
            b['policy']['past_due']='inclusive';b['roles'].pop('cash');b['commands']=[]
        test('policy_before_roles_and_count',competing)
        def competing2(b):
            b['roles']['cash'],b['roles']['inventory']=b['roles']['inventory'],b['roles']['cash'];b['unit_cost_pointer']='/absent'
        test('cash_before_cost',competing2)
    t=templates['alpha'];b=bodies['alpha']
    def refuse(label,reason,template=None,body=None,call=None):
        result=candidate(t if template is None else template,b if body is None else body,call)
        ensure(result['status']=='invalid' and reason in result.get('reason',''),label+':refusal:'+result.get('reason',''))
        controls.append(dict(case=label,result=result));return result
    for field in ('template_sha256','input_sha256','input_order_sha256'):
        call=a.make_call(t,b);call[field]='0'*64;refuse('stale_'+field,'stale_'+field.split('_sha256')[0],call=call)
    reordered=deepcopy(b);reordered['policy']=dict(reversed(list(reordered['policy'].items())))
    call=a.make_call(t,b);ensure(a.core.digest(reordered)==a.core.digest(b),'canonical_ignores_input_order')
    refuse('reordered_input_old_call','stale_input_order',body=reordered,call=call)
    changed=deepcopy(t);changed['stages'][-1]['op']='callback';refuse('unsupported_later_stage','unsupported_stage',template=changed)
    changed=deepcopy(t);changed['stages'].append(deepcopy(changed['stages'][0]));refuse('duplicate_stage','duplicate_stage',template=changed)
    changed=deepcopy(t);p=next(x for x in changed['stages'] if x['id']=='positive_cost');p['bindings']['cost']={'kind':'literal','type':p['bindings']['cost']['type'],'value':'1/1'}
    refuse('caller_supplied_cost','unsupported_binding_source',template=changed)
    changed=deepcopy(t);p=next(x for x in changed['stages'] if x['id']=='cursor');p['bindings'].pop('day')
    refuse('missing_binding','exact_bindings',template=changed)
    changed=deepcopy(t);p=next(x for x in changed['stages'] if x['id']=='cursor');p['bindings']['day']['type']=a.gate.TEXT
    refuse('wrong_binding_type','binding_type_mismatch',template=changed)
    changed=deepcopy(t);next(x for x in changed['stages'] if x['id']=='cursor')['manifest']['requirements'][0]['guard']['value']=False
    refuse('inactive_requirement','unconditional_opening_predicate',template=changed)
    changed=deepcopy(t);changed['dependency_pins'][0]['sha256']='0'*64
    refuse('dependency_mutation','dependency_hash:',template=changed)
    # A consequential rule variant is accepted as another explicitly selected
    # template; it must not be called equivalent to the retained positive-cost rule.
    changed=deepcopy(t);next(x for x in changed['stages'] if x['id']=='positive_cost')['manifest']['requirements'][0]['predicate']['op']='le'
    zero=deepcopy(b);zero['opening']['memory']['stock']['unit_cost']='0/1'
    original=baseline(zero);variant=candidate(changed,zero)
    ensure(original['reason']=='positive_unit_cost' and variant['status']=='opening_admitted','consequential_nonnegative_variant')
    controls.append(dict(case='nonnegative_cost_variant',original=original,variant=variant,native_equivalent=False))
    dump('cases.json',cases);dump('controls.json',controls)
    for row in read(HERE/'cases.json'):
        ensure(equal(candidate(templates[row['company']],row['input'],row['call']),row['result']),row['case']+':saved_recomputed')
    for name,h in lock.items():ensure(sha(ROOT/name)==h,'protected:'+name)
    summary=dict(passed=True,templates=2,audit_cases=len(previous),complete_cases=len(cases),controls=len(controls),assertions=len(assertions),
                 protected_files=len(lock),native_admission_and_builder_disabled=True,admitted=sum(r['result']['status']=='opening_admitted' for r in cases),
                 future_commands_validated=False,accounting_admission=False,production_ready=False)
    dump('checks.json',summary);dump('assertions.json',assertions)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/declared-opening-admission-20261026/verify.py',environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version=sha(HERE/'source-lock.json'),plan_file='docs/plans/accounting-declared-opening-admission-20261026.md',result_file='data/accounting-master/declared-opening-admission-20261026/result.md',artifacts=['templates','cases.json','controls.json','checks.json','assertions.json'],implementation_sha256={n:sha(HERE/n) for n in ('admission.py','prepare.py','verify.py')},timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))
if __name__=='__main__':main()
