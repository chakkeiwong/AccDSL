"""Publish the completed scoped audit; do not invoke any frozen writer."""
from hashlib import sha256
import json
from pathlib import Path
import platform
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
NEXT = 'docs/plans/accounting-profile-publication-effects-20261026.md'
PRIOR = 'data/accounting-master/authoring-scope-reconciliation-20261026/coverage.json'
PDF = 'docs/design/proposal/manuscript-authoring-scope-20261026/accounting-product-proposal.pdf'
PDF_HASH = 'e463820a696aefed8acdd5b142178bbbaa01eab2f0185b32ef4e21a84e7591eb'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


assert not (HERE / 'control-refresh.json').exists(), 'already published'
runpy.run_path(str(HERE / 'update_audit.py'))['main']()
audit = json.loads((HERE / 'audit-status.json').read_text())
original = json.loads((HERE / 'original-obligations.json').read_text())
assert audit['judgment'] == 'scoped_documentary_review_complete'
assert audit['reviewed_counts'] == {'obligations': 53, 'interactions': 6, 'operations': 46}
assert digest(ROOT / PDF) == PDF_HASH
prior = json.loads((ROOT / PRIOR).read_text())
coverage = {'schema': 'accdsl.coverage.references.v1', 'date': '2026-10-26',
            'candidate': '4.40', 'readiness': 'not_ready', 'whole_rows_closed': 0,
            'baseline': {'path': PRIOR, 'sha256': digest(ROOT / PRIOR)},
            'next_plan': NEXT, 'audit': REL + '/audit-status.json'}
for group, count in audit['reviewed_counts'].items():
    expected = [r['id'] for r in original['groups'][group]]
    assert expected == [r['id'] for r in audit['groups'][group]]
    assert len(expected) == len(set(expected)) == count
    by_id = {r['id']: r for r in prior[group]}
    assert set(by_id) == set(expected)
    coverage[group] = []
    for row in audit['groups'][group]:
        assert digest(ROOT / row['review_note']) == row['note_sha256']
        coverage[group].append(dict(row, prior_ref={
            'path': PRIOR, 'collection': group, 'id': row['id'],
            'sha256': sha256(json.dumps(by_id[row['id']], sort_keys=True,
                separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()}))
dump(HERE / 'coverage.json', coverage)

note = f'''## All-row design reconciliation — 26 October 2026

Version 4.40 remains 534 pages, not_ready; PDF SHA256 {PDF_HASH}.
All 53 obligations, six interactions and 46 operations have scoped current
judgments. This is documentary review, not whole-requirement acceptance.
Delivered corporate/annual/sector/recovery examples are credited; stale tasks
are replaced by precise composition, source, method and validation residuals.
The insurance slash-key defect has a separate checked metadata successor:
455 checks and 85 retained indexes; no frozen profile or receipt is rewritten.
Result: {REL}/result.md.
Phase detail: {REL}/remaining-work.md.
S1–S5 partial; S6 held; S7/E3 deferred.
Next plan: {NEXT}.

'''
names = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-current-program-20261025.md',
         'docs/plans/accounting-master-checkpoint.md', 'docs/plans/accounting-master-program.md',
         'docs/plans/accounting-mission-requirements.md', 'docs/plans/accounting-product-design-checkpoint.md',
         'data/accounting-master/next-plan.md', 'data/accounting-master/simulator-session-20261023.md',
         'data/accounting-master/next-plan.json', 'scripts/accounting_master_catalog.json']
before = {}
for name in names:
    p = ROOT / name
    before[name] = digest(p)
    saved = HERE / 'control-before' / name
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_bytes(p.read_bytes())
    if p.suffix == '.md':
        title, rest = p.read_text().split('\n', 1)
        p.write_text(title + '\n\n' + note + rest.lstrip('\n'))
for name in names[:2]:
    p = ROOT / name
    text = p.read_text().replace(
        'Current question: which current design obligations remain unspecified after the completed compositions?\nNext action: execute docs/plans/accounting-current-design-reconciliation-20261025.md.',
        'Current question: how should different profile publication effects be represented without losing owners, receipts or financial distinctions?\nNext action: execute ' + NEXT + '.')
    p.write_text(text)
p = ROOT / 'data/accounting-master/next-plan.json'
doc = json.loads(p.read_text())
active = doc['active_execution']
active.update(updated='2026-10-26', active_work_plan=NEXT,
              latest_result=REL + '/result.md', current_audit=REL + '/audit-status.json',
              remaining_work=REL + '/remaining-work.md')
active['latest_results'].extend(['data/accounting-master/component-identity-repair-20261026/result.md', REL + '/result.md'])
active['completed_increments'].extend(['All 53/6/46 original rows receive scoped current design judgments',
    'Insurance component request-pair collision has a checked metadata successor; frozen records preserved'])
active['next'] = ['Describe and verify profile-specific publication effects using exact retained exchanges',
    'Specify shared method composition and all-method authoring boundaries with matched conformance cases',
    'Resolve consequential source/version and actual-company dependencies using new legitimate leads',
    'Integrate checked repairs and complete candidate-specific review before product or E3 execution']
dump(p, doc)
p = ROOT / 'scripts/accounting_master_catalog.json'
doc = json.loads(p.read_text())
doc['active_execution_note'].update(updated='2026-10-26', active_work_plan=NEXT,
    latest_result=REL + '/result.md', current_candidate='4.40;534 pages;not_ready',
    current_audit=REL + '/audit-status.json', remaining_work=REL + '/remaining-work.md')
dump(p, doc)
dump(HERE / 'control-refresh.json', {'before': before,
    'after': {name: digest(ROOT / name) for name in names}, 'next_plan': NEXT,
    'version': '4.40', 'readiness': 'not_ready'})
dump(HERE / 'run-manifest.json', {
    'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'command': 'python3 ' + REL + '/finish.py',
    'environment': {'python': sys.executable, 'version': platform.python_version()},
    'cpu_gpu': 'CPU-only document/index work; no GPU framework or device accessed',
    'data_version': 'Protected Version4.39 baseline and Version4.40 governing manuscript',
    'random_seeds': 'N/A: deterministic documentary audit',
    'wall_time': 'Not captured for distributed documentary reading; identity diagnostic timed separately',
    'plan': 'docs/plans/accounting-current-design-reconciliation-20261025.md',
    'result': REL + '/result.md',
    'artifacts': {p.name: digest(p) for p in HERE.iterdir() if p.is_file() and p.name != 'run-manifest.json'}})
print(json.dumps({'reviewed': audit['reviewed_counts'], 'controls': len(names),
                  'pdf_unchanged': True, 'next_plan': NEXT}))
