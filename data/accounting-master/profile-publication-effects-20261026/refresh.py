"""Refresh active routing once, preserving prior controls as historical evidence."""
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REL=HERE.relative_to(ROOT).as_posix()
NEXT='docs/plans/accounting-profile-composition-boundary-20261026.md'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
assert not (HERE/'control-refresh.json').exists(),'already refreshed'
checks=json.loads((HERE/'checks.json').read_text())
assert checks['status']=='passed_bounded_documentary_conformance'
manifest=json.loads((HERE/'run-manifest.json').read_text())
for p,h in manifest['artifacts'].items():
    if p.endswith('.py') or p.endswith('.jsonl') or p.endswith('/checks.json') or p.endswith('/source-lock.json'):
        assert digest(ROOT/p)==h,p
assert (ROOT/NEXT).exists() and (HERE/'result.md').exists()
names=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md',
 'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
 'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
 'data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
 'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
note=f'''## Publication effects checked — 26 October 2026

Version 4.40 remains 534 pages, not_ready. S1–S5 partial; S6 held; S7/E3 deferred.
PublicationEffects/1 checks 1,892 retained exchanges, 412 crash worlds/retries
and 70 negative/independence cases. Query publication, component updates,
legal-account changes and journals retain their separate native meanings.
No frozen source or manuscript changed; no whole requirement closes.
Result: {REL}/result.md.
Next plan: {NEXT}.

'''
concise=f'''# Current AccDSL master program

{note}Mission: represent disclosed company histories and alternatives, then simulate
explicit economic events into coherent journals, statements and notes.

| Phase | Remaining work | Status |
|---|---|---|
| S1 Research | Consequential source/version matching and build/reuse comparison | Partial |
| S2 Architecture | Shared method composition and broader group/sector state | Partial |
| S3 Language | Common authoring, broader measurements and fiscal policies | Partial |
| S4 Conformance | Real-source company cases, integrated methods and broader recovery | Partial |
| S5 Governing design | Integration, consistency, implementability and human review | Partial |
| S6 Product implementation | Await sufficiently settled specification | Held |
| S7 Predictive evaluation | Saved E3 choices retained; simulator design first | Deferred |

Current question: which exact native state and information dependencies permit
a finite composition, and which need an explicit adapter or unresolved finding?
Next action: inspect retained InsuranceComponents/1 and InsuranceAssessment/1
state bindings, then check matched native and incompatible composition cases.

Full residuals: data/accounting-master/current-design-reconciliation-20261025/remaining-work.md.
All 53 obligations, six interactions and 46 operations remain in that audit.
PDF: docs/design/proposal/manuscript-authoring-scope-20261026/accounting-product-proposal.pdf
SHA256: {checks['governing_pdf_sha256']}.
No background process is running. Preserve frozen evidence and unrelated work.
'''
before={}
compact=set(names[:2]+['data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md'])
for name in names:
    path=ROOT/name;before[name]=digest(path);saved=HERE/'control-before'/name
    saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(path.read_bytes())
    if name in compact:path.write_text(concise)
    elif path.suffix=='.md':
        title,rest=path.read_text().split('\n',1);path.write_text(title+'\n\n'+note+rest.lstrip('\n'))
path=ROOT/'data/accounting-master/next-plan.json';doc=json.loads(path.read_text());active=doc['active_execution']
active.update(updated='2026-10-26',active_work_plan=NEXT,latest_result=REL+'/result.md')
active['latest_results'].append(REL+'/result.md')
active['completed_increments'].append('PublicationEffects/1: exact retained publication/financial/unknown-acknowledgement distinctions verified')
active['next']=['Specify exact-profile composition and matched text/typed authoring with meaningful incompatibilities',
 'Integrate checked identity, publication and composition repairs into a preserved manuscript successor',
 'Continue wider methods, actual-company inputs and consequential source/version work; E3 stays deferred']
dump(path,doc)
path=ROOT/'scripts/accounting_master_catalog.json';doc=json.loads(path.read_text())
doc['active_execution_note'].update(updated='2026-10-26',active_work_plan=NEXT,latest_result=REL+'/result.md',current_candidate='4.40;534 pages;not_ready');dump(path,doc)
dump(HERE/'coverage-delta.json',{'baseline':'data/accounting-master/current-design-reconciliation-20261025/coverage.json',
 'affected':['MC20','MC24','MC25','MC33','MC34','G2','G18','I04','P17-07.08'],
 'evidence':REL+'/result.md','whole_rows_closed':0,'counts_preserved':{'obligations':53,'interactions':6,'operations':46},'next_plan':NEXT})
dump(HERE/'control-refresh.json',{'before':before,'after':{n:digest(ROOT/n) for n in names},'next_plan':NEXT})
for name in ['contract.md','recovery-note.md','result.md','coverage-delta.json','refresh.py']:
    manifest['artifacts'][REL+'/'+name]=digest(HERE/name)
manifest['control_refresh_command']='python3 '+REL+'/refresh.py';dump(HERE/'run-manifest.json',manifest)
print(json.dumps({'controls':len(names),'next_plan':NEXT,'readiness':'not_ready'}))
