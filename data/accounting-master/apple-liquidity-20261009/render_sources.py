"""Render pinned annual pages and a text/column-preserving interim source view."""
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
if (OUT / 'completion.json').exists() or (OUT / 'source-render-receipt.json').exists():
    raise SystemExit('Preserve earlier renders before rerunning')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda s: re.sub(r'\s+', '', s)
record = json.loads((OUT / 'source-claim-supplement.json').read_text())
annual = ROOT / 'docs/design/cases/apple/annual-2024.pdf'
doc = fitz.open(annual)
pages = [28, 29, 30, 33, 34, 36, 37, 39, 40, 41, 42, 43, 44]
images, preserved = [], []
for n in pages:
    p = OUT / 'source-render' / f'annual-{n:03}.png'
    if not p.exists():
        doc[n - 1].get_pixmap(matrix=fitz.Matrix(1.7, 1.7)).save(p)
    images.append(dict(path=str(p.relative_to(ROOT)), sha256=sha(p), original_pdf_page=n))
original_path = ROOT / 'docs/design/cases/apple/interim-2025q1.html'
original = BeautifulSoup(original_path.read_text(), 'html.parser')
tables = original.find_all('table')


def table_html(index):
    investment = index in [19, 20]
    columns = 8 if investment else 3
    rows = []
    for tr in tables[index].find_all('tr'):
        cells = tr.find_all(['td', 'th'], recursive=False)
        texts = [c.get_text(' ', strip=True) for c in cells]
        nonempty = [s for s in texts if s]
        if not nonempty:
            continue
        if len(nonempty) == 1:
            rows.append('<tr><td colspan="' + str(columns) + '">' + html.escape(nonempty[0]) + '</td></tr>')
            continue
        if investment:
            grid = []
            for c, s in zip(cells, texts):
                grid.extend([s] + [''] * (int(c.get('colspan', 1)) - 1))
            assert len(grid) == 42, (index, grid)
            merged = [' '.join(s for s in grid[:3] if s)]
            for start in range(3, 42, 6):
                assert not any(grid[start + 3:start + 6]), (index, start, grid)
                merged.append(' '.join(s for s in grid[start:start + 3] if s))
        else:
            merged, i = [], 0
            while i < len(nonempty):
                if nonempty[i] == '$':
                    merged.append('$ ' + nonempty[i + 1]); i += 2
                else:
                    merged.append(nonempty[i]); i += 1
            if len(merged) == 2:
                assert merged[0].startswith('December'), merged
                merged = [''] + merged
        assert len(merged) == columns, (index, merged)
        widths = [26] + [74 / 7] * 7 if investment else [62, 19, 19]
        rows.append('<tr>' + ''.join('<td style="width:' + str(widths[n]) + '%;text-align:' + ('left' if n == 0 else 'right') + '">' + html.escape(s) + '</td>' for n, s in enumerate(merged)) + '</tr>')
    result = '<table>' + ''.join(rows) + '</table>'
    assert norm(tables[index].get_text()) == norm(BeautifulSoup(result, 'html.parser').get_text())
    preserved.append(dict(id='HTML table ' + str(index), all_cell_text_in_order=True, columns=columns,
                          alignment='Original colspan grid groups' if investment else 'Label and two dated columns'))
    return result


def paragraph(q):
    return '<p>' + html.escape(' '.join(q.split())) + '</p>' if q.strip() else ''


def excerpt(ident, source, table_indices=()):
    q = source['quote']
    positions = [i for i, c in enumerate(q) if not c.isspace()]
    replacements = []
    for index in table_indices:
        needle = norm(tables[index].get_text())
        start = norm(q).index(needle)
        a, b = positions[start], positions[start + len(needle) - 1] + 1
        replacements.append((a, b, table_html(index)))
    cursor, parts = 0, []
    for a, b, replacement in sorted(replacements):
        parts.extend([paragraph(q[cursor:a]), replacement]); cursor = b
    parts.append(paragraph(q[cursor:]))
    body = ''.join(parts)
    assert norm(BeautifulSoup(body, 'html.parser').get_text()) == norm(q)
    preserved.append(dict(id=ident, complete_excerpt_text_preserved=True, start=source['start'], end=source['end']))
    return '<h2>' + html.escape(ident) + ' — retained span ' + str(source['start']) + '–' + str(source['end']) + '</h2>' + body


blocks = []
for u in record['material_units']:
    if u['source'] != 'interim':
        continue
    indices = {'investment_december': [19], 'investment_september': [20], 'hedging': [21]}.get(u['id'].split('.')[-1], [])
    blocks.append(excerpt(u['id'], u, indices))
for ident in ['interim.basis_calendar', 'interim.liquidity', 'interim.market_risk']:
    blocks.append(excerpt(ident, record['dependencies'][ident]))
for index, title in [(13, 'Comprehensive income — USD millions'),
                     (14, 'Balance sheet — USD millions, except shares in thousands and par value'),
                     (16, 'Cash flows — USD millions')]:
    blocks.append('<h2>' + title + '</h2>' + table_html(index))
view = ('<html><body><h1>Apple Q1 FY2025 — derived liquidity source view</h1>'
        '<p>Local reflow of the retained SEC HTML/text, not an original filing page or a new acquisition. '
        'The complete Note 4 and selected complete dependency excerpts retain all text in order. '
        'Investment tables retain the label plus seven original measurement/classification columns.</p>'
        + ''.join(blocks) + '</body></html>')
src = OUT / 'sources/interim-liquidity-print.html'
src.write_text(view)
dst = OUT / 'source-render/interim-liquidity-derived.pdf'
story = fitz.Story(html=view, user_css='body {font-family:sans-serif;font-size:10.5pt;} h1 {font-size:15pt;} h2 {font-size:12pt;} table {width:100%;font-size:9pt;} td {padding:3pt;} p {margin-bottom:8pt;}')
writer = fitz.DocumentWriter(str(dst))
page = fitz.paper_rect('a4-l')
where = page + (30, 30, -30, -30)
more, count = True, 0
while more:
    count += 1
    if count > 18:
        raise RuntimeError('Source view exceeded bounded page count')
    dev = writer.begin_page(page)
    more, _ = story.place(where)
    story.draw(dev); writer.end_page()
writer.close()
derived = fitz.open(dst)
for n, pg in enumerate(derived, 1):
    p = OUT / 'source-render' / f'interim-liquidity-{n:03}.png'
    pg.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(p)
    images.append(dict(path=str(p.relative_to(ROOT)), sha256=sha(p), derived_pdf_page=n))
receipt = dict(recorded_at=datetime.now(timezone.utc).isoformat(), script_sha256=sha(Path(__file__)),
    source_supplement_sha256=sha(OUT / 'source-claim-supplement.json'), annual_source=str(annual.relative_to(ROOT)), annual_sha256=sha(annual),
    annual_pages=pages, interim_original_sha256=sha(original_path), derived_html=str(src.relative_to(ROOT)), derived_html_sha256=sha(src),
    derived_pdf=str(dst.relative_to(ROOT)), derived_pdf_sha256=sha(dst), derived_pages=len(derived),
    text_preservation=preserved, rendered_images=images, scope='Original annual pages and explicitly derived interim excerpts; no browser screenshot claim.')
(OUT / 'source-render-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(dict(annual_pages=len(pages), derived_pages=len(derived))))
