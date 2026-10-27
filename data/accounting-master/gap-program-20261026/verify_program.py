"""Check exact obligation preservation, evidence routing and live refresh."""
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
checks=[]
def read(p):return json.loads(p.read_text())
def hashfile(p):return sha256(p.read_bytes()).hexdigest()
def ck(name,condition):
 checks.append({'id':name,'passed':bool(condition)})
 if not condition:raise AssertionError(name)
old=read(ROOT/'data/accounting-master/current-design-reconciliation-20261025/audit-status.json')
current=read(OUT/'audit-status.json'); packages=read(OUT/'closure-packages.json')['packages']
ids={p['id'] for p in packages}
ck('unique_packages',len(ids)==len(packages)==18)
for group,rows in old['groups'].items():
 new=current['groups'][group]
 ck('exact_ids.'+group,[r['id'] for r in rows]==[r['id'] for r in new])
 for a,b in zip(rows,new):
  ck('preserve_inherited.'+a['id'],a==b['inherited_record'])
  ck('routed.'+a['id'],bool(b['closure_packages']) and set(b['closure_packages'])<=ids)
  ck('not_promoted.'+a['id'],b['full_requirement_closed'] is False and b['acceptance']=='not_promoted')
  ck('current_next_action.'+a['id'],all(k+':' in b['remaining_work_and_next_action'] for k in b['closure_packages']))
seen=set();todo=packages[:];order=[]
while todo:
 ready=[p for p in todo if set(p['depends_on'])<=seen]
 ck('acyclic_step.'+str(len(seen)),bool(ready))
 for p in ready:
  ck('closure_fields.'+p['id'],all(p[k] for k in ['failure','existing_support','closure_evidence','next_action','limits']))
  seen.add(p['id']);order.append(p['id']);todo.remove(p)
ck('literature_ids',[r['id'] for r in current['literature']]==[f'L{i:02d}' for i in range(1,10)])
for row in current['literature']:ck('literature_route.'+row['id'],bool(row['closure_packages']) and set(row['closure_packages'])<=ids)
f=read(OUT/'failure-register.json');oldf=read(ROOT/'data/accounting-master/simulation-monograph-20261026/failure-cases.json')['cases']
ck('original_failures',[r['id'] for r in f['original']]==[r['id'] for r in oldf])
for a,b in zip(oldf,f['original']):ck('original_failure_preserved.'+a['id'],all(b[k]==v for k,v in a.items()))
for group,rows in f.items():
 if not isinstance(rows,list):continue
 for row in rows:ck('failure_route.'+row['id'],bool(row['closure_packages']) and set(row['closure_packages'])<=ids)
for record in read(OUT/'trace-source-lock.json')['files']:ck('trace_hash.'+record['path'],hashfile(ROOT/record['path'])==record['sha256'])
for path,digest in read(OUT/'settlement-source-lock.json').items():ck('runtime_hash.'+path,hashfile(ROOT/path)==digest)
for kind in ['settlement','smc2']:
 manifest=read(OUT/(kind+'-run-manifest.json'))
 ck(kind+'.manifest_pass',manifest['status']=='PASS')
 ck(kind+'.cpu_only',manifest['environment']['CUDA_VISIBLE_DEVICES']=='-1')
 script='settlement_cases.py' if kind=='settlement' else 'smc2_exchange.py'
 ck(kind+'.script_hash',hashfile(OUT/script)==manifest['script_sha256'])
 if kind=='smc2':
  for path,digest in manifest['source_sha256'].items():ck('smc_source.'+path,hashfile(ROOT/path)==digest)
settlement=read(OUT/'settlement-checks.json');smc=read(OUT/'smc2-exchange-results.json')
ck('settlement_checks',len(settlement)==179 and all(c['passed'] for c in settlement))
ck('smc2_checks',len(smc['checks'])==28 and all(c['passed'] for c in smc['checks']))
ck('settlement_controls',len(read(OUT/'settlement-controls.json'))==14)
contract_manifest=read(OUT/'contract-run-manifest.json')
contract=read(OUT/'contract-condition-results.json')
ck('contract.manifest_pass',contract_manifest['status']=='PASS')
ck('contract.cpu_only',contract_manifest['environment']['CUDA_VISIBLE_DEVICES']=='-1')
ck('contract.script_hash',hashfile(OUT/'contract_conditions.py')==contract_manifest['script_sha256'])
ck('contract.result_hash',hashfile(OUT/'contract-condition-results.json')==contract_manifest['results_sha256'])
for path,digest in contract_manifest['source_sha256'].items():
 ck('contract.source_hash.'+path,hashfile(ROOT/path)==digest)
source_packet=read(OUT/'apple-contract-source/manifest.json')
for page in source_packet['extracted_pages']:
 ck('contract.page_text.'+str(page['pdf_page']),hashfile(ROOT/page['text'])==page['sha256'])
 if 'render' in page:ck('contract.page_image.'+str(page['pdf_page']),hashfile(ROOT/page['render'])==page['render_sha256'])
ck('contract.cases',len(contract['cases'])==58 and all(c['actual']==c['expected'] for c in contract['cases']))
ck('contract.controls',len(contract['mutations'])==12 and all(c['detected'] for c in contract['mutations']))
ck('contract.checks',len(contract['checks'])==144 and all(c['passed'] for c in contract['checks']))
ck('contract.no_actual_admission',all(c['actual_issuer_admission'] is False for c in contract['cases']))
ck('contract.source_inventory',sum(line.startswith('| C') for line in (OUT/'contract-conditions.md').read_text().splitlines())==20)
ck('contract.scoped_successor',any(d['id']=='D14' for d in current['successor_deltas']))
ck('concurrent.scoped_successor',any(d['id']=='D15' for d in current['successor_deltas']))
ck('contract.cross_interface',f['cross_interface'][-1]['id']=='X14')
ck('packages_remain_open',all(p['status']=='open' for p in packages))
for path in ['closure-program.md','plan-review.md','settlement-result.md','smc2-transfer.md','remaining-work.md','result.md']:ck('artifact.'+path,(OUT/path).is_file())
refresh=read(OUT/'master-refresh-manifest.json')
catalog=read(ROOT/'scripts/accounting_master_catalog.json')
prior=read(OUT/'controls-before-refresh/scripts/accounting_master_catalog.json')
ck('legacy_catalog_preserved',{k:v for k,v in prior.items() if k!='active_execution_note'}=={k:v for k,v in catalog.items() if k!='active_execution_note'})
a=catalog['active_execution_note'];old_active=prior['active_execution_note']
ck('active_full_gap_route',a['full_gap_plan']=='docs/plans/accounting-gap-program-20261026.md')
ck('active_audit_route',a['current_audit']=='data/accounting-master/gap-program-20261026/audit-status.json')
ck('active_full_remaining_route',a['full_gap_remaining_work']=='data/accounting-master/gap-program-20261026/remaining-work.md')
ck('active_language_remaining_exists',(ROOT/a['remaining_work']).is_file())
ck('active_language_plan_listed',a['active_work_plan'] in a['active_work_plans'])
ck('concurrent_language_plan_retained',refresh['concurrent_plan_preserved'] in a['active_work_plans'])
ck('live_language_plan_exists',(ROOT/a['active_work_plan']).is_file())
ck('not_historical_controller',a['execution']==old_active['execution'])
ck('phase_status_preserved',a['phase_status']==old_active['phase_status'])
followup=read(OUT/'e03-master-refresh-manifest.json')
pre_e03=read(OUT/'controls-before-e03/scripts/accounting_master_catalog.json')
for key,value in followup['preserved_active_fields'].items():
 ck('e03.saved_concurrent_field.'+key,pre_e03['active_execution_note'][key]==value)
# Current pointers may advance in concurrent work; do not insist they remain stale.
ck('e03.recorded',a['gap_program_execution']['E03'].startswith('checked conditional reference:'))
ck('e03.result_route',a['gap_program_contract_result']=='data/accounting-master/gap-program-20261026/contract-conditions.md')
for item in followup['changes']:
 path=item['path'];saved=(OUT/'controls-before-e03'/path).read_bytes();now=(ROOT/path).read_bytes()
 ck('e03.saved_before.'+path,sha256(saved).hexdigest()==item['before_sha256'])
 if not path.endswith('.json'):
  ck('e03.prior_body_retained.'+path,saved.decode().split(chr(10),1)[1].lstrip(chr(10)) in now.decode())
  ck('e03.source_result_link.'+path,'data/accounting-master/gap-program-20261026/contract-conditions.md' in now.decode())
ck('e03.original_refresh_preserved',hashfile(OUT/'master-refresh-manifest.json')==followup['original_refresh_sha256'])
ck('e03.refresh_script_preserved',hashfile(OUT/'refresh_e03.py')==followup['script_sha256'])
route=read(OUT/'final-route-refresh.json')
ck('final_route.before_hash',hashfile(OUT/'catalog-before-final-route.json')==route['before_sha256'])
e03_catalog=next(r for r in followup['changes'] if r['path']=='scripts/accounting_master_catalog.json')
ck('final_route.previous_link',route['before_sha256']==e03_catalog['after_sha256'])
ck('final_route.counts',a['gap_program_trace_counts']['successor_deltas']==len(current['successor_deltas']) and a['gap_program_trace_counts']['cross_interface_challenges']==len(f['cross_interface']))
final_checkpoint=read(OUT/'final-checkpoint-refresh.json')
for item in final_checkpoint['changes']:
 path=item['path'];saved=(OUT/'controls-before-final-checkpoint'/path).read_bytes();now=(ROOT/path).read_bytes()
 ck('final_checkpoint.before_hash.'+path,sha256(saved).hexdigest()==item['before_sha256'])
 earlier=next(r for r in followup['changes'] if r['path']==path)
 ck('final_checkpoint.previous_link.'+path,item['before_sha256']==earlier['after_sha256'])
 ck('final_checkpoint.prior_body_retained.'+path,saved.decode().split(chr(10),1)[1].lstrip(chr(10)) in now.decode())
 ck('final_checkpoint.result_link.'+path,'data/accounting-master/gap-program-20261026/result.md' in now.decode())
concurrent_dir=ROOT/'data/accounting-master/nested-invariant-integration-20261026'
concurrent_refresh=read(concurrent_dir/'control-refresh.json')
for item in refresh['changes']:
 path=item['path']; prior_bytes=(OUT/'controls-before-refresh'/path).read_bytes();now=(ROOT/path).read_bytes()
 ck('saved_before.'+path,sha256(prior_bytes).hexdigest()==item['before_sha256'])
 concurrent_before=(concurrent_dir/'control-before'/path).read_bytes()
 concurrent_row=concurrent_refresh['updated_files'][path]
 ck('concurrent.chain_before.'+path,sha256(concurrent_before).hexdigest()==item['after_sha256']==concurrent_row['before'])
 ck('concurrent.chain_after.'+path,hashfile(OUT/'controls-before-e03'/path)==concurrent_row['after'])
 if not path.endswith('.json'):
  old_body=prior_bytes.decode().split('\n',1)[1].lstrip('\n')
  ck('old_content_preserved_in_preintegration.'+path,old_body in concurrent_before.decode())
  ck('program_link.'+path,'data/accounting-master/gap-program-20261026/closure-program.md' in now.decode())
for key,field,alias in [('main','current_pdf','docs/AccDSL-latest.pdf'),('standalone','standalone_pdf','docs/AccDSL-simulation-foundations.pdf')]:
 ck(key+'.frozen_hash',hashfile(ROOT/refresh[key])==refresh[key+'_sha256'])
 ck(key+'.alias', (ROOT/alias).resolve()==(ROOT/a[field]).resolve())
 ck(key+'.catalog_hash',hashfile(ROOT/a[field])==a[field+'_sha256'])
result={'status':'PASS','checks':checks,'count':len(checks),'topological_order':order,
 'scope':'Trace preservation, known coverage routing, scoped execution evidence and guarded master control refresh; not whole mission closure'}
(OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'packages':len(packages),'topological_order':order}))
