"""One-shot current-program evidence refresh; preserve original task meanings."""
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
backup = HERE / 'navigation-before'
if backup.exists():
    raise SystemExit('one-shot backup exists')
backup.mkdir()
paths = [
    'data/accounting-master/unified-program-20261028/program.json',
    'docs/plans/company-state-research-release-program-20261028.md',
    'data/accounting-master/next-plan.md',
    'data/accounting-master/construction-continuation-20261028/checkpoint.md',
    'data/accounting-master/unified-program-20261028/current-requirement-decisions.md']
for i,p in enumerate(paths):
    (backup/(str(i)+'-'+Path(p).name)).write_bytes((ROOT/p).read_bytes())
program = json.loads((ROOT/paths[0]).read_text())
before = deepcopy(program)
source_result = 'data/accounting-master/company-state-rea-policy-reading-20261028/result.md'
native_result = 'data/accounting-master/company-state-policy-effects-20261028/result.md'
note = 'docs/design/research/company-state-program-20261028/rea-policy-and-state.md'
for task in program['tasks']:
    if task['id'] in ['S01','T01']:
        task['evidence'].extend([source_result,note])
    if task['id'] in ['T01','C04']:
        task['evidence'].append(native_result)
    if task['id']=='S01':
        task['next_action']='REA1982 and policy-level2006 full primary readings are delivered; inspect extended ontology/commitments, direct automation and empirical/database competitors.'
    if task['id']=='T01':
        task['next_action']='Typed audit queries and separate generation/equality/target effects are delivered for one native owner. Review common state/population/operation meanings across owners; commitment and actor meanings remain explicit gaps.'
        task['remaining'].append('The scoped three-role policy dispatcher does not supply a contract lifecycle, policy amendments or admitted actor decision rules.')
for old,new in zip(before['tasks'],program['tasks']):
    for k in ['id','title','depends_on','closure_packages','requirements','status','deliverable','completion_criterion','failure_conditions']:
        assert old[k]==new[k],(old['id'],k)
(ROOT/paths[0]).write_text(json.dumps(program,indent=2)+chr(10))
entry = '''
## Policy survey and explicit native effects — 28 October 2026

The complete Geerts/McCarthy2006 policy article is read and retained, with
technical anchors, metadata and all six live survey ledgers updated. It
distinguishes derived descriptions, validation rules and targets; its patterns
are heuristic and nonexhaustive. Commitments and direct implementation/empirical
competitors remain separate reading tasks. See company-state-rea-policy-reading-20261028/result.md
under data/accounting-master and rea-policy-and-state.md in the research directory.

The native CompanyPolicyEffectRequest/1 now keeps generation, exact-equality
validation and target comparison separate.144 checks across19 cases preserve
full native outcomes, unknown openings and unexecuted allocations. A failed
target does not become a failed transaction; generated inputs still face all
native guards. Result: data/accounting-master/company-state-policy-effects-20261028/result.md.

Next: common native-owner meanings and actor/operation definitions; primary
commitment/extended-ontology reading; remaining original failure dispositions
and ordered manuscript review. T01/S01/C04 remain in_progress. All40 task
criteria and dependency edges are preserved. S1–S5 partial, S6 held, E3 deferred;
selected5.55-R1 and unselected5.56-D1 remain not_ready.

'''
for p in paths[1:4]:
    text=(ROOT/p).read_text(); title,rest=text.split(chr(10),1)
    (ROOT/p).write_text(title+chr(10)+entry+rest)
p=ROOT/paths[4]
with p.open('a') as f:
    f.write('''
## Policy-effect continuation, 28 October 2026

MC08/10/13/18/19/26/28/32/35 now have bounded three-role native evidence in
company-state-policy-effects-20261028/result.md under data/accounting-master.
The REA2006 primary reading supports source-anchored distinctions and updates
the six ledgers (MC29/30 included). These supplements do not replace original
acceptance decisions. Common owners, commitments, actual authority and actor
access remain open; T01/S01/C04 statuses are unchanged.
''')
print(json.dumps({'tasks':len(program['tasks']),'preserved_original_conditions':True,'updated':paths}))
