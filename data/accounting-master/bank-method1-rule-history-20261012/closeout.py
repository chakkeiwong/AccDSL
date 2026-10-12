"""Refresh live controls and bind this inquiry once; never alter closed units."""
import datetime
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, o): (OUT / n).write_text(json.dumps(o, indent=2) + '\n')

assert not (OUT / 'completion.json').exists()
base = json.loads((OUT / 'baseline.json').read_text())
checks = json.loads((OUT / 'source-checks.json').read_text())
assert checks['passed'] == 63 and not checks['failed']
for rel, digest in json.loads((OUT / 'reading-review.json').read_text())['renders'].items():
    assert sha(ROOT / rel) == digest
pdf = ROOT / 'docs/design/proposal/manuscript-reporting-inputs-20261012/accounting-product-proposal.pdf'
assert sha(pdf) == base['pdf_sha256']
summary = '''## Latest Method 1 rule-history inquiry

The bounded inquiry passes 63 checks over 13 condition groups and 24
denominator matches. Nine selected renders were inspected. The Board's 2026
proposal describes existing nearest-basis-point rounding with halves up;
the older exact passage is 49084 n22, in the 2015 preamble's proposal recap.
This locates an official explanation without establishing a codified explicit
clause or the complete current amendment chain. Proposed averaging, FX,
indicator and Method 2 ceiling changes stay separate. A bounded search found
no final record; it does not prove absence of a final action. Version 2.43
remains protected and readiness remains not_ready.
Result: `data/accounting-master/bank-method1-rule-history-20261012/result.md`.

'''
old = '''Inspect the exact official denominator-index link and March 2026 proposed
rule, preserving proposed/final/effective status and unresolved score rounding.
Keep the checked Version 2.43 example and source boundaries. Plan:
`docs/plans/accounting-bank-method1-rule-history-20261012.md`.'''
new = '''Integrate the official score-rounding explanation in a separate Version 2.44,
preserving its preamble context and the proposed/operative distinction. Then
audit all five remaining workstreams before choosing another source unit. Plan:
`docs/plans/accounting-bank-score-rounding-integration-20261012.md`.'''
rows = []
for row in base['pointer_snapshots']:
    p = ROOT / row['live']
    assert sha(p) == row['sha256'] == sha(ROOT / row['snapshot'])
    s = p.read_text()
    marker = '## Latest Method 1 reporting source inquiry' if p.name != 'next-plan.md' else '## Completed boundary'
    assert s.count(marker) == 1
    s = s.replace(marker, summary + marker, 1)
    if p.name != 'accounting-continuation-requirements-20261007.md':
        assert s.count(old) == 1
        s = s.replace(old, new, 1)
    s = s.replace('Actual bank inputs, score\nrounding, reporting-rule history and independent/human/domain acceptance stay\nopen.',
                  'The rule-history follow-up locates an official rounding explanation. Actual\nbank inputs, the complete reporting-rule history and independent/human/domain\nacceptance stay open.')
    if p.name == 'accounting-master-current.md':
        s = s.replace('and the reporting-source inquiry; latest candidate', 'and the rule-history inquiry; latest candidate', 1)
        s = s.replace('next unit checks exact denominator/rule-history leads', 'next unit integrates the attributed rounding explanation', 1)
        s = s.replace('Inspect exact denominator-index and March 2026 proposed-rule leads after Version 2.43.',
                      'The denominator/rule-history inquiry is complete; integrate its attributed rounding explanation, then refresh the wider frontier.', 1)
        s = s.replace('1. Follow the direct next plan: inspect the exact denominator-index and\n   March 2026 proposed-rule leads after the Version 2.43 integration.',
                      '1. Follow the direct next plan: integrate the attributed rounding explanation\n   into Version 2.44, then review all five remaining workstreams.', 1)
    if p.name == 'accounting-continuation-requirements-20261007.md':
        s = s.replace('next source work\nchecks the exact denominator-index and March 2026 proposed-rule leads after\nthe completed reporting integration.',
                      'the rule-history inquiry is complete. Next integrate its attributed\nrounding explanation, then review all five remaining workstreams.', 1)
    assert s != p.read_text()
    p.write_text(s)
    dest = OUT / 'pointers-after' / row['live']
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(p.read_bytes())
    rows.append({'live': row['live'], 'snapshot': str(dest.relative_to(ROOT)), 'sha256': sha(dest)})
save('controls-after.json', rows)
plans = [base['plan'], 'docs/plans/accounting-bank-score-rounding-integration-20261012.md']
deps = [pdf, ROOT / 'data/accounting-master/bank-method1-reporting-20261012/run-manifest.json',
        ROOT / 'data/accounting-master/bank-method1-surcharge-20261012/run-manifest.json']
paths = [p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts] + [ROOT / p for p in plans]
now = datetime.datetime.now(datetime.timezone.utc)
manifest = {'git_commit': base['git_commit'], 'started_utc': base['started_utc'], 'closed_utc': now.isoformat(),
    'plans': plans, 'result': str((OUT / 'result.md').relative_to(ROOT)),
    'commands': ['python3 data/accounting-master/bank-method1-rule-history-20261012/check_sources.py',
                 'python3 data/accounting-master/bank-method1-rule-history-20261012/closeout.py'],
    'source_commands': ['access-receipts.json', 'release-receipt.json', 'final-rule-receipt.json', 'status-search-receipt.json'],
    'environment': {'python': sys.executable, 'version': platform.python_version(), 'libraries': ['PyMuPDF', 'BeautifulSoup']},
    'cpu_gpu': 'CPU document processing only; no GPU framework import, detection or use.',
    'data_version': 'Four retained official publications and one bounded status search; selected reading only.',
    'seeds': 'N/A: deterministic documentary work',
    'wall_seconds': {'elapsed_including_recovery_review': (now - datetime.datetime.fromisoformat(base['started_utc'])).total_seconds(),
                     'source_checks': checks['wall_seconds']},
    'input_hashes': {str(p.relative_to(ROOT)): sha(p) for p in deps},
    'artifact_hashes': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))},
    'readiness': 'not_ready', 'runtime': 'held', 'manuscript': 'Version 2.43 unchanged', 'next_plan': plans[-1]}
save('run-manifest.json', manifest)
for rel, digest in (manifest['input_hashes'] | manifest['artifact_hashes']).items():
    assert sha(ROOT / rel) == digest
save('completion.json', {'status': 'bounded source inquiry complete', 'source_checks': checks['passed'],
     'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json'), 'bound_artifacts': len(manifest['artifact_hashes']),
     'readiness': 'not_ready', 'next_plan': plans[-1]})
print(json.dumps({'checks': checks['passed'], 'bound_artifacts': len(manifest['artifact_hashes']), 'controls': len(rows)}))
