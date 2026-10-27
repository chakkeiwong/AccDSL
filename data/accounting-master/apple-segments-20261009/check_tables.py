"""Independently check positional cells and extend witnesses to all products."""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
if (OUT / 'table-checks.json').exists():
    raise SystemExit('Preserve earlier table checks')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda s: re.sub(r'\s+', '', s)
source = json.loads((OUT / 'source-claim-supplement.json').read_text())
calc = json.loads((OUT / 'calculations.json').read_text())
doc = fitz.open(ROOT / source['sources']['annual']['original_path'])
soup = BeautifulSoup((ROOT / source['sources']['interim']['original_path']).read_text(), 'html.parser')
checks, cells, rows = [], [], {}


def check(name, ok, detail=None):
    checks.append(dict(name=name, passed=bool(ok), detail=detail))


def values(s):
    s = re.sub(r'\(\s*([\d,]+)\s*\)', r'-\1', s)
    return [int(v.replace(',', '')) for v in re.findall(r'-?\d[\d,]*', s)]


def annual_row(ident, quote, label, expected, page=50, occurrence=0):
    found = [line for line in quote.splitlines() if re.split(r'\s{2,}', line.strip())[0] == label]
    line = found[occurrence]
    raw = re.split(r'\s{2,}', line.strip(), maxsplit=1)[1]
    got = values(raw)
    original = doc[page - 1].get_text()
    compared = line
    if '(1)' in label:
        # The retained PDF text stream places the superscript separately.
        # Keep its existence and original visual association as separate checks.
        check(ident + ' PDF superscript retained', '(1)' in original)
        compared = line.replace('(1)', '', 1)
    check(ident + ' original PDF ordered row', norm(compared) in norm(original), line)
    check(ident + ' positional numeric row', got == expected, got)
    rows[ident] = dict(label=label, values=got, literal=line, original_pdf_page=page)
    cells.extend((ident, j, v) for j, v in enumerate(got))
    return got


def html_rows(index):
    out = []
    for tr in soup.find_all('table')[index].find_all('tr'):
        vals = [c.get_text(' ', strip=True) for c in tr.find_all(['td','th'],recursive=False)]
        nonempty = [v for v in vals if v]
        if nonempty:
            out.append((nonempty[0], values(' '.join(nonempty[1:])), vals))
    return out


def interim_row(ident, index, label, expected, occurrence=0):
    found = [r for r in html_rows(index) if r[0] == label]
    _, got, raw = found[occurrence]
    check(ident + ' original HTML positional row', got == expected, got)
    rows[ident] = dict(label=label, values=got, original_cells=raw, html_table_index=index)
    cells.extend((ident, j, v) for j, v in enumerate(got))
    return got


names = list(source['tables']['annual.sales']['rows'])
for key in ['annual', 'interim']:
    q = source['notes'][key + '.note.' + ('13' if key == 'annual' else '10')]['quote']
    for j, name in enumerate(names):
        for measure, label in [('sales','Net sales'), ('income','Operating income')]:
            want = source['tables'][key + '.' + measure]['rows'][name]
            ident = key + '.segment.' + name + '.' + measure
            if key == 'annual':
                annual_row(ident,q,label,want,occurrence=j)
            else:
                interim_row(ident,26,label,want,occurrence=j)
    for measure,label in [('segment','Segment operating income'), ('rd','Research and development expense'),
                          ('other','Other corporate expenses, net'), ('consolidated','Total operating income')]:
        want = source['tables'][key + '.bridge'][measure]
        if measure in ['rd','other']: want = [-v for v in want]
        ident = key + '.bridge.' + measure
        if key == 'annual':
            annual_row(ident,q,label + (' (1)' if measure == 'other' else ''),want)
        else:
            interim_row(ident,27,label,want)
    # Validate issuer date/period headers, not just the numeric multiset.
    check(key + ' segment dated header', all(x in q for x in
          (['2024','2023','2022'] if key == 'annual' else ['Three Months Ended','December 28,','December 30,','2024','2023'])))

q = source['notes']['annual.note.13']['quote']
for measure, occurrence in [('country_sales',0), ('long_lived_assets',1)]:
    tab = source['tables']['annual.' + measure]
    for label,key in [('U.S.','U.S.'),('China (1)','China (incl. HK/Taiwan)'),('Other countries','Other countries')]:
        annual_row('annual.'+measure+'.'+key,q,label,tab['rows'][key],occurrence=occurrence)
    annual_row('annual.'+measure+'.total',q,'Total net sales' if measure == 'country_sales' else 'Total long-lived assets',tab['totals'])
note_cells = len(cells)
check('all note table cells accounted for once', note_cells == 90, note_cells)

products = ['iPhone','Mac','iPad','Wearables, Home and Accessories','Services']
product_values = [[201183,200583,205489],[29984,29357,40177],[26694,28300,29292],
                  [37005,39845,41241],[96169,85200,78129]]
quarter_values = [[69138,69702],[8987,7780],[8088,7023],[11747,11953],[26340,23117]]
for j,name in enumerate(products):
    annual_row('annual.product.'+name, source['dependencies']['annual.note2']['quote'],
               name + (' (1)' if name == 'Services' else ''),product_values[j],page=38)
    interim_row('interim.product.'+name,17,name + (' ®' if name in ['iPhone','Mac','iPad'] else ''),quarter_values[j])
for key,index in [('annual',None),('interim',12)]:
    specs = [('sales','Total net sales',[391035,383285,394328],[124300,119575]),
             ('rd','Research and development',[31370,29915,26251],[8268,7696]),
             ('sga','Selling, general and administrative',[26097,24932,25094],[7175,6786]),
             ('operating_income','Operating income',[123216,114301,119437],[42832,40373])]
    for name,label,a,b in specs:
        if key == 'annual':
            annual_row(key+'.operations.'+name,source['dependencies'][key+'.operations']['quote'],label,a,page=32)
        else:
            interim_row(key+'.operations.'+name,index,label,b)
    check(key+' R&D equals reconciliation amount', rows[key+'.operations.rd']['values'] == source['tables'][key+'.bridge']['rd'])
    check(key+' consolidated income agrees with reconciliation', rows[key+'.operations.operating_income']['values'] == source['tables'][key+'.bridge']['consolidated'])
    check(key+' other corporate expenses are not all consolidated SG&A', rows[key+'.operations.sga']['values'] != source['tables'][key+'.bridge']['other'])
annual_row('annual.ppe.net',source['dependencies']['annual.assets_note5']['quote'],
           'Total property, plant and equipment, net',[45680,43715],page=42)

# Independent exact full 5-by-5 constructions. Splitting remaining product
# totals proportionally is a witness recipe only, never an admitted default.
full = []
for n, small in enumerate(calc['couplings']):
    z = small['iPhone_by_region_musd'][2]
    region_sales = [source['tables']['annual.sales']['rows'][name][0] for name in names]
    iphone_by_region = [F((201183-z)*region_sales[j],324083) if j != 2 else F(z) for j in range(5)]
    other_by_region = [F(region_sales[j])-iphone_by_region[j] for j in range(5)]
    matrix = [iphone_by_region]
    for product in product_values[1:]:
        matrix.append([F(product[0])*x/F(391035-201183) for x in other_by_region])
    check('witness '+str(n)+' all five product marginals', [sum(row) for row in matrix] == [F(row[0]) for row in product_values])
    check('witness '+str(n)+' all five region marginals', [sum(row[j] for row in matrix) for j in range(5)] == [F(source['tables']['annual.sales']['rows'][name][0]) for name in names])
    check('witness '+str(n)+' nonnegative', all(v >= 0 for row in matrix for v in row))
    full.append(dict(products=products,regions=names,values_musd=[[str(x) for x in row] for row in matrix],
                     qualitative_admission='not checked; source supplies no numerical tolerance for generally consistent or moderately higher'))
check('witnesses are different',full[0]['values_musd'] != full[1]['values_musd'])
result = dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),
              source_supplement_sha256=sha(OUT/'source-claim-supplement.json'),calculations_sha256=sha(OUT/'calculations.json'),
              checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),
              note_numeric_cells=note_cells,dependency_numeric_cells=len(cells)-note_cells,
              source_rows=rows, full_product_region_witnesses=full)
(OUT/'table-checks.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:result[k] for k in ['passed','failed','note_numeric_cells','dependency_numeric_cells']}))
if result['failed']:
    print(json.dumps([c for c in checks if not c['passed']],ensure_ascii=False))
    raise SystemExit(1)
