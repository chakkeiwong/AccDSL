"""Full pinned Note 4 population and exact, population-aware consequences."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import time

from bs4 import BeautifulSoup
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()
if (OUT / 'completion.json').exists() or (OUT / 'evidence-checks.json').exists():
    raise SystemExit('Preserve earlier reports before rerunning')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda s: re.sub(r'\s+', '', s)
checks, inputs, notes, units, deps, tables = [], {}, {}, [], {}, {}
(OUT / 'sources').mkdir(exist_ok=True)


def check(name, ok, detail=None):
    checks.append(dict(name=name, passed=bool(ok), detail=detail))


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def pin(path):
    inputs[str(path.relative_to(ROOT))] = sha(path)
    return path.read_text()


prior = json.loads(pin(ROOT / 'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'))
texts = {}
for key in ['annual', 'interim']:
    src = prior['sources'][key]
    for pk, hk in [('original_path', 'original_sha256'), ('extraction_path', 'extraction_sha256')]:
        path = ROOT / src[pk]
        inputs[src[pk]] = sha(path)
        check(key + ' pinned ' + pk, sha(path) == src[hk])
    texts[key] = (ROOT / src['extraction_path']).read_text()
pdf = fitz.open(ROOT / prior['sources']['annual']['original_path'])
soup = BeautifulSoup((ROOT / prior['sources']['interim']['original_path']).read_text(), 'html.parser')

partition = {
    'annual.note.4': [
        ('introduction', 'Note 4', 'Two dated seven-column investment classifications; USD millions.'),
        ('investment_2024', 'Cash, Cash Equivalents', 'All category rows, subtotals and seven distinct columns, 28 September 2024.'),
        ('investment_2023', '\f', 'All 2023 investment rows; valuation method and both restriction footnotes.'),
        ('maturity_classification', 'As of September 28, 2024, 86%', 'Two distinct maturity-band denominators; available-for-sale debt and classification by underlying maturity.'),
        ('hedging', 'Derivative Instruments and Hedging', 'Complete previously checked derivative discussion retained as a dependency, not a new risk model.'),
        ('trade', 'Accounts Receivable', 'Carrier concentration and credit support; no individual identities or default probabilities.'),
        ('vendor', 'Vendor Non-Trade Receivables', 'Component sales are excluded from product revenue; gains reduce product cost of sales when final products sell; dated vendor concentrations.'),
    ],
    'interim.note.4': [
        ('introduction', 'Note 4', 'Two dated investment classifications, USD millions.'),
        ('investment_december', 'Cash, Cash Equivalents', 'All December investment rows and seven columns.'),
        ('investment_september', 'September 28, 2024\nAdjusted', 'Repeated September snapshot, valuation method and escrow restriction footnotes, explicitly current securities.'),
        ('maturity', 'As of December\u00a028, 2024,\n85', 'Distinct December maturity-band denominators; not cash-availability forecasts.'),
        ('hedging', 'Derivative Instruments and Hedging', 'Entire retained prior hedge discussion; no new sensitivity reissue.'),
        ('trade', 'Accounts Receivable', 'Two large customers, carrier percentage and credit support with membership unknown.'),
        ('vendor', 'Vendor Non-Trade Receivables', 'Full component-sale accounting and dated concentrations, no continuity of counterparty names.'),
    ],
}
for ident, specs in partition.items():
    src = next(r['source'] for r in prior['note_dispositions'] if r['note_id'] == ident)
    key = ident.split('.')[0]
    q = texts[key][src['start']:src['end']]
    check(ident + ' full retained span', q == src['quote'])
    notes[ident] = dict(source=key, start=src['start'], end=src['end'], quote=q,
                        original_pdf_pages=[39, 40, 41] if key == 'annual' else None)
    (OUT / 'sources' / (ident + '.txt')).write_text(q)
    positions = [q.index(marker) for _, marker, _ in specs] + [len(q)]
    check(ident + ' exhaustive ordered material partition', positions[0] == 0 and positions == sorted(set(positions)))
    for (name, _, meaning), a, b in zip(specs, positions, positions[1:]):
        units.append(dict(id=ident + '.' + name, source=key, start=src['start'] + a, end=src['start'] + b,
                          quote=q[a:b], sha256=hashlib.sha256(q[a:b].encode()).hexdigest(), interpretation=meaning))
    if key == 'interim':
        check(ident + ' full original HTML', norm(q) in norm(soup.get_text()))
    else:
        original = ''.join(pdf[n - 1].get_text() for n in [39, 40, 41])
        check(ident + ' full PDF text token population', Counter(re.findall(r'\S+', q)) <= Counter(re.findall(r'\S+', original)))


def dep(key, name, first, last, meaning, after=0, pages=None):
    t = texts[key]
    a = t.index(first, after)
    b = t.index(last, a + len(first))
    q = t[a:b]
    ident = key + '.' + name
    deps[ident] = dict(id=ident, source=key, start=a, end=b, quote=q,
                      sha256=hashlib.sha256(q.encode()).hexdigest(), interpretation=meaning, original_pdf_pages=pages)
    (OUT / 'sources' / (ident + '.txt')).write_text(q)
    if key == 'interim':
        check(ident + ' original HTML span', norm(q) in norm(soup.get_text()))
    return q


for key, pre in [('annual', ''), ('interim', 'CONDENSED ')]:
    n1 = next(r['source'] for r in prior['note_dispositions'] if r['note_id'] == key + '.note.1')
    dep(key, 'basis_calendar', 'Note 1', 'Note 2', 'Full Note 1 retained: reporting basis, interim completeness and fiscal calendar; formalise only relevant policies.', after=n1['start'], pages=[37] if key == 'annual' else None)
    dep(key, 'balance', pre + 'CONSOLIDATED BALANCE SHEETS', pre + 'CONSOLIDATED STATEMENTS OF SHAREHOLDERS',
        'Full balance sheet; selected cash, current/noncurrent securities, net trade and vendor receivables.', pages=[34] if key == 'annual' else None)
    dep(key, 'cash', pre + 'CONSOLIDATED STATEMENTS OF CASH FLOWS', 'Notes to ' + ('Condensed ' if key == 'interim' else '') + 'Consolidated Financial Statements',
        'Full cash-flow statement; cash population, security turnover and receivable adjustments.', pages=[36] if key == 'annual' else None)
    dep(key, 'comprehensive', pre + 'CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME', pre + 'CONSOLIDATED BALANCE SHEETS',
        'Full statement retained; marketable-debt movements are net of tax, distinct from broad investment endpoint unrealised amounts.', pages=[33] if key == 'annual' else None)
dep('annual', 'liquidity', 'Liquidity and Capital Resources', 'Critical Accounting Estimates',
    'Unrestricted total, prospective sufficiency belief, contractual requirements and State Aid escrow.', pages=[28, 29])
dep('interim', 'liquidity', 'Liquidity and Capital Resources', 'Recent Accounting Pronouncements',
    'Prospective sufficiency belief, changed requirements and State Aid payments; no unrestricted numerical total stated.')
dep('annual', 'market_risk', 'Item 7A.', 'Item 8.', 'Entire dated risk discussion; use investment portfolio fair-value sensitivity only as issuer scenario.', after=100000, pages=[30])
dep('interim', 'market_risk', 'Item 3.\u00a0\u00a0\u00a0\u00a0Quantitative', 'Item 4.', 'No material change and annual referral, not an updated numeric scenario.')
tax = next(r['source'] for r in prior['note_dispositions'] if r['note_id'] == 'annual.note.7')
dep('annual', 'tax_cross_reference', 'Note 7', 'Note 8', 'Full restriction cross-reference retained; tax-unit calculations and settlement interpretations remain dependencies.', after=tax['start'], pages=[42, 43, 44])
for directory in ['apple-debt-20261009', 'apple-tax-20261009']:
    base = ROOT / 'data/accounting-master' / directory
    old = json.loads(pin(base / 'source-claim-supplement.json'))
    pin(base / 'calculations.json')
    pin(base / 'completion.json')
    pin(base / 'run-manifest.json')
    if 'debt' in directory:
        for key in ['annual', 'interim']:
            current = next(u['quote'] for u in units if u['id'] == key + '.note.4.hedging')
            check(key + ' previous hedge span preserved exactly', current == old['dependencies'][key + '.hedging']['quote'])


def numbers(s):
    s = s.replace('$', '').replace('(', '-').replace(')', '')
    s = re.sub(r'-\s+', '-', s)
    return [x.replace(',', '') if x != '\u2014' else '0' for x in re.findall(r'-?\d[\d,]*(?:\.\d+)?|\u2014', s)]


def annual_rows(ident, q, page):
    rows = []
    for line in q.splitlines():
        parts = re.split(r'\s{2,}', line.strip(), maxsplit=1)
        if len(parts) == 2 and len(numbers(parts[1])) == 7:
            label = re.sub(r'\s*\(\d\)', '', parts[0]).strip()
            values = list(map(int, numbers(parts[1])))
            check(ident + ' original row ' + label + str(len(rows)), norm(line) in norm(pdf[page - 1].get_text()))
            rows.append(dict(label=label, values=values, literal=line))
    check(ident + ' complete 14 rows/seven columns', len(rows) == 14)
    tables[ident] = dict(rows=rows, date='2024-09-28' if page == 39 else '2023-09-30', original_pdf_page=page,
                        columns=['adjusted_cost', 'unrealised_gains', 'unrealised_losses_signed', 'fair_value', 'cash_equivalents', 'current_securities', 'noncurrent_securities'], unit='USD million', displayed_quantum='1 million')
    return rows


def html_rows(ident, index, date):
    table = soup.find_all('table')[index]
    rows = []
    for tr in table.find_all('tr'):
        cells = [c.get_text(' ', strip=True) for c in tr.find_all(['td', 'th'], recursive=False)]
        nonempty = [c for c in cells if c]
        if nonempty and len(numbers(' '.join(nonempty[1:]))) == 7 and not nonempty[0].startswith('Level'):
            rows.append(dict(label=re.sub(r'\s*\(\d\)', '', nonempty[0]).strip(), values=list(map(int, numbers(' '.join(nonempty[1:])))), original_cells=cells))
    check(ident + ' complete original 14 rows/seven columns', len(rows) == 14)
    tables[ident] = dict(rows=rows, date=date, html_table_index=index, columns=tables['annual.investment_2024']['columns'], unit='USD million', displayed_quantum='1 million')
    (OUT / 'sources' / ('interim.table.' + str(index) + '.html')).write_text(str(table))
    return rows


q = notes['annual.note.4']['quote']
annual_rows('annual.investment_2024', q[:q.index('\f')], 39)
annual_rows('annual.investment_2023', q[q.index('\f'):q.index('    (1)')], 40)
html_rows('interim.investment_december', 19, '2024-12-28')
html_rows('interim.investment_september', 20, '2024-09-28')
for ident, table in list(tables.items()):
    rows = table['rows']
    for row in rows:
        cost, gains, losses, fair, cash, current, noncurrent = row['values']
        check(ident + ' fair-value identity ' + row['label'], cost + gains + losses == fair)
        check(ident + ' presentation partition ' + row['label'], cash + current + noncurrent == fair)
        check(ident + ' sign domains ' + row['label'], cost >= 0 and gains >= 0 and losses <= 0 and min(fair, cash, current, noncurrent) >= 0)
    for name, indices, total in [('level1', [1, 2], 3), ('level2', list(range(4, 12)), 12), ('total', [0, 3, 12], 13)]:
        check(ident + ' seven-column subtotal ' + name, [sum(rows[i]['values'][c] for i in indices) for c in range(7)] == rows[total]['values'])
check('September complete repeated snapshot matches', [(r['label'], r['values']) for r in tables['annual.investment_2024']['rows']] == [(r['label'], r['values']) for r in tables['interim.investment_september']['rows']])
check('three totals match pinned original displayed values', [tables[i]['rows'][-1]['values'] for i in ['annual.investment_2023', 'annual.investment_2024', 'interim.investment_december']] == [[173752, 30, -11683, 162099, 29965, 31590, 100544], [160600, 688, -4638, 156650, 29943, 35228, 91479], [147088, 261, -5981, 141368, 30299, 23476, 87593]])


def statement_row(ident, label, expected, key, page=None, index=None, occurrence=0):
    q = deps[key]['quote']
    if page:
        rows = [l.strip() for l in q.splitlines() if re.split(r'\s{2,}', l.strip(), maxsplit=1)[0] == label]
        literal = rows[occurrence]
        values = list(map(int, numbers(re.split(r'\s{2,}', literal, maxsplit=1)[1])))
        check(ident + ' original PDF row', norm(literal) in norm(pdf[page - 1].get_text()))
        row = dict(label=label, literal=literal, values=values, original_pdf_page=page)
    else:
        found = []
        for tr in soup.find_all('table')[index].find_all('tr'):
            cells = [c.get_text(' ', strip=True) for c in tr.find_all(['td', 'th'], recursive=False)]
            nonempty = [c for c in cells if c]
            if nonempty and nonempty[0] == label:
                found.append((cells, list(map(int, numbers(' '.join(nonempty[1:]))))))
        cells, values = found[occurrence]
        row = dict(label=label, values=values, original_cells=cells, html_table_index=index)
    check(ident + ' pinned dated columns', values == expected, values)
    tables[ident] = dict(**row, dependency=key, unit='USD million', displayed_quantum='1 million')
    return values


balance = {}
for key, dates, values in [('annual', ['2024-09-28', '2023-09-30'], [[29943,29965],[35228,31590],[91479,100544],[33410,29508],[32833,31477]]),
                           ('interim', ['2024-12-28', '2024-09-28'], [[30299,29943],[23476,35228],[87593,91479],[29639,33410],[29667,32833]])]:
    balance[key] = dict(dates=dates)
    for name, label, expect, occ in [('cash','Cash and cash equivalents',values[0],0), ('current','Marketable securities',values[1],0), ('noncurrent','Marketable securities',values[2],1), ('trade_net','Accounts receivable, net',values[3],0), ('vendor','Vendor non-trade receivables',values[4],0)]:
        balance[key][name] = statement_row(key+'.balance.'+name,label,expect,key+'.balance',page=34 if key=='annual' else None,index=14 if key=='interim' else None,occurrence=occ)
    for col, ident in enumerate(['annual.investment_2024','annual.investment_2023'] if key=='annual' else ['interim.investment_december','interim.investment_september']):
        check(key+' investment/balance partition '+dates[col],tables[ident]['rows'][-1]['values'][4:]==[balance[key][n][col] for n in ['cash','current','noncurrent']])
cash = {}
cash_specs = [('opening','Cash, cash equivalents, and restricted cash and cash equivalents, beginning balances',[30737,24977,35929],[29943,30737]),
              ('purchases','Purchases of marketable securities',[-48656,-29513,-76923],[-6124,-9780]),
              ('maturities','Proceeds from maturities of marketable securities',[51211,39686,29917],[15967,13046]),
              ('sales','Proceeds from sales of marketable securities',[11135,5828,37446],[3492,1337]),
              ('trade','Accounts receivable, net',[-3788,-1688,-1823],[3597,6555]),
              ('vendor','Vendor non-trade receivables',[-1356,1271,-7520],[3166,4569]),
              ('operating','Cash generated by operating activities',[118254,110543,122151],[29935,39895]),
              ('investing','Cash generated by/(used in) investing activities',[2935,3705,-22354],[9792,1927]),
              ('financing','Cash used in financing activities',[-121983,-108488,-110749],[-39371,-30585]),
              ('change','Increase/(Decrease) in cash, cash equivalents, and restricted cash and cash equivalents',[-794,5760,-10952],[356,11237]),
              ('closing','Cash, cash equivalents, and restricted cash and cash equivalents, ending balances',[29943,30737,24977],[30299,41974])]
for key in ['annual','interim']:
    cash[key] = {}
    for name,label,a,b in cash_specs:
        if key=='interim':
            if name=='investing': label='Cash generated by investing activities'
            if name=='change': label='Increase in cash, cash equivalents, and restricted cash and cash equivalents'
        cash[key][name]=statement_row(key+'.cash.'+name,label,a if key=='annual' else b,key+'.cash',page=36 if key=='annual' else None,index=16 if key=='interim' else None)
    for j in range(3 if key=='annual' else 2):
        check(key+' cash activity bridge '+str(j),sum(cash[key][n][j] for n in ['operating','investing','financing'])==cash[key]['change'][j])
        check(key+' cash endpoint bridge '+str(j),cash[key]['opening'][j]+cash[key]['change'][j]==cash[key]['closing'][j])
oci = {}
for key in ['annual','interim']:
    oci[key]={}
    for name,label,a,b in [('fair','Change in fair value of marketable debt securities',[5850,1563,-12104],[-1647,3045]),
                           ('realised','Adjustment for net (gains)/losses realized and included in net income',[204,253,205],[220,75]),
                           ('total','Total change in unrealized gains/losses on marketable debt securities',[6054,1816,-11899],[-1427,3120])]:
        oci[key][name]=statement_row(key+'.oci.'+name,label,a if key=='annual' else b,key+'.comprehensive',page=33 if key=='annual' else None,index=13 if key=='interim' else None,occurrence=1 if name=='realised' else 0)
    check(key+' debt-security OCI rows add',all(a+b==c for a,b,c in zip(oci[key]['fair'],oci[key]['realised'],oci[key]['total'])))

anchors = [
    ('cash-equivalent purchase maturity', 'annual.basis_calendar', 'All highly liquid investments with maturities of three months or less at the date of purchase are treated as cash equivalents.'),
    ('specific identification', 'annual.basis_calendar', 'The cost of securities sold is determined using the specific identification method.'),
    ('annual unrestricted rounded total', 'annual.liquidity', 'which totaled $140.8 billion as of September 28, 2024'),
    ('interim liquidity belief', 'interim.liquidity', 'The Company believes its balances of unrestricted cash, cash equivalents and marketable securities'),
    ('tax settlement', 'interim.liquidity', 'During the first quarter of 2025, the Company paid \u20ac11.0\u00a0billion or $11.9 billion to Ireland'),
]
claims=[]
for name,ident,literal in anchors:
    q=deps[ident]['quote'];check(name+' exact source anchor',literal in q)
    claims.append(dict(id=name,source=ident,literal=literal,status='issuer disclosure',unknown='No guarantee, causal journal or newly verified publication date inferred'))
for key, bands in [('annual', [[86,10,4],[14,9,77]]),('interim',[[85,11,4],[13,10,77]])]:
    q=next(u['quote'] for u in units if u['id']==key+'.note.4.'+('maturity_classification' if key=='annual' else 'maturity'))
    found=[int(n) for n in re.findall(r'(\d+)\s*%',q)]
    check(key+' two distinct maturity denominators',found==sum(bands,[]))
    check(key+' maturity bands sum per denominator',all(sum(v)==100 for v in bands))
    tables[key+'.maturity']=dict(values=bands,unit='percent',displayed_quantum='1 percentage point',denominators=['noncurrent marketable debt excluding mortgage/asset-backed','noncurrent mortgage/asset-backed'])
for key, values in [('annual',[38,41,44,23,48,23]),('interim',[18,11,33,38,43,24,44,23])]:
    q=''.join(u['quote'] for u in units if u['id'] in [key+'.note.4.trade',key+'.note.4.vendor'])
    percentages=[int(n) for n in re.findall(r'(\d+)\s*%',q) if int(n)!=10]
    check(key+' all concentration percentages and order',percentages==values,percentages)
    tables[key+'.concentration']=dict(values=values,unit='percent',displayed_quantum='1 percentage point',denominator='trade or vendor non-trade as specified, not their sum',unknown='Names, overlap, gross/net trade basis and persistence of ranks')
risk=deps['annual.market_risk']['quote']
line=next(l.strip() for l in risk.splitlines() if l.strip().startswith('Investment portfolio'))
check('portfolio scenario exact original row',norm(line) in norm(pdf[29].get_text()))
check('portfolio scenario pinned values',numbers(line)==['100','2755','3089'])
tables['annual.portfolio_sensitivity']=dict(literal=line,values=[2755,3089],shock='100 basis points, all tenors',unit='USD million decline in fair value',includes='associated derivatives',dates=['2024-09-28','2023-09-30'])

calc={'investment_totals':{},'security_stock_cash':{},'cash_population':{},'resources':{},'concentration':{},'receivable_stock_cash':{}}
for ident in ['annual.investment_2023','annual.investment_2024','interim.investment_december']:
    t=tables[ident]['rows'][-1]['values'];calc['investment_totals'][tables[ident]['date']]=dict(adjusted_cost=t[0],net_unrealised=t[1]+t[2],fair_value=t[3],cash=t[4],marketable=t[5]+t[6])
for key,a,b in [('annual','2023-09-30','2024-09-28'),('interim','2024-09-28','2024-12-28')]:
    old,new=calc['investment_totals'][a],calc['investment_totals'][b]
    cash_release=sum(cash[key][n][0] for n in ['purchases','maturities','sales'])
    stock_change=new['marketable']-old['marketable']
    residual=stock_change+cash_release
    change={n:new[n]-old[n] for n in ['adjusted_cost','net_unrealised','fair_value']}
    check(key+' cost/unrealised fair-value change identity',change['adjusted_cost']+change['net_unrealised']==change['fair_value'])
    check(key+' marketable/cash total change identity',stock_change+new['cash']-old['cash']==change['fair_value'])
    check(key+' stock/cash residual independently expected',residual==(8263 if key=='annual' else -2303))
    check(key+' endpoint unrealised differs from period debt OCI',change['net_unrealised']!=oci[key]['total'][0])
    calc['security_stock_cash'][key]=dict(opening=old['marketable'],closing=new['marketable'],stock_change=stock_change,net_cash_release=cash_release,unallocated_residual=residual,total_change=change,debt_oci_net_of_tax=oci[key]['total'][0],nonclaim='Residual is not an identified fair-value/FX/reclassification journal; cash proceeds are not book disposals')
    calc['cash_population'][key]=dict(balance_change=new['cash']-old['cash'],cash_flow_change=cash[key]['change'][0],opening_population_difference=cash[key]['opening'][0]-old['cash'],closing_population_difference=cash[key]['closing'][0]-new['cash'])
    for n in ['trade','vendor']:
        stock=balance[key]['trade_net' if n=='trade' else 'vendor']
        remainder=stock[0]-stock[1]+cash[key][n][0]
        calc['receivable_stock_cash'][key+'.'+n]=dict(stock_change=stock[0]-stock[1],indirect_cash_adjustment=cash[key][n][0],unallocated_remainder=remainder,nonclaim='An indirect adjustment is not total collections; matching changes do not identify receipts')
check('cash population difference correctly isolated',calc['cash_population']['annual']==dict(balance_change=-22,cash_flow_change=-794,opening_population_difference=772,closing_population_difference=0))
check('interim cash population endpoint agreement',calc['cash_population']['interim']==dict(balance_change=356,cash_flow_change=356,opening_population_difference=0,closing_population_difference=0))
check('trade/vendor residuals remain unallocated',[r['unallocated_remainder'] for r in calc['receivable_stock_cash'].values()]==[114,0,-174,0])


def interval(center, quantum):
    return [F(center)-F(quantum,2),F(center)+F(quantum,2)]


annual_total=interval(156650,1);r_cash=interval(2600,100);r_sec=interval(13200,100);mdna=interval(140800,100)
annual_free=[annual_total[0]-r_cash[1]-r_sec[1],annual_total[1]-r_cash[0]-r_sec[0]]
intersection=[max(annual_free[0],mdna[0]),min(annual_free[1],mdna[1])]
check('rounded unrestricted narrative compatible',intersection[0]<intersection[1])
q_total=interval(141368,1);q_cash=interval(126,1);q_sec=interval(3300,100)
q_free=[q_total[0]-q_cash[1]-q_sec[1],q_total[1]-q_cash[0]-q_sec[0]]
calc['resources']=dict(annual=dict(reported_total=156650,restricted_cash_center=2600,restricted_securities_center=13200,unrestricted_subtraction_center=140850,conditional_unrestricted_interval=list(map(str,annual_free)),issuer_unrestricted_center=140800,conditional_overlap=list(map(str,intersection))),interim=dict(reported_total=141368,restricted_cash_center=126,restricted_current_securities_center=3300,unrestricted_subtraction_center=137942,conditional_unrestricted_interval=list(map(str,q_free)),current_cash_securities_center=53775,current_general_use_subtraction_center=50349),rounding='Nearest displayed quantum assumed only for compatibility illustration; not an issuer-stated rounding method or confidence interval',nonclaim='Excluding disclosed escrow does not establish frictionless liquidation, timing of receipts, solvency or exact unrestricted cash')
check('resource centre arithmetic',156650-2600-13200==140850 and 141368-126-3300==137942 and 30299+23476-126-3300==50349)
sizes=[18,11,9,9,8,7,4,9,9,8,8]
alternatives=[]
for name,carrier_indices in [('large_customers_are_carriers',[0,1,6]),('large_customers_are_not_carriers',[2,3,4,5])]:
    major={0,1};carriers=set(carrier_indices)
    result=dict(name=name,customer_shares=sizes,carrier_indices=carrier_indices,carrier_share=sum(sizes[i] for i in carriers),major_share=sum(sizes[i] for i in major),overlap=sum(sizes[i] for i in major&carriers),union=sum(sizes[i] for i in major|carriers))
    check(name+' exact share population and whole-customer membership',sum(sizes)==100 and sum(s>=10 for s in sizes)==2 and result['carrier_share']==33 and result['major_share']==29)
    check(name+' union identity',result['union']==29+33-result['overlap'])
    alternatives.append(result)
calc['concentration']=dict(alternatives=alternatives,discrete_centred_possible_unions=[33,44,51,62],annual_vendor_top_two=67,interim_vendor_top_two=67,nonclaim='Centred percentage examples only; not actual customers, continuous overlap identification, monetary loss or probability')
check('discrete group overlap outcomes',sorted({29+33-o for o in [0,11,18,29]})==calc['concentration']['discrete_centred_possible_unions'])
check('two vendor shares keep separate dated denominator',44+23==43+24==67)

queries=[
    dict(id='Q01',question='What resources are reported?',answer='Three dated seven-column totals and balance partitions.',facts='Exact lots and ownership remain unknown.'),
    dict(id='Q02',question='What is available for general use?',answer='Rounded reported/subtracted unrestricted amounts; escrow excluded.',facts='Transfer/liquidation/currency/settlement constraints and exact restricted balances.'),
    dict(id='Q03',question='Does current mean unrestricted?',answer='No; interim footnote identifies restricted current securities at both dates.',facts='Current/noncurrent status cannot establish free use.'),
    dict(id='Q04',question='Is a stock fall security cash released?',answer='No; annual/quarter stock-cash residuals 8263/-2303 remain unallocated.',facts='Specific lots, book disposals, accrual, currency, reclassification and measurement movements.'),
    dict(id='Q05',question='Is endpoint unrealised change debt-security OCI?',answer='Different population/tax/timing: 7703/-1770 versus 6054/-1427.',facts='Security-level tax, income, sale and measurement entries.'),
    dict(id='Q06',question='Do cash statements share populations?',answer='2023 balance/cash-flow endpoints differ by 772; 2024/December agree.',facts='Location/cause of earlier population difference not identified here.'),
    dict(id='Q07',question='Do maturity bands imply readily available funds?',answer='Two distinct denominators; current by underlying maturity and equivalents by purchase maturity.',facts='Balances per maturity band, liquidity/price conditions and instrument cash schedules.'),
    dict(id='Q08',question='What does portfolio sensitivity measure?',answer='Dated issuer +100bp/all-tenors fair-value decline including derivatives.',facts='No replicated model, new quarter scenario, actual cash payout or return distribution.'),
    dict(id='Q09',question='Can customer/carrier shares be added?',answer='Whole-customer membership unknown; examples reproduce marginals with union 33 or 62.',facts='Actual identities, membership, gross/net denominator, collateral and loss/default inputs.'),
    dict(id='Q10',question='Are vendor receivables product revenue?',answer='No; component sales excluded, gain reduces product cost when final products sell.',facts='Component cohorts, gains, delivery and settlement.'),
    dict(id='Q11',question='Do receivable decreases identify receipts?',answer='No; indirect adjustments are not total collections; net-trade residuals 114/-174 unallocated.',facts='Sales, collections, gross/net/allowance/currency/noncash entries and same-counterparty facts.'),
]
save('calculations.json',calc)
coverage=dict(full_notes=2,material_units=len(units),dependencies=len(deps),investment_numeric_cells=4*14*7,unique_dated_investment_cells=3*14*7,statement_numeric_cells=sum(len(t['values']) for t in tables.values() if 'dependency' in t),queries=len(queries),meaning='Declared source reading only; no whole-filing semantic or forecast completion')
save('source-claim-supplement.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),sources=prior['sources'],notes=notes,material_units=units,dependencies=deps,tables=tables,claims=claims,queries=queries,coverage=coverage,prior_checked_dependencies=['apple-debt-20261009','apple-tax-20261009'],source_limits='Publication/byte vintage, operative ASC, actual journals and complete package remain unresolved'))
owned=[OUT/'calculations.json',OUT/'source-claim-supplement.json',*sorted((OUT/'sources').iterdir())]
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,checks=checks,passed=sum(r['passed'] for r in checks),failed=sum(not r['passed'] for r in checks),output_hashes={str(p.relative_to(ROOT)):sha(p) for p in owned},wall_seconds=time.monotonic()-START)
save('evidence-checks.json',report)
print(json.dumps(dict(passed=report['passed'],failed=report['failed'],coverage=coverage)))
if report['failed']:
    print(json.dumps([r for r in checks if not r['passed']],ensure_ascii=False))
    raise SystemExit(1)
