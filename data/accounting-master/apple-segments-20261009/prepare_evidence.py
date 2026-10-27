"""Pin full Apple segment notes and test geography/allocation consequences."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import time

from bs4 import BeautifulSoup
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
if (OUT / 'evidence-checks.json').exists():
    raise SystemExit('Evidence is frozen')
start_time = time.monotonic()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda s: re.sub(r'\s+', '', s)
checks, inputs, notes, units, dependencies, tables, queries = [], {}, {}, [], {}, {}, []
(OUT / 'sources').mkdir(exist_ok=True)


def check(name, condition, detail=None):
    checks.append(dict(name=name, passed=bool(condition), detail=detail))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def pin(path):
    inputs[str(path.relative_to(ROOT))] = sha(path)
    return path.read_text()


case = json.loads(pin(ROOT / 'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'))
texts = {}
for key in ['annual', 'interim']:
    src = case['sources'][key]
    for pk, hk in [('original_path', 'original_sha256'), ('extraction_path', 'extraction_sha256')]:
        path = ROOT / src[pk]
        check(key + ' ' + pk + ' pinned', sha(path) == src[hk])
        inputs[src[pk]] = sha(path)
    texts[key] = (ROOT / src['extraction_path']).read_text()
pdf = fitz.open(ROOT / case['sources']['annual']['original_path'])
soup = BeautifulSoup((ROOT / case['sources']['interim']['original_path']).read_text(), 'html.parser')
original_html_text = soup.get_text()

partitions = {
    'annual.note.13': [
        ('definition', 'Note 13', 'Five issuer-defined regions, customer/retail attribution and CODM asset exclusion.'),
        ('segment_table', 'The following table shows information by reportable segment', 'All fifteen dated segment sales/income pairs.'),
        ('income_reconciliation', 'A reconciliation of the Company', 'Three dated corporate cost bridges and other-cost footnote.'),
        ('country_sales', 'The following tables show net sales', 'Country sales scope and all dated columns.'),
        ('long_lived_assets', 'Long-lived assets:', 'Dated stock, remaining-countries aggregation and China footnote.'),
    ],
    'interim.note.10': [
        ('segment_table', 'Note 10', 'All ten dated segment sales/income pairs; annual definitions are a declared dependency.'),
        ('income_reconciliation', 'A reconciliation of the Company', 'Two dated R&D and other corporate cost bridges.'),
    ],
}
for ident, specs in partitions.items():
    row = next(r for r in case['note_dispositions'] if r['note_id'] == ident)
    src = row['source']; key = src['document']; q = texts[key][src['start']:src['end']]
    check(ident + ' exact retained span', q == src['quote'])
    notes[ident] = dict(source=key, start=src['start'], end=src['end'], quote=q,
                        original_pdf_pages=[49, 50] if key == 'annual' else None)
    (OUT / 'sources' / (ident + '.txt')).write_text(q)
    positions = [q.index(marker) for _, marker, _ in specs] + [len(q)]
    check(ident + ' exhaustive ordered partition', positions[0] == 0 and positions == sorted(set(positions)))
    for (name, _, meaning), a, b in zip(specs, positions, positions[1:]):
        quote = q[a:b]
        units.append(dict(id=ident + '.' + name, source=key, start=src['start'] + a,
                          end=src['start'] + b, quote=quote, sha256=hashlib.sha256(quote.encode()).hexdigest(),
                          interpretation=meaning))
    if key == 'annual':
        tokens = lambda s: Counter(re.findall(r'\w+|[^\w\s]', s))
        check('annual full note original PDF tokens', tokens(q) <= tokens(''.join(pdf[i - 1].get_text() for i in [49, 50])))
    else:
        check('interim full note original HTML text', norm(q) in norm(original_html_text))


def dep(key, name, first, last, interpretation, after=0, pages=None):
    t = texts[key]; a = t.index(first, after); b = t.index(last, a + len(first))
    q = t[a:b]; ident = key + '.' + name
    dependencies[ident] = dict(source=key, start=a, end=b, quote=q, interpretation=interpretation,
                               original_pdf_pages=pages)
    (OUT / 'sources' / (ident + '.txt')).write_text(q)
    if key == 'interim':
        check(ident + ' original HTML span', norm(q) in norm(original_html_text))
    return q


for key in ['annual', 'interim']:
    note1 = next(r['source'] for r in case['note_dispositions'] if r['note_id'] == key + '.note.1')
    note2 = next(r['source'] for r in case['note_dispositions'] if r['note_id'] == key + '.note.2')
    dep(key, 'note1', 'Note 1', 'Note 2', 'Basis, perimeter, estimates and fiscal periods.', after=note1['start'], pages=[37] if key == 'annual' else None)
    dep(key, 'note2', 'Note 2', 'Note 3', 'Product rows and qualitative regional product-mix qualification.', after=note2['start'], pages=[38, 39] if key == 'annual' else None)
    pre = '' if key == 'annual' else 'CONDENSED '
    dep(key, 'operations', pre + 'CONSOLIDATED STATEMENTS OF OPERATIONS', pre + 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME',
        'Consolidated sales, R&D, SG&A and operating income.', pages=[32] if key == 'annual' else None)
    dep(key, 'segment_mda', 'Segment Operating Performance', 'Products and Services Performance',
        'Full management segment-sales discussion and dated FX/product drivers.', pages=[25, 26] if key == 'annual' else None)
    dep(key, 'reporting_change', 'Segment Reporting', 'Critical Accounting Estimates',
        'Dated issuer adoption plan; not operative standards authority.')
dep('annual', 'manufacture', 'Substantially all of the Company’s hardware products', 'Note 13',
    'Outsourced manufacturing-location statement, not a sales-location mapping.', after=220000, pages=[49])
note5 = next(r['source'] for r in case['note_dispositions'] if r['note_id'] == 'annual.note.5')
dep('annual', 'assets_note5', 'Note 5 – Property, Plant and Equipment', 'Note 6',
    'Net PP&E comparator; numerical equality is not a category-definition proof.', after=note5['start'], pages=[42])
dep('annual', 'fiscal_period', 'Fiscal Period', 'Macroeconomic Conditions',
    '52/53-week MD&A qualifier.', after=100000, pages=[24])
dep('interim', 'seasonality', 'Business Seasonality and Product Introductions', 'Macroeconomic Conditions',
    'Issuer says first-quarter sales have historically been higher; do not annualise.', after=36045)
for key in ['annual', 'interim']:
    old = next(a for a in case['material_assertions'] if a['id'] == ('A21' if key == 'annual' else 'I11'))
    check(key + ' prior assertion quote retained', old['source']['quote'] in notes[key + '.note.' + ('13' if key == 'annual' else '10')]['quote'])
check('prior income bridges remain dependencies', case['calculation_results']['annual_segment_to_consolidated_income_musd'] == 123216 and case['calculation_results']['quarter_segment_to_consolidated_income_musd'] == 42832)

region_names = ['Americas', 'Europe', 'Greater China', 'Japan', 'Rest of Asia Pacific']
annual_sales = [[167045, 162560, 169658], [101328, 94294, 95118], [66952, 72559, 74200],
                [25052, 24257, 25977], [30658, 29615, 29375]]
annual_income = [[67656, 60508, 62683], [41790, 36098, 35233], [27082, 30328, 31153],
                 [12454, 11888, 12257], [13062, 12066, 11569]]
quarter_sales = [[52648, 50430], [33861, 30397], [18513, 20819], [8987, 7767], [10291, 10162]]
quarter_income = [[21509, 20357], [14607, 12711], [8160, 8622], [4314, 3819], [4584, 4579]]
country_sales = [[142196, 138573, 147859], [66952, 72559, 74200], [181887, 172153, 172269]]
long_assets = [[35664, 33276], [4797, 5778], [5219, 4661]]
bridge = {'annual': {'segment': [162044, 150888, 152895], 'rd': [31370, 29915, 26251],
                     'other': [7458, 6672, 7207], 'consolidated': [123216, 114301, 119437]},
          'interim': {'segment': [53174, 50088], 'rd': [8268, 7696],
                      'other': [2074, 2019], 'consolidated': [42832, 40373]}}
targets = [('annual', 'sales', annual_sales), ('annual', 'income', annual_income),
           ('interim', 'sales', quarter_sales), ('interim', 'income', quarter_income)]
for key, measure, matrix in targets:
    note = notes[key + '.note.' + ('13' if key == 'annual' else '10')]['quote']
    for name, row in zip(region_names, matrix):
        check(key + ' ' + name + ' ' + measure + ' all dated values',
              all(re.search(r'(?<!\d)' + f'{v:,}' + r'(?!\d)', note) for v in row))
    tables[key + '.' + measure] = dict(rows=dict(zip(region_names, matrix)),
                                      dates=['2024', '2023', '2022'] if key == 'annual' else ['2024-12-28', '2023-12-30'],
                                      unit='USD million', numeric_status='displayed centres')
    # All row labels and values are checked against the issuer original page/HTML table.
    original = ''.join(pdf[i - 1].get_text() for i in [49, 50]) if key == 'annual' else ' '.join(soup.find_all('table')[26].stripped_strings)
    check(key + ' original ' + measure + ' table all values', all(f'{v:,}' in original for row in matrix for v in row))

for key, sales, income in [('annual', annual_sales, annual_income), ('interim', quarter_sales, quarter_income)]:
    b = bridge[key]; cols = len(b['segment'])
    for j in range(cols):
        check(key + ' segment income sum ' + str(j), sum(r[j] for r in income) == b['segment'][j])
        check(key + ' corporate reconciliation ' + str(j), b['segment'][j] - b['rd'][j] - b['other'][j] == b['consolidated'][j])
    tables[key + '.bridge'] = dict(**b, dates=tables[key + '.sales']['dates'], unit='USD million')
    q = notes[key + '.note.' + ('13' if key == 'annual' else '10')]['quote']
    original = ''.join(pdf[i - 1].get_text() for i in [49, 50]) if key == 'annual' else ' '.join(soup.find_all('table')[27].stripped_strings)
    check(key + ' original reconciliation all values', all(f'{v:,}' in q and f'{v:,}' in original for row in b.values() for v in row))
    check(key + ' sales match source total', [sum(row[j] for row in sales) for j in range(cols)] ==
          ([391035, 383285, 394328] if key == 'annual' else [124300, 119575]))
check('annual corporate-other footnote', 'Includes general and administrative compensation costs, various nonrecurring charges, and other separately managed costs.' in notes['annual.note.13']['quote'])
check('CODM asset exclusion', 'excludes asset information' in notes['annual.note.13']['quote'])
check('generally customer location', 'generally\nbased on the location of customers' in notes['annual.note.13']['quote'])
check('Europe includes India Middle East Africa', 'Europe includes European countries, as well as India, the Middle East and' in notes['annual.note.13']['quote'])
check('China footnote', 'China includes Hong Kong and Taiwan.' in notes['annual.note.13']['quote'])
for key in ['annual', 'interim']:
    check(key + ' product-mix qualitative statement', 'generally consistent for each reportable segment' in dependencies[key + '.note2']['quote'] and 'moderately higher proportion' in dependencies[key + '.note2']['quote'])
    check(key + ' issuer retrospective adoption statement',
          'fourth quarter of 2025 using a retrospective transition method' in
          ' '.join(dependencies[key + '.reporting_change']['quote'].split()))
for name, arr, total in [('country sales', country_sales, [391035,383285,394328]),
                         ('country long-lived assets', long_assets, [45680,43715])]:
    q = notes['annual.note.13']['quote']; orig = pdf[49].get_text()
    check(name + ' all original values', all(f'{v:,}' in q and f'{v:,}' in orig for row in arr for v in row))
    check(name + ' complete dated totals', [sum(row[j] for row in arr) for j in range(len(total))] == total)
tables['annual.country_sales'] = dict(rows=dict(zip(['U.S.', 'China (incl. HK/Taiwan)', 'Other countries'], country_sales)),
                                      totals=[391035,383285,394328], dates=['2024','2023','2022'], unit='USD million')
tables['annual.long_lived_assets'] = dict(rows=dict(zip(['U.S.', 'China (incl. HK/Taiwan)', 'Other countries'], long_assets)),
                                         totals=[45680,43715], dates=['2024-09-28','2023-09-30'], unit='USD million')
check('country China equals Greater China sales in three displayed years', country_sales[1] == annual_sales[2])
check('annual country sales totals match segment sales', tables['annual.country_sales']['totals'] == [sum(row[j] for row in annual_sales) for j in range(3)])
check('long-lived asset total equals Note 5 net PP&E at annual 2024 centre',
      long_assets[0][0] + long_assets[1][0] + long_assets[2][0] == case['calculation_results']['annual_ppe_musd'])

# Two distinct nonnegative 2024 product-by-region couplings, each matching the
# reported 2024 iPhone and region totals and the direction of the qualitative
# Greater China sentence. Neither is certified as the actual qualitative mix.
iphone_total, grand_total, gc_total = 201183, 391035, 66952
couplings = []
for gc_iphone in [36000, 38000]:
    # Set four other regions near their remaining aggregate share, with the
    # final region assigned the residual. Integer centres are illustrative.
    remaining = iphone_total - gc_iphone
    other_indices = [0, 1, 3, 4]
    other_sum = grand_total - gc_total
    cells = [None] * 5
    for idx in other_indices[:-1]:
        cells[idx] = (annual_sales[idx][0] * remaining) // other_sum
    cells[4] = remaining - sum(cells[i] for i in other_indices[:-1])
    cells[2] = gc_iphone
    other = [annual_sales[i][0] - cells[i] for i in range(5)]
    check('coupling ' + str(gc_iphone) + ' nonnegative and exact marginals',
          all(x >= 0 for x in cells + other) and sum(cells) == iphone_total and
          sum(other) == grand_total - iphone_total and
          all(cells[i] + other[i] == annual_sales[i][0] for i in range(5)))
    gc_share = Fraction(gc_iphone, gc_total)
    non_gc_share = Fraction(remaining, other_sum)
    check('coupling ' + str(gc_iphone) + ' GC iPhone directional share', gc_share > non_gc_share)
    couplings.append(dict(iPhone_by_region_musd=cells, other_by_region_musd=other,
                          gc_iPhone_share_exact=str(gc_share), non_gc_iPhone_share_exact=str(non_gc_share),
                          conditional_ten_percent_gc_iPhone_sales_change_musd=gc_iphone // 10))
check('different 10 percent conditional GC iPhone revenue responses',
      [x['conditional_ten_percent_gc_iPhone_sales_change_musd'] for x in couplings] == [3600, 3800])
cost_allocations = [[14000,10000,5000,4000,5828],[13000,10000,6000,4000,5828]]
for index, costs in enumerate(cost_allocations):
    check('corporate cost allocation ' + str(index) + ' nonnegative sum', min(costs) >= 0 and sum(costs) == 31370 + 7458)
    check('corporate cost allocation ' + str(index) + ' consolidated income',
          sum(annual_income[i][0] - costs[i] for i in range(5)) == 123216)
check('alternative GC fully allocated profits',
      [annual_income[2][0] - x[2] for x in cost_allocations] == [22082,21082])
calculations = dict(couplings=couplings, corporate_cost_allocations_musd=cost_allocations,
                    gc_hypothetical_fully_allocated_profit_musd=[22082,21082],
                    gc_2024_share_of_sales=Fraction(66952,391035).__str__(),
                    gc_2024_share_of_long_lived_assets=Fraction(4797,45680).__str__(),
                    conditional_us_within_americas_sales_remainder_2024_musd=167045-142196,
                    status='Illustrative exact displayed-centre constraints, not issuer allocations or probabilities')
for ident, answer, unknown in [
    ('region_definition', 'Five issuer-defined customer-facing regions.', 'Actual customer and legal-entity mapping'),
    ('regional_sales', 'Reported dated regional net sales.', 'Product-region cells and future drivers'),
    ('regional_profit', 'Reported regional operating income before corporate bridge.', 'Attribution of R&D/other costs'),
    ('country_sales', 'Reported three-country-class net sales.', 'Countries inside Other and exact US/region nesting'),
    ('country_assets', 'Reported dated long-lived asset stocks.', 'Segment assets, asset composition and capacity'),
    ('product_region_shock', 'Conditional revenue differs across numeric-marginal couplings.', 'Actual matrix, margin and cash response'),
    ('retrospective_view', 'Issuer described future retrospective adoption.', 'Operative authority and future restated observation')]:
    queries.append(dict(id=ident, supported=answer, unresolved=unknown))
supplement = dict(recorded_at=datetime.now(timezone.utc).isoformat(), sources=case['sources'], notes=notes,
                  material_units=units, dependencies=dependencies, tables=tables, queries=queries,
                  boundaries=['Country labels are not legal entities or factories',
                              'Net sales geography generally follows customers and retail stores',
                              'Long-lived asset country stock is not segment assets or capacity',
                              'Cost and product allocations are illustrative; qualitative mix is not numerically certified',
                              'ASU adoption is the issuer\'s dated plan, not an operative-standard finding'])
save('source-claim-supplement.json', supplement)
save('calculations.json', calculations)
report = dict(recorded_at=datetime.now(timezone.utc).isoformat(), checker_sha256=sha(Path(__file__)),
              inputs=inputs, output_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted((OUT / 'sources').rglob('*')) if p.is_file()},
              checks=checks, passed=sum(c['passed'] for c in checks), failed=sum(not c['passed'] for c in checks),
              wall_seconds=time.monotonic() - start_time)
for name in ['source-claim-supplement.json','calculations.json']:
    report['output_hashes'][str((OUT / name).relative_to(ROOT))] = sha(OUT / name)
save('evidence-checks.json', report)
print(json.dumps(dict(passed=report['passed'], failed=report['failed'], units=len(units), dependencies=len(dependencies), queries=len(queries))))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']], ensure_ascii=False))
    raise SystemExit(1)
