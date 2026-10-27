"""Add the completed source unit without replacing concurrent master work."""
from pathlib import Path
from hashlib import sha256
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DEST = OUT / 'controls-before-e03'
MANIFEST = OUT / 'e03-master-refresh-manifest.json'
assert not DEST.exists() and not MANIFEST.exists(), 'One-shot additive refresh already attempted'
prior_refresh = json.loads((OUT/'master-refresh-manifest.json').read_text())
paths = [x['path'] for x in prior_refresh['changes']]
before = {p:(ROOT/p).read_bytes() for p in paths}
catalog_path = 'scripts/accounting_master_catalog.json'
catalog = json.loads(before[catalog_path])
active = catalog['active_execution_note']
retained = {key:active[key] for key in [
    'active_work_plan','latest_internal_result','latest_result','phase_status',
    'current_candidate','current_pdf','current_pdf_sha256','standalone_pdf',
    'standalone_pdf_sha256','execution','next']}
assert (ROOT/active['active_work_plan']).is_file()
for name in ['current_pdf','standalone_pdf']:
    assert sha256((ROOT/active[name]).read_bytes()).hexdigest()==active[name+'_sha256']
run = json.loads((OUT/'contract-run-manifest.json').read_text())
assert (run['status'],run['cases'],run['mutation_controls'],run['checks'])==('PASS',58,12,144)
addition = '''## Source-linked contract continuation — 26 October 2026

E03 adds 20 source-dependency rows and a checked conditional reference:
58 hypothetical cases, 12 contrary-policy controls and 144 assertions. The
retained 2024 issuer summary distinguishes missed payment, clause-specific
default, acceleration, rescission, consent and series scope. Missing evidence
and boundary-day ordering remain unresolved. Its qualification by underlying
indentures is preserved; the earlier failed 2018 instrument acquisition remains
open. This work is not actual issuer admission or common-runtime integration.

The full gap program now records 14 successor deltas and 14 cross-interface
challenges, alongside the unchanged 53 obligations, six interactions,
46 operations, nine literature gaps, 67 original failures and 48 literature
extensions. All 18 broad packages remain open. E01/E02/E03 are companion
evidence pending protected manuscript integration. Current manuscript links,
concurrent language work, S6 held and E3 deferred remain as recorded below.

Source result: data/accounting-master/gap-program-20261026/contract-conditions.md.
Reviewed plan: docs/plans/accounting-gap-program-20261026.md.
Closure program: data/accounting-master/gap-program-20261026/closure-program.md.
Execution result: data/accounting-master/gap-program-20261026/result.md.
Current remaining work: data/accounting-master/gap-program-20261026/remaining-work.md.

'''
after = {}
for p, raw in before.items():
    if p == catalog_path:
        continue
    heading, body = raw.decode().split(chr(10),1)
    after[p] = (heading+chr(10)+chr(10)+addition+body.lstrip(chr(10))).encode()
active['gap_program_execution']['E03'] = 'checked conditional reference:20 source-dependency rows,58 cases,12 controls,144 assertions; actual admission and runtime integration open'
active['gap_program_contract_result'] = 'data/accounting-master/gap-program-20261026/contract-conditions.md'
active['gap_program_verification'] = 'data/accounting-master/gap-program-20261026/verification.json'
active['gap_program_next'] = [
    'Continue the live language subplan without repeating completed projections/grouped queries',
    'Follow E03 with a new evidenced indenture/series source lead; bind actual applicability and notice facts into a partial history',
    'Expose E01 financial-state invariants and compose E03 conditional remedy states in the common runtime',
    'Audit SMC2 resampling/waste-free dependencies and immutable evidence-vintage inference',
    'Execute remaining W01-W17 closure evidence; retain S6 held and E3 deferred']
assert all(active[k]==v for k,v in retained.items())
after[catalog_path] = (json.dumps(catalog,indent=2,ensure_ascii=False)+chr(10)).encode()
# Recheck every input before any live write, then retain the exact old bytes.
assert all((ROOT/p).read_bytes()==raw for p,raw in before.items()), 'Concurrent control changed: reread and rebase'
changes = []
for p,raw in before.items():
    snapshot = DEST/p
    snapshot.parent.mkdir(parents=True,exist_ok=True)
    snapshot.write_bytes(raw)
for p,raw in before.items():
    assert (ROOT/p).read_bytes()==raw, 'Concurrent write at '+p
    (ROOT/p).write_bytes(after[p])
    assert (ROOT/p).read_bytes()==after[p]
    changes.append({'path':p,'before_sha256':sha256(raw).hexdigest(),
                    'after_sha256':sha256(after[p]).hexdigest()})
manifest = {'status':'PASS','date':'2026-10-26','changes':changes,
            'preserved_active_fields':retained,'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'original_refresh_sha256':sha256((OUT/'master-refresh-manifest.json').read_bytes()).hexdigest(),
            'scope':'Additive E03 follow-up; original refresh manifest and frozen evidence preserved'}
MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+chr(10))
print(json.dumps({'status':'PASS','controls_updated':len(changes),
                  'concurrent_plan_preserved':retained['active_work_plan'],
                  'current_candidate':retained['current_candidate']}))
