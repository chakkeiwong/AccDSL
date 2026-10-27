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
assert c['passed'] and a['passed'] and c['count'] == 125 and a['count'] == 104
pdf = ROOT / 'docs/design/proposal/manuscript-bank-options-20261015/accounting-product-proposal.pdf'
assert sha(pdf) == c['pdf_sha256'] == r['pdf_sha256']
idx = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
assert idx == (ROOT / 'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
assert (OUT / 'result.md').exists()
next_plan = 'docs/plans/accounting-insurance-model-branches-20261015.md'
assert (ROOT / next_plan).exists()
paths = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md',
         'docs/plans/accounting-continuation-requirements-20261007.md',
         'docs/plans/accounting-p17-completion-20261014.md', 'docs/plans/accounting-p18-completion-20261014.md',
         'data/accounting-master/next-plan.md']
next_line = f'Next: insurance modification, PAA/VFA and finance methods under {next_plan}; closed extended exchanges and R07/R08 stay open. Runtime and empirical execution remain held.'
section = '''## Retained options and asset classification — 15 October 2026

R03-N is integrated in Version 3.12, 335 pages. Seven groups pass 104 exact checks; 125 preservation/build checks and seven final pages were inspected. Result: data/accounting-master/bank-options-classification-20261015/result.md. Conditional calls, puts, collars and amortised-cost transfers preserve net exposure; debt/equity measurement and disposal follow distinct classification findings. Pricing, actual admission, closed profiles and full readiness remain open.

''' + next_line + '\n\n'
before = OUT / 'controls-before-insurance-branches'
before.mkdir()
records = []
for rel in paths:
    p = ROOT / rel
    s = p.read_text()
    (before / p.name).write_bytes(p.read_bytes())
    h = sha(p)
    s = s.replace('Version **3.11**, 332 pages', 'Version **3.12**, 335 pages')
    s = s.replace('**Version 3.11, 332 pages.**', '**Version 3.12, 335 pages.**')
    s = s.replace('Versions 2.73–3.11 add scoped', 'Versions 2.73–3.12 add scoped')
    s = s.replace('Integrations delivered through 3.11', 'Integrations delivered through 3.12')
    s = s.replace('docs/design/proposal/manuscript-financing-modifications-20261015/accounting-product-proposal.pdf', str(pdf.relative_to(ROOT)))
    s = s.replace('cc009f7d98a34039c4ad61d1a3dd36e8ed65f4f731c555a26f03c78bd003ee3a', c['pdf_sha256'])
    s = '\n'.join(next_line if line.startswith('Next: transferred options') else line for line in s.split('\n'))
    i = s.index('\n## ')
    s = s[:i+1] + section + s[i+1:]
    p.write_text(s)
    records.append({'path': rel, 'before_sha256': h, 'after_sha256': sha(p)})
residual = ROOT / 'data/accounting-master/finite-method-decisions-20261015/residual-followup.md'
with residual.open('a') as f:
    f.write('\n## Progress 15 October 2026 through Version 3.12\n\nR03-N adds conditional option/collar continuing involvement and asset-classification/reporting methods. See bank-options-classification-20261015/result.md. Actual pricing, classifications and closed successor exchanges remain. ' + next_line + '\n')
(OUT / 'render-review.json').write_text(json.dumps({
    'pdf_sha256': c['pdf_sha256'], 'physical_pages': [1, 215, 216, 217, 227, 228, 229],
    'render_manifest': 'render-v2/render-manifest.json',
    'review': 'Final scoped author visual inspection; heading and forced-page-break repairs checked. Human comprehension pending.',
}, indent=2) + '\n')
assert subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT) == idx
manifest = {
    'date': '2026-10-15',
    'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'plan': 'docs/plans/accounting-bank-options-classification-20261015.md',
    'result': str((OUT / 'result.md').relative_to(ROOT)), 'pdf_sha256': c['pdf_sha256'], 'page_count': c['page_count'],
    'commands': [
        'python3 data/accounting-master/bank-options-classification-20261015/check_cases.py',
        'python3 data/accounting-master/bank-options-classification-20261015/prepare_manuscript.py (executed once)',
        'python3 scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-bank-options-20261015 --evidence data/accounting-master/bank-options-classification-20261015 --timeout 240 --force',
        'python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-bank-options-20261015 --evidence data/accounting-master/bank-options-classification-20261015/render-v2 --pages 1,215-217,227-229 --dpi 110',
        'python3 data/accounting-master/bank-options-classification-20261015/verify_manuscript.py',
        'python3 data/accounting-master/bank-options-classification-20261015/closeout.py',
    ],
    'environment': 'Python standard library rational arithmetic, existing LuaLaTeX and Poppler; trusted font-cache access for build',
    'cpu_gpu_status': 'CPU only; no GPU detection or framework imports',
    'data_version': 'Retained EU2023/1803 and seven synthetic case groups; source hashes in cases.json',
    'random_seeds': 'N/A: deterministic',
    'wall_seconds': {'final_build': json.loads((OUT / 'build-run.json').read_text())['wall_seconds'], 'author_total': 'Not captured; no performance claim'},
    'checks': {'arithmetic': a['count'], 'manuscript': c['count']},
    'artifacts': [str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))],
    'controls': records, 'index_preserved': True, 'readiness': 'not_ready', 'next_plan': next_plan,
}
(OUT / 'run-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'version': '3.12', 'controls': len(records), 'checks': manifest['checks'],
                  'index_preserved': True, 'next_plan': next_plan}))
