"""Check the bounded V2.3 delta and preserve the earlier negative assessment."""
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NEW = ROOT / 'docs/design/proposal/manuscript-taxonomy-20261008'
start = time.monotonic()
checks = []
inputs = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    inputs[str(path.relative_to(ROOT))] = sha(path)
    return json.loads(path.read_text())


def check(label, ok, details=None):
    checks.append({'check': label, 'passed': bool(ok), 'details': details})


def subsequence(before, after):
    iterator = iter(after.splitlines())
    return all(any(line == other for other in iterator) for line in before.splitlines())


base = read(OUT / 'manuscript-baseline.json')
old = ROOT / base['source_directory']
changed = []
for name, expected in base['protected_hashes'].items():
    check('baseline preserved: ' + name, (ROOT / name).is_file() and sha(ROOT / name) == expected)
sources = sorted(p for p in old.rglob('*') if p.suffix in {'.tex', '.bib', '.lark'})
check('candidate source inventory matches baseline',
      {p.relative_to(old) for p in sources} ==
      {p.relative_to(NEW) for p in NEW.rglob('*') if p.suffix in {'.tex', '.bib', '.lark'}})
before_tex, after_tex = [], []
for original in sources:
    rel = original.relative_to(old)
    candidate = NEW / rel
    before, after = original.read_text(), candidate.read_text()
    inputs[str(candidate.relative_to(ROOT))] = sha(candidate)
    if before != after:
        changed.append(str(rel))
    if rel.as_posix() == 'accounting-product-proposal.tex':
        check('only intended title version and date changes',
              before.replace('Version 2.2', 'Version 2.3').replace('7 October 2026', '8 October 2026') == after)
    else:
        check('all original lines retained in order: ' + str(rel), subsequence(before, after))
    if original.suffix == '.tex':
        before_tex.append(before)
        after_tex.append(after)
check('only planned source files changed', set(changed) ==
      {'accounting-product-proposal.tex', 'sections/adapter-methods.tex', 'references.bib'}, changed)
before_text, after_text = '\n'.join(before_tex), '\n'.join(after_tex)
display_pattern = r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{\1\}'
displays = lambda text: [m.group() for m in re.finditer(display_pattern, text, re.S)]
check('display mathematics unchanged', displays(before_text) == displays(after_text))
labels = re.findall(r'\\label\{([^}]+)\}', after_text)
check('no duplicated labels', len(labels) == len(set(labels)))
refs = re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}', after_text)
check('all literal reference targets exist', set(refs) <= set(labels))
bib = (NEW / 'references.bib').read_text()
keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib)
old_keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)', (old / 'references.bib').read_text())
check('bibliography keys unique', len(keys) == len(set(keys)))
check('all old bibliography keys preserved', set(old_keys) <= set(keys))
new_keys = {'arellepinned2026', 'fasbtaxonomyuses', 'fasbsrtuses', 'xbrlcopyright'}
check('exact intended bibliography additions', set(keys) - set(old_keys) == new_keys)
cites = [k.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', after_text) for k in group.split(',')]
check('all cited keys present', set(cites) <= set(keys))
check('new source entries cited in body', new_keys <= set(cites))
log = (NEW / 'accounting-product-proposal.log').read_text()
diagnostics = [line for line in log.splitlines() if any(x in line for x in ['Warning', 'Overfull', 'Underfull', '! '])]
check('final TeX log has no warnings or box errors', not diagnostics, diagnostics)
check('BibTeX log has no errors', not re.search(r'Warning--|error message|I couldn.t open', (NEW / 'accounting-product-proposal.blg').read_text()))
receipt = read(OUT / 'build-receipt.json')
check('saved final build succeeded in candidate directory', receipt['exit_code'] == 0 and receipt['cwd'] == str(NEW.relative_to(ROOT)))
pdf = NEW / 'accounting-product-proposal.pdf'
inputs[str(pdf.relative_to(ROOT))] = sha(pdf)
with fitz.open(pdf) as doc:
    pages = len(doc)
    full_text = '\n'.join(p.get_text() for p in doc)
check('final 127-page V2.3 PDF', pages == 127 and 'Version 2.3' in full_text)
for marker in ['validationExitCode', 'IOerror', 'Software Notice', '2027', '01f6a4656c2c6551d2f05f31c9d74366d133ee7e']:
    check('final PDF includes source finding: ' + marker, marker in full_text)
render = read(OUT / 'render-final-manifest.json')
check('render input binds final PDF before and after', render['pdf_sha256_before'] == render['pdf_sha256_after'] == sha(pdf))
check('bounded page coverage', render['pages'] == pages and render['page_numbers'] == [1,5,6,98,99,100,101,122,123,124,125,126,127])
for number, row in render['rendered_pages'].items():
    check('render bytes: ' + number, sha(ROOT / row['path']) == row['sha256'])
review = read(OUT / 'render-review.json')
check('author review binds exact render', review['render_manifest_sha256'] == sha(OUT / 'render-final-manifest.json') and review['page_numbers'] == render['page_numbers'])
check('review text bound', review['author_review_sha256'] == sha(OUT / 'author-review.md'))
check('author review not promoted to human acceptance', review['independent_reader'] == review['human_acceptance'] == 'pending')

entry = read(ROOT / 'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
counts = {}
for group in ['protected_hashes', 'upstream_reference_hashes', 'controller_hashes']:
    mismatches = [name for name, expected in entry[group].items() if not (ROOT / name).is_file() or sha(ROOT / name) != expected]
    counts[group] = len(entry[group])
    check('historical ' + group + ' unchanged', not mismatches, {'count': counts[group], 'mismatches': mismatches})
continuation = read(ROOT / 'data/accounting-master/continuation-20261007/baseline-manifest.json')
relocations = {r['historical_path']: r['preserved_path'] for r in continuation['relocations']}
historical_mismatches = [name for name, expected in continuation['p19_historical_artifact_hashes'].items()
                        if sha(ROOT / relocations.get(name, name)) != expected]
check('P19 historical manifest resolves via preserved pointer copies', not historical_mismatches, historical_mismatches)
assessment = read(ROOT / 'data/accounting-master/deliverables/P19/readiness.json')
check('readiness remains negative', assessment['ready'] is False and assessment['status'] == 'not_ready')
dossier = read(OUT / 'adapter-dossier.json')
check('dossier binds retained graph', dossier['source_dependency_snapshot']['sha256'] == sha(OUT / 'graph-final.json'))
for name, anchor in dossier['source_anchors'].items():
    check('dossier source preserved: ' + name, sha(ROOT / anchor['path']) == anchor['sha256'])
graph = read(OUT / 'graph-final.json')
check('all graph node bytes preserved', all(sha(ROOT / node['path']) == node['sha256'] for node in graph['nodes']))
for name in ['graph-checks.json', 'dossier-checks.json']:
    report = read(OUT / name)
    check('saved bounded check is passing: ' + name, report['failed'] == 0 and all(r['passed'] for r in report['checks']))
report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
          'command': ['python3', str(Path(__file__).relative_to(ROOT))],
          'checker_sha256': sha(Path(__file__)), 'inputs': inputs,
          'pdf': {'path': str(pdf.relative_to(ROOT)), 'sha256': sha(pdf), 'pages': pages},
          'changed_sources': changed, 'display_count': len(displays(before_text)),
          'baseline_bibliography_keys': len(old_keys), 'candidate_bibliography_keys': len(keys),
          'preservation_counts': counts, 'checks': checks,
          'passed': sum(r['passed'] for r in checks), 'failed': sum(not r['passed'] for r in checks),
          'wall_seconds': time.monotonic() - start,
          'scope': 'Source preservation, final render/build and retained evidence integrity; no runtime, accounting or human acceptance'}
(OUT / 'manuscript-checks.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['passed','failed','display_count','baseline_bibliography_keys','candidate_bibliography_keys','wall_seconds']}))
if report['failed']:
    print([r for r in checks if not r['passed']])
    raise SystemExit(1)
