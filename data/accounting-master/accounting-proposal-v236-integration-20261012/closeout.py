"""Freeze the Version 2.36 integration without rewriting predecessors."""
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
    assert not (OUT / 'completion.json').exists(), 'Closed evidence stays frozen'
    report = json.loads((OUT / 'check-run.json').read_text())
    baseline = json.loads((OUT / 'baseline.json').read_text())
    renders = json.loads((OUT / 'render-manifest.json').read_text())
    build = json.loads((OUT / 'build-run.json').read_text())
    source_unit = ROOT / baseline['source_unit']
    candidate = ROOT / report['candidate_pdf']['path']
    checks = []
    def ck(name, value):
        checks.append({'check': name, 'passed': bool(value)})
    ck('155 integration checks', report['passed'] == 155 and not report['failed'])
    ck('candidate hash and renders match', sha(candidate) == report['candidate_pdf']['sha256'] == renders['pdf_sha256'])
    ck('174-page final candidate', report['pages'] == renders['pages'] == 174)
    ck('protected baseline PDF', sha(ROOT / baseline['baseline_pdf']['path']) == baseline['baseline_pdf']['sha256'])
    ck('source unit frozen', json.loads((source_unit / 'completion.json').read_text())['manifest_sha256'] == sha(source_unit / 'run-manifest.json'))
    ck('build passed', build['exit_code'] == 0)
    ck('12 ordered final renders', [r['pdf_page'] for r in renders['renders']] == list(range(115, 127)))
    for r in renders['renders']:
        ck('render page ' + str(r['pdf_page']), sha(ROOT / r['image']) == r['sha256'])
    for name in ['result.md', 'author-review.md', 'four-ledger-review.md', 'next-source-frontier.md', 'surface-audit.json', 'surface-audit.md']:
        ck('review artifact ' + name, (OUT / name).is_file())
    controls = {}
    for row in baseline['pointer_snapshots']:
        ck('prior pointer ' + row['live'], sha(ROOT / row['snapshot']) == row['sha256'])
        live = ROOT / row['live']
        content = live.read_text()
        ck('live candidate ' + row['live'], 'Version 2.36' in content and report['candidate_pdf']['sha256'] in content)
        ck('negative readiness ' + row['live'], 'not_ready' in content)
        controls[row['live']] = sha(live)
    ck('human acceptance remains pending', 'Independent-reader and human acceptance pending' in (OUT / 'four-ledger-review.md').read_text())
    ck('unverified mapping remains explicit', 'legal/accounting explanation remains unverified' in (OUT / 'result.md').read_text())
    failures = [x['check'] for x in checks if not x['passed']]
    if failures:
        print(json.dumps({'failures': failures}))
        raise SystemExit(1)
    excluded = {'run-manifest.json', 'closeout-checks.json', 'completion.json'}
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in excluded and p.suffix != '.pyc'}
    plan = 'docs/plans/accounting-jpmorgan-debt-perimeter-integration-20261012.md'
    hashes[plan] = sha(ROOT / plan)
    candidate_dir = (ROOT / report['candidate_pdf']['path']).parent
    for p in candidate_dir.rglob('*'):
        if p.is_file() and p.suffix in {'.tex', '.bib', '.lark', '.pdf', '.log', '.blg'}:
            hashes[str(p.relative_to(ROOT))] = sha(p)
    manifest = {
        'recorded_at': '2026-10-12', 'unit': 'Version 2.36 bounded debt-perimeter integration',
        'git_commit': '8b6826ccb4a2a86f940f4ca04931d4a4cd901edb',
        'git_state': 'main; unrelated dirty work preserved; .git read-only',
        'plan': plan, 'result': str((OUT / 'result.md').relative_to(ROOT)),
        'candidate_pdf': {**report['candidate_pdf'], 'pages': report['pages']},
        'baseline_pdf': baseline['baseline_pdf'],
        'data_version': 'Closed JPMorgan 2025 Note 20/33 source unit and frozen Version 2.35',
        'environment': {'python': platform.python_version(), 'typesetter': 'LuaLaTeX/TinyTeX through latexmk', 'cpu_gpu': 'CPU-only; GPU intentionally hidden', 'random_seeds': 'N/A deterministic document checks'},
        'commands': [
            'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v236-integration-20261012/build_candidate.py',
            'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v236-integration-20261012/build_pdf.py',
            'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v236-integration-20261012/render_review.py',
            'python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py <candidate>/chapters/15-banking.tex --pdf <candidate>/accounting-product-proposal.pdf --output-json <unit>/surface-audit.json --output-md <unit>/surface-audit.md',
            'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v236-integration-20261012/check_integration.py',
            'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v236-integration-20261012/closeout.py',
        ],
        'build_workdir': build['cwd'], 'build_command': build['command'],
        'wall_time_seconds': {'final_build': build['wall_seconds'], 'integration_check': report['wall_seconds'], 'closeout_before_manifest': time.monotonic() - START},
        'integration_checks': report['passed'], 'closeout_checks': len(checks),
        'controls': controls, 'pointer_snapshots': baseline['pointer_snapshots'],
        'artifact_hashes': hashes, 'readiness': 'not_ready',
        'independent_reader': 'pending', 'human_acceptance': 'pending',
        'current_codification': 'not_verified', 'runtime_compatibility': 'not_tested',
    }
    write('run-manifest.json', manifest)
    write('closeout-checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json')})
    write('completion.json', {'status': 'closed_bounded_manuscript_integration', 'integration_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json'), 'readiness': 'not_ready'})
    print(json.dumps({'integration_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0, 'artifact_hashes': len(hashes)}))

if __name__ == '__main__':
    main()
