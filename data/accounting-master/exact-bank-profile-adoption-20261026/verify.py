"""Complete deterministic profile conversion, replay and timing conformance."""
from migrate import *
from datetime import datetime,timezone
from collections import Counter
import subprocess,sys,time
from datetime import date
import adapted_methods

def dump(name,value):
 (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
def outcome(fn):
 try:fn();return 'accepted'
 except n.Refusal as exc:return exc.code
def check(ok,label):
 if not ok:raise AssertionError(label)
def digest(path):return n.sha(Path(path).read_bytes())

class NativeTimeComparator(Auditor):
 # Diagnostic ablation: successor identity checks, pinned old time consumers.
 # It is not the old profile or a second independently implemented evaluator.
 information=n.Auditor.information
 expected_capital=n.Auditor.expected_capital
 expected_loss=n.Auditor.expected_loss

def verify_exchange(f,ex,expected):
 a=f.a;snapshot=n.sha(n.enc(a.reg));world=deepcopy(ex['world_before'])
 check(outcome(lambda:a.request(f.rq,f.sub,world))==expected,f.name+':request')
 a.response(ex)
 check(n.sha(n.enc(a.reg))==snapshot and ex['world_before']==world,'auditor_mutation')
 for k in ('accounting_heads','journals','unrelated_owners'):
  check(ex['world_after'][k]==world[k],f.name+':accounting_effect')
 oldidx=f.template['world_after']['query_index']
 check(all(ex['world_after']['query_index'][k]==v for k,v in oldidx.items()),'old_query_changed')
 for h,r in f.old.reg.items():check(a.reg[h]==r,'old_record_changed')
 if expected=='accepted':
  old=f.old.body(f.template['response_ref']);new=a.body(ex['response_ref'])
  # Compare all saved output fields, statuses, obligations and coverage.
  check(new==f.walk(old),'complete_response_correspondence:'+f.name)
  oldout=f.old.body(old['payload']['result_refs'][0]);newout=a.body(new['payload']['result_refs'][0])
  check(newout==f.walk(oldout),'complete_output_correspondence:'+f.name)
  check(len(ex['world_after']['query_index'])==len(oldidx)+1,'publication_count')
  replay=f.replay();a.response(replay);f.packet['replay']=replay
 else:check(ex['world_after']==world,'refusal_mutated_world')
 f.save()
 return {'case':f.name,'operation':a.body(f.rq)['operation'],'expected':expected,
  'disposition':a.body(ex['response_ref'])['disposition'],'records':len(f.packet['records']),
  'full_response_checked':True,'old_queries_preserved':True,'accounting_unchanged':True}

def main():
 start=time.monotonic();lock=json.loads((HERE/'source-lock.json').read_text())
 for p,h in lock.items():check(digest(ROOT/p)==h,'protected:'+p)
 native=(prior.ATT/'inputs/verify_exchanges.py').read_text()
 block=native[native.index(' def expected_capital('):native.index(' def expected_policy(')]
 check(block.count("instant(self.body(v)['decision_at']).date()")==2,'date_owner_inventory')
 block=block.replace("instant(self.body(v)['decision_at']).date()","utc_day(self.body(v)['decision_at'])")
 block='\n'.join(x[1:] if x.startswith(' ') else x for x in block.splitlines())+'\n'
 check((HERE/'adapted_methods.py').read_text().split('def expected_capital(',1)[1]==block.split('def expected_capital(',1)[1],'financial_methods_exact_preservation')
 check(adapted_methods.utc_day('2026-04-01T00:00:00.000000000000000001+01:00')==date(2026,3,31),'utc_day_previous_date')
 check(adapted_methods.utc_day('2026-03-31T23:59:59.999999999999999999-01:00')==date(2026,4,1),'utc_day_next_date')
 old=n.Auditor(prior.ATT);publications=[e for e in old.packet['exchanges'] if e['role']=='publication']
 check(len(publications)==33,'retained_publication_count')
 ordinary=[];fixtures={}
 for ex in publications:
  f=Migration(ex['id']);ordinary.append(verify_exchange(f,f.build(),'accepted'));fixtures[f.name]=f
 print(json.dumps({'phase':'ordinary_publications','passed':len(ordinary),'families':dict(Counter(x['operation'] for x in ordinary))}),flush=True)
 base={k:'2026-04-01T00:00:00.0000001Z' for k in ('available_at','ingested_at','decision_at','system_asof')}
 cases=[('equal',{},'accepted','accepted'),
  ('later-availability',{'available_at':'2026-04-01T00:00:00.0000002Z'},'later_information','accepted'),
  ('later-ingestion',{'ingested_at':'2026-04-01T00:00:00.0000002Z'},'later_ingestion','accepted'),
  ('offset-equivalent',{'available_at':'2026-04-01T01:00:00.0000001+01:00'},'accepted','accepted'),
  ('precision-limit',{'available_at':'2026-04-01T00:00:00.0000001000000000001Z'},'exact_time_unsupported:fraction_precision_limit','accepted'),
  ('unknown-offset',{'available_at':'2026-04-01T00:00:00.0000001-00:00'},'exact_time_unsupported:unknown_negative_zero_offset','accepted'),
  ('decision-precision-limit',{'decision_at':'2026-04-01T00:00:00.0000001000000000001Z'},'exact_time_unsupported:fraction_precision_limit','accepted'),
  ('system-precision-limit',{'system_asof':'2026-04-01T00:00:00.0000001000000000001Z'},'exact_time_unsupported:fraction_precision_limit','accepted'),
  ('eighteenth-digit',{**{k:'2026-04-01T00:00:00.123456789123456788Z' for k in base},
   'available_at':'2026-04-01T00:00:00.123456789123456789Z'},'later_information','accepted'),
  ('utc-day-equivalent',{'decision_at':'2026-04-02T00:30:00+01:00','system_asof':'2026-04-02T00:30:00+01:00'},'accepted','accepted')]
 timing=[]
 for template in ['capital.final','loss.original','policy.describe']:
  for name,change,expected,previous in cases:
   f=Migration(template,template+'.'+name,{**base,**change});ex=f.build(None if expected=='accepted' else expected)
   comparator=NativeTimeComparator(f.packet)
   actual=outcome(lambda:comparator.request(f.rq,f.sub,f.before))
   check(actual==previous,f.name+':native_comparator:'+actual)
   row=verify_exchange(f,ex,expected);row['pinned_native_time_comparator']=actual
   timing.append(row);fixtures[f.name]=f
 print(json.dumps({'phase':'timing_cases','passed':len(timing)}),flush=True)
 controls=[];f=fixtures['capital.final'];a=f.a;ex=f.exchange
 def refused(label,call,code):
  actual=outcome(call);check(actual==code,label+':'+actual+':expected:'+code)
  controls.append({'case':label,'reason':actual})
 for template in ['capital.final','loss.original','policy.describe']:
  g=fixtures[template]
  refused(template+'.old-request-before-replay',lambda:g.a.request(g.rq_old,g.sub_old,g.template['world_after']),'successor_request_schema')
  bad=deepcopy(g.before);bad['query_index'][g.a.identity(g.rq)]=deepcopy(next(iter(g.template['world_after']['query_index'].values())))
  refused(template+'.old-cache-under-new-identity',lambda:g.a.request(g.rq,g.sub,bad),'request_identity_conflict')
  refused(template+'.old-auditor-rejects-successor',lambda:g.old.shape(g.a.record(g.rq),g.rq['digest']),'record_schema_mismatch')
  # Replay remains available despite later freshness/head drift.
  replay=deepcopy(g.packet['replay']);world=replay['world_before'];world['current_view_ref']=g.a.legacy_profile
  for head in world['accounting_heads'].values():head['generation']+=1
  replay['world_after']=deepcopy(world);g.a.response(replay)
  controls.append({'case':template+'.replay-before-freshness','reason':'accepted'})
 refused('wrong-submission-bytes',lambda:a.request(f.rq,f.sub_old,f.before),'submission_bytes_mismatch')
 world=deepcopy(f.before);world['current_view_ref']=a.legacy_profile
 refused('stale-view',lambda:a.request(f.rq,f.sub,world),'stale_view')
 world=deepcopy(f.before);next(iter(world['accounting_heads'].values()))['generation']+=1
 refused('stale-head',lambda:a.request(f.rq,f.sub,world),'stale_accounting_head')
 rq=f.clone(f.rq,request_id='missing-head',expected_head=None);sub=f.submission(rq,'missing-head')
 refused('missing-head',lambda:a.request(rq,sub,f.before),'expected_head_required')
 # Use a second signature inside this packet, preserving independently named requests.
 foreign=f.derive(fixtures['loss.original'].old.body(fixtures['loss.original'].rq_old)['signature_ref'])
 rq=f.clone(f.rq,signature_ref=foreign);sub=f.submission(rq,'wrong-signature')
 cached=deepcopy(ex['world_after']);cached['query_index'][a.identity(rq)]['request_digest']=rq['digest']
 refused('wrong-signature-before-cache',lambda:a.request(rq,sub,cached),'signature_mismatch')
 rq=f.clone(f.rq,execution={**a.body(f.rq)['execution'],'budget':{'operation_count':999,'elapsed_seconds':60}});sub=f.submission(rq,'conflict')
 refused('same-identity-different-bytes',lambda:a.request(rq,sub,ex['world_after']),'request_identity_conflict')
 bad=deepcopy(ex);bad['world_after']['journals'].append({'forged':'posting'})
 refused('false-accounting-publication',lambda:a.response(bad),'non_atomic_or_accounting_publication')
 bad=deepcopy(ex);bad['world_after']['query_index'].pop(a.identity(f.rq))
 refused('missing-query-index',lambda:a.response(bad),'non_atomic_or_accounting_publication')
 g=fixtures['capital.final.later-availability'];bad=deepcopy(g.exchange);bad['world_after']['published_records'].append(bad['response_ref']['digest'])
 refused('refusal-publishes',lambda:g.a.response(bad),'refusal_changed_world')
 bad=deepcopy(g.exchange);b=deepcopy(g.a.body(bad['response_ref']));b['diagnostics'][0]['code']='later_ingestion';bad['response_ref']=g.clone(bad['response_ref'],**b)
 refused('wrong-refusal-reason',lambda:g.a.response(bad),'wrong_refusal')
 # Validly hashed but semantically stale schema/contract locks must still fail.
 profile=a.body(a.alias['profile']);original_lock=f.old.body(f.old.body(f.old.alias['profile'])['schema_lock_ref'])
 for field,code in [('schema_blob','successor_schema_lock_mismatch'),('semantic_contract_blob','successor_contract_lock_mismatch')]:
  lockref=f.clone(profile['schema_lock_ref'],**{field:original_lock[field]})
  pref=f.clone(a.alias['profile'],schema_lock_ref=lockref)
  packet=deepcopy(f.packet);packet['aliases']['profile']=pref;auditor=Auditor(packet)
  refused('stale-'+field,lambda:auditor.request(f.rq,f.sub,ex['world_after']),code)
 # A valid alternate profile cannot relabel the active request, even on replay.
 alternate=f.clone(a.alias['profile']);packet=deepcopy(f.packet);packet['aliases']['profile']=alternate;auditor=Auditor(packet)
 refused('alternate-profile-on-replay',lambda:auditor.request(f.rq,f.sub,ex['world_after']),'successor_request_profile')
 packet=deepcopy(f.packet);h=next(iter(f.old.reg));packet['records'][h]=deepcopy(f.old.reg[h]);packet['records'][h]['key']+='tampered'
 refused('immutable-record-collision',lambda:Auditor(packet),'immutable_record_collision')
 # Decoder identity is checked even on replay.
 refused('invalid-decoder-encoding',lambda:f.clone(a.alias['decoder'],canonical_encoding='wrong'),'closed_record_shape')
 # A separately identified decoder with the same semantics remains compatible.
 decoder=f.clone(a.alias['decoder']);sub=f.clone(f.sub,decoder_ref=decoder)
 check(a.body(decoder)==a.body(a.alias['decoder']),'decoder_same_semantics')
 a.request(f.rq,sub,ex['world_after'])
 controls.append({'case':'equivalent-decoder-description','reason':'accepted'})
 reloaded=0
 for row in ordinary+timing:
  packet=json.loads((HERE/'examples'/(row['case']+'.json')).read_text())
  check(digest(ROOT/packet['base_packet'])==packet['base_packet_sha256'],'saved_base_packet')
  fresh=Auditor(packet)
  for h,r in packet['records'].items():fresh.shape(r,h)
  fresh.response(packet['exchange'])
  if 'replay' in packet:fresh.response(packet['replay'])
  reloaded+=1
 for p,h in lock.items():check(digest(ROOT/p)==h,'protected_after:'+p)
 checks={'passed':True,'retained_publications':len(ordinary),'operation_families':3,'timing_cases':len(timing),
  'repaired_timing_outcomes':sum(x['expected']!=x['pinned_native_time_comparator'] for x in timing),
  'exact_replays':sum(x['expected']=='accepted' for x in ordinary+timing),'adverse_and_replay_controls':len(controls),
  'saved_packages_revalidated':reloaded,'protected_files':len(lock),'documentary_profile_adoption':True,
  'financial_method_source_preserved':True,'utc_day_boundary_checks':2,
  'general_migration':False,'source_admission':False,'accounting_admission':False,'forecast_admission':False,
  'runtime_executed':False,'product_ready':False}
 for name,value in [('checks.json',checks),('ordinary-comparisons.json',ordinary),('timing-comparisons.json',timing),('controls.json',controls)]:dump(name,value)
 dump('run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
  'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/exact-bank-profile-adoption-20261026/verify.py',
  'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','data_version':digest(HERE/'source-lock.json'),
  'random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'plan_file':'docs/plans/accounting-exact-bank-profile-adoption-20261026.md',
  'result_file':str((HERE/'result.md').relative_to(ROOT)),'artifacts':['checks.json','ordinary-comparisons.json','timing-comparisons.json','controls.json','examples/','request-bytes/'],
  'implementation_sha256':{p:digest(HERE/p) for p in ['migrate.py','successor.py','adapted_methods.py','verify.py','record-schemas.json','semantic-contract.md']},
  'timestamp_utc':datetime.now(timezone.utc).isoformat()})
 print(json.dumps(checks),flush=True)
if __name__=='__main__':main()
