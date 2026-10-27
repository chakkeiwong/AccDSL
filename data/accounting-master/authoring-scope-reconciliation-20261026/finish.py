"""Publish only verified documentary progress to editable master controls."""
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
NEXT = 'docs/plans/accounting-current-design-reconciliation-20261025.md'
PRIOR = 'data/accounting-master/fiscal-timeline-integration-20261025/coverage.json'


def sha(p):
    return sha256(p.read_bytes()).hexdigest()


def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


assert not (HERE / 'control-refresh.json').exists()
check = runpy.run_path(str(HERE / 'integrate.py'))['verify']()
assert check == json.loads((HERE / 'verification.json').read_text())
for page in [102, 104]:
    assert sha(HERE / f'page-{page}.png') == sha(HERE / 'rejected-date-build' / f'page-{page}.png')
dump(HERE / 'render-review.json', {'pdf_sha256': check['pdf_sha256'], 'pages': [1,102,103,104],
    'review': REL + '/review.md', 'author_review_complete': True,
    'whole_document_review': False, 'independent_and_human_acceptance': 'pending',
    'images': {f'page-{n}.png': sha(HERE / f'page-{n}.png') for n in [1,102,103,104]}})
prior = json.loads((ROOT / PRIOR).read_text())
coverage = {'schema': 'accdsl.coverage.references.v1', 'date': '2026-10-26',
    'candidate': '4.40', 'readiness': 'not_ready', 'baseline': {'path': PRIOR, 'sha256': sha(ROOT / PRIOR)},
    'next_plan': NEXT, 'whole_rows_closed': 0}
for group, count in [('obligations',53), ('interactions',6), ('operations',46)]:
    assert len(prior[group]) == len({r['id'] for r in prior[group]}) == count
    coverage[group] = []
    for row in prior[group]:
        changed = group == 'obligations' and row['id'] in {'MC24','MC32','MC34','G2'}
        coverage[group].append({'id': row['id'], 'prior_ref': {'path': PRIOR, 'collection': group, 'id': row['id'],
            'sha256': sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()},
            'assessment': 'scoped_documentary_clarification' if changed else 'prior_scope_retained_not_reaudited',
            'advance': 'Initial and later bounded authoring scopes distinguished.' if changed else 'No new evidence assigned.',
            'residual': 'Current all-obligation audit and the prior substantive limits remain open.',
            'evidence': [REL+'/result.md',REL+'/verification.json',REL+'/review.md'] if changed else [],
            'full_requirement_closed': False, 'acceptance': 'not_promoted'})
dump(HERE / 'coverage.json', coverage)
note = f'''## Authoring scope clarified — 26 October 2026

Version4.40:534 pages,not_ready.
PDF: {check['pdf']}
SHA256: {check['pdf_sha256']}.
The initial portable debt frontend and later bounded company grammars are now distinguished.
All174 predecessor sources and all existing equations/citations remain protected.
Cover and physical pages102–104 inspected; no new warnings.
Original53 obligations,6 interactions and46 operations remain; no whole requirement closes.
Result: {REL}/result.md.
S1–S5 partial; S6 held; S7/E3 deferred.
Next plan: {NEXT}.

'''
names = ['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md',
    'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
    'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
    'data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
    'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before = {}
for name in names:
    path = ROOT / name
    before[name] = sha(path)
    saved = HERE / 'control-before' / name
    saved.parent.mkdir(parents=True,exist_ok=True)
    saved.write_bytes(path.read_bytes())
    if path.suffix == '.md':
        title, rest = path.read_text().split('\n',1)
        path.write_text(title+'\n\n'+note+rest.lstrip('\n'))
path = ROOT / 'data/accounting-master/next-plan.json'
doc = json.loads(path.read_text()); active = doc['active_execution']
active.update(updated='2026-10-26',active_work_plan=NEXT,latest_result=REL+'/result.md',
    current_candidate={'version':'4.40','pages':534,'status':'not_ready','pdf':check['pdf'],'sha256':check['pdf_sha256']})
active['latest_results'].append(REL+'/result.md')
active['completed_increments'].append('Version4.40 clarifies bounded authoring scope with preserved mathematics and rendered review')
active['next'][0] = 'Continue current-design audit: economic/sector methods, language/reuse, interactions and all46 operations'
dump(path,doc)
path = ROOT / 'scripts/accounting_master_catalog.json'; doc=json.loads(path.read_text())
doc['active_execution_note'].update(updated='2026-10-26',active_work_plan=NEXT,
    latest_result=REL+'/result.md',current_candidate='4.40;534 pages;not_ready')
dump(path,doc)
dump(HERE/'run-manifest.json', {'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'command':'python3 -B '+REL+'/integrate.py prepare; build; verify; repair_date.py; build; verify; finish.py (sequential invocations)',
    'build':json.loads((HERE/'build.json').read_text()),'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform()},
    'cpu_gpu':'CPU-only document work; GPU intentionally hidden for build','data_version':'Protected Version4.39',
    'random_seeds':'N/A deterministic documentary edit','plan':'docs/plans/accounting-authoring-scope-reconciliation-20261026.md',
    'result':REL+'/result.md','artifacts':{p.name:sha(p) for p in HERE.iterdir() if p.is_file() and p.name!='run-manifest.json'}})
dump(HERE/'control-refresh.json', {'before':before,'after':{name:sha(ROOT/name) for name in names},
    'version':'4.40','next_plan':NEXT,'status':'not_ready'})
print(json.dumps({'refreshed_controls':len(names),'version':'4.40','status':'not_ready','next_plan':NEXT}))
