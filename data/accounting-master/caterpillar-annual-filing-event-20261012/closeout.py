"""Freeze the Caterpillar event and mixed annual-wrapper evidence."""
import hashlib
import json
import platform
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert not (OUT / 'completion.json').exists(), 'Closed unit stays frozen'
    report = json.loads((OUT / 'checks.json').read_text())
    ledger = json.loads((OUT / 'event.json').read_text())
    baseline = json.loads((OUT / 'baseline.json').read_text())
    checks = []

    def ck(name, value):
        checks.append({'name': name, 'passed': bool(value)})

    ck('17 source and boundary checks', report['passed'] == 17 and not report['failed'])
    ck('official source identity', sha(ROOT / ledger['official_source']['path']) == ledger['official_source']['sha256'])
    ck('selected report identity', sha(ROOT / ledger['selected_report']['path']) == ledger['selected_report']['sha256'])
    ck('event date and accession', ledger['event']['filingDate'] == '2025-02-14'
       and ledger['event']['accessionNumber'] == '0000018230-25-000008')
    ck('selected date not promoted', ledger['selected_report']['whole_file_publication_date'] == 'not_verified'
       and ledger['selected_report']['byte_as_of_admission'] == 'none')
    ck('frozen 56/136 count', ledger['frozen_date_inventory_counts_unchanged'] == {'verified': 56, 'unverified': 136})
    ck('three source renders', [r['pdf_page'] for r in ledger['renders']] == [3, 11, 110])
    for item in ledger['renders']:
        ck('render ' + str(item['pdf_page']), sha(ROOT / item['image']) == item['sha256'])
    for name in ['author-review.md', 'result.md', 'next-source-frontier.md']:
        ck('record ' + name, (OUT / name).is_file())
    pdf = ROOT / 'docs/design/proposal/manuscript-junior-classification-20261012/accounting-product-proposal.pdf'
    ck('Version 2.37 unchanged', sha(pdf) == baseline['current_pdf_sha256'])
    controls = {}
    for item in baseline['pointer_snapshots']:
        ck('snapshot ' + item['live'], sha(ROOT / item['snapshot']) == item['sha256'])
        path = ROOT / item['live']
        text = path.read_text()
        ck('current source pointer ' + item['live'], 'caterpillar-annual-filing-event-20261012/result.md' in text
           and baseline['current_pdf_sha256'] in text and 'not_ready' in text)
        controls[item['live']] = sha(path)
    failures = [x['name'] for x in checks if not x['passed']]
    if failures:
        print(json.dumps({'failed': failures}))
        raise SystemExit(1)
    plan = 'docs/plans/accounting-caterpillar-annual-filing-event-20261012.md'
    excluded = {'run-manifest.json', 'closeout-checks.json', 'completion.json'}
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob('*')
              if p.is_file() and p.name not in excluded and p.suffix != '.pyc'}
    external = [plan, ledger['official_source']['path'], ledger['selected_report']['path'],
                'data/financial-report-benchmark/source-access.json',
                'data/financial-report-benchmark/coverage.json',
                'data/accounting-master/publication-evidence-20261011/selected-date-inventory.json']
    for rel in external:
        hashes[rel] = sha(ROOT / rel)
    manifest = {
        'recorded_at': '2026-10-12', 'unit': 'Caterpillar 2024 original 10-K event and selected annual wrapper',
        'git_commit': '8b6826ccb4a2a86f940f4ca04931d4a4cd901edb',
        'git_state': 'main; unrelated dirty work preserved; .git read-only',
        'plan': plan, 'result': str((OUT / 'result.md').relative_to(ROOT)),
        'data_version': 'Retained SEC submissions 2026-10-02 and selected annualreports 2024 PDF',
        'environment': {'python': platform.python_version(), 'cpu_gpu': 'CPU-only; GPU intentionally hidden',
                        'random_seeds': 'N/A deterministic documentary checks'},
        'commands': ['CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/caterpillar-annual-filing-event-20261012/' + f
                     for f in ['build_event.py', 'prepare.py', 'closeout.py']],
        'control_update_method': 'targeted local apply_patch between prepare and closeout',
        'wall_time_seconds': {'source_check': report['wall_seconds'], 'closeout_before_manifest': time.monotonic()-START},
        'source_checks': report['passed'], 'closeout_checks': len(checks),
        'controls': controls, 'pointer_snapshots': baseline['pointer_snapshots'],
        'artifact_hashes': hashes, 'readiness': 'not_ready', 'selected_byte_admissions': 0,
        'current_candidate_sha256': baseline['current_pdf_sha256'],
    }
    write('run-manifest.json', manifest)
    write('closeout-checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0,
                                  'manifest_sha256': sha(OUT / 'run-manifest.json')})
    write('completion.json', {'status': 'closed_bounded_event_wrapper_date_unverified',
                              'source_checks': report['passed'], 'closeout_checks': len(checks),
                              'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json'),
                              'readiness': 'not_ready'})
    print(json.dumps({'source_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0}))


if __name__ == '__main__':
    main()
