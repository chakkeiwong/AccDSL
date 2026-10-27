"""Freeze P1 documentary baselines and check authored operation coverage once."""
from pathlib import Path
import hashlib
import json
import subprocess
from coverage_inputs import METHODS, ROWS

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / 'data/accounting-master'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

assert not (OUT / 'protected-inputs.json').exists(), 'One-shot snapshot already exists'
index = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
assert index == (BASE / 'remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
profiles = ['corporate-portable-20261015', 'finite-method-decisions-20261015/group',
            'p17-completion-20261014/P17-10/insurance-atomic']
protected = set()
snapshots = []
for name in ROWS:
    protected.add(BASE / 'p17-completion-20261014' / name / 'operation-matrix.md')
for rel in profiles:
    for name in ['record-schemas.json', 'portable-exchanges.json', 'result.md']:
        protected.add(BASE / rel / name)
for rel in ['scripts/accounting_master_catalog.json', 'scripts/run_accounting_master.py',
            'data/accounting-master/post-certainty-readiness-20261013/assessment.json',
            'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt',
            'data/accounting-master/finite-method-decisions-20261015/residual-followup.md',
            'data/accounting-master/finite-method-decisions-20261015/corporate/residual-disposition.md',
            'docs/plans/accounting-mission-requirements.md']:
    p = ROOT / rel
    assert p.exists(), rel
    protected.add(p)
manuscript = ROOT / 'docs/design/proposal/manuscript-insurance-branches-20261015'
protected.update(p for p in manuscript.rglob('*') if p.is_file() and p.suffix in ['.tex', '.bib', '.sty', '.pdf'])
coverage = []
for phase, authored in ROWS.items():
    matrix = BASE / 'p17-completion-20261014' / phase / 'operation-matrix.md'
    original = [s for s in matrix.read_text().splitlines() if s.startswith('|')][2:]
    assert len(original) == len(authored), phase
    for i, (old, row) in enumerate(zip(original, authored), 1):
        keys, missing, other = row
        evidence = []
        for key in keys.split():
            method, result = METHODS[key]
            mp = ROOT / 'docs/design/proposal/methods' / method
            rp = BASE / result
            assert mp.is_file() and rp.is_file(), (key, mp, rp)
            protected.update([mp, rp])
            evidence.append({'method': str(mp.relative_to(ROOT)), 'method_sha256': sha(mp),
                             'result': str(rp.relative_to(ROOT)), 'result_sha256': sha(rp)})
        coverage.append({'id': f'{phase}.{i:02}', 'operation': old.split('|')[1].strip(),
            'original_row': old, 'matrix': str(matrix.relative_to(ROOT)),
            'current_method_support': evidence, 'required_fields_and_semantics': missing.split('; '),
            'separate_dependencies': other.split('; '),
            'wire_disposition': 'successor_or_explicit_reuse_required',
            'full_requirement_closed': False})
for p in sorted(protected):
    target = OUT / 'protected' / p.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(p.read_bytes())
    assert sha(target) == sha(p)
    snapshots.append({'path': str(p.relative_to(ROOT)), 'sha256': sha(p),
                      'snapshot': str(target.relative_to(ROOT))})
schemas = [json.loads((BASE / rel / 'record-schemas.json').read_text())['$defs'] for rel in profiles]
c, g, ins = schemas
assert c['MethodDefinition']['properties']['method_id']['const'] == 'northstar.purchase@1'
assert set(c['EconomicEvent']['properties']['parameters']['properties']) == {'amount', 'units', 'consideration'}
assert c['Assumptions']['properties']['oci']['const'] == 'zero'
assert c['Assumptions']['properties']['tax_rule']['const'] == 'positive_profit_times_rate_no_deferred_tax'
assert g['AccountingEventBasis']['properties']['stage']['enum'] == ['A', 'O', 'R', 'D']
assert ins['GroupMeasurement']['properties']['group_id']['enum'] == ['A', 'B', 'R']
assert ins['EconomicEvent']['properties']['phase']['enum'] == ['finance', 'service', 'incurrence', 'settlement']
profile_counts = []
for rel in profiles:
    b = json.loads((BASE / rel / 'portable-exchanges.json').read_text())
    profile_counts.append({'path': rel, 'records': len(b['record_registry']), 'blobs': len(b['blobs']),
                           'exchanges': len(b.get('exchanges', b.get('cases', [])))})
save('protected-inputs.json', {'date': '2026-10-15', 'files': snapshots,
    'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'index_sha256': hashlib.sha256(index).hexdigest(), 'index_entries': len(index.splitlines())})
save('coverage.json', {'scope': 'All original P17-04–08 operation rows; documentary reconciliation only',
    'candidate_version': '3.13', 'rows': coverage, 'profiles': profile_counts,
    'readiness': 'not_ready', 'method_review_is_not_current_authority_admission': True})
save('coverage-checks.json', {'passed': True, 'operation_rows': len(coverage), 'protected_files': len(snapshots),
    'profile_counts': profile_counts, 'explicit_schema_constraints_checked': 7,
    'index_preserved': index == subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT),
    'meaning': 'Coverage/reference/preservation integrity; no financial, method or readiness promotion'})
table = ['# P1 operation-to-field reconciliation', '',
    '15 October 2026. All 46 original rows are preserved in coverage.json and protected/.',
    'The mappings are authored judgments; the check verifies coverage and byte integrity.', '',
    '| Row | Operation | Required fields and semantics | Separate dependencies |',
    '|---|---|---|---|']
for r in coverage:
    table.append('| ' + ' | '.join([r['id'], r['operation'], '; '.join(r['required_fields_and_semantics']),
                                    '; '.join(r['separate_dependencies'])]) + ' |')
table += ['', '## Exact baseline restrictions', '',
    'CorporateJointHistory/1: the method is northstar.purchase@1, event parameters are amount/units/consideration, '
    'the 16-account state has no component ledgers, tax is positive-profit-only with no deferred tax, and OCI is zero. '
    'Its 70 exchanges and 525 records remain valid under that restricted lock.', '',
    'GroupForeignOperation/1: 22 exchanges/197 records cover the A/O/R/D acquisition, operation, translation and disposal '
    'stages with USD/EUR books. They do not type inflation indices, reciprocal joins, exchangeability or corporate-asset impairment.', '',
    'Insurance atomic: 27 exchanges/274 records cover A/B/R groups and finance/service/incurrence/settlement phases. '
    'The fixed assumptions and account set lack PAA/VFA, equivalent premiums, coverage subsets and finance-OCI origins.', '',
    '## Dependency decision', '',
    'R03-F/G/L resolve the named finite corporate event/cohort/tax methods; R03-H/M resolve financing conditions/components/dates; '
    'R03-I/N resolve bank funding/transfer/classification branches; R03-J/O resolve the named insurance branches; '
    'R03-K resolves conditional group joins/restatement/exchangeability. Their source limits and supplied valuations remain. '
    'An old matrix naming those methods as absent is historical evidence, not a reason to create another example.', '',
    'The successor still needs closed state/event variants, exact method/source/date/context bindings, independent finances, '
    'explicit uncomputed-tax handling, adverse and atomic replay/recovery paths. Current ASC/ASBE admission, real contracts, '
    'actual valuation/calibration, all-zero impairment reversal and heterogeneous-lease allocation are distinct dependencies. '
    'They cannot be repaired with empty fields, arbitrary zeroes or a schema pass. R03 remains open.', '',
    'Next P2 starts with the named corporate variants and a complete production-cohort transition; it then adds benefits, '
    'asset/lease/provision/tax and customer operations. P3/P4 retain sector-specific records; P5 reconciles all 46 rows.']
(OUT / 'field-gaps.md').write_text('\n'.join(table) + '\n')
print(json.dumps({'rows': len(coverage), 'protected_files': len(snapshots), 'profiles': profile_counts, 'index_preserved': True}))
