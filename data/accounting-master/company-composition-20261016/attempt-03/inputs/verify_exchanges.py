"""Independent documentary audit; imports no builder or authored expectations."""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as F
import hashlib,json,subprocess,sys,time,re
from jsonschema import Draft202012Validator,FormatChecker
from financial_checks import derive,report,invariant
from migration_design import SPECS,projection,target_step,map_closed_result,projection_schema,rational
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
class Refusal(Exception):
 def __init__(self,code,status='rejected'):self.code=code;self.status=status;super().__init__(code)
def need(ok,code,status='rejected'):
 if not ok:raise Refusal(code,status)
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def pairs(items):
 d={}
 for k,v in items:need(k not in d,'duplicate_key');d[k]=v
 return d
def no_float(v):raise Refusal('float_forbidden')
def decode(raw):return json.loads(raw,object_pairs_hook=pairs,parse_float=no_float,parse_constant=no_float)
def references(v):
 if isinstance(v,dict):
  if set(v)=={'kind','schema','digest'}:yield v
  else:
   for x in v.values():yield from references(x)
 elif isinstance(v,list):
  for x in v:yield from references(x)
def numbers(v):
 if isinstance(v,str) and re.fullmatch(r'-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?',v):need(str(F(v))==v,'noncanonical_rational')
 elif isinstance(v,dict):
  for x in v.values():numbers(x)
 elif isinstance(v,list):
  for x in v:numbers(x)
class Auditor:
 def __init__(self,path):
  self.path=path;self.packet=json.loads((path/'portable-exchanges.json').read_text());self.reg=self.packet['record_registry'];self.alias=self.packet['aliases'];self.schema=json.loads((path/'record-schemas.json').read_text());self.checks=[]
 def audit(self,label,fn):
  try:fn();self.checks.append(dict(label=label,passed=True))
  except Exception as e:self.checks.append(dict(label=label,passed=False,error=type(e).__name__+': '+str(e)))
 def expected(self,fn,code,status=None):
  try:fn()
  except Refusal as e:need(e.code==code and (status is None or e.status==status),'wrong_refusal:'+e.code);return
  raise Refusal('missing_refusal:'+code)
 def record(self,r):
  need(r['digest'] in self.reg,'missing_reference');a=self.reg[r['digest']];need((r['kind'],r['schema'])==(a['kind'],a['schema']),'reference_kind_schema');return a
 def decode_request(self,raw):
  r=decode(raw);self.shape(r);need(r['kind']=='Request','not_a_request')
  need(raw==enc(r),'noncanonical_request_bytes')
  d=sha(('accdsl.portable.v1/'+r['schema']).encode()+b'\0'+raw)
  need(d in self.reg and self.reg[d]==r,'request_record_mismatch')
  return {'kind':r['kind'],'schema':r['schema'],'digest':d}
 def body(self,r):return self.record(r)['body']
 def closure(self,roots):
  found=set();active=set()
  def visit(r):
   d=r['digest'];need(d not in active,'cyclic_reference')
   if d in found:return
   active.add(d)
   for x in self.record(r)['dependencies']:visit(x)
   active.remove(d);found.add(d)
  for r in roots:visit(r)
  return sorted(found)
 def shape(self,r,d=None):
  need(set(r)=={'kind','schema','key','body','dependencies'},'record_shape');need(r['kind'] in self.schema['$defs'],'unknown_kind')
  need(r['schema']==self.schema['schema_ids'][r['kind']],'record_schema')
  errors=list(Draft202012Validator(self.schema['$defs'][r['kind']],format_checker=FormatChecker()).iter_errors(r['body']))
  need(not errors,'closed_record_shape:'+(';'.join(str(e.message) for e in errors[:2])))
  numbers(r['body']);deps={enc(x):x for x in references(r['body'])}
  need(r['dependencies']==[deps[k] for k in sorted(deps)],'dependency_mismatch')
  for x in deps.values():self.record(x)
  if d:need(sha(('accdsl.portable.v1/'+r['schema']).encode()+b'\0'+enc(r))==d,'record_digest')
 def preservation(self):
  lock=json.loads((HERE/'predecessor-lock.json').read_text());orig=ROOT/lock['original_protection_manifest']
  need(sha(orig.read_bytes())==lock['original_manifest_sha256'],'original_manifest_changed')
  for item in json.loads(orig.read_text())['files']:
   for key in ['path','snapshot']:need(sha((ROOT/item[key]).read_bytes())==item['sha256'],'original_changed:'+item[key])
  for item in lock['predecessor_files']:need(sha((ROOT/item['path']).read_bytes())==item['sha256'],'predecessor_changed:'+item['path'])
  need(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==lock['git_commit'],'head_changed')
  raw=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
  need(sha(raw)==lock['index_sha256'] and len(raw.splitlines())==lock['index_entries'],'staged_diff_changed')
 def sources(self):
  for d,b in self.packet['blobs'].items():
   raw=(ROOT/b['path']).read_bytes();need(sha(raw)==d==b['sha256'] and len(raw)==b['byte_length'],'blob_mismatch')
  for name,b in self.packet['input_snapshots'].items():need(sha((ROOT/b['path']).read_bytes())==b['sha256'],'input_snapshot_changed')
  p=self.body(self.alias['profile']);lock=self.body(p['lock']);source=self.body(p['source'])
  need(p['name']=='CompanyComposition/1' and p['execution']=='documentary_only' and p['sector']=='nonfinancial_corporate','profile_scope')
  need(lock['schema']['path']==str((self.path/'record-schemas.json').relative_to(ROOT)) and lock['contract']['path']==str((self.path/'inputs/semantic-contract.md').relative_to(ROOT)),'profile_lock')
  need(source['pdf']['sha256']=='e4fde71d4db44ef7c6c74055a564c8cb071340442b63185ff1700c86a64579e5','source_pdf_identity')
  need(source['text']['sha256']=='37f207b1ecdde43e3971cf076f127576d3d7810c791385ba5b1c35f110f17664','source_text_identity')
  need(source['status']=='historical_conditional_not_current_admission','source_scope')
 def effects(self,br):
  b=self.body(br);need(b['profile']==self.alias['profile'] and self.body(b['view'])['profile']==b['profile'],'basis_binding')
  return derive(self.body(b['opening']),self.body(b['event']),need)
 def authorization(self,ar,br):
  a=self.body(ar);need(a==dict(basis=br,posting_permitted=True,facts='supplied_synthetic'),'authorization_mismatch')
 def proposal(self,p):
  self.authorization(p['authorization'],p['basis']);z,j,c=self.effects(p['basis'])
  need(self.body(p['closing'])==z and p['journals']==j and p['cash']==c,'proposal_financial_mismatch')
 def report_check(self,args,candidate):
  expected={k:args[k] for k in ['opening','closing','start','end']}
  g,l=report(self.body(args['opening']),self.body(args['closing']),args['start'],args['end'],need)
  expected.update(group=g,legal=l,scope='joined_finite_company_conditional');need(candidate==expected,'report_financial_mismatch')
 def world_shape(self,w):
  need(set(w)=={'head','view','receipts','proposals','decisions','published','unaffected'},'world_shape')
  need(w['published']==sorted(set(w['published'])),'world_publication_order')
  need(set(self.closure([w['head'],w['view']]))<=set(w['published']),'head_unpublished')
  need(len(w['receipts'])==len(w['proposals'])==len(w['decisions']),'world_effect_count')
  for r in references(w):self.record(r)
 def atomic(self,t,candidate):
  before=t['before'];rq=self.body(t['request']);p=self.body(rq['arguments']['proposal']);out=self.body(t['result'])['outputs'][0];r=self.body(out)
  self.proposal(p);need(r==dict(request=t['request'],proposal=rq['arguments']['proposal'],opening=before['head'],closing=p['closing'],generation=self.body(p['closing'])['sequence']),'receipt_mismatch')
  expected=deepcopy(before);expected['head']=p['closing'];expected['receipts'].append(out);expected['proposals'].append(rq['arguments']['proposal'])
  expected['decisions'][rq['identity']]=dict(request=t['request'],result=t['result'],receipt=out)
  expected['published']=sorted(set(expected['published'])|set(self.closure([out,t['result']])))
  need(candidate==expected,'atomic_publication_mismatch')
 def dispatch(self,r,w):
  q=self.body(r);need(q['profile']==self.alias['profile'],'profile_mismatch');stored=w['decisions'].get(q['identity'])
  if stored:
   need(stored['request']==r,'identity_conflict')
   need(stored['receipt'] in w['receipts'] and set(self.closure([stored['receipt'],stored['result']]))<=set(w['published']),'stored_decision_unpublished')
   return 'replayed',stored['result']
  need(q['head']==w['head'],'stale_head');need(q['view']==w['view'],'stale_view')
  args=q['arguments'];op=q['operation']
  if op=='report':
   need(set(self.closure([args['opening'],args['closing']]))<=set(w['published']),'report_unpublished')
   # Selected receipt chain must exactly connect the requested opening and closing.
   current=args['opening'];selected=0
   for t in self.packet['transitions']:
    prop=self.body(self.body(t['request'])['arguments']['proposal']);ev=self.body(self.body(prop['basis'])['event'])
    if args['start']<=ev['date']<args['end']:
     need(self.body(t['result'])['outputs'][0] in w['receipts'],'report_receipt_missing')
     need(self.body(prop['basis'])['opening']==current,'report_receipt_chain')
     current=prop['closing'];selected+=1
   need(selected>0 and current==args['closing'],'report_receipt_chain')
   report(self.body(args['opening']),self.body(args['closing']),args['start'],args['end'],need)
  else:
   br=args['basis'] if op!='commit' else self.body(args['proposal'])['basis'];b=self.body(br)
   need(b['opening']==q['head'] and b['view']==q['view'],'basis_head_view_mismatch');self.effects(br)
   if op=='propose':self.authorization(args['authorization'],br)
   if op=='commit':self.proposal(self.body(args['proposal']))
  return 'completed',None
 def exchange(self,e):
  self.world_shape(e['before']);self.world_shape(e['after']);rq=self.body(e['request']);res=self.body(e['result'])
  path=self.path/'bytes'/(self.record(e['request'])['key'].removeprefix('request.')+'.json')
  need(self.decode_request(path.read_bytes())==e['request'],'request_bytes_binding')
  need(res['request']==e['request'],'result_request_mismatch')
  if res['status']!='completed':
   self.expected(lambda:self.dispatch(e['request'],e['before']),res['diagnostic'],res['status']);need(e['before']==e['after'] and not res['outputs'],'refusal_mutation');return
  need(self.dispatch(e['request'],e['before'])[0]=='completed','dispatch_status');need(res['diagnostic'] is None and len(res['outputs'])==1,'completed_result')
  out=self.body(res['outputs'][0]);op=rq['operation']
  if op=='authorize':self.authorization(res['outputs'][0],rq['arguments']['basis'])
  elif op=='propose':
   need(out['basis']==rq['arguments']['basis'] and out['authorization']==rq['arguments']['authorization'],'proposal_request_binding');self.proposal(out)
  elif op=='commit':self.atomic(e,e['after']);return
  else:self.report_check(rq['arguments'],out)
  need(e['before']==e['after'],'read_mutation')
 def replay(self,x):
  status,result=self.dispatch(x['request'],x['later_world']);need(status=='replayed' and result==x['stored_result'],'replay_changed_result')
  self.expected(lambda:self.dispatch(x['conflicting_request'],x['later_world']),'identity_conflict')
 def recovery(self,x):
  need(x['transport_observation']=='commit_unknown','false_commit_observation')
  need(self.dispatch(x['request'],x['not_committed'])[0]=='completed','retry_no_commit')
  need(self.dispatch(x['request'],x['committed'])[0]=='replayed','retry_committed')
 def migration(self,m):
  key=m['subset'];old=json.loads((ROOT/m['source_packet']['path']).read_text());schema=json.loads((ROOT/m['source_schema']['path']).read_text())
  target_schema=json.loads((self.path/'migration-schemas.json').read_text())[key]
  need(target_schema==projection_schema(schema,key),'migration_schema_lock')
  for target in [m['projected'],m['expected_after']]:
   need(not list(Draft202012Validator(target_schema,format_checker=FormatChecker()).iter_errors(target)),'migration_closed_shape')
  projected=projection(old,m['source_state_ref'],key,need);need(projected==m['projected'],'migration_projection_mismatch')
  state=old['record_registry'][m['source_state_ref']['digest']]['body'];restored=deepcopy(state)
  restored['balances']={k:rational(0) for k in schema['$defs']['CompanyState']['properties']['balances']['properties']}
  for a,b in SPECS[key]['accounts'].items():restored['balances'][a]=rational(projected['balances'][b])
  need(restored==state,'migration_roundtrip_loss')
  result=target_step(projected,m['event'],need);need(result==m['expected_after']==map_closed_result(old,m['source_closing_ref'],key),'migration_noncommuting')
  # Unknown fields, nonzero omitted balance, foreign profile and unsupported method are real refusals.
  for change,code in [('field','migration_unknown_field'),('balance','migration_unmapped_balance'),('profile','migration_profile_unsupported')]:
   bad=deepcopy(old);s=bad['record_registry'][m['source_state_ref']['digest']]['body']
   if change=='field':s['hidden_state']='1'
   elif change=='profile':bad['profile']='Unknown/1'
   else:s['balances'][next(k for k in s['balances'] if k not in SPECS[key]['accounts'])]=rational(1)
   self.expected(lambda:projection(bad,m['source_state_ref'],key,need),code,'unsupported')
  bad=deepcopy(m['event']);bad['method_id']='unknown.method';self.expected(lambda:target_step(projected,bad,need),'migration_method_unsupported','unsupported')
 def challenge(self,c):
  kind=c['kind']
  if kind=='atomic':fn=lambda:self.atomic(next(t for t in self.packet['transitions'] if t['id']==c['transition']),c['candidate'])
  elif kind=='report':fn=lambda:self.report_check(self.body(c['request'])['arguments'],c['candidate'])
  elif kind=='proposal':fn=lambda:self.proposal(c['candidate'])
  elif kind=='opening':fn=lambda:invariant(c['candidate'],need)
  elif kind=='migration_target':fn=lambda:need(c['candidate']==next(m['projected'] for m in self.packet['migrations'] if m['subset']==c['subset']),'migration_projection_mismatch')
  else:raise Refusal('unknown_challenge')
  self.expected(fn,c['code'])
 def coverage(self):
  need(len(self.packet['transitions'])==13 and len(self.packet['recoveries'])==13 and len(self.packet['replays'])==13,'transition_coverage')
  need(len(self.packet['reports'])==3 and len(self.packet['migrations'])==2,'report_migration_coverage')
  methods={self.body(self.body(self.body(self.body(t['request'])['arguments']['proposal'])['basis'])['event'])['method'] for t in self.packet['transitions']}
  need(methods=={'compound.redeem','returns.settle','payroll.pay','ppe.depreciate','inventory.transfer','inventory.sell','intercompany.pay','tax.close','ownership.purchase'},'method_coverage')
  refused={self.body(self.body(self.body(e['request'])['arguments']['basis'])['event'])['method'] for e in self.packet['exchanges'] if self.body(e['result'])['status']!='completed'}
  need(refused==methods,'refusal_method_coverage')
  states=self.packet['states'];need(len(states)==14,'state_count')
  for i,t in enumerate(self.packet['transitions']):need(t['before']['head']==states[i] and t['after']['head']==states[i+1],'state_chain')
 def adverse_transport(self):
  t=self.packet['transitions'][0];w=deepcopy(t['before']);w['head']=self.packet['states'][1]
  self.expected(lambda:self.dispatch(t['request'],w),'stale_head')
  w=deepcopy(t['before']);w['view']=self.alias['view.later']
  self.expected(lambda:self.dispatch(t['request'],w),'stale_view')
  report_ex=self.packet['reports'][0];w=deepcopy(report_ex['before']);w['receipts']=[]
  self.expected(lambda:self.dispatch(report_ex['request'],w),'report_receipt_missing')
  w=deepcopy(t['after']);w['published']=t['before']['published']
  self.expected(lambda:self.dispatch(t['request'],w),'stored_decision_unpublished')
  raw=enc(self.record(t['request']))
  self.expected(lambda:self.decode_request(raw+b' '),'noncanonical_request_bytes')
  self.expected(lambda:numbers('2/2'),'noncanonical_rational')
  unknown=deepcopy(self.record(t['request']));unknown['body']['untyped_field']=True
  try:self.shape(unknown)
  except Refusal as e:need(e.code.startswith('closed_record_shape:'),'wrong_shape_refusal')
  else:raise Refusal('unknown_field_accepted')
 def run(self):
  self.audit('preservation',self.preservation)
  if not self.checks[-1]['passed']:return
  self.audit('source-and-input-locks',self.sources)
  for d,r in self.reg.items():self.audit('record:'+r['key'],lambda d=d,r=r:self.shape(r,d))
  for key,r in self.alias.items():self.audit('alias:'+key,lambda key=key,r=r:need(self.record(r)['key']==key,'alias_mismatch'))
  self.audit('full-reference-closure',lambda:self.closure(list(self.alias.values())))
  for e in self.packet['exchanges']:self.audit('exchange:'+e['id'],lambda e=e:self.exchange(e))
  for x in self.packet['replays']:self.audit('replay:'+self.body(x['request'])['identity'],lambda x=x:self.replay(x))
  for x in self.packet['recoveries']:self.audit('recovery:'+self.body(x['request'])['identity'],lambda x=x:self.recovery(x))
  for m in self.packet['migrations']:self.audit('migration:'+m['subset'],lambda m=m:self.migration(m))
  for c in self.packet['validation_challenges']:self.audit('challenge:'+c['id'],lambda c=c:self.challenge(c))
  self.audit('coverage',self.coverage)
  self.audit('adverse-transport-and-byte-boundaries',self.adverse_transport)
  self.audit('decoder-duplicate',lambda:self.expected(lambda:decode(b'{"a":1,"a":2}'),'duplicate_key'))
  self.audit('decoder-float',lambda:self.expected(lambda:decode(b'{"a":1.5}'),'float_forbidden'))
  self.audit('decoder-nonfinite',lambda:self.expected(lambda:decode(b'{"a":NaN}'),'float_forbidden'))
def main():
 start=time.monotonic();path=HERE/sys.argv[1];a=Auditor(path);a.run();failed=[x for x in a.checks if not x['passed']]
 n=1
 while (path/f'validation-{n:02}.json').exists():n+=1
 out=path/f'validation-{n:02}.json';result=dict(checks=a.checks,failed=len(failed),wall_seconds=time.monotonic()-start,
  packet_sha256=sha((path/'portable-exchanges.json').read_bytes()),verifier_sha256=sha(Path(__file__).read_bytes()),
  financial_sha256=sha((HERE/'financial_checks.py').read_bytes()),migration_sha256=sha((HERE/'migration_design.py').read_bytes()),
  environment='CPU-only; CUDA_VISIBLE_DEVICES=-1; no GPU frameworks imported',runtime_executed=False)
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(path=str(out.relative_to(ROOT)),checks=len(a.checks),failed=len(failed),failures=failed[:12])))
 raise SystemExit(bool(failed))
if __name__=='__main__':main()
