"""Pinned debt disclosures, exact displayed-centre bridges and a scoped example."""
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
if (OUT / 'completion.json').exists():
    raise SystemExit('Closed unit; preserve its evidence')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda s: re.sub(r'\s+', '', s)
checks, inputs = [], {}


def check(name, passed, detail=None):
    checks.append(dict(name=name, passed=bool(passed), detail=detail))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


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
notes, units, deps, tables, claims = {}, [], {}, {}, []
(OUT / 'sources').mkdir(exist_ok=True)

partition = {
    'annual.note.9': [
        ('commercial_terms', 'Note 9 –', 'Unsecured short-term paper, general corporate uses, rounded dated balances, generally short maturities and dated weighted rates.'),
        ('commercial_cash', 'The following table provides a', 'All three years and both maturity classes; short-maturity net flows do not identify gross issuance.'),
        ('term_measurement', 'Term Debt', 'Senior unsecured notes; interest in arrears; calendar maturity range, effective-rate ranges, and two years of measurement components.'),
        ('linked_swaps', 'To manage interest rate risk', 'Certain fixed USD notes swapped to floating; certain foreign-currency notes effectively converted to USD. Actual swaps remain unknown.'),
        ('effective_rates', 'The effective interest rates', 'Reported effective rates include interest, premium/discount amortisation and applicable hedge adjustments; not a coupon schedule.'),
        ('principal_maturities', 'The future principal payments', 'All six future principal buckets and their total; fiscal-year default from Note 1.'),
        ('fair_value', 'As of September 28, 2024 and September 30, 2023, the fair value', 'Dated rounded fair value based on Level 2 inputs; distinct from face and carrying amount.'),
    ],
    'interim.note.6': [
        ('commercial_terms', 'Note 6 –', 'Short-term unsecured paper, general corporate purposes and two rounded dated balances.'),
        ('term_measurement', 'Term Debt', 'Fixed-rate notes with varying maturities; rounded carrying and Level 2 fair values at both dates.'),
    ],
}
for ident, specs in partition.items():
    source = next(r['source'] for r in prior['note_dispositions'] if r['note_id'] == ident)
    key = ident.split('.')[0]
    q = texts[key][source['start']:source['end']]
    check(ident + ' retained complete span', q == source['quote'])
    notes[ident] = dict(source=key, start=source['start'], end=source['end'], quote=q)
    (OUT / 'sources' / (ident + '.txt')).write_text(q)
    positions = [q.index(marker) for _, marker, _ in specs] + [len(q)]
    check(ident + ' exhaustive ordered partition', positions[0] == 0 and positions == sorted(set(positions)))
    for (name, _, meaning), a, b in zip(specs, positions, positions[1:]):
        units.append(dict(id=ident+'.'+name, source=key, start=source['start']+a,
                          end=source['start']+b, quote=q[a:b],
                          sha256=hashlib.sha256(q[a:b].encode()).hexdigest(), interpretation=meaning))
    if key == 'annual':
        original = ''.join(pdf[n-1].get_text() for n in [46, 47])
        # Both extractors preserve the table, but order its two-tier header differently.
        def strip_header(t):
            m = re.search(r'(Company’s term debt as of .*?:)(.*?)(2013 – 2023 debt issuances:)', t, re.S)
            assert m, 'Missing term-debt header boundary'
            return t[:m.start(2)] + t[m.end(2):], m[2]
        a, ah = strip_header(q)
        b, bh = strip_header(original)
        check(ident + ' exact header token permutation', Counter(re.findall(r'\w+', ah)) == Counter(re.findall(r'\w+', bh)))
        check(ident + ' full original PDF outside that header', norm(a) in norm(b))
    else:
        check(ident + ' full original HTML', norm(q) in norm(soup.get_text()))


def dep(key, name, first, last, meaning, after=0, pages=None):
    t = texts[key]
    a = t.index(first, after)
    b = t.index(last, a+len(first))
    q = t[a:b]
    ident = key+'.'+name
    deps[ident] = dict(id=ident, source=key, start=a, end=b, quote=q,
                      sha256=hashlib.sha256(q.encode()).hexdigest(), interpretation=meaning,
                      original_pdf_pages=pages)
    (OUT/'sources'/(ident+'.txt')).write_text(q)
    if key == 'interim':
        check(ident+' retained original HTML text', norm(q) in norm(soup.get_text()))
    return q


support = {}
for key, pre in [('annual', ''), ('interim', 'CONDENSED ')]:
    support[key+'.hedging'] = dep(key, 'hedging', 'Derivative Instruments and Hedging', 'Accounts Receivable',
        'Full derivative discussion; scopes, horizons, cash presentation, designated/undesignated notionals and hedged-item carrying amounts.', pages=[40, 41] if key=='annual' else None)
    support[key+'.balance'] = dep(key, 'balance', pre+'CONSOLIDATED BALANCE SHEETS', pre+'CONSOLIDATED STATEMENTS OF SHAREHOLDERS',
        'Whole statement retained for context; formalised rows are commercial paper and current/noncurrent term debt.', pages=[34] if key=='annual' else None)
    support[key+'.cash'] = dep(key, 'cash', pre+'CONSOLIDATED STATEMENTS OF CASH FLOWS',
        'Notes to '+('Condensed ' if key=='interim' else '')+'Consolidated Financial Statements',
        'Whole cash statement retained; formalised rows are net term proceeds, term repayments and net commercial-paper cash.', pages=[36] if key=='annual' else None)
    n1 = next(r['source'] for r in prior['note_dispositions'] if r['note_id']==key+'.note.1')
    support[key+'.calendar'] = dep(key, 'calendar', 'The Company’s fiscal year is the 52-',
        '\n\nRevenue' if key=='annual' else '\nNote 2',
        'Note 1 fiscal-year convention, 52/53-week boundaries and explicit exception for calendar-labelled fields.',
        after=n1['start'], pages=[37] if key=='annual' else None)
support['annual.derivative_presentation'] = dep('annual', 'derivative_presentation', 'Derivative Instruments\n', '\n\nIncome Taxes',
    'Derivative assets and liabilities presented at gross fair value; not netted into note principal.', after=160208, pages=[37])
support['annual.liquidity'] = dep('annual', 'liquidity', 'Liquidity and Capital Resources', '\n\nLeases',
    'Issuer liquidity belief and debt contractual cash requirements, including interest and twelve-month amounts.', pages=[28])
support['interim.liquidity'] = dep('interim', 'liquidity', 'Liquidity and Capital Resources', '\nManufacturing Purchase Obligations',
    'Issuer liquidity belief, named cash-requirement changes and commercial paper payable within twelve months.')
support['annual.market_risk'] = dep('annual', 'market_risk', 'Item 7A.', 'Item 8.',
    'Entire Item 7A: dated rate scenarios and issuer derivative-only Monte Carlo VaR, with underlying exposures excluded.', after=100000, pages=[30])
support['interim.market_risk'] = dep('interim', 'market_risk', 'Item 3.\u00a0\u00a0\u00a0\u00a0Quantitative', 'Item 4.',
    'No material market-risk change and annual referral; not an updated numerical sensitivity.')
for ident in ['annual.hedging', 'annual.calendar', 'annual.derivative_presentation', 'annual.liquidity']:
    check(ident+' full original PDF text', norm(support[ident]) in norm(''.join(pdf[p-1].get_text() for p in deps[ident]['original_pdf_pages'])))


def numbers(s):
    s = s.replace('$', '').replace('(', '-').replace(')', '')
    s = re.sub(r'-\s+', '-', s)
    return [x.replace(',', '') if x != '—' else '0' for x in re.findall(r'-?\d[\d,]*(?:\.\d+)?|—', s)]


def annual_row(key, q, label, expected, page, occurrence=0, meaning=''):
    candidates = [line.strip() for line in q.splitlines() if re.split(r'\s{2,}', line.strip(), maxsplit=1)[0] == label]
    assert len(candidates) > occurrence, (key, label)
    line = candidates[occurrence]
    value = numbers(re.split(r'\s{2,}', line, maxsplit=1)[1])
    check(key+' parsed columns', value == list(map(str, expected)), value)
    check(key+' original PDF row', norm(line) in norm(pdf[page-1].get_text()))
    tables[key] = dict(label=label, values=value, literal=line, original_pdf_page=page,
                       unit='USD million', displayed_quantum='1 million', interpretation=meaning)
    return [F(v) for v in value]


def html_row(key, index, label, expected, occurrence=0, meaning=''):
    table = soup.find_all('table')[index]
    candidates = []
    for tr in table.find_all('tr'):
        cells = [c.get_text(' ', strip=True) for c in tr.find_all(['td','th'], recursive=False)]
        nonempty = [c for c in cells if c]
        if nonempty and nonempty[0] == label:
            candidates.append((cells, numbers(' '.join(nonempty[1:]))))
    assert len(candidates) > occurrence, (key, label)
    cells, value = candidates[occurrence]
    check(key+' original HTML columns', value == list(map(str, expected)), value)
    tables[key] = dict(label=label, values=value, original_cells=cells, html_table_index=index,
                       unit='USD million', displayed_quantum='1 million', interpretation=meaning)
    (OUT/'sources'/('interim.table.'+str(index)+'.html')).write_text(str(table))
    return [F(v) for v in value]


q = notes['annual.note.9']['quote']
cp = {}
for name, label, values, occ in [
    ('short_net', 'Proceeds from/(Repayments of) commercial paper, net', [3960, -1333, 5264], 0),
    ('long_proceeds', 'Proceeds from commercial paper', [0, 0, 5948], 0),
    ('long_repayments', 'Repayments of commercial paper', [0, -2645, -7257], 0),
    ('long_net', 'Proceeds from/(Repayments of) commercial paper, net', [0, -2645, -1309], 1),
    ('total_net', 'Total proceeds from/(repayments of) commercial paper, net', [3960, -3978, 3955], 0),
]:
    cp[name] = annual_row('annual.cp.'+name, q, label, values, 46, occ,
        'FY2024, FY2023, FY2022; short means source maturities at most 90 days, long means greater than 90 days.')
term = {}
for name, label, values in [
    ('principal', 'Total term debt principal', [97341, 106572]),
    ('net_costs', 'Unamortized premium/(discount) and issuance costs, net', [-321, -356]),
    ('hedge_basis', 'Hedge accounting fair value adjustments', [-358, -1113]),
    ('carrying', 'Total term debt', [96662, 105103]),
    ('less_current', 'Less: Current portion of term debt', [-10912, -9822]),
    ('noncurrent', 'Total non-current portion of term debt', [85750, 95281]),
]:
    term[name] = annual_row('annual.term.'+name, q, label, values, 46,
                           meaning='28 September 2024, 30 September 2023. Preserve source subtraction sign for current portion.')
maturities = []
for label, value in [('2025',10930),('2026',12342),('2027',9936),('2028',7800),('2029',5153),('Thereafter',51180)]:
    maturities += annual_row('annual.maturity.'+label, q, label, [value], 46,
                             meaning='Fiscal-year principal bucket under Note 1 default; not the calendar-year issuance range.')
annual_row('annual.maturity.total', q, 'Total term debt principal', [97341], 46, 1)
balance, cash = {}, {}
for key in ['annual','interim']:
    for name, label, vals, occ in [
        ('cp', 'Commercial paper', [9967,5985] if key=='annual' else [1995,9967], 0),
        ('current', 'Term debt', [10912,9822] if key=='annual' else [10848,10912], 0),
        ('noncurrent', 'Term debt', [85750,95281] if key=='annual' else [83956,85750], 1),
    ]:
        balance[key+'.'+name] = annual_row(key+'.balance.'+name, support[key+'.balance'], label, vals, 34, occ) if key=='annual' else html_row(key+'.balance.'+name, 14, label, vals, occ)
    labels = [('repayments','Repayments of term debt',[-9958,-11151,-9543] if key=='annual' else [-1009,0]),
              ('cp','Proceeds from/(Repayments of) commercial paper, net' if key=='annual' else 'Repayments of commercial paper, net',[3960,-3978,3955] if key=='annual' else [-7944,-3984])]
    if key=='annual': labels += [('proceeds','Proceeds from issuance of term debt, net',[0,5228,5465])]
    for name, label, vals in labels:
        cash[key+'.'+name] = annual_row(key+'.cash.'+name, support[key+'.cash'], label, vals, 36) if key=='annual' else html_row(key+'.cash.'+name, 16, label, vals)
hedges = {}
for key in ['annual','interim']:
    for name, label, vals, occ in [
        ('fx_designated','Foreign exchange contracts',[64069,74730] if key=='annual' else [47466,64069],0),
        ('rate_designated','Interest rate contracts',[14575,19375] if key=='annual' else [14575,14575],0),
        ('fx_undesignated','Foreign exchange contracts',[91493,104777] if key=='annual' else [96150,91493],1),
    ]:
        hedges[key+'.'+name] = annual_row(key+'.hedges.'+name, support[key+'.hedging'], label, vals, 41, occ) if key=='annual' else html_row(key+'.hedges.'+name, 21, label, vals, occ)
for name, label, vals in [('securities','Current and non-current marketable securities',[0,14433]),('debt','Current and non-current term debt',[-13505,-18247])]:
    hedges['annual.hedged_'+name] = annual_row('annual.hedged.'+name,support['annual.hedging'],label,vals,41)
risk = {}
for label, values, target in [('Investment portfolio',[2755,3089],'Decline in fair value'),('Term debt',[139,194],'Increase in annual interest expense')]:
    line = next(l.strip() for l in support['annual.market_risk'].splitlines() if l.strip().startswith(label+' '))
    fields = re.split(r'\s{2,}', line)
    vals = numbers(' '.join(fields[3:]))
    check('rate scenario '+label+' original row', norm(line) in norm(pdf[29].get_text()))
    check('rate scenario '+label+' condition/measure/values', fields[1]=='100 basis points, all tenors' and fields[2]==target and vals==list(map(str,values)))
    risk[label] = [F(x) for x in vals]
    tables['annual.risk.'+label] = dict(label=label, scenario=fields[1], target=target, values=vals,
        dates=['2024-09-28','2023-09-30'], unit='USD million', displayed_quantum='1 million',
        associated_derivatives_included=True, original_pdf_page=30, literal=line)


def claim(name, reference, literal, values, meaning):
    q = notes[reference]['quote'] if reference in notes else support[reference]
    check(name+' literal source support', norm(literal) in norm(q))
    claims.append(dict(id=name, reference=reference, literal=literal, values=values, interpretation=meaning))


claim('annual.cp.terms','annual.note.9',
      'had $10.0 billion and $6.0 billion of commercial paper outstanding, respectively, with maturities generally less than nine months. The weighted-average interest rate of the Company’s commercial paper was 5.00% and 5.28% as of September 28, 2024 and September 30, 2023, respectively.',
      dict(balance_billions=['10.0','6.0'],balance_quantum_billions='0.1',rate_percent=['5.00','5.28'],rate_quantum_percentage_points='0.01'),
      'Dated weighted rates are not an inferred contract rate or period borrowing cost.')
claim('annual.term.issuance','annual.note.9',
      'Fixed-rate 0.000% – 4.850% notes 2024 – 2062 $ 97,341 0.03% – 6.65% $ 106,572 0.03% – 6.72%',
      dict(stated_coupon_range_percent=['0.000','4.850'],effective_ranges_percent=[['0.03','6.65'],['0.03','6.72']],calendar_maturity_years=[2024,2062]),
      'Aggregate ranges, not terms for an identified instrument; table explicitly labels calendar years.')
claim('annual.term.fair_value','annual.note.9',
      'the fair value of the Company’s Notes, based on Level 2 inputs, was $88.4 billion and $90.8 billion, respectively.',
      dict(fair_value_billions=['88.4','90.8'],quantum_billions='0.1'), 'Fair value, not a principal or carrying balance.')
claim('interim.cp.balance','interim.note.6',
      'As of December 28, 2024 and September 28, 2024, the Company had $2.0 billion and $10.0 billion of commercial paper outstanding, respectively.',
      dict(balance_billions=['2.0','10.0'],quantum_billions='0.1'), 'Rounded note amounts at the two balance dates.')
claim('interim.term.carrying','interim.note.6',
      'an aggregate carrying amount of $94.8 billion and $96.7 billion, respectively',
      dict(carrying_billions=['94.8','96.7'],quantum_billions='0.1'), 'Rounded totals, not exact principal.')
claim('interim.term.fair_value','interim.note.6',
      'the fair value of the Company’s Notes, based on Level 2 inputs, was $82.7 billion and $88.4 billion, respectively.',
      dict(fair_value_billions=['82.7','88.4'],quantum_billions='0.1'), 'Distinct measurement target from carrying amount.')
claim('annual.contractual_cash','annual.liquidity',
      'an aggregate principal amount of $97.3 billion (collectively the “Notes”), with $10.9 billion payable within 12 months. Future interest payments associated with the Notes total $38.5 billion, with $2.6 billion payable within 12 months.',
      dict(principal_billions='97.3',principal_12m_billions='10.9',interest_billions='38.5',interest_12m_billions='2.6',quantum_billions='0.1'),
      'Undiscounted stated future interest requirements are not period expense, effective rates or present value.')
claim('annual.cp.within12m','annual.liquidity',
      '$10.0 billion of commercial paper outstanding, all of which was payable within 12 months.',
      dict(balance_billions='10.0'), 'Twelve-month cash requirement, not a gross rollover history.')
claim('interim.cp.within12m','interim.liquidity',
      '$2.0 billion of commercial paper outstanding, which was payable within 12 months.',
      dict(balance_billions='2.0'), 'Dated interim cash requirement.')
claim('annual.derivative.gross_presentation','annual.derivative_presentation',
      'The Company presents derivative assets and liabilities at their gross fair values in the Consolidated Balance Sheets.',
      {}, 'Principal, hedged-item basis adjustment and derivative fair values remain separate measures.')
claim('annual.derivative.cash_classification','annual.hedging',
      'The Company classifies cash flows related to derivative instruments in the same section of the Consolidated Statements of Cash Flows as the items being hedged, which are generally classified as operating activities.',
      {}, 'Generally operating is not an all-derivatives operating rule.')
for key in ['annual','interim']:
    claim(key+'.hedge_horizon',key+'.hedging',
          'the maximum length of time over which the Company is hedging its exposure to the variability in future cash flows for term debt–related foreign currency transactions is 18 years.',
          dict(years=18), 'Specific cash-flow exposure horizon; no complete instrument or hedge schedule is identified.')
claim('interim.hedged_debt','interim.hedging',
      'the carrying amount of the Company’s current and non-current term debt subject to fair value hedges was $13.3 billion and $13.5 billion, respectively.',
      dict(carrying_billions=['13.3','13.5'],quantum_billions='0.1'), 'Positive liability magnitude in narrative; annual table reports a signed liability.')
claim('annual.fx_var','annual.market_risk',
      'the Company estimates, with 95% confidence, a maximum one-day loss in fair value of $538 million and $669 million as of September 28, 2024 and September 30, 2023, respectively.',
      dict(confidence_percent=95,horizon_days=1,loss_millions=[538,669]),
      'Issuer Monte Carlo VaR description: foreign-currency derivatives only, not a hard maximum or locally replicated loss law.')
claim('annual.fx_var.excluded_underlying','annual.market_risk',
      'Changes in the Company’s underlying foreign currency exposures, which were excluded from the assessment, generally offset changes in the fair values of the Company’s foreign currency derivatives.',
      {}, 'Exclusion prevents interpretation as whole-company net currency risk; generally does not guarantee full offset.')
claim('interim.market_risk.referral','interim.market_risk',
      'There have been no material changes to the Company’s market risk during the first three months of 2025.',
      {}, 'Referral to annual Item 7A supplies context; does not reissue its numerical sensitivity at December 28.')

# Every retained original table is checked by content and dates, not index alone.
for index, labels in [(14,['December 28, 2024','September 28, 2024','Commercial paper','Term debt']),
                      (16,['Three Months Ended','December 28, 2024','December 30, 2023','Repayments of term debt']),
                      (21,['December 28, 2024','September 28, 2024','Derivative instruments designated as accounting hedges:','Derivative instruments not designated as accounting hedges:'])]:
    t = soup.find_all('table')[index].get_text(' ',strip=True)
    check('interim table '+str(index)+' identity and dates',all(norm(s) in norm(t) for s in labels))

for i, year in enumerate([2024,2023,2022]):
    check(str(year)+' longer paper net cash',cp['long_proceeds'][i]+cp['long_repayments'][i]==cp['long_net'][i])
    check(str(year)+' total paper net cash',cp['short_net'][i]+cp['long_net'][i]==cp['total_net'][i]==cash['annual.cp'][i])
for i, year in enumerate([2024,2023]):
    check(str(year)+' principal to carrying',sum(term[n][i] for n in ['principal','net_costs','hedge_basis'])==term['carrying'][i])
    check(str(year)+' current and noncurrent note split',term['carrying'][i]+term['less_current'][i]==term['noncurrent'][i])
    check(str(year)+' balance to note split',balance['annual.current'][i]==-term['less_current'][i] and balance['annual.noncurrent'][i]==term['noncurrent'][i])
check('all six fiscal principal buckets',sum(maturities)==term['principal'][0])
delta = {name:values[0]-values[1] for name,values in term.items()}
net_term_cash = cash['annual.proceeds'][0]+cash['annual.repayments'][0]
principal_residual = delta['principal']-net_term_cash
carrying_residual = delta['carrying']-net_term_cash
check('annual component movement identity',delta['principal']+delta['net_costs']+delta['hedge_basis']==delta['carrying'])
check('annual residual decomposition',principal_residual+delta['net_costs']+delta['hedge_basis']==carrying_residual)
check('annual derived amounts', [delta[n] for n in ['principal','net_costs','hedge_basis','carrying']]+[principal_residual,carrying_residual]==[-9231,35,755,-8441,727,1517])
quarter_carrying = [balance['interim.current'][i]+balance['interim.noncurrent'][i] for i in [0,1]]
quarter_residual = quarter_carrying[0]-quarter_carrying[1]-cash['interim.repayments'][0]
check('quarter bridge agrees with earlier checked result',quarter_residual==prior['calculation_results']['quarter_carrying_reconciliation_residual_after_cash_repayments_musd']==-849)
check('overlap date term balances agree',quarter_carrying[1]==term['carrying'][0])
check('overlap date paper balance agrees',balance['interim.cp'][1]==balance['annual.cp'][0])
cp_bridges = {}
for key in ['annual','interim']:
    closing, opening = balance[key+'.cp']
    flow = cash[key+'.cp'][0]
    residue = closing-opening-flow
    check(key+' paper bridge',opening+flow+residue==closing and residue=={'annual':22,'interim':-28}[key])
    cp_bridges[key]=dict(opening=int(opening),closing=int(closing),change=int(closing-opening),net_cash=int(flow),unallocated_residual=int(residue))
for name, centre, rounded in [('annual.cp2024',9967,10000),('annual.cp2023',5985,6000),('interim.cp',1995,2000),
                               ('interim.term',94804,94800),('annual.term',96662,96700),('annual.principal',97341,97300),
                               ('annual.hedged_debt',13505,13500)]:
    check(name+' conditional nearest-rounding compatibility',abs(F(centre)-rounded)<50,
          'Rounded narrative quantum 100 million; compatibility only, no claim about issuer rounding rule.')
check('maturity/current difference matches earlier result',maturities[0]-balance['annual.current'][0]==prior['calculation_results']['annual_fy2025_principal_minus_current_carrying_musd']==18)

shortcuts = []
for i, year in enumerate([2024,2023]):
    notional = hedges['annual.rate_designated'][i]
    naive = notional/100
    reported = risk['Term debt'][i]
    interval = [naive-F(1,200),naive+F(1,200)]
    target_interval = [reported-F(1,2),reported+F(1,2)]
    overlaps = interval[0]<target_interval[1] and interval[1]>target_interval[0]
    check(str(year)+' notional shortcut rounding relation',overlaps==(year==2023))
    shortcuts.append(dict(year=year,notional_millions=int(notional),shock='1/100',naive_millions=str(naive),
        naive_decimal_millions=float(naive),reported_annual_expense_increase=int(reported),
        difference_millions=str(naive-reported),conditional_rounding_intervals=[list(map(str,interval)),list(map(str,target_interval))],
        overlaps=overlaps,interpretation='2024 mismatch is not explained by nearest rounding. A 2023 match does not validate the shortcut or identify swaps.'))

principal, rate, days, basis = F(1000), F(5,100), F(60), F(360)
interest = principal*rate*days/basis
entries = [
    dict(event='issue at par',debits={'cash':principal},credits={'principal':principal}),
    dict(event='accrue over 60 days',debits={'interest_expense':interest},credits={'interest_payable':interest}),
    dict(event='settle',debits={'principal':principal,'interest_payable':interest},credits={'cash':principal+interest}),
]
book = dict(cash=F(0),principal=F(0),interest_payable=F(0),interest_expense=F(0))
states = []
for row in entries:
    check('example '+row['event']+' balanced journal',sum(row['debits'].values())==sum(row['credits'].values()))
    for account, amount in row['debits'].items():book[account]+=amount
    for account, amount in row['credits'].items():book[account]-=amount
    liability = -book['principal']-book['interest_payable']
    equity = -book['interest_expense']
    check('example '+row['event']+' incremental balance',book['cash']==liability+equity)
    states.append(dict(event=row['event'],incremental_cash=str(book['cash']),principal_liability=str(-book['principal']),
                       interest_payable=str(-book['interest_payable']),incremental_equity=str(equity)))
check('example interest and settlement',interest==F(25,3) and principal+interest==F(3025,3))
check('example net principal is zero with intermediate funding',principal-principal==0 and F(states[0]['incremental_cash'])==1000 and F(states[-1]['principal_liability'])==0)
check('example nonzero cost remains',book['cash']==-F(25,3) and -book['interest_expense']==-F(25,3) and book['interest_payable']==0)
for row in entries:
    for side in ['debits','credits']:row[side]={k:str(v) for k,v in row[side].items()}

queries = [
    ('annual_balance_movement',['annual.note.9.term_measurement','annual.cash'], 'Principal falls 9,231; costs and hedge basis add 35 and 755, making carrying fall 8,441. Cash net term repayment is 9,958.', '727 principal and 1,517 carrying residuals are unallocated differences, not inferred FX or other journals.'),
    ('quarter_carrying',['interim.note.6.term_measurement','interim.balance','interim.cash'], '94,804 equals 96,662 less 1,009 less 849, reproducing the prior result.', 'No new principal/cost/hedge movement detail is disclosed for a unique quarter history.'),
    ('maturity_and_current',['annual.note.9.principal_maturities','annual.calendar','annual.liquidity'], 'Six fiscal buckets sum to 97,341; first bucket 10,930 differs from current carrying 10,912.', 'Calendar issuance range and twelve-month cash requirements cannot replace fiscal buckets. The 18 difference is not an allocated cost or hedge item.'),
    ('measurement_and_rates',['annual.note.9.term_measurement','annual.note.9.effective_rates','annual.note.9.fair_value','interim.note.6.term_measurement'], 'Principal, carrying, fair value, stated coupon and effective rates have distinct targets and precision.', 'No issue price, unique effective-interest schedule or undisclosed instrument-specific rate is identified.'),
    ('paper_balance_cash',['annual.note.9.commercial_cash','annual.balance','annual.cash','interim.balance','interim.cash'], 'All three annual maturity-class flow bridges reconcile; annual and quarter balance/cash residuals are +22 and -28.', 'Residual causes and gross flows inside reported net rows remain unknown.'),
    ('paper_rollover',['annual.note.9.commercial_terms','annual.note.9.commercial_cash'], 'A hypothetical 60-day at-par round trip contributes zero net principal cash but funds 1,000 temporarily and costs 25/3.', 'This is a scoped incremental principal-flow example. It does not fit all Apple disclosures or preserve interest/other statement targets.'),
    ('contractual_cash',['annual.liquidity','interim.liquidity'], 'Future interest 38.5 billion and 2.6 billion within twelve months are disclosed separately from principal.', 'No present value, annual expense or exact dated payment sequence follows from these rounded commitments.'),
    ('rate_shock',['annual.market_risk','annual.hedging','interim.market_risk'], 'Issuer scenario adds 100 basis points at all tenors including associated derivatives: annual term interest expense +139/+194.', 'Notional times 1% is not the reported measure; December no-material-change referral does not update those figures.'),
    ('foreign_currency_risk',['annual.market_risk','annual.hedging','interim.hedging'], 'Issuer reports 95% one-day derivative VaR 538/669, excluding underlying exposures; maximum debt FX cash-flow hedge horizon is 18 years.', 'Not whole-company VaR, a hard maximum, a local model replication or evidence that every exposure is hedged.'),
    ('hedge_presentation',['annual.derivative_presentation','annual.hedging','annual.note.9.linked_swaps'], 'Gross derivative balance presentation, hedged-item basis adjustments and cash classification by hedged item remain separately specified.', 'No blanket netting, operating classification or complete hedge-accounting eligibility determination is inferred.'),
]
known_ids = {u['id'] for u in units} | set(deps)
for name, references, answer, unknown in queries:
    check('query '+name+' source references resolve',set(references)<=known_ids)

calc = dict(
    units='USD millions unless expressly stated; exact arithmetic on displayed centres, not unrounded issuer records',
    annual_term=dict(component_changes={k:int(v) for k,v in delta.items()},net_cash=int(net_term_cash),
                     unallocated_principal_residual=int(principal_residual),unallocated_carrying_residual=int(carrying_residual),
                     interpretation='The net-proceeds row is not automatically legal face proceeds. No residual is assigned a cause or journal.'),
    quarter_term=dict(carrying=list(map(int,quarter_carrying)),cash_repayment=-int(cash['interim.repayments'][0]),unallocated_residual=int(quarter_residual),status='prior checked result retained'),
    maturity=dict(buckets=list(map(int,maturities)),total=int(sum(maturities)),current_carrying=int(balance['annual.current'][0]),difference=18,
                  time_scope='Fiscal future-payment buckets; issuance row is explicitly calendar-year; MD&A twelve months is kept separately.'),
    paper_bridges=cp_bridges,notional_shortcuts=shortcuts,
    incremental_example=dict(principal='1000',days='60',simple_rate='1/20',day_count='ACT/360',at_par=True,fees=0,taxes=0,hedges=False,
        assumptions='USD at par; accrual at stipulated simple 5%; settlement at 60 days; no fees, taxes, hedges or early settlement. 5% is not inferred from Apple’s dated weighted rate.',
        interest=str(interest),interest_decimal=float(interest),gross_principal_proceeds='1000',gross_principal_repayment='-1000',net_principal_cash='0',
        journals=entries,states=states,scope='Incremental principal-flow teaching example only; no claim of a complete compatible Apple history. Interest and other statement targets can distinguish it. Negative final incremental cash is a reduction relative to a funded baseline, not a standalone feasible opening balance.',probability='None assigned'),
)
supplement = dict(recorded_at=datetime.now(timezone.utc).isoformat(),plan='docs/plans/accounting-apple-debt-20261009.md',
    source_hashes=inputs,notes=notes,material_units=units,dependencies=deps,tables=tables,narrative_claims=claims,
    table_column_conventions=dict(annual_balance=['2024-09-28','2023-09-30'],annual_flow=['FY2024','FY2023','FY2022'],
        interim_balance=['2024-12-28','2024-09-28'],interim_flow=['FY2025Q1','FY2024Q1']),
    prior_dependency=dict(path='docs/design/cases/apple/continuation-20261007/case-supplement-v1.json',sha256=inputs['docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'],
        query=prior['query'],scope='Retain earlier euro coupon/settlement and 849-quarter-residual findings. No repeated indenture acquisition or new instrument-completeness claim.'),
    queries=[dict(id=n,sources=r,checked_answer=a,unresolved=u) for n,r,a,u in queries],
    coverage=dict(complete_debt_notes=2,material_units=len(units),source_dependencies=len(deps),prior_checked_query_dependencies=1,
        numeric_table_rows=len(tables),numeric_table_cells=sum(len(r['values']) for r in tables.values()),queries=len(queries),
        completeness='Bounded two-note reading with declared dependencies; not the whole filing package, all instruments or all accounting rules.'),
    decision='Integrate checked documentary consequences and scoped example; full proposal remains not_ready.')
save('calculations.json',calc)
save('source-claim-supplement.json',supplement)
outputs={str(p.relative_to(ROOT)):sha(p) for p in (OUT/'sources').iterdir() if p.is_file()}
for name in ['calculations.json','source-claim-supplement.json']:outputs[str((OUT/name).relative_to(ROOT))]=sha(OUT/name)
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,output_hashes=outputs,
    checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),wall_seconds=time.monotonic()-START)
save('evidence-checks.json',report)
print(json.dumps(dict(passed=report['passed'],failed=report['failed'],coverage=supplement['coverage'],annual_term=calc['annual_term'],paper_bridges=cp_bridges)))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']]))
    raise SystemExit(1)
