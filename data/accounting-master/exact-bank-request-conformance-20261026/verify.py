"""Full request/response timing comparisons with independently retained outputs."""
from fixtures import *
from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,time
NL=chr(10)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+NL)
def result(fn):
 try:fn();return 'accepted'
 except n.Refusal as exc:return exc.code
def check(ok,reason):
 if not ok:raise AssertionError(reason)
def main():
 start=time.monotonic();lock_path=HERE/'source-lock.json'
 if not lock_path.exists():
  lock=json.loads((timing.HERE/'source-lock.json').read_text())
  files=[timing.HERE/x for x in ['checker.py','verify.py','checks.json','result.md','design.md']]
  files += [timing.ATT/'inputs'/x for x in ['build_exchanges.py','semantic-contract.md']]
  files += [ROOT/'docs/plans/accounting-exact-bank-request-conformance-20261026.md']
  for p in files:lock[str(p.relative_to(ROOT))]=sha(p)
  dump(lock_path,lock)
 lock=json.loads(lock_path.read_text())
 for p,h in lock.items():check(sha(ROOT/p)==h,'protected:'+p)
 old=n.Auditor(timing.ATT);exact=timing.Auditor(timing.ATT)
 retained=[e for e in old.packet['exchanges'] if old.body(e['request_ref'])['operation']==n.OPS[0]]
 for ex in retained:old.response(ex);exact.response(ex)
 print(json.dumps({'phase':'retained_response_regression','passed':len(retained)}),flush=True)
 base={'available_at':'2026-04-01T00:00:00.0000001Z','ingested_at':'2026-04-01T00:00:00.0000001Z',
  'decision_at':'2026-04-01T00:00:00.0000001Z','system_asof':'2026-04-01T00:00:00.0000001Z'}
 cases=[('equal',{},'accepted','accepted'),
  ('later-availability',{'available_at':'2026-04-01T00:00:00.0000002Z'},'later_information','accepted'),
  ('later-ingestion',{'ingested_at':'2026-04-01T00:00:00.0000002Z'},'later_ingestion','accepted'),
  ('offset-equivalent',{'available_at':'2026-04-01T01:00:00.0000001+01:00'},'accepted','accepted'),
  ('precision-limit',{'available_at':'2026-04-01T00:00:00.0000001000000000001Z'},'exact_time_unsupported:fraction_precision_limit','accepted'),
  ('unknown-offset',{'available_at':'2026-04-01T00:00:00.0000001-00:00'},'exact_time_unsupported:unknown_negative_zero_offset','accepted'),
  ('equal-eighteen-digits',{k:'2026-04-01T00:00:00.123456789123456789Z' for k in base},'accepted','accepted'),
  ('later-eighteenth-digit',{**{k:'2026-04-01T00:00:00.123456789123456788Z' for k in base},
    'available_at':'2026-04-01T00:00:00.123456789123456789Z'},'later_information','accepted'),
  ('utc-date-equivalent',{'available_at':'2026-03-31T22:00:00Z','ingested_at':'2026-03-31T22:00:00Z',
    'decision_at':'2026-04-01T00:00:00+02:00','system_asof':'2026-04-01T00:00:00+02:00'},'accepted','accepted'),
  ('assessment-after-decision',{'decision_at':'2026-03-31T00:00:00+02:00'},'assessment_after_decision','assessment_after_decision')]
 folder=HERE/'examples';folder.mkdir(exist_ok=True);comparisons=[];fixtures={};replays=[]
 for name,changes,expected,expected_old in cases:
  f=Fixture(name,{**base,**changes});f.base_request();a=f.a;prior=f.original_auditor()
  actual=result(lambda:a.request(f.rq,f.sub,f.before));previous=result(lambda:prior.request(f.rq,f.sub,f.before))
  check((actual,previous)==(expected,expected_old),name+':'+actual+':'+previous)
  ex=f.response(None if expected=='accepted' else expected);a.response(ex)
  # Auditor result methods must not mutate the caller's registry or world.
  before=deepcopy(ex['world_before']);snapshot=n.sha(n.enc(a.reg));a.response(ex)
  check(ex['world_before']==before and n.sha(n.enc(a.reg))==snapshot,'auditor_mutation')
  for key in ['accounting_heads','journals','unrelated_owners']:
   check(ex['world_after'][key]==before[key],name+':accounting_effect:'+key)
  r=a.body(f.rq);basis=a.body(r['arguments']['value']['basis_ref']);newstate=a.body(basis['state_ref'])
  oldr=f.original[f.template['request_ref']['digest']]['body'];oldbasis=f.original[oldr['arguments']['value']['basis_ref']['digest']]['body']
  oldstate=f.original[oldbasis['state_ref']['digest']]['body']
  check(newstate['balances']==oldstate['balances'] and newstate['opening_balances']==oldstate['opening_balances'],'unchanged_financial_state')
  # Entire state equals the old state with only the explicitly repinned refs.
  check(newstate==f.walk(oldstate),'state_correspondence')
  a.shape(a.record(f.rq),f.rq['digest']);a.shape(a.record(f.sub),f.sub['digest'])
  if expected=='accepted':
   prior=f.original_auditor();prior.response(ex)
   response=a.body(ex['response_ref']);original_response=f.original[f.template['response_ref']['digest']]['body']
   out=a.body(response['payload']['result_refs'][0]);original_output=f.original[original_response['payload']['result_refs'][0]['digest']]['body']
   for group in ['amounts','ratios']:
    for key,value in out[group].items():
     check({k:v for k,v in value.items() if k!='dependency_refs'}=={k:v for k,v in original_output[group][key].items() if k!='dependency_refs'},'financial_output_changed')
   check(len(ex['world_after']['query_index'])==1 and not before['query_index'],'single_query_publication')
   replay_body=deepcopy(response);replay_body['disposition']='replayed';replay_body['payload']['additional_commit']=False
   replay_ref=f.clone(ex['response_ref'],**replay_body)
   replay={**deepcopy(ex),'id':name+'.replay','role':'exact_replay','response_ref':replay_ref,
    'world_before':deepcopy(ex['world_after']),'world_after':deepcopy(ex['world_after'])}
   a.response(replay);f.original_auditor().response(replay)
   replays.append({'case':name,'exact_replay':True,'world_unchanged':True})
   dump(folder/(name+'.replay.json'),replay)
  else:
   check(ex['world_after']==before,'refusal_changed_world')
   if expected_old!=expected:
    check(result(lambda:f.original_auditor().response(ex))=='missing_query_output','old_accepts_successor_refusal')
  # Store only derived records plus their frozen base, not repeated whole packets.
  package={'evidence_mode':'complete_derived_request_response_conformance','checker_profile':timing.PROFILE,
   'record_profile':'BankAssessment/1','profile_adoption':False,'base_packet':str((timing.ATT/'portable-exchanges.json').relative_to(ROOT)),
   'base_packet_sha256':sha(timing.ATT/'portable-exchanges.json'),'records':f.records,'blobs':f.blobs,
   'times':{**base,**changes},'expected':expected,'expected_original':expected_old,'exchange':ex}
  dump(folder/(name+'.json'),package)
  comparisons.append({'case':name,'exact':actual,'original':previous,'complete_response_checked':True,
   'query_published':expected=='accepted','accounting_unchanged':True,'record_count':len(f.records)})
  fixtures[name]=(f,ex)
 print(json.dumps({'phase':'complete_derived_requests','passed':len(comparisons),'replays':len(replays)}),flush=True)
 controls=[];f,ex=fixtures['equal'];a=f.a
 def refused(label,call,code):
  actual=result(call);check(actual==code,label+':'+actual);controls.append({'case':label,'reason':actual})
 badworld=deepcopy(f.before);badworld['current_view_ref']=f.template['world_before']['current_view_ref']
 refused('stale-view',lambda:a.request(f.rq,f.sub,badworld),'stale_view')
 badworld=deepcopy(f.before);key=next(iter(badworld['accounting_heads']));badworld['accounting_heads'][key]['generation']+=1
 refused('changed-accounting-head',lambda:a.request(f.rq,f.sub,badworld),'stale_accounting_head')
 refused('wrong-submission-bytes',lambda:a.request(f.rq,f.template['submission_ref'],f.before),'submission_bytes_mismatch')
 rq=f.clone(f.rq,request_id='timing.bad-head',expected_head=None);sub=f.submission(rq,'.bad-head')
 refused('missing-accounting-head',lambda:a.request(rq,sub,f.before),'expected_head_required')
 rq=f.clone(f.rq,request_id='timing.bad-signature',signature_ref=f.a.body(next(e for e in a.packet['exchanges'] if a.body(e['request_ref'])['operation']==n.OPS[1])['request_ref'])['signature_ref'])
 sub=f.submission(rq,'.bad-signature');refused('foreign-operation-signature',lambda:a.request(rq,sub,f.before),'signature_mismatch')
 rq=f.clone(f.rq,execution={**a.body(f.rq)['execution'],'budget':{'operation_count':0,'elapsed_seconds':60}});sub=f.submission(rq,'.budget')
 refused('exhausted-budget',lambda:a.request(rq,sub,f.before),'budget_exhausted')
 rq=f.clone(f.rq,execution={**a.body(f.rq)['execution'],'budget':{'operation_count':999,'elapsed_seconds':60}});sub=f.submission(rq,'.conflict')
 refused('identity-conflict',lambda:a.request(rq,sub,ex['world_after']),'request_identity_conflict')
 bad=deepcopy(ex);bad['world_after']['journals'].append({'forged':'post'})
 refused('query-adds-accounting-journal',lambda:a.response(bad),'non_atomic_or_accounting_publication')
 bad=deepcopy(ex);bad['world_after']['query_index']={}
 refused('query-index-not-published',lambda:a.response(bad),'non_atomic_or_accounting_publication')
 negative,nex=fixtures['later-availability'];bad=deepcopy(nex);bad['world_after']['published_records'].append(nex['response_ref']['digest'])
 refused('refusal-publishes-response',lambda:negative.a.response(bad),'refusal_changed_world')
 bad=deepcopy(nex);body=deepcopy(negative.a.body(bad['response_ref']));body['diagnostics'][0]['code']='later_ingestion';bad['response_ref']=negative.clone(bad['response_ref'],**body)
 refused('wrong-refusal-diagnostic',lambda:negative.a.response(bad),'wrong_refusal')
 outref=a.body(ex['response_ref'])['payload']['result_refs'][0];out=deepcopy(a.body(outref));out['minimum_ratio_verdict']='forged'
 refused('tampered-financial-output',lambda:a.output(n.OPS[0],a.body(f.rq)['arguments']['value']['basis_ref'],out),'query_output_mismatch')
 # A saved package must replay without any fixture-construction state.
 reconstructed=0
 for row in comparisons:
  package=json.loads((folder/(row['case']+'.json')).read_text());fresh=timing.Auditor(timing.ATT)
  fresh.reg.update(package['records']);fresh.blobs.update(package['blobs'])
  for h,record in package['records'].items():fresh.shape(record,h)
  fresh.closure([package['exchange']['response_ref']]);fresh.response(package['exchange']);reconstructed+=1
 for p,h in lock.items():check(sha(ROOT/p)==h,'protected_after:'+p)
 checks={'passed':True,'retained_regulatory_responses':len(retained),'complete_derived_cases':len(comparisons),
  'changed_expected_results':sum(x['exact']!=x['original'] for x in comparisons),'exact_replays':len(replays),
  'adverse_controls':len(controls),'saved_packages_revalidated':reconstructed,'protected_files':len(lock),
  'full_derived_request_response':True,'financial_amounts_unchanged':True,'profile_adoption':False,
  'source_admission':False,'accounting_admission':False,'executed':False}
 for name,value in [('checks.json',checks),('comparisons.json',comparisons),('adverse-controls.json',controls),('replays.json',replays)]:dump(HERE/name,value)
 dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
  'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/exact-bank-request-conformance-20261026/verify.py',
  'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic',
  'wall_seconds':time.monotonic()-start,'data_version':sha(lock_path),'plan_file':'docs/plans/accounting-exact-bank-request-conformance-20261026.md',
  'result_file':str((HERE/'result.md').relative_to(ROOT)),'artifact_paths':['examples/','request-bytes/','comparisons.json','checks.json','adverse-controls.json'],
  'implementation_sha256':{'fixtures':sha(HERE/'fixtures.py'),'verifier':sha(Path(__file__))},'timestamp_utc':datetime.now(timezone.utc).isoformat()})
 print(json.dumps(checks),flush=True)
if __name__=='__main__':main()
