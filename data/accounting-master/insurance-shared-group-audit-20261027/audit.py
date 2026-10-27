"""Bounded read-only call-chain and existing-case diagnostic."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,os,platform,subprocess,sys,time
H=Path(__file__).resolve().parent;R=H.parents[2]
def digest(p):return sha256(p.read_bytes()).hexdigest()
def main():
    started=time.monotonic();assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    attempt=sys.argv[1];assert attempt in ['01','02','03']
    out=H/('attempt-'+attempt);out.mkdir(exist_ok=False)
    def save(n,v):(out/n).write_text(json.dumps(v,indent=2)+'\n')
    checks=[];cases=[];refusals=[]
    def ck(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
    sys.path.insert(0,str(R/'scripts'))
    import insurance_loss_book_v1 as loss
    import insurance_fiscal_book_v1 as fiscal
    import declared_indirect_cash_v2 as bridge
    p=H.parent/'insurance-service-finance-origins-20261016'
    rows=json.loads((p/'attempt-02/exchanges.json').read_text())
    expected=json.loads((p/'authored-cases-v2.json').read_text())['cases']
    sourcepaths=[p/'reference.py',p/'authored-cases-v2.json',p/'attempt-02/exchanges.json',p/'input-lock-v2.json',
        R/'scripts/insurance_loss_book_v1.py',R/'scripts/insurance_fiscal_book_v1.py',
        R/'scripts/declared_indirect_cash_v2.py',R/'scripts/declared_company_program_v2.py',
        H.parent/'insurance-statement-bridge-20261025/examples.py',
        H.parent/'insurance-identity-adoption-20261026/checks.json',
        H.parent/'insurance-identity-adoption-20261026/protocol-delta.json',
        H.parent/'insurance-treaty-changes-20261015/cases.json',
        H/'audit-note.md',H/'audit.py',R/'docs/plans/accounting-insurance-shared-group-audit-20261027.md']
    for f in json.loads((p/'input-lock-v2.json').read_text())['files']:
        path=R/f['path'];ck('native_lock:'+f['path'],digest(path)==f['sha256']);sourcepaths.append(path)
    locked={str(p.relative_to(R)):digest(p) for p in sourcepaths}
    save('source-lock.json',locked)
    try:
        ck('fiscal_calls_loss',fiscal.base is loss)
        ck('two_supported_loss_cases',loss.CASES==('loss-service-finance','zero-loss-boundary'))
        for ident in loss.CASES:
            chosen=loss.native_case(ident)
            ck('supported_endpoint:'+ident,chosen['request']['operation']=='loss_schedule')
        for ident in ['recovery-change-once','covered-loss-exhausted']:
            original=next(x for x in rows if x['id']==ident)
            target=next(x for x in expected if x['id']==ident)
            req=deepcopy(original['request']);result=loss.native_result(req)
            ck(ident+':exact_native_replay',result==original['result'])
            ck(ident+':request_unchanged',req==original['request']==target['request'])
            ck(ident+':no_effect',result['posts'] is False and result['mutations']==[])
            def subset(e,a,path):
                if isinstance(e,dict):
                    for k,v in e.items():subset(v,a[k],path+'/'+k)
                else:ck(ident+':authored'+path,e==a)
            subset(target['expected'],result['report'],'')
            ck(ident+':no_component_double_expense',result['report']['change']['additional_component_expense']=='0')
            try:
                loss.native_case(ident)
            except loss.core.Invalid as exc:
                refusal={'case_id':ident,'status':'invalid_selection','reason':str(exc)}
            else:raise AssertionError('unsupported recovery unexpectedly selected')
            ck(ident+':loss_adapter_refusal',refusal['reason']=='supported_native_case')
            refusals.append(refusal);cases.append({'case_id':ident,'request':req,'result':result})
        folder=H.parent/'insurance-statement-bridge-20261025'
        evidence=json.loads((folder/'evidence.json').read_text());observed=set();selected=[]
        for entry in evidence['cases']:
            path=R/entry['path'];ck('statement_file:'+entry['name'],digest(path)==entry['sha256'])
            locked[entry['path']]=entry['sha256'];case=json.loads(path.read_text())
            observed.add(entry['name'].split('.')[1]);ck('statement_no_admission:'+entry['name'],case['result']['status']=='explained_provisional')
            if entry['name'] in ['named.loss-service-finance.split.2027','numbered.zero-loss-boundary.all_noncash.2027']:
                actual=bridge.report(case['request']);ck('report_endpoint:'+entry['name'],actual==case['result'])
                selected.append(entry['name'])
        ck('actual_statement_population',observed==set(loss.CASES))
        ck('complete_statement_count',len(evidence['cases'])==24)
        ck('selected_actual_report_calls',len(selected)==2)
        identity=json.loads((H.parent/'insurance-identity-adoption-20261026/checks.json').read_text())
        ck('identity_profile_distinct',identity['financial_profile']=='InsuranceComponents/1')
        ck('identity_native_population',identity['native_cases']==43 and identity['passed'])
        for n,h in locked.items():ck('preserved:'+n,digest(R/n)==h)
        save('source-lock.json',locked);save('native-replays.json',cases);save('adapter-refusals.json',refusals)
        save('verification.json',{'status':'PASS_SCOPED_AUDIT','checks':len(checks),'results':checks,
             'recovery_native_cases':2,'loss_supported_cases':2,'statement_records':24,'actual_report_calls':selected,
             'protected_files':len(locked),'gap':'recovery_change is not admitted by the existing loss/fiscal book adapter',
             'financial_method_added':False,'readiness':'not_ready'})
    except Exception as exc:
        save('failure.json',{'type':type(exc).__name__,'reason':str(exc),'checks':checks});raise
    finally:
        save('run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
             'command':'env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 data/accounting-master/insurance-shared-group-audit-20261027/audit.py '+attempt,
             'environment':{'python':platform.python_version(),'executable':sys.executable},
             'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic',
             'wall_seconds':round(time.monotonic()-started,3),'data_version':'source-lock.json',
             'plan':'docs/plans/accounting-insurance-shared-group-audit-20261027.md',
             'result':'data/accounting-master/insurance-shared-group-audit-20261027/result.md',
             'artifacts':{p.name:digest(p) for p in out.iterdir() if p.is_file()}})
    print(json.dumps({k:v for k,v in json.loads((out/'verification.json').read_text()).items() if k!='results'}))
if __name__=='__main__':main()
