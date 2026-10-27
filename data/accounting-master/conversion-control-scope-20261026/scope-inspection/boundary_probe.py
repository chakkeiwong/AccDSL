"""One-shot diagnostic on a frozen live-evaluator snapshot."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json, os, subprocess, sys, time
H=Path(__file__).resolve().parent
ROOT=H.parents[3]

def main():
 start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
 assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
 out=H/'boundary-attempt-01';out.mkdir(exist_ok=False)
 source=(H.parent/'dependencies.py').read_bytes()
 snap=out/'dependencies-snapshot.py';snap.write_bytes(source)
 spec=importlib.util.spec_from_file_location('dependency_boundary_snapshot',snap)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 def assessment(value,at):
  return dict(status=value,evidence=[] if value=='unknown' else ['synthetic:boundary-case'],subject=['holder','issuer'],as_of=at)
 def control(at,power):
  return dict(as_of=at,elements={k:assessment(power if k=='power' else 'yes',at) for k in m.CONTROL},reviews={k:assessment('yes',at) for k in m.REVIEWS})
 base=dict(profile=m.PROFILE,context=dict(holder='holder',issuer='issuer',basis='conditional_AASB_design',period_start='2028-01-01'),conversion_date='2028-01-01',votes=dict(received=120,total=160),control_before=control('2027-12-31','no'),control_after=control('2028-01-01','yes'),report='consolidated',assessments={k:assessment('yes' if k=='business' else 'no','2028-01-01') for k in m.GENERAL},separate_policy='unknown',measurements={},authority=dict(status='unresolved',evidence=[],period_start='2028-01-01',basis='conditional_AASB_design'))
 cases=[]
 def run(name,body,predicate,criterion):
  original=deepcopy(body)
  try:result=m.evaluate(body);error=None
  except Exception as exc:result=None;error=type(exc).__name__+': '+str(exc)
  cases.append(dict(id=name,input=original,output=result,error=error,criterion=criterion,pass_check=predicate(result,error)))
  assert body==original,'input mutation'
 run('known_gain',deepcopy(base),lambda r,e:e is None and r['routes']==['consolidation_scope','business_combination'] and not r['accounting_admission'],'Supplied gain lists combination dependencies without admission.')
 b=deepcopy(base);b['control_before']=control('2027-12-31','yes')
 run('continued_control',b,lambda r,e:e is None and 'continued_control_conversion' in r['routes'],'Prior and later control preserve continued-control route.')
 b=deepcopy(base);b['control_before']=control('2027-12-31','unknown')
 run('unknown_prior_control',b,lambda r,e:e is None and 'business_combination' not in r['routes'] and any('timing' in x or 'prior' in x or 'history' in x for x in r['routes']),'Unknown prior control must preserve continued-control versus acquisition alternatives.')
 b=deepcopy(base);b['control_before']=control('2027-12-31','yes');b['control_after']=control('2028-01-01','no')
 run('loss_of_control',b,lambda r,e:e is None and 'loss' in r['timing'] and any('loss' in x for x in r['missing']+r['routes']),'Loss must retain loss-of-control dependencies and accurate timing.')
 b=deepcopy(base);b['control_after']=control('2028-01-01','unknown')
 run('unknown_after_75_percent',b,lambda r,e:e is None and r['routes']==['control_unresolved'] and not r['posting_authorized'],'75% does not replace control assessment.')
 b=deepcopy(base);b['control_after']['elements']['power']['evidence']=[]
 run('missing_evidence',b,lambda r,e:e is not None,'Known assertion without evidence reference refuses.')
 b=deepcopy(base);b['context']['period_start']='20280101';b['authority']['period_start']='20280101'
 run('noncanonical_period',b,lambda r,e:e is not None,'Proposed canonical YYYY-MM-DD boundary; acceptance requires specification or implementation repair.')
 (out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
 summary=dict(status='PASS' if all(c['pass_check'] for c in cases) else 'REPAIR_REQUIRED',cases=len(cases),failures=[c['id'] for c in cases if not c['pass_check']],snapshot_sha256=sha256(source).hexdigest(),interpretation='Local dependency diagnostic only.')
 (out/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
 manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(ROOT)),started_utc=started,wall_seconds=time.monotonic()-start,environment=sys.version,cpu_gpu='CPU; GPU devices intentionally hidden',random_seeds='N/A: deterministic',data_version=summary['snapshot_sha256'],plan=str((H/'boundary-audit-plan.md').relative_to(ROOT)),result=str((out/'verification.json').relative_to(ROOT)),output=str(out.relative_to(ROOT)))
 (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(summary))

if __name__=='__main__':main()
