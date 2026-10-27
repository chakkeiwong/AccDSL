#!/usr/bin/env python3
"""One-off P15 document reference diagnostic; no product or substantive acceptance."""
from pathlib import Path
import hashlib,json,re,subprocess,datetime,sys
ROOT=Path(__file__).resolve().parents[3]; B='docs/plans/accounting-proposal/'
OUT=B+'p15-reference-validation-v5.json'; AV=B+'p15-assessment-validation-v5.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
errors=[];edges=[];pins={};seen=set();historical=[];pdfcache={};mdlinks=[]
OUTPUTS={OUT,AV}
ARCHIVE_NAMES={'p15-assessment-validation-v3.json','p15-reference-validation-v3.json','p15-registered-check-p07-reconciliation-v3.json','p15-registered-check-p07-reconciliation-v3.meta.json','p15-registered-check-p07-reconciliation-v3.stderr.txt','p15-assessment-validation-v3.json','p15-reference-validation-v3.json','p15-reference-validator-v3-run.meta.json','p15-reference-validator-v3-run.stdout.json','p15-reference-validator-v3-run.stderr.txt','p15-assessment-validation-v1.json','p15-register-validation-v1.json','p15-assessment-check-v1.meta.json','p15-assessment-check-v1.stdout.json','p15-evidence-assessments-v1.json','p15-reference-validation-v2.json','p15-assessment-validation-v2.json','p15-reference-repair-v2.json','p15-reference-repair-v2.md','p15-reference-completion-v1.json','p15-registered-check-reference-repair-v2.json','p15-registered-check-reference-repair-v2.meta.json','p15-reference-validator-v2-run-v1.meta.json'}
ARCHIVE_NAMES.update({'p15-assessment-validation-v4.json','p15-reference-validation-v4.json'})
def checkpath(name,expected=None,owner='',loc='',quote=None,allow_empty=False):
 try:
  p=ROOT/name
  assert isinstance(name,str) and not Path(name).is_absolute() and '..' not in Path(name).parts and Path(name).as_posix()==name,'noncanonical path'
  assert p.resolve().is_relative_to(ROOT) and not p.is_symlink(),'escaped/symlink path'
  assert p.is_file() and (allow_empty or p.stat().st_size),'missing/empty file'
  actual=sha(p)
  if expected:assert actual==expected,'SHA-256 mismatch'
  if name not in OUTPUTS:pins[name]=actual
  if loc.startswith('JSON Pointer '):
   ptr=loc[len('JSON Pointer '):];assert ptr=='' or ptr.startswith('/'),'RFC 6901 prefix';v=load(p)
   for raw in ptr.split('/')[1:]:
    assert not re.search(r'~(?![01])',raw),'invalid RFC 6901 escape';k=raw.replace('~1','/').replace('~0','~')
    if isinstance(v,list):assert re.fullmatch(r'0|[1-9][0-9]*',k),'noncanonical array index';v=v[int(k)]
    else:v=v[k]
  elif loc.startswith('lines '):
   m=re.fullmatch(r'lines (\d+)-(\d+)',loc);assert m and p.suffix!='.pdf','invalid line locator'
   a,b=map(int,m.groups());assert 1<=a<=b<=len(p.read_text().splitlines()),'line bounds'
  elif loc.startswith('PDF '):
   m=re.fullmatch(r'PDF physical pages? (\d+)(?:-(\d+))?; section (.+)',loc);assert m,'unsupported PDF locator'
   a=int(m[1]);b=int(m[2] or m[1]);section=m[3]
   if name not in pdfcache:
    info=subprocess.run(['pdfinfo',str(p)],capture_output=True,text=True,check=True).stdout
    n=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1]);pdfcache[name]={'pages':n}
   assert 1<=a<=b<=pdfcache[name]['pages'],'PDF page bounds'
   txt=subprocess.run(['pdftotext','-f',str(a),'-l',str(b),'-layout',str(p),'-'],capture_output=True,text=True,check=True).stdout
   assert section in txt,'PDF section absent from selected pages'
  elif loc:raise AssertionError('unrecognised locator: '+loc)
  if quote:assert quote in p.read_text(),'exact quotation absent'
  edges.append({'owner':owner,'path':name,'sha256':actual,'locator':loc,'passed':True})
  return p
 except Exception as e:
  errors.append({'owner':owner,'path':name,'locator':loc,'error':str(e)});return None

def walk(x,owner,at=''):
 if isinstance(x,dict):
  # Superseded edges are historical evidence, intentionally not active inputs.
  for k in ['old_reference']:
   if k in x:historical.append({'owner':owner,'at':at+'/'+k,'reason':'superseded reference; preserved in before-snapshot'})
  candidates=[]
  if 'sha256' in x:
   for key in ['path','snapshot','local_path']:
    if isinstance(x.get(key),str):candidates.append((key,x[key],x['sha256']));break
  for k,v in x.items():
   if k.endswith('_path') and isinstance(v,str) and k[:-5]+'_sha256' in x:candidates.append((k,v,x[k[:-5]+'_sha256']))
  for key,name,digest in candidates:
   p=checkpath(name,digest,owner+at,x.get('locator',''),x.get('quote'),allow_empty='stderr' in name)
   if p and name.startswith(B) and p.suffix in ['.json','.md']:
    if (('/evidence-v1/' in name or '/evidence-v2/' in name or '/evidence-v3/' in name or '/evidence-v4/' in name or '/evidence-v5/' in name) and p.name!='capture-manifest.json') or p.name in ARCHIVE_NAMES or (p.name.endswith('-v1.json') and ('check' in p.name or 'validation' in p.name)):
     historical.append({'path':name,'sha256':digest,'reason':'archived record; hash preserved, historical inputs not freshly endorsed'})
    else:visit(name)
  for k,v in x.items():
   if k=='old_reference':continue
   if k in ['input_hashes','input_hash_map'] and isinstance(v,dict):
    for name,digest in v.items():checkpath(name,digest,owner+at+'/'+k)
   else:walk(v,owner,at+'/'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):walk(v,owner,at+'/'+str(i))
def visit(name):
 if name in seen or name in OUTPUTS:return
 if Path(name).name in ARCHIVE_NAMES:
  historical.append({'path':name,'sha256':sha(ROOT/name),'reason':'preserved historical record; v2 inputs verified against before-images separately'});return
 if ('/evidence-v1/' in name or '/evidence-v2/' in name or '/evidence-v3/' in name or '/evidence-v4/' in name or '/evidence-v5/' in name) and Path(name).name!='capture-manifest.json':
  historical.append({'path':name,'reason':'verbatim source snapshot; embedded navigation retains origin-relative meaning, not active authored dependencies'});return
 seen.add(name);p=ROOT/name
 if p.suffix=='.json':walk(load(p),name)
 elif p.suffix=='.md':
  for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text()):
   if re.match(r'https?://|#',target):continue
   clean=re.sub(r':\d+$','',target.split('#')[0].strip('<>'))
   dest=(Path(clean) if clean.startswith('/') else p.parent/clean).resolve()
   try:rel=dest.relative_to(ROOT).as_posix()
   except ValueError:errors.append({'owner':name,'error':'external local Markdown link','path':clean});continue
   mdlinks.append({'owner':name,'target':rel,'kind':'output link, no circular self hash' if rel in OUTPUTS else 'dependency'})
   if rel not in OUTPUTS:
    q=checkpath(rel,owner=name)
    if q and rel.startswith(B) and q.suffix in ['.json','.md'] and q.name not in ARCHIVE_NAMES:visit(rel)

# Direct roots exercise all active reference arrays and nested proposal records.
roots=['data/accounting-master/deliverables/P15/coverage.json',B+'p15-evidence-assessments-v2.json',B+'p15-evidence-assessments-v2.md',B+'p15-prior-work-v1.json',B+'p15-prior-work-v1.md',B+'p15-p07-reconciliation-v3.json',B+'p15-p07-reconciliation-v3.md',B+'evidence-v4/capture-manifest.json',B+'evidence-v4/master-program.md',B+'evidence-v4/master-program-before-retry-policy.md',B+'p15-provenance-repair-v4.md','data/accounting-master/deliverables/P15/result.md','data/accounting-master/deliverables/P15/progress.md']
roots += [B+'evidence-v5/capture-manifest.json',B+'p15-reference-validator-v5.py']
for name in roots:checkpath(name,owner='active root');visit(name)
# Verify catalog counts, actual retained PDF hashes/pages, and forward-query counts.
catalog=load(ROOT/'docs/design/research/catalog.json');catalog_results=[]
for i,x in enumerate(catalog):
 if x.get('local_path'):
  p=checkpath(x['local_path'],x['sha256'],f'catalog/{i}')
  if p:
   info=subprocess.run(['pdfinfo',str(p)],capture_output=True,text=True,check=True).stdout
   pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1]);ok=pages==x['pages']
   if not ok:errors.append({'path':x['local_path'],'error':'catalog page count mismatch'})
   catalog_results.append({'index':i,'id':x['id'],'pages':pages,'passed':ok})
 else:
  assert 'SOURCE_BLOCKED' in x['status'];catalog_results.append({'index':i,'id':x['id'],'status':x['status'],'passed':True})
forward=load(ROOT/'docs/design/research/forward-snowball.json')['records'];screen=load(ROOT/'docs/design/research/forward-screening-decisions.json')
counts={'catalog_entries':len(catalog),'retained_pdfs':sum(bool(x.get('local_path')) for x in catalog),'blocked':sum(not x.get('local_path') for x in catalog),'forward_queries':len(forward),'candidate_occurrences':sum(len(x.get('candidates',[])) for x in forward),'screening_records':len(screen['records'])}
assert counts=={'catalog_entries':36,'retained_pdfs':32,'blocked':4,'forward_queries':72,'candidate_occurrences':194,'screening_records':179},counts
# Confirm substantive rows unchanged in the eight-assessment copy.
a1=load(ROOT/(B+'p15-evidence-assessments-v1.json'));a2=load(ROOT/(B+'p15-evidence-assessments-v2.json'))
for key in ['requirements','gaps','planned_ids','completed_ids','remaining_ids','open_decisions']:
 if a1[key]!=a2[key]:errors.append({'path':B+'p15-evidence-assessments-v2.json','error':'changed protected eight-assessment substance: '+key})
# Separate known stale historical provenance from active pass/fail.
old=a1['source_evidence'][1];actual=sha(ROOT/old['path']);historical.append({'path':old['path'],'recorded_sha256':old['sha256'],'observed_sha256':actual,'status':'known superseded mutable-plan mismatch','replacement':a2['source_evidence'][1],'historical_validation':'v1 passed on its recorded inputs; not rerun or presented as current'})
manifest=load(ROOT/(B+'evidence-v3/capture-manifest.json'))
for x in manifest['preserved_preexisting_records']+manifest['protected_files']:
 checkpath(x['path'],x['sha256'],'preservation inventory',allow_empty=True)

# Validate the new capture inventory and require stable current/historical master bytes.
manifest4=load(ROOT/(B+'evidence-v4/capture-manifest.json'))
for x in manifest4['snapshots']+manifest4['preserved_preexisting_records']+manifest4['protected_files']:
 checkpath(x.get('snapshot',x.get('path')),x['sha256'],'v4 capture inventory',allow_empty=True)
comp=manifest4['source_comparison']
cur_bytes=(ROOT/(B+'evidence-v4/master-program.md')).read_bytes()
hist_bytes=(ROOT/(B+'evidence-v4/master-program-before-retry-policy.md')).read_bytes()
if sha(ROOT/(B+'evidence-v4/master-program.md')) != comp['current_master_sha256']:
 errors.append({'error':'v4 current master capture hash mismatch'})
if sha(ROOT/(B+'evidence-v4/master-program-before-retry-policy.md')) != comp['historical_before_image_sha256']:
 errors.append({'error':'v4 historical master capture hash mismatch'})
if comp['current_equals_historical'] != (cur_bytes==hist_bytes):
 errors.append({'error':'v4 master comparison metadata mismatch'})
if not comp.get('capture_stable'):
 errors.append({'error':'v4 current master capture was not stable'})

# v2 reports are immutable historical records. Resolve their changed P15 inputs
# against byte-identical before-images instead of accepting stale live hashes.
substitutions={x['original_path']:x['snapshot'] for x in manifest['snapshots']}
# v2 recorded the mutable master path before the retry-policy update; resolve it
# to the exact v4 historical before-image rather than the changed live file.
substitutions['docs/plans/accounting-master-program.md']=B+'evidence-v4/master-program-before-retry-policy.md'
historical_input_checks=[]
v2=load(ROOT/(B+'p15-reference-validation-v2.json'))
for name,digest in v2['input_hashes'].items():
 target=substitutions.get(name,name)
 p=checkpath(target,digest,'v2 historical input',allow_empty='stderr' in target)
 historical_input_checks.append({'original_path':name,'validated_path':target,'sha256':digest,'passed':p is not None})
before=load(ROOT/(B+'evidence-v4/before-coverage.json'))
after=load(ROOT/'data/accounting-master/deliverables/P15/coverage.json')
changed_rows=[]
for key in ['requirements','gaps']:
 oldrows={x['id']:x for x in before[key]};newrows={x['id']:x for x in after[key]}
 if set(oldrows)!=set(newrows):errors.append({'error':'coverage IDs changed','path':key})
 changed_rows.extend(k for k in oldrows if oldrows[k]!=newrows.get(k))
if set(changed_rows)!={'MC34'}:errors.append({'error':'scope exceeded','retained_v4_changed_rows':changed_rows,'changed_rows':[]})
for rid in ('MC25','G18'):
 oldrow=next(r for r in before['requirements']+before['gaps'] if r['id']==rid)
 newrow=next(r for r in after['requirements']+after['gaps'] if r['id']==rid)
 if oldrow != newrow: errors.append({'error':'retained MC25/G18 substance changed during provenance repair','id':rid})
for key in before:
 if key not in ['requirements','gaps','audit_note','deferred_reconciliation'] and before[key]!=after.get(key):errors.append({'error':'unapproved coverage metadata change','key':key})
ledger=load(ROOT/(B+'p15-p07-reconciliation-v3.json'))
for row in after['requirements']+after['gaps']:
 if row['id'] in changed_rows and row['status']!='partial':errors.append({'error':'row must remain partial','id':row['id']})
rec=load(ROOT/'data/accounting-master/deliverables/P07/recovery.json')
for name,digest in rec['manifest']['changed_source_code_test_files'].items():checkpath(name,digest,'P07 manifest implementation bytes')
for item in ledger['claims']:
 for name in item['test_names']:
  if 'test_accounting_p07.P07Tests.'+name not in rec['tests']['test_ids']:errors.append({'error':'test absent from historical execution','test':name})
if not rec['tests']['passed'] or rec['tests']['failures'] or rec['tests']['skipped']:errors.append({'error':'P07 retained tests not clean'})
if rec['comparison']['persistent_result_sha256']!=rec['comparison']['interrupted_result_sha256']:errors.append({'error':'P07 replay result mismatch'})

# This continuation changes reporting only. Pin all retained files to its entry.
manifest5=load(ROOT/(B+'evidence-v5/capture-manifest.json'))
for x in manifest5['snapshots']+manifest5['preserved_preexisting_records']+manifest5['protected_files']:
 checkpath(x.get('snapshot',x.get('path')),x['sha256'],'v5 preservation inventory',allow_empty=True)
coverage_name='data/accounting-master/deliverables/P15/coverage.json'
checkpath(coverage_name,manifest5['entry_hashes'][coverage_name],'unchanged v5 coverage')
reconciliation_name=B+'p15-p07-reconciliation-v3.json'
checkpath(reconciliation_name,manifest5['entry_hashes'][reconciliation_name],'unchanged v5 reconciliation')
if after != load(ROOT/(B+'evidence-v5/before-coverage.json')):
 errors.append({'error':'coverage changed during reporting-only slice'})
# Older reports retain their exact recorded dependencies. Substitute only a
# known original-path/hash pair whose snapshot has those exact bytes; active
# dependencies continue to resolve against the actual current file.
snapshot_by_input={}
for m in (manifest,manifest4,manifest5):
 for x in m['snapshots']:
  snapshot_by_input[(x['original_path'],x['sha256'])]=x['snapshot']
for version in ('v3','v4'):
 report_name=B+'p15-reference-validation-'+version+'.json'
 checkpath(report_name,manifest5['entry_hashes'][report_name],version+' retained report')
 doc=load(ROOT/report_name)
 if not doc['passed'] or doc['errors']:
  errors.append({'path':report_name,'error':'retained historical report not clean'})
 for name,digest in doc['input_hashes'].items():
  current=ROOT/name
  target=name if current.is_file() and sha(current)==digest else snapshot_by_input.get((name,digest),name)
  p=checkpath(target,digest,version+' historical input',allow_empty='stderr' in target)
  historical_input_checks.append({'report':report_name,'original_path':name,'validated_path':target,'sha256':digest,'passed':p is not None})
for name in manifest5['missing_completion_records_at_entry']:
 if (ROOT/name).exists():errors.append({'path':name,'error':'absent historical completion unexpectedly materialized'})
# Inventory is relative to this slice, not to v3 or the phase entry. The final
# completion record adds actual later process captures and cumulative changes.

oldpaths=manifest5['entry_hashes']
files=[p for p in (ROOT/B).rglob('*') if p.is_file()]+[ROOT/p for p in ['data/accounting-master/deliverables/P15/coverage.json','data/accounting-master/deliverables/P15/result.md','data/accounting-master/deliverables/P15/progress.md']]
changed=sorted(p.relative_to(ROOT).as_posix() for p in files if p.relative_to(ROOT).as_posix() not in oldpaths or sha(p)!=oldpaths[p.relative_to(ROOT).as_posix()])
changed=sorted(set(changed)|OUTPUTS)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assessment={'schema_version':'accdsl.proposal.p15.assessment_validation.v5','created_at':now,'passed':not errors,'scope':'Final-document and retained-reference integrity for the MC25/G18 and MC34 reporting continuation; no substantive acceptance.','procedure':'python3 -B '+B+'p15-reference-validator-v5.py','validator':{'path':B+'p15-reference-validator-v5.py','sha256':sha(Path(__file__))},'inputs':{k:{'path':B+p,'sha256':sha(ROOT/(B+p))} for k,p in [('assessment','p15-evidence-assessments-v2.json'),('companion','p15-evidence-assessments-v2.md')]},'checked_ids':['MC25','MC34','G18'],'preserved_assessment_ids':a2['completed_ids'],'retained_v4_changed_rows':changed_rows,'changed_rows':[],'reconciliation':{'path':B+'p15-p07-reconciliation-v3.json','sha256':sha(ROOT/(B+'p15-p07-reconciliation-v3.json'))},'substantive_rows_unchanged':a1['requirements']==a2['requirements'] and a1['gaps']==a2['gaps'],'phase_complete':False,'checked_edges':[e for e in edges if 'p15-evidence-assessments-v2' in e['owner'] or 'p15-p07-reconciliation-v3' in e['owner'] or 'evidence-v4' in e['owner'] or 'v5' in e['owner'] or '/P15/' in e['owner']],'errors':errors,'historical_validation':'v1-v4 reports preserved; v2/v3/v4 recorded inputs are checked against current matching bytes or exact original-path/hash before-images. Current result/progress are checked as active roots.'}
if '--probe' in sys.argv:
 print(json.dumps({'passed':not errors,'errors':errors,'counts':counts,'edges':len(edges),'visited':len(seen)},indent=2));sys.exit(bool(errors))
# Outputs use exclusive creation; a retry must use a new version, never overwrite.
for name,doc in [(AV,assessment)]:
 with (ROOT/name).open('x') as f:json.dump(doc,f,indent=2,ensure_ascii=False);f.write('\n')
pins[AV]=sha(ROOT/AV)
report={'schema_version':'accdsl.proposal.p15.reference_validation.v5','created_at':now,'passed':not errors,'scope':'Canonical paths, byte hashes, recursively visited active proposal dependencies, RFC 6901 pointers, text lines, exact quotes, PDF physical pages/section text, Markdown links, all catalog PDF hashes/pages and historical-byte preservation. No substantive whole-row, accounting or human acceptance.','procedure':'python3 -B '+B+'p15-reference-validator-v5.py','recursion_boundary':'Traverse current coverage, reconciliation, retained active assessments and prior-work references. Preserve v2/v3/v4 repair and check reports as historical, checking their recorded inputs against saved before-images. Retained supervisor reports and snapshots are source records, not current acceptance. old_reference edges are deliberately archival. Output self-hashes excluded.','visited_records':sorted(seen),'checked_edges':edges,'markdown_dependencies':mdlinks,'historical_classifications':historical,'historical_input_checks':historical_input_checks,'retained_v4_changed_rows':changed_rows,'changed_rows':[],'aggregate_counts':counts,'catalog_checks':catalog_results,'pdf_anchors':pdfcache,'input_hashes':pins,'changed_files':changed,'inventory_scope':'This slice through validation outputs; process captures and final completion inventory are produced afterward.','final_document_hashes':{n:pins[n] for n in ['data/accounting-master/deliverables/P15/coverage.json','data/accounting-master/deliverables/P15/result.md','data/accounting-master/deliverables/P15/progress.md']},'errors':errors,'unresolved_substantive_findings':['Remaining provisional assessments and gap-specific obligations','P15 initial-profile comparison','Independent bounded review and full P15 substantive review','Accounting/forecast validity and human acceptance'],'product_implemented':False,'human_acceptance':'pending'}
with (ROOT/OUT).open('x') as f:json.dump(report,f,indent=2,ensure_ascii=False);f.write('\n')
for x in mdlinks:
 if x['target'] in OUTPUTS:assert load(ROOT/x['target']),x
print(json.dumps({'passed':not errors,'edges':len(edges),'visited':len(seen),'counts':counts,'errors':errors},indent=2))
sys.exit(bool(errors))
