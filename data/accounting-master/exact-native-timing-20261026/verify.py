from copy import deepcopy
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys,time
from checker import *

def dump(path,value):path.write_text(json.dumps(value,indent=2)+chr(10))
def sha(path):return sha256(path.read_bytes()).hexdigest()
def outcome(a,root,view):
    try:a.information(root,view);return 'accepted'
    except native.Refusal as exc:return exc.code

def main():
    start=time.monotonic();old=native.Auditor(ATT);new=Auditor(ATT)
    lock_path=HERE/'source-lock.json'
    files=[ATT/'portable-exchanges.json',ATT/'record-schemas.json',ATT/'inputs/verify_exchanges.py',
       ATT/'inputs/financial_checks.py',ATT/'inputs/source_policy.py',EXACT/'projection.py',EXACT/'checks.json',
       ROOT/'docs/plans/accounting-exact-native-timing-20261026.md']
    if not lock_path.exists():dump(lock_path,{str(p.relative_to(ROOT)):sha(p) for p in files})
    lock=json.loads(lock_path.read_text())
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    selected=[e for e in old.packet['exchanges'] if old.body(e['request_ref'])['operation']=='bank.regulatory.assess@1']
    for ex in selected:old.response(ex);new.response(ex)
    ex=next(e for e in selected if e['id']=='capital.final')
    basis=old.body(old.body(ex['request_ref'])['arguments']['value']['basis_ref'])
    average=old.record(basis['average_ref']);view0=old.record(basis['view_ref'])
    evidence0=old.record(view0['body']['evidence_refs'][0])
    base={'available_at':'2026-04-01T00:00:00.0000001Z','ingested_at':'2026-04-01T00:00:00.0000001Z',
          'measurement_asof':'2026-04-01','decision_at':'2026-04-01T00:00:00.0000001Z',
          'system_asof':'2026-04-01T00:00:00.0000001Z','include':True}
    cases=[('equal',{},'accepted','accepted'),
      ('later-availability',{'available_at':'2026-04-01T00:00:00.0000002Z'},'later_information','accepted'),
      ('later-ingestion',{'ingested_at':'2026-04-01T00:00:00.0000002Z'},'later_ingestion','accepted'),
      ('absent-membership',{'include':False},'evidence_not_in_view','evidence_not_in_view'),
      ('future-measurement',{'measurement_asof':'2026-04-02'},'future_measurement','future_measurement'),
      ('equivalent-offset',{'available_at':'2026-04-01T01:00:00.0000001+01:00'},'accepted','accepted'),
      ('utc-day-boundary',{'available_at':'2026-03-31T22:00:00Z','ingested_at':'2026-03-31T22:00:00Z',
       'decision_at':'2026-04-01T00:00:00+02:00','system_asof':'2026-04-01T00:00:00+02:00'},'future_measurement','future_measurement'),
      ('utc-day-valid',{'available_at':'2026-03-31T22:00:00Z','ingested_at':'2026-03-31T22:00:00Z',
       'decision_at':'2026-04-01T00:00:00+02:00','system_asof':'2026-04-01T00:00:00+02:00','measurement_asof':'2026-03-31'},'accepted','accepted'),
      ('precision-refusal',{'available_at':'2026-04-01T00:00:00.0000001000000000001Z'},'exact_time_unsupported:fraction_precision_limit','accepted'),
      ('unknown-offset',{'available_at':'2026-04-01T00:00:00.0000001-00:00'},'exact_time_unsupported:unknown_negative_zero_offset','accepted')]
    rows=[];retained=[]
    def add(record):
        record['dependencies']=native.unique(native.references(record['body']))
        digest=native.sha(('accdsl.portable.v1/'+record['schema']).encode()+bytes([0])+native.enc(record))
        ref={'kind':record['kind'],'schema':record['schema'],'digest':digest}
        old.reg[digest]=record;new.reg[digest]=record
        old.shape(record,digest);new.shape(record,digest)
        return ref
    for name,changes,expected,expected_old in cases:
        data={**base,**changes};e=deepcopy(evidence0);e['key']='derived.exact-time.'+name
        e['body'].update({k:data[k] for k in ['available_at','ingested_at','measurement_asof']})
        er=add(e);v=deepcopy(view0);v['key']='derived.exact-time-view.'+name
        # Keep one existing evidence member so the native nonempty schema still holds.
        v['body'].update(decision_at=data['decision_at'],system_asof=data['system_asof'],
            evidence_refs=[er] if data['include'] else view0['body']['evidence_refs'])
        vr=add(v);root=deepcopy(average);root['key']='derived.exact-time-root.'+name
        root['body']['evidence_ref']=er;rr=add(root)
        actual,prior=outcome(new,rr,vr),outcome(old,rr,vr)
        assert (actual,prior)==(expected,expected_old),(name,actual,prior)
        rows.append({'case':name,'successor':actual,'original':prior,'root_ref':rr,'view_ref':vr,'evidence_ref':er})
        retained.append({'case':name,'records':[root,v,e],'evidence_mode':'derived_information_submethod_only'})
    # A superseded evidence record remains checked through immutable dependencies.
    later=deepcopy(evidence0);later['key']='derived.superseded-later'
    later['body'].update(available_at='2026-04-01T00:00:00.0000002Z',ingested_at=base['ingested_at'])
    lr=add(later)
    vintage0=next(r for r in old.reg.values() if r['kind']=='Vintage')
    prior_average=deepcopy(vintage0);prior_average['key']='derived.prior-vintage';prior_average['body']['evidence_ref']=lr
    prior_average['body']['supersedes_ref']=None
    pr=add(prior_average)
    root=deepcopy(vintage0);root['key']='derived.current-vintage';root['body']['supersedes_ref']=pr
    root['body']['evidence_ref']=view0['body']['evidence_refs'][0]
    rr=add(root)
    v=deepcopy(view0);v['key']='derived.supersession-view';v['body'].update(decision_at=base['decision_at'],system_asof=base['system_asof'],evidence_refs=native.unique([lr,*view0['body']['evidence_refs']]))
    vr=add(v);actual=outcome(new,rr,vr);prior=outcome(old,rr,vr)
    assert actual=='later_information' and prior=='accepted',(actual,prior)
    rows.append({'case':'superseded-evidence-still-checked','successor':actual,'original':prior,'root_ref':rr,'view_ref':vr})
    retained.append({'case':'superseded-evidence-still-checked','records':[root,v,prior_average,later],'evidence_mode':'derived_information_submethod_only'})
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    checks={'passed':True,'retained_regulatory_responses':len(selected),'derived_information_cases':len(rows),
         'changed_expected_results':sum(r['successor']!=r['original'] for r in rows),'protected_files':len(lock),
         'native_profile_modified':False,'source_admission':False,'accounting_admission':False,'executed':False}
    dump(HERE/'checks.json',checks);dump(HERE/'comparisons.json',rows);dump(HERE/'derived-records.json',retained)
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
       'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/exact-native-timing-20261026/verify.py',
       'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic',
       'wall_seconds':time.monotonic()-start,'data_version':sha(ATT/'portable-exchanges.json'),
       'plan_file':'docs/plans/accounting-exact-native-timing-20261026.md','result_file':str((HERE/'result.md').relative_to(ROOT)),
       'artifact_paths':['checks.json','comparisons.json','derived-records.json'],
       'implementation_sha256':sha(HERE/'checker.py'),'verifier_sha256':sha(Path(__file__)),
       'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(checks))

if __name__=='__main__':main()
