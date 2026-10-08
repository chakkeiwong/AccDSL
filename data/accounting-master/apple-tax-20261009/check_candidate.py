"""Check the bounded tax argument, its rendered evidence and preservation."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import re
import time

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/manuscript-assets-20261008'
NEW = ROOT / 'docs/design/proposal/manuscript-tax-20261009'
START = time.monotonic()
if (OUT / 'completion.json').exists():
    raise SystemExit('Closed unit')
checks, inputs = [], {}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    inputs[str(p.relative_to(ROOT))] = sha(p)
    return json.loads(p.read_text())


def check(name, passed, detail=None):
    checks.append(dict(name=name, passed=bool(passed), detail=detail))


def verify(name, hashes):
    bad = [n for n, h in hashes.items() if not (ROOT / n).is_file() or sha(ROOT / n) != h]
    check(name, not bad, dict(count=len(hashes), mismatches=bad))


baseline = read(OUT / 'baseline.json')
verify('V2.9 unit and retained source inputs preserved', baseline['protected_hashes'])
reloc = {r['historical_path']: r['preserved_path'] for r in baseline['pointer_relocations']}
verify('prior live pointer copies preserved', {r['preserved_path']: r['sha256'] for r in baseline['pointer_relocations']})
previous = read(ROOT / baseline['prior_manifest'])
verify('prior manifest references resolved', {reloc.get(n, n): h for n, h in previous['artifact_hashes'].items()})
oldfiles = {p.relative_to(OLD) for p in OLD.rglob('*') if p.suffix in {'.tex', '.bib', '.lark'}}
newfiles = {p.relative_to(NEW) for p in NEW.rglob('*') if p.suffix in {'.tex', '.bib', '.lark'}}
newsection = Path('sections/apple-tax-settlement.tex')
check('source inventory adds only the declared section', newfiles == oldfiles | {newsection})
before, after, changed, diff = [], [], [], []
pattern = r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{\1\}'
displays = lambda t: [m.group() for m in re.finditer(pattern, t, re.S)]
display_changes = []
for n in sorted(newfiles):
    a = (OLD / n).read_text() if n in oldfiles else ''
    b = (NEW / n).read_text()
    inputs[str((NEW / n).relative_to(ROOT))] = sha(NEW / n)
    if a != b:
        changed.append(str(n))
        diff.extend(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
                    fromfile=str(OLD / n) if n in oldfiles else '/dev/null', tofile=str(NEW / n)))
    if n.suffix == '.tex':
        before.append(a)
        after.append(b)
        if n in oldfiles and displays(a) != displays(b):
            display_changes.append(str(n))
(OUT / 'manuscript-delta.diff').write_text(''.join(diff))
check('exactly two existing sources plus one new source changed', set(changed) == {
    'accounting-product-proposal.tex', 'sections/corporate-methods.tex',
    str(newsection)})
a, b = '\n'.join(before), '\n'.join(after)
old_displays, new_displays = displays(a), displays(b)
addition = (NEW / newsection).read_text()
check('all old displays preserved per file with one added tax equation',
      not display_changes and len(old_displays) == 40 and len(new_displays) == 41
      and len(displays(addition)) == 1 and '\\label{eq:apple-tax-bridges}' in displays(addition)[0],
      dict(before=len(old_displays), after=len(new_displays), old_files_with_display_changes=display_changes))
check('entire earlier Apple chapter preserved',
      (OLD / 'chapters/13-reference-company.tex').read_bytes() == (NEW / 'chapters/13-reference-company.tex').read_bytes())
old_methods = (OLD / 'sections/corporate-methods.tex').read_text()
new_methods = (NEW / 'sections/corporate-methods.tex').read_text()
check('corporate methods preserved around one inclusion',
      new_methods.replace('\\input{sections/apple-tax-settlement}\n\n', '') == old_methods)
check('source admission preserved exactly',
      (NEW / 'sections/source-admission.tex').read_bytes() == (OLD / 'sections/source-admission.tex').read_bytes())
check('title changed only to Version 2.10 and current date',
      (NEW / 'accounting-product-proposal.tex').read_text().replace('Version 2.10', 'Version 2.9').replace('9 October 2026','8 October 2026') ==
      (OLD / 'accounting-product-proposal.tex').read_text())
check('new narrative retains material assumptions and limits', all(s in ' '.join(addition.split()) for s in [
    'diagnostic definitions', 'same recognition or settlement scope', 'wrong closing payable',
    'remains unresolved here', 'not a separately disclosed liability',
    'conditional rounding check', 'tie convention unverified',
    'Neither calculation supplies a common exchange rate',
    "the liability's carrying value", 'omits any associated gain, loss or fee',
    'Interest and penalties are excluded', 'neither a probability law']))
keys = lambda t: re.findall(r'@\w+\s*\{\s*([^,\s]+)', t)
old_bib, new_bib = (OLD / 'references.bib').read_text(), (NEW / 'references.bib').read_text()
check('all 66 bibliography entries preserved exactly', old_bib == new_bib and len(keys(new_bib)) == 66)
cites = lambda t: {k.strip() for g in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', t) for k in g.split(',')}
check('prior citations retained and every citation resolves', cites(a) <= cites(b) <= set(keys(new_bib)))
labels = re.findall(r'\\label\{([^}]+)\}', b)
refs = re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}', b)
check('labels are unique and all references resolve', len(labels) == len(set(labels)) and set(refs) <= set(labels))
pdf = NEW / 'accounting-product-proposal.pdf'
doc = fitz.open(pdf)
text = ' '.join(' '.join(p.get_text().split()) for p in doc)
text = re.sub(r'(?<=\d),\s+(?=\d)', ',', text)
check('material quantities appear in final PDF', all(s in text for s in [
    'Version 2.10', '32,780', '3,031', '29,749', '26,102', '11,579', '6,678',
    '4,901', '1,951', '1,080', '10,246', '10,177', '10,076.5', '10,277.5',
    '126', '3,426', '18,651', '22,038']))
log = (NEW / 'accounting-product-proposal.log').read_text()
warnings = [l for l in log.splitlines() if any(s in l for s in ['Warning', 'Overfull', 'Underfull', '! '])]
check('clean final LuaLaTeX log', 'LuaHBTeX' in log and not warnings, warnings)
check('clean bibliography log', not re.search(r'Warning--|error message|I couldn.t open', (NEW / 'accounting-product-proposal.blg').read_text()))
e = read(OUT / 'evidence-checks.json')
check('source and calculation check report is current', e['failed'] == 0 and e['passed'] == 148
      and all(c['passed'] for c in e['checks']) and e['checker_sha256'] == sha(OUT / 'prepare_evidence.py'))
verify('source check inputs current', e['inputs'])
verify('source claim and calculation outputs bound', e['output_hashes'])
ledger = read(OUT / 'source-claim-supplement.json')
check('bounded note population stays separate from whole-package closure',
      len(ledger['units']) == 12 and len(ledger['dependencies']) == 18
      and ledger['coverage']['note_monetary_cells'] == 109 and ledger['coverage']['note_percentage_cells'] == 3 and len(ledger['queries']) == 9
      and ledger['coverage']['whole_apple_package'] == 'open'
      and ledger['coverage']['outstanding_exhibit_targets'] == 40)
build = read(OUT / 'build-receipt.json')
check('successful build binds final PDF and log', build['exit_code'] == 0
      and build['pdf_sha256'] == sha(pdf) and build['log_sha256'] == sha(OUT / 'build.log'))
render, review = read(OUT / 'render-manifest.json'), read(OUT / 'render-review.json')
check('render binds final PDF', render['pdf_sha256_before'] == render['pdf_sha256_after'] == sha(pdf))
verify('render image and contact-sheet hashes current',
       {r['path']: r['sha256'] for group in ['rendered_pages', 'contact_sheets'] for r in render[group].values()})
check('author inspection binds actual rendered pages',
      review['render_manifest_sha256'] == sha(OUT / 'render-manifest.json')
      and review['author_review_sha256'] == sha(OUT / 'author-review.md')
      and review['page_numbers'] == render['page_numbers'])
check('independent and human acceptance remain pending', review['independent_reader'] == review['human_acceptance'] == 'pending')
source_render = read(OUT / 'source-render-receipt.json')
check('derived HTML renders preserve retained source text', all(
    sha(Path(r['source_html'])) == r['sha256'] and sha(Path(r['pdf'])) == r['pdf_sha256']
    and r['text_preserved_after_namespace_unwrap'] for r in source_render['records']))
verify('original and derived source images preserved', {r['path']: r['sha256'] for r in source_render['rendered_images']})
history = read(ROOT / 'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
counts = {}
for k in ['protected_hashes', 'upstream_reference_hashes', 'controller_hashes']:
    verify('historical ' + k, history[k])
    counts[k] = len(history[k])
c = read(ROOT / 'data/accounting-master/continuation-20261007/baseline-manifest.json')
rel = {r['historical_path']: r['preserved_path'] for r in c['relocations']}
verify('P19 hashes resolve through historical paths', {rel.get(n, n): h for n, h in c['p19_historical_artifact_hashes'].items()})
readiness = read(ROOT / 'data/accounting-master/deliverables/P19/readiness.json')
check('full proposal negative assessment retained', readiness['status'] == 'not_ready' and not readiness['ready']
      and set(readiness['remaining_blockers']) == {'P15-' + s for s in ['E01', 'E05', 'E07', 'E08', 'E14']})
report = dict(recorded_at=datetime.now(timezone.utc).isoformat(), checker_sha256=sha(Path(__file__)),
    inputs=inputs, pdf=dict(path=str(pdf.relative_to(ROOT)), sha256=sha(pdf), pages=len(doc)),
    changed_sources=changed, baseline_displays=len(old_displays), candidate_displays=len(new_displays),
    bibliography_keys=len(keys(new_bib)), preservation_counts=counts, checks=checks,
    passed=sum(c['passed'] for c in checks), failed=sum(not c['passed'] for c in checks),
    wall_seconds=time.monotonic() - START)
(OUT / 'candidate-checks.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['passed', 'failed', 'baseline_displays', 'candidate_displays', 'bibliography_keys']}))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']]))
    raise SystemExit(1)
