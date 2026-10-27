"""Bounded exact comparisons for immutable-vintage requests."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
import json,platform,sys,time
import inference as m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
start=time.monotonic();attempt=HERE/'attempt-02';assert not attempt.exists();attempt.mkdir()
checks=[];cases=[]
def save(n,x):(attempt/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))
def ck(name,ok):
    checks.append(dict(id=name,passed=bool(ok)))
    save('checks.json',dict(status='running',checks=checks))
    assert ok,name
def observation(slot,likelihood,text,supersedes=None,at='2026-01-01T00:00:00Z',disposition='observation',information_id=None):
    source=m.source_identity(text)
    r=dict(profile='FiniteObservation/1',slot=slot,information_id=information_id or slot,available_at={'analyst':at},source_sha256=source,supersedes=supersedes,disposition=disposition,likelihood=likelihood)
    return m.identity(r),r,source,text
def packet(items,heads,prior=None):
    return dict(profile=m.PROFILE,model=dict(profile='FinitePersistentTypeModel/1',states=['fixed','floating'],prior=prior or {'fixed':'1/2','floating':'1/2'},observation_model='authored-finite-diagnostic/1',factorization='conditionally_independent_given_type'),actor='analyst',cutoff='2026-03-01T00:00:00Z',heads=heads,evidence={h:r for h,r,_,_ in items},sources={s:t for _,_,s,t in items})
def exact_expected(prior,vectors):
    masses={s:F(q) for s,q in prior.items()}
    for s in masses:
        for v in vectors:masses[s]*=F(v[s])
    total=sum(masses.values())
    return {s:m.fmt(q/total) for s,q in masses.items()},m.fmt(total)
def accepted(name,request,vectors,checkpoint=None,route=None):
    original=deepcopy(request);cp=deepcopy(checkpoint)
    got=m.evaluate(request,checkpoint);expected,z=exact_expected(request['model']['prior'],vectors)
    ck(name+'.complete',got['status']=='complete')
    ck(name+'.all_masses',got['posterior']==expected)
    ck(name+'.normalizer',got['normalizer']==z)
    ck(name+'.request_identity',got['request_sha256']==m.identity(request))
    ck(name+'.unchanged',request==original and checkpoint==cp)
    if route:ck(name+'.route',got['route']==route)
    cases.append(dict(name=name,request=request,checkpoint=checkpoint,result=got,expected=expected,expected_normalizer=z))
    return got
def refused(name,request,status,reason,checkpoint=None):
    original=deepcopy(request);got=m.evaluate(request,checkpoint)
    ck(name+'.status',got['status']==status)
    ck(name+'.reason',reason in got.get('reason',''))
    ck(name+'.no_posterior','posterior' not in got and request==original)
    cases.append(dict(name=name,request=request,checkpoint=checkpoint,result=got))

paths=['data/accounting-master/gap-program-20261026/smc2_exchange.py','data/accounting-master/gap-program-20261026/smc2-exchange-results.json','data/accounting-master/gap-program-20261026/smc2-transfer.md','data/accounting-master/exact-information-time-20261026/projection.py','scripts/method_requirements_v1.py','scripts/method_input_binding_v2.py','scripts/method_requirements_v2.py']
locks={p:m.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths};save('source-lock.json',locks)
old=observation('rate-type',{'fixed':'1/1','floating':'0/1'},'Synthetic old observation: fixed only.')
new=observation('rate-type',{'fixed':'1/4','floating':'3/4'},'Synthetic correction: uncertain rate type.',old[0],at='2026-02-01T00:00:00Z')
extra=observation('independent-signal',{'fixed':'1/2','floating':'1/4'},'Authored independent second signal.')
retract=observation('rate-type',None,'Synthetic retraction.',new[0],at='2026-02-02T00:00:00Z',disposition='retraction')
r0=packet([old],[old[0]]);r1=packet([old,new],[new[0]])
accepted('old_hard_observation',r0,[old[1]['likelihood']]);cp=m.make_checkpoint(r0)
restored=accepted('replacement_restores_support',r1,[new[1]['likelihood']],cp,'replay_prior')
ck('replacement.literal_posterior',restored['posterior']=={'fixed':'1/4','floating':'3/4'})
wrong,_=exact_expected({'fixed':'1/1','floating':'0/1'},[new[1]['likelihood']])
ck('wrong_restricted_posterior_discriminated',wrong!=restored['posterior'])
r2=packet([old,new,extra],[new[0],extra[0]])
accepted('second_signal',r2,[new[1]['likelihood'],extra[1]['likelihood']],m.make_checkpoint(r1),'verified_prefix')
accepted('no_new_observation',r1,[new[1]['likelihood']],m.make_checkpoint(r1),'verified_prefix')
accepted('retraction_restores_prior',packet([old,new,retract],[retract[0]]),[],cp,'replay_prior')
accepted('retraction_keeps_other_signal',packet([old,new,retract,extra],[retract[0],extra[0]]),[extra[1]['likelihood']],m.make_checkpoint(r2),'replay_prior')
accepted('empty_prior_checkpoint',r1,[new[1]['likelihood']],m.make_checkpoint(packet([],[])),'verified_prefix')
accepted('unequal_prior',packet([old,new],[new[0]],{'fixed':'1/3','floating':'2/3'}),[new[1]['likelihood']])
accepted('zero_prior_support_remains_zero',packet([old,new],[new[0]],{'fixed':'1/1','floating':'0/1'}),[new[1]['likelihood']])
same=observation('rate-type',{'fixed':'1/4','floating':'3/4'},'Same-clock correction.',old[0])
accepted('same_clock_explicit_replacement',packet([old,same],[same[0]]),[same[1]['likelihood']])
different_bytes=observation('rate-type',{'fixed':'1/4','floating':'3/4'},'Another source with the same likelihood.',old[0],at='2026-02-01T00:00:00Z')
other=accepted('equal_numeric_distinct_vintage',packet([old,different_bytes],[different_bytes[0]]),[different_bytes[1]['likelihood']])
ck('source_identity_not_numeric_equality',other['request_sha256']!=restored['request_sha256'])

for actor,cutoff,status,reason in [('unknown_actor',r1['cutoff'],'unresolved','availability_unknown'),('analyst','2026-01-15T00:00:00Z','ineligible','after_cutoff')]:
    q=deepcopy(r1);q['actor']=actor;q['cutoff']=cutoff;refused(actor+cutoff,q,status,reason)
unknown=observation('rate-type',{'fixed':'1/4','floating':'3/4'},'Unknown availability',old[0],at=None)
refused('unknown_availability',packet([old,unknown],[unknown[0]]),'unresolved','availability_unknown')
future=observation('rate-type',{'fixed':'1/4','floating':'3/4'},'Just after exact cutoff',old[0],at='2026-03-01T00:00:00.000000000000000001Z')
refused('subnanosecond_future',packet([old,future],[future[0]]),'ineligible','after_cutoff')
q=deepcopy(r1);q['cutoff']='2026-03-01';refused('date_only_cutoff',q,'invalid','explicit_fixed_offset')
q=deepcopy(r1);q['model']['prior']['floating']=None;refused('unknown_prior',q,'unresolved','prior_probability_unknown')
unknown_lik=observation('signal',{'fixed':'1/1','floating':None},'Unknown likelihood')
refused('unknown_likelihood',packet([unknown_lik],[unknown_lik[0]]),'unresolved','likelihood_probability_unknown')
impossible=observation('signal',{'fixed':'0/1','floating':'0/1'},'Impossible evidence')
refused('zero_normalizer',packet([impossible],[impossible[0]]),'incompatible','zero_normalizer')
refused('conflicting_heads',packet([old,new],[old[0],new[0]]),'invalid','conflicting_active_slot_heads')
refused('missing_ancestry',packet([new],[new[0]]),'invalid','replacement_ancestry_missing')
wrongslot=observation('different-slot',new[1]['likelihood'],'Wrong slot',old[0])
refused('cross_slot_replacement',packet([old,wrongslot],[wrongslot[0]]),'invalid','replacement_slot_mismatch')
early=observation('rate-type',new[1]['likelihood'],'Earlier than original',old[0],at='2025-01-01T00:00:00Z')
refused('replacement_before_parent',packet([old,early],[early[0]]),'invalid','replacement_precedes_parent')
refused('unselected_records',packet([old,new],[old[0]]),'invalid','unselected_evidence_records')
duplicate=observation('renamed-slot',new[1]['likelihood'],'Same semantic information repackaged.',information_id='rate-type')
refused('duplicate_information_different_slot',packet([old,new,duplicate],[new[0],duplicate[0]]),'invalid','duplicate_active_information')
doubled,_=exact_expected(r1['model']['prior'],[new[1]['likelihood'],new[1]['likelihood']])
ck('duplicate_information_changes_target',doubled=={'fixed':'1/10','floating':'9/10'} and doubled!=restored['posterior'])
wronginfo=observation('rate-type',new[1]['likelihood'],'Different information mislabelled as replacement.',old[0],information_id='other-fact')
refused('replacement_information_changed',packet([old,wronginfo],[wronginfo[0]]),'invalid','replacement_information_mismatch')
q=deepcopy(r1);q['sources'][old[2]]+=' altered';refused('corrupt_source',q,'invalid','source_content_mismatch')
q=deepcopy(r1);q['evidence'][new[0]]['likelihood']['fixed']='1/2';refused('mutated_likelihood',q,'invalid','evidence_content_mismatch')
q=deepcopy(r1);q['evidence'][old[0]]['supersedes']=new[0];refused('circular_mutation',q,'invalid','evidence_content_mismatch')
q=deepcopy(r1);q['model']['factorization']='unexamined';refused('missing_independence_premise',q,'invalid','explicit_factorization')
q=deepcopy(r1);q['model']['prior']['fixed']=0.5;refused('float_prior',q,'invalid','exact_rational')
q=deepcopy(r1);q['model']['prior']['fixed']='2/4';refused('noncanonical_fraction',q,'invalid','canonical_rational')
q=deepcopy(r1);q['model']['prior']['fixed']='1/1';refused('unnormalized_prior',q,'invalid','normalized_prior')
badcp=deepcopy(cp);badcp['result']['posterior']={'fixed':'1/2','floating':'1/2'};refused('forged_checkpoint_mass',r1,'invalid','checkpoint_calculation_mismatch',badcp)
for key in ['model','actor','cutoff']:
    q=deepcopy(r1)
    if key=='model':q[key]['observation_model']='different-model'
    elif key=='actor':
        # A prior-only checkpoint isolates actor mismatch from evidence availability.
        q=packet([],[]);q[key]='another-analyst'
    else:q[key]='2026-03-01T08:00:00+08:00'
    oldcp=m.make_checkpoint(packet([],[])) if key=='actor' else cp
    refused('checkpoint_'+key+'_drift',q,'invalid','checkpoint_'+key+'_mismatch',oldcp)
saved=m._time.instant;calls=[]
def traced(s):calls.append(s);return saved(s)
m._time.instant=traced
accepted('timestamp_call_chain',r1,[new[1]['likelihood']])
m._time.instant=saved
ck('timestamp_existing_implementation_used',calls==[r1['cutoff'],new[1]['available_at']['analyst'],old[1]['available_at']['analyst']])
uninformative=observation('uninformative',{'fixed':'1/1','floating':'1/1'},'No distinction between types.')
accepted('persistent_ambiguity',packet([uninformative],[uninformative[0]]),[uninformative[1]['likelihood']])
accepted('independent_factors_reverse_order',packet([old,new,extra],[extra[0],new[0]]),[extra[1]['likelihood'],new[1]['likelihood']],m.make_checkpoint(r2),'replay_prior')

# A declared finite lattice tests replacement support and prefix behavior beyond
# the motivating two examples. This is exact coverage of this grid, not a sweep
# selecting model defaults or a statistical method ranking.
for numerator in [1,2,3]:
    prior={'fixed':m.fmt(F(numerator,4)),'floating':m.fmt(1-F(numerator,4))}
    for left in [0,1,2]:
        for right in [0,1,2]:
            if not (left or right):continue
            likelihood={'fixed':m.fmt(F(left,2)),'floating':m.fmt(F(right,2))}
            replacement=observation('rate-type',likelihood,'Finite-grid replacement '+str((numerator,left,right)),old[0],at='2026-02-01T00:00:00Z')
            request=packet([old,replacement,extra],[replacement[0],extra[0]],prior)
            old_checkpoint=m.make_checkpoint(packet([old],[old[0]],prior))
            accepted('grid_'+str((numerator,left,right)),request,[likelihood,extra[1]['likelihood']],old_checkpoint,'replay_prior')

for p,h in locks.items():ck('preserved.'+p,m.sha256((ROOT/p).read_bytes()).hexdigest()==h)
for p in ['inference.py','verify.py']:(attempt/p).write_bytes((HERE/p).read_bytes())
save('cases.json',cases)
save('checks.json',dict(status='PASS',assertions=len(checks),accepted_cases=sum(c['result']['status']=='complete' for c in cases),refused_cases=sum(c['result']['status']!='complete' for c in cases),checks=checks))
save('run-manifest.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),git_commit='unavailable; unusable marker preserved',command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/inference-vintage-20261026/verify.py',environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic exact enumeration',wall_seconds=time.monotonic()-start,data_version=locks,plan_file='docs/plans/accounting-inference-vintage-20261026.md',result_file='data/accounting-master/inference-vintage-20261026/result.md',artifacts=['checks.json','cases.json','source-lock.json','inference.py','verify.py']))
print(json.dumps(dict(status='PASS',assertions=len(checks),cases=len(cases),source_files=len(locks))))
