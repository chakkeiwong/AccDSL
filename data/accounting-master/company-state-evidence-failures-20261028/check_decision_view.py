"""Verify complete audit preservation and detached conflict-aware decision views."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
import decision_view as adapter
ROOT=adapter.ROOT;HERE=Path(__file__).resolve().parent
PLAN='docs/plans/company-state-conflict-aware-decision-view-20261028.md'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
 out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 baseline=json.loads((HERE/'attempt-02/cases.json').read_text());checks=[];results=[]
 def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
 for c in baseline:
  body=c['input'];before=deepcopy(body);r=adapter.build(body['base'],body['sources'],body['query']);label=c['id']
  ck(label+'/wrapper status',r['status'],'complete_conditional');ck(label+'/whole native outcome',r['audit_result'],c['result'])
  ck(label+'/input unchanged',body,before)
  view=r['decision_view'];status=c['result']['status']
  ck(label+'/outcome carried',view['outcome'],adapter.STATUSES[status])
  ck(label+'/conditional support',view['conditional_inputs_supported'],status=='selected_conditional_inputs')
  for f in ['source_admission','actual_actor_knowledge','forecast_admission','production_execution_authorized']:ck(label+'/'+f,view[f],False)
  ck(label+'/no probability',view['probability_model'],None)
  expected=c['result'].get('policy_evidence',{}).get('assertions',[])
  ck(label+'/observable assertions retained',view['assertions'],expected)
  ck(label+'/no clocks or ingestion metadata',all(set(x)==set(adapter.FIELDS) for x in view['assertions']),True)
  ck(label+'/detached status available','outcome' in json.loads(json.dumps(view)),True)
  results.append(dict(id=label,output=r))
 by={r['id']:r['output']['decision_view'] for r in results}
 for amount in ['4/1','7/1']:ck('whole decision view future invariance '+amount,by['changed future amount '+amount],by['before correction'])
 for label in ['correction with unlinked alias','outside complete domain','conflicting provider interpretation']:
  ck(label+'/conflict visible',by[label]['outcome'],'conflict')
  ck(label+'/unexecutable',by[label]['conditional_inputs_supported'],False)
  ck(label+'/observable conflict not censored',bool(by[label]['assertions']),True)
 # Explicitly show why an old child projection alone was not enough.
 old=next(c['result'] for c in baseline if c['id']=='outside complete domain')
 ck('old detached projection had no outcome','outcome' in old['policy_evidence'],False)
 mutations=[]
 x=deepcopy(old);x['policy_evidence']['assertions']=[];mutations.append(('removed assertions',x))
 x=deepcopy(old);x['policy_evidence']['assertions'][0]['ingested']={'earliest':220,'latest':220};mutations.append(('extra clock metadata',x))
 x=deepcopy(old);x['policy_evidence']['view']['cutoff']=999;mutations.append(('wrong cutoff',x))
 x=deepcopy(old);x.pop('status');mutations.append(('missing status',x))
 x=deepcopy(old);x['policy_evidence']['source_admission']=True;mutations.append(('forged admission',x))
 x=deepcopy(old);x['policy_evidence']['assertions'][0]['interval']['lower']='0/1';mutations.append(('forged assertion',x))
 refused=[]
 for label,x in mutations:
  try:adapter._project(x);reason=None
  except (ValueError,KeyError,TypeError) as exc:reason=str(exc)
  ck(label+'/projection refused',reason is not None,True);refused.append(dict(id=label,reason=reason))
 pins=json.loads((HERE/'decision-view-source-lock.json').read_text())
 for path,h in pins.items():ck('pinned/'+path,sha256((ROOT/path).read_bytes()).hexdigest(),h)
 failures=[c['name'] for c in checks if not c['passed']]
 result=dict(status='fail' if failures else 'pass',checks=len(checks),complete_native_cases=len(results),refusal_controls=len(refused),failures=failures)
 dump(out/'checks.json',checks);dump(out/'results.json',results);dump(out/'refusals.json',refused);dump(out/'verification.json',result)
 sources=[Path(__file__),Path(adapter.__file__),HERE/'attempt-02/cases.json',HERE/'decision-view-source-lock.json',ROOT/PLAN]
 dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command='python3 -B '+str(Path(__file__).relative_to(ROOT))+' --output '+str(out.relative_to(ROOT)),
 environment=sys.version,cpu_gpu='CPU-only standard-library; no GPU import or detection',random_seeds='N/A deterministic',data_version='22 retained exact conditional source outcomes',
 utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources},
 pinned_native_dependencies=pins,plan=PLAN,result=str(out.relative_to(ROOT))))
 print(json.dumps(result));return bool(failures)
if __name__=='__main__':raise SystemExit(main())

