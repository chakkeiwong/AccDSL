from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


b = json.loads((OUT / 'manuscript-baseline.json').read_text())
old, new = ROOT / b['baseline'], ROOT / b['candidate']
checks = []


def ck(name, value):
    checks.append({'name': name, 'passed': bool(value)})


ck('old-pdf', sha(old / 'accounting-product-proposal.pdf') == b['pdf_sha256'])
changed = []
for item in b['source_files']:
    ck('protected/' + item['path'], sha(old / item['path']) == item['sha256'])
    if sha(new / item['path']) != item['sha256']:
        changed.append(item['path'])
ck('intended-changes', set(changed) == {
    'accounting-product-proposal.tex', 'chapters/15-banking.tex', 'sections/bank-methods.tex'})
repair = json.loads((OUT / 'presentation-repair.json').read_text())
for relative, section, addition in [
        ('chapters/15-banking.tex', 'bank-asset-classification', '\\input{sections/bank-asset-classification}\n\n'),
        ('sections/bank-methods.tex', 'bank-option-transfers', '\n\n\\input{sections/bank-option-transfers}')]:
    text = (new / relative).read_text().replace(addition, '')
    if relative == repair['path']:
        text = text.replace(repair['after'], repair['before'])
    ck('prior-text/' + relative, text == (old / relative).read_text())
    ck('method-copy/' + section,
       (new / f'sections/{section}.tex').read_bytes()
       == (ROOT / f'docs/design/proposal/methods/{section}-20261015.tex').read_bytes())
texts = ['\n'.join(p.read_text() for p in sorted(d.rglob('*.tex'))) for d in [old, new]]
counts = {}
for key, pattern in {
    'displays': r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?)\}.*?\\end\{(?:equation\*?|align\*?)\}',
    'labels': r'\\label\{[^}]+\}',
    'citations': r'\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}',
}.items():
    before, after = [Counter(re.findall(pattern, text, re.S)) for text in texts]
    counts[key] = {'before': sum(before.values()), 'after': sum(after.values()),
                   'removed': list((before - after).elements())}
    ck(key + '/preserved', not (before - after))
build = json.loads((OUT / 'build-run.json').read_text())
render = json.loads((OUT / 'render-v2/render-manifest.json').read_text())
h = sha(new / 'accounting-product-proposal.pdf')
ck('clean-build', build['exit_code'] == 0 and not build['diagnostics'])
ck('render-bound', build['pdf_sha256'] == render['pdf_sha256'] == h)
for number, row in render['pages'].items():
    ck('page/' + number, sha(ROOT / row['path']) == row['sha256'])
cases = json.loads((OUT / 'cases.json').read_text())
ck('independent-arithmetic', cases['passed'])
for item in cases['sources']:
    ck('authority/' + item['path'], sha(ROOT / item['path']) == item['sha256'])
ck('index-preserved', subprocess.check_output(
    ['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
    == (ROOT / 'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
out = {'passed': all(c['passed'] for c in checks), 'count': len(checks),
       'counts': counts, 'checks': checks, 'pdf_sha256': h, 'page_count': build['page_count']}
(OUT / 'manuscript-checks.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({k: v for k, v in out.items() if k != 'checks'}))
assert out['passed'], [c for c in checks if not c['passed']]
