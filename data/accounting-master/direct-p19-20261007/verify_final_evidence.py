"""Verify saved P19 review/check inputs without rerunning or promoting them."""
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
start = time.monotonic()
checks = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def check(name, passed, details=None):
    checks.append({'name': name, 'passed': bool(passed), 'details': details})


def refs(value):
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
            yield value['path'], value['sha256']
        for item in value.values():
            yield from refs(item)
    elif isinstance(value, list):
        for item in value:
            yield from refs(item)


entry = read(OUT / 'recovery-entry-v1.json')
for group in ['protected_hashes', 'upstream_reference_hashes', 'controller_hashes']:
    mismatches = [p for p, expected in entry[group].items()
                  if not (ROOT / p).is_file() or sha(ROOT / p) != expected]
    check(group + ' unchanged', not mismatches,
          {'count': len(entry[group]), 'mismatches': mismatches})

assessment = read(ROOT / 'data/accounting-master/deliverables/P19/readiness.json')
references = sorted(set(refs(assessment)))
check('all current assessment references match',
      all(sha(ROOT / p) == h for p, h in references), len(references))
check('readiness remains false with five specified blockers',
      assessment['ready'] is False and assessment['status'] == 'not_ready' and
      sorted(assessment['remaining_blockers']) ==
      ['P15-E01', 'P15-E05', 'P15-E07', 'P15-E08', 'P15-E14'])

for filename in ['source-repair-checks-v1.json', 'assessment-integrity-v1.json',
                 'translation-anchor-checks-v1.json',
                 'manuscript-integration-v1/candidate-checks-v1.json']:
    report = read(OUT / filename)
    check(filename + ' passed', report['passed'] is True)
    inputs = report.get('inputs', [])
    pairs = list(inputs.items()) if isinstance(inputs, dict) else list(refs(inputs))
    if filename == 'source-repair-checks-v1.json':
        inspection = read(ROOT / 'docs/design/proposal/readiness/sources-20261007/inspection-v1.json')
        pairs += list(refs(inspection))
    check(filename + ' exact inputs retained', all(sha(ROOT / p) == h for p, h in pairs))
    if report.get('source_path') and report.get('source_sha256'):
        check(filename + ' source retained',
              sha(ROOT / report['source_path']) == report['source_sha256'])

for filename in ['negative-packet-inputs-v1.json', 'repair-packet-inputs-v1.json',
                 'manuscript-tax-packet-inputs-v1.json',
                 'manuscript-dates-v2-packet-inputs-v1.json']:
    manifest = read(OUT / filename)
    check(filename + ' unchanged', all(sha(ROOT / p) == h for p, h in manifest.items()))

wrapper_copies = [OUT / 'run_readonly_review.py']
wrapper_copies += list((OUT / 'manuscript-integration-v1').glob('review-wrapper-*.py'))
wrapper_hashes = {sha(p) for p in wrapper_copies}
verdicts = {}
for stage, packet in [('negative', 'negative-packet-v1.md'),
                      ('repair', 'repair-packet-v1.md'),
                      ('manuscript-tax', 'manuscript-tax-packet-v1.md'),
                      ('manuscript-dates-v2', 'manuscript-dates-v2-packet-v1.md')]:
    receipt = read(OUT / f'{stage}-review-v1.receipt.json')
    output = (ROOT / receipt['text']).read_text().strip()
    check(stage + ' completed AGREE', receipt['exit_code'] == 0 and
          output.endswith('VERDICT: AGREE'))
    check(stage + ' prompt matches saved packet', receipt['prompt_sha256'] == sha(OUT / packet))
    check(stage + ' exact wrapper retained', receipt['wrapper_sha256'] in wrapper_hashes)
    records = [json.loads(line) for line in (ROOT / receipt['stdout']).read_text().splitlines()]
    calls = [block.get('name') for record in records
             for block in record.get('message', {}).get('content', [])
             if isinstance(block, dict) and block.get('type') == 'tool_use']
    check(stage + ' no reviewer tool use', not calls and receipt['tools'] == [], calls)
    verdicts[stage] = {'exit_code': receipt['exit_code'],
                      'wall_seconds': receipt['wall_seconds'], 'verdict': output.splitlines()[-1]}

for stage in ['assessment', 'manuscript-final-read']:
    receipt = read(OUT / f'{stage}-review-v1.receipt.json')
    check(stage + ' timeout preserved as timeout', receipt['exit_code'] == 124)
for stage in ['manuscript-read', 'manuscript-dates-read']:
    check(stage + ' packet block preserved',
          (OUT / f'{stage}-review-v1.text.md').read_text().lstrip().startswith('BLOCK_PACKET'))

promotion = read(OUT / 'promotion-check-v2.receipt.json')
check('unchanged checker rejects MC01', promotion['exit_code'] == 1 and
      promotion['errors'] == ['MC01 design specified'] and
      promotion['checker_sha256'] == sha(ROOT / 'scripts/check_accounting_proposal.py') and
      promotion['checker_sha256'] == read(OUT / 'promotion-check-v1.receipt.json')['checker_sha256'])
check('promotion check bound to final unchanged assessment',
      promotion['assessment_sha256'] == sha(ROOT / 'data/accounting-master/deliverables/P19/readiness.json'))

for filename, groups in [('baseline-manifest.json', ['baseline_file_hashes']),
                         ('candidate-manifest-v1.json', ['artifacts', 'renders'])]:
    manifest = read(OUT / 'manuscript-integration-v1' / filename)
    for group in groups:
        mismatches = [p for p, h in manifest[group].items() if sha(ROOT / p) != h]
        check(filename + '/' + group + ' unchanged', not mismatches, mismatches)

report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
          'passed': all(row['passed'] for row in checks), 'checks': checks,
          'review_verdicts': verdicts,
          'counts': {'checks': len(checks), 'protected_files': len(entry['protected_hashes']),
                     'upstream_references': len(entry['upstream_reference_hashes']),
                     'controller_records': len(entry['controller_hashes']),
                     'assessment_references': len(references)},
          'command': ['python3', str(Path(__file__).relative_to(ROOT))],
          'checker_sha256': sha(Path(__file__)), 'wall_seconds': time.monotonic() - start,
          'scope': 'Exact final evidence and preservation only; negative assessment completion, '
                   'not phase promotion, product readiness or human acceptance.'}
(OUT / 'final-evidence-v1.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'counts': report['counts'],
                  'failures': [c for c in checks if not c['passed']]}))
raise SystemExit(0 if report['passed'] else 1)
