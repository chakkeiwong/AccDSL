from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
import composer as m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'authored-event-contract-20261026'))
import contract
import declared_receivable_lifecycle_v1 as native

def read(p):return json.loads(p.read_text())
def dump(name,v):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def sha(p):return sha256(p.read_bytes()).hexdigest()
def equal(a,b):return m.core.canonical(a)==m.core.canonical(b)
def known(v):return dict(status='known',value=v)

def prepare():
    assert not (HERE/'examples').exists(),'Do not rerun preparation'
    source=HERE.parent/'ordered-event-eligibility-20261026';lock=read(source/'source-lock.json')
    for folder in (source,HERE.parent/'authored-state-invariants-20261026'):
        for p in folder.iterdir():
            if p.is_file() and p.suffix in ('.py','.json','.md'):lock[str(p.relative_to(ROOT))]=sha(p)
    rows=read(HERE.parent/'event-specialization-audit-20261026/request-comparisons.json')
    for owner in ('alpha','beta'):
        prior=read(HERE.parent/f'authored-event-contract-20261026/examples/{owner}.program.json')
        nativebody=contract.native_body(prior);native.validate(nativebody);baseline=native.run(nativebody)
        assert baseline['status']=='complete_provisional'
        rules={}
        for kind in ('sale','collect','assess'):
            eligibility=read(source/f'templates/{owner}.{kind}.json')
            folder='ordered-assessment-expansion-20261026' if kind=='assess' else 'parameterized-method-construction-20261026'
            construction=read(HERE.parent/f'{folder}/templates/{owner}.{kind}.json')
            rules[kind]=dict(eligibility=eligibility,eligibility_sha256=m.core.digest(eligibility),
                             construction=construction,construction_sha256=m.core.digest(construction))
        commands=[]
        for index,cmd in enumerate(prior['commands']):
            command=deepcopy(cmd)
            if cmd['kind']=='event':
                command.pop('registry_sha256');command['event']=deepcopy(prior['event_contract']['intents'][cmd['event']['id']])
                command['order']=list(next(r for r in rows if r['company']==owner and r['index']==index)['before']['memory']['claims']) if cmd['method_key']=='assess' else None
            commands.append(command)
        body={k:deepcopy(prior[k]) for k in ('name','opening','schemas','mapping','memory_definition','state_invariant')}
        body.update(profile=m.PROFILE,invariant_sha256=m.core.digest(body['state_invariant']),rules=rules,commands=commands,
                    carry_policy=dict(mode='preserve_all_memory',provenance=prior['event_contract']['policy']['provenance']),
                    residuals=['Native opening admission is a separately checked prerequisite',
                               'Two synthetic charts; no source/accounting/production admission'])
        m.validate(body,m.make_call(body))
        dump(f'examples/{owner}.program.json',body);dump(f'examples/{owner}.native-input.json',nativebody)
        dump(f'examples/{owner}.native-result.json',baseline)
    for name,digest in lock.items():assert sha(ROOT/name)==digest,name
    dump('source-lock.json',lock);print(json.dumps(dict(prepared=2,protected_files=len(lock))))

def verify():
    start=time.monotonic();lock=read(HERE/'source-lock.json');assertions=[];comparisons=[];adverse=[];controls=[]
    for name,digest in lock.items():assert sha(ROOT/name)==digest,name
    def ensure(ok,label):assertions.append(dict(check=label,passed=bool(ok)));assert ok,label
    originals={n:getattr(native,n) for n in ('validate','control','event_types','make_request','run','observation')}
    def disabled(*args,**kwargs):raise AssertionError('native lifecycle callback in candidate execution')
    def run(body,call=None):
        before=m.core.digest(body)
        try:
            for n in originals:setattr(native,n,disabled)
            result=m.run(body,m.make_call(body) if call is None else call)
        finally:
            for n,value in originals.items():setattr(native,n,value)
        ensure(m.core.digest(body)==before,'program_input_unchanged');return result
    def compare(label,body,baseline,result):
        ensure(result['status']==baseline['status'],label+':status:'+str(result.get('reason')))
        ensure(result['successful_commands']==baseline['successful_commands'],label+':prefix_length')
        ensure(equal(result['current'],baseline['current']),label+':current')
        for i,(left,right) in enumerate(zip(result['trace'],baseline['trace'])):
            for field in ('request','result','before_sha256','after_sha256'):
                ensure(equal(left[field],right[field]),label+':command:'+str(i)+':'+field)
            state=left['result']['after'] if left['command']['kind']=='event' else left['result']['next_opening'] if left['command']['kind']=='carry' else None
            if state is None:
                state=deepcopy(body['opening'] if i==0 else states[-1]);state['date']=left['command']['cutoff']
            if i==0:states=[]
            states.append(state)
            ensure(equal(native.observation(state),right['observation']),label+':observation:'+str(i))
        ensure(len(result['reports'])==len(baseline['reports']),label+':report_count')
        for left,right in zip(result['reports'],baseline['reports']):
            ensure(left['id']==right['id'] and equal(left['result'],right['result']),label+':complete_report:'+left['id'])
        expected_opening=body['opening']
        for item in baseline['trace']:
            if item['command']['kind']=='carry':expected_opening=item['result']['next_opening']
        ensure(equal(result['opening'],expected_opening),label+':opening')
        ensure(equal(result['remaining_commands'],body['commands'][baseline['successful_commands']:]),label+':unexecuted_suffix')
        if baseline['stop']:
            ensure(result['stop']['status']==baseline['stop']['status'] and result['stop']['reason']==baseline['stop']['reason'],label+':stop')
            if 'inputs' in baseline['stop']:
                ensure(result['stop']['eligibility']['inputs']==baseline['stop']['inputs'],label+':unknown_inputs')
            if 'result' in baseline['stop']:
                ensure(equal(result['stop']['result'],baseline['stop']['result']),label+':complete_refused_transition')
        else:ensure(result['stop'] is None,label+':no_stop')
        return dict(case=label,all_complete_command_requests_results_equal=True,all_state_hashes_equal=True,
                    complete_report_results_equal=True,observations_recomputed_equal=True,
                    successful_commands=result['successful_commands'],status=result['status'],
                    wrapper_difference='Candidate adds ordered eligibility/construction/invariant evidence and explicit opening state; native implementation/observation wrappers are not claimed byte-identical')
    bodies={o:read(HERE/f'examples/{o}.program.json') for o in ('alpha','beta')}
    natives={o:read(HERE/f'examples/{o}.native-input.json') for o in ('alpha','beta')}
    for owner,body in bodies.items():
        result=run(body);baseline=read(HERE/f'examples/{owner}.native-result.json')
        comparisons.append(compare(owner,body,baseline,result));dump(f'examples/{owner}.result.json',result)
        saved=read(HERE/f'examples/{owner}.result.json');ensure(equal(run(body),saved),owner+':saved_recomputed')
    # Fresh complete programs use the previously checked new scalar events, not
    # retained finished event methods or any native result as candidate input.
    scalar=read(HERE.parent/'parameterized-method-construction-20261026/cases.json')
    new_comparisons=[]
    for owner,original in bodies.items():
        rows=[r for r in scalar if r['company']==owner and '_new_' in r['case']]
        body=deepcopy(original);commands=[]
        for row in rows:commands.append(dict(kind='event',method_key=row['method'],event=deepcopy(row['event']),order=None))
        final=rows[-1]['complete_transition']['after'];order=list(final['memory']['claims'])
        assessment=deepcopy(original['commands'][2]);assessment['event'].update(id='new.assessment.yearend',date='2027-12-31')
        assessment['event']['inputs']['start']['value']=known('2027-01-01');assessment['event']['inputs']['end_exclusive']['value']=known('2028-01-01');assessment['order']=order
        commands.append(assessment)
        report=deepcopy(original['commands'][6]);report['id']='new.report.yearend';commands.append(report)
        carry=deepcopy(original['commands'][7]);carry['id']='new.boundary'
        carry['memory_policies']={p:dict(kind='preserve',provenance=body['carry_policy']['provenance']) for p in final['memory_types']};commands.append(carry)
        assessment=deepcopy(assessment);assessment['event'].update(id='new.assessment.nextyear',date='2028-01-31')
        assessment['event']['inputs']['start']['value']=known('2028-01-01');assessment['event']['inputs']['end_exclusive']['value']=known('2028-02-01');commands.append(assessment)
        report=deepcopy(original['commands'][-1]);report.update(id='new.report.nextyear',cutoff='2028-01-31');commands.append(report)
        body['commands']=commands;nativebody=deepcopy(natives[owner]);nativebody['commands']=[]
        for cmd in commands:
            x=deepcopy(cmd)
            if x['kind']=='event':x.pop('order')
            if x['kind']=='carry':x.pop('memory_policies')
            nativebody['commands'].append(x)
        baseline=native.run(nativebody);ensure(baseline['status']=='complete_provisional',owner+':new_native_complete')
        result=run(body);new_comparisons.append(compare(owner+':new_population',body,baseline,result))
        dump(f'examples/{owner}.new-program.json',body);dump(f'examples/{owner}.new-native-input.json',nativebody)
        dump(f'examples/{owner}.new-native-result.json',baseline);dump(f'examples/{owner}.new-result.json',result)
        ensure(equal(run(body),read(HERE/f'examples/{owner}.new-result.json')),owner+':new_saved_recomputed')
    # Complete original refusal programs, preserving each successful prefix.
    mutations=[('wrong-customer',1,'customer',known('Different customer')),
               ('missing-claim',1,'claim_id',known('absent')),
               ('unknown-customer',1,'customer',dict(status='unknown',reason='unobserved')),
               ('false-approval',1,'approved',known(False)),('assessment-start',2,'start',known('2027-01-02')),
               ('assessment-end',2,'end_exclusive',known('2027-02-02')),('due-before-sale',0,'due',known('2027-01-01')),
               ('negative-collection',1,'amount',known('-1/1')),('excess-collection',1,'amount',known('1000/1'))]
    for owner,original in bodies.items():
        for label,index,key,value in mutations:
            body=deepcopy(original);body['commands'][index]['event']['inputs'][key]['value']=value
            nativebody=deepcopy(natives[owner]);nativebody['commands'][index]['event']['inputs'][key]['value']=value
            baseline=native.run(nativebody);result=run(body);record=compare(owner+':'+label,body,baseline,result)
            if 'result' in baseline['stop']:
                expected=native.make_request(baseline['current'],nativebody,nativebody['commands'][index])
                ensure(equal(result['stop']['request'],expected),owner+':'+label+':complete_refused_request')
                ensure(result['stop']['eligibility']['status']=='eligible',owner+':'+label+':eligibility_precedes_financial_refusal')
            adverse.append(dict(**record,program=body,native_program=nativebody,native_result=baseline,result=result))
        for label,index,source,key,day in [('sealed-window',3,1,'late.same.day','2027-01-31'),('duplicate-claim',1,0,'sale.duplicate','2027-01-03')]:
            body=deepcopy(original);cmd=deepcopy(body['commands'][source]);cmd['event'].update(id=key,date=day);body['commands']=body['commands'][:index]+[cmd]
            nativebody=deepcopy(natives[owner]);cmd=deepcopy(nativebody['commands'][source]);cmd['event'].update(id=key,date=day);nativebody['commands']=nativebody['commands'][:index]+[cmd]
            baseline=native.run(nativebody);result=run(body);record=compare(owner+':'+label,body,baseline,result)
            adverse.append(dict(**record,program=body,native_program=nativebody,native_result=baseline,result=result))
        for label,customer in [('unknown_false_missing',dict(status='unknown',reason='missing')),('false_missing',known('Wrong customer'))]:
            body=deepcopy(original);nativebody=deepcopy(natives[owner])
            for b in (body,nativebody):
                inputs=b['commands'][1]['event']['inputs'];inputs['customer']['value']=customer;inputs['approved']['value']=known(False);inputs['claim_id']['value']=known('absent')
            baseline=native.run(nativebody);result=run(body);record=compare(owner+':'+label,body,baseline,result)
            adverse.append(dict(**record,program=body,native_program=nativebody,native_result=baseline,result=result))
    control_cases(bodies,natives,run,compare,ensure,controls)
    dump('comparisons.json',comparisons);dump('new-comparisons.json',new_comparisons);dump('adverse.json',adverse);dump('controls.json',controls)
    for row in read(HERE/'adverse.json'):
        ensure(equal(run(row['program']),row['result']),row['case']+':saved_adverse_recomputed')
    for name,digest in lock.items():ensure(sha(ROOT/name)==digest,'protected:'+name)
    summary=dict(passed=True,complete_programs=len(comparisons),complete_commands=sum(x['successful_commands'] for x in comparisons),
                 original_refusal_programs=18,adverse_programs=len(adverse),controls=len(controls),assertions=len(assertions),
                 new_complete_programs=len(new_comparisons),new_complete_commands=sum(x['successful_commands'] for x in new_comparisons),
                 protected_files=len(lock),native_lifecycle_disabled_during_execution=True,
                 native_opening_admission_separate=True,accounting_admission=False,production_ready=False)
    dump('checks.json',summary);dump('assertions.json',assertions)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
        command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/declarative-event-program-20261026/verify.py verify',
        environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,
        data_version=sha(HERE/'source-lock.json'),plan_file='docs/plans/accounting-declarative-event-program-20261026.md',
        result_file='data/accounting-master/declarative-event-program-20261026/result.md',
        artifacts=['examples','comparisons.json','adverse.json','controls.json','checks.json','assertions.json'],
        implementation_sha256={n:sha(HERE/n) for n in ('composer.py','verify.py')},timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

def control_cases(bodies,natives,run,compare,ensure,controls):
    original=bodies['alpha']
    def refused(label,body,reason,call=None,stage='validation',prefix=0):
        result=run(body,call)
        if result['status']=='stopped_provisional':
            ensure(result['successful_commands']==prefix and reason in result['stop']['reason'],label+':stopped')
        else:ensure(result['status']=='invalid' and reason in result['reason'] and result['executed_commands']==0,label+':validation:'+result.get('reason',''))
        controls.append(dict(case=label,result=result));return result
    for field in ('program_sha256','input_order_sha256'):
        call=m.make_call(original);call[field]='0'*64;refused('stale_'+field,original,'stale_'+field.split('_sha256')[0],call)
    body=deepcopy(original);body['invariant_sha256']='0'*64;refused('stale_invariant',body,'invariant_digest')
    body=deepcopy(original);body['rules']['sale']['construction_sha256']='0'*64;refused('stale_construction',body,'rule_digest:construction')
    body=deepcopy(original);body['rules']['collect']['eligibility']['stages'][3]['manifest']['requirements'][0]['predicate']['op']='callback'
    body['rules']['collect']['eligibility_sha256']=m.core.digest(body['rules']['collect']['eligibility'])
    refused('malformed_later_rule_before_first_event',body,'unsupported_operator:callback')
    body=deepcopy(original);body['commands'][0]['event']['inputs']['customer']['value']=dict(status='unknown',reason='unknown')
    call=m.make_call(body);body['commands'][0]['event']['inputs']=dict(reversed(list(body['commands'][0]['event']['inputs'].items())))
    refused('reordered_inputs_stale_call',body,'stale_input_order',call)
    body=deepcopy(original);body['commands'][1]['event']['id']=body['commands'][0]['event']['id']
    nativebody=deepcopy(natives['alpha']);nativebody['commands'][1]['event']['id']=nativebody['commands'][0]['event']['id']
    baseline=native.run(nativebody);result=run(body);compare('duplicate_identity',body,baseline,result)
    controls.append(dict(case='duplicate_identity',result=result,native=baseline))
    body=deepcopy(original);body['commands'][7]['memory_policies'][next(iter(body['commands'][7]['memory_policies']))]['provenance']='Wrong policy provenance'
    result=refused('changed_carry_policy',body,'selected_carry_policy',prefix=7)
    ensure(result['current']['date']=='2027-12-31','carry_prefix_date')
    ensure(result['current']==run({**deepcopy(original),'commands':deepcopy(original['commands'][:7])})['current'],'carry_prefix_preserved')
    ensure(result['remaining_commands']==body['commands'][7:],'carry_unexecuted_suffix')
    body=deepcopy(original);body['commands'][2]['order']=[]
    refused('missing_assessment_key',body,'order_coverage',prefix=2)
    # Type-correct sale row with an incorrect remaining amount: the transition
    # succeeds but the separately selected aggregate invariant vetoes commitment.
    body=deepcopy(original);tree=body['rules']['sale']['construction']['method_template']
    fields=tree['fields']['memory']['fields']['definition']['fields']['operations']['items'][0]['fields']['value']['fields']['fields']['fields']
    fields['remaining']=m.expander.encode({'kind':'literal','value':'0/1'})
    body['rules']['sale']['construction_sha256']=m.core.digest(body['rules']['sale']['construction'])
    result=run(body)
    ensure(result['status']=='stopped_provisional' and result['successful_commands']==0,'after_invariant_stops')
    ensure(result['stop']['failed_stage']=='after' and result['stop']['result']['status']=='proposed','typed_transition_then_invariant_refusal')
    ensure(result['current']==body['opening'] and result['opening']==body['opening'] and result['trace']==[],'after_invariant_rolls_back')
    ensure(result['remaining_commands']==body['commands'],'after_invariant_complete_suffix')
    controls.append(dict(case='after_invariant_veto',program=body,result=result))
    body=deepcopy(original);body['commands']=body['commands']*6
    refused('command_limit',body,'command_limit')

if __name__=='__main__':{'prepare':prepare,'verify':verify}[sys.argv[1]]()
