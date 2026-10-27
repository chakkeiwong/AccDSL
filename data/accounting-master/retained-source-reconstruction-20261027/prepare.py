"""Stage the inspected source reconstruction dependencies, never archival writers."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('data/accounting-master')
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()

record = HERE/'preparation-01'
record.mkdir(exist_ok=False)
old = read(ROOT/BASE/'executable-evidence-closure-20261027/preparation-04/bundle-manifest.json')
graph = old['import_graph']
pending, modules = ['scripts/retained_statement_network_v1.py'], set()
while pending:
    name = pending.pop()
    if name in modules:
        continue
    modules.add(name)
    pending.extend(graph[name]['local_dependencies'])
reasons = {name:['inspected native source module'] for name in modules}
lock_name = BASE/'joint-source-relation-binding-20261024/dependency-lock.json'
locks = read(ROOT/lock_name)
reasons[str(lock_name)] = ['native import-time lock']
for name in locks:
    reasons.setdefault(name,[]).append('native import checks all 183 locked files')
extra = {
    'retained-population-overlap-20261025/exchanges.json':'complete source request and original parent',
    'real-package-connection-20261015/portable-exchanges.json':'native source packet',
    'apple-statement-network-20261013/statement-readings.json':'annual displayed readings',
    'apple-interim-network-20261013/statement-readings.json':'interim displayed readings',
    'apple-statement-network-20261013/relationship-ledger.json':'annual authored relationships',
    'apple-interim-network-20261013/relationship-ledger.json':'interim authored relationships',
    'company-operations-20261023/operations.py':'target code hash only; not imported',
    'company-composed-profile-20261024/company_program.py':'other target identity; not imported',
    'debt-reading-network-20261027/attempt-01/full-result.json':'selected-parent and reading cross-check',
    'debt-dash-source-20261027/source_reading_v2.py':'pure native selected-reading function',
    'debt-dash-source-20261027/source-inspection-01/facts.json':'complete parsed source facts to validate',
    'debt-dash-source-20261027/selected-binding.json':'reviewed occurrence/interpretation binding',
    'debt-dash-source-20261027/attempt-01/reading.json':'frozen complete selected reading',
    'retained-source-reconstruction-20261027/replay.py':'new audited reconstruction driver',
    'retained-source-reconstruction-20261027/prepare.py':'new dependency staging driver',
}
for leaf, reason in extra.items():
    reasons.setdefault(str(BASE/leaf),[]).append(reason)
for leaf, reason in {
    'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json':'opening/comparative source readings',
    'docs/design/cases/apple/continuation-20261007/sources/annual-2024-taxonomy-trusted-v1.zip':'retained raw XBRL archive',
    'docs/design/cases/apple/annual-2024.pdf':'exact retained PDF identity; caption interpretation remains reviewed input',
    'docs/plans/accounting-retained-source-reconstruction-20261027.md':'reviewed scope and evidence contract',
}.items():
    reasons.setdefault(leaf,[]).append(reason)
for leaf in ['source-opening-compatibility-20261027/dependency-lock.json',
             'debt-dash-source-20261027/attempt-01/source-lock.json',
             'debt-reading-network-20261027/attempt-01/source-lock.json']:
    for name, expected in read(ROOT/BASE/leaf).items():
        if name in locks:
            assert locks[name] == expected, name
        locks[name] = expected
entries = {}
for name, why in sorted(reasons.items()):
    path = ROOT/name
    value = digest(path)
    if name in locks:
        assert value == locks[name], 'changed retained identity: '+name
    entries[name] = dict(sha256=value,bytes=path.stat().st_size,reasons=why,inherited_identity=name in locks)
stage = Path(tempfile.mkdtemp(prefix='accdsl-source-reconstruction-',dir='/tmp'))
for name, entry in entries.items():
    target = stage/name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/name,target)
    assert digest(target) == entry['sha256']
manifest = dict(entries=entries,executable_modules=sorted(modules),original_root=str(ROOT),
    source_construction_boundary='Retained packet/readings/ledgers and reviewed binding; no PDF-to-all-records reconstruction',
    plan='docs/plans/accounting-retained-source-reconstruction-20261027.md')
for path in [stage/'source-manifest.json',record/'bundle-manifest.json']:
    with path.open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
summary = dict(stage=str(stage),files=len(entries),bytes=sum(e['bytes'] for e in entries.values()),
    manifest_sha256=digest(stage/'source-manifest.json'))
with (record/'stage.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
print(json.dumps(summary))
