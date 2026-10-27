"""Independent scope routes, exact bindings, adverse controls and retained results."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,os,platform,resource,subprocess,sys,time,traceback
import scope as m
H=Path(__file__).resolve().parent;R=H.parents[2];h=m.history
spec=importlib.util.spec_from_file_location('group_examples',R/'data/accounting-master/group-period-report-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
START='2025-01-01T00:00:00Z';END='2026-01-01T00:00:00Z'

def add(b,name,a,z,status,available=None,parent=None):
    request=b['history_request'];source='Synthetic interval premise: '+name
    sid=h.source_digest(source);request['sources'][sid]=source
    record=dict(profile=h.RECORD,subject=['P','S'],basis='conditional_group_design',start=a,end_exclusive=z,status=status,coverage='asserted_whole_interval',evidence_sha256=sid,available_at=available if available is not None else {'manager':'2024-12-31T00:00:00Z','analyst':'2024-12-31T00:00:00Z'},supersedes=parent)
    rid=h.digest(record);request['records'][rid]=record;return rid

def bind(b):
    b['expected_history_sha256']=h.digest(b['history_request'])
    b['expected_group_sha256']=h.digest(b['group_request'])
    return b

def fixture(cells):
    g=ex.fixture()
    b=dict(profile=m.PROFILE,history_request=dict(profile=h.PROFILE,subject=['P','S'],basis='conditional_group_design',interval=dict(start=START,end_exclusive=END),actor='manager',cutoff='2026-01-02T00:00:00Z',records={},sources={}),group_request=g,expected_history_sha256='',expected_group_sha256='',calendar_offset='Z',basis_bridge=dict(history_basis='conditional_group_design',group_measurement_basis=g['opening']['compatibility']['measurement_basis'],premise='Supplied synthetic correspondence; no authority or measurement assessment'))
    bounds={1:[START,END],2:[START,'2025-07-01T00:00:00Z',END],3:[START,'2025-05-01T00:00:00Z','2025-09-01T00:00:00Z',END]}[len(cells)]
    for i,status in enumerate(cells):
        if status is not None:add(b,'cell'+str(i),bounds[i],bounds[i+1],status)
    return bind(b)

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(100,100))
    out=H/sys.argv[1];out.mkdir(exist_ok=False);start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    checks=[];cases=[];controls=[]
    files={Path(__file__),H/'scope.py',H/'expected-routes.json',H/'contract.md',R/'docs/plans/accounting-control-group-boundary-20261027.md'}
    files.update(p for p in (H/'baseline-attempt-01').iterdir() if p.is_file())
    files.update(R/p for p in m.PINS)
    files.update(Path(module.__file__) for module in list(sys.modules.values()) if getattr(module,'__file__',None) and str(getattr(module,'__file__')).startswith(str(R)) and Path(module.__file__).is_file())
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:
        q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    def ck(name,actual,expected=True):
        checks.append(dict(name=name,passed=actual==expected))
        if actual!=expected:raise AssertionError(name+': '+repr(actual)[:250]+' != '+repr(expected)[:250])
    def run(name,b,route,methods=None):
        before=deepcopy(b);result=m.scope(b)
        ck(name+'/status',result['status'],'scope_assessed');ck(name+'/input',b,before)
        ck(name+'/route',result['route'],route)
        if methods is not None:ck(name+'/methods',result['required_methods'],methods)
        ck(name+'/complete_history',result['history'],h.evaluate(b['history_request']))
        ck(name+'/no_permission',[result[k] for k in m.FLAGS],[False]*len(m.FLAGS))
        ck(name+'/no_report','legal_reports' not in result and 'cash_flows' not in result)
        ck(name+'/bindings',[result['history_request_sha256'],result['group_request_sha256']],[h.digest(b['history_request']),h.digest(b['group_request'])])
        ck(name+'/bridge',result['basis_bridge'],b['basis_bridge'])
        cases.append(dict(id=name,request=b,result=result));return result
    def reject(name,b,reason):
        before=deepcopy(b);result=m.scope(b)
        ck(name+'/status',result['status'],'invalid');ck(name+'/reason',result['reason'],reason)
        ck(name+'/input',b,before);ck(name+'/no_permission',[result[k] for k in m.FLAGS],[False]*len(m.FLAGS))
        controls.append(dict(id=name,request=b,result=result))
    try:
        for row in json.loads((H/'expected-routes.json').read_text()):run(row['id'],fixture(row['cells']),row['route'],row['methods'])
        for fraction in ['3/4','0/1']:
            b=fixture(['yes'])
            for side in ['opening','closing']:b['group_request'][side]['world']['control_edges'][0]['ownership_fraction']=fraction
            run('partial-ownership/'+fraction,bind(b),'nci_methods_required',['ownership_and_nci_method'])
        b=fixture(['yes']);add(b,'conflict',START,END,'no');run('conflicting-evidence',bind(b),'unresolved_history')
        b=fixture(['yes']);parent=next(iter(b['history_request']['records']))
        add(b,'correction',START,END,'no',{'manager':'2026-02-01T00:00:00Z','analyst':'2026-01-01T00:00:00Z'},parent)
        run('manager-before-correction',bind(deepcopy(b)),'stable_scope_candidate')
        b['history_request']['actor']='analyst';run('analyst-after-correction',bind(deepcopy(b)),'outside_controlled_group')
        b['history_request']['actor']='manager';b['history_request']['cutoff']='2026-02-01T00:00:00Z'
        run('manager-after-correction',bind(b),'outside_controlled_group')
        b=fixture(['yes']);parent=next(iter(b['history_request']['records']))
        add(b,'unknown-availability',START,END,'no',{'manager':None},parent)
        run('unknown-correction',bind(b),'unresolved_history')
        b=fixture(['yes']);b['history_request']['interval']=dict(start='2025-01-01T08:00:00+08:00',end_exclusive='2026-01-01T08:00:00+08:00')
        run('equivalent-offset-query',bind(b),'stable_scope_candidate')
        b=fixture([None]);b['calendar_offset']='+08:00'
        b['history_request']['interval']=dict(start='2025-01-01T00:00:00+08:00',end_exclusive='2026-01-01T00:00:00+08:00')
        add(b,'local-calendar','2025-01-01T00:00:00+08:00','2026-01-01T00:00:00+08:00','yes')
        run('explicit-local-calendar',bind(b),'stable_scope_candidate')
        b=fixture(['yes']);b['group_request']['internal_cash_pairs']=[]
        run('scope-does-not-assert-elimination-completeness',bind(b),'stable_scope_candidate')
        b=fixture(['yes']);b['group_request']['legal_reports']={}
        run('scope-does-not-authorize-incomplete-report',bind(b),'stable_scope_candidate')
        ck('incomplete_report_refuses',m.group.report(b['group_request'])['status'],'invalid')
        b=fixture(['yes']);b['history_request']['cutoff']='2026-01-03T00:00:00Z';reject('stale-history',b,'history_binding')
        b=fixture(['yes']);b['group_request']['internal_cash_pairs']=[];reject('stale-group',b,'group_binding')
        b=fixture(['yes']);b['calendar_offset']='-00:00';reject('unknown-offset',b,'unknown_negative_zero_offset')
        b=fixture(['yes']);b['calendar_offset']='+08:00';reject('offset-mismatch',b,'calendar_interval_binding:start')
        b=fixture(['yes']);b['history_request']['interval']['start']='2025-01-01T00:00:00.1Z';reject('subday-rounding',bind(b),'calendar_interval_binding:start')
        b=fixture(['yes']);b['history_request']['subject']=['S','P'];reject('reversed-subject',bind(b),'history_subject_binding')
        b=fixture(['yes']);b['basis_bridge']['history_basis']='other';reject('history-basis',b,'history_basis_binding')
        b=fixture(['yes']);b['basis_bridge']['group_measurement_basis']='other';reject('group-basis',b,'group_basis_binding')
        b=fixture(['yes']);b['basis_bridge']['premise']='';reject('missing-basis-premise',b,'text_required')
        b=fixture(['yes']);b['group_request']['closing']['world']['control_edges'][0]['start']='2025-02-01';reject('changed-report-edge',bind(b),'period_control_edge_changed')
        b=fixture(['yes'])
        for side in ['opening','closing']:b['group_request'][side]['world']['control_edges'][0]['end_exclusive']='2025-12-31'
        reject('edge-omits-last-day',bind(b),'edge_interval_coverage')
        b=fixture(['yes']);b['group_request']['closing']['books']['S']['period']['end_exclusive']='2027-01-01';reject('mixed-periods',bind(b),'period_binding')
        b=fixture(['yes']);rid=next(iter(b['history_request']['records']));b['history_request']['records'][rid]['status']='no';reject('record-tampering',bind(b),'record_identity')
        b=fixture(['yes']);sid=next(iter(b['history_request']['sources']));b['history_request']['sources'][sid]='changed';reject('source-tampering',bind(b),'source_identity')
        b=fixture(['yes']);b['unexpected']=1;reject('open-schema',b,'scope_fields')
        for filename,expected in [('unchanged','period_reported'),('changed-control','invalid'),('partial-ownership','invalid')]:
            prior=json.loads((H/'baseline-attempt-01'/(filename+'.json')).read_text())
            result=m.group.report(prior['request']);ck('baseline-complete/'+filename,result,prior['result']);ck('baseline-status/'+filename,result['status'],expected)
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,report_authorized=False)
    except Exception:
        result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for name,obj in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]:
        (out/name).write_text(json.dumps(obj,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU devices intentionally hidden',random_seeds='N/A deterministic',started_utc=started,wall_seconds=time.monotonic()-start,data_version='source-lock.json',plan='docs/plans/accounting-control-group-boundary-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
