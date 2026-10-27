"""Record bounded render review and update active controls without legacy rewrites."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
REL=HERE.relative_to(ROOT).as_posix(); PLAN='docs/plans/accounting-company-portable-authoring-20261023.md'
PDF='docs/design/proposal/manuscript-company-language-20261023/accounting-product-proposal.pdf'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert not (HERE/'control-refresh.json').exists()
 v=json.loads((HERE/'verification.json').read_text()); assert v['passed'] and v['pages']==415
 assert sha(ROOT/PDF)==v['pdf_sha256']
 pages=[1,98,99,108,109,110,378,379,380,381,382,383]
 dump(HERE/'render-review.json',{'pdf':PDF,'pdf_sha256':v['pdf_sha256'],'actual_pages_inspected':pages,'page_hashes':{str(n):sha(HERE/'render'/f'{n}.png') for n in pages},'continuous_segments':[[378,379,380],[381,382,383]],'review':REL+'/review.md','scope':'Bounded author reading; no independent or whole-document acceptance'})
 inventory=json.loads((ROOT/'data/accounting-master/language-scope-review-20261023/inventory.json').read_text())
 advanced={'MC05','MC08','MC10','MC11','MC12','MC13','MC14','MC15','MC16','MC18','MC23','MC24','MC25','MC26','MC28','MC32','MC34','G2','G6','G13','G14','G15','G18'}
 rows=[{'id':r['id'],'original_obligation':r['prior_record'].get('original_obligation',r['prior_record'].get('label')),'prior_review':r['review'],'new_evidence':'Version 3.54 integrates bounded timing/family/expression/recovery design' if r['id'] in advanced else 'No new method evidence; original residual retained','full_requirement_closed':False} for r in inventory['obligations']]
 dump(HERE/'coverage-delta.json',{'candidate_version':'3.54','candidate_pdf':PDF,'candidate_pdf_sha256':v['pdf_sha256'],'readiness':'not_ready','obligation_count':53,'interaction_count':6,'operation_count':46,'rows':rows,'interactions':inventory['interactions'],'operations':inventory['operations'],'whole_rows_closed':0,'scope':'Bounded integration, not complete fresh method or full-manuscript review'})
 names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
 note=('## 23 October 2026 — current candidate Version 3.54\n\n'
 'Version 3.54 is 415 pages, not_ready, at '+PDF+'.\n'
 'SHA256: '+v['pdf_sha256']+'.\n'
 'Version 3.53 and 149 predecessor sources remain protected; all 307 labels,\n'
 '92 references, 729 citations and 219 displays are retained. Corrected build\n'
 'and bounded author reading of twelve pages pass; full successor reading and\n'
 'independent/domain/human acceptance remain pending.\n'
 'Result: '+REL+'/result.md.\n\n'
 'The candidate integrates policy information (93 checks), authored families\n'
 '(96), typed policy expressions (79) and member-boundary recovery (57), all\n'
 'replayed. Scope review preserves 53 obligations, six interactions and 46\n'
 'operations. General language, richer modules, actual source admission and\n'
 'physical durability remain open; no whole requirement closes.\n\n'
 'Next: '+PLAN+'.\n'
 'Preserve draft identity while connecting explicit typed portable references,\n'
 'dependencies and replay. S1–S5 remain partial, S6 held, S7 deferred. Older\n'
 'entries below are historical checkpoints.\n\n')
 before={}
 for n in names:
  p=ROOT/n; before[n]=sha(p); dest=HERE/'control-before'/n
  dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(p.read_bytes())
  if n.endswith('.md'):
   title,rest=p.read_text().split('\n',1)
   if 'simulator-session' in n: rest='No active diagnostic. All recorded increments have read-only replay.\nDo not repeat manuscript preparation/build/finish or one-time recordings.\nPreserve dirty work; no commit, subagent, controller campaign, outreach or forecast experiment.\nNext inspect existing portable encoder and company exchange; no new generic serializer.\n'
   p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
 p=ROOT/'data/accounting-master/next-plan.json'; d=json.loads(p.read_text()); old={k:v for k,v in d.items() if k!='active_execution'}
 a=d['active_execution']; a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',current_candidate={'version':'3.54','pages':415,'status':'not_ready','pdf':PDF,'sha256':v['pdf_sha256']})
 a['latest_results'].append(a['latest_result']); a['completed_increments'].append('Version3.54:415 pages;149 baseline sources/protected math retained;12 rendered pages inspected;not_ready')
 a['next'][0]='Connect draft family/expression/recovery identities to the existing portable exchange boundary, preserving unknowns and no-admission semantics'
 dump(p,d); assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution'}
 p=ROOT/'scripts/accounting_master_catalog.json'; d=json.loads(p.read_text()); old={k:v for k,v in d.items() if k!='active_execution_note'}
 d['active_execution_note'].update(active_work_plan=PLAN,latest_result=REL+'/result.md',current_candidate='3.54;415 pages;not_ready'); dump(p,d)
 assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution_note'}
 dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True,'whole_rows_closed':0})
 build=json.loads((HERE/'build.json').read_text())
 dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-company-language-integration-20261023.md','result':REL+'/result.md','build':build,'cpu_gpu':'CPU only; GPU intentionally hidden','random_seeds':'N/A: document integration','data_version':str((HERE/'baseline.json').relative_to(ROOT)),'candidate_pdf':PDF,'candidate_pdf_sha256':v['pdf_sha256'],'independent_acceptance':'pending','files':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.is_file()}})
 print(json.dumps({'candidate':'3.54','pages':415,'controls':len(names),'next':PLAN,'legacy_fields_unchanged':True}))
if __name__=='__main__': main()
