"""Exact interval partitions, actor views and refusals against authored cases."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import itertools, json, os, platform, resource, subprocess, sys, time, traceback
import history as h
H=Path(__file__).resolve().parent;R=H.parents[2]
T=['2027-12-30T00:00:00Z','2027-12-31T00:00:00Z','2028-01-01T00:00:00Z']

def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
 assert os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
 resource.setrlimit(resource.RLIMIT_CPU,(60,60))
 started=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
 out=H/sys.argv[1];out.mkdir(exist_ok=False);checks=[];cases=[];controls=[]
 paths=[Path(__file__),H/'history.py',R/'docs/plans/accounting-control-history-contract-20261026.md',
        R/'scripts/company_world_envelope_v1.py',R/'data/accounting-master/vintage-decision-20261026/decision.py']
 paths += [Path(m.__file__) for m in [h.clock,h.clock.core,h.clock.binder,h.clock.dimensional]]
 lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in paths}
 for p in paths:
  q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 def ck(name,actual,expected=True):
  checks.append(dict(name=name,pass_check=actual==expected))
  if actual!=expected:raise AssertionError(name+': '+repr(actual)[:300]+' != '+repr(expected)[:300])
 def blank():return dict(profile=h.PROFILE,subject=['holder','issuer'],basis='conditional_AASB_design',interval=dict(start=T[0],end_exclusive=T[2]),actor='manager',cutoff='2028-01-02T00:00:00Z',records={},sources={})
 def add(b,name,a,z,status,availability=None,parent=None):
  text='Synthetic whole-interval assessment: '+name;sid=h.source_digest(text);b['sources'][sid]=text
  record=dict(profile=h.RECORD,subject=deepcopy(b['subject']),basis=b['basis'],start=a,end_exclusive=z,status=status,coverage='asserted_whole_interval',evidence_sha256=sid,available_at=availability if availability is not None else {'manager':'2027-12-29T00:00:00Z','analyst':'2027-12-29T00:00:00Z'},supersedes=parent)
  rid=h.digest(record);b['records'][rid]=record;return rid
 def evaluate(name,b,statuses):
  old=deepcopy(b);got=h.evaluate(b)
  ck(name+'/input',b,old);ck(name+'/statuses',[a['status'] for a in got['atoms']],statuses)
  ck(name+'/no-admission',[got[k] for k in ['source_admission','accounting_admission','posting_authorized']],[False]*3)
  ck(name+'/boundary-start',got['atoms'][0]['start'],h.normalized(h.moment(b['interval']['start'])))
  ck(name+'/boundary-end',got['atoms'][-1]['end_exclusive'],h.normalized(h.moment(b['interval']['end_exclusive'])))
  ck(name+'/partition',all(x['end_exclusive']==y['start'] for x,y in zip(got['atoms'],got['atoms'][1:])))
  ck(name+'/completion',got['status'],'partial' if 'unresolved' in statuses else 'conditionally_covered')
  cases.append(dict(id=name,input=b,result=got));return got
 def reject(name,b):
  original=deepcopy(b)
  try:h.evaluate(b)
  except (ValueError,KeyError,TypeError,AttributeError):controls.append(name);ck(name+'/refuse',True)
  else:ck(name+'/refuse',False)
  ck(name+'/unchanged',b,original)
 try:
  evaluate('empty-is-unknown',blank(),['unresolved'])
  for a,z in itertools.product(['yes','no','unknown'],repeat=2):
   b=blank();add(b,'left',T[0],T[1],a);add(b,'right',T[1],T[2],z)
   expected=[x if x!='unknown' else 'unresolved' for x in [a,z]];got=evaluate('two-cells/'+a+'/'+z,b,expected)
   transitions=[] if a==z or 'unknown' in [a,z] else ['gain' if z=='yes' else 'loss']
   ck('two-cells/'+a+'/'+z+'/transition',[r['kind'] for r in got['conditional_transitions']],transitions)
   ck('two-cells/'+a+'/'+z+'/continuous',got['continuous_control_under_assertions'],a==z=='yes')
  b=blank();add(b,'partial',T[0],T[1],'yes');evaluate('uncovered-gap',b,['yes','unresolved'])
  b=blank();add(b,'full',T[0],T[2],'yes');add(b,'conflict',T[1],T[2],'no');got=evaluate('overlap-conflict',b,['yes','unresolved']);ck('conflict-reason','conflicting_control_assertions' in got['atoms'][1]['reasons'])
  b=blank();add(b,'full',T[0],T[2],'yes');add(b,'unknown',T[1],T[2],'unknown');evaluate('unknown-overlap',b,['yes','unresolved'])
  b=blank();add(b,'left',T[0],T[1],'no');add(b,'right-offset','2027-12-31T08:00:00+08:00','2028-01-01T08:00:00+08:00','yes');evaluate('same-instant-offset',b,['no','yes'])
  b=blank();first=add(b,'original',T[0],T[2],'no');before=evaluate('original-view',deepcopy(b),['no'])
  newer=add(b,'correction',T[0],T[2],'yes',{'manager':'2028-02-01T00:00:00Z','analyst':'2028-01-01T00:00:00Z'},first)
  early=evaluate('future-correction-manager',deepcopy(b),['no']);ck('future-not-rewrite-atoms',early['atoms'],before['atoms']);ck('future-excluded',early['excluded_future'],[newer])
  analyst=deepcopy(b);analyst['actor']='analyst';got=evaluate('analyst-correction',analyst,['yes']);ck('analyst-head',got['available_heads'],[newer])
  late=deepcopy(b);late['cutoff']='2028-02-01T00:00:00Z';evaluate('manager-later-correction',late,['yes'])
  b=blank();first=add(b,'original',T[0],T[2],'yes');add(b,'unknown-correction',T[0],T[2],'no',{'manager':None},first);got=evaluate('unknown-availability-is-not-future',b,['unresolved']);ck('unknown-availability-reason','unknown_actor_availability' in got['atoms'][0]['reasons'])
  b=blank();first=add(b,'original',T[0],T[2],'yes');add(b,'branch-no',T[0],T[2],'no',parent=first);add(b,'branch-yes',T[0],T[2],'yes',parent=first);evaluate('incomparable-revisions',b,['unresolved'])
  b=blank();add(b,'two-same-one',T[0],T[2],'yes');add(b,'two-same-two',T[0],T[2],'yes');evaluate('consistent-independent-assertions',b,['yes'])
  b=blank();add(b,'before-query','2027-12-01T00:00:00Z',T[0],'yes');evaluate('half-open-outside',b,['unresolved'])
  def valid():
   b=blank();rid=add(b,'valid',T[0],T[2],'yes');return b,rid
  for name,mutation in [
   ('no-coverage',lambda r:r.update(coverage='snapshot_only')),
   ('backwards',lambda r:r.update(start=T[2],end_exclusive=T[0])),
   ('other-subject',lambda r:r.update(subject=['other','issuer'])),
   ('missing-parent',lambda r:r.update(supersedes='0'*64)),
   ('bad-date',lambda r:r.update(start='2027-12-30')),
   ('bad-state',lambda r:r.update(status='probably')),
   ('bad-availability',lambda r:r.update(available_at={'manager':'2027-12-29'})),
   ('no-evidence',lambda r:r.update(evidence_sha256='0'*64))]:
   b,rid=valid();row=b['records'].pop(rid);mutation(row);b['records'][h.digest(row)]=row;reject(name,b)
  b,rid=valid();b['records'][rid]['status']='no';reject('record-tamper',b)
  b,rid=valid();b['sources'][next(iter(b['sources']))]='tampered';reject('source-tamper',b)
  b,rid=valid();add(b,'partial-revision',T[1],T[2],'no',parent=rid);reject('partial-revision-refuses',b)
  b,rid=valid();b['interval']['end_exclusive']=T[0];reject('empty-query',b)
  b,rid=valid();b['cutoff']='2028-01-02T00:00:60Z';reject('leap-second',b)
  b,rid=valid();b['cutoff']='2028-01-02T00:00:00-00:00';reject('unknown-offset',b)
  for p,s in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),s)
  result=dict(status='PASS',cases=len(cases),controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,scope='Exact partition and actor-view conformance under supplied whole-interval assertions only.')
 except Exception:result=dict(status='FAIL',assertions=len(checks),error=traceback.format_exc())
 for name,obj in [('verification.json',result),('cases.json',cases),('checks.json',checks),('controls.json',controls),('source-lock.json',lock)]:(out/name).write_text(json.dumps(obj,indent=2)+chr(10))
 manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU devices intentionally hidden',random_seeds='N/A: deterministic',data_version='source-lock.json',started_utc=started,wall_seconds=time.monotonic()-clock,plan='docs/plans/accounting-control-history-contract-20261026.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
 (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10));print(json.dumps(result))
 if result['status']!='PASS':sys.exit(1)

if __name__=='__main__':main()
