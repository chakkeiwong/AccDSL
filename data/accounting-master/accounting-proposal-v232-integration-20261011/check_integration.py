"""Bounded preservation and build checks; never rebuild predecessor units."""
import hashlib
import json
import re
import time
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / 'docs/design/proposal/manuscript-jpmorgan-succession-20261011'
CAND = ROOT / 'docs/design/proposal/manuscript-bidi-dependencies-20261011'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    checks = []

    def ck(name, value):
        checks.append({'check': name, 'passed': bool(value)})

    baseline = json.loads((OUT / 'baseline.json').read_text())
    ck('protected baseline PDF', sha(ROOT / baseline['baseline_pdf']['path']) == baseline['baseline_pdf']['sha256'])
    sources = baseline['source_hashes']
    extensions = {'.tex', '.bib', '.lark', '.md', '.json'}
    ck('source inventory preserved', set(sources) == {str(p.relative_to(CAND)) for p in CAND.rglob('*') if p.is_file() and p.suffix in extensions})
    addition = (OUT / 'addition.tex').read_text()
    bib_addition = (OUT / 'bibliography-addition.bib').read_text()
    marker = 'The actual taxonomy notices show why that distinction changes the design.'
    changed = []
    for relative, digest in sorted(sources.items()):
        a, b = BASE / relative, CAND / relative
        ck('baseline intact: ' + relative, sha(a) == digest)
        before, after = a.read_text(), b.read_text()
        if before != after:
            changed.append(relative)
        if relative == 'accounting-product-proposal.tex':
            expected = before.replace('Version 2.31', 'Version 2.32')
        elif relative == 'sections/adapter-methods.tex':
            ck('single insertion anchor', before.count(marker) == 1)
            expected = before.replace(marker, addition + marker)
        elif relative == 'references.bib':
            expected = before + bib_addition
        else:
            expected = before
        ck('exact candidate content: ' + relative, after == expected)
    ck('only three intended files changed', set(changed) == {'accounting-product-proposal.tex', 'sections/adapter-methods.tex', 'references.bib'})
    before = '\n'.join((BASE / p).read_text() for p in sorted(sources) if p.endswith('.tex'))
    after = '\n'.join((CAND / p).read_text() for p in sorted(sources) if p.endswith('.tex'))
    pattern = re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}', re.S)
    displays = lambda text: [m.group() for m in pattern.finditer(text)]
    ck('48 exact displayed equations preserved', displays(before) == displays(after) and len(displays(after)) == 48)
    labels = re.findall(r'\\label\{([^{}]+)\}', after)
    refs = re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}', after)
    ck('unique labels', len(labels) == len(set(labels)))
    ck('references resolve', set(refs) <= set(labels))
    bib = (CAND / 'references.bib').read_text()
    keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib)
    old_keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)', (BASE / 'references.bib').read_text())
    ck('71 old and three new bibliography entries', len(old_keys) == 71 and len(keys) == len(set(keys)) == 74 and set(keys) - set(old_keys) == {'easyocr172source', 'pythonbidi0611source', 'bidirustsources2026'})
    cited = {k.strip() for group in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}', after) for k in group.split(',')}
    ck('citations resolve', cited <= set(keys))
    for name, expected in [('easyocr-python-bidi-20261011', 23), ('bidi-direct-rust-terms-20261011', 17), ('bidi-remaining-rust-terms-20261011', 118)]:
        source = ROOT / 'data/accounting-master' / name
        manifest = json.loads((source / 'run-manifest.json').read_text())
        report = json.loads((source / ('checks.json' if name.startswith('easyocr') else 'source-checks.json')).read_text())
        ck(name + ': source checks passed', report['passed'] == expected and report['failed'] == 0)
        ck(name + ': bound artifacts intact', all(sha(ROOT / path) == digest for path, digest in manifest['artifact_hashes'].items()))
    ck('four earlier controls preserved', len(baseline['pointer_relocations']) == 4 and all(sha(ROOT / row['preserved_path']) == row['sha256'] for row in baseline['pointer_relocations']))
    pdf = CAND / 'accounting-product-proposal.pdf'
    with fitz.open(pdf) as doc:
        pages = len(doc)
        text = ' '.join(doc[142].get_text().split())
        ck('dependency discussion and final citation together', all(term in text for term in ['EasyOCR', 'LGPLv3-or-later', 'target-lexicon', 'unicode-ident', 'XBRL International, 2026']))
        ck('next chapter starts on following page', 'Chapter 14' in doc[143].get_text())
        ck('172-page layout diagnostic', pages == 172)
    log = (CAND / 'accounting-product-proposal.log').read_text()
    warnings = [line for line in log.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning', line, re.I) and 'Package: infwarerr' not in line]
    ck('clean final TeX log', not warnings)
    ck('clean bibliography log', not re.search(r'Warning--|error message|I couldn.t open', (CAND / 'accounting-product-proposal.blg').read_text(), re.I))
    renders = json.loads((OUT / 'render-manifest.json').read_text())
    ck('renders bind final PDF', renders['pdf_sha256'] == sha(pdf))
    ck('ordered affected-page review coverage', set(range(141, 147)) <= {r['pdf_page_index'] for r in renders['rendered_pages']})
    ck('render images intact', all(sha(ROOT / r['image']) == r['sha256'] for r in renders['rendered_pages']))
    result = {'recorded_at': '2026-10-11', 'plan': 'docs/plans/accounting-bidi-manuscript-integration-20261011.md', 'baseline_pdf': baseline['baseline_pdf'], 'candidate_pdf': {'path': str(pdf.relative_to(ROOT)), 'sha256': sha(pdf), 'pages': pages}, 'changed_sources': changed, 'checks': checks, 'passed': sum(x['passed'] for x in checks), 'failed': sum(not x['passed'] for x in checks), 'readiness': 'not_ready', 'review_scope': 'bounded adapter discussion and transitions; author review only'}
    (OUT / 'manuscript-checks.json').write_text(json.dumps(result, indent=2) + '\n')
    (OUT / 'check-run.json').write_text(json.dumps({'command': 'CUDA_VISIBLE_DEVICES=-1 python3 ' + str(Path(__file__).relative_to(ROOT)), 'wall_seconds': time.monotonic() - start}, indent=2) + '\n')
    print(json.dumps({'passed': result['passed'], 'failed': result['failed'], 'failures': [x['check'] for x in checks if not x['passed']], 'pages': pages}))
    raise SystemExit(bool(result['failed']))


if __name__ == '__main__':
    main()
