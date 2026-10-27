from pathlib import Path
import hashlib,json,subprocess,time,sys,re,platform,os
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
T=R/'docs/design/proposal/manuscript-release-prep-v552r1-20261027'
clock=time.monotonic();checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,ok,detail=None):checks.append({'check':n,'pass':bool(ok),'detail':detail})
def read(p):return json.loads(p.read_text())
b=read(D/'v552r1/baseline.json');B=R/b['source']
for row in b['inputs']:ck('predecessor_source:'+row['path'],sha(B/row['path'])==row['sha256'])
for n,h in b['pdfs'].items():ck('predecessor_pdf:'+n,sha(B/n)==h)
pr=read(D/'v552r1/package-record.json')
ck('external_manifest_identity',sha(T/'package-manifest.json')==pr['manifest_sha256'])
cmd=[sys.executable,'-I','-B',str(T/'verify_package.py')]
p=subprocess.run(cmd,cwd=R,text=True,capture_output=True,timeout=60,env={**os.environ,'CUDA_VISIBLE_DEVICES':'-1','PYTHONDONTWRITEBYTECODE':'1'})
ck('package_verifier',p.returncode==0,{'command':cmd,'stdout':p.stdout,'stderr':p.stderr})
for name,key in [('accounting-product-proposal.pdf','main_pdf'),('simulation-foundations.pdf','simulation_pdf')]:ck('candidate_pdf:'+name,sha(T/name)==pr['inputs'][key])
old=read(R/'data/accounting-master/acceptance-priority-20261027/release-acceptance.json');cur=read(D/'release-acceptance.json')
ck('acceptance_predecessor_identity',sha(R/cur['predecessor']['path'])==cur['predecessor']['sha256'])
ck('acceptance_row_order',[x['id'] for x in old['rows']]==[x['id'] for x in cur['rows']])
by={x['id']:x for x in old['rows']}
for x in cur['rows']:ck('original_acceptance:'+x['id'],x['original_condition']==by[x['id']]['original_condition'])
clauses=read(D/'acceptance-clauses.json')
ck('all_mc_clauses',set(x['parent'] for x in clauses['rows'])=={'MC'+str(i).zfill(2) for i in range(1,36)})
for x in clauses['rows']:
 o=by[x['parent']]['original_condition']
 ck('clause_original:'+x['id'],x['original_requirement']==o['requirement'] and x['original_acceptance']==o['acceptance'] and hashlib.sha256(x['original_acceptance'].encode()).hexdigest()==x['original_acceptance_sha256'])
idx=read(D/'citation-source-index.json')
ck('index_candidate',idx['candidate']==str(T.relative_to(R)))
for x in idx['ledger_manifests']:ck('literature_ledger:'+x['path'],sha(R/x['path'])==x['sha256'])
for x in idx['citation_routes']:
 for a in x['occurrences']:
  lines=(T/a['file']).read_text().splitlines();ck('citation:'+x['key']+':'+a['file']+':'+str(a['line']),a['citation'] in chr(10).join(lines[a['line']-1:a['line']+a['citation'].count(chr(10))]))
cm=read(D/'current-claim-map.json')
for x in cm['rows']:
 ck('claim_origin:'+x['id'],sha(R/x['original_ledger'])==x['original_ledger_sha256'])
 for a in x['current_locations']:ck('claim_location:'+x['id']+':'+a['file'],sha(T/a['file'])==a['sha256'])
case=read(D/'acceptance-case-review.json')
for n,h in case['input_hashes'].items():ck('case_input:'+n,sha(R/n)==h)
for name,field in [('v552r1/checks.json','passed'),('v552r1/relocation-result.json','pass'),('acceptance-case-review.json','pass'),('current-claim-map.json','passed')]:ck('recorded_pass:'+name,read(D/name)[field])
render=read(D/'v552r1/rendered-review.json')
for x in render['rows']:
 ck('rendered:'+x['volume']+':'+str(x['physical_page']),x['review']=='bounded_author_inspection_pass' and x['pdf_sha256']==sha(T/(x['volume']+'.pdf')) and (R/x['path']).is_file())
req=['result.md','remaining-work.md','scholarly-review.md','integration-plan.md','plan-review.md','release-acceptance.json','release-acceptance.md','acceptance-clauses.json','acceptance-clauses.md','citation-source-index.json','citation-source-index.md','current-claim-map.json','current-claim-map.md']
for n in req:ck('required_record:'+n,(D/n).is_file())
for name in ['result.md','remaining-work.md','scholarly-review.md','integration-plan.md']:
 for dest in re.findall(r'[]][(]([^)]*)[)]',(D/name).read_text()):
  if '://' not in dest and not dest.startswith('#'):ck('record_link:'+name+':'+dest,(D/dest.split('#')[0]).exists())
out={'date':'2026-10-27','candidate':str(T.relative_to(R)),'pass':all(c['pass'] for c in checks),'checks':checks,'command':[sys.executable,str(Path(__file__).resolve())],'cwd':str(R),'python':sys.version,'platform':platform.platform(),'seconds':time.monotonic()-clock,'cpu_gpu':'CPU; GPU intentionally hidden for verifier; no GPU framework imported','plan':str((D/'integration-plan.md').relative_to(R)),'limits':'Integrity and navigation checks only; no new whole-document/source/domain/independent acceptance.'}
(D/'final-verification.json').write_text(json.dumps(out,indent=2)+chr(10))
print(json.dumps({'pass':out['pass'],'checks':len(checks),'failures':[c for c in checks if not c['pass']],'seconds':out['seconds']}))
raise SystemExit(0 if out['pass'] else 1)
