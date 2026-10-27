from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert not (OUT / 'run-manifest.json').exists()
c = json.loads((OUT / 'manuscript-checks.json').read_text())
a = json.loads((OUT / 'cases.json').read_text())
r = json.loads((OUT / 'render-v2/render-manifest.json').read_text())
assert c['passed'] and a['passed'] and c['count'] == 136 and a['count'] == 121
pdf = ROOT / 'docs/design/proposal/manuscript-insurance-branches-20261015/accounting-product-proposal.pdf'
assert sha(pdf) == c['pdf_sha256'] == r['pdf_sha256']
idx = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
assert idx == (ROOT / 'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
assert (OUT / 'result.md').exists()
next_plan = 'docs/plans/accounting-extended-method-exchanges-20261015.md'
assert (ROOT / next_plan).exists()
paths = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md',
         'docs/plans/accounting-continuation-requirements-20261007.md',
         'docs/plans/accounting-p17-completion-20261014.md', 'docs/plans/accounting-p18-completion-20261014.md',
         'data/accounting-master/next-plan.md']
next_line = f'Next: closed successor method profiles and complete exchanges under {next_plan}; closed extended exchanges and R07/R08 stay open. Runtime and empirical execution remain held.'
section = '''## Insurance models, modification values and dependence — 15 October 2026

R03-O is integrated in Version 3.13, 340 pages. Eight groups pass 121 exact checks; 136 preservation/build checks and ten final pages were inspected. Result: data/accounting-master/insurance-model-branches-20261015/result.md. Modification values, PAA costs/claim finance, VFA service/mitigation and variable-payment OCI have conditional methods. The joint claim-law family preserves dependence. Actual valuation, closed profiles and full readiness remain open.

''' + next_line + '\n\n'
before = OUT / 'controls-before-extended-exchanges'
before.mkdir()
records = []
for rel in paths:
    p = ROOT / rel
    s = p.read_text()
    (before / p.name).write_bytes(p.read_bytes())
    h = sha(p)
    s = s.replace('Version **3.12**, 335 pages', 'Version **3.13**, 340 pages')
    s = s.replace('**Version 3.12, 335 pages.**', '**Version 3.13, 340 pages.**')
    s = s.replace('Versions 2.73–3.12 add scoped', 'Versions 2.73–3.13 add scoped')
    s = s.replace('Integrations delivered through 3.12', 'Integrations delivered through 3.13')
    s = s.replace('docs/design/proposal/manuscript-bank-options-20261015/accounting-product-proposal.pdf', str(pdf.relative_to(ROOT)))
    s = s.replace('d08c6612845a7391d5c7cf51bb154642b99955ac95413e966a7aea638fc5237b', c['pdf_sha256'])
    s = '\n'.join(next_line if line.startswith('Next: insurance modification') else line for line in s.split('\n'))
    i = s.index('\n## ')
    s = s[:i+1] + section + s[i+1:]
    p.write_text(s)
    records.append({'path': rel, 'before_sha256': h, 'after_sha256': sha(p)})
residual = ROOT / 'data/accounting-master/finite-method-decisions-20261015/residual-followup.md'
with residual.open('a') as f:
    f.write('\n## Progress 15 October 2026 through Version 3.13\n\nR03-O adds conditional modification, PAA/VFA/finance and joint-process methods. See insurance-model-branches-20261015/result.md. Actual valuation, authority and closed successor exchanges remain. ' + next_line + '\n')
(OUT / 'render-review.json').write_text(json.dumps({
    'pdf_sha256': c['pdf_sha256'], 'physical_pages': [1, 241, 242, 245, 246, 247, 249, 250, 251, 252],
    'render_manifest': 'render-v2/render-manifest.json',
    'review': 'Ten scoped page images inspected; final hierarchy repair checked, with eight unchanged images bound by render-comparison.json. Human comprehension pending.',
}, indent=2) + '\n')
assert subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT) == idx
manifest = {
    'date': '2026-10-15',
    'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'plan': 'docs/plans/accounting-insurance-model-branches-20261015.md',
    'result': str((OUT / 'result.md').relative_to(ROOT)), 'pdf_sha256': c['pdf_sha256'], 'page_count': c['page_count'],
    'commands': [
        'python3 data/accounting-master/insurance-model-branches-20261015/check_cases.py',
        'python3 data/accounting-master/insurance-model-branches-20261015/prepare_manuscript.py (executed once)',
        'python3 scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-insurance-branches-20261015 --evidence data/accounting-master/insurance-model-branches-20261015 --timeout 240 --force',
        'python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-insurance-branches-20261015 --evidence data/accounting-master/insurance-model-branches-20261015/render-v2 --pages 1,241-242,245-247,249-252 --dpi 110',
        'python3 data/accounting-master/insurance-model-branches-20261015/verify_manuscript.py',
        'python3 data/accounting-master/insurance-model-branches-20261015/closeout.py',
    ],
    'environment': 'Python standard library rational arithmetic, existing LuaLaTeX and Poppler; trusted font-cache access for build',
    'cpu_gpu_status': 'CPU only; no GPU detection or framework imports',
    'data_version': 'Retained EU2023/1803 and eight synthetic case groups; source hashes in cases.json',
    'random_seeds': 'N/A: deterministic',
    'wall_seconds': {'final_build': json.loads((OUT / 'build-run.json').read_text())['wall_seconds'], 'author_total': 'Not captured; no performance claim'},
    'checks': {'arithmetic': a['count'], 'manuscript': c['count']},
    'artifacts': [str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))],
    'controls': records, 'index_preserved': True, 'readiness': 'not_ready', 'next_plan': next_plan,
}
(OUT / 'run-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'version': '3.13', 'controls': len(records), 'checks': manifest['checks'],
                  'index_preserved': True, 'next_plan': next_plan}))
