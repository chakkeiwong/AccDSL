from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys,time
import common_text as t
from source_export import from_program
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
PRIOR=HERE.parent/'authored-event-contract-20261026'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+NL)
def check(ok,label):
 if not ok:raise AssertionError(label)
def ready(source,resources):
 result=t.compile_text(source,resources)
 check(result['status']=='compiled_structural','compile:'+result.get('reason',''))
 return result
def changed_body(body,index,name,value):
 b=deepcopy(body);identity=b['commands'][index]['event']['id']
 b['event_contract']['intents'][identity]['inputs'][name]['value']=value
 b['expected_event_contract_sha256']=t.digest(b['event_contract']);return b
def main():
 started=time.monotonic();out=HERE/'examples';out.mkdir(exist_ok=True)
 lock=json.loads((HERE.parent/'common-program-authoring-audit-20261026/source-lock.json').read_text())
 for p in [HERE.parent/'common-program-authoring-audit-20261026'/n for n in ['inventory.py','design.md','result.md','field-ownership.json','checks.json']]:lock[str(p.relative_to(ROOT))]=sha(p)
 for name,h in lock.items():check(sha(ROOT/name)==h,'protected:'+name)
 dump(HERE/'source-lock.json',lock)
 comparisons=[];saved={}
 for owner in ['alpha','beta']:
  b=json.loads((PRIOR/'examples'/f'{owner}.program.json').read_text())
  expected=json.loads((PRIOR/'examples'/f'{owner}.result.json').read_text())
  source,resources=from_program(b);compiled=ready(source,resources);check(compiled['program']==b,owner+':program')
  actual=t.execute_text(source,resources)
  check(actual==expected,owner+':full_saved_result')
  check(len(actual['trace'])==11,owner+':command_count')
  encoded=source.encode()
  for span in compiled['source_spans']:
   check(sha256(encoded[span['byte_start']:span['byte_end']]).hexdigest()==span['slice_sha256'],'source_span')
  for block in compiled['method_spans']:
   check(sha256(encoded[block['byte_start']:block['byte_end']]).hexdigest()==block['source_sha256'],'method_span')
   for span in block['declarations']:check(sha256(encoded[span['byte_start']:span['byte_end']]).hexdigest()==span['slice_sha256'],'nested_span')
  dump(out/f'{owner}.compiled.json',compiled);dump(out/f'{owner}.result.json',actual)
  (out/f'{owner}.acc').write_bytes(source.encode());dump(out/f'{owner}.resources.json',resources)
  comparisons.append({'company':owner,'commands':11,'entire_typed_program_equal':True,'entire_saved_runtime_result_equal':True,'all_byte_spans_checked':True})
  saved[owner]=(b,source,resources,actual)
 print(json.dumps({'phase':'full_program_comparisons','passed':True,'commands':22}),flush=True)
 b,source,resources,baseline=saved['alpha'];failures=[]
 def refused(label,s,r=resources,reason=None):
  actual=t.compile_text(s,r);check(actual['status']=='invalid',label+':accepted')
  if reason:check(reason in actual['reason'],label+':'+actual['reason'])
  failures.append({'case':label,'status':actual['status'],'reason':actual['reason'],'stage':actual['stage'],'location':actual['location']})
 refused('missing-resource',source,{k:v for i,(k,v) in enumerate(resources.items()) if i!=0},'missing_resource')
 extra=deepcopy(resources);extra[t.digest({'unused':True})]={'unused':True};refused('extra-resource',source,extra,'exact_resource_population')
 tampered=deepcopy(resources);h=t.digest(b['opening']);tampered[h]['name']='tampered';refused('changed-resource',source,tampered,'resource_digest')
 refused('wrong-target',source.replace(t.contracted.PROFILE,'UnknownProgram/1',1),reason='target_profile')
 first=next(x for x in source.splitlines() if x.startswith('clock '))
 refused('duplicate-clock',source.replace(first,first+NL+first,1),reason='duplicate_field')
 first=next(x for x in source.splitlines() if x.startswith('supplied_input '));refused('duplicate-input-declaration',source.replace(first,first+NL+first,1),reason='duplicate_field')
 first=next(x for x in source.splitlines() if x.startswith('intent_input '));refused('duplicate-intent-input',source.replace(first,first+NL+first,1),reason='duplicate_field')
 refused('missing-full-intent',NL.join(x for x in source.splitlines() if not x.startswith(('intent ','intent_input ')))+NL,reason='full_intent_required')
 first=next(x for x in source.splitlines() if x.startswith('intent_input "customer"'));refused('missing-full-field',source.replace(first+NL,'',1),reason='exact_full_intent_inputs')
 refused('unknown-registry',source.replace('registry "registry_1" method','registry "absent" method',1),reason='unknown_registry_alias')
 refused('missing-method-end',source.replace('end_method_source;','',1),reason='method')
 refused('missing-program-end',source.replace('end_program;',''),reason='incomplete_program')
 refused('trailing-declaration',source+'clock "direct_event_date";'+NL,reason='declaration_after_end')
 refused('bom',chr(65279)+source,reason='bom')
 refused('bare-cr',source+chr(13),reason='carriage')
 refused('control-character',source+chr(11),reason='source_control')
 refused('oversize-source',source+' '*(t.core.MAX_BYTES+1),reason='source_size_limit')
 malformed_method=source.replace('account_map ', 'bad_method_field ',1)
 refused('method-error-location',malformed_method,reason='unknown_declaration')
 loc=failures[-1]['location']
 check(malformed_method.splitlines()[loc['line']-1].startswith('bad_method_field '),'method_error_line')
 # Exact original intent is edited in source, with the same native refusal.
 runtime=[]
 for owner,(b,s,res,base_result) in saved.items():
  for name,value,status,reason in [('customer',t.base.known('Different customer'),'invalid','claim_customer_mismatch'),
    ('customer',{'status':'unknown','reason':'unobserved'},'unresolved','unknown_event_inputs'),
    ('approved',t.base.known(False),'unsupported','applicability_not_selected')]:
   changed=changed_body(b,1,name,value);src,rs=from_program(changed);actual=t.execute_text(src,rs)
   typed=t.contracted.run(changed);native=t.contracted.contract.native.run(t.contracted.contract.native_body(changed))
   check(actual==typed,'refusal_typed_equality');stop=actual.get('stop') or {}
   check(stop.get('index')==1 and stop.get('status')==status and reason in stop.get('reason',''),'native_refusal:'+reason)
   check(actual['current']==native['current'] and actual['trace']==base_result['trace'][:1],'refused_prefix')
   check(actual['remaining_commands']==changed['commands'][1:],'remaining_commands')
   runtime.append({'company':owner,'case':reason,'status':status,'full_typed_equal':True,'native_current_equal':True,'prefix_equal':True})
 b,source,resources,baseline=saved['alpha']
 # Direct source algorithm edit: no typed builder or cached result creates it.
 bounded=deepcopy(b);bounded['commands']=bounded['commands'][:2]
 ids={x['event']['id'] for x in bounded['commands']};bounded['event_contract']['intents']={k:v for k,v in bounded['event_contract']['intents'].items() if k in ids}
 bounded['expected_event_contract_sha256']=t.digest(bounded['event_contract']);s,res=from_program(bounded)
 start=s.index('entry "collect";');begin=s.index('begin_monetary ',start);end=s.index('end_monetary;',begin)
 entry=bounded['registries'][bounded['commands'][1]['registry_sha256']]['entries']['collect']
 scalar=deepcopy(entry['method']['monetary']['definition']['inputs']['amount']['type']);scalar['dimensions']={}
 replacement='(mul (ref "amount") (const '+json.dumps(scalar,sort_keys=True,separators=(',',':'))+' "1/2"))'
 edited=s[:begin]+s[begin:end].replace('(ref "amount")',replacement)+s[end:]
 compiled=ready(edited,res);contract_result=t.execute_text(edited,res)
 check(contract_result['stop']['index']==1 and contract_result['stop']['reason']=='selected_method_intent_mismatch','edited_contract_refusal')
 lines=edited.splitlines(keepends=True);guard_lines=[];inside=False
 for line in lines:
  if line.startswith('select_event_contract '):inside=True;continue
  if inside:
   if line.strip()=='end_event_contract;':inside=False
   continue
  if line.startswith(('intent ','intent_input ')):continue
  guard_lines.append(line.replace(t.contracted.PROFILE,t.guarded.PROFILE) if line.startswith('company_program ') else line)
 guarded_source=''.join(guard_lines);guard_compiled=ready(guarded_source,res);actual=t.execute_text(guarded_source,res)
 check(actual['status']=='complete_provisional','edited_guard_completion')
 check(actual['current']['balances']['cash']=='105/1' and actual['current']['balances']['receivables']=='25/1','edited_algorithm_balances')
 check(actual['current']['memory']['claims']['invoice/a~1']['remaining']=='25/1','edited_algorithm_memory')
 (out/'alpha.half-collection.guarded.acc').write_bytes(guarded_source.encode());dump(out/'alpha.half-collection.guarded.result.json',actual)
 (out/'alpha.half-collection.contracted.acc').write_bytes(edited.encode());dump(out/'alpha.half-collection.resources.json',res)
 # Unicode and CRLF are checked against the actual bytes, including method bodies.
 unicode_source=source.replace('authored-alpha','公司-é',1).replace('Explicit synthetic lifecycle premise','明确事实 é')
 crlf=unicode_source.replace(NL,chr(13)+NL);compiled=ready(crlf,resources);encoded=crlf.encode()
 for span in compiled['source_spans']:
  check(sha256(encoded[span['byte_start']:span['byte_end']]).hexdigest()==span['slice_sha256'],'crlf_outer_span')
 for block in compiled['method_spans']:
  check(sha256(encoded[block['byte_start']:block['byte_end']]).hexdigest()==block['source_sha256'],'crlf_method_span')
  for span in block['declarations']:check(sha256(encoded[span['byte_start']:span['byte_end']]).hexdigest()==span['slice_sha256'],'crlf_nested_span')
 # Report notes remain field-for-field; missing evidence stays explicitly missing.
 changed=deepcopy(b);changed['commands'][3]['notes']=[{'id':'missing-evidence','label':'Customer data','status':'missing','reason':'Not disclosed'}]
 s,res=from_program(changed);check(ready(s,res)['program']==changed,'report_note_preserved')
 check(t.execute_text(s,res)==t.contracted.run(changed),'report_note_result')
 # Invalid command after a multibyte prefix keeps a true byte location.
 malformed=unicode_source.replace('input "approved" known true','input "approved" known 1',1)
 refused('bad-command-multibyte',malformed,reason='string_or_boolean_required')
 loc=failures[-1]['location'];lines=malformed.splitlines(keepends=True)
 check(loc['byte_start']==len(''.join(lines[:loc['line']-1]).encode()),'error_byte_origin')
 for name,h in lock.items():check(sha(ROOT/name)==h,'protected_after:'+name)
 checks={'passed':True,'companies':2,'complete_commands_equal':22,'compile_refusals':len(failures),'matched_runtime_refusals':len(runtime),
  'direct_source_algorithm_edit':True,'selected_contract_rejects_changed_algorithm':True,'all_byte_spans_checked':True,
  'unicode_crlf_checked':True,'report_note_preserved':True,'protected_files':len(lock),'general_invariant_authoring':False,'admission':False}
 for name,v in [('checks.json',checks),('comparisons.json',comparisons),('compile-refusals.json',failures),('runtime-refusals.json',runtime)]:dump(HERE/name,v)
 dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
  'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/common-program-authoring-20261026/verify.py',
  'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-started,
  'data_version':sha(HERE/'source-lock.json'),'plan_file':'docs/plans/accounting-common-program-authoring-20261026.md',
  'result_file':str((HERE/'result.md').relative_to(ROOT)),'artifact_paths':['checks.json','examples/','compile-refusals.json','runtime-refusals.json'],
  'implementation_sha256':{'parser':sha(HERE/'common_text.py'),'export':sha(HERE/'source_export.py'),'verifier':sha(Path(__file__))},'timestamp_utc':datetime.now(timezone.utc).isoformat()})
 print(json.dumps(checks),flush=True)
if __name__=='__main__':main()
