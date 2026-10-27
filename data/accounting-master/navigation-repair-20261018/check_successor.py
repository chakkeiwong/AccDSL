"""Compare the actual D008 successor; identical renders are not new reading."""
from collections import Counter
from pathlib import Path
import hashlib
import importlib.util
import json
import re

import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/design/proposal/manuscript-readability-20261017'
NEXT = ROOT / 'docs/design/proposal/manuscript-navigation-20261018'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    lock = json.loads((OUT / 'source-lock.json').read_text())
    assert sha(BASE / 'accounting-product-proposal.pdf') == lock['baseline_pdf_sha256']
    changed = []
    for row in lock['files']:
        assert sha(BASE / row['path']) == row['baseline_sha256']
        assert sha(NEXT / row['path']) == row['candidate_sha256']
        if row['changed']:
            changed.append(row['path'])
    assert changed == ['accounting-product-proposal.tex', 'sections/corporate-methods.tex']
    before = (BASE / changed[1]).read_text()
    expected = before.replace(
        'The extended obligations for pensions, impairment, provisions, valuation and share-based payment are in the additional corporate methods that follow',
        'The corporate methods in this chapter cover pensions, impairment, provisions, valuation and share-based payment')
    assert expected != before and expected == (NEXT / changed[1]).read_text()
    assert (BASE / 'references.bib').read_bytes() == (NEXT / 'references.bib').read_bytes()
    assert (BASE / 'spec/core-0.lark').read_bytes() == (NEXT / 'spec/core-0.lark').read_bytes()
    spec = importlib.util.spec_from_file_location('prior', ROOT / 'data/accounting-master/readability-repair-20261017/check_candidate.py')
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    a, b = prior.expand(BASE), prior.expand(NEXT)
    start, end = '\\begin{document}', '\\end{document}'
    old_body, new_body = a[a.index(start):a.index(end)], b[b.index(start):b.index(end)]
    expected_body = old_body.replace('Version 3.42 (proposal candidate)', 'Version 3.43 (proposal candidate)').replace('17 October 2026', '18 October 2026').replace(
        'The extended obligations for pensions, impairment, provisions, valuation and share-based payment are in the additional corporate methods that follow',
        'The corporate methods in this chapter cover pensions, impairment, provisions, valuation and share-based payment')
    assert new_body == expected_body
    citations = r'\\cite[a-zA-Z]*\*?(?:\[[^]]*\])?\{[^}]+\}'
    ca, cb = Counter(re.findall(citations, a)), Counter(re.findall(citations, b))
    assert ca == cb and sum(cb.values()) == 716
    labels = re.findall(r'\\label\{([^}]+)\}', b)
    assert labels == re.findall(r'\\label\{([^}]+)\}', a)
    assert len(labels) == len(set(labels))
    assert not set(re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}', b)) - set(labels)
    # Exact expanded-body equality apart from two prose replacements preserves
    # every display, source boundary and qualifier; bind the reviewed inventory.
    structure = json.loads((ROOT / 'data/accounting-master/readability-repair-20261017/regression/structure.json').read_text())
    assert sum(n['kind'] == 'equation' for n in structure['nodes']) == 208
    log = (NEXT / 'accounting-product-proposal.log').read_text()
    warnings = [line for line in log.splitlines() if any(x in line for x in ('Overfull', 'undefined', 'multiply defined', 'Missing character', 'Fatal error', 'LaTeX Error'))]
    assert not warnings, warnings
    old = fitz.open(BASE / 'accounting-product-proposal.pdf')
    new = fitz.open(NEXT / 'accounting-product-proposal.pdf')
    assert len(old) == len(new) == 395
    assert old.get_toc() == new.get_toc()
    rendered = OUT / 'rendered'
    rendered.mkdir(exist_ok=True)
    pages = []
    bounds = []
    for number, (old_page, new_page) in enumerate(zip(old, new), 1):
        old_pix = old_page.get_pixmap(matrix=fitz.Matrix(110/72, 110/72), alpha=False)
        new_pix = new_page.get_pixmap(matrix=fitz.Matrix(110/72, 110/72), alpha=False)
        same = old_pix.samples == new_pix.samples
        row = dict(page=number, same_pixels=same, same_text=old_page.get_text() == new_page.get_text(),
                   baseline_pixel_sha256=hashlib.sha256(old_pix.samples).hexdigest(),
                   candidate_pixel_sha256=hashlib.sha256(new_pix.samples).hexdigest())
        if not same or number in range(161, 167):
            target = rendered / f'page-{number:03}.png'
            new_pix.save(target)
            row['render'] = dict(path=str(target.relative_to(ROOT)), sha256=sha(target), dpi=110)
        pages.append(row)
        for block in new_page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    x0, y0, x1, y1 = span['bbox']
                    if x0 < -1 or y0 < -1 or x1 > new_page.rect.width+1 or y1 > new_page.rect.height+1:
                        bounds.append(dict(page=number, text=span['text']))
    assert not bounds, bounds
    save('page-comparison.json', dict(baseline_pdf_sha256=sha(BASE / 'accounting-product-proposal.pdf'), candidate_pdf_sha256=sha(NEXT / 'accounting-product-proposal.pdf'), pages=pages, reading_inferred=False))
    result = dict(version='3.43', pdf=str((NEXT / 'accounting-product-proposal.pdf').relative_to(ROOT)),
                  pdf_sha256=sha(NEXT / 'accounting-product-proposal.pdf'), pages=395,
                  sources=len(lock['files']), changed_sources=changed,
                  displayed_equations=208, citation_occurrences=716,
                  changed_render_pages=[p['page'] for p in pages if not p['same_pixels']],
                  changed_text_pages=[p['page'] for p in pages if not p['same_text']],
                  material_build_warnings=warnings, text_bounds=bounds,
                  actual_body_delta='title version/date and D008 directional clause only',
                  all_checks_passed=True, independent_reader='pending', human_acceptance='pending',
                  proposal_status='not_ready')
    save('candidate-checks.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
