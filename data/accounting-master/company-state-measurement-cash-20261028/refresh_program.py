"""Record exact measurement/category evidence without changing original criteria."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
H = Path(__file__).resolve().parent
S = ROOT / 'data/accounting-master/construction-continuation-20261028'
def dump(p, d): p.write_text(json.dumps(d, indent=2) + '\n')
def rel(p): return str(p.relative_to(ROOT))
v = json.loads((H/'attempt-01/verification.json').read_text())
assert v['status'] == 'pass' and v['checks'] == 249
hashes = json.loads((H/'attempt-01/run-manifest.json').read_text())['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest() == h for p,h in hashes.items())
p = ROOT/'data/accounting-master/unified-program-20261028/program.json'
program = json.loads(p.read_text()); old = deepcopy(program)
d = json.loads((S/'failure-dispositions.json').read_text())
with (H/'navigation-before.json').open('x') as out: json.dump(dict(program=old, dispositions=d), out, indent=2)
originals = {r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(d['rows']) == 38
comparisons = {
 'SIM-F037': 'Native supplied DTA10 to4 records expense6, no cash and unchanged legal rights. Exact full-state/carry checks detect balanced false cash and erased-right controls across two account maps.',
 'SIM-F038': 'Native borrowing100/repayment40 yields financing60 and operating0 under an explicit classification. Balanced operating-category mutation passes generic reconciliation but fails the independent principal-category criterion.'}
for ident, comparison in comparisons.items():
 assert not any(r['id'] == ident for r in d['rows'])
 d['rows'].append(dict(id=ident, original_row=originals[ident], disposition='original_scoped_measurement_and_category_discriminator', comparison=comparison,
  evidence=[rel(H/'attempt-01/verification.json'), rel(H/'result.md')], next_action='Actual measurement, rights, applicable standards/perimeter and source authority remain open; synthetic full-state checks do not admit accounting treatment.', original_status_unchanged=True, broad_package_closed=False))
d['rows'].sort(key=lambda r:r['id']); d['reviewed_rows'] = len(d['rows'])
d['scope'] = '40 original rows individually reviewed;161 outside this continuation. Original criteria/statuses persist; scoped evidence is not whole-company closure.'
for r in d['rows']: assert r['original_row'] == originals[r['id']]
dump(S/'failure-dispositions.json', d)
lines = ['# Current original failure dispositions', '', '28 October2026. 40 original rows reviewed;161 outside this pass. All201 original rows/statuses persist. Coverage is not closure.', '', '| Original row | Current comparison | Residual / next action |', '| --- | --- | --- |']
lines += ['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in d['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for t in program['tasks']:
 if t['id'] == 'C04':
  t['evidence'].append(rel(H/'result.md'))
  t['next_action'] = '40 original failures reviewed;161 outside this pass. Continue entity/currency/timing and information/scenario cases, source dependencies and ordered reading from337.'
  t['remaining'] = [x for x in t['remaining'] if not x.startswith('Thirty-eight original rows')]
  t['remaining'].append('40 original rows individually compared;161 outside this pass. Actual measurement/rights, applicable basis/perimeter and source/operation completeness remain open.')
for a,b in zip(old['tasks'], program['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']: assert a[key] == b[key]
dump(p, program)
entry = '''
## Measurement, rights and cash categories — 28 October 2026

SIM-F037/038 pass249 checks across34 native programs. Supplied DTA10 to4
records expense6 without cash or legal-right changes. Principal financing60
remains distinct from reported OCF0. Balanced cash/rights/category defects are
detected independently. Result: company-state-measurement-cash-20261028/result.md
under data/accounting-master. Actual tax/measurement/authority admission is open.

40 original failures reviewed;161 outside this pass. Main reading336/831,
resume337. Original criteria/statuses and releases persist. E3 deferred.
Continue entity/currency/timing cases, source dependencies and ordered review.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p = ROOT/name; title,rest = p.read_text().split('\n',1); p.write_text(title+'\n'+entry+rest)
checkpoint = S/'checkpoint.md'
(H/'checkpoint-before.md').write_bytes(checkpoint.read_bytes())
checkpoint.write_text('# Construction continuation checkpoint\n'+entry+'''Current program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 original acceptance rows,156 clauses,18 packages,201 failures.
T01 definitions complete; construction, source surveys and acceptance remain
incomplete. S1–S5 partial;S6 held;E3 deferred. Selected5.55-R1 and provisional
5.56-D1 remain not_ready. Main reading336/831;resume337. No global veto.

Next: audit SIM-F039 parent/subsidiary transfer and SIM-F040 currency/timing
against existing native methods. Preserve unknown rights and original targets.
Then continue source and ordered-review work. Prior detailed history is retained
at company-state-measurement-cash-20261028/checkpoint-before.md in this parent.
Concurrent goal-alignment edits and the five pre-existing dirty files remain
unowned; stage only this continuation's exact changes.
''')
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p = ROOT/name; data = json.loads(p.read_text())
 data[key]['measurement_cash_continuation_20261028'] = dict(result=rel(H/'result.md'), checks=249, native_cases=34, reviewed_original_failures=40, outside_pass=161, scope='Supplied measurement/rights and cash-category discriminators; no actual admission')
 dump(p, data)
print(json.dumps(dict(reviewed=40, outside_pass=161, source_hashes_verified=len(hashes), task_statuses_preserved=True)))
