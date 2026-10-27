"""One-shot evidence refresh after reviewing the original T01 criterion."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
backup = HERE / 'navigation-before'
backup.mkdir(exist_ok=False)
paths = [
    'data/accounting-master/unified-program-20261028/program.json',
    'docs/plans/company-state-research-release-program-20261028.md',
    'data/accounting-master/next-plan.md',
    'data/accounting-master/construction-continuation-20261028/checkpoint.md',
    'MISSION_CONTROL.md',
    'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-mission-requirements.md',
    'data/accounting-master/unified-program-20261028/current-requirement-decisions.md']
for i, relative in enumerate(paths):
    (backup / (str(i) + '-' + Path(relative).name)).write_bytes((ROOT / relative).read_bytes())
program = json.loads((ROOT / paths[0]).read_text()); before = deepcopy(program)
research = 'docs/design/research/company-state-program-20261028/'
reading = 'data/accounting-master/company-state-rea-commitment-reading-20261028/result.md'
owner = 'data/accounting-master/company-state-owner-semantics-20261028/result.md'
caller = 'data/accounting-master/company-state-common-request-20261028/result.md'
review = 'data/accounting-master/construction-continuation-20261028/t01-definition-review.md'
for task in program['tasks']:
    extra = []
    if task['id'] in ['S01', 'T01']:
        extra += [reading, research + 'rea-commitments-and-events.md']
    if task['id'] == 'S01':
        task['next_action'] = 'REA1982, policy2006 and extended commitment2002 author manuscript are technically read. Continue Lampe discussion/full foundational commitment source, automation and empirical/database competitors; version-equivalence and access limits remain.'
    if task['id'] == 'T01':
        extra += [owner, caller, review, research + 'common-state-owners.md',
                  research + 'common-request-contract.md', research + 'actor-information-requirements.md']
        task['status'] = 'complete'
        task['next_action'] = 'Reuse the reviewed task-relative definition and exact native mappings; reopen if a required undefined state category or false mapping is found. Downstream work retains its own survey prerequisites.'
        task['remaining'] = [
            'No remaining prerequisite for the original T01 definition criterion under its declared operation scope; internal review is not independent implementability acceptance.',
            'General source-to-company construction, actual principal/authority/receipt admission and industry composition remain separate T03/C01/T05 obligations.',
            'The executable common caller supports three audit capabilities; general actor policies, contract lifecycle and cross-owner joins are not implemented or admitted.']
    if task['id'] == 'C04':
        extra += [caller]
    task['evidence'] = list(dict.fromkeys(task.get('evidence', []) + extra))
for old, new in zip(before['tasks'], program['tasks']):
    for key in ['id', 'title', 'depends_on', 'closure_packages', 'requirements', 'deliverable',
                'completion_criterion', 'failure_conditions']:
        assert old[key] == new[key], (old['id'], key)
    assert old['status'] == new['status'] or (old['id'] == 'T01' and new['status'] == 'complete')
(ROOT / paths[0]).write_text(json.dumps(program, indent=2) + '\n')
entry = '''
## Common native request and T01 definition review — 28 October 2026

T01 is complete against its unchanged definition criterion: economic/contract
state, accounting memory, parameters, actor information, histories, changing
populations, refusal dependencies and historical queries are now explicitly
distinguished and traced to their native owners. Internal review is recorded
in construction-continuation-20261028/t01-definition-review.md under
data/accounting-master. This does not complete the DSL or its general constructor.

CompanyNativeRequest/1 passes304 checks over39 cases for three fixed audit
capabilities, preserving entire native results, partial/unknown histories and
seven interim PAA reports. The27-profile owner review preserves16 existing
compatibility edges. Actor requirements are typed and linked to the existing
bank information contracts; actual actor requests remain unsupported by this
caller. Result: data/accounting-master/company-state-common-request-20261028/result.md.

The19-page extended-REA author manuscript is fully read, with commitment/event
distinctions and all six survey ledgers updated. Published-version equivalence
and Lampe's discussion remain open; the latter has retained access failures.
No source critic's position is inferred from metadata.

Next: individual original failure cases, connected survey competitors and
ordered manuscript reading; continue actual-source/actor admission separately.
T04/T05/T07 retain their incomplete survey prerequisites. All40 task criteria
and edges,114 acceptance rows,156 clauses,18 packages and201 failure rows remain.
Only T01 task status advances. S1–S5 remain partial, S6 held, E3 deferred;
selected5.55-R1 and unselected5.56-D1 remain not_ready.

'''
for relative in paths[1:7]:
    p = ROOT / relative; title, rest = p.read_text().split('\n', 1)
    p.write_text(title + '\n' + entry + rest)
with (ROOT / paths[7]).open('a') as stream:
    stream.write('\n## T01 definition review, 28 October 2026\n\n'
        'T01 completes its original definition criterion under the internal review in ' + review + '. '
        'Common owner/request/actor definitions and304 checks add scoped evidence for '
        'MC08/09/10/13/18/19/20/24/25/28/32. The full extended-REA reading adds S01 evidence '
        'with critic/version limitations. No original requirement, closure package or '
        'release acceptance is changed; actual source and sector obligations remain.\n')
authority = [
    'docs/plans/company-state-definition-review-20261028.md', review,
    research + 'actor-information-requirements.md', research + 'common-request-contract.md',
    research + 'common-state-owners.md', research + 'native-construction-contract-v1.md',
    'data/accounting-master/extended-method-exchanges-20261015/bank-assessment/semantic-contract.md',
    'data/accounting-master/extended-method-exchanges-20261015/bank-assessment/verify_exchanges.py',
    'data/accounting-master/exact-bank-profile-adoption-20261026/semantic-contract.md',
    'data/accounting-master/exact-bank-profile-adoption-20261026/successor.py',
    'data/accounting-master/exact-bank-profile-adoption-20261026/result.md']
manifest = dict(review=review, decision='T01 definition complete; broader acceptance unchanged',
    baseline_program_sha256=sha256((backup / '0-program.json').read_bytes()).hexdigest(),
    source_hashes={p: sha256((ROOT / p).read_bytes()).hexdigest() for p in authority})
(ROOT / 'data/accounting-master/construction-continuation-20261028/t01-definition-source-lock.json').write_text(
    json.dumps(manifest, indent=2) + '\n')
print(json.dumps(dict(tasks=len(program['tasks']), status_change='T01 in_progress -> complete',
                      original_criteria_edges_preserved=True, paths=len(paths))))
