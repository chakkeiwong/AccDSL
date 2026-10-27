"""Prepare a bounded inventory from named retained PDF bytes; no state inference."""
from pathlib import Path
from fractions import Fraction
from hashlib import sha256
import json
import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PDF = 'data/financial-report-benchmark/documents/henkel/henkel-2025-annual/original.pdf'
DOC = fitz.open(ROOT / PDF)
OBS = []
QUAL = []
CONTEXT = {
    'issuer': 'Henkel AG & Co. KGaA', 'perimeter': 'Henkel consolidated Group',
    'document_id': 'henkel-2025-annual', 'currency': 'EUR', 'unit': 'million EUR',
    'basis': 'IFRS Accounting Standards as adopted in the European Union',
    'measurement_policy': 'display_only', 'rounding_tie_rule': 'unknown',
    'exact_byte_publication_time': None, 'historical_as_of_admission': False,
    'native_state_admission': False,
}

def dump(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def span(page, phrase):
    text = DOC[page - 1].get_text()
    assert text.count(phrase) == 1, (page, phrase, text.count(phrase))
    start = text.index(phrase)
    return {'kind': 'pdf_text_span', 'start': start, 'end': start + len(phrase), 'text': phrase}

def row(page, y):
    words = DOC[page - 1].get_text('words')
    return [(i, w) for i, w in enumerate(words) if abs(w[1] - y) < .7]

def add(key, concept, year, literal, page, anchor, column, measure='period', category=None):
    amount = None if literal == '–' else str(Fraction(literal.replace(',', '')))
    OBS.append({
        'id': f'{year}.{key}', 'concept': concept, 'literal': literal,
        'display_kind': 'dash' if literal == '–' else ('signed_zero' if literal == '-0' else 'number'),
        'displayed_rational': amount, 'category': category, 'unit': 'million EUR',
        'currency': 'EUR', 'context_id': 'henkel-consolidated-eur-2025-report',
        'period': {'start': f'{year}-01-01', 'end_exclusive': f'{year+1}-01-01'} if measure == 'period' else None,
        'measurement_date': f'{year-1 if measure == "opening" else year}-12-31' if measure != 'period' else None,
        'presentation_year': year,
        'comparative_role': 'comparative_in_2025_report' if year == 2024 else 'current_in_2025_report',
        'column': column, 'physical_page': page, 'printed_page': page-2,
        'source_sha256': sha256((ROOT / PDF).read_bytes()).hexdigest(),
        'anchor': anchor, 'constraint_mode': 'display_only', 'underlying_amount': None,
    })

def table(key, concept, year, literal, page, y, low, high, column, measure='period', category=None):
    candidates = [(i,w) for i,w in row(page,y) if low < w[0] < high]
    assert len(candidates) == 1, (key, candidates)
    i,w = candidates[0]
    assert w[4] == literal, (key, literal, w[4])
    anchor = {'kind':'pdf_word', 'word_index':i, 'token':w[4], 'bbox':list(w[:4]),
              'row_tokens':[{'word_index':j,'token':v[4],'bbox':list(v[:4])} for j,v in row(page,y)]}
    add(key,concept,year,literal,page,anchor,column,measure,category)

def narrative(key,concept,year,literal,page,phrase,measure='period'):
    anchor=span(page,phrase)
    assert phrase.count(literal)==1, (key,phrase)
    anchor['literal_offset']=phrase.index(literal)
    add(key,concept,year,literal,page,anchor,'explicit narrative year',measure)

def qualitative(key,page,phrase,meaning):
    QUAL.append({'id':key,'physical_page':page,'printed_page':page-2,
                 'anchor':span(page,phrase),'interpretation':meaning})

def main():
    assert not (HERE/'observations.json').exists(), 'prepared already'
    for name,digest in json.loads((HERE/'source-lock.json').read_text()).items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest, name
    columns=[('land_buildings',475,510),('plant_machinery',540,570),('factory_office',600,630),('construction',670,690),('total',720,750)]
    for key,concept,page,measure,rows in [
        ('rou_additions','ROU additions',372,'period',[(2024,217.8,['176','11','32','–','219']),(2025,334.0,['104','5','29','–','139'])]),
        ('rou_gross','ROU gross acquisition/manufacturing cost',372,'instant',[(2024,291.7,['1,009','60','104','–','1,173']),(2025,407.9,['942','56','104','–','1,102'])]),
        ('rou_accumulated','ROU accumulated depreciation and impairment',373,'instant',[(2024,265.7,['444','37','61','–','543']),(2025,381.9,['412','40','57','–','508'])]),
        ('rou_net','ROU net carrying amount',374,'instant',[(2024,181.2,['564','23','44','–','631']),(2025,160.1,['530','16','47','–','594'])]),
    ]:
        for year,y,values in rows:
            for (cat,lo,hi),literal in zip(columns,values):
                table(f'{key}.{cat}',concept,year,literal,page,y,lo,hi,cat,measure,cat)
    expenses=[('rou_depreciation','ROU depreciation and impairment',341.1,'153','132'),('rou_dep_land','ROU land/building depreciation and impairment',351.7,'114','96'),('rou_dep_plant','ROU plant/machinery depreciation and impairment',362.2,'14','11'),('rou_dep_office','ROU factory/office depreciation and impairment',372.8,'25','25'),('lease_interest','Lease interest expense',383.3,'25','25'),('short_term_expense','Short-term lease expense',393.9,'12','11'),('low_value_expense','Low-value lease expense',404.5,'6','5'),('variable_expense','Variable lease expense excluded from liability valuation',415.0,'1','1'),('sublease_income','Sublease income',425.6,'5','3')]
    for key,concept,y,v24,v25 in expenses:
        for year,value,lo,hi in [(2024,v24,660,695),(2025,v25,720,750)]:
            table(key,concept,year,value,375,y,lo,hi,str(year))
    for year,values,offset in [(2024,['593','120','713'],0),(2025,['557','109','666'],182)]:
        for i,(cat,value) in enumerate(zip(['noncurrent','current','total'],values)):
            table('liability.'+cat,'Lease liability carrying amount',year,value,399,168.7,420+61*i+offset,445+61*i+offset,cat,'instant',cat)
    for year,page,y,values in [(2024,425,290.5,['713','141','399','276','816']),(2025,426,192.1,['666','114','351','255','721'])]:
        for i,(cat,value) in enumerate(zip(['carrying','due_le_1y','due_1_to_5y','due_gt_5y','total'],values)):
            table('maturity.'+cat,'Lease liability carrying amount' if i==0 else 'Undiscounted contractual lease cash flows',year,value,page,y,480+61*i,510+61*i,cat,'instant',cat)
    reconciliation=[('opening','Opening signed lease liability','opening'),('cash','Cash changes subtotal','period'),('interest_paid','Cash interest paid, included in cash subtotal','period'),('redemption','Cash redemption, included in cash subtotal','period'),('expense','Noncash interest-expense reconciliation','period'),('additions','Signed liability additions','period'),('acquisitions','Acquisition/disposal of subsidiaries','period'),('fx','Foreign exchange movement','period'),('fair_value','Change in fair values','period'),('sundry','Sundry changes','period'),('closing','Closing signed lease liability','instant')]
    for year,page,ys,values in [
        (2024,452,[186.8,197.3,218.5,248.9,289.9,300.4,311,321.5,332.1,342.7,353.3],['-624','171','25','146','-25','-219','-9','-14','7','1','-713']),
        (2025,453,[186.8,197.3,218.5,248.9,279.3,289.9,300.4,311,321.5,332.1,342.7],['-713','158','25','133','-25','-139','1','50','-0','2','-666'])]:
        for (key,concept,measure),y,value in zip(reconciliation,ys,values):
            table('reconciliation.'+key,concept,year,value,page,y,600,625,'Lease liabilities',measure)
    for year,value in [(2024,'-146'),(2025,'-133')]:
        words=DOC[348].get_text('words')
        candidates=[w for w in words if w[4]==value]
        assert candidates
        table('cashflow_redemption','Cash-flow statement redemption of lease liabilities',year,value,349,candidates[0][1],candidates[0][0]-.1,candidates[0][0]+.1,str(year))
    narrative('rou_acquisition','ROU additions through acquisitions',2025,'0',375,'Acquisitions accounted for additions of 0 million euros')
    narrative('rou_acquisition','ROU additions through acquisitions',2024,'10',375,'10 million euros). Additions are offset')
    narrative('total_paid','Total cash paid for leases',2025,'174',376,'Henkel paid 174 million euros in total for leases in fiscal 2025')
    narrative('total_paid','Total cash paid for leases',2024,'189',376,'189 million euros).')
    narrative('uncommenced','Payment commitments for uncommenced leases',2025,'7',376,'payment commitments of 7 million euros','instant')
    narrative('uncommenced','Payment commitments for uncommenced leases',2024,'6',376,'previous year: 6 million euros','instant')
    qualitative('rounding',353,'All individual figures have been rounded. Addition \nmay therefore result in deviations from the totals indicated.', 'Displayed arithmetic may differ from underlying arithmetic; no tie-breaking rule is specified.')
    qualitative('unit',353,'Unless otherwise indicated, all amounts \nare shown in million euros.', 'Use EUR millions; do not import totals into USD methods.')
    qualitative('basis',353,'Financial Reporting Standards (IFRS Accounting Standards) as adopted per \nRegulation number 1606/2002', 'Reported consolidated basis; not independent accounting compliance acceptance.')
    qualitative('prepared',353,'prepared the consolidated financial statements on February 9, \n2026', 'Preparation date is not evidence of exact-byte publication time.')
    qualitative('exempt',375,'In the \ncase of short-term leases and leases involving assets of low value, the \nHenkel Group exercises the option not to recognize a right-of-use asset or \na lease liability.', 'Preserve separately from recognised lease rights.')
    qualitative('rou_measurement',375,'Right-of-use assets are recognized initially at the value of the lease liability \nplus any lease payments made at or prior to provision of the leased asset, \nless any lease incentives received.', 'ROU and liability are not interchangeable measurements; further costs are described in the following sentences.')
    qualitative('rates',376,'This rate is based on country-\nspecific interest rates that are observable in the market and which are \nadjusted with regard to duration and credit risk.', 'No per-contract numeric rate, currency or schedule is supplied here.')
    qualitative('interpolation',376,'If no interest rates are observ-\nable for the relevant durations, they are derived from linear interpolation.', 'Narrative policy does not identify individual rate inputs.')
    qualitative('maturity_link',376,'included with the disclosures on financial instruments in Note 23 on pages \n400 to 428.', 'Followed to physical pages425/426, printed423/424; not whole-note coverage.')
    qualitative('optional',376,'are in the mid-triple-digit million euro range', 'Qualitative magnitude only; no invented numerical endpoints.')
    qualitative('optional_exclusion',376,'They are not included in the measurement of the lease liability \nbecause there is insufficient certainty that the options on the lease periods \nwill be exercised.', 'Missing exercise findings remain separate from recognised-liability maturity flows.')
    qualitative('undiscounted',425,'the scope of IFRS 7 based on undiscounted cash flows', 'Maturity cash flows are not discounted carrying values.')
    dump('observations.json',{'profile':'HenkelLeaseSourceInventory/1','context':CONTEXT,'observations':OBS,'qualitative':QUAL})
    print(json.dumps({'observations':len(OBS),'qualitative':len(QUAL),'physical_pages':len(set(o['physical_page'] for o in OBS+QUAL))}))

if __name__=='__main__':
    main()
