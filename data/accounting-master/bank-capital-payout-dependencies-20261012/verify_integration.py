"""Verify the precise manuscript delta, bindings and build; not readability."""
import json
import re
import time
import fitz
from build_candidate import OUT, ROOT, BASE, CAND, ANCHOR, sha, save

assert not (OUT / 'completion.json').exists()
start = time.monotonic()
checks = []
def ck(name, condition):
    checks.append({'name': name, 'passed': bool(condition)})

candidate = json.loads((OUT / 'candidate.json').read_text())
source_checks = json.loads((OUT / 'source-checks.json').read_text())
ck('source checks pass', source_checks['passed'] == 52 and not source_checks['failed'])
files = candidate['source_hashes']
ck('protected baseline PDF', sha(BASE / 'accounting-product-proposal.pdf') == candidate['baseline_pdf_sha256'])
ck('source inventory', set(files) == {str(p.relative_to(CAND)) for p in CAND.rglob('*')
                                     if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}})
for relative, digest in files.items():
    ck('baseline ' + relative, sha(BASE / relative) == digest)
    expected = (BASE / relative).read_text()
    if relative == 'accounting-product-proposal.tex':
        expected = expected.replace('Version 2.40 (proposal candidate)', 'Version 2.41 (proposal candidate)')
    elif relative == 'chapters/15-banking.tex':
        expected = expected.replace(ANCHOR, (OUT / 'insertion.tex').read_text() + '\n' + ANCHOR)
    elif relative == 'references.bib':
        expected += '\n' + (OUT / 'new-references.bib').read_text()
    ck('exact candidate ' + relative, (CAND / relative).read_text() == expected)
before = '\n'.join((BASE / p).read_text() for p in sorted(files) if p.endswith('.tex'))
after = '\n'.join((CAND / p).read_text() for p in sorted(files) if p.endswith('.tex'))
pattern = re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}', re.S)
displays = lambda t: [x.group() for x in pattern.finditer(t)]
ck('48 displays exactly preserved', displays(before) == displays(after) and len(displays(after)) == 48)
bib = (CAND / 'references.bib').read_text()
keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib)
ck('80 distinct bibliography entries', len(keys) == len(set(keys)) == 80)
citations = {k.strip() for group in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}', after) for k in group.split(',')}
ck('all citations resolve', citations <= set(keys))
labels = re.findall(r'\\label\{([^{}]+)\}', after)
refs = re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}', after)
ck('labels unique and references resolve', len(labels) == len(set(labels)) and set(refs) <= set(labels))
ck('final insertion bound', sha(OUT / 'insertion.tex') == candidate['insertion_sha256'])
ck('final references bound', sha(OUT / 'new-references.bib') == candidate['new_references_sha256'])
pdf = CAND / 'accounting-product-proposal.pdf'
doc = fitz.open(pdf)
text = ' '.join(' '.join(p.get_text().split()) for p in doc)
for phrase in ['Version 2.41', 'eligible retained income', 'US$2m remainder',
               'US$10m quarterly average', 'Table 2 gives zero',
               '100% ratio or permission', 'not interchangeable names']:
    ck('rendered meaning ' + phrase, phrase in text)
log = (CAND / 'accounting-product-proposal.log').read_text(errors='replace')
warnings = [s for s in log.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning', s)]
ck('TeX log clean', not warnings)
ck('repaired emphasis command', 'empheligible' not in text and 'emph{eligible' not in after)
blg = (CAND / 'accounting-product-proposal.blg').read_text(errors='replace')
ck('bibliography log clean', 'Warning--' not in blg and "I didn't find" not in blg)
for row in json.loads((OUT / 'final-renders.json').read_text()):
    ck('final render ' + str(row['pdf_page']), sha(ROOT / row['render']) == row['sha256'] and sha(pdf) == row['pdf_sha256'])
failure = [c['name'] for c in checks if not c['passed']]
result = {'checks': checks, 'passed': len(checks) - len(failure), 'failed': failure,
          'pages': len(doc), 'pdf_sha256': sha(pdf), 'warnings': warnings,
          'wall_seconds': time.monotonic() - start, 'readiness': 'not_ready',
          'scope': 'Exact documentary preservation and build checks; author source/reader review is separate.'}
save('integration-checks.json', result)
print(json.dumps({k: result[k] for k in ['passed', 'failed', 'pages', 'pdf_sha256', 'warnings']}))
raise SystemExit(bool(failure))
