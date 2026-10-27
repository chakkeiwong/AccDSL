from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
from datetime import datetime,timezone
import json,time,platform
import decision as m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];out=HERE/'attempt-01';assert not out.exists();out.mkdir();start=time.monotonic()
checks=[];cases=[]
def save(n,x):(out/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))
def ck(name,ok):checks.append(dict(id=name,passed=bool(ok)));assert ok,name
base=ROOT/'data/accounting-master/inference-vintage-20261026';locks={str((base/n).relative_to(ROOT)):m.inference.sha256((base/n).read_bytes()).hexdigest() for n in ['inference.py','result.md','attempt-02/cases.json','attempt-02/checks.json']};save('source-lock.json',locks)
old=next(x for x in json.load(open(base/'attempt-02/cases.json')) if x['name']=='old_hard_observation')['request']
model=old['model'];sources=deepcopy(old['sources']);record=deepcopy(next(iter(old['evidence'].values())))
record['available_at']={'manager':'2026-01-01T00:00:00Z','analyst':'2026-01-01T00:00:00Z'}
old_id=m.inference.identity(record);registry={old_id:record}
revision=deepcopy(record);revision['supersedes']=old_id;revision['likelihood']={'fixed':'1/4','floating':'3/4'}
revision['available_at']={'manager':'2026-03-01T00:00:00Z','analyst':'2026-02-01T00:00:00Z'}
source='Authored correction with distinct actor availability.';source_id=m.inference.source_identity(source);sources[source_id]=source;revision['source_sha256']=source_id
revision_id=m.inference.identity(revision);both={**registry,revision_id:revision}
losses={'unhedged':{'fixed':'0/1','floating':'20/1'},'hedged':{'fixed':'6/1','floating':'6/1'}}
def run(name,actor,cutoff,records,raw,posterior,expected,minimizers):
    r0=deepcopy(records);s=m.select(model,records,raw,actor,cutoff);d=m.decide(s,losses)
    ck(name+'.selected',s['status']=='selected');ck(name+'.posterior',s['inference']['posterior']==posterior)
    ck(name+'.decision',d['status']=='complete' and d['expected_losses']==expected and d['minimizers']==minimizers)
    independent={a:m.inference.fmt(sum(F(posterior[h])*F(v[h]) for h in posterior)) for a,v in losses.items()}
    ck(name+'.enumerated_losses',d['expected_losses']==independent);ck(name+'.unchanged',records==r0)
    cases.append(dict(name=name,selection=s,decision=d));return s,d
early='2026-01-15T00:00:00Z';middle='2026-02-15T00:00:00Z';late='2026-03-02T00:00:00Z'
before,d0=run('old_registry','manager',early,registry,{record['source_sha256']:sources[record['source_sha256']]},{'fixed':'1/1','floating':'0/1'},{'unhedged':'0/1','hedged':'6/1'},['unhedged'])
future,d1=run('future_revision','manager',early,both,sources,{'fixed':'1/1','floating':'0/1'},{'unhedged':'0/1','hedged':'6/1'},['unhedged'])
ck('future_registry_does_not_rewrite_request',before['request']==future['request']);ck('future_registry_does_not_rewrite_decision',d0==d1)
manager,dm=run('manager_before_access','manager',middle,both,sources,{'fixed':'1/1','floating':'0/1'},{'unhedged':'0/1','hedged':'6/1'},['unhedged'])
analyst,da=run('analyst_after_access','analyst',middle,both,sources,{'fixed':'1/4','floating':'3/4'},{'unhedged':'15/1','hedged':'6/1'},['hedged'])
run('manager_after_access','manager',late,both,sources,{'fixed':'1/4','floating':'3/4'},{'unhedged':'15/1','hedged':'6/1'},['hedged'])
ck('wrong_actor_information_changes_decision',dm['minimizers']!=da['minimizers'])
ck('earlier_decision_still_reproducible',m.decide(before,losses)==d0)
tie=deepcopy(revision);tie['likelihood']={'fixed':'7/10','floating':'3/10'};tie_id=m.inference.identity(tie)
run('all_ties_retained','analyst',late,{old_id:record,tie_id:tie},sources,{'fixed':'7/10','floating':'3/10'},{'unhedged':'6/1','hedged':'6/1'},['hedged','unhedged'])
def refusal(name,records,raw,actor,cutoff,status,reason):
    x=m.select(model,records,raw,actor,cutoff);ck(name+'.status',x['status']==status);ck(name+'.reason',reason in x['reason']);ck(name+'.no_decision',m.decide(x,losses)['status']=='invalid');cases.append(dict(name=name,result=x))
unknown=deepcopy(revision);unknown['available_at']['manager']=None;unknown_id=m.inference.identity(unknown)
refusal('unknown_is_not_future',{old_id:record,unknown_id:unknown},sources,'manager',middle,'unresolved','unknown_actor_availability')
branch=deepcopy(revision);branch['likelihood']={'fixed':'3/4','floating':'1/4'};branch_id=m.inference.identity(branch)
refusal('incomparable_revisions',{**both,branch_id:branch},sources,'analyst',late,'unresolved','incomparable_available_revisions')
refusal('missing_predecessor',{revision_id:revision},sources,'analyst',late,'invalid','missing_ancestry')
refusal('unknown_actor',both,sources,'unobserved',late,'unresolved','unknown_actor_availability')
bad=deepcopy(sources);bad[source_id]+='changed';refusal('source_corruption',both,bad,'analyst',late,'invalid','source_identity')
fake=deepcopy(analyst);fake['inference']['posterior']={'fixed':'1/1','floating':'0/1'}
ck('forged_selection_refused',m.decide(fake,losses)['status']=='invalid')
unknown_losses=deepcopy(losses);unknown_losses['hedged']['fixed']=None
ck('unknown_action_loss_unresolved',m.decide(analyst,unknown_losses)['status']=='unresolved')
saved=m.inference.evaluate;calls=[]
def traced(request,checkpoint=None):calls.append(m.inference.identity(request));return saved(request,checkpoint)
m.inference.evaluate=traced
s=m.select(model,both,sources,'analyst',middle);d=m.decide(s,losses)
m.inference.evaluate=saved
ck('existing_evaluator_call_path',len(calls)==2 and all(h==d['request_sha256'] for h in calls))
for n,h in locks.items():ck('preserved.'+n,m.inference.sha256((ROOT/n).read_bytes()).hexdigest()==h)
for n in ['decision.py','verify.py']:(out/n).write_bytes((HERE/n).read_bytes())
save('cases.json',cases);save('checks.json',dict(status='PASS',assertions=len(checks),cases=len(cases),checks=checks))
save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/vintage-decision-20261026/verify.py',git_commit='unavailable; unusable marker preserved',environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,timestamp_utc=datetime.now(timezone.utc).isoformat(),data_version=locks,plan_file='docs/plans/accounting-vintage-decision-20261026.md',result_file='data/accounting-master/vintage-decision-20261026/result.md',artifacts=['cases.json','checks.json','source-lock.json','decision.py','verify.py']))
print(json.dumps(dict(status='PASS',assertions=len(checks),cases=len(cases))))
