"""Check the bounded liquidity integration and cumulative preservation."""
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
OLD = ROOT / 'docs/design/proposal/manuscript-debt-20261009'
NEW = ROOT / 'docs/design/proposal/manuscript-liquidity-20261009'
START = time.monotonic()
if (OUT / 'completion.json').exists() or (OUT / 'candidate-checks.json').exists():
    raise SystemExit('Preserve previous candidate-check evidence before rerunning')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks, inputs = [], {}
def check(name, ok, detail=None):
    checks.append(dict(name=name, passed=bool(ok), detail=detail))
def read(p):
    inputs[str(p.relative_to(ROOT))] = sha(p)
    return json.loads(p.read_text())
def verify(name, hashes):
    bad = [p for p, h in hashes.items() if not (ROOT / p).exists() or sha(ROOT / p) != h]
    check(name, not bad, bad)
def displays(s):
    return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}', s, re.S)
def sources(base):
    return {p.relative_to(base): p for p in base.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}}
old, new = sources(OLD), sources(NEW)
check('every prior manuscript source retained', old.keys() <= new.keys())
changed, delta, display_changes, before, after = [], [], [], [], []
for n in sorted(new):
    a = old[n].read_text() if n in old else ''
    b = new[n].read_text()
    if a != b:
        changed.append(str(n))
        delta += list(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
            fromfile=str(OLD / n) if n in old else '/dev/null', tofile=str(NEW / n)))
    if n.suffix == '.tex':
        before.append(a)
        after.append(b)
        if n in old and displays(a) != displays(b):
            display_changes.append(str(n))
(OUT / 'manuscript-delta.diff').write_text(''.join(delta))
section, chapter = 'sections/apple-liquidity.tex', 'chapters/13-reference-company.tex'
check('bounded three-file source delta', set(changed) == {'accounting-product-proposal.tex', chapter, section}, changed)
check('earlier chapter retained with exactly one appended inclusion',
      (NEW / chapter).read_text() == (OLD / chapter).read_text() + '\n\\input{sections/apple-liquidity}\n')
check('title changes only version', (NEW / 'accounting-product-proposal.tex').read_text().replace('Version 2.13', 'Version 2.12') == (OLD / 'accounting-product-proposal.tex').read_text())
check('grammar listing retained', (NEW / 'spec/core-0.lark').read_bytes() == (OLD / 'spec/core-0.lark').read_bytes())
a, b, nd = '\n'.join(before), '\n'.join(after), (NEW / section).read_text()
check('44 prior displays retained with two new displays', not display_changes and len(displays(a)) == 44 and len(displays(b)) == 46 and len(displays(nd)) == 2,
      dict(changed=display_changes, old=len(displays(a)), new=len(displays(b))))
keys = lambda s: re.findall(r'@\w+\s*\{\s*([^,\s]+)', s)
ob, nb = (OLD / 'references.bib').read_text(), (NEW / 'references.bib').read_text()
check('all 66 bibliography entries retained exactly', ob == nb and len(keys(nb)) == 66)
cites = lambda s: {k.strip() for g in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', s) for k in g.split(',')}
check('citations retained and resolved', cites(a) <= cites(b) <= set(keys(nb)))
labels = re.findall(r'\\label\{([^}]+)\}', b)
refs = re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}', b)
check('unique labels and resolved references', len(labels) == len(set(labels)) and set(refs) <= set(labels))
check('scope qualifications present', all(s in ' '.join(nd.split()) for s in [
    'conditional compatibility check', 'not exact freely spendable balances',
    'it does not explain it', 'cause and location of the earlier 772 remain unallocated',
    'not recovered customer identities or probabilities of loss',
    'exact-centre membership does not permit an arbitrary continuously divisible overlap']))
pdf = NEW / 'accounting-product-proposal.pdf'
doc = fitz.open(pdf)
text = ' '.join(' '.join(p.get_text().split()) for p in doc)
text = re.sub(r'(?<=\d),\s+(?=\d)', ',', text)
check('key numerical consequences reach the PDF', all(s in text for s in [
    'Version 2.13', '140,749.5', '140,950.5', '137,942', '50,349', '13,690', '8,263', '2,303',
    '15,282', '6,054', '1,427', '772', '114', '174', '44%', '51%', '62%']))
log = (NEW / 'accounting-product-proposal.log').read_text()
warnings = [s for s in log.splitlines() if any(w in s for w in ['Warning', 'Overfull', 'Underfull', '! '])]
check('clean final LuaLaTeX log', 'LuaHBTeX' in log and not warnings, warnings)
check('clean bibliography log', not re.search(r'Warning--|error message|I couldn.t open', (NEW / 'accounting-product-proposal.blg').read_text()))
e = read(OUT / 'evidence-checks.json')
check('339 final source/arithmetic checks pass', e['failed'] == 0 and e['passed'] == 339 and e['checker_sha256'] == sha(OUT / 'prepare_evidence.py'))
verify('source inputs current', e['inputs'])
verify('source outputs current', e['output_hashes'])
c = read(OUT / 'source-claim-supplement.json')
check('full declared population retained', len(c['notes']) == 2 and len(c['material_units']) == 14 and len(c['dependencies']) == 13 and len(c['queries']) == 11 and
      c['coverage']['investment_numeric_cells'] == 392 and c['coverage']['unique_dated_investment_cells'] == 294 and c['coverage']['statement_numeric_cells'] == 90)
calc = read(OUT / 'calculations.json')
table_rows = re.findall(r'^([^\n&]+)&([^\n&]+)&([^\n&]+)&([^\n]+?)\\\\', nd, re.M)
numeric = []
for label, *cells in table_rows:
    if label.strip() != 'Resource / measurement' and all(re.fullmatch(r'\s*\$?[+-]?[\d,]+\$?\s*', x) for x in cells):
        numeric.append([int(re.sub(r'[^\d+-]', '', x)) for x in cells])
totals = [c['tables'][k]['rows'][-1]['values'] for k in ['annual.investment_2023', 'annual.investment_2024', 'interim.investment_december']]
expected = [[t[i] for t in totals] for i in [4, 5, 6, 3, 0]] + [[t[1] + t[2] for t in totals]]
check('all resource-table numbers agree with pinned source columns', numeric == expected, numeric)
shares = re.search(r'\$18,11,9,9,8,7,4,9,9,8,8\$', nd)
check('whole-customer example agrees with checked constructions', bool(shares) and
      all(x['customer_shares'] == [18, 11, 9, 9, 8, 7, 4, 9, 9, 8, 8] for x in calc['concentration']['alternatives']))
check('prior debt/tax/asset/EPS additions unchanged', all((NEW / n).read_bytes() == (OLD / n).read_bytes() for n in [
    'sections/apple-debt.tex', 'sections/apple-tax-settlement.tex', 'sections/apple-operating-assets.tex', 'sections/apple-eps-ownership.tex']))
render, review = read(OUT / 'render-manifest.json'), read(OUT / 'render-review.json')
check('render bound to final PDF and script', render['pdf_sha256_before'] == render['pdf_sha256_after'] == sha(pdf) and render['script_sha256'] == sha(OUT / 'render_candidate.py'))
verify('render image hashes current', {r['path']: r['sha256'] for g in ['rendered_pages', 'contact_sheets'] for r in render[g].values()})
check('actual author review bound', review['render_manifest_sha256'] == sha(OUT / 'render-manifest.json') and review['author_review_sha256'] == sha(OUT / 'author-review.md') and
      review['page_numbers'] == render['page_numbers'] and review['continuous_read_pages'] == list(range(20, 26)))
check('independent/human acceptance pending', review['independent_reader'] == review['human_acceptance'] == 'pending')
sr = read(OUT / 'source-render-receipt.json')
check('source render bound to current inputs', sr['source_supplement_sha256'] == sha(OUT / 'source-claim-supplement.json') and sr['script_sha256'] == sha(OUT / 'render_sources.py') and
      sr['derived_html_sha256'] == sha(ROOT / sr['derived_html']) and sr['derived_pdf_sha256'] == sha(ROOT / sr['derived_pdf']))
verify('original and derived source images retained', {r['path']: r['sha256'] for r in sr['rendered_images']})
build = read(OUT / 'build-receipt.json')
check('successful build receipt binds PDF and log', build['exit_code'] == 0 and build['pdf_sha256'] == sha(pdf) and build['log_sha256'] == sha(OUT / 'build.log') and build['script_sha256'] == sha(OUT / 'build_candidate.py'))
attempt = read(OUT / 'candidate-attempt-01/preservation.json')
verify('superseded candidate evidence preserved', {r['preserved_path']: r['sha256'] for r in attempt['relocations']})
baseline = read(OUT / 'baseline.json')
verify('baseline candidate and closed unit retained', baseline['protected_hashes'])
rel = {r['historical_path']: r['preserved_path'] for r in baseline['pointer_relocations']}
previous = read(ROOT / baseline['prior_manifest'])
verify('preceding manifest resolves preserved live pointers', {rel.get(n, n): h for n, h in previous['artifact_hashes'].items()})
history = read(ROOT / 'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
counts = {}
for k in ['protected_hashes', 'upstream_reference_hashes', 'controller_hashes']:
    verify('historical ' + k, history[k])
    counts[k] = len(history[k])
p19 = read(ROOT / 'data/accounting-master/continuation-20261007/baseline-manifest.json')
rel = {r['historical_path']: r['preserved_path'] for r in p19['relocations']}
verify('P19 historical hashes resolved', {rel.get(n, n): h for n, h in p19['p19_historical_artifact_hashes'].items()})
r = read(ROOT / 'data/accounting-master/deliverables/P19/readiness.json')
check('full readiness remains negative', r['status'] == 'not_ready' and not r['ready'] and set(r['remaining_blockers']) == {'P15-' + x for x in ['E01', 'E05', 'E07', 'E08', 'E14']})
report = dict(recorded_at=datetime.now(timezone.utc).isoformat(), checker_sha256=sha(Path(__file__)), inputs=inputs,
    pdf=dict(path=str(pdf.relative_to(ROOT)), sha256=sha(pdf), pages=len(doc)), changed_sources=changed,
    baseline_displays=44, candidate_displays=46, bibliography_keys=66, preservation_counts=counts,
    checks=checks, passed=sum(c['passed'] for c in checks), failed=sum(not c['passed'] for c in checks), wall_seconds=time.monotonic() - START)
(OUT / 'candidate-checks.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['passed', 'failed', 'pdf', 'preservation_counts']}))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']]))
    raise SystemExit(1)
