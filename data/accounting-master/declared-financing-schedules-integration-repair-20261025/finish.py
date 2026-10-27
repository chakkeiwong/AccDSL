from pathlib import Path
from hashlib import sha256
import json
import platform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
PLAN = 'docs/plans/accounting-declared-financing-clock-coverage-20261025.md'
PDF = 'docs/design/proposal/manuscript-financing-schedules-repair-20261025/accounting-product-proposal.pdf'


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    assert not (HERE / 'control-refresh.json').exists()
    verification = json.loads((HERE / 'verification.json').read_text())
    assert verification['passed'] and verification['candidate_version'] == '4.15'
    evidence = json.loads((HERE / 'evidence-check.json').read_text())
    assert evidence['passed']
    review = json.loads((HERE / 'render-review-final.json').read_text())
    assert review['pdf_sha256'] == verification['pdf_sha256'] and review['author_review_complete']
    assert (HERE / 'result.md').exists() and (HERE / 'review.md').exists()
    for name, expected in evidence['protected_evidence'].items():
        assert sha(ROOT / name) == expected, name
    names = ['docs/plans/accounting-master-current.md',
             'docs/plans/accounting-master-checkpoint.md',
             'docs/plans/accounting-master-program.md',
             'docs/plans/accounting-mission-requirements.md',
             'docs/plans/accounting-product-design-checkpoint.md',
             'data/accounting-master/next-plan.md',
             'data/accounting-master/simulator-session-20261023.md',
             'data/accounting-master/next-plan.json',
             'scripts/accounting_master_catalog.json']
    note = f'''## Current candidate Version 4.15 — 25 October 2026

Version4.15 is512 pages,not_ready. PDF:{PDF}.
SHA256:{verification['pdf_sha256']}.
Corrected financing schedules record15 focused tests and123 named comparisons;
the predecessor220-count claim remains rejected. All174 predecessor sources and
the PDF remain protected;370 labels,150 references,740 citations and289 exact
displays remain unchanged. Build and bounded rendered review pass.
Result:{REL}/result.md. Next:{PLAN}.
S1-S5 partial,S6 held,S7 deferred;no whole requirement closes.

'''
    before = {}
    for name in names:
        path = ROOT / name
        before[name] = sha(path)
        backup = HERE / 'control-before' / name
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(path.read_bytes())
        if name.endswith('.md'):
            title, rest = path.read_text().split('\n', 1)
            if 'master-current' in name or 'simulator-session' in name:
                rest = 'No command running. Preserve all recorded packages and unrelated dirty work.\n'
            path.write_text(title + '\n\n' + note + rest.lstrip('\n'))
    for name, key in [('data/accounting-master/next-plan.json', 'active_execution'),
                      ('scripts/accounting_master_catalog.json', 'active_execution_note')]:
        path = ROOT / name
        data = json.loads(path.read_text())
        old = {k: v for k, v in data.items() if k != key}
        active = data[key]
        active.update(active_work_plan=PLAN, latest_result=REL + '/result.md',
                      updated='2026-10-25')
        if key == 'active_execution':
            active['current_candidate'] = {'version': '4.15', 'pages': 512,
                'status': 'not_ready', 'pdf': PDF, 'sha256': verification['pdf_sha256']}
            active['latest_results'].append(REL + '/result.md')
            active['completed_increments'].append(
                'Version4.15: corrected financing schedules;15 focused;123 named comparisons;512 pages')
            active['next'][0] = 'Refresh complete coverage and select the next distinct simulator dependency'
        else:
            active['current_candidate'] = '4.15;512 pages;not_ready'
        dump(path, data)
        assert old == {k: v for k, v in json.loads(path.read_text()).items() if k != key}
    dump(HERE / 'render-review.json', {'pdf_sha256': verification['pdf_sha256'],
        'pages_inspected': [1, 394, 395, 396, 397], 'continuous_segments': [[394, 395, 396, 397]],
        'review': 'review.md', 'reviewer': 'author', 'whole_document_review': 'pending',
        'independent_reader': 'pending', 'human_acceptance': 'pending'})
    dump(HERE / 'coverage-delta.json', {'advanced': ['MC02','MC06','MC11','MC13','MC14','MC15',
        'MC16','MC18','MC23','MC24','MC25','MC26','MC28','MC32','MC34','MC35'],
        'whole_rows_closed': 0, 'remaining': 'broader language/module coverage,real-source historical feasibility,latent state and independent/domain/human acceptance'})
    dump(HERE / 'control-refresh.json', {'before': before,
        'after': {name: sha(ROOT / name) for name in names}, 'legacy_json_fields_unchanged': True})
    build = json.loads((HERE / 'build.json').read_text())
    dump(HERE / 'run-manifest.json', {'git_commit': '03fea070f089821f4759e49a4466a3399b7fc078',
        'command': build['command'], 'environment': {'python': platform.python_version(), **build['environment']},
        'cpu_gpu': 'CPU only; CUDA_VISIBLE_DEVICES=-1', 'random_seeds': 'N/A: deterministic build',
        'data_version': json.loads((HERE / 'baseline.json').read_text()), 'wall_seconds': build['wall_seconds'],
        'output_artifacts': {PDF: sha(ROOT / PDF)}, 'plan': 'docs/plans/accounting-declared-financing-schedules-integration-20261025.md',
        'result': REL + '/result.md'})
    print(json.dumps({'candidate': '4.15', 'pages': 512, 'controls': len(names), 'next': PLAN}))


if __name__ == '__main__':
    main()
