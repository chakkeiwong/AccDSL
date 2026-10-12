"""Advance four live controls and bind this completed integration once."""
import datetime
import json
import platform
import sys
from build_candidate import OUT, ROOT, BASE, CAND, sha, save

assert not (OUT / 'completion.json').exists()
b = json.loads((OUT / 'baseline.json').read_text())
c = json.loads((OUT / 'integration-checks.json').read_text())
assert c['passed'] == 126 and not c['failed'] and c['pages'] == 181
pdf = str((CAND / 'accounting-product-proposal.pdf').relative_to(ROOT))
digest = sha(ROOT / pdf)
assert digest == c['pdf_sha256']
summary = '''Version 2.44 attributes the Board's nearest-basis-point score-rounding
explanation and keeps the 2026 proposed changes separate on PDF 118–119.
All 126 integration checks pass; all 48 displays and 87 prior references
remain, with two official references added. Eight final pages were inspected
and the build is clean. The source inquiry passed 63 checks across 13 groups
and 24 denominator matches. Actual bank inputs, the complete amendment chain
and independent/human/domain acceptance stay open. Readiness remains not_ready.
Result: `data/accounting-master/bank-score-rounding-integration-20261012/result.md`.
'''
oldnext = '''Integrate the official score-rounding explanation in a separate Version 2.44,
preserving its preamble context and the proposed/operative distinction. Then
audit all five remaining workstreams before choosing another source unit. Plan:
`docs/plans/accounting-bank-score-rounding-integration-20261012.md`.'''
newnext = '''Audit the latest evidence and dependencies for E01/E05/E07/E08/E14, correct
stale live instructions and execute an independent ready source/specification
unit. Preserve Version 2.44 and all held implementation boundaries. Plan:
`docs/plans/accounting-frontier-refresh-20261012.md`.'''
oldpdf = str((BASE / 'accounting-product-proposal.pdf').relative_to(ROOT))
rows = []
for r in b['pointer_snapshots']:
    p = ROOT / r['live']
    assert sha(p) == r['sha256'] == sha(ROOT / r['snapshot'])
    s = p.read_text()
    if p.name == 'accounting-master-checkpoint.md':
        a = s.index('## Current candidate\n')
        z = s.index('## Preserved Version 2.42', a)
        previous = s[a + len('## Current candidate\n'):z]
        s = s[:a] + f'## Current candidate\n\n**Version 2.44, 181 pages**\nPDF: {pdf}\nSHA256: {digest}\n\n' + summary + '\n## Preserved Version 2.43 reporting inputs\n' + previous + s[z:]
    elif p.name == 'next-plan.md':
        s = s.replace('**180-page Version 2.43**', '**181-page Version 2.44**', 1)
        s = s.replace(oldpdf, pdf, 1).replace(b['pdf_sha256'], digest, 1)
        s = s.replace('Result: data/accounting-master/bank-reporting-integration-20261012/result.md', 'Result: data/accounting-master/bank-score-rounding-integration-20261012/result.md', 1)
        s = s.replace('## Completed boundary\n', '## Completed boundary\n\n' + summary + '\n## Preserved Version 2.43 reporting inputs\n', 1)
    elif p.name == 'accounting-master-current.md':
        s = s.replace('Version 2.43 explains Method 1 inputs, reporting precision and denominator dates.',
                      'Version 2.44 adds the attributed score-rounding explanation and proposal boundary.\nVersion 2.43 preserves Method 1 inputs, reporting precision and denominator dates.', 1)
        s = s.replace('**180-page Version 2.43**', '**181-page Version 2.44**', 1).replace(b['pdf_sha256'], digest, 1)
        s = s.replace('Current through Version 2.43', 'Current through Version 2.44')
        s = s.replace('Current; Version 2.43 integrated; next unit integrates the attributed rounding explanation',
                      'Current; Version 2.44 integrated; next unit reviews the five-workstream frontier', 1)
        s = s.replace('or Version 2.43 outputs', 'or Version 2.44 outputs', 1)
        s = s.replace('delivered through Version 2.43', 'delivered through Version 2.44', 1)
        s = s.replace('The current baseline is Version 2.43', 'The current baseline is Version 2.44', 1)
        s = s.replace('## Current Version 2.43 bank reporting inputs\n', '## Current Version 2.44 score-rounding explanation\n\n' + summary + '\n## Preserved Version 2.43 bank reporting inputs\n', 1)
        s = s.replace('The denominator/rule-history inquiry is complete; integrate its attributed rounding explanation, then refresh the wider frontier.',
                      'The denominator/rule-history inquiry and Version 2.44 integration are complete; refresh the wider frontier before selecting another source unit.', 1)
        s = s.replace('1. Follow the direct next plan: integrate the attributed rounding explanation\n   into Version 2.44, then review all five remaining workstreams.',
                      '1. Follow the direct next plan: review all five remaining workstreams after\n   Version 2.44 and execute an independent ready source/specification unit.', 1)
    else:
        s = s.replace('## Current Version 2.43 bank reporting inputs\n', '## Current Version 2.44 score-rounding explanation\n\nE07/C05/P18; MC02–05/19/21/25/28/30/32–35, G7/G8/G13/G18.\n' + summary + '\n## Preserved Version 2.43 bank reporting inputs\n', 1)
        s = s.replace('integrated through Version 2.43; the rule-history inquiry is complete. Next integrate its attributed\nrounding explanation, then review all five remaining workstreams.',
                      'integrated through Version 2.44; the rule-history inquiry and attributed\nrounding integration are complete. Next review all five remaining workstreams.', 1)
    if p.name != 'accounting-continuation-requirements-20261007.md':
        assert s.count(oldnext) == 1
        s = s.replace(oldnext, newnext, 1)
    assert s != p.read_text() and 'not_ready' in s
    p.write_text(s)
    dest = OUT / 'pointers-after' / r['live']
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(p.read_bytes())
    rows.append({'live': r['live'], 'snapshot': str(dest.relative_to(ROOT)), 'sha256': sha(dest)})
save('controls-after.json', rows)
plans = ['docs/plans/accounting-bank-score-rounding-integration-20261012.md', 'docs/plans/accounting-frontier-refresh-20261012.md']
source = ROOT / 'data/accounting-master/bank-method1-rule-history-20261012'
inputs = [BASE / 'accounting-product-proposal.pdf', source / 'run-manifest.json', source / 'completion.json',
          source / 'sources/proposal-2026-05961.pdf', source / 'sources/final-2015-18702.pdf',
          source / 'citation-location.json', source / 'condition-ledger.json']
paths = [p for parent in [OUT, CAND] for p in parent.rglob('*') if p.is_file() and '__pycache__' not in p.parts] + [ROOT / p for p in plans]
now = datetime.datetime.now(datetime.timezone.utc)
build = json.loads((OUT / 'build-run.json').read_text())
manifest = {'git_commit': b['git_commit'], 'started_utc': b['started_utc'], 'closed_utc': now.isoformat(), 'plans': plans,
    'result': str((OUT / 'result.md').relative_to(ROOT)),
    'commands': [['python3', str((OUT / n).relative_to(ROOT))] for n in ['build_candidate.py', 'render_review.py', 'verify_integration.py', 'closeout.py']],
    'surface_audits': 'Bundled scholarly_surface_audit.py on root and banking source; exact commands retained in session and output paths.',
    'build': build, 'environment': {'python': sys.executable, 'version': platform.python_version(), 'libraries': ['PyMuPDF'], 'latex': 'LuaLaTeX via latexmk'},
    'cpu_gpu': 'CPU document work; CUDA_VISIBLE_DEVICES=-1 during build; no framework imports or device use.',
    'data_version': 'Exact Version 2.43 source copy plus declared paragraph replacement and two official references.',
    'seeds': 'N/A: deterministic documentary work',
    'wall_seconds': {'elapsed_including_review': (now - datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(), 'build': build['wall_seconds'], 'checks': c['wall_seconds']},
    'input_hashes': {str(p.relative_to(ROOT)): sha(p) for p in inputs},
    'artifact_hashes': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))},
    'pdf': pdf, 'pdf_sha256': digest, 'manuscript': 'Version 2.44', 'pages': c['pages'], 'readiness': 'not_ready', 'runtime': 'held', 'next_plan': plans[-1]}
assert sha(BASE / 'accounting-product-proposal.pdf') == b['pdf_sha256']
save('run-manifest.json', manifest)
for rel, digest in (manifest['input_hashes'] | manifest['artifact_hashes']).items(): assert sha(ROOT / rel) == digest
save('completion.json', {'status': 'bounded manuscript integration complete', 'integration_checks': c['passed'], 'failed': 0,
    'manifest_sha256': sha(OUT / 'run-manifest.json'), 'bound_artifacts': len(manifest['artifact_hashes']), 'manuscript': 'Version 2.44',
    'pdf_sha256': c['pdf_sha256'], 'pages': c['pages'], 'readiness': 'not_ready', 'next_plan': plans[-1]})
print(json.dumps({'checks': c['passed'], 'artifacts': len(manifest['artifact_hashes']), 'pages': c['pages'], 'controls': len(rows)}))
