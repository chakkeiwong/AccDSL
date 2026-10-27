"""Mechanical verification only. Does not certify source reading or scientific acceptance."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,platform,time
start=time.monotonic();p=Path(__file__).resolve().parent;root=p.parents[2]
tex=root/'docs/design/research/simulation-literature-closure-20261026/supplement.tex'
def read(f):return json.loads(f.read_text())
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
checks=[]
def check(name,ok,detail):
 checks.append(dict(id=name,passed=bool(ok),detail=detail))
 if not ok:raise AssertionError((name,detail))
s=tex.read_text();b=chr(92)
cites={key for group in re.findall(re.escape(b)+r'cite(?:\[[^]]*\])?\{([^}]+)\}',s) for key in group.split(',')}
refs=re.findall(re.escape(b)+r'bibitem\{([^}]+)\}',s)
check('resolved_citations',cites==set(refs),dict(cited=len(cites),bibliography=len(refs),missing=list(cites-set(refs)),unused=list(set(refs)-cites)))
check('unique_bibliography',len(set(refs))==len(refs),len(refs))
labels=re.findall(re.escape(b)+r'label\{([^}]+)\}',s)
used=re.findall(re.escape(b)+r'(?:eqref|ref)\{([^}]+)\}',s)
check('resolved_crossrefs',set(used)<=set(labels),dict(labels=labels,used=used))
log=tex.with_suffix('.log').read_text();warnings=[x for x in log.splitlines() if re.search(r'Warning|Overfull|Underfull|undefined|^!',x)]
check('final_latex_log_clean',not warnings,warnings)
info=subprocess.check_output(['pdfinfo',str(tex.with_suffix('.pdf'))],text=True)
pages=int(re.search(r'Pages:\s+(\d+)',info).group(1))
check('expected_page_count',pages==21,pages)
check('rendered_every_page',len(list((p/'rendered-current').glob('page-*.png')))==pages,pages)
for name,expected,key in [('exact-results.json',47,'checks'),('interaction-results.json',28,'checks'),('actus-fixture-results.json',24,'records'),('code-integrity.json',8,'records'),('tcvae-code-integrity.json',11,'records'),('recent-method-results.json',29,'checks'),('finite-compression-results.json',668,'checks'),('persistent-financing-results.json',350,'checks'),('runtime-integration-results.json',174,'checks'),('pmcmc-exact-results.json',24,'checks')]:
 j=read(p/name);rows=j[key]
 check(name,j['status']=='PASS' and len(rows)==expected and all(r['passed'] for r in rows),len(rows))
for filename in ['code-integrity.json','tcvae-code-integrity.json']:
 for r in read(p/filename)['records']:
  f=p/'sources'/r['local'];raw=f.read_bytes()
  check('code_sha_'+r['local'],sha(f)==r['sha256'],r['local'])
  blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
  check('git_blob_'+r['local'],blob==r['git_blob'],r['git_blob'])
for name in ['runtime-integration-manifest.json']:
 for rel,h in read(p/name)['dependencies'].items():check('runtime_dependency_'+rel,sha(root/rel)==h,rel)
integration=read(p/'integration-verification.json')
check('integration_source_preservation',integration['status']=='PASS' and all(r['passed'] for r in integration['checks']),integration['protected_sources'])
review=read(p/'rendered-review.json')
check('rendered_review_current',review['supplement_sha256']==sha(tex.with_suffix('.pdf')),review['scope'])
for name,r in integration['rendered'].items():
 f=root/read(p/'manuscript-integration.json')['successor']/(name+'.pdf')
 check('integrated_pdf_current_'+name,sha(f)==r['sha256']==review['pdfs'][name]['sha256'],r['total_pages'])
 check('integrated_pages_inspected_'+name,set(r['pages'])<=set(review['pdfs'][name]['pages']),len(r['pages']))
sources=read(p/'source-support.json')['records'];ids={r['id'] for r in sources}
for r in sources:
 f=root/r['path'];check('source_hash_'+r['id'],f.is_file() and sha(f)==r['sha256'],r['path'])
 check('source_pdf_'+r['id'],f.read_bytes().startswith(b'%PDF-'),r['read_scope'])
 check('source_metadata_'+r['id'],all(k in r for k in ['title','authors','full_text_status','retraction_check','correction_check','classification']),r['publication_identity_doi'])
 check('metadata_hash_'+r['id'],sha(root/r['retraction_check']['source'])==r['retraction_check']['sha256'],r['retraction_check']['source'])
for c in read(p/'claim-support.json')['records']:
 check('claim_source_links_'+c['id'],set(c['sources'])<=ids,c['sources'])
for r in read(p/'baseline.json')['files']:
 if r['path'].endswith('.pdf') or r['path'].startswith('/home/chakwong/python/MathDevMCP/'):
  f=Path(r['path']);f=f if f.is_absolute() else root/f
  check('protected_entry_'+f.name,sha(f)==r['sha256'],r['path'])
# Later protected snapshots are checked at resolved targets, not against a live
# alias that another authorized work unit can legitimately advance.
for r in read(p/'controls-integration-baseline.json'):
 if 'target' in r:check('protected_intermediate_'+r['path'],sha(Path(r['target']))==r['sha256'],r['target'])
checkpoint=(root/'docs/plans/accounting-master-checkpoint.md').read_text()
head=checkpoint.split('## Prior governing')[0]
match=re.search(r'^PDF: (.+)$',head,re.M);expected=re.search(r'^SHA256: ([a-f0-9]{64})',head,re.M)
if match and expected:check('current_governing_alias',sha(root/'docs/AccDSL-latest.pdf')==expected.group(1),match.group(1))
publication=read(p/'publication-result.json')
check('publication_status',publication['status']=='PASS' and publication['whole_requirements_closed']==0,publication['scope'])
for rel,r in publication['links'].items():
 f=root/rel
 check('published_alias_'+rel,f.is_symlink() and f.readlink().as_posix()==r['target'] and sha(f)==r['sha256'],r)
check('active_plan_preserved',publication['active_plan_preserved'] in (root/'data/accounting-master/next-plan.md').read_text(),publication['active_plan_preserved'])
for rel in ['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md']:
 check('additive_control_'+rel,'## Additive simulation literature evidence — 26 October 2026' in (root/rel).read_text(),rel)
# Only new links are checked; historical links elsewhere are not rewritten.
link_errors=[]
for f in [p/'result.md',root/'docs/README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
  if '://' in target or target.startswith('#'):continue
  if f.name=='README.md' and 'literature-closure-20261026' not in target:continue
  target=target.split('#')[0]
  if not (f.parent/target).resolve().exists():link_errors.append(str(f)+':'+target)
# verification/manifest are generated below and can be absent on first run.
link_errors=[e for e in link_errors if not e.endswith(':verification.json') and not e.endswith(':artifact-manifest.json')]
check('new_document_links',not link_errors,link_errors)
result=dict(date='2026-10-26',status='PASS',mechanical_checks=len(checks),checks=checks,pdf_pages=pages,pdf_sha256=sha(tex.with_suffix('.pdf')),tex_sha256=sha(tex),scope='Mechanical consistency and exact-fixture replay evidence only. Review and residual sources are separate.',review_status='Author self-review; human and independent review pending',full_program_status='PARTIAL_NOT_COMPLETE',known_provenance_limit='Two initial round10 metadata-search responses overwritten by retry; hashes retained, fresh exact-DOI replacements present; correction-checks.json records incident')
(p/'verification.json').write_text(json.dumps(result,indent=2)+chr(10))
manifest=dict(date='2026-10-26',git_commit='Unavailable: unusable .git; content hashes retained',command='python3 data/accounting-master/literature-closure-20261026/verify.py',environment=sys.version,platform=platform.platform(),cpu_gpu='CPU-only exact arithmetic, parsing and document build; no GPU detection or ML imports',random_seeds='N/A: deterministic verification',wall_seconds=time.monotonic()-start,plan='docs/plans/accounting-literature-closure-20261026.md',result='data/accounting-master/literature-closure-20261026/result.md',data='Retained primary documents, official pinned code and authored finite cases',files=[])
for directory in [p,tex.parent,root/read(p/'manuscript-integration.json')['successor']]:
 for f in sorted(directory.rglob('*')):
  if not f.is_file() or f.name=='artifact-manifest.json' or '__pycache__' in f.parts:continue
  manifest['files'].append(dict(path=str(f.relative_to(root)),bytes=f.stat().st_size,sha256=sha(f)))
for r in sources:manifest['files'].append(dict(path=r['path'],bytes=(root/r['path']).stat().st_size,sha256=r['sha256']))
(p/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
print(json.dumps(dict(status='PASS',mechanical_checks=len(checks),pdf_pages=pages,citations=len(refs),primary_sources=len(sources),pdf_sha256=result['pdf_sha256'],manifest_files=len(manifest['files']))))
