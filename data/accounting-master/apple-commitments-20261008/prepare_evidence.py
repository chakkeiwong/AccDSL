"""Check the bounded retained commitments disclosures and conditional examples."""
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
    raise SystemExit('Closed unit')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
save = lambda n, d: (OUT / n).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
norm = lambda t: re.sub(r'\s+', '', t)
checks = []
inputs = {}
def check(name, passed, detail=None):
    checks.append(dict(name=name, passed=bool(passed), detail=detail))

priorpath = ROOT / 'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'
prior = json.loads(priorpath.read_text())
inputs[str(priorpath.relative_to(ROOT))] = sha(priorpath)
texts = {}
for key in ['annual', 'interim']:
    src = prior['sources'][key]
    for pk, hk in [('original_path', 'original_sha256'), ('extraction_path', 'extraction_sha256')]:
        p = ROOT / src[pk]
        inputs[src[pk]] = sha(p)
        check(key + ' ' + pk + ' integrity', sha(p) == src[hk])
    texts[key] = (ROOT / src['extraction_path']).read_text()

specs = {
 'annual.note.8': [
  ('heading','Note 8 – Leases','Note identity','No financial assertion','None'),
  ('terms','The Company has lease arrangements','Equipment/facility leases typically original terms <=10 years; multiyear renewal options, some reasonably certain','Retain original term versus remaining term and renewal assumptions; typical is not universal','Contract commencement/renewal decisions and options'),
  ('costs','Payments under the Company’s lease arrangements','Fixed/variable payments; variable primarily output-related; fixed operating and variable all-lease costs have different scope','Historical costs are not future fixed cash; variable output, rates and procurement overlaps stay unresolved','Output paths, prices, classification, timing and population overlap'),
  ('cash_noncash','The Company made fixed cash payments','Operating fixed cash 1.9/1.9/1.8 and noncash ROU additions 1.0/2.1/2.8 billion in 2024/23/22','Separate expense, cash and noncash recognition, with explicit years','Reconciliation of all lease movements'),
  ('assets_liabilities','The following table shows ROU assets','ROU and operating/finance liability components and their statement lines at two dates','Carry measurement and classification; ROU amount need not equal liability','Full amortisation/prepayment/incentive/modification histories'),
  ('maturities','Lease liability maturities','Undiscounted fiscal-year cash buckets, imputed interest and liabilities by lease class','Reconcile columns; do not add discounted liability and gross maturities as separate cash needs','Exact within-year dates and thereafter tail'),
  ('rates','The weighted-average remaining lease term','Remaining term 10.3/10.6 years and discount rate 3.1/3.0%; rates generally estimated incremental borrowing rate','Aggregate descriptions do not identify every contract rate or cash timing; original term and remaining term differ','Contract curves, weights and renewal/cash timing'),
  ('uncommenced','As of September 28, 2024, the Company had $849','849 million fixed obligations for additional leases, mainly corporate/retail, not commenced; start 2025–26, terms <1–21 years','Preserve separate commencement obligation; do not append face amount to recognised liability','Dates, allocation, discount rates and accounting treatment'),
 ],
 'annual.note.12': [
  ('heading','Note 12 – Commitments','Note identity','No financial assertion','None'),
  ('purchases','Unconditional Purchase Obligations','Off-balance purchase commitments, primarily supplier/IP/content/distribution; table limited to remaining terms >1 year at September date','Long contract term does not place every payment beyond next year; table is not all purchases or recognised liabilities','Category mapping, short-term contracts, delivery and settlement facts'),
  ('contingencies','\fContingencies\n','Unresolved legal claims; litigation inherently uncertain; management conclusion about reasonable possibility of material loss/excess over accrual','Preserve attribution, materiality and possibility qualifier; do not assign zero loss or zero probability','Claims, accrued amounts, severity and timing; legal-proceedings cross-reference unresolved here'),
  ('supply','Concentrations in the Available Sources','Mostly multiple sources, some single/limited; competition, shortages and commodity-price fluctuations','Future purchases and production can share supply shocks; do not assume independent fixed unit prices','Suppliers, contracts, input mapping and joint scenarios'),
  ('custom','The Company uses some custom components','Some custom/new technologies initially one source; yield/capacity maturation and supplier choices affect availability/prices','Retain capacity/delivery constraints and alternative outcomes rather than arbitrary fulfillment','Substitution, capacity, yield paths and contract terms'),
  ('locations','Substantially all of the Company’s hardware products','Outsourced manufacturing primarily in six named locations','Location describes manufacturing, not revenue segments, entity ownership or deterministic shock','Supplier geography and actual legal/control/dependency mapping'),
 ],
 'interim.note.9': [
  ('heading','Note 9 –','Note identity','No financial assertion','None'),
  ('contingencies','The Company is subject to various legal proceedings','Dated interim management contingency assessment, same qualified wording','A later qualitative assessment does not prove identical claims or accruals','Claim-specific developments, values and legal-proceedings facts'),
 ],
}
units = []
notes = {}
for note_id, rows in specs.items():
    src = next(n['source'] for n in prior['note_dispositions'] if n['note_id'] == note_id)
    key = note_id.split('.')[0]
    text = texts[key][src['start']:src['end']]
    check(note_id + ' retained exact span', text == src['quote'])
    positions = [text.index(row[1]) for row in rows]
    check(note_id + ' ordered units', positions[0] == 0 and positions == sorted(set(positions)))
    positions.append(len(text))
    rebuilt = ''
    for i, (ident, marker, meaning, consequence, unknown) in enumerate(rows):
        a, b = positions[i:i+2]
        quote = text[a:b]
        rebuilt += quote
        units.append(dict(id=note_id+'.'+ident, source=key, source_start=src['start']+a, source_end=src['start']+b,
            quote=quote, span_sha256=hashlib.sha256(quote.encode()).hexdigest(), interpretation=meaning,
            query_consequence=consequence, missing_facts=unknown, status='Author interpretation; independent/human admission pending'))
    check(note_id + ' full character coverage', rebuilt == text)
    notes[note_id] = dict(source=src, unit_ids=[u['id'] for u in units if u['id'].startswith(note_id+'.')])
    (OUT / 'sources' / (note_id+'.txt')).write_text(text)

dep_specs = [
 ('annual','policy','The Company combines and accounts for lease and nonlease components','\fNote 2',
  'Policy combines lease/nonlease components only for stated corporate, data-center and retail facilities; do not generalise to all classes'),
 ('annual','mda_leases','Leases\nThe Company has lease arrangements','\n\nManufacturing Purchase Obligations',
  '15.6 billion fixed lease obligations, 2.0 due within twelve months, at September date; different precision from note'),
 ('annual','mda_manufacturing','Manufacturing Purchase Obligations\nThe Company utilizes','\n\nOther Purchase Obligations',
  'Manufacturing 53.0 billion, 52.9 within twelve months; outsourcing and suppliers; broader cash-requirement evidence than Note 12'),
 ('annual','mda_other','Other Purchase Obligations\nThe Company’s other purchase obligations','\n\nDeemed Repatriation Tax Payable',
  'Other 12.0 billion, 4.1 within twelve months, includes capital assets as well as suppliers/IP/content/distribution; mapping to Note 12 not supplied'),
 ('interim','mda_changes','The Company’s contractual cash requirements have not changed materially','\nCommercial Paper',
  'No material change except commercial paper, manufacturing and State Aid tax; qualitative threshold not quantified; no fresh lease maturity values'),
 ('interim','mda_manufacturing','Manufacturing Purchase Obligations\nThe Company utilizes','\nState Aid Decision Tax Payable',
  'Manufacturing obligations 39.8 billion, all payable within twelve months, at December date; different date and moving horizon'),
]
dependencies = []
for key, ident, first, last, meaning in dep_specs:
    text = texts[key]
    a = text.index(first)
    b = text.index(last, a)
    quote = text[a:b]
    dependencies.append(dict(id=key+'.'+ident, source=key, source_start=a, source_end=b,
        quote=quote, span_sha256=hashlib.sha256(quote.encode()).hexdigest(), interpretation=meaning))
    (OUT / 'sources' / (key+'.'+ident+'.txt')).write_text(quote)

lease = notes['annual.note.8']['source']['quote']
purchases = notes['annual.note.12']['source']['quote']
assets_text = lease.split('Right-of-use assets:',1)[1].split('Lease liabilities:',1)[0]
liabilities_text = lease.split('Lease liabilities:',1)[1].split('Lease liability maturities',1)[0]
parse_line = lambda line: [int(s.replace(',','')) for s in re.findall(r'\(?\b\d[\d,]*\b\)?', line)]
# Table rows below are independently expected values, checked against exact extracted rows and original page.
expected_assets = [[10234,10661],[1069,1015],[11303,11676]]
expected_liabilities = [[1488,1410],[10046,10408],[144,165],[752,859],[12430,12842]]
assets = [parse_line(l) for l in assets_text.splitlines() if re.search(r'\d',l)]
liabilities = [parse_line(l) for l in liabilities_text.splitlines() if re.search(r'\d',l)]
check('ROU table values and 2024/2023 order', assets == expected_assets)
check('liability table values and 2024/2023 order', liabilities == expected_liabilities)
for i, year in enumerate([2024,2023]):
    check(f'ROU component sum {year}', sum(r[i] for r in assets[:2]) == assets[2][i])
    check(f'liability component sum {year}', sum(r[i] for r in liabilities[:4]) == liabilities[4][i])
maturity_text = lease.split('Lease liability maturities',1)[1].split('The weighted-average',1)[0]
maturity = {}
for label in ['2025','2026','2027','2028','2029','Thereafter','Total undiscounted liabilities','Less: Imputed interest','Total lease liabilities']:
    line = next(l for l in maturity_text.splitlines() if l.strip().startswith(label))
    # Remove the textual year/label before reading monetary cells.
    vals = [int(s.replace(',','')) for s in re.findall(r'\b\d[\d,]*\b',line.strip()[len(label):])]
    maturity[label] = vals
    check('maturity three columns '+label, len(vals) == 3)
    check('maturity class sum '+label, vals[0]+vals[1] == vals[2])
for i, cls in enumerate(['operating','finance','all']):
    check('undiscounted bucket sum '+cls, sum(maturity[k][i] for k in list(maturity)[:6]) == maturity['Total undiscounted liabilities'][i])
    check('imputed interest reconciliation '+cls, maturity['Total undiscounted liabilities'][i]-maturity['Less: Imputed interest'][i] == maturity['Total lease liabilities'][i])
check('operating liabilities tie to current/noncurrent lines', maturity['Total lease liabilities'][0] == liabilities[0][0]+liabilities[1][0])
check('finance liabilities tie to current/noncurrent lines', maturity['Total lease liabilities'][1] == liabilities[2][0]+liabilities[3][0])
purchase_rows = {}
for label in ['2025','2026','2027','2028','2029','Thereafter','Total']:
    line = next(l for l in purchases.splitlines() if l.strip().startswith(label))
    vals = [int(s.replace(',','')) for s in re.findall(r'\b\d[\d,]*\b',line.strip()[len(label):])]
    check('purchase one monetary column '+label,len(vals)==1)
    purchase_rows[label] = vals[0]
check('purchase table total',sum(v for k,v in purchase_rows.items() if k!='Total')==purchase_rows['Total']==11226)
check('long-term contract includes first-year payments',purchase_rows['2025']==3206 and 'remaining term in excess of one year' in purchases)

annpdf = fitz.open(ROOT / prior['sources']['annual']['original_path'])
original_lease = norm(annpdf[44].get_text()).replace('$','')
original_purchase = norm(annpdf[47].get_text()).replace('$','')
for label, vals in list(maturity.items()) + [('ROU'+str(i),v) for i,v in enumerate(assets)] + [('liability'+str(i),v) for i,v in enumerate(liabilities)]:
    check('original PDF lease cells '+label,all(f'{v:,}' in original_lease for v in vals))
for label, value in purchase_rows.items():
    check('original PDF purchase cell '+label,f'{value:,}' in original_purchase)

soup = BeautifulSoup((ROOT/prior['sources']['interim']['original_path']).read_bytes(),'html.parser')
selected = []
for prefix in ['The Company’s contractual cash requirements','The Company utilizes several outsourcing partners','The Company is subject to various legal proceedings']:
    node = next(x for x in soup.find_all(string=True) if str(x).startswith(prefix)).parent.parent
    selected.append(str(node))
    check('interim original HTML text '+prefix, norm(node.get_text()) in norm(texts['interim']))
html = '<html><head><meta charset="utf-8"></head><body><h1>Retained interim passages — derived print view</h1>'+''.join(selected)+'</body></html>'
(OUT/'sources/interim-selected-print.html').write_text(html)
for phrase in ['fixed lease payment obligations of $15.6 billion, with $2.0 billion payable within 12 months',
               'manufacturing purchase obligations of $53.0 billion, with $52.9 billion payable within 12 months',
               'other purchase obligations of $12.0 billion, with $4.1 billion payable within 12 months']:
    check('annual MD&A amount/context '+phrase, norm(phrase) in norm(texts['annual']) and norm(phrase) in norm(annpdf[27].get_text()))
check('interim manufacturing amount/context',norm('manufacturing purchase obligations of $39.8 billion, which were payable within 12 months') in norm(texts['interim']))
interim_heads = re.findall(r'Note \d+ –\s*\n([^\n]+)', texts['interim'])
check('interim note inventory has no separate lease note', len(interim_heads)==10 and not any('lease' in h.lower() for h in interim_heads), interim_heads)
check('interim has no new lease maturity table', 'Lease liability maturities' not in texts['interim'],
      'Bounded retained-file search and note inventory; not a claim of no lease-related disclosure anywhere')
for phrase in [
 'Lease costs associated with fixed payments on the Company’s operating leases were $2.0 billion for both 2024 and 2023 and $1.9 billion for 2022',
 'Lease costs associated with variable payments on the Company’s leases were $13.8 billion, $13.9 billion and $14.9 billion for 2024, 2023 and 2022',
 'fixed cash payments related to operating leases of $1.9 billion in both 2024 and 2023 and $1.8 billion in 2022',
 'assets obtained in exchange for lease liabilities were $1.0 billion, $2.1 billion and $2.8 billion for 2024, 2023 and 2022',
 'was 10.3 years and 10.6 years', 'was 3.1% and 3.0%',
 'These leases will commence between 2025 and 2026, with lease terms ranging from less than 1 year to 21 years',
]:
    check('lease narrative number and scope '+phrase, norm(phrase) in norm(lease) and norm(phrase) in norm(annpdf[44].get_text()))

gross = F(maturity['Total undiscounted liabilities'][2],1000)
uncommenced = F(849,1000)
fixed_sum = gross + uncommenced
check('gross plus uncommenced displayed-centre sum',fixed_sum==F('15.639'))
check('MD&A fixed obligations conditional rounding compatibility',F('15.55')<=fixed_sum<=F('15.65'))
check('current liability is distinct from first maturity bucket',liabilities[0][0]+liabilities[2][0]==1632 and maturity['2025'][2]==1991)
check('ROU asset and liability need not equal',assets[2][0]==11303 and liabilities[4][0]==12430 and assets[2][0]!=liabilities[4][0])

opening, closing = F(53), F('39.8')
histories = []
for name, additions in [('H1',F(0)),('H2',F(5))]:
    delivery = opening+additions-closing
    check(name+' assumed undelivered-commitment reconciliation', opening+additions-delivery==closing)
    for settlement in ['cash','payable']:
        inventory = delivery
        cash = -delivery if settlement=='cash' else F(0)
        payable = F(0) if settlement=='cash' else delivery
        entries = [dict(account='inventory',debit=str(delivery),credit='0'),
                   dict(account='cash' if settlement=='cash' else 'trade_payables',debit='0',credit=str(delivery))]
        check(name+' '+settlement+' incremental balance sheet', inventory+cash==payable)
        check(name+' '+settlement+' journal debits equal credits',sum(F(j['debit']) for j in entries)==sum(F(j['credit']) for j in entries)==delivery)
        histories.append(dict(id=name+'.'+settlement,new_orders=str(additions),deliveries=str(delivery),closing_commitment=str(closing),
            delta_inventory=str(inventory),delta_cash=str(cash),delta_payable=str(payable),profit_effect='0',journal_entries=entries))
check('different deliveries preserve selected commitment balances',{h['deliveries'] for h in histories}=={'66/5','91/5'})
check('settlement changes cash without changing deliveries',len({h['delta_cash'] for h in histories})==3)
calculations=dict(units='USD billion except explicit million tables',lease_maturity=maturity,rou_assets=assets,lease_liabilities=liabilities,purchase_schedule=purchase_rows,
    fixed_payment_compatibility=dict(undiscounted='14.790',uncommenced='0.849',sum='15.639',mda='15.6',status='Conditional rounding compatibility, not a contract-population proof or recognised liability'),
    purchase_point_change='13.2',histories=histories,
    assumptions=['Displayed 53.0 and 39.8 used as exact illustrative inputs', 'One comparable population of fixed-price undelivered orders removed on delivery; this reporting convention is not established for every issuer obligation',
                 'No cancellations, price/FX changes, taxes, opening payables or prepayments; all delivered goods remain unsold inventory',
                 'No equity/profit effect in this inventory-only subsystem; actual consumption/expense/impairment requires facts'],
    nonclaims=['No actual Apple purchases/cash estimate','No fit to other Apple statement constraints','No complete real history family','No inferred probabilities','No full ASC authority'])
queries = [
 dict(id='Q1',question='How much lease liability is recognised?',answer='12,430 million at September date; operating/finance current and noncurrent components retained; gross maturity total is different',depends=['annual.note.8.assets_liabilities','annual.note.8.maturities']),
 dict(id='Q2',question='Does 15.6 billion identify the recognised liability or a complete cash forecast?',answer='No; gross fixed obligations are distinct from discounted liability, variable amounts and future changes. 14.790+0.849=15.639 is rounding-compatible only',depends=['annual.note.8.uncommenced','annual.mda_leases']),
 dict(id='Q3',question='Can 3.1% and annual buckets reproduce the lease book?',answer='Not uniquely: contract rates, timing, options and thereafter distribution missing; do not apply one aggregate rate mechanically',depends=['annual.note.8.rates','annual.note.8.maturities']),
 dict(id='Q4',question='Is variable cost a separate fixed future outflow?',answer='No: output, rates, settlement and overlap with manufacturing commitments need facts; no blanket addition',depends=['annual.note.8.costs','annual.mda_manufacturing']),
 dict(id='Q5',question='Does the purchase table omit all upcoming-year payments?',answer='No: 3,206 of 11,226 million is in 2025 although contract remaining terms exceed one year. Broader MD&A gives near-term aggregates',depends=['annual.note.12.purchases','annual.mda_manufacturing','annual.mda_other']),
 dict(id='Q6',question='Does 12.0 minus 11.226 identify short contracts?',answer='Unsupported without mapping category/term populations and precision; 12.0 includes capital purchases, while Note 12 lists its own scope',depends=['annual.note.12.purchases','annual.mda_other']),
 dict(id='Q7',question='Does the 53.0-to-39.8 decrease identify purchases or cash?',answer='No roll-forward supplied; 13.2/18.2 illustrative deliveries with cash/payable alternatives preserve selected endpoints under explicit model assumptions',depends=['annual.mda_manufacturing','interim.mda_manufacturing']),
 dict(id='Q8',question='Can annual lease values be stamped as exact December observations?',answer='No: qualitative no-material-change assertion is not new measurement or zero change',depends=['interim.mda_changes']),
 dict(id='Q9',question='May litigation and supply uncertainty be set to zero?',answer='No: preserve dated management assessment, materiality and unresolved claims; source concentration affects joint delivery/price scenarios without assigning probabilities',depends=['annual.note.12.contingencies','annual.note.12.supply','annual.note.12.custom','annual.note.12.locations','interim.note.9.contingencies']),
]
ledger=dict(plan='docs/plans/accounting-apple-commitments-20261008.md',sources=prior['sources'],notes=notes,units=units,dependencies=dependencies,
    numeric_tables=dict(rou_assets=assets,lease_liabilities=liabilities,maturity=maturity,purchases=purchase_rows,monetary_cells=50),queries=queries,
    previous_assertion_refinement=dict(id='A18',status='Historical note-scope assertion preserved; new MD&A evidence qualifies its file-wide short-term implication',
        finding='Near-term manufacturing and other-purchase aggregate amounts are reported; contract-level detail and category/term reconciliation remain unknown'),
    coverage=dict(note_units=len(units),dependency_passages=len(dependencies),whole_apple_package='open',outstanding_exhibit_targets=40,publication_date_repairs=0),
    acceptance=dict(author_interpretation='provisional',independent_reader='pending',human_acceptance='pending',full_readiness='not_ready'))
save('source-claim-supplement.json',ledger)
save('commitment-history.json',calculations)
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,
    output_hashes={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in ['source-claim-supplement.json','commitment-history.json']},
    checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),wall_seconds=time.monotonic()-START)
save('evidence-checks.json',report)
print(json.dumps(dict(passed=report['passed'],failed=report['failed'],units=len(units),queries=len(queries))))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']]))
    raise SystemExit(1)
