"""Accept the recovered diagnostic and advance the existing controls once."""
from pathlib import Path
from hashlib import sha256
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
NEXT = 'docs/plans/accounting-credit-linked-measurements-20261025.md'
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p, v): p.write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n')

assert not (HERE / 'acceptance-manifest.json').exists()
locks = json.loads((HERE / 'source-lock.json').read_text())
assert len(locks) == 29
for name, h in locks.items(): assert sha(ROOT / name) == h, name
manifest = json.loads((HERE / 'run-manifest.json').read_text())
for name, h in manifest['artifacts'].items(): assert sha(ROOT / name) == h, name
for mode in ['record', 'replay']:
    source = Path('/tmp/accdsl-credit-representation-' + mode + '.log')
    observation = json.loads(source.read_text().strip().splitlines()[-1])
    assert observation['passed'] and observation['native_replays'] == 9
    assert observation['locked_files'] == 29
    shutil.copyfile(source, HERE / (mode + '.log'))
dump(HERE / 'replay-observation.json', observation)
pdf = ROOT / 'docs/design/proposal/manuscript-insurance-statement-20261025/accounting-product-proposal.pdf'
assert sha(pdf) == 'ae30f68628d4a3c40bdf0fe6281a51ed4c9e0f3a3b853fa9d547315af3082f92'
assert (ROOT / NEXT).exists()
note = f'''## Credit measurement dependence checked — 25 October 2026

Nine retained schedules replay against 29 locked files. Three have exact
rational journals and states; six require shared non-rational measurements.
Independent interval endpoints fail exact balance in a checked counterexample.
Next: {NEXT}. Build a bounded exact shared-factor representation before posting.
Result: {REL}/result.md.
Version 4.30 remains 527 pages, not_ready; the manuscript is unchanged.
All 53 obligations, 6 interactions and 46 operations remain. No whole row closes.
S1–S5 partial; S6 held; S7/E3 deferred.

'''
names = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-current-program-20261025.md',
    'docs/plans/accounting-master-checkpoint.md', 'docs/plans/accounting-master-program.md',
    'docs/plans/accounting-mission-requirements.md', 'docs/plans/accounting-product-design-checkpoint.md',
    'data/accounting-master/next-plan.md', 'data/accounting-master/simulator-session-20261023.md',
    'data/accounting-master/next-plan.json', 'scripts/accounting_master_catalog.json']
before = {}
for name in names:
    p = ROOT / name; before[name] = sha(p)
    saved = HERE / 'control-before' / name
    saved.parent.mkdir(parents=True, exist_ok=True); saved.write_bytes(p.read_bytes())
    if p.suffix == '.md':
        title, rest = p.read_text().split('\n', 1)
        if name.endswith(('accounting-master-current.md', 'accounting-current-program-20261025.md', 'simulator-session-20261023.md')):
            rest = 'Mission:' + rest.split('Mission:', 1)[1]
            rest = rest.replace('docs/plans/accounting-credit-posting-representation-20261025.md', NEXT)
        p.write_text(title + '\n\n' + note + rest.lstrip('\n'))
p = ROOT / 'data/accounting-master/next-plan.json'; d = json.loads(p.read_text()); a = d['active_execution']
a.update(updated='2026-10-25', active_work_plan=NEXT, latest_result=REL + '/result.md')
a['latest_results'].append(REL + '/result.md')
a['completed_increments'].append('Nine credit schedules and dependent interval representation checked with exact counterexample')
a['next'][0] = 'Implement and verify the bounded CreditLinkedSchedule/1 exact expression layer before host admission'
dump(p, d)
p = ROOT / 'scripts/accounting_master_catalog.json'; d = json.loads(p.read_text())
d['active_execution_note'].update(updated='2026-10-25', active_work_plan=NEXT, latest_result=REL + '/result.md')
dump(p, d)
for name in names: assert NEXT in (ROOT / name).read_text(), name
dump(HERE / 'control-refresh.json', {'before':before, 'after':{n:sha(ROOT/n) for n in names}})
artifacts = ['audit.md','verify.py','evidence.json','source-lock.json','run-manifest.json','result.md',
    'record.log','replay.log','replay-observation.json','control-refresh.json','finish.py']
dump(HERE / 'acceptance-manifest.json', {'status':'accepted_representation_diagnostic_only',
    'frozen_candidate':'4.30', 'scope':'No book or accounting admission',
    'next_plan':NEXT,'artifacts':{REL+'/'+n:sha(HERE/n) for n in artifacts}})
print(json.dumps({'passed':True,'locked_files':len(locks),'controls':len(names),'next_plan':NEXT}))
