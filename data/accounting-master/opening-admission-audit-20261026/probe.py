"""Discriminate opening checks from delayed event checks without changing owners."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import ast,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import declared_receivable_lifecycle_v1 as n
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(name,v):(HERE/name).write_text(json.dumps(v,indent=2)+chr(10))
def read(p):return json.loads(p.read_text())
def main():
    start=time.monotonic();lock_path=HERE/'source-lock.json'
    if not lock_path.exists():
        lock={}
        for name in ['declared_receivable_lifecycle_v1.py','declared_operating_methods_v1.py','company_book_transition_v2.py','company_book_transition_v1.py','company_memory_types_v1.py','company_book_reports_v1.py','company_book_carry_v1.py']:
            p=ROOT/'scripts'/name;lock[str(p.relative_to(ROOT))]=sha(p)
        for owner in ('alpha','beta'):
            p=HERE.parent/f'declarative-event-program-20261026/examples/{owner}.native-input.json';lock[str(p.relative_to(ROOT))]=sha(p)
        dump('source-lock.json',lock)
    lock=read(lock_path)
    for name,digest in lock.items():assert sha(ROOT/name)==digest,name
    findings=[]
    for owner in ('alpha','beta'):
        original=read(HERE.parent/f'declarative-event-program-20261026/examples/{owner}.native-input.json')
        def test(label,mutate,expected,phase='opening'):
            body=deepcopy(original);mutate(body);before=n.core.digest(body)
            try:n.validate(body);status='accepted';reason=None
            except Exception as exc:status='invalid';reason=str(exc)
            assert status==('accepted' if expected is None else 'invalid'),(label,status,reason)
            if expected is not None:assert expected in reason,(label,reason,expected)
            assert before==n.core.digest(body)
            result=n.run(body) if phase=='runtime' else None
            findings.append(dict(company=owner,case=label,phase=phase,input=body,validation_status=status,
                                 validation_reason=reason,runtime_result=result,unchanged_input=True))
            return body,result
        test('baseline',lambda b:None,None)
        test('wrong_profile',lambda b:b.update(profile='Other/1'),'profile')
        test('unknown_top_field',lambda b:b.update(extra=True),'fields')
        test('policy_due_convention',lambda b:b['policy'].update(past_due='inclusive'),'explicit_policy')
        test('policy_carry_convention',lambda b:b['policy'].update(carry='reset'),'explicit_policy')
        test('policy_provenance',lambda b:b['policy'].update(provenance=''),'text:policy_provenance')
        test('wrong_opening_cursor',lambda b:b['opening']['memory']['collection_clock'].update(cursor='2027-01-02'),'opening_cursor')
        def rederive(b):
            x=n.transition.types.derive(b['memory_definition'],b['opening']['memory'],b['opening']);assert x['status']=='typed',x
            b['opening'].update(memory_schema=x['schema_sha256'],memory_types=x['memory_types']);b['schemas'][x['schema_sha256']]=x['schema']
        def wrong_row(b):
            b['memory_definition']['root']['fields']['claims']['values']['fields']['customer']['type']=n.DATE;rederive(b)
        test('wrong_empty_row_type',wrong_row,'claim_type_contract')
        def populated(b):
            first=n.run({**deepcopy(b),'commands':b['commands'][:1]});assert first['status']=='complete_provisional'
            b['opening']=first['current'];b['schemas'].update(first['trace'][0]['request']['schemas'])
        test('populated_opening',populated,'empty_opening_claim_population_required')
        test('missing_role',lambda b:b['roles'].pop('receivables'),'complete_operating_roles')
        test('duplicate_role',lambda b:b['roles'].update(receivables=b['roles']['cash']),'injective_operating_roles')
        test('wrong_role_class',lambda b:b['roles'].update(cash=b['roles']['revenue'],revenue=b['roles']['cash']),'operating_role_class')
        test('missing_cost_pointer',lambda b:b.update(unit_cost_pointer='/absent'),'unit_cost_leaf')
        def zero_cost(b):
            parts=n.engine.binding.pointer_parts(b['unit_cost_pointer']);v=b['opening']['memory']
            for p in parts[:-1]:v=v[p]
            v[parts[-1]]='0/1'
        test('zero_cost',zero_cost,'positive_unit_cost')
        def negative_cost(b):
            parts=n.engine.binding.pointer_parts(b['unit_cost_pointer']);v=b['opening']['memory']
            for p in parts[:-1]:v=v[p]
            v[parts[-1]]='-1/1'
        test('negative_cost',negative_cost,'positive_unit_cost')
        def receivable_without_claim(b):
            b['opening']['balances'][b['roles']['receivables']]='1/1';b['opening']['balances'][b['roles']['cash']]=n.reports.fmt(n.reports.number(b['opening']['balances'][b['roles']['cash']])-1)
        test('claim_total_opening',receivable_without_claim,'claim_receivable_sum')
        test('wrong_map_context',lambda b:b['mapping']['context'].update(entity='Other'),'opening_report:map_context')
        test('incomplete_account_partition',lambda b:b['mapping']['lines'].pop(),'opening_report:complete_account_partition')
        def off_period_start(b):
            b['opening']['date']='2027-01-02';b['opening']['memory']['collection_clock']['cursor']='2027-01-02'
        test('opening_not_period_start',off_period_start,'opening_report:opening_at_period_start')
        test('empty_commands',lambda b:b.update(commands=[]),'command_limit')
        test('large_command_structure_before_count',lambda b:b.update(commands=[deepcopy(b['commands'][0])]*65),'record_structure_limit')
        test('too_many_commands',lambda b:b.update(commands=[{}]*65),'command_limit')
        # Native validate only bounds the command list. It does not establish
        # the shape, method, chronology or values of each future command.
        _,result=test('malformed_future_command',lambda b:b.update(commands=[{'kind':'not_a_command'}]),None,'runtime')
        assert result['stop']['reason']=='command_kind' and result['successful_commands']==0
        _,result=test('unknown_future_operation',lambda b:b['commands'][0].update(method_key='not_selected'),None,'runtime')
        assert result['stop']['reason']=='unsupported_method:not_selected'
        _,result=test('unknown_future_customer',lambda b:b['commands'][0]['event']['inputs']['customer'].update(value={'status':'unknown','reason':'missing'}),None,'runtime')
        assert result['stop']['status']=='unresolved'
        def zero_capacity(b):b['memory_definition']['root']['fields']['claims']['max_items']=0
        test('zero_capacity_opening',zero_capacity,'typed_memory:memory_map_limit')
        def one_capacity(b):b['memory_definition']['root']['fields']['claims']['max_items']=1;rederive(b)
        test('one_capacity_empty_opening',one_capacity,None)
        def invalid_policy_and_cursor(b):
            b['policy']['carry']='reset';b['opening']['memory']['collection_clock']['cursor']='2027-01-02'
        test('policy_before_cursor',invalid_policy_and_cursor,'explicit_policy')
        def invalid_cursor_and_roles(b):
            b['opening']['memory']['collection_clock']['cursor']='2027-01-02';b['roles'].pop('receivables')
        test('cursor_before_roles',invalid_cursor_and_roles,'opening_cursor')
    anchors={}
    for file in ['declared_receivable_lifecycle_v1.py','declared_operating_methods_v1.py','company_book_reports_v1.py']:
        p=ROOT/'scripts'/file;anchors[file]={x.name:[x.lineno,x.end_lineno] for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef)}
    mapping=[
        ('structure','declared_receivable_lifecycle_v1.py','validate','Closed body/profile/name, explicit policy and provenance; bounded full native input','Separate program envelope and explicitly declared policy'),
        ('typed_opening','declared_receivable_lifecycle_v1.py','validate','Typed book and memory schema correspondence','Existing typed book validator'),
        ('claim_shape','declared_receivable_lifecycle_v1.py','claim_type','Exact row shape and scalar types even with no rows','Explicit schema equality, not runtime row inspection'),
        ('opening_population','declared_receivable_lifecycle_v1.py','validate','Empty claims and cursor equal opening date','Explicit opening-only constraints'),
        ('roles','declared_operating_methods_v1.py','build','Complete/injective roles, account classes and cash role','Explicit role contract plus existing typed book owner'),
        ('unit_cost','declared_operating_methods_v1.py','build','Leaf exists, exact price dimensions and strictly positive rational','Typed pointer binding and ordered requirements'),
        ('state_invariants','declared_receivable_lifecycle_v1.py','control','Claim totals, dates, reference and assessment invariants','Already authored invariant; retain exact failure/status correspondence scope'),
        ('opening_report','company_book_reports_v1.py','validate','Opening at period start, empty flows/temporary balances, complete mapping and report arithmetic','Existing report owner; do not duplicate statement rules'),
        ('command_population','declared_receivable_lifecycle_v1.py','validate','Only command list type/length is checked here','Keep event shape/value checks at their declared execution boundary'),
        ('future_execution','declared_receivable_lifecycle_v1.py','run','Command shape, identity, chronology, complete types/unknowns, event checks','Existing explicit composer is stricter for some structural checks; do not assert universal malformed-program precedence')]
    rows=[dict(id=k,source='scripts/'+file,source_sha256=sha(ROOT/'scripts'/file),function=fn,lines=anchors[file][fn],native_obligation=obligation,candidate_owner=owner) for k,file,fn,obligation,owner in mapping]
    dump('cases.json',findings);dump('obligation-map.json',rows)
    for name,digest in lock.items():assert sha(ROOT/name)==digest,name
    summary=dict(passed=True,cases=len(findings),mapped_groups=len(rows),protected_files=len(lock),
                 delayed_checks=sum(x['phase']=='runtime' for x in findings),native_validate_proves_all_future_commands=False,
                 native_opening_replaced=False,accounting_admission=False)
    dump('checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/opening-admission-audit-20261026/probe.py',environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version=sha(lock_path),plan_file='docs/plans/accounting-opening-admission-audit-20261026.md',result_file='data/accounting-master/opening-admission-audit-20261026/result.md',artifacts=['cases.json','obligation-map.json','checks.json'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))
if __name__=='__main__':main()
