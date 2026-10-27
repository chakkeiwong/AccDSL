from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,subprocess,sys,time
import runner as p
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
REG=HERE.parent/'authored-method-registry-20261026'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
helpers=load('registry_comparison_helpers',REG/'verify.py')
fixtures=load('program_lifecycle_examples',ROOT/'data/accounting-master/declared-collection-state-growth-20261025/examples.py')
import declared_receivable_lifecycle_v1 as life
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,x):path.write_text(json.dumps(x,indent=2)+NL)
def build(owner):
    source,mapping,_=fixtures.lifecycle_fixture(owner);native=life.run(source);assert native['status']=='complete_provisional'
    body={'profile':p.PROFILE,'name':'authored-'+owner,'opening':deepcopy(source['opening']),
        'schemas':deepcopy(source['schemas']),'mapping':deepcopy(source['mapping']),
        'memory_definition':deepcopy(source['memory_definition']),'registries':{},'commands':[]}
    current=deepcopy(source['opening']);projections=[]
    for i,row in enumerate(native['trace']):
        command=deepcopy(row['command'])
        if command['kind']=='event':
            q=deepcopy(row['request']);declarations=p.methods.prior.event_declarations(q['method'])
            removed={k:v for k,v in q['event']['inputs'].items() if k not in declarations}
            q['event']['inputs']={k:v for k,v in q['event']['inputs'].items() if k in declarations}
            if command['method_key']=='collect':q['profile']=p.base.PROFILE;q.pop('memory_definition')
            text=p.methods.frontend.render(q['method'],q['profile'],helpers.environment(current,q))
            entry=helpers.entry(current,q,text)
            registry={'profile':p.methods.REGISTRY,'context':deepcopy(current['context']),'entries':{command['method_key']:entry}}
            h=p.digest(registry);body['registries'][h]=registry
            command={'kind':'event','registry_sha256':h,'method_key':command['method_key'],'event':deepcopy(q['event'])}
            projections.append({'index':i,'removed_event_inputs':removed,'original_request_sha256':p.digest(row['request']),
                'derived_request_sha256':p.digest(q),'transition_profile':q['profile']})
            current=deepcopy(row['result']['after'])
        elif command['kind']=='carry':
            command['memory_policies']=deepcopy(row['request']['memory_policies'])
            current=deepcopy(row['result']['next_opening'])
        else:current=deepcopy(row['request']['closing'])
        body['commands'].append(command)
    return body,native,source,mapping,projections
def main():
    started=time.monotonic();out=HERE/'examples';out.mkdir(exist_ok=True);lock_path=HERE/'source-lock.json'
    if not lock_path.exists():
        lock=json.loads((REG/'source-lock.json').read_text())
        for path in [REG/'registry.py',REG/'verify.py',REG/'checks.json',REG/'result.md',
                     ROOT/'scripts/company_book_reports_v1.py',ROOT/'scripts/company_book_carry_v1.py']:
            lock[str(path.relative_to(ROOT))]=sha(path)
        dump(lock_path,lock)
    lock=json.loads(lock_path.read_text())
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    comparisons=[];saved={}
    for owner in ['alpha','beta']:
        body,native,source,mapping,projections=build(owner);before=deepcopy(body);actual=p.run(body)
        assert actual['status']=='complete_provisional',actual.get('stop',actual)
        assert actual['current']==native['current'] and len(actual['trace'])==len(native['trace']) and body==before
        for i,(row,old) in enumerate(zip(actual['trace'],native['trace'])):
            assert row['before_sha256']==old['before_sha256'] and row['after_sha256']==old['after_sha256'],(owner,i)
            if row['command']['kind']=='event':
                effect=row['result']['transition']
                for key in ['after','journal','flows']:assert effect[key]==old['result'][key],(owner,i,key)
                q=row['result']['materialized_request'];before_book=body['opening'] if i==0 else (
                    native['trace'][i-1]['result']['after'] if native['trace'][i-1]['command']['kind']=='event' else
                    native['trace'][i-1]['result']['next_opening'] if native['trace'][i-1]['command']['kind']=='carry' else
                    native['trace'][i-1]['request']['closing'])
                assert effect==p.methods.frontend.ENGINES[q['profile']].propose(before_book,q)
            else:assert row['request']==old['request'] and row['result']==old['result'],(owner,i,'report/carry')
        assert actual['reports']==[{'id':row['id'],'result':row['result']} for row in native['reports']]
        assert actual['current']['balances'][mapping['cash']]=='130/1'
        assert actual['current']['balances'][mapping['receivables']]=='0/1'
        assert actual['reports'][-1]['result']['cash_flows']['activities']['operating']['net']=='20/1'
        assert p.verify(body,actual)
        dump(out/(owner+'.program.json'),body);dump(out/(owner+'.result.json'),actual);dump(out/(owner+'.projections.json'),projections)
        comparisons.append({'company':owner,'commands':len(actual['trace']),'full_event_effects_equal':True,'full_reports_carry_equal':True,
            'closing_cash':'130/1','closing_receivables':'0/1','next_period_operating_cash':'20/1'})
        saved[owner]=(body,actual,mapping)
    body,baseline,mapping=saved['alpha'];failures=[]
    def stopped(name,changed,index,status,reason=None):
        actual=p.run(changed);assert actual['status']=='stopped_provisional',(name,actual)
        assert actual['stop']['index']==index and actual['stop']['status']==status,(name,actual['stop'])
        if reason:assert reason in actual['stop']['reason'],(name,actual['stop']['reason'])
        assert actual['trace']==baseline['trace'][:index],name
        assert actual['remaining_commands']==changed['commands'][index:]
        expected=body['opening'] if index==0 else (baseline['trace'][index-1]['result']['transition']['after']
            if baseline['trace'][index-1]['command']['kind']=='event' else baseline['trace'][index-1]['request']['closing'])
        assert actual['current']==expected,name
        failures.append({'case':name,'index':index,'status':status,'prefix_preserved':True})
    for name,value,status in [('unknown',{'status':'unknown','reason':'unobserved'},'unresolved'),
                              ('negative',p.base.known('-1/1'),'invalid')]:
        changed=deepcopy(body);changed['commands'][1]['event']['inputs']['amount']['value']=value
        stopped(name,changed,1,status)
    changed=deepcopy(body);changed['commands'][1]['event']['inputs']['approved']['value']=p.base.known(False);stopped('false-approval',changed,1,'unsupported')
    changed=deepcopy(body);changed['commands'][1]['event']['id']=changed['commands'][0]['event']['id'];stopped('duplicate-id',changed,1,'invalid','duplicate_command_identity')
    changed=deepcopy(body);changed['commands'][3]['cutoff']='2027-01-01';stopped('report-cutoff',changed,3,'invalid','cutoff_chronology')
    changed=deepcopy(body);changed['commands'][7]['memory_policies'].pop(next(iter(changed['commands'][7]['memory_policies'])));stopped('carry-policy',changed,7,'invalid')
    changed=deepcopy(body);h=changed['commands'][1]['registry_sha256'];registry=deepcopy(changed['registries'][h])
    registry['entries']['unused']=deepcopy(next(iter(registry['entries'].values())))
    registry['entries']['unused']['account_classes']['cash']='liability'
    key=p.digest(registry);changed['registries'][key]=registry;changed['commands'][1]['registry_sha256']=key
    stopped('unselected-invalid-entry',changed,1,'invalid','role_class_mismatch')
    envelope=[]
    for name,change in [('stale-registry',lambda x:x['commands'][1].update(registry_sha256='0'*64)),
                        ('tampered-source',lambda x:next(iter(x['registries'].values()))['entries']['sale'].update(source_sha256='0'*64))]:
        changed=deepcopy(body);change(changed);actual=p.run(changed);assert actual['status']=='invalid'
        envelope.append({'case':name,'status':actual['status'],'reason':actual['reason']})
    forged=deepcopy(baseline);forged['current']['balances'][mapping['cash']]='999/1';assert not p.verify(body,forged)
    # A changed input changes the complete state, not a cached replay.
    changed=deepcopy(body);changed['commands']=changed['commands'][:1]
    changed['commands'][0]['event']['inputs']['consideration']['value']=p.base.known('32/1')
    actual=p.run(changed);assert actual['status']=='complete_provisional'
    assert actual['current']['balances'][mapping['receivables']]=='32/1'
    assert actual['current']['memory']['claims']['invoice/a~1']['remaining']=='32/1'
    # Independently edit the collection algorithm to collect half the amount.
    changed=deepcopy(body);changed['commands']=changed['commands'][:2]
    key=changed['commands'][1]['registry_sha256'];registry=deepcopy(changed['registries'][key]);entry=registry['entries']['collect']
    scalar=deepcopy(entry['method']['monetary']['definition']['inputs']['amount']['type']);scalar['dimensions']={}
    replacement='(mul (ref "amount") (const '+json.dumps(scalar,sort_keys=True,separators=(',',':'))+' "1/2"))'
    source=entry['source'];start=source.index('begin_monetary ');end=source.index('end_monetary;')
    source=source[:start]+source[start:end].replace('(ref "amount")',replacement)+source[end:]
    entry.update(source=source,source_sha256=sha256(source.encode()).hexdigest(),method=p.methods.frontend.lower(source)['method'])
    entry['method_sha256']=p.digest(entry['method']);key=p.digest(registry)
    changed['registries'][key]=registry;changed['commands'][1]['registry_sha256']=key
    actual=p.run(changed);assert actual['status']=='complete_provisional',actual.get('stop',actual)
    assert actual['current']['balances'][mapping['cash']]=='105/1'
    assert actual['current']['balances'][mapping['receivables']]=='25/1'
    assert actual['current']['memory']['claims']['invoice/a~1']['remaining']=='25/1'
    dump(out/'alpha.half-collection.program.json',changed);dump(out/'alpha.half-collection.result.json',actual)
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    checks={'passed':True,'companies':2,'complete_program_commands':sum(x['commands'] for x in comparisons),
        'full_native_reports_carry_equal':True,'stopped_prefix_cases':len(failures),'envelope_refusals':len(envelope),
        'changed_input_changes_result':True,'authored_algorithm_changes_result':True,
        'tampered_result_refused':True,'protected_files':len(lock),'admission':False}
    for name,x in [('checks.json',checks),('comparisons.json',comparisons),('stopped-cases.json',failures),('envelope-refusals.json',envelope)]:dump(HERE/name,x)
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/authored-program-composition-20261026/verify.py',
        'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic',
        'wall_seconds':time.monotonic()-started,'data_version':sha(lock_path),'plan_file':'docs/plans/accounting-authored-program-composition-20261026.md',
        'result_file':str((HERE/'result.md').relative_to(ROOT)),'artifact_paths':['checks.json','comparisons.json','stopped-cases.json','examples/'],
        'implementation_sha256':sha(HERE/'runner.py'),'verifier_sha256':sha(Path(__file__)),'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(checks))
if __name__=='__main__':main()
