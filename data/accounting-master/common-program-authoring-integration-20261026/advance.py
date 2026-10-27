"""Advance current pointers after the checked and rendered 4.49 successor."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,sys,subprocess,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+NL)
started=time.monotonic();v=json.loads((HERE/'verification.json').read_text())
assert v['version']=='4.49' and not v['new_warnings'] and v['passed_preservation']
assert sha(ROOT/v['pdf'])==v['pdf_sha256'] and (HERE/'review.md').exists()
checks=json.loads((HERE.parent/'common-program-authoring-20261026/checks.json').read_text());assert checks['passed']
original=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
original_sha=sha(original);counts={k:len(x) for k,x in json.loads(original.read_text())['groups'].items()}
assert counts=={'obligations':53,'interactions':6,'operations':46}
plan='docs/plans/accounting-language-scope-reconciliation-20261026.md'
result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
targets=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
backup=HERE/'control-before';assert not backup.exists()
before={n:(ROOT/n).read_bytes() for n in targets}
for n,b in before.items():
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
note=NL.join(['## Common program authoring integrated — 26 October 2026','',
 'Version 4.49 is 545 pages, not_ready. Complete source reconstructs both saved',
 'programs and all 22 command results. Nineteen structural and six matched native',
 'refusals pass; a direct half-collection edit changes the guarded outcome and',
 'refuses under the selected full-payment contract. All 183 predecessor sources',
 'preserved; no new warnings. Cover and physical pages 510–512 read.',
 'All 53 obligations, six interactions and 46 operations remain. S1–S5 partial;',
 'S6 held, E3 deferred. Next: reconcile the main language scope explanation.',
 'PDF: '+v['pdf'],'SHA256: '+v['pdf_sha256']+'.',
 'Result: '+result+'.','Next plan: '+plan+'.','',''])
tail=NL.join(['Mission: represent disclosed company histories and alternatives, then simulate',
 'explicit economic events into coherent journals, statements and notes.','',
 '| Phase | Remaining work | Status |','|---|---|---|',
 '| S1 Research | Technical source/version matching and actual accounting authority | Partial |',
 '| S2 Architecture | Wider common state/effects and group/sector composition | Partial |',
 '| S3 Language | General invariant/rule authoring, broader measurements and fiscal policies | Partial |',
 '| S4 Conformance | Actual-source partial history, wider interactions and recovery | Partial |',
 '| S5 Governing design | Main-chapter consistency, whole-document review and acceptance | Partial |',
 '| S6 Product implementation | Await sufficiently settled specification | Held |',
 '| S7 Predictive evaluation | Saved E3 choices retained; simulator design first | Deferred |','',
 'Current question: does the main language chapter explain the present authoring responsibilities and limits?',
 'Next action: execute '+plan+'.','Current residuals: '+remaining+'.',
 'Original all-row audit: data/accounting-master/current-design-reconciliation-20261025/remaining-work.md.',
 'No background process is running. Preserve frozen evidence and unrelated work.',''])
for n in concise:(ROOT/n).write_text('# Current AccDSL master program'+NL*2+note+tail)
for n in historical:
 first,rest=before[n].decode().split(NL,1);(ROOT/n).write_text(first+NL*2+note+rest.lstrip(NL))
updates={'active_work_plan':plan,'latest_result':result,'current_candidate':'4.49;545 pages;not_ready',
 'current_pdf':v['pdf'],'current_pdf_sha256':v['pdf_sha256'],'remaining_work':remaining}
p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(before[str(p.relative_to(ROOT))]);a=d['active_execution'];a.update(updates)
a['next']=['Read and map the main language scope argument against current checked capabilities','Repair the bounded explanation if substantiated; preserve all prior substance','Reassess wider method/source/state work; S6 held and E3 deferred']
a['completed_increments'].append('Version4.49:545 pages;common program text;22 exact commands;19 structural and6 native refusals;direct source algorithm edit')
a['latest_results'].extend(['data/accounting-master/common-program-authoring-audit-20261026/result.md','data/accounting-master/common-program-authoring-20261026/result.md',result])
dump(p,d)
p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(before[str(p.relative_to(ROOT))]);d['active_execution_note'].update(updates);dump(p,d)
remaining_text=(HERE.parent/'post-authoring-program-refresh-20261026/remaining-work.md').read_text()
remaining_text=remaining_text.replace('Version 4.48, 544 pages','Version 4.49, 545 pages')
remaining_text=remaining_text.replace('## Next dependency', '## Previous dependency (completed)')
remaining_text=remaining_text[:remaining_text.index('## Previous dependency (completed)')]+NL.join([
 '## Next dependency','', 'The common source audit and implementation are complete within their bounded',
 'profiles: two exact eleven-command programs, explicit imported invariants and',
 'native contract choice, full intent, source algorithm edits and refusal checks.',
 'General invariant algorithms remain typed resources. Broader financial methods',
 'and actual source applicability remain open. No whole requirement closes.','',
 'Next execute '+plan+'.',
 'The main language opening still narrates older subsets in historical order.',
 'Inspect and map that discussion before editing; make current authoring duties',
 'and remaining gaps understandable without treating this as whole-document review.','',
 'S1 source gaps need genuinely new leads: the excluded Gentry leaves were already',
 'checked and contain no technical text. Repeating that retrieval cannot help.',
 'EPS additivity is already derived for its declared model; general nonadditive',
 'selection still needs authority. Do not replace either gap with another proxy.',''])
remaining_text=remaining_text.replace('One coherent program text for authored methods, registries, invariant selection and full event intent; wider algorithms','General rule/invariant authoring, broader algorithms and authoring usability')
remaining_text=remaining_text.replace('Execute common-program authoring inventory, then explicit grammar and semantic ownership; compare complete source/typed/native programs and consequential edits','Retain checked common source; reconcile main explanation, then extend a justified wider method with exact comparisons')
(HERE/'remaining-work.md').write_text(remaining_text)
for n in targets:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text(),n
assert sha(original)==original_sha
dump(HERE/'control-refresh.json',{'next_plan':plan,'updated_files':{n:{'before':sha256(b).hexdigest(),'after':sha(ROOT/n)} for n,b in before.items()},'original_scope':counts,'whole_requirements_closed':0})
dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'commands':['integrate.py prepare','integrate.py build','integrate.py verify','repair-layout.py','integrate.py build','integrate.py verify','advance.py'],
 'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden during build','random_seeds':'N/A deterministic',
 'wall_seconds':time.monotonic()-started,'build_wall_seconds':json.loads((HERE/'build.json').read_text())['wall_seconds'],
 'data_version':original_sha,'plan_file':'docs/plans/accounting-common-program-authoring-20261026.md','result_file':result,
 'artifact_paths':['baseline.json','build.json','verification.json','review.md','control-refresh.json','remaining-work.md'],
 'timestamp_utc':datetime.now(timezone.utc).isoformat()})
(ROOT/'data/accounting-master/recovery-current-20261026.md').write_text('# Current recovery pointer'+NL*2+
 'Version 4.49, 545 pages, not_ready. PDF: '+v['pdf']+NL+'SHA256: '+v['pdf_sha256']+NL+
 'Active plan: '+plan+NL+'Next: read and map the current main language scope discussion.'+NL+
 'Ten controls agree. Do not rerun completed writers/verifiers pinned by successors.'+NL+
 'No background process running. E3 deferred. Original scope 53/6/46 preserved.'+NL)
print(json.dumps({'candidate':updates['current_candidate'],'controls':len(targets),'original_scope':counts,'next_plan':plan}))
