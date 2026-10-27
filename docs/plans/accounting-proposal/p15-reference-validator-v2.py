#!/usr/bin/env python3
"""One-off P15 document reference diagnostic; no product or substantive acceptance."""
from pathlib import Path
import hashlib,json,re,subprocess,datetime,sys
ROOT=Path(__file__).resolve().parents[3]; B='docs/plans/accounting-proposal/'
OUT=B+'p15-reference-validation-v2.json'; AV=B+'p15-assessment-validation-v2.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
errors=[];edges=[];pins={};seen=set();historical=[];pdfcache={};mdlinks=[]
OUTPUTS={OUT,AV}
ARCHIVE_NAMES={'p15-assessment-validation-v1.json','p15-register-validation-v1.json','p15-assessment-check-v1.meta.json','p15-assessment-check-v1.stdout.json','p15-evidence-assessments-v1.json'}
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
    if (('/evidence-v1/' in name or '/evidence-v2/' in name) and p.name!='capture-manifest.json') or p.name in ARCHIVE_NAMES or (p.name.endswith('-v1.json') and ('check' in p.name or 'validation' in p.name)):
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
 if ('/evidence-v1/' in name or '/evidence-v2/' in name) and Path(name).name!='capture-manifest.json':
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
roots=['data/accounting-master/deliverables/P15/coverage.json',B+'p15-evidence-assessments-v2.json',B+'p15-evidence-assessments-v2.md',B+'p15-prior-work-v1.json',B+'p15-prior-work-v1.md',B+'p15-reference-repair-v2.json',B+'p15-reference-repair-v2.md',B+'evidence-v2/capture-manifest.json','data/accounting-master/deliverables/P15/result.md','data/accounting-master/deliverables/P15/progress.md']
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
manifest=load(ROOT/(B+'evidence-v2/capture-manifest.json'))
for x in manifest['preserved_preexisting_records']+manifest['protected_files']:
 checkpath(x['path'],x['sha256'],'preservation inventory',allow_empty=True)
# Every added or changed file is included. Historical v1 records must not change.
oldpaths={x['path']:x['sha256'] for x in manifest['preserved_preexisting_records']}
files=[p for p in (ROOT/B).rglob('*') if p.is_file()]+[ROOT/p for p in ['data/accounting-master/deliverables/P15/coverage.json','data/accounting-master/deliverables/P15/result.md','data/accounting-master/deliverables/P15/progress.md']]
changed=sorted(p.relative_to(ROOT).as_posix() for p in files if p.relative_to(ROOT).as_posix() not in oldpaths or sha(p)!=oldpaths[p.relative_to(ROOT).as_posix()])
changed=sorted(set(changed)|OUTPUTS)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
assessment={'schema_version':'accdsl.proposal.p15.assessment_validation.v2','created_at':now,'passed':not errors,'scope':'Reference integrity of the eight preserved assessments; no substantive acceptance.','procedure':'python3 -B '+B+'p15-reference-validator-v2.py','validator':{'path':B+'p15-reference-validator-v2.py','sha256':sha(Path(__file__))},'inputs':{k:{'path':B+p,'sha256':sha(ROOT/(B+p))} for k,p in [('assessment','p15-evidence-assessments-v2.json'),('companion','p15-evidence-assessments-v2.md')]},'checked_ids':a2['completed_ids'],'substantive_rows_unchanged':a1['requirements']==a2['requirements'] and a1['gaps']==a2['gaps'],'remaining_count':45,'checked_edges':[e for e in edges if 'p15-evidence-assessments-v2' in e['owner']],'errors':errors,'historical_validation':'p15-assessment-validation-v1.json preserved unchanged, not rerun.'}
if '--probe' in sys.argv:
 print(json.dumps({'passed':not errors,'errors':errors,'counts':counts,'edges':len(edges),'visited':len(seen)},indent=2));sys.exit(bool(errors))
# Outputs use exclusive creation; a retry must use a new version, never overwrite.
for name,doc in [(AV,assessment)]:
 with (ROOT/name).open('x') as f:json.dump(doc,f,indent=2,ensure_ascii=False);f.write('\n')
pins[AV]=sha(ROOT/AV)
report={'schema_version':'accdsl.proposal.p15.reference_validation.v2','created_at':now,'passed':not errors,'scope':'Canonical paths, byte hashes, recursively visited active proposal dependencies, RFC 6901 pointers, text lines, exact quotes, PDF physical pages/section text, Markdown links, all catalog PDF hashes/pages and historical-byte preservation. No substantive whole-row, accounting or human acceptance.','procedure':'python3 -B '+B+'p15-reference-validator-v2.py','recursion_boundary':'Traverse active coverage, assessments, prior-work register, history inspection, repair record and Markdown dependencies; retained supervisor reports and before-snapshots are source evidence with their own historical inputs, not active revalidation graphs. old_reference edges are deliberately archival. Output self-hashes excluded.','visited_records':sorted(seen),'checked_edges':edges,'markdown_dependencies':mdlinks,'historical_classifications':historical,'aggregate_counts':counts,'catalog_checks':catalog_results,'pdf_anchors':pdfcache,'input_hashes':pins,'changed_files':changed,'errors':errors,'unresolved_substantive_findings':load(ROOT/(B+'p15-reference-repair-v2.json'))['deferred_work'],'product_implemented':False,'human_acceptance':'pending'}
with (ROOT/OUT).open('x') as f:json.dump(report,f,indent=2,ensure_ascii=False);f.write('\n')
for x in mdlinks:
 if x['target'] in OUTPUTS:assert load(ROOT/x['target']),x
print(json.dumps({'passed':not errors,'edges':len(edges),'visited':len(seen),'counts':counts,'errors':errors},indent=2))
sys.exit(bool(errors))
