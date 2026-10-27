"""Fresh complete-program evidence; frozen per-event writers never run."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json, subprocess, sys, time
import program as p
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,v):path.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
assert len(sys.argv)==2
O=H/sys.argv[1];O.mkdir(exist_ok=False);start=time.monotonic();checks=[];controls=[]
def check(ok,name):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
def equal(a,b):return p.core.canonical(a)==p.core.canonical(b) and p.source.full.p.order_digest(a)==p.source.full.p.order_digest(b)
sourcebase=B/'term-event-source-20261026';typedbase=B/'term-full-event-binding-20261026'
locks=read(sourcebase/'attempt-01/source-lock.json')
for name,d in locks.items():check(sha(R/name)==d,'protected_before:'+name)
for path in [H/'program.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-selected-term-program-20261027.md',sourcebase/'event_text.py',sourcebase/'verify.py',sourcebase/'attempt-01/checks.json',typedbase/'attempt-01/rules.json']:
    locks[str(path.relative_to(R))]=sha(path)
cases=read(B/'receivable-term-history-20261025/evidence.json')['cases']
rules=read(typedbase/'attempt-01/rules.json');contracts=read(B/'term-structural-admission-20261026/contracts.json')
programs={};selections={};expected={}
def select(obj,term_selection):
    # Test author supplies this explicitly. Runtime never calls this helper.
    selection=dict(profile=p.SELECTION,**p.identities(obj),term_selection=term_selection)
    return selection,p.core.digest(selection)
for chart,case in cases.items():
    path=sourcebase/'attempt-01'/f'{chart}-trace.jsonl';locks[str(path.relative_to(R))]=sha(path)
    trace=[json.loads(line) for line in path.read_text().splitlines()];expected[chart]=trace
    opening=deepcopy(case['migration']['state']);book_hash=p.core.digest(opening['book'])
    coverage={
      'claims':dict(profile='SuppliedClaimPopulation/1',status='complete',map_pointer='/claims',book_sha256=book_hash,provenance='Explicit supplied semantic fixture'),
      'terms':dict(profile='SuppliedNestedPopulation/1',status='complete',book_sha256=book_hash,parent_pointer='/claims',child_pointer='/terms',provenance='Explicit supplied term rows'),
      'assessments':dict(profile='SuppliedNestedPopulation/1',status='complete',book_sha256=book_hash,parent_pointer='/claims',child_pointer='/assessments',provenance='Explicit supplied assessment rows')}
    src={}
    for name in rules[chart]:
        file=sourcebase/'attempt-01'/f'{chart}.{name}.accdsl';locks[str(file.relative_to(R))]=sha(file);src[name]=file.read_text()
    cs=B/'nested-contract-source-20261026/attempt-01'/f'{chart}.accdsl';locks[str(cs.relative_to(R))]=sha(cs)
    commands=[]
    for item in trace:
        key=item['command'];request=case['carry_request'] if key=='carry' else case['steps'][int(key.split('-')[1])]['request']
        commands.append(dict(id=key,request=deepcopy(request)))
    obj=dict(profile=p.PROFILE,name=chart,contract_source=cs.read_text(),rule_sources=src,opening=opening,coverage=coverage,commands=commands)
    programs[chart]=obj;selections[chart]=select(obj,p.source.full.selection_for(contracts[chart],rules[chart]))
    dump(O/f'{chart}-program.json',obj);dump(O/f'{chart}-selection.json',dict(selection=selections[chart][0],expected_sha256=selections[chart][1]))
dump(O/'source-lock.json',locks)
import receivable_term_history_v1 as native
saved=[]
for mod,names in [(native,('validate','step','carry','migrate','state_request','event_types','literal','protected','claim_type','term_type','assessment_type')),
 (native.life,('validate','control','claim_type','event_types','make_request','run','protected')),(native.life.operating,('build','conditions'))]:
    for name in names:saved.append((mod,name,getattr(mod,name)))
def disabled(*a,**kw):raise AssertionError('native_callback_in_term_program')
try:
    for mod,name,_ in saved:setattr(mod,name,disabled)
    actuals={}
    for chart,obj in programs.items():
        before=deepcopy(obj);actual=p.execute(obj,*selections[chart]);actuals[chart]=actual
        check(actual['status']=='complete_provisional' and actual['successful_commands']==10,chart+':complete')
        check(equal(before,obj),chart+':input_unchanged')
        for step,oracle in zip(actual['steps'],expected[chart]):
            check(step['id']==oracle['command'] and equal(step['result'],oracle['result']),chart+':complete_source_result:'+step['id'])
        check(equal(actual['after'],cases[chart]['final']),chart+':complete_final_state')
        book=actual['after']['book'];roles=actual['after']['roles']
        check(book['balances'][roles['cash']]=='130/1' and book['balances'][roles['receivables']]=='0/1',chart+':independent_cash_claim_totals')
        check(all(v['remaining']=='0/1' for v in book['memory']['claims'].values()),chart+':explicit_zero_claims')
        check(book['period']==dict(start='2028-01-01',end_exclusive='2029-01-01'),chart+':independent_carried_period')
        check(equal(p.execute(obj,*selections[chart]),actual),chart+':deterministic_replay')
        dump(O/f'{chart}-result.json',actual)
    original=programs['alpha'];selection,selhash=selections['alpha'];baseline=actuals['alpha']
    def rejected(name,mutate,renew=False,expected_status='invalid_program',prefix=0):
        obj=deepcopy(original);mutate(obj)
        supplied=select(obj,selection['term_selection']) if renew else (selection,selhash)
        before=deepcopy(obj);result=p.execute(obj,*supplied)
        check(result['status']==expected_status,name+':status:'+str(result.get('reason',result.get('failed_result',{}).get('execution',{}).get('reason'))))
        check(result['successful_commands']==prefix and equal(obj,before),name+':prefix_and_input')
        if expected_status in ['partial','refused']:
            check(result['failed_index']==prefix,name+':first_failed_index')
            check(equal(result['steps'],baseline['steps'][:prefix]),name+':exact_successful_prefix')
            last=original['opening'] if prefix==0 else baseline['steps'][prefix-1]['result']['execution']['after']
            check(equal(result['after'],last),name+':last_state_unchanged')
            check(equal(result['failed_command'],obj['commands'][prefix]) and equal(result['remaining_commands'],obj['commands'][prefix+1:]),name+':exact_remaining')
        controls.append(dict(name=name,result=result));return result
    rejected('unselected_source_change',lambda o:o['rule_sources'].__setitem__('carry',o['rule_sources']['carry']+'\n'))
    rejected('unselected_command_order',lambda o:o['commands'].reverse())
    rejected('unselected_opening',lambda o:o['opening']['book']['balances'].__setitem__('cash','999/1'))
    rejected('duplicate_program_command_id',lambda o:o['commands'][1].update(id=o['commands'][0]['id']),True)
    rejected('missing_rule',lambda o:o['rule_sources'].pop('collection'),True)
    rejected('unknown_program_field',lambda o:o.update(extra=True),True)
    rejected('empty_program',lambda o:o.update(commands=[]),True)
    rejected('command_limit',lambda o:o.update(commands=[dict(id=str(i),request=deepcopy(o['commands'][0]['request'])) for i in range(65)]),True)
    rejected('malformed_source',lambda o:o.update(contract_source='malformed;\n'),True)
    rejected('stale_later_state',lambda o:o['commands'][4]['request'].update(expected_state_sha256='0'*64),True,'partial',4)
    rejected('unsupported_report',lambda o:o['commands'][3]['request'].update(profile='StandaloneReport/1'),True,'partial',3)
    rejected('unknown_first_approval',lambda o:o['commands'][0]['request']['event']['inputs']['approved'].update(value=dict(status='unknown',reason='No supplied approval')),True,'refused',0)
    rejected('partial_population',lambda o:o['coverage']['claims'].update(status='partial'),True,'refused',0)
    rejected('stale_carry_state',lambda o:o['commands'][7]['request'].update(expected_state_sha256='0'*64),True,'partial',7)
    bad=p.execute(original,selection,'0'*64);check(bad['status']=='invalid_program' and bad['reason']=='external_selection_identity','externally_wrong_selection');controls.append(dict(name='externally_wrong_selection',result=bad))
finally:
    for mod,name,value in saved:setattr(mod,name,value)
    dump(O/'assertions.json',checks);dump(O/'controls.json',controls)
for name,d in locks.items():check(sha(R/name)==d,'protected_after:'+name)
summary=dict(passed=True,programs=2,commands=20,full_source_results_equal=True,controls=len(controls),assertions=len(checks),protected_files=len(locks),native_callbacks_disabled=True,production_ready=False)
dump(O/'assertions.json',checks);dump(O/'checks.json',summary)
git=subprocess.run(['git','rev-parse','HEAD'],cwd=R,capture_output=True,text=True)
dump(O/'run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/selected-term-program-20261027/verify.py '+sys.argv[1],environment=sys.version,git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version=sha(O/'source-lock.json'),timestamp_utc=datetime.now(timezone.utc).isoformat(),plan_file='docs/plans/accounting-selected-term-program-20261027.md',result_file=str((H/'result.md').relative_to(R))))
print(json.dumps(summary))
