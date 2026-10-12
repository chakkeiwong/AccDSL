"""Check exact preservation, citation integrity and final build evidence."""
import json
import re
import time
import fitz
from build_candidate import OUT, ROOT, BASE, CAND, sha, save, expected_text

assert not (OUT / 'completion.json').exists()
start = time.monotonic()
checks = []
def ck(n, v): checks.append({'name': n, 'passed': bool(v)})
c = json.loads((OUT / 'candidate.json').read_text())
unit = ROOT / 'data/accounting-master/bank-method1-rule-history-20261012'
source = json.loads((unit / 'completion.json').read_text())
ck('source closure binding', sha(unit / 'run-manifest.json') == source['manifest_sha256'])
ck('63 source checks pass', source['source_checks'] == 63 and source['failed'] == 0)
ck('protected baseline PDF', sha(BASE / 'accounting-product-proposal.pdf') == c['baseline_pdf_sha256'])
files = c['source_hashes']
ck('same source inventory', set(files) == {str(p.relative_to(CAND)) for p in CAND.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}})
for rel, digest in files.items():
    ck('baseline ' + rel, sha(BASE / rel) == digest == sha(OUT / 'baseline-source' / rel))
    ck('exact delta ' + rel, (CAND / rel).read_text() == expected_text(rel))
before = '\n'.join((BASE / p).read_text() for p in sorted(files) if p.endswith('.tex'))
after = '\n'.join((CAND / p).read_text() for p in sorted(files) if p.endswith('.tex'))
pattern = re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}', re.S)
displays = lambda s: [m.group() for m in pattern.finditer(s)]
ck('48 displays preserved exactly', displays(before) == displays(after) and len(displays(after)) == 48)
bib = (CAND / 'references.bib').read_text()
keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib)
oldkeys = re.findall(r'@\w+\s*\{\s*([^,\s]+)', (BASE / 'references.bib').read_text())
ck('87 old and two new references', len(oldkeys) == 87 and len(keys) == len(set(keys)) == 89 and set(oldkeys) <= set(keys))
citations = {k.strip() for group in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}', after) for k in group.split(',')}
ck('all citations resolve', citations <= set(keys))
labels = re.findall(r'\\label\{([^{}]+)\}', after)
refs = re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}', after)
ck('labels unique and references resolve', len(labels) == len(set(labels)) and set(refs) <= set(labels))
for name, digest in c['passage_hashes'].items(): ck('delta binding ' + name, sha(OUT / name) == digest)
pdf = CAND / 'accounting-product-proposal.pdf'
doc = fitz.open(pdf)
text = ' '.join(' '.join(p.get_text().split()) for p in doc)
for phrase in ['Version 2.44', 'Rounding the resulting score is a separate operation', 'fractions below one-half round down',
               'at or above one-half round up', 'account of the preceding proposal', 'separate ceiling formula',
               'Those proposed changes cannot be substituted', 'bank-specific score', 'not complete the amendment history']:
    ck('rendered meaning ' + phrase, phrase in text)
log = (CAND / 'accounting-product-proposal.log').read_text(errors='replace')
warnings = [s for s in log.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning', s)]
ck('TeX log clean', not warnings)
blg = (CAND / 'accounting-product-proposal.blg').read_text(errors='replace')
ck('bibliography log clean', 'Warning--' not in blg and "I didn't find" not in blg)
for row in json.loads((OUT / 'final-renders.json').read_text()):
    ck('render binding ' + str(row['pdf_page']), sha(ROOT / row['render']) == row['sha256'] and sha(pdf) == row['pdf_sha256'])
failure = [x['name'] for x in checks if not x['passed']]
result = {'checks': checks, 'passed': len(checks) - len(failure), 'failed': failure, 'pages': len(doc),
          'pdf_sha256': sha(pdf), 'warnings': warnings, 'wall_seconds': time.monotonic() - start,
          'readiness': 'not_ready', 'scope': 'Preservation/build evidence; independent readability and domain acceptance remain open.'}
save('integration-checks.json', result)
print(json.dumps({k: result[k] for k in ['passed', 'failed', 'pages', 'pdf_sha256', 'warnings']}))
raise SystemExit(bool(failure))
