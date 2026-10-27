"""Verify the bounded insertion, protected evidence, citations and final build."""
import hashlib
import json
import re
import time
from pathlib import Path
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not (OUT / 'completion.json').exists(), 'Closed evidence stays frozen'
    baseline = json.loads((OUT / 'baseline.json').read_text())
    base = (ROOT / baseline['baseline_pdf']['path']).parent
    cand = ROOT / baseline['candidate']
    checks = []
    def ck(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    ck('protected baseline PDF', sha(base / 'accounting-product-proposal.pdf') == baseline['baseline_pdf']['sha256'])
    files = baseline['source_hashes']
    actual = {str(p.relative_to(cand)) for p in cand.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}}
    ck('same author-source inventory', actual == set(files))
    addition = (OUT / 'addition.tex').read_text()
    anchor = "\\newpage\n\nThe complete Form~10-Ks describe Series~A as the issuer's direct, unsecured"
    changed = []
    for rel, digest in sorted(files.items()):
        old = (base / rel).read_text()
        new = (cand / rel).read_text()
        ck('baseline source ' + rel, sha(base / rel) == digest)
        expected = old
        if rel == 'accounting-product-proposal.tex':
            expected = old.replace('Version 2.35 (proposal candidate)', 'Version 2.36 (proposal candidate)')
        elif rel == 'chapters/15-banking.tex':
            ck('one insertion anchor', old.count(anchor) == 1)
            expected = old.replace(anchor, addition + anchor)
        ck('exact candidate source ' + rel, new == expected)
        if new != old:
            changed.append(rel)
    ck('only title and banking chapter changed', set(changed) == {'accounting-product-proposal.tex', 'chapters/15-banking.tex'})
    before = '\n'.join((base / p).read_text() for p in sorted(files) if p.endswith('.tex'))
    after = '\n'.join((cand / p).read_text() for p in sorted(files) if p.endswith('.tex'))
    pattern = re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}', re.S)
    displays = lambda t: [m.group() for m in pattern.finditer(t)]
    ck('48 unchanged displays', displays(before) == displays(after) and len(displays(after)) == 48)
    labels = re.findall(r'\\label\{([^{}]+)\}', after)
    refs = re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}', after)
    ck('labels unique', len(labels) == len(set(labels)))
    ck('references resolve', set(refs) <= set(labels))
    bib = (cand / 'references.bib').read_text()
    keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib)
    cited = {k.strip() for group in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}', after) for k in group.split(',')}
    ck('75 unchanged bibliography entries', len(keys) == len(set(keys)) == 75 and bib == (base / 'references.bib').read_text())
    ck('citations resolve', cited <= set(keys))
    unit = ROOT / baseline['source_unit']
    m = json.loads((unit / 'run-manifest.json').read_text())
    c = json.loads((unit / 'completion.json').read_text())
    ck('closed source manifest intact', c['manifest_sha256'] == sha(unit / 'run-manifest.json') and c['failed'] == 0)
    ck('50 source and 47 closeout checks preserved', c['source_checks'] == 50 and c['closeout_checks'] == 47)
    for rel, digest in m['artifact_hashes'].items():
        ck('source artifact ' + rel, sha(ROOT / rel) == digest)
    for item in baseline['pointer_snapshots']:
        ck('preserved control ' + item['live'], sha(ROOT / item['snapshot']) == item['sha256'])
    pdf = cand / 'accounting-product-proposal.pdf'
    with fitz.open(pdf) as doc:
        count = len(doc)
        text = ' '.join(doc[115].get_text().split())
        ck('parent example together with citation', all(s in text for s in ['Note 33', '57,048', '71,163', '14,115', '50,000', '8,583', '44,468', '9,790', '8.0bn', '669,449', '44,512', '34m', '310–311']))
        ck('forward funding boundary on same page', all(s in text for s in ['payment dates', 'permissible', 'deposit terms', 'funding actions']))
        ck('debt figures together with source citation', all(s in text for s in ['253,039', '254,633', '1,594', '1,603', '14,298', '14.3bn', '18.1bn', '57.6bn', '435,206', '47.6bn', '281–282, 310–311']))
        ck('arithmetic match not a legal or accounting explanation', all(s in text for s in ['does not establish why', 'which legal entity owes', 'still needs source support']))
        ck('carrying value and contractual payments remain distinct', all(s in text for s in ['premiums', 'discounts, costs and valuation adjustments', 'principal payable', 'neither a liability valuation nor a payment forecast']))
        ck('instrument discussion starts next page', "The complete Form 10-Ks" in doc[116].get_text())
        ck('historical ASU boundary retained', 'not verified current Codification' in ' '.join(doc[119].get_text().split()))
    renders = json.loads((OUT / 'render-manifest.json').read_text())
    ck('render PDF binding', renders['pdf_sha256'] == sha(pdf))
    ck('ordered bank and transition renders', [r['pdf_page'] for r in renders['renders']] == list(range(115, 127)))
    for r in renders['renders']:
        ck('final render ' + str(r['pdf_page']), sha(ROOT / r['image']) == r['sha256'])
    prior = json.loads((OUT.parent / 'accounting-proposal-v235-integration-20261012/render-manifest.json').read_text())
    prior_hashes = {r['pdf_page']: r['sha256'] for r in prior['renders']}
    ck('only bank page 116 changes from inspected baseline renders', [r['pdf_page'] for r in renders['renders'] if r['sha256'] != prior_hashes[r['pdf_page']]] == [116])
    log = (cand / 'accounting-product-proposal.log').read_text(errors='replace')
    warnings = [s for s in log.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning', s)]
    ck('clean final TeX log', not warnings)
    blg = (cand / 'accounting-product-proposal.blg').read_text(errors='replace')
    ck('clean bibliography log', 'Warning--' not in blg and "I didn't find" not in blg)
    failed = [r['name'] for r in checks if not r['passed']]
    result = {'checks': checks, 'passed': len(checks) - len(failed), 'failed': failed, 'pages': count, 'candidate_pdf': {'path': str(pdf.relative_to(ROOT)), 'sha256': sha(pdf)}, 'warnings': warnings, 'wall_seconds': time.monotonic() - START, 'readiness': 'not_ready'}
    (OUT / 'check-run.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['passed', 'failed', 'pages', 'candidate_pdf']}))
    raise SystemExit(bool(failed))

if __name__ == '__main__':
    main()
