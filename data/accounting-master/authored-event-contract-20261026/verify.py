from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,subprocess,sys,time
import contract as c
import contract_runner as runner
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
GUARD=HERE.parent/'authored-state-invariants-20261026';AUDIT=HERE.parent/'authored-event-prerequisite-audit-20261026'
spec=importlib.util.spec_from_file_location('contract_verification_helpers',GUARD/'verify.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+NL)
def wrap(body,source,mapping):
    result=helper.wrap(body,mapping['receivables']);result['profile']=runner.PROFILE
    result['event_contract']={'profile':c.PROFILE,'native_sha256':sha(Path(c.native.__file__)),
        'roles':deepcopy(source['roles']),'unit_cost_pointer':source['unit_cost_pointer'],'policy':deepcopy(source['policy']),
        'intents':{x['event']['id']:deepcopy(x['event']) for x in source['commands'] if x['kind']=='event'}}
    result['expected_event_contract_sha256']=c.digest(result['event_contract']);return result
def repin(body):body['expected_event_contract_sha256']=c.digest(body['event_contract'])
def main():
    started=time.monotonic();out=HERE/'examples';out.mkdir(exist_ok=True);lock_path=HERE/'source-lock.json'
    if not lock_path.exists():
        lock=json.loads((AUDIT/'source-lock.json').read_text())
        for p in [AUDIT/'probe.py',AUDIT/'checks.json',AUDIT/'result.md']:
            lock[str(p.relative_to(ROOT))]=sha(p)
        dump(lock_path,lock)
    lock=json.loads(lock_path.read_text())
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    comparisons=[];saved={}
    for owner in ['alpha','beta']:
        body,native,source,mapping,_=helper.helpers.build(owner);wrapped=wrap(body,source,mapping)
        actual=runner.run(wrapped);stop=actual.get('stop') or {}
        assert actual['status']=='complete_provisional',(owner,actual['status'],stop.get('reason',actual.get('reason')))
        prior=c.prior.run(helper.wrap(body,mapping['receivables']))
        for key in ['current','opening','reports','archives','remaining_commands','stop']:assert actual[key]==prior[key],(owner,key)
        for row,previous,native_row in zip(actual['trace'],prior['trace'],native['trace']):
            stripped={k:v for k,v in row.items() if k!='event_contract'};assert stripped==previous
            if row['command']['kind']=='event':assert row['event_contract']['native_request']==native_row['request']
        assert runner.verify(wrapped,actual)
        comparisons.append({'company':owner,'commands':len(actual['trace']),'full_native_intent_requests_equal':True,'full_prior_results_equal':True})
        dump(out/(owner+'.program.json'),wrapped);dump(out/(owner+'.result.json'),actual)
        saved[owner]=(wrapped,source,mapping,actual)
    failures=[]
    for owner,(wrapped,source,mapping,baseline) in saved.items():
        # Full original intent is mutated; the selected native contract owns refusal.
        mutations=[('wrong-customer',1,'customer',c.base.known('Different customer'),'invalid','claim_customer_mismatch'),
            ('missing-claim',1,'claim_id',c.base.known('absent'),'invalid','unknown_claim'),
            ('unknown-customer',1,'customer',{'status':'unknown','reason':'unobserved'},'unresolved','unknown_event_inputs'),
            ('false-approval',1,'approved',c.base.known(False),'unsupported','applicability_not_selected'),
            ('assessment-start',2,'start',c.base.known('2027-01-02'),'invalid','assessment_cursor'),
            ('assessment-end',2,'end_exclusive',c.base.known('2027-02-02'),'invalid','assessment_window'),
            ('due-before-sale',0,'due',c.base.known('2027-01-01'),'invalid','due_before_sale')]
        for name,index,key,value,status,reason in mutations:
            original=deepcopy(source);original['commands'][index]['event']['inputs'][key]['value']=value
            native=c.native.run(original);assert native['status']=='stopped_provisional' and native['stop']['status']==status and native['stop']['reason']==reason,(name,native.get('stop'))
            changed=deepcopy(wrapped);identity=changed['commands'][index]['event']['id']
            changed['event_contract']['intents'][identity]=deepcopy(original['commands'][index]['event']);repin(changed)
            actual=runner.run(changed);stop=actual.get('stop') or {}
            assert actual['status']=='stopped_provisional' and stop['index']==index and stop['status']==status and reason in stop['reason'],(name,actual['status'],stop.get('reason'))
            assert actual['trace']==baseline['trace'][:index] and actual['current']==native['current']
            assert actual['remaining_commands']==changed['commands'][index:]
            failures.append({'company':owner,'case':name,'index':index,'status':status,'native_reason':reason,'prefix_equal':True})
        # A same-day event after the January assessment violates its sealed cursor.
        original=deepcopy(source);event=deepcopy(original['commands'][1]);event['event'].update(id='late.same.day',date='2027-01-31')
        original['commands']=original['commands'][:3]+[event];native=c.native.run(original)
        changed=deepcopy(wrapped);event=deepcopy(changed['commands'][1]);event['event'].update(id='late.same.day',date='2027-01-31')
        changed['commands']=changed['commands'][:3]+[event]
        changed['event_contract']['intents']={x['event']['id']:deepcopy(x['event']) for x in original['commands']};repin(changed)
        actual=runner.run(changed);assert actual['stop']['reason']==native['stop']['reason']=='assessment_day_sealed'
        assert actual['current']==native['current'] and actual['trace']==baseline['trace'][:3]
        failures.append({'company':owner,'case':'sealed-window','index':3,'status':'invalid','prefix_equal':True})
        original=deepcopy(source);event=deepcopy(original['commands'][0]);event['event'].update(id='sale.duplicate',date='2027-01-03')
        original['commands']=original['commands'][:1]+[event];native=c.native.run(original)
        changed=deepcopy(wrapped);event=deepcopy(changed['commands'][0]);event['event'].update(id='sale.duplicate',date='2027-01-03')
        changed['commands']=changed['commands'][:1]+[event]
        changed['event_contract']['intents']={x['event']['id']:deepcopy(x['event']) for x in original['commands']};repin(changed)
        actual=runner.run(changed);assert actual['stop']['reason']==native['stop']['reason']=='duplicate_claim'
        assert actual['current']==native['current'] and actual['trace']==baseline['trace'][:1]
        failures.append({'company':owner,'case':'duplicate-claim','index':1,'status':'invalid','prefix_equal':True})
    wrapped,source,mapping,baseline=saved['alpha'];specialization=[]
    changed=deepcopy(wrapped);changed['commands'][1]['event']['inputs']['amount']['value']=c.base.known('11/1')
    actual=runner.run(changed);assert actual['stop']['reason']=='selected_method_intent_mismatch'
    specialization.append('projected-value-mismatch')
    # The half-collection algorithm is allowed by authoring but violates this selected contract.
    path=HERE.parent/'authored-program-composition-20261026/examples/alpha.half-collection.program.json'
    variant=json.loads(path.read_text());original=deepcopy(source);original['commands']=original['commands'][:2]
    variant=wrap(variant,original,mapping);actual=runner.run(variant)
    assert actual['status']=='stopped_provisional' and actual['stop']['index']==1 and actual['stop']['reason']=='selected_method_intent_mismatch'
    specialization.append('half-payment-contract-mismatch')
    changed=deepcopy(wrapped);changed['event_contract']['native_sha256']='0'*64;repin(changed)
    assert runner.run(changed)['reason']=='native_contract_hash'
    changed=deepcopy(wrapped);changed['expected_event_contract_sha256']='0'*64;assert runner.run(changed)['reason']=='event_contract_hash'
    changed=deepcopy(wrapped);changed['event_contract']['intents'].pop(next(iter(changed['event_contract']['intents'])));repin(changed)
    assert runner.run(changed)['reason']=='exact_intent_population'
    forged=deepcopy(baseline);forged['trace'][0]['event_contract']['native_request']['event']['id']='changed';assert not runner.verify(wrapped,forged)
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    checks={'passed':True,'companies':2,'preserved_commands':sum(x['commands'] for x in comparisons),
        'matched_native_refusals':len(failures),'specialization_refusals':len(specialization),
        'full_intent_requests_preserved':True,'exact_prefixes_preserved':True,'identity_refusals':3,
        'tampering_refused':True,'protected_files':len(lock),'general_portable_event_contract':False,'admission':False}
    for name,x in [('checks.json',checks),('comparisons.json',comparisons),('native-refusals.json',failures),('specialization-refusals.json',specialization)]:dump(HERE/name,x)
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/authored-event-contract-20261026/verify.py',
        'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-started,
        'data_version':sha(lock_path),'plan_file':'docs/plans/accounting-authored-event-contract-20261026.md','result_file':str((HERE/'result.md').relative_to(ROOT)),
        'artifact_paths':['checks.json','comparisons.json','native-refusals.json','examples/'],'implementation_sha256':{'contract':sha(HERE/'contract.py'),'runner':sha(HERE/'contract_runner.py')},
        'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(checks))
if __name__=='__main__':main()
