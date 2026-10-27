from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import importlib.util,json,sys,time,subprocess
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
GUARD=HERE.parent/'authored-state-invariants-20261026'
sys.path.insert(0,str(GUARD));import guards as g;import guarded_runner as runner
spec=importlib.util.spec_from_file_location('event_audit_helpers',GUARD/'verify.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+NL)
def main():
    started=time.monotonic();out=HERE/'examples';out.mkdir(exist_ok=True);rows=[];lost=[]
    lock_path=HERE/'source-lock.json'
    if not lock_path.exists():
        lock=json.loads((GUARD/'source-lock.json').read_text())
        for p in [GUARD/'guards.py',GUARD/'guarded_runner.py',GUARD/'verify.py',GUARD/'checks.json',GUARD/'result.md']:
            lock[str(p.relative_to(ROOT))]=sha(p)
        dump(lock_path,lock)
    lock=json.loads(lock_path.read_text())
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    for owner in ['alpha','beta']:
        body,native,source,mapping,projections=helper.helpers.build(owner)
        guarded=helper.wrap(body,mapping['receivables'])
        # After a January assessment, the cursor is February 1, while date is January 31.
        # Repeat collection on that date: ordinary chronology permits it, sealed-window policy does not.
        original=deepcopy(source);command=deepcopy(source['commands'][1]);command['event'].update(id='late.same.day',date='2027-01-31')
        original['commands']=original['commands'][:3]+[command]
        refused=helper.helpers.life.run(original)
        assert refused['status']=='stopped_provisional' and refused['stop']['reason']=='assessment_day_sealed'
        changed=deepcopy(guarded);derived=deepcopy(changed['commands'][1]);derived['event'].update(id='late.same.day',date='2027-01-31')
        changed['commands']=changed['commands'][:3]+[derived]
        actual=runner.run(changed);stop=actual.get('stop') or {}
        assert actual['status']=='complete_provisional',(owner,actual['status'],stop.get('reason',actual.get('reason')))
        rows.append({'company':owner,'case':'sealed-window','native':'assessment_day_sealed','authored':'complete_provisional','gap_confirmed':True})
        dump(out/(owner+'.sealed-window.json'),{'native_program':original,'authored_program':changed,'native_result':refused,'authored_result':actual})
        # Alter only an unused assessment input. The selected method still carries
        # the original hardcoded cursor/snapshot updates, so event intent is lost.
        original=deepcopy(source);original['commands']=original['commands'][:3]
        original['commands'][2]['event']['inputs']['start']['value']=g.base.known('2027-01-02')
        refused=helper.helpers.life.run(original)
        assert refused['status']=='stopped_provisional' and refused['stop']['reason']=='assessment_cursor'
        changed=deepcopy(guarded);changed['commands']=changed['commands'][:3]
        actual=runner.run(changed);assert actual['status']=='complete_provisional'
        rows.append({'company':owner,'case':'assessment-intent-projection','native':'assessment_cursor','authored':'no_start_input',
            'gap_confirmed':True,'comparison_scope':'Information was projected out; not identical input contracts'})
        # Customer intent is similarly omitted by specialized collection methods.
        original=deepcopy(source);original['commands']=original['commands'][:2]
        original['commands'][1]['event']['inputs']['customer']['value']=g.base.known('Different customer')
        refused=helper.helpers.life.run(original)
        assert refused['status']=='stopped_provisional' and refused['stop']['reason']=='claim_customer_mismatch'
        projection=next(row for row in projections if row['index']==1)
        assert 'customer' in projection['removed_event_inputs'] and 'claim_id' in projection['removed_event_inputs']
        lost.append({'company':owner,'customer_mismatch_refused_natively':True,'removed_collection_fields':list(projection['removed_event_inputs']),
            'assessment_removed_fields':list(next(row for row in projections if row['index']==2)['removed_event_inputs']),
            'required_repair':'Retain original event intent separately and bind the selected specialization to it'})
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    checks={'passed':True,'companies':2,'sealed_window_counterexamples':2,'intent_loss_cases':4,
        'guarded_state_controls_still_pass':True,'complete_lifecycle_contract':False,'protected_files':len(lock)}
    dump(HERE/'checks.json',checks);dump(HERE/'comparisons.json',rows);dump(HERE/'intent-loss.json',lost)
    dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/authored-event-prerequisite-audit-20261026/probe.py',
        'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-started,
        'data_version':sha(lock_path),'plan_file':'docs/plans/accounting-authored-event-prerequisite-audit-20261026.md',
        'result_file':str((HERE/'result.md').relative_to(ROOT)),'artifact_paths':['checks.json','comparisons.json','intent-loss.json','examples/'],
        'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(checks))
if __name__=='__main__':main()
