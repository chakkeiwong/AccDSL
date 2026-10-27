from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,sys,subprocess,time
import guards as g
import guarded_runner as runner
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
PROGRAM=HERE.parent/'authored-program-composition-20261026';AUDIT=HERE.parent/'authored-program-invariant-audit-20261026'
spec=importlib.util.spec_from_file_location('guarded_program_helpers',PROGRAM/'verify.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+NL)
def wrap(body,account):
    result=deepcopy(body);result['profile']=runner.PROFILE
    result['state_invariant']=g.receivable_definition(body['opening'],account)
    result['expected_invariant_sha256']=g.digest(result['state_invariant']);return result
def main():
    started=time.monotonic();out=HERE/'examples';out.mkdir(exist_ok=True);lock_path=HERE/'source-lock.json'
    if not lock_path.exists():
        lock=json.loads((AUDIT/'source-lock.json').read_text())
        for p in [AUDIT/'probe.py',AUDIT/'checks.json',AUDIT/'result.md',ROOT/'scripts/method_collections_v1.py',ROOT/'scripts/method_collection_totals_v1.py']:
            lock[str(p.relative_to(ROOT))]=sha(p)
        for p in (AUDIT/'examples').glob('*.json'):lock[str(p.relative_to(ROOT))]=sha(p)
        dump(lock_path,lock)
    lock=json.loads(lock_path.read_text())
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    comparisons=[];books=[];saved={}
    for owner in ['alpha','beta']:
        body,native,source,mapping,_=helpers.build(owner);wrapped=wrap(body,mapping['receivables'])
        actual=runner.run(wrapped);stop=actual.get('stop') or {}
        assert actual['status']=='complete_provisional',(owner,actual['status'],stop.get('reason',actual.get('reason')))
        ordinary=g.program.run(body)
        for key in ['current','opening','trace','reports','archives','remaining_commands','stop']:assert actual[key]==ordinary[key],(owner,key)
        assert runner.verify(wrapped,actual)
        all_books=[body['opening']]
        for row in actual['trace']:
            kind=row['command']['kind'];book=(row['result']['transition']['after'] if kind=='event' else row['result']['next_opening'] if kind=='carry' else row['request']['closing'])
            helpers.life.control(book,source['roles']);all_books.append(book)
        for book in all_books:
            assessment=g.assess(wrapped['state_invariant'],book,body['memory_definition'],body['schemas'])
            assert assessment['status']=='collection_total_requirements_satisfied',assessment.get('reason')
        comparisons.append({'company':owner,'commands':len(actual['trace']),'full_prior_results_equal':True,'native_controls_passed':len(all_books)})
        dump(out/(owner+'.program.json'),wrapped);dump(out/(owner+'.result.json'),actual)
        saved[owner]=(wrapped,source,mapping,all_books)
    refused=[]
    for path in sorted((AUDIT/'examples').glob('*.json')):
        row=json.loads(path.read_text());owner=row['comparison']['company'];wrapped,source,mapping,_=saved[owner]
        bad=wrap(row['program'],mapping['receivables']);actual=runner.run(bad);stop=actual.get('stop') or {}
        assert actual['status']=='stopped_provisional' and stop['index']==0 and stop['stage']=='after',(path.name,actual['status'],stop.get('reason'))
        assert actual['trace']==[] and actual['current']==bad['opening'] and actual['remaining_commands']==bad['commands']
        assert stop['invariant']['status']=='invalid'
        refused.append({'case':path.stem,'status':'invalid','stage':'after','successful_prefix':0,'original_gap_repaired':True})
        dump(out/(path.stem+'.refusal.json'),stop['invariant'])
    wrapped,source,mapping,all_books=saved['alpha'];spec=wrapped['state_invariant'];book=all_books[1]
    values,_=g.bind(spec,book,wrapped['memory_definition'],wrapped['schemas'])
    unknown=deepcopy(values);unknown['collections']['claims']['rows'][0]['remaining']={'status':'unknown','reason':'unobserved'}
    partial=deepcopy(values);partial['collections']['claims'].update(status='partial',reason='incomplete supplied set')
    for changed in [unknown,partial]:assert g.totals.assess(spec['definition'],changed,[])['status']=='unresolved'
    bad=deepcopy(values);bad['collections']['claims']['rows'][0]['remaining']=g.base.known('31/1')
    bad['collections']['claims']['rows'][0]['customer']={'status':'unknown','reason':'unknown label'}
    assert g.totals.assess(spec['definition'],bad,[])['status']=='invalid'
    negatives=[]
    mutations=[('wrong-context',lambda x:x['context'].update(entity='Other')),
        ('missing-pointer',lambda x:x['collections']['claims'].update(pointer='/absent')),
        ('record-not-map',lambda x:x['collections']['claims'].update(pointer='/stock')),
        ('wrong-account',lambda x:x['globals']['receivable'].update(account='absent')),
        ('wrong-row-type',lambda x:x['definition']['snapshot']['collections']['claims']['fields']['remaining']['type'].update(dimensions={}))]
    for name,mutate in mutations:
        changed=deepcopy(spec);mutate(changed);result=g.assess(changed,book,wrapped['memory_definition'],wrapped['schemas'])
        assert result['status']=='invalid';negatives.append({'case':name,'reason':result.get('reason','assessment_invalid')})
    bad=deepcopy(wrapped);bad['expected_invariant_sha256']='0'*64;assert runner.run(bad)['reason']=='invariant_digest'
    unsupported=deepcopy(wrapped)
    unsupported['state_invariant']['definition']['assessment']['capabilities']=['unavailable.test.capability']
    unsupported['expected_invariant_sha256']=g.digest(unsupported['state_invariant'])
    assert runner.run(unsupported)['status']=='unsupported'
    unresolved=deepcopy(wrapped)
    unresolved['state_invariant']['definition']['assessment']['requirements'][0]['on_false']='unsupported'
    unresolved['expected_invariant_sha256']=g.digest(unresolved['state_invariant'])
    source_case=json.loads((AUDIT/'examples/alpha.claim-total.json').read_text())
    unresolved['registries']=source_case['program']['registries'];unresolved['commands']=source_case['program']['commands']
    uncertain=runner.run(unresolved);assert uncertain['status']=='stopped_provisional' and uncertain['stop']['status']=='unsupported'
    assert uncertain['trace']==[] and uncertain['current']==unresolved['opening']
    forged=runner.run(wrapped);forged['current']['balances'][mapping['cash']]='999/1';assert not runner.verify(wrapped,forged)
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    checks={'passed':True,'companies':2,'preserved_command_results':sum(x['commands'] for x in comparisons),
        'native_state_controls':sum(x['native_controls_passed'] for x in comparisons),'counterexamples_refused':len(refused),
        'binding_refusals':len(negatives),'partial_unknown_preserved':True,'postfailure_prefix_preserved':True,
        'definition_hash_checked':True,'distinct_guard_outcomes_preserved':True,
        'tampering_refused':True,'protected_files':len(lock),'admission':False}
    for name,x in [('checks.json',checks),('comparisons.json',comparisons),('repaired-counterexamples.json',refused),('binding-refusals.json',negatives)]:dump(HERE/name,x)
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/authored-state-invariants-20261026/verify.py',
        'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic',
        'wall_seconds':time.monotonic()-started,'data_version':sha(lock_path),'plan_file':'docs/plans/accounting-authored-state-invariants-20261026.md',
        'result_file':str((HERE/'result.md').relative_to(ROOT)),'artifact_paths':['checks.json','comparisons.json','examples/'],
        'implementation_sha256':{'guards':sha(HERE/'guards.py'),'runner':sha(HERE/'guarded_runner.py')},
        'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(checks))
if __name__=='__main__':main()
