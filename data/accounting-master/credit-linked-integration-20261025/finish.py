"""Refresh the current master controls after scoped rendered acceptance."""
from pathlib import Path
from hashlib import sha256
import json
import platform
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
NEXT = 'docs/plans/accounting-credit-host-boundary-20261025.md'
PRIOR = 'data/accounting-master/insurance-statement-integration-20261025/coverage.json'
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p, value): p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

assert not (HERE / 'control-refresh.json').exists()
check = runpy.run_path(str(HERE / 'integrate_v2.py'))['verify']()
assert check == json.loads((HERE / 'integration-verification.json').read_text())
assert (ROOT / NEXT).exists() and (HERE / 'review.md').exists()
pages = [1, 408, 409, 410, 411]
dump(HERE / 'render-review.json', {'author_review_complete': True,
    'independent_reader_pending': True, 'whole_document_review': False,
    'pages': pages, 'pdf_sha256': check['pdf_sha256'], 'review': REL + '/review.md',
    'images': {REL + '/page-' + str(n) + '.png': sha(HERE / ('page-' + str(n) + '.png')) for n in pages}})
dump(HERE / 'replay-observation.json', {'passed': True, 'mode': 'read_only_integration_verification',
    'pdf_sha256': check['pdf_sha256'], 'verifier_sha256': sha(HERE / 'integrate_v2.py')})
prior = json.loads((ROOT / PRIOR).read_text())
advanced = {'MC08','MC10','MC11','MC13','MC16','MC17','MC18',
            'MC24','MC25','MC26','MC27','MC28','MC30','MC32','MC33','MC34','MC35'}
coverage = {'schema':'accdsl.coverage.references.v1','date':'2026-10-25','candidate':'4.31',
    'readiness':'not_ready','baseline':{'path':PRIOR,'sha256':sha(ROOT / PRIOR)},
    'next_plan':NEXT,'whole_rows_closed':0}
for group, count in [('obligations',53),('interactions',6),('operations',46)]:
    assert len(prior[group]) == len({r['id'] for r in prior[group]}) == count
    coverage[group] = []
    for row in prior[group]:
        changed = group == 'obligations' and row['id'] in advanced
        coverage[group].append({'id':row['id'], 'prior_ref':{'path':PRIOR,'collection':group,'id':row['id'],
            'sha256':sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()},
            'assessment':'scoped_advance_remaining_open' if changed else 'prior_scope_retained_not_reaudited',
            'advance':'Exact shared-factor credit measurements and bounded equality integrated in4.31.' if changed else 'No new evidence assigned.',
            'residual':'Actual-source and classification admission, broader group/sector methods and full design review remain open.',
            'evidence':[REL+'/result.md',REL+'/integration-verification.json',REL+'/review.md'] if changed else [],
            'full_requirement_closed':False,'acceptance':'not_promoted'})
dump(HERE / 'coverage.json', coverage)
note = f'''## Shared exact credit measurements integrated — 25 October 2026

Version 4.31: {check['pages']} pages, not_ready.
PDF: {check['pdf']}
SHA256: {check['pdf_sha256']}.
23 focused tests,44 regressions,9 schedules and53 native refusals replay.
652 identities,80 authored targets and986 contained enclosures pass.
Exact shared factors preserve57 stages and63 journals; host and accounting admission remain false.
All174 predecessor sources and all existing mathematics/citations remain protected.
Cover and PDF408–411 were viewed; first overfull line repaired, no new warnings, five inherited underfull notices.
All53 obligations,6 interactions,46 operations remain; no whole requirement closes.
Result: {REL}/result.md.
S1–S5 partial; S6 held; S7/E3 deferred. Next: {NEXT}.

'''
phase = f'''Mission: represent disclosed company histories and alternatives, then simulate
explicit economic events into coherent journals, statements and notes.

| Phase | Remaining work | Status |
|---|---|---|
| S1 Research | Consequential source/version matching and build/reuse comparison | Partial |
| S2 Architecture | Broader group/sector methods and actual claim state | Partial |
| S3 Language | Broader measurements, method authoring and fiscal policies | Partial |
| S4 Conformance | Real-source whole-company cases, integrated sector methods and recovery | Partial |
| S5 Governing design | Full implementability, source, domain and human review | Partial |
| S6 Product implementation | Await sufficiently settled governing specification | Held |
| S7 Predictive evaluation | Saved E3 choices retained; simulator design comes first | Deferred |

Current question: how can exact credit expressions cross the company-book boundary with context and dependence intact?
Next action: execute {NEXT}.
Preserve frozen evidence and unrelated work. No paid outreach or background campaign.
'''
names = ['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md',
    'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
    'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
    'data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
    'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before = {}
for name in names:
    p = ROOT / name; before[name] = sha(p)
    saved = HERE / 'control-before' / name; saved.parent.mkdir(parents=True,exist_ok=True); saved.write_bytes(p.read_bytes())
    if p.suffix == '.md':
        title, rest = p.read_text().split('\n',1)
        if name.endswith(('accounting-master-current.md','accounting-current-program-20261025.md','simulator-session-20261023.md')):
            rest = phase
        p.write_text(title + '\n\n' + note + rest.lstrip('\n'))
p = ROOT / 'data/accounting-master/next-plan.json'; d = json.loads(p.read_text()); active = d['active_execution']
active.update(updated='2026-10-25',active_work_plan=NEXT,latest_result=REL+'/result.md',
    current_candidate={'version':'4.31','pages':check['pages'],'status':'not_ready','pdf':check['pdf'],'sha256':check['pdf_sha256']})
for folder in ['credit-linked-measurements-20261025',HERE.name]:
    result = 'data/accounting-master/'+folder+'/result.md'
    if result not in active['latest_results']: active['latest_results'].append(result)
active['completed_increments'].append('Shared exact credit measurements integrated in4.31 with exact replay, preservation and bounded rendered review')
active['next'][0] = 'Audit exact credit amounts at the rational company-book boundary and specify the next supported integration'
dump(p,d)
p = ROOT / 'scripts/accounting_master_catalog.json'; d = json.loads(p.read_text())
d['active_execution_note'].update(updated='2026-10-25',latest_result=REL+'/result.md',
    active_work_plan=NEXT,current_candidate='4.31;528 pages;not_ready'); dump(p,d)
dump(HERE / 'control-refresh.json', {'before':before,'after':{n:sha(ROOT/n) for n in names}})
for name in names: assert NEXT in (ROOT/name).read_text(), name
artifacts = ['integration-baseline.json','integration-verification.json','source-lock.json','build-v2.json','build-v2.log',
    'audit.md','review.md','result.md','coverage.json','render-review.json','replay-observation.json','control-refresh.json',
    'integrate.py','integrate_v2.py','setup.py','repair_layout.py','layout-repair-lock.json','prepare_finish.py','finish.py']
dump(HERE / 'run-manifest.json', {'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'command':'python3 -B integrate.py prepare/build; repair_layout.py; integrate_v2.py build/verify; finish.py',
    'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU Python/LuaLaTeX; GPU intentionally hidden for build',
    'data_version':'Version4.30 plus accepted exact shared-factor credit exchanges','seeds':'N/A deterministic',
    'wall_seconds':sum(json.loads((HERE/n).read_text())['wall_seconds'] for n in ['build.json','build-v2.json']),
    'plan':'docs/plans/accounting-credit-linked-integration-20261025.md','result':REL+'/result.md',
    'provenance':'Uncommitted local sources bound by hashes',
    'artifacts':{REL+'/'+n:sha(HERE/n) for n in artifacts}})
print(json.dumps({'candidate':'4.31','pages':check['pages'],'controls':len(names),
    'coverage':[len(coverage[k]) for k in ['obligations','interactions','operations']],'next':NEXT}))
