"""Full native-result and adversarial correspondence for explicit invariants."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys,time
import invariant_text as t
import program_text as p
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
COMMON=HERE.parent/'common-program-authoring-20261026'
AUDIT=HERE.parent/'authored-program-invariant-audit-20261026'
GUARDS=HERE.parent/'authored-state-invariants-20261026'
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def check(ok,label):
 if not ok:raise AssertionError(label)
def load(path):return json.loads(path.read_text())
def splice(source,text):
 a,b=source.split('begin_invariant_source;\n',1);_,c=b.split('end_invariant_source;\n',1)
 return a+'begin_invariant_source;\n'+text+'end_invariant_source;\n'+c
def spans(source,items):
 raw=source.encode()
 for loc in items:
  check(sha256(raw[loc['byte_start']:loc['byte_end']]).hexdigest()==loc['slice_sha256'],'source_span')

def main():
 started=time.monotonic();out=HERE/'examples';out.mkdir(exist_ok=True);lockfile=HERE/'source-lock.json'
 if not lockfile.exists():
  lock=load(COMMON/'source-lock.json')
  files=[COMMON/x for x in ['common_text.py','source_export.py','verify.py','checks.json','result.md']]
  files += list((COMMON/'examples').glob('*'))+list((AUDIT/'examples').glob('*.json'))
  files += [ROOT/'docs/plans/accounting-invariant-source-authoring-20261026.md',HERE/'design.md']
  for path in files:
   if path.is_file():lock[str(path.relative_to(ROOT))]=sha(path)
  dump(lockfile,lock)
 lock=load(lockfile)
 for name,h in lock.items():check(sha(ROOT/name)==h,'protected:'+name)
 ordinary=[];saved={}
 for owner in ['alpha','beta']:
  body=load(COMMON/'examples'/(owner+'.compiled.json'))['program'];source,resources=p.from_program(body)
  compiled=p.compile_text(source,resources);check(compiled['status']=='compiled_structural',compiled.get('reason'))
  check(compiled['program']==body,'full_program_equal');check(body['expected_invariant_sha256'] not in resources,'opaque_invariant_import')
  actual=p.execute_text(source,resources);expected=load(COMMON/'examples'/(owner+'.result.json'))
  check(actual==expected,'full_result_equal:'+owner)
  inv=t.render(body['state_invariant']);lowered=t.lower(inv);check(lowered['invariant']==body['state_invariant'],'typed_invariant_equal')
  spans(source,compiled['source_spans']);spans(source,compiled['invariant_source']['declarations'])
  for block in compiled['method_spans']:
   spans(source,block['declarations']);check(sha256(source.encode()[block['byte_start']:block['byte_end']]).hexdigest()==block['source_sha256'],'method_span')
  (out/(owner+'.acc')).write_text(source);(out/(owner+'.invariant.acc')).write_text(inv)
  dump(out/(owner+'.resources.json'),resources);dump(out/(owner+'.compiled.json'),compiled);dump(out/(owner+'.result.json'),actual)
  ordinary.append({'company':owner,'commands':len(actual['trace']),'full_program_equal':True,'full_result_equal':True,'source_bytes':len(source.encode()),'invariant_declarations':len(inv.splitlines())})
  saved[owner]=(body,source,resources,actual,inv)
 print(json.dumps({'phase':'ordinary_programs','commands':sum(x['commands'] for x in ordinary)}),flush=True)
 refused=[]
 for path in sorted((AUDIT/'examples').glob('*.json')):
  row=load(path);owner=row['comparison']['company'];body,_,_,_,_=saved[owner]
  bad=deepcopy(row['program']);bad['profile']=p.prior.guarded.PROFILE
  bad['state_invariant']=deepcopy(body['state_invariant']);bad['expected_invariant_sha256']=body['expected_invariant_sha256']
  source,resources=p.from_program(bad);actual=p.execute_text(source,resources);expected=p.prior.guarded.run(bad)
  check(actual==expected,'counterexample_full_result:'+path.stem)
  check(actual['status']=='stopped_provisional' and actual['trace']==[] and actual['current']==bad['opening'],'failed_prefix:'+path.stem)
  check(actual['stop']['stage']=='after' and actual['stop']['invariant']['status']=='invalid','counterexample_refusal:'+path.stem)
  (out/(path.stem+'.counterexample.acc')).write_text(source);dump(out/(path.stem+'.counterexample.resources.json'),resources);dump(out/(path.stem+'.counterexample.result.json'),actual)
  refused.append({'case':path.stem,'complete_result_equal':True,'prefix_length':0,'status':actual['stop']['status']})
 print(json.dumps({'phase':'retained_counterexamples','refused':len(refused)}),flush=True)
 body,source,resources,actual,inv=saved['alpha'];negatives=[]
 def invalid(label,text,expected,resource=resources,needle=None):
  result=p.compile_text(text,resource);check(result['status']=='invalid',label+':accepted')
  check(expected in result['reason'],label+':'+result['reason'])
  if needle is not None:
   loc=result['location'];check(loc is not None,label+':location_missing');raw=text.encode()
   check(needle.encode() in raw[loc['byte_start']:loc['byte_end']],label+':wrong_location:'+str(loc))
  negatives.append({'case':label,'reason':result['reason'],'location':result['location']})
 row=next(x for x in inv.splitlines(True) if x.startswith('global '))
 invalid('duplicate-global',splice(source,inv.replace(row,row+row,1)),'duplicate_declaration',needle='global ')
 row=next(x for x in inv.splitlines(True) if x.startswith('field '))
 invalid('duplicate-field',splice(source,inv.replace(row,row+row,1)),'duplicate_declaration',needle='field ')
 invalid('malformed-expression',splice(source,inv.replace('(le ','(mystery ',1)),'unknown_operator:mystery',needle='mystery')
 invalid('unbound-predicate',splice(source,inv.replace('(ref "remaining")','(ref "unbound")',1)),'undeclared',needle='end_rules')
 invalid('wrong-reference-field-type',splice(source,inv.replace('field "sale_event" {"context":{},"kind":"text"}','field "sale_event" {"context":{},"kind":"date"}',1)),'reference_type_or_context_mismatch',needle='end_invariant')
 invalid('missing-row-binding',splice(source,inv.replace(next(x for x in inv.splitlines(True) if x.startswith('row_binding ')),'')),'inexact_template_binding',needle='end_invariant')
 invalid('missing-total-binding',splice(source,inv.replace(next(x for x in inv.splitlines(True) if x.startswith('total_binding ')),'')),'inexact_total_bindings',needle='end_invariant')
 invalid('missing-rule-end',splice(source,inv.replace('end_rules;\n','',1)),'incomplete_rules')
 invalid('duplicate-block',source.replace('begin_invariant_source;','begin_invariant_source;\nbegin_invariant_source;',1),'exact_invariant_source_block')
 invalid('opaque-invariant-import',source,'inline_invariant_supplied_as_resource',{**resources,body['expected_invariant_sha256']:body['state_invariant']})
 invalid('oversized-source','x'*(t.core.MAX_BYTES+1),'source_size_limit')
 invalid('forbidden-control',source+chr(0),'source_control')
 invalid('code-instead-of-predicate',splice(source,inv.replace('(le ','(__import__ ',1)),'unknown_operator:__import__',needle='__import__')
 # A date-typed uniqueness rule is structurally legitimate. Binding it to
 # actual text map keys is invalid only when the native typed-book binder runs.
 badkey=splice(source,inv.replace('field "identity" {"context":{},"kind":"text"}','field "identity" {"context":{},"kind":"date"}',1))
 compiled=p.compile_text(badkey,resources);check(compiled['status']=='compiled_structural','key_rule_structure')
 bound=p.execute_text(badkey,resources);check(bound==p.prior.TARGETS[compiled['program']['profile']].run(compiled['program']),'typed_binding_result')
 check(bound['status']!='complete_provisional' and 'row_declaration_type' in json.dumps(bound),'typed_key_binding_refusal')
 # Different on-false semantics are authored in source and compared to typed intent.
 badcase=load(AUDIT/'examples/alpha.claim-total.json')['program'];variant=deepcopy(badcase)
 variant['profile']=p.prior.guarded.PROFILE;variant['state_invariant']=deepcopy(body['state_invariant'])
 variant['expected_invariant_sha256']=t.g.digest(variant['state_invariant']);vsource,vresources=p.from_program(variant)
 original_rule='guarded "claim_receivable_sum" invalid unresolved'
 check(original_rule in vsource,'variant_rule_found')
 vsource=vsource.replace(original_rule,'guarded "claim_receivable_sum" unsupported unresolved',1)
 typed=deepcopy(variant);typed['state_invariant']['definition']['assessment']['requirements'][0]['on_false']='unsupported'
 typed['expected_invariant_sha256']=t.g.digest(typed['state_invariant'])
 vactual=p.execute_text(vsource,vresources);check(vactual==p.prior.guarded.run(typed),'edited_rule_full_typed_result')
 check(vactual['trace']==[] and vactual['current']==typed['opening'] and vactual['stop']['status']=='unsupported','edited_rule_failed_prefix')
 (out/'alpha.edited-rule.acc').write_text(vsource);dump(out/'alpha.edited-rule.resources.json',vresources);dump(out/'alpha.edited-rule.result.json',vactual)
 # A predicate edit must also change truth, not merely failure classification.
 # This intentionally weaker hypothesis is an authoring control, not a rule
 # recommended for accounting: it permits a claim total above receivables.
 qsource,qresources=p.from_program(variant)
 old_predicate='(eq (ref "claim_total") (ref "receivable"))'
 check(qsource.count(old_predicate)==1,'predicate_variant_target')
 qsource=qsource.replace(old_predicate,'(le (ref "receivable") (ref "claim_total"))',1)
 qtyped=deepcopy(variant);rule=qtyped['state_invariant']['definition']['assessment']['requirements'][0]
 rule['predicate']={'op':'le','left':{'op':'ref','id':'receivable'},'right':{'op':'ref','id':'claim_total'}}
 qtyped['expected_invariant_sha256']=t.g.digest(qtyped['state_invariant'])
 qactual=p.execute_text(qsource,qresources);check(qactual==p.prior.guarded.run(qtyped),'predicate_full_result')
 check(qactual['status']=='complete_provisional' and len(qactual['trace'])>0,'predicate_changes_truth')
 check(qactual['current']['memory']['claims']['invoice/a~1']['remaining']=='31/1','predicate_permits_named_counterexample')
 (out/'alpha.weakened-predicate.acc').write_text(qsource);dump(out/'alpha.weakened-predicate.resources.json',qresources);dump(out/'alpha.weakened-predicate.result.json',qactual)
 # Unknown and partial values remain unresolved in the same typed engine.
 book=actual['trace'][0]['result']['transition']['after'];spec=t.lower(inv)['invariant']
 values,_=t.g.bind(spec,book,body['memory_definition'],body['schemas']);uncertain=[]
 for label in ['unknown-field','partial-population']:
  vals=deepcopy(values)
  if label=='unknown-field':vals['collections']['claims']['rows'][0]['remaining']={'status':'unknown','reason':'unobserved'}
  else:vals['collections']['claims'].update(status='partial',reason='incomplete supplied set')
  result=t.g.totals.assess(spec['definition'],vals,[]);check(result==t.g.totals.assess(body['state_invariant']['definition'],vals,[]),'unknown_exact_result')
  check(result['status']=='unresolved','unknown_preserved');dump(out/(label+'.json'),result);uncertain.append(label)
 # Non-ASCII provenance and CRLF must preserve semantic identity and all spans.
 unicode_source=source.replace('Actual history, source admission','已知來源: Actual history, source admission',1)
 unicode_source=unicode_source.replace('\n','\r\n');c=p.compile_text(unicode_source,resources)
 check(c['status']=='compiled_structural','unicode_crlf:'+c.get('reason',''))
 spans(unicode_source,c['source_spans']);spans(unicode_source,c['invariant_source']['declarations'])
 for block in c['method_spans']:
  spans(unicode_source,block['declarations']);check(sha256(unicode_source.encode()[block['byte_start']:block['byte_end']]).hexdigest()==block['source_sha256'],'crlf_method_span')
 changed=unicode_source.replace('(le ','(mystery ',1);invalid('unicode-crlf-error',changed,'unknown_operator:mystery',needle='mystery')
 whitespace=source.replace('global "as_of"','global  "as_of"',1);c=p.compile_text(whitespace,resources)
 check(c['program']==body and c['source_sha256']!=p.compile_text(source,resources)['source_sha256'],'semantic_vs_source_identity')
 # Reconstruct the two ordinary programs from saved source and resources only.
 for owner in saved:
  check(p.execute_text((out/(owner+'.acc')).read_text(),load(out/(owner+'.resources.json')))==load(out/(owner+'.result.json')),'saved_reconstruction')
 for name,h in lock.items():check(sha(ROOT/name)==h,'protected_after:'+name)
 checks={'passed':True,'companies':2,'complete_command_results':sum(x['commands'] for x in ordinary),'counterexamples_refused':len(refused),
  'compile_refusals':len(negatives),'meaningful_rule_variant':True,'predicate_truth_variant':True,'native_binding_refusal':True,'partial_unknown_cases':len(uncertain),'utf8_crlf_spans':True,
  'complete_invariant_resource_removed':True,'saved_programs_revalidated':2,'protected_files':len(lock),
  'source_admission':False,'accounting_admission':False,'general_rule_language':False,'product_ready':False}
 for name,value in [('checks.json',checks),('comparisons.json',ordinary),('counterexamples.json',refused),('compile-refusals.json',negatives)]:dump(HERE/name,value)
 dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
  'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/invariant-source-authoring-20261026/verify.py',
  'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-started,
  'data_version':sha(lockfile),'plan_file':'docs/plans/accounting-invariant-source-authoring-20261026.md',
  'result_file':str((HERE/'result.md').relative_to(ROOT)),'artifact_paths':['checks.json','comparisons.json','counterexamples.json','compile-refusals.json','examples/'],
  'implementation_sha256':{name:sha(HERE/name) for name in ['invariant_text.py','program_text.py','verify.py']},'timestamp_utc':datetime.now(timezone.utc).isoformat()})
 print(json.dumps(checks),flush=True)
if __name__=='__main__':main()
