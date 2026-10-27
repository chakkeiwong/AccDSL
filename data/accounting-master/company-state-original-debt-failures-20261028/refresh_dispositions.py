"""Extend the current supplement without changing original failure records."""
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
STATE = ROOT / 'data/accounting-master/construction-continuation-20261028'
backup = HERE / 'navigation-before'; backup.mkdir(exist_ok=False)
paths = ['data/accounting-master/construction-continuation-20261028/failure-dispositions.json',
         'data/accounting-master/construction-continuation-20261028/failure-dispositions.md',
         'data/accounting-master/unified-program-20261028/program.json',
         'data/accounting-master/construction-continuation-20261028/checkpoint.md',
         'data/accounting-master/next-plan.md',
         'docs/plans/company-state-research-release-program-20261028.md']
for i, relative in enumerate(paths):
    (backup / (str(i) + '-' + Path(relative).name)).write_bytes((ROOT / relative).read_bytes())
original = json.loads((ROOT / 'data/accounting-master/unified-program-20261028/failure-map.json').read_text())
by_id = {r['original_row']['id']: r['original_row'] for r in original['rows']}
supplement = json.loads((ROOT / paths[0]).read_text())
before_rows = deepcopy(supplement['rows'])
updates = {
    'SIM-F005': ('Both fixed/floating endpoints and an interior mixture satisfy principal100 and historical interest5; the continuous native family remains explicit.', 'Continue actual-contract/source admission and complete financial history execution separately; three witness points do not exhaust the family.'),
    'SIM-F007': ('Interest7 and cash90 each occur marginally but are jointly infeasible; the complete declared family satisfies cash+interest=95.', 'Extend only with explicit extra flows or changed templates; this scoped debt relation cannot stand in for whole-company cash.'),
    'SIM-F009': ('The same feasible family under zero max_cells returns PartialSearch/Unknown with the full unvisited formula, never infeasible.', 'Inspect other resource/timeout/backend cases separately; no wall-clock timeout was induced.'),
    'SIM-F014': ('Repeated pre-reset interest5 equalities retain fixed, floating and interior feasible mixtures; no posterior is assigned.', 'New rate-reset observations and probability updates need their own declared source and likelihood assumptions.')}
evidence = 'data/accounting-master/company-state-original-debt-failures-20261028/attempt-03/verification.json'
for identifier, (comparison, action) in updates.items():
    row = dict(id=identifier, original_row=by_id[identifier], disposition='exact_original_scoped_solver_evidence',
               comparison=comparison, evidence=[evidence], next_action=action,
               original_status_unchanged=True, broad_package_closed=False)
    existing = next((i for i, r in enumerate(supplement['rows']) if r['id'] == identifier), None)
    if existing is None: supplement['rows'].append(row)
    else: supplement['rows'][existing] = row
supplement['rows'].sort(key=lambda r: r['id'])
supplement['reviewed_rows'] = len(supplement['rows'])
supplement['scope'] = 'Eleven individually inspected rows; remaining190 outside this continuation. Four exact debt discriminators now supplement prior native evidence.'
for row in supplement['rows']: assert row['original_row'] == by_id[row['id']]
(ROOT / paths[0]).write_text(json.dumps(supplement, indent=2) + '\n')
lines = ['# Current original failure dispositions', '',
         '28 October2026. Eleven individually inspected rows;190 remain outside this continuation. Original statuses and all201 records are unchanged.', '',
         '| Original row | Current comparison | Residual / next action |', '| --- | --- | --- |']
lines += ['| ' + r['id'] + ' | ' + r['comparison'] + ' | ' + r['next_action'] + ' |' for r in supplement['rows']]
lines += ['', 'SIM-F005/007/009/014 now have exact scoped solver evidence in company-state-original-debt-failures-20261028/result.md under data/accounting-master. The earlier eight-row review is preserved in that directory navigation-before. Counts do not close C04 or the broader packages.', '']
(ROOT / paths[1]).write_text('\n'.join(lines))
program = json.loads((ROOT / paths[2]).read_text()); before = deepcopy(program)
for task in program['tasks']:
    if task['id'] == 'C04':
        task['evidence'].append('data/accounting-master/company-state-original-debt-failures-20261028/result.md')
        task['next_action'] = 'Eleven original rows individually reviewed, including four exact debt-family discriminators; continue the remaining190 exact targets without substituting related examples.'
for old, new in zip(before['tasks'], program['tasks']):
    for key in ['id', 'status', 'depends_on', 'completion_criterion', 'requirements']:
        assert old[key] == new[key]
(ROOT / paths[2]).write_text(json.dumps(program, indent=2) + '\n')
entry = '''
## Original debt-family failures — 28 October2026

SIM-F005/007/009/014 now have37 passing checks over13 exact native solver
queries: nonidentified fixed/floating composition, joint cash/interest rather
than marginal recombination, unresolved search-budget remainder, and repeated
uninformative observations. Two harness failures and their repairs are retained;
native compiler/adapter/solver code is unchanged. This is synthetic engineering
evidence, not empirical forecasting. Result:
data/accounting-master/company-state-original-debt-failures-20261028/result.md.

The current individual failure supplement covers11 original rows;190 remain
outside this pass. All201 original records/statuses and task criteria remain.
T01 is complete as a definition task; C04 remains in_progress. Continue exact
failure review, remaining survey and ordered reading. Release holds and E3
deferral remain unchanged. Common-caller commit680234a6 is pushed.

'''
for relative in paths[3:]:
    p = ROOT / relative; title, rest = p.read_text().split('\n', 1)
    p.write_text(title + '\n' + entry + rest)
print(json.dumps(dict(reviewed=len(supplement['rows']), untouched=201-len(supplement['rows']),
                      original_statuses_preserved=True)))
