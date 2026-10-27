"""Advance checked controls and stable navigation, preserving all prior bytes."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os,subprocess,sys
import fitz
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+NL)
v=json.loads((HERE/'verification.json').read_text())
assert v['version']=='5.1' and v['passed_preservation'] and not v['new_warnings']
assert sha(ROOT/v['pdf'])==v['pdf_sha256'] and (HERE/'review.md').exists()
target=(ROOT/v['pdf']).parent
standalone=target/'simulation-foundations.pdf'
original=ROOT/'docs/design/proposal/manuscript-simulation-foundations-20261026/simulation-foundations.pdf'
a,b=fitz.open(standalone),fitz.open(original)
assert len(a)==len(b)==170 and [p.get_text() for p in a]==[p.get_text() for p in b]
log=(target/'simulation-foundations.log').read_text(errors='replace')
assert not any(x in log for x in ['Overfull','undefined','Missing character:','LaTeX Error'])
plan='docs/plans/accounting-invariant-source-authoring-20261026.md'
result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
assert (ROOT/plan).exists()
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
controls=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
navigation=['MISSION_CONTROL.md','docs/README.md','docs/design/README.md','data/accounting-master/recovery-current-20261026.md']
backup=HERE/'control-before';assert not backup.exists()
before={n:(ROOT/n).read_bytes() for n in controls+navigation}
for n,data in before.items():
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
note=NL.join(['## Current governing candidate — Version 5.1 — 26 October 2026','',
 'Version 5.1 is the 715-page governing design candidate, not_ready. It retains',
 'all 26 simulation chapters and the checked language-scope revision. Exact bank',
 'profile adoption now has 33 retained publications, 30 timing cases, 42 replays,',
 '28 additional controls and 63 reconstructible packages. All 211 predecessor',
 'sources are preserved; no new build warnings. Cover/pages 674–677 inspected.',
 'All 53 obligations, six interactions and 46 operations remain; no whole',
 'requirement closes. S1–S5 partial, S6 held and E3 deferred.',
 'PDF: '+v['pdf'],'SHA256: '+v['pdf_sha256']+'.',
 'Result: '+result+'.','Next plan: '+plan+'.','',''])
proposed={}
for n in concise:
 old=before[n].decode();tail=old[old.index('Mission:'):]
 lines=[]
 for line in tail.splitlines():
  if line.startswith('Current question:'):line='Current question: can explicit invariant source preserve exact typed rules and complete company-program behaviour?'
  elif line.startswith('Next action:'):line='Next action: execute '+plan+'.'
  elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
  lines.append(line)
 proposed[n]='# Current AccDSL master program'+NL*2+note+NL.join(lines)+NL
for n in historical:
 first,rest=before[n].decode().split(NL,1)
 rest=rest.replace('## Current governing candidate — Version 5.0 — 26 October 2026','## Prior governing candidate — Version 5.0 — 26 October 2026',1)
 proposed[n]=first+NL*2+note+rest.lstrip(NL)
updates={'active_work_plan':plan,'latest_result':result,'current_candidate':'5.1;715 pages;not_ready',
 'current_pdf':v['pdf'],'current_pdf_sha256':v['pdf_sha256'],'remaining_work':remaining}
n='data/accounting-master/next-plan.json';d=json.loads(before[n]);active=d['active_execution'];active.update(updates)
active['next']=['Audit explicit invariant grammar and retained typed ownership','Author the finite invariant source and compare complete two-chart results','Integrate checked invariant authoring while retaining simulation foundations; S6 held, E3 deferred']
active['completed_increments'].append('Version5.1:715 pages;26 simulation chapters retained;explicit exact-time bank profile;63 complete packages;stable links and controls reconciled')
active['latest_results'].extend(['data/accounting-master/exact-bank-request-conformance-20261026/result.md','data/accounting-master/exact-bank-profile-adoption-20261026/result.md',result])
proposed[n]=json.dumps(d,indent=2)+NL
n='scripts/accounting_master_catalog.json';d=json.loads(before[n]);d['active_execution_note'].update(updates);proposed[n]=json.dumps(d,indent=2)+NL
n='MISSION_CONTROL.md';text=before[n].decode();assert 'Version 5.0 is the current 714-page' in text
text=text.replace('Version 5.0 is the current 714-page','Version 5.1 is the current 715-page',1)
text=text.replace('## Purpose', 'The [current integration result]('+result+') records exact bank profile adoption, preserved simulation content and repaired navigation. The [active plan]('+plan+') continues explicit invariant authoring.'+NL*2+'## Purpose',1);proposed[n]=text
n='docs/README.md';text=before[n].decode().replace('**Version 5.0, 714 pages**','**Version 5.1, 715 pages**',1)
text=text.replace('- [Documentation result and checks]', '- [Current integration and checks](../'+result+').'+NL+'- [Documentation result and checks]',1);proposed[n]=text
n='docs/design/README.md';proposed[n]=before[n].decode().replace('Version 5.0,','Version 5.1,',1)
n='data/accounting-master/recovery-current-20261026.md';proposed[n]='# Current recovery pointer'+NL*2+note+'Next: audit and implement bounded explicit invariant source; bank adoption and manuscript integration are complete.'+NL+'Ten controls and four stable links agree. Do not rerun completed writers. No background process running.'+NL
prior=(HERE.parent/'language-scope-reconciliation-20261026/remaining-work.md').read_text()
prior=prior[:prior.index('## Next dependency')].replace('Version 4.50, 546 pages','Version 5.1, 715 pages')
prior=prior.replace('Native bank exact-time and insurer identity successors are not automatically adopted','Bank exact-time adoption now has finite documentary evidence; insurer identity adoption and general migration remain')
prior+=NL.join(['## Next dependency','',
 'Full-request timing and explicit BankAssessmentExactTime/1 conversion are now',
 'checked within their finite scopes. Preserve all simulation foundations and',
 'the 4.50 language revision. Execute '+plan+'.',
 'The current common program still imports its whole invariant as a hashed',
 'typed definition. Expose that bounded algorithm as explicit declarations,',
 'lower to the same evaluator and preserve complete outcomes and unknowns.','',
 'The 26 simulation chapters add design and 67 failure mechanisms, not runtime',
 'or empirical acceptance. Their family/information/pricing interfaces and',
 'adversarial examples remain part of S2/S4; source/code correspondence remains',
 'S1. Broader real-source histories, fiscal rules, sector/group composition and',
 'whole-document independent acceptance remain. Do not repeat exhausted source',
 'routes without new leads. S6 held; E3 deferred.',''])
(HERE/'remaining-work.md').write_text(prior)
for n,text in proposed.items():
 assert (ROOT/n).read_bytes()==before[n],'concurrent_control_change:'+n
 (ROOT/n).write_text(text)
links={'docs/AccDSL-latest.pdf':target/'accounting-product-proposal.pdf',
 'docs/AccDSL-latest.tex':target/'accounting-product-proposal.tex',
 'docs/AccDSL-simulation-foundations.pdf':standalone,
 'docs/AccDSL-simulation-foundations.tex':target/'simulation-foundations.tex'}
link_rows=[]
for name,destination in links.items():
 p=ROOT/name;assert destination.exists() and destination.is_relative_to(ROOT)
 assert p.is_symlink() or not p.exists(),'non_link_navigation:'+name
 old=os.readlink(p) if p.is_symlink() else None
 relative=os.path.relpath(destination,p.parent);temp=p.with_name(p.name+'.next')
 assert not temp.exists() and not temp.is_symlink()
 os.symlink(relative,temp);os.replace(temp,p)
 assert p.resolve()==destination.resolve()
 link_rows.append({'path':name,'before_target':old,'after_target':relative,'sha256':sha(p)})
original_scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in json.loads(original_scope.read_text())['groups'].items()};assert counts=={'obligations':53,'interactions':6,'operations':46}
for n in controls:
 text=(ROOT/n).read_text();assert plan in text and v['pdf_sha256'] in text,n
dump(HERE/'control-refresh.json',{'next_plan':plan,'updated_files':{n:{'before':sha256(data).hexdigest(),'after':sha(ROOT/n)} for n,data in before.items()},
 'links':link_rows,'original_scope':counts,'whole_requirements_closed':0,'ten_controls_agree':True,
 'standalone_pages':170,'standalone_full_text_equal':True,'standalone_pdf_sha256':sha(standalone)})
dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'commands':['integrate.py prepare','integrate.py build','integrate.py verify','latexmk -lualatex -silent -g -interaction=nonstopmode -halt-on-error simulation-foundations.tex','advance.py'],
 'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic',
 'wall_seconds':json.loads((HERE/'build.json').read_text())['wall_seconds'],'wall_time_scope':'Main document build only',
 'standalone_build_repair':'Set TEXMFVAR and TEXMFCACHE to /tmp/accdsl-bank-profile-tex-cache after initial missing writable cache',
 'data_version':sha(original_scope),'plan_file':'docs/plans/accounting-bank-time-manuscript-integration-20261026.md',
 'result_file':result,'artifact_paths':['source-preservation.json','verification.json','review.md','control-refresh.json','remaining-work.md'],
 'timestamp_utc':datetime.now(timezone.utc).isoformat()})
print(json.dumps({'candidate':updates['current_candidate'],'controls':len(controls),'stable_links':len(links),'next_plan':plan}))
