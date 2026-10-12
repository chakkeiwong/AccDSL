"""Close the selected historical-source and finite-payoff inquiry once."""
import datetime
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
assert not (OUT / 'completion.json').exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, v): (OUT / n).write_text(json.dumps(v, indent=2)+'\n')
b = json.loads((OUT / 'baseline.json').read_text())
c = json.loads((OUT / 'source-checks.json').read_text())
assert c['passed'] == 30 and not c['failed'] and c['finite_checks'] == 15
assert (OUT / 'result.md').is_file()
for p, h in b['inputs'].items(): assert sha(ROOT / p) == h
old = '''Inspect the retained AASB 17 direct-participation and variable-fee provisions,
including guarantees and the distinction between payoff, fulfilment cash flows
and CSM. Preserve the historical edition boundary and Version 2.46. The Apple
2018 indenture still lacks inspectable text; its four new discovery requests
yielded no usable lead. Continue under:
`docs/plans/accounting-insurance-vfa-source-20261012.md`.'''
new = '''Integrate the checked direct-participation and guarantee explanation in a
separate Version 2.47, preserving Version 2.46 and the correct conditional
10% share example. Distinguish settlement payoff, FCF and CSM; preserve the
historical AASB 17 edition and all wider limitations. Plan:
`docs/plans/accounting-insurance-vfa-integration-20261012.md`.'''
note = '''## Latest direct-participation and guarantee source inquiry

The retained AASB 17 compilation supplies 19 inspected source pages and
19 exact anchors; six source renders were inspected. Thirty source checks
and fifteen finite arithmetic checks pass. The authored guarantee example
leaves -10, 10 and 12 after payment at pool values 80, 100 and 120. This
explains why the valid 10% share component does not determine the full
exposure or CSM. Eligibility, expected measurement, loss and mitigation
conditions remain distinct. Actual contracts and later authority remain open.
Version 2.46 stays current until the planned 2.47 integration; not_ready.
Result: `data/accounting-master/insurance-vfa-source-20261012/result.md`.

'''
prepared = []
for r in b['pointer_snapshots']:
    p = ROOT / r['live'];assert sha(p) == r['sha256'] == sha(ROOT / r['snapshot'])
    s = p.read_text();anchor = '## Latest Apple 2018 indenture source attempt\n\n';assert s.count(anchor) == 1
    s = s.replace(anchor, note + anchor, 1)
    if p.name != 'accounting-continuation-requirements-20261007.md':
        assert s.count(old) == 1;s = s.replace(old, new, 1)
    if p.name == 'accounting-master-current.md':
        s = s.replace('Apple indenture access attempt complete without a body; next unit inspects retained AASB 17 variable-fee conditions',
                      'VFA source inquiry complete; next unit integrates the guarantee explanation in Version 2.47', 1)
        s = s.replace('Version 2.42 capital reconciliation |',
                      'Version 2.42 capital reconciliation; selected VFA eligibility/guarantee/mitigation provisions and an exact settlement-component example |', 1)
        s = s.replace('the next rotation inspects retained direct-participation and guarantee conditions.',
                      'direct-participation/guarantee source preparation is complete and the next unit integrates its explanation.', 1)
        s = s.replace('1. Follow the direct next plan: inspect retained AASB 17 direct-participation,\n   guarantee and variable-fee conditions after the Apple source-specific block.',
                      '1. Follow the direct next plan: integrate the checked direct-participation\n   and guarantee explanation in a separate Version 2.47.', 1)
    prepared.append((p, r, s))
rows = []
for p, r, s in prepared:
    p.write_text(s);q = OUT / 'pointers-after' / r['live'];q.parent.mkdir(parents=True, exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live': r['live'], 'snapshot': str(q.relative_to(ROOT)), 'sha256': sha(q)})
save('controls-after.json', rows)
plans = ['docs/plans/accounting-insurance-vfa-source-20261012.md', 'docs/plans/accounting-insurance-vfa-integration-20261012.md']
paths = [p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts] + [ROOT / p for p in plans]
now = datetime.datetime.now(datetime.timezone.utc)
f = json.loads((OUT / 'finite-diagnostic.json').read_text())
e = json.loads((OUT / 'source-evidence.json').read_text())
m = {'git_commit': b['git_commit'], 'started_utc': b['started_utc'], 'closed_utc': now.isoformat(),
    'plans': plans, 'result': str((OUT / 'result.md').relative_to(ROOT)),
    'commands': [['python3', str((OUT / n).relative_to(ROOT))] for n in ['finite_diagnostic.py','prepare_evidence.py','check_source.py','closeout.py']],
    'environment': {'python': sys.executable, 'version': platform.python_version(), 'arithmetic': 'stdlib Fraction', 'source_processing': 'PyMuPDF'},
    'cpu_gpu': 'CPU file and exact-arithmetic processing; no ML import or GPU probe',
    'data_version': 'AASB 17 compilation no. 4, December 2022; applicable period-start boundary retained',
    'random_seeds': 'N/A: deterministic unweighted authored examples',
    'wall_seconds': {'elapsed_including_review': (now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),
        'finite_diagnostic': f['wall_seconds'], 'source_preparation': e['wall_seconds'], 'checks': c['wall_seconds']},
    'input_hashes': b['inputs'], 'artifact_hashes': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))},
    'readiness': 'not_ready', 'next_plan': plans[-1]}
save('run-manifest.json', m)
for p, h in (m['input_hashes'] | m['artifact_hashes']).items(): assert sha(ROOT / p) == h
save('completion.json', {'status': 'bounded source and payoff inquiry complete; independent interpretation pending',
    'source_checks': c['passed'], 'finite_checks': f['passed'], 'failed': 0, 'source_pages': 19, 'source_anchors': 19,
    'manifest_sha256': sha(OUT / 'run-manifest.json'), 'bound_artifacts': len(m['artifact_hashes']), 'readiness': 'not_ready', 'next_plan': plans[-1]})
print(json.dumps({'source_checks': c['passed'], 'finite_checks': f['passed'], 'artifacts': len(m['artifact_hashes']), 'readiness': 'not_ready'}))
