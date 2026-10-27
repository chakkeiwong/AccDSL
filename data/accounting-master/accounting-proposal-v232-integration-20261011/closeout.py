"""Freeze this bounded integration without rewriting any predecessor."""
import hashlib
import json
import platform
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    start = time.monotonic()
    assert not (OUT / 'completion.json').exists(), 'Closed evidence must remain frozen'
    report = json.loads((OUT / 'manuscript-checks.json').read_text())
    baseline = json.loads((OUT / 'baseline.json').read_text())
    checks = []

    def ck(name, value):
        checks.append({'check': name, 'passed': bool(value)})

    ck('integration checks pass', report['passed'] == 124 and report['failed'] == 0)
    ck('candidate hash intact', sha(ROOT / report['candidate_pdf']['path']) == report['candidate_pdf']['sha256'])
    ck('baseline hash intact', sha(ROOT / baseline['baseline_pdf']['path']) == baseline['baseline_pdf']['sha256'])
    for name in ['result.md', 'author-review.md', 'four-ledger-review.md', 'next-source-frontier.md', 'layout-repair.md', 'surface-audit.json']:
        ck('review artifact: ' + name, (OUT / name).is_file())
    controls = {}
    for row in baseline['pointer_relocations']:
        ck('prior pointer: ' + row['historical_path'], sha(ROOT / row['preserved_path']) == row['sha256'])
        path = ROOT / row['historical_path']
        text = path.read_text()
        ck('live candidate: ' + row['historical_path'], 'Version 2.32' in text and report['candidate_pdf']['sha256'] in text)
        controls[row['historical_path']] = sha(path)
    ck('human acceptance remains pending', 'pending' in (OUT / 'four-ledger-review.md').read_text() or 'No independent reader' in (OUT / 'four-ledger-review.md').read_text())
    ck('readiness remains negative', report['readiness'] == 'not_ready')
    failures = [r['check'] for r in checks if not r['passed']]
    if failures:
        print(json.dumps({'failures': failures}))
        raise SystemExit(1)
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in {'run-manifest.json', 'closeout-checks.json', 'completion.json'}}
    hashes['docs/plans/accounting-bidi-manuscript-integration-20261011.md'] = sha(ROOT / 'docs/plans/accounting-bidi-manuscript-integration-20261011.md')
    candidate_dir = (ROOT / report['candidate_pdf']['path']).parent
    for p in candidate_dir.rglob('*'):
        if p.is_file() and p.suffix in {'.tex', '.bib', '.lark', '.pdf', '.log', '.blg'}:
            hashes[str(p.relative_to(ROOT))] = sha(p)
    manifest = {'recorded_at': '2026-10-11', 'unit': 'Version 2.32 bounded integration', 'git_commit': '8b6826ccb4a2a86f940f4ca04931d4a4cd901edb', 'git_state': 'main; unrelated dirty work preserved; .git read-only', 'plan': 'docs/plans/accounting-bidi-manuscript-integration-20261011.md', 'result': str((OUT / 'result.md').relative_to(ROOT)), 'candidate_pdf': report['candidate_pdf'], 'baseline_pdf': baseline['baseline_pdf'], 'data_version': 'Exact predecessor source manifests and frozen Version 2.31', 'environment': {'python': platform.python_version(), 'typesetter': 'LuaLaTeX/TinyTeX through latexmk', 'cpu_gpu': 'CPU-only; GPU intentionally hidden for documentary checks; no ML framework used', 'random_seeds': 'N/A deterministic document checks'}, 'commands': ['python3 data/accounting-master/accounting-proposal-v232-integration-20261011/build_candidate.py', 'TEXMFVAR=/tmp/accdsl-texmfvar TEXMFCACHE=/tmp/accdsl-texmfvar latexmk -g -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex', 'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v232-integration-20261011/check_integration.py', 'python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py <candidate>/sections/adapter-methods.tex --pdf <candidate>/accounting-product-proposal.pdf --output-json <unit>/surface-audit.json --output-md <unit>/surface-audit.md', 'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v232-integration-20261011/closeout.py'], 'build_workdir': str(candidate_dir.relative_to(ROOT)), 'wall_time': {'integration_check_seconds': json.loads((OUT / 'check-run.json').read_text())['wall_seconds'], 'closeout_seconds_before_manifest': time.monotonic() - start, 'build_seconds': None, 'build_timing_limit': 'Both successful builds were not instrumented for exact elapsed time; logs preserved'}, 'integration_checks': report['passed'], 'closeout_checks': len(checks), 'controls': controls, 'pointer_relocations': baseline['pointer_relocations'], 'artifact_hashes': hashes, 'readiness': 'not_ready', 'independent_reader': 'pending', 'human_acceptance': 'pending', 'runtime_compatibility': 'not_tested', 'distribution_clearance': 'not_established'}
    write('run-manifest.json', manifest)
    write('closeout-checks.json', {'checks': checks, 'passed': len(checks), 'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json')})
    write('completion.json', {'status': 'closed_bounded_manuscript_integration', 'integration_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json'), 'readiness': 'not_ready'})
    print(json.dumps({'integration_checks': report['passed'], 'closeout_checks': len(checks), 'failed': 0, 'artifact_hashes': len(hashes)}))


if __name__ == '__main__':
    main()
