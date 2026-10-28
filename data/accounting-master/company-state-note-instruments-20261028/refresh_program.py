"""One-shot source-summary refresh; preserve original populations and statuses."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
H = Path(__file__).resolve().parent

def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def rel(path):
    return str(path.relative_to(ROOT))

v = json.loads((H / 'attempt-01/verification.json').read_text())
assert v['status'] == 'pass' and v['checks'] == 264 and v['series'] == 8
manifest = json.loads((H / 'attempt-01/run-manifest.json').read_text())
hashes = {**manifest['source_hashes'], **manifest['render_hashes']}
assert all(sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in hashes.items())
assert (H / 'result.md').is_file()
p = ROOT / 'data/accounting-master/unified-program-20261028/program.json'
program = json.loads(p.read_text())
old = deepcopy(program)
f = ROOT / 'data/accounting-master/construction-continuation-20261028/failure-dispositions.json'
dispositions = json.loads(f.read_text())
failure_hash = sha256(f.read_bytes()).hexdigest()
assert len(program['tasks']) == 40 and len(dispositions['rows']) == 28
with (H / 'navigation-before.json').open('x') as out:
    json.dump(dict(program=old, dispositions=dispositions), out, indent=2)
for task in program['tasks']:
    if task['id'] in ['T03', 'C04']:
        assert rel(H / 'result.md') not in task['evidence']
        task['evidence'].append(rel(H / 'result.md'))
    if task['id'] == 'T03':
        task['next_action'] = ('Eight retained Apple note-series summaries are now source-bound and typed. '
            'Recover governing instruments and explicit series identities; inspect September28 holdings, '
            'currency/carrying/hedge allocations, source chronology and actor access. Do not repeat '
            'completed Note9 aggregation or equate October18 issuer principals with earlier consolidated debt.')
        task['remaining'].append('Eight issuer-summary series lack governing-instance/ISIN, September28 holdings, '
            'settlement adjustment and consolidated carrying/hedge/FX links. Source and accounting admission remain false.')
    if task['id'] == 'C04':
        task['next_action'] = ('Twenty-eight original failures reviewed;173 outside this pass. Continue remaining '
            'original discriminators, supported instrument/measurement bridges with T03, and ordered reading from337. '
            'Eight-series mapping adds supporting evidence without closing another original failure.')
for before, after in zip(old['tasks'], program['tasks']):
    for key in ['id', 'status', 'depends_on', 'completion_criterion', 'requirements']:
        assert before[key] == after[key]
dump(p, program)
assert sha256(f.read_bytes()).hexdigest() == failure_hash
entry = '''
## Eight source-bound Apple note series — 28 October 2026

Exhibit4.1 mapping passes264 checks for eight series and24 native temporal
measurements;15 altered semantic cards and wrong currency/date relations refuse.
Twelve source pages retain governing-document and payment qualifications.
October18 EUR/GBP issuer-summary principals remain separate from September28
consolidated USD carrying debt. Result: company-state-note-instruments-20261028/result.md
under data/accounting-master. Governing instruments, IDs, holdings and
currency/carrying/hedge allocations remain open; all admission flags stay false.

Twenty-eight original failures reviewed;173 outside this pass. Main reading
336/831, resume337. Original criteria/statuses and frozen releases persist.
E3 deferred. Continue governing-source matching and independent ready work.

'''
for name in ['MISSION_CONTROL.md', 'docs/plans/accounting-mission-requirements.md',
             'docs/plans/accounting-master-checkpoint.md',
             'data/accounting-master/construction-continuation-20261028/checkpoint.md',
             'data/accounting-master/next-plan.md',
             'docs/plans/company-state-research-release-program-20261028.md']:
    p = ROOT / name
    title, rest = p.read_text().split('\n', 1)
    p.write_text(title + '\n' + entry + rest)
for name, key in [('scripts/accounting_master_catalog.json', 'active_execution_note'),
                  ('data/accounting-master/next-plan.json', 'active_execution')]:
    p = ROOT / name
    d = json.loads(p.read_text())
    d[key]['note_instruments_continuation_20261028'] = dict(result=rel(H / 'result.md'),
        checks=264, series=8, native_observations=24, semantic_controls=15,
        reviewed_original_failures=28, outside_pass=173,
        scope='Source-bound issuer-summary subset; no governing instrument or opening-state admission')
    dump(p, d)
print(json.dumps(dict(source_and_render_hashes_verified=len(hashes),
    reviewed_original_failures=28, task_statuses_preserved=True, failure_dispositions_unchanged=True)))
