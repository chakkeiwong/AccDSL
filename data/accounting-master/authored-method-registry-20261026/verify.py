from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,subprocess,sys,time
import registry as r
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
AUTHOR=HERE.parent/'complete-method-authoring-20261026'
AUDIT=HERE.parent/'complete-method-authoring-audit-20261026'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+NL)
def entry(book,q,source):
    method=q['method'];e={'method_sha256':r.digest(method),'method':deepcopy(method),'schemas':deepcopy(q['schemas']),
        'account_classes':{key:book['accounts'][account]['classification'] for key,account in method['account_map'].items()},
        'event_inputs':r.prior.event_declarations(method),'metadata_bindings':{},'clock':{'kind':'direct_event_date'},
        'transition_profile':q['profile'],'source':source,'source_sha256':sha256(source.encode()).hexdigest()}
    if q['profile']==r.frontend.v2.PROFILE:e['memory_definition']=deepcopy(q['memory_definition'])
    return e
def call(book,entries,key,event):
    registry={'profile':r.REGISTRY,'context':deepcopy(book['context']),'entries':deepcopy(entries)}
    return {'profile':r.PROFILE,'expected_state_sha256':r.digest(book),'expected_registry_sha256':r.digest(registry),
            'registry':registry,'method_key':key,'event':deepcopy(event)}
def environment(book,q):
    e={'book':deepcopy(book),'event':deepcopy(q['event']),'schemas':deepcopy(q['schemas'])}
    if 'memory_definition' in q:e['memory_definition']=deepcopy(q['memory_definition'])
    return e
def repin(c):c['expected_registry_sha256']=r.digest(c['registry']);return c
def main():
    started=time.monotonic();out=HERE/'examples';out.mkdir(exist_ok=True)
    lock_path=HERE/'source-lock.json'
    if not lock_path.exists():
        files=json.loads((AUTHOR/'source-lock.json').read_text())
        extra=[AUTHOR/'frontend.py',AUTHOR/'verify.py',AUTHOR/'checks.json',AUTHOR/'result.md',
               ROOT/'scripts/company_method_clock_v1.py',ROOT/'scripts/company_method_clock_v2.py',
               ROOT/'scripts/declared_receivable_lifecycle_v1.py',
               ROOT/'data/accounting-master/declared-collection-state-growth-20261025/examples.py']
        extra+=list((AUTHOR/'examples').glob('*.acc'))
        for p in extra:files[str(p.relative_to(ROOT))]=sha(p)
        dump(lock_path,files)
    lock=json.loads(lock_path.read_text())
    for p,h in lock.items():assert sha(ROOT/p)==h,p
    rows=[];examples={};economic=[]
    for path in sorted((AUDIT/'examples').glob('*.json')):
        d=json.loads(path.read_text());book,q=d['book'],d['request'];source=(AUTHOR/'examples'/(path.stem+'.acc')).read_text()
        e=entry(book,q,source);c=call(book,{'authored':e},'authored',q['event']);before=deepcopy((book,c))
        assert r.materialize(book,c)==q
        engine=r.frontend.ENGINES[q['profile']];native=engine.propose(book,q);result=r.propose(book,c)
        assert result['status']=='proposed' and result['transition']==native
        assert r.apply(book,c,result)['transition']==engine.apply(book,q,native)
        assert (book,c)==before
        if q['profile']==r.frontend.v1.PROFILE:
            old_entry={k:v for k,v in e.items() if k not in ['source','source_sha256','transition_profile']}
            old=call(book,{'authored':old_entry},'authored',q['event']);old['profile']=r.prior.PROFILE
            old['registry']['profile']=r.prior.REGISTRY;repin(old)
            assert r.prior.materialize(book,old)==q and r.prior.propose(book,old)['transition']==native
        rows.append({'method':path.stem,'transition_profile':q['profile'],'full_request_equal':True,'full_result_equal':True})
        dump(out/(path.stem+'.call.json'),c);dump(out/(path.stem+'.result.json'),result)
        examples[path.stem]=(book,c)
        amount='amount' if path.stem.startswith('payment') else 'consideration'
        for name,key,value,status in [('unknown',amount,{'status':'unknown','reason':'unobserved'},'unresolved'),
                ('negative',amount,r.base.known('-1/1'),'invalid'),('false-approval','approved',r.base.known(False),'unsupported')]:
            changed=deepcopy(c);changed['event']['inputs'][key]['value']=value
            actual=r.propose(book,changed);assert actual['status']==status and 'after' not in actual.get('transition',{})
            economic.append({'method':path.stem,'case':name,'status':status})
    failures=[];book,valid=examples['payment.alpha']
    def refusal(name,c,reason):
        actual=r.propose(book,c);assert actual['status'] in ['invalid','unsupported'] and reason in actual['reason'],(name,actual)
        failures.append({'case':name,'status':actual['status'],'reason':actual['reason']})
    c=deepcopy(valid);c['expected_state_sha256']='0'*64;refusal('stale-state',c,'stale_state')
    c=deepcopy(valid);c['expected_registry_sha256']='0'*64;refusal('stale-registry',c,'registry_digest')
    c=deepcopy(valid);c['method_key']='missing';refusal('unknown-method',c,'unregistered_method')
    mutations=[('method-hash',lambda e:e.update(method_sha256='0'*64),'method_digest'),
        ('source-hash',lambda e:e.update(source_sha256='0'*64),'source_digest'),
        ('unsupported-transition',lambda e:e.update(transition_profile='Unknown/1'),'transition_profile'),
        ('unsupported-clock',lambda e:e['clock'].update(kind='annual'),'clock_family'),
        ('missing-schema',lambda e:e['schemas'].clear(),'memory_schema_unavailable'),
        ('wrong-account-class',lambda e:e['account_classes'].update(cash='liability'),'role_class_mismatch'),
        ('extra-field',lambda e:e.update(inferred=True),'fields'),
        ('metadata-overlap',lambda e:e['metadata_bindings'].update(amount='id'),'metadata_input_overlap')]
    for name,change,reason in mutations:
        for unselected in [False,True]:
            c=deepcopy(valid);key='unselected' if unselected else 'authored'
            if unselected:c['registry']['entries'][key]=deepcopy(c['registry']['entries']['authored'])
            change(c['registry']['entries'][key]);refusal(name+('-unselected' if unselected else ''),repin(c),reason)
    c=deepcopy(valid);c['registry']['context']['entity']='other';refusal('wrong-context',repin(c),'registry_context')
    c=deepcopy(valid);e=c['registry']['entries']['authored'];e['source']=e['source'].replace('residual "Constructed','residual "Changed constructed')
    e['source_sha256']=sha256(e['source'].encode()).hexdigest();refusal('source-method-mismatch',repin(c),'source_method_correspondence')
    c=deepcopy(valid);c['event']['inputs']['amount']['type']['dimensions']={};refusal('event-units',c,'event_type_mismatch')
    c=deepcopy(valid);c['registry']['entries']['authored']['transition_profile']=r.frontend.v2.PROFILE
    c['registry']['entries']['authored']['memory_definition']={};refusal('source-transition-mismatch',repin(c),'source_transition_correspondence')
    sale_book,sale_call=examples['sale.alpha'];c=deepcopy(sale_call);c['registry']['entries']['authored'].pop('memory_definition')
    actual=r.propose(sale_book,repin(c));assert actual['status']=='invalid' and 'fields' in actual['reason']
    failures.append({'case':'missing-v2-definition','status':actual['status'],'reason':actual['reason']})
    bad=r.propose(book,valid);bad['transition']['after']['balances'][book['cash_account']]='999/1'
    assert r.apply(book,valid,bad)['status']=='invalid'
    good=r.propose(book,valid);after=good['transition']['after'];c=call(after,valid['registry']['entries'],'authored',valid['event'])
    assert r.propose(after,c)['reason']=='duplicate_event'
    # Reuse the retained lifecycle as the independent sequential baseline.
    path=ROOT/'data/accounting-master/declared-collection-state-growth-20261025/examples.py'
    spec=importlib.util.spec_from_file_location('registry_lifecycle_examples',path);fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)
    import declared_receivable_lifecycle_v1 as life
    sequence=[];projections=[]
    for owner in ['alpha','beta']:
        body,mapping,_=fixtures.lifecycle_fixture(owner);current=deepcopy(body['opening']);entries={}
        for i,command in enumerate(body['commands'][:2]):
            q=life.make_request(current,body,command);native=r.frontend.v2.propose(current,q);assert native['status']=='proposed'
            if i==1:q.pop('memory_definition');q['profile']=r.base.PROFILE;q['expected_method_sha256']=r.digest(q['method'])
            # The old adapter embeds identity/due/customer in generated methods.
            # Record its exact projection; do not allow undeclared registry inputs.
            declared=r.prior.event_declarations(q['method'])
            removed={k:deepcopy(v) for k,v in q['event']['inputs'].items() if k not in declared}
            projections.append({'company':owner,'step':i,'removed_event_inputs':removed,
                'reason':'Retained lifecycle builder specializes these values into method data before transition'})
            q['event']['inputs']={k:v for k,v in q['event']['inputs'].items() if k in declared}
            source=r.frontend.render(q['method'],q['profile'],environment(current,q));e=entry(current,q,source)
            entries[command['method_key']]=e;c=call(current,entries,command['method_key'],q['event'])
            actual=r.propose(current,c);assert actual['status']=='proposed',actual
            assert actual['materialized_request']==q
            assert actual['transition']==r.frontend.ENGINES[q['profile']].propose(current,q)
            assert actual['transition']['after']==native['after'] and actual['transition']['journal']==native['journal'] and actual['transition']['flows']==native['flows']
            assert r.apply(current,c,actual)['status']=='applied_provisional'
            current=actual['transition']['after'];dump(out/(owner+'.sequence.'+str(i)+'.json'),{'call':c,'result':actual})
        assert current['balances'][mapping['cash']]=='110/1' and current['balances'][mapping['receivables']]=='20/1'
        assert current['memory']['claims']['invoice/a~1']['remaining']=='20/1'
        sequence.append({'company':owner,'steps':2,'selected_versions':['CompanyBookTransition/2','CompanyBookTransition/1'],
            'full_native_states_equal':True,'cash':'110/1','receivables':'20/1','claim_remaining':'20/1'})
    for p,h in lock.items():assert sha(ROOT/p)==h,p
    checks={'passed':True,'full_method_comparisons':len(rows),'refusals':len(failures),'economic_outcomes':len(economic),
        'mixed_version_sequences':len(sequence),'unselected_entries_checked':True,'duplicate_event_refused':True,
        'proposal_tampering_refused':True,'protected_files':len(lock),'admission':False}
    for name,value in [('checks.json',checks),('comparisons.json',rows),('refusals.json',failures),('economic-outcomes.json',economic),('sequences.json',sequence),('event-projections.json',projections)]:dump(HERE/name,value)
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/authored-method-registry-20261026/verify.py',
        'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic',
        'wall_seconds':time.monotonic()-started,'data_version':sha(lock_path),'plan_file':'docs/plans/accounting-authored-method-registry-20261026.md',
        'result_file':str((HERE/'result.md').relative_to(ROOT)),'artifact_paths':['checks.json','comparisons.json','refusals.json','sequences.json','examples/'],
        'implementation_sha256':sha(HERE/'registry.py'),'verifier_sha256':sha(Path(__file__)),'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(checks))
if __name__=='__main__':main()
