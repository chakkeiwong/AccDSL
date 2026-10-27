"""Bounded source, citation, equation, reference and rendering preservation checks."""
from collections import Counter
from pathlib import Path
import hashlib
import importlib.util
import json
import re

import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/design/proposal/manuscript-navigation-20261018'
NEXT = ROOT / 'docs/design/proposal/manuscript-early-conversion-20261018'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expanded(base, path='accounting-product-proposal.tex', seen=None):
    seen = [] if seen is None else seen
    seen.append(path)
    source = (base / path).read_text()
    return re.sub(r'\\(?:input|include)\{([^}]+)\}',
                  lambda m: expanded(base, m[1] + '.tex', seen), source)


def main():
    lock = json.loads((OUT / 'source-lock.json').read_text())
    assert sha(BASE / 'accounting-product-proposal.pdf') == lock['baseline_pdf_sha256']
    changed = []
    for row in lock['files']:
        old, new = BASE / row['path'], NEXT / row['path']
        assert sha(old) == row['baseline_sha256'], row['path']
        assert sha(new) == row['candidate_sha256'], row['path']
        if row['changed']:
            changed.append(row['path'])
    expected_changed = ['accounting-product-proposal.tex', 'references.bib',
                        'sections/company-eps-records.tex', 'sections/eps-lifecycle.tex']
    assert changed == expected_changed, changed
    for row in lock['external_support']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']

    old_seen, new_seen = [], []
    old, new = expanded(BASE, seen=old_seen), expanded(NEXT, seen=new_seen)
    assert len(old_seen) == len(set(old_seen)) and len(new_seen) == len(set(new_seen))
    assert old.count('\\begin{document}') == new.count('\\begin{document}') == 1
    old_body = old[old.index('\\begin{document}'):old.index('\\end{document}')]
    new_body = new[new.index('\\begin{document}'):new.index('\\end{document}')]
    assert old_body.count('Version 3.43 (proposal candidate)') == 1
    assert new_body.count('Version 3.44 (proposal candidate)') == 1
    assert '1 January 2026 maturity' in new_body
    assert 'without a conversion gain' in new_body and 'acceleration of the remaining interest' in new_body
    assert 'transaction outside exercise' in new_body and 'unchanged equity right' in new_body
    assert 'The tax benefit of 100' in new_body

    inventory_path = ROOT / 'data/accounting-master/continuous-reading-20261017/reading_inventory.py'
    spec = importlib.util.spec_from_file_location('reading_inventory', inventory_path)
    inventory = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inventory)

    def equations(source):
        source = re.sub(r'(?<!\\)%[^\n]*', '', source)
        source = re.sub(r'\\begin\{(lstlisting|verbatim|Verbatim)\}.*?\\end\{\1\}', '', source, flags=re.S)
        found, pos = [], 0
        while match := inventory.TOKEN.search(source, pos):
            pos = match.end()
            if match['heading']:
                _, pos = inventory.braces(source, pos)
            elif not match['input']:
                ending = r'\]' if match['bracket'] else '$$' if match['dollars'] else r'\end{' + match['math'] + '}'
                end = source.find(ending, pos)
                assert end >= 0
                found.append(source[match.start():end + len(ending)].strip())
                pos = end + len(ending)
        return Counter(found)

    eq_old, eq_new = equations(old), equations(new)
    assert eq_old == eq_new and sum(eq_new.values()) == 208
    citation_pattern = r'\\cite[a-zA-Z]*\*?(?:\[[^]]*\])?\{[^}]+\}'
    cite_old = Counter(re.findall(citation_pattern, old))
    cite_new = Counter(re.findall(citation_pattern, new))
    assert sum(cite_old.values()) == 716
    assert sum(cite_new.values()) == 718
    added_citations = [key for key, count in (cite_new - cite_old).items() for _ in range(count)]
    assert len(added_citations) == 2
    assert any('bdoconvertible2026' in key for key in added_citations)
    assert any('IFRIC~19' in key and 'IAS~8' in key for key in added_citations)
    labels_old = re.findall(r'\\label\{([^}]+)\}', old)
    labels_new = re.findall(r'\\label\{([^}]+)\}', new)
    assert labels_old == labels_new and len(labels_new) == len(set(labels_new))
    refs = re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}', new)
    assert not (set(refs) - set(labels_new))
    bbl = (NEXT / 'accounting-product-proposal.bbl').read_text()
    assert r'\bibitem[{BDO}(2026)]{bdoconvertible2026}' in bbl
    assert 'IFRS Accounting Standards in Practice: IAS 32 Accounting for Convertible Notes' in bbl
    log_text = (NEXT / 'accounting-product-proposal.log').read_text()
    warnings = [line for line in log_text.splitlines() if any(token in line for token in
        ('Overfull', 'undefined', 'multiply defined', 'Missing character', 'Fatal error', 'LaTeX Error'))]
    assert not warnings, warnings
    biblog = (NEXT / 'accounting-product-proposal.blg').read_text()
    assert 'Warning--' not in biblog and 'I found no' not in biblog

    old_pdf = fitz.open(BASE / 'accounting-product-proposal.pdf')
    new_pdf = fitz.open(NEXT / 'accounting-product-proposal.pdf')
    old_toc, new_toc = old_pdf.get_toc(), new_pdf.get_toc()
    assert [(level, title) for level, title, _ in old_toc] == [(level, title) for level, title, _ in new_toc]
    renders = OUT / 'rendered'
    renders.mkdir(exist_ok=True)
    pages, bounds = [], []
    for index, new_page in enumerate(new_pdf):
        old_page = old_pdf[index] if index < len(old_pdf) else None
        new_pix = new_page.get_pixmap(matrix=fitz.Matrix(110/72, 110/72), alpha=False)
        old_pix = old_page.get_pixmap(matrix=fitz.Matrix(110/72, 110/72), alpha=False) if old_page else None
        same = bool(old_pix and old_pix.samples == new_pix.samples and old_page.get_text() == new_page.get_text())
        row = dict(page=index + 1, baseline_page_exists=bool(old_page), same_pixels=same,
                   same_text=bool(old_page and old_page.get_text() == new_page.get_text()),
                   candidate_pixel_sha256=hashlib.sha256(new_pix.samples).hexdigest())
        if not same:
            target = renders / f'page-{index + 1:03}.png'
            new_pix.save(target)
            row['render'] = str(target.relative_to(ROOT))
        pages.append(row)
        for block in new_page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    x0, y0, x1, y1 = span['bbox']
                    if x0 < -1 or y0 < -1 or x1 > new_page.rect.width + 1 or y1 > new_page.rect.height + 1:
                        bounds.append(dict(page=index + 1, text=span['text']))
    assert not bounds, bounds
    result = dict(candidate_version='3.44', pdf=str((NEXT / 'accounting-product-proposal.pdf').relative_to(ROOT)),
                  pdf_sha256=sha(NEXT / 'accounting-product-proposal.pdf'), pages=len(new_pdf),
                  baseline_pages=len(old_pdf), source_files_checked=len(lock['files']), changed_sources=changed,
                  source_bindings_passed=True, displayed_equations=len(eq_new),
                  citation_occurrences_before=sum(cite_old.values()), citation_occurrences_after=sum(cite_new.values()),
                  added_citations=2, labels_preserved=True, references_resolved=True,
                  bibliography_entry_resolved=True, build_warnings=warnings, text_bounds=bounds,
                  changed_render_pages=[p['page'] for p in pages if not p['same_pixels']],
                  changed_text_pages=[p['page'] for p in pages if not p['same_text']],
                  render_identity_reading_inferred=False, independent_reader='pending', human_acceptance='pending',
                  proposal_status='not_ready')
    (OUT / 'candidate-checks.json').write_text(json.dumps(result, indent=2) + '\n')
    (OUT / 'page-comparison.json').write_text(json.dumps(dict(baseline_pdf_sha256=sha(BASE/'accounting-product-proposal.pdf'),
         candidate_pdf_sha256=result['pdf_sha256'], pages=pages, text_bounds=bounds,
         reading_inferred=False), indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
