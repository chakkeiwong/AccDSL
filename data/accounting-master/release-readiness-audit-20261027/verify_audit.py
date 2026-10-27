"""Check the audit's own completeness and integrity; not manuscript acceptance."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,sys
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
checks=[]
def check(n,v,detail=None):checks.append({'check':n,'pass':bool(v),'detail':detail})
def load(n):return json.loads((H/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=load('baseline.json');inv=load('inventory.json');rw=load('requirement-crosswalk.json');pm=load('package-release-map.json');fw=load('failure-release-crosswalk.json');cov=load('review-coverage.json');g=load('release-gap-register.json')
a=json.loads((H/'cutoff-v550'/b['active_execution']['current_audit']).read_text())
for name,pred in [('obligations',53),('interactions',6),('operations',46),('literature',9)]:
 src=a['literature'] if name=='literature' else a['groups'][name];actual=[r for r in rw['rows'] if r['group']==name];check(name+'_exact_ids',len(actual)==pred and {x['id'] for x in actual}=={x['id'] for x in src});check(name+'_no_closure',all(x['full_requirement_closed'] is False for x in actual))
check('requirements_unique',len({r['id'] for r in rw['rows']})==114)
check('MC_original_acceptance_preserved',all(x['original_requirement'] and x['original_requirement']['acceptance'] for x in rw['rows'] if x['id'].startswith('MC')))
check('18_packages',len(pm)==18 and {p['id'] for p in pm}=={f'W{i:02d}' for i in range(1,19)})
check('all_rows_mapped',all(r['closure_packages'] and r['release_gaps'] and r['closure_steps'] for r in rw['rows']))
check('201_failure_rows',len(fw['rows'])==201 and fw['counts']=={'original':67,'literature_extensions':48,'cross_interface':86})
check('failure_ids_unique',len({(r['group'],r['id']) for r in fw['rows']})==201)
check('nine_release_gaps',len(g['gaps'])==9 and {r['id'] for r in g['gaps']}=={f'R{i:02d}' for i in range(1,10)})
check('43_source_and_compiled_chapters',len(cov['chapters'])==43==cov['compiled_chapter_bookmarks'])
check('coverage_not_overclaimed',all(x['continuous_read']=='not_checked' and x['independent_human_acceptance']=='pending' for x in cov['chapters']))
check('five_pages_inspected',len(cov['rendered_pages'])==5)
check('citation_and_structure_integrity',not any(inv[k] for k in ['missing_citation_keys','duplicate_bib_keys','duplicate_labels','unresolved_inputs']))
check('all_source_hashes_preserved',all((R/p).exists() and sha(R/p)==h for p,h in b['source_files'].items()))
check('both_PDF_hashes_preserved',all(sha(R/p)==h for p,h in b['pdfs'].items()))
json_fail=[]
for p in H.glob('*.json'):
 try:json.loads(p.read_text())
 except Exception as e:json_fail.append([p.name,str(e)])
check('audit_JSON_parse',not json_fail,json_fail)
links=[]
for p in [H/'result.md',R/'docs/plans/accounting-release-closure-20261027.md']:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not (p.parent/link.split('#')[0]).exists():links.append([str(p.relative_to(R)),link])
check('report_plan_links',not links,links)
nav=load('navigation-changes.json');current=json.loads((R/'data/accounting-master/next-plan.json').read_text());before=json.loads((H/'navigation-before-v551/data/accounting-master/next-plan.json').read_text());v=json.loads(json.dumps(current));v['active_execution'].pop('release_readiness_audit',None);before['active_execution'].pop('release_readiness_audit',None);check('active_master_preserved',v==before)
check('navigation_still_present',all('release-readiness-audit-20261027/result.md' in (R/x['path']).read_text() for x in nav['changes']))
status={'audit_checks_pass':all(x['pass'] for x in checks),'checks':checks,'audited_candidate':b['candidate'],'live_candidate_at_verification':current['active_execution']['current_candidate'],'claim_limit':'Audit integrity only; no mathematical, accounting, reader, runtime or release acceptance follows.'};(H/'verification.json').write_text(json.dumps(status,indent=2)+chr(10));print(json.dumps({'passed':sum(x['pass'] for x in checks),'total':len(checks),'failed':[x for x in checks if not x['pass']],'live':status['live_candidate_at_verification']},indent=2));sys.exit(0 if status['audit_checks_pass'] else 1)
