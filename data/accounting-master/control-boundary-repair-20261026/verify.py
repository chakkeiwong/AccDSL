"""Exact endpoint, saved-case and malformed-input checks; append-only output."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import itertools, json, os, platform, resource, subprocess, sys, time, traceback
import dependencies_v2 as d

H=Path(__file__).resolve().parent;R=H.parents[2]
OLD=R/'data/accounting-master/conversion-control-scope-20261026'

def main():
 started=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
 assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
 assert os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
 resource.setrlimit(resource.RLIMIT_CPU,(60,60))
 out=H/sys.argv[1];out.mkdir(exist_ok=False)
 cases=[];checks=[];controls=[]
 inputs=[H/'baseline.py',H/'baseline.json',H/'dependencies_v2.py',H/'expected-endpoints.json',H/'contract.md',Path(__file__),R/'docs/plans/accounting-control-boundary-repair-20261026.md',OLD/'attempt-01/cases.json',OLD/'scope-inspection/boundary-attempt-01/cases.json',OLD/'source-attempt-02/aasb10-2026.pdf',OLD/'scope-inspection/technical-review.md']
 lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in inputs}
 for p in inputs:
  q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 def ck(name,got,want=True):
  checks.append(dict(name=name,pass_check=got==want))
  if got!=want:raise AssertionError(name+': '+repr(got)[:300]+' != '+repr(want)[:300])
 saved=json.loads((OLD/'attempt-01/cases.json').read_text())
 base=deepcopy(saved[0]['input']);base['profile']=d.PROFILE
 def state(body,key,value):
  a=body[key]['elements']['power'];a['status']=value;a['evidence']=[] if value=='unknown' else ['synthetic:endpoint-table']
 def evaluate(name,body):
  original=deepcopy(body);got=d.evaluate(body)
  ck(name+'/unchanged',body,original)
  ck(name+'/admission',[got[k] for k in ['source_admission','accounting_admission','posting_authorized']],[False]*3)
  ck(name+'/interval','complete_control_history_between_assessments' in got['missing'])
  ck(name+'/not_complete',got['interval_history'],'unresolved')
  cases.append(dict(id=name,input=original,result=got));return got
 def reject(name,mutation):
  body=deepcopy(base);mutation(body);original=deepcopy(body)
  try:d.evaluate(body)
  except (ValueError,TypeError,KeyError):controls.append(name);ck(name+'/refused',True)
  else:ck(name+'/refused',False)
  ck(name+'/unchanged',body,original)
 try:
  expected=json.loads((H/'expected-endpoints.json').read_text())
  ck('all-nine-endpoints',{(r['before'],r['after']) for r in expected},set(itertools.product(['yes','no','unknown'],repeat=2)))
  for row in expected:
   b=deepcopy(base);state(b,'control_before',row['before']);state(b,'control_after',row['after'])
   name=row['before']+'/'+row['after'];got=evaluate(name,b)
   ck(name+'/timing',got['timing'],row['timing'])
   ck(name+'/transitions',got['required_transitions'],row['required'])
   ck(name+'/classes',got['possible_history_classes'],sorted(row['classes']))
   ck(name+'/routes',got['routes'],row['routes'])
   routes={x['route'] for x in got['conditional_dependencies']}
   ck(name+'/gain-dependency','gain_of_control_assessment' in routes,any('gain' in x for x in row['classes']))
   ck(name+'/loss-dependency','loss_of_control_assessment' in routes,any('loss' in x for x in row['classes']))
   ck(name+'/continued-dependency','continued_control_conversion' in routes,'continuous_control' in row['classes'])
   ck(name+'/no-exclusive-acquisition','business_combination' not in got['routes'])
  for old in saved:
   b=deepcopy(old['input']);b['profile']=d.PROFILE;got=evaluate('retained/'+old['id'],b)
   want=old['result']['routes']
   if want[0]=='consolidation_scope':want=['consolidation_scope','control_history_unresolved']
   ck('retained/'+old['id']+'/report-context',got['routes'],want)
   ck('retained/'+old['id']+'/votes',got['vote_fraction_descriptive'],old['result']['vote_fraction_descriptive'])
   for key in b['measurements']:
    ck('retained/'+old['id']+'/measurement-remains/'+key,key in got['missing'])
  for invalid in ['20280101','2028-W01-1','2028-1-01','2028-02-30',20280101,None]:
   reject('period/'+repr(invalid),lambda b,v=invalid:(b['context'].update(period_start=v),b['authority'].update(period_start=v)))
  for field in ['conversion_date','before','after','assessment','authority']:
   def mutate(b,key=field):
    if key=='conversion_date':b[key]='20280101'
    elif key in ['before','after']:b['control_'+key]['as_of']='20280101'
    elif key=='assessment':b['assessments']['business']['as_of']='20280101'
    else:b['authority']['period_start']='20280101'
   reject('date/'+field,mutate)
  rejects=[('missing_evidence',lambda b:b['control_after']['elements']['power'].update(evidence=[])),
   ('wrong_subject',lambda b:b['control_before']['elements']['power'].update(subject=['issuer','holder'])),
   ('wrong_assessment_date',lambda b:b['control_after']['elements']['power'].update(as_of='2027-01-01')),
   ('absent_review',lambda b:b['control_after']['reviews'].pop('timing')),
   ('unknown_field',lambda b:b.update(control_inferred=True)),
   ('boolean_votes',lambda b:b['votes'].update(received=True)),
   ('zero_total',lambda b:b['votes'].update(total=0)),
   ('measurement_as_admission',lambda b:b['measurements'].update(accounting_authority_admission='ok')),
   ('authority_as_admission',lambda b:b['authority'].update(status='admitted')),
   ('wrong_profile',lambda b:b.update(profile='ConversionScopeDependencies/1')),
   ('wrong_context',lambda b:b['context'].update(issuer='holder')),
   ('misordered_dates',lambda b:b.update(conversion_date='2027-01-01'))]
  for name,fn in rejects:reject(name,fn)
  # Frozen v1 must still reproduce the two substantive discriminators.
  oldcases=json.loads((OLD/'scope-inspection/boundary-attempt-01/cases.json').read_text())
  for case in oldcases:
   if case['id'] in ['unknown_prior_control','loss_of_control']:
    ck('baseline-discriminator/'+case['id'],d.baseline.evaluate(case['input']),case['output'])
  for path,h in lock.items():ck('protected/'+path,sha256((R/path).read_bytes()).hexdigest(),h)
  result=dict(status='PASS',endpoint_cases=9,retained_cases=len(saved),cases=len(cases),controls=len(controls),assertions=len(checks),protected_files=len(lock),scope='Exact local dependency routing and refusal only; no actual control, journals or authority admission.')
 except Exception:
  result=dict(status='FAIL',assertions=len(checks),error=traceback.format_exc())
 for name,obj in [('verification.json',result),('checks.json',checks),('cases.json',cases),('controls.json',controls),('source-lock.json',lock)]:
  (out/name).write_text(json.dumps(obj,indent=2)+chr(10))
 manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU devices intentionally hidden',random_seeds='N/A: exact deterministic',data_version='source-lock.json',started_utc=started,wall_seconds=time.monotonic()-clock,plan='docs/plans/accounting-control-boundary-repair-20261026.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
 (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10));print(json.dumps(result))
 if result['status']!='PASS':sys.exit(1)

if __name__=='__main__':main()
