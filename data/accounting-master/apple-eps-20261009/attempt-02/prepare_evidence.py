"""Bounded filing analysis, exact arithmetic and quantity-history witnesses."""
from datetime import date, datetime, timedelta, timezone
from fractions import Fraction as F
from collections import Counter
import hashlib
import html
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
    raise SystemExit('Closed unit; preserve evidence')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda s: re.sub(r'\s+', '', s)
save = lambda n, d: (OUT / n).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
checks, inputs = [], {}
def check(name, passed, detail=None):
    checks.append(dict(name=name, passed=bool(passed), detail=detail))
def pinned(p):
    inputs[str(p.relative_to(ROOT))] = sha(p)
    return p.read_text()
prior = json.loads(pinned(ROOT / 'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'))
texts = {}
for key in ['annual', 'interim']:
    src = prior['sources'][key]
    for pk, hk in [('original_path', 'original_sha256'), ('extraction_path', 'extraction_sha256')]:
        p = ROOT / src[pk]
        inputs[src[pk]] = sha(p)
        check(key + ' ' + pk + ' hash', sha(p) == src[hk])
    texts[key] = (ROOT / src['extraction_path']).read_text()
pdf = fitz.open(ROOT / prior['sources']['annual']['original_path'])
soup = BeautifulSoup((ROOT / prior['sources']['interim']['original_path']).read_text(), 'html.parser')
notes, units, deps = {}, [], []
specs = {
 'annual.note.3': [('computation', 'Note 3 –', 'Income millions, shares thousands, per-share dollars; three periods'), ('exclusion', 'Approximately 24 million', 'Antidilutive exclusion applies to FY2023; not other years')],
 'annual.note.10': [('repurchases', 'Note 10 –', '499 million/$95.0 billion rounded purchase narrative; no minimum obligation; permitted routes'), ('shares', 'Shares of Common Stock', 'Three annual quantity bridges; net issuance includes employee withholding but is not identified as RSUs alone')],
 'annual.note.11': [('plan2022', 'Note 11 –', 'Permitted award types; RSUs generally four-year service vesting, one-for-one settlement, dividend equivalents, initial authorised maximum'), ('plan2014', '2014 Employee Stock Plan', 'Broadly same award terms plus cash bonuses; new grant authority terminated in third quarter 2022'), ('activity', 'Restricted Stock Units', 'All three annual RSU count movements; grant-date per-award values and closing aggregate fair value have different measurement dates'), ('settlement', 'The fair value as of', 'Vesting-date values, majority net settlement, rounded withheld shares and employee-tax payments; not all net issuance or cash-flow scope'), ('expense', 'Share-Based Compensation\nThe following', 'Expense and related tax benefit by period; neither equals equity compensation line'), ('future', 'As of September 28, 2024, the total unrecognized', 'Unrecognised cost and weighted recognition period; not constant annual expense or cash liability')],
 'interim.note.3': [('computation', 'Note 3 –', 'Two three-month EPS computations, with separate numerator and denominator units')],
 'interim.note.7': [('repurchases', 'Note 7 –', 'Rounded 100 million/$23.3 billion purchases; no minimum obligation; permitted routes')],
 'interim.note.8': [('activity', 'Note 8 –', 'Quarter RSU quantity bridge and grant-date per-award values'), ('vesting', 'The total vesting-date', 'Two comparative vesting-date values, not grant-date cost'), ('expense', 'Share-Based Compensation\nThe following', 'Quarter compensation expense and related tax benefit'), ('future', 'As of December', 'Unrecognised cost and weighted period; no fixed expense schedule')],
}
for ident, spec in specs.items():
    src = next(r['source'] for r in prior['note_dispositions'] if r['note_id'] == ident)
    key = ident.split('.')[0]
    q = texts[key][src['start']:src['end']]
    check(ident + ' exact retained span', q == src['quote'])
    positions = [q.index(marker) for _, marker, _ in spec] + [len(q)]
    check(ident + ' exhaustive ordered partition', positions[0] == 0 and positions == sorted(set(positions)))
    notes[ident] = dict(source=key, start=src['start'], end=src['end'], quote=q)
    (OUT / 'sources' / (ident + '.txt')).write_text(q)
    for (name, _, meaning), a, b in zip(spec, positions, positions[1:]):
        units.append(dict(id=ident+'.'+name, source=key, start=src['start']+a, end=src['start']+b,
                          quote=q[a:b], sha256=hashlib.sha256(q[a:b].encode()).hexdigest(), interpretation=meaning))
    if key == 'annual':
        pages = [39] if ident.endswith('.3') else [47, 48]
        original = ''.join(pdf[p-1].get_text() for p in pages)
        if ident == 'annual.note.11':
            # pdftotext and PyMuPDF order this multi-column header differently.
            # Allow only that exact header permutation; all other text is exact.
            a, b = q.index('Number of'), q.index('Balance as of September 25, 2021')
            c, d = original.index('Number of'), original.index('Balance as of September 25, 2021')
            check(ident+' header token permutation',Counter(re.findall(r'\w+',q[a:b])) == Counter(re.findall(r'\w+',original[c:d])))
            check(ident+' original PDF text outside header',norm(q[:a]+q[b:]) in norm(original[:c]+original[d:]))
        else:
            check(ident + ' original PDF text', norm(q) in norm(original))
    else:
        check(ident + ' original HTML text', norm(q) in norm(soup.get_text()))

def dep(key, name, first, last, meaning):
    t = texts[key]; a = t.index(first); b = t.index(last, a+len(first)); q = t[a:b]
    ident = key+'.'+name
    row = dict(id=ident, source=key, start=a, end=b, quote=q, interpretation=meaning,
               sha256=hashlib.sha256(q.encode()).hexdigest())
    deps.append(row); (OUT/'sources'/(ident+'.txt')).write_text(q)
    return q

support = {}
for key, pre in [('annual',''), ('interim','CONDENSED ')]:
    targets = [('operations','CONSOLIDATED STATEMENTS OF OPERATIONS','CONSOLIDATED STATEMENTS OF COMPREHENSIVE', 'Income, EPS and share-unit/date context'),
               ('balance','CONSOLIDATED BALANCE SHEETS','CONSOLIDATED STATEMENTS OF SHAREHOLDERS', 'Dated issued/outstanding shares and monetary equity'),
               ('equity','CONSOLIDATED STATEMENTS OF SHAREHOLDERS’ EQUITY','CONSOLIDATED STATEMENTS OF CASH FLOWS','Complete monetary equity movement rows, separate from quantity movements'),
               ('cash','CONSOLIDATED STATEMENTS OF CASH FLOWS','Notes to '+('Condensed ' if key=='interim' else '')+'Consolidated Financial Statements','Cash settlement and expense adjustment; selected rows only')]
    for name, first, last, meaning in targets:
        # Cash's accompanying-notes line ends the complete statement before Note 1.
        support[key+'.'+name] = dep(key,name,pre+first,pre+last if name!='cash' else last,meaning)
    support[key+'.calendar'] = dep(key,'calendar','The Company’s fiscal year is the 52-', '\n\nRevenue' if key=='annual' else '\nNote 2', 'Reported fiscal calendar; not calendar-year EPS')
support['annual.purchases'] = dep('annual','purchases','Purchases of Equity Securities by the Issuer','Company Stock Performance','All fourth-quarter purchase intervals, prices, programme counts, unused authority and footnote')
support['interim.purchases'] = dep('interim','purchases','Share repurchase activity during the three months ended','Item 3.', 'All first-quarter purchase intervals, prices, programme counts, unused authority and footnote')
support['annual.capital_return'] = dep('annual','capital_return','Capital Return Program\n','Recent Accounting Pronouncements','Board authorisation, dividend intention and reported annual capital return')
support['interim.capital_return'] = dep('interim','capital_return','Capital Return Program\n','Recent Accounting Pronouncements','Quarter capital return and programme scope')

def parse_values(s):
    s = s.replace('$','').replace('(', '-').replace(')', '')
    s = re.sub(r'-\s+', '-', s)
    return [x.replace(',','') if x!='—' else '0' for x in re.findall(r'-?\d[\d,]*(?:\.\d+)?|—',s)]
tables = {}
def annual_table(key, text, selectors, units_, page, columns):
    rows = []
    for line in text.splitlines():
        clean = line.strip()
        if not any(clean.startswith(label) for label in selectors): continue
        parts = re.split(r'\s{2,}',clean,maxsplit=1)
        if len(parts)!=2: continue
        label, rest = parts; vals=parse_values(rest)
        if not vals: continue
        check(key+' PDF row '+str(len(rows)),norm(clean) in norm(pdf[page-1].get_text()))
        rows.append(dict(label=label,values=vals,literal=clean))
    tables[key]=dict(rows=rows,units=units_,columns=columns,original_pdf_page=page)
    return rows
def html_table(key, index, selectors, units_, columns):
    table=soup.find_all('table')[index];rows=[]
    for tr in table.find_all('tr'):
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'],recursive=False)]
        cells=[c for c in cells if c]
        if not cells or not any(cells[0].startswith(l) for l in selectors):continue
        rows.append(dict(label=cells[0],values=parse_values(' '.join(cells[1:])),literal=' | '.join(cells)))
    tables[key]=dict(rows=rows,units=units_,columns=columns,html_table_index=index)
    (OUT/'sources'/(key+'.html')).write_text(str(table))
    return rows
eps_labels=['Net income','Weighted-average basic','Effect of dilutive','Weighted-average diluted','Basic earnings','Diluted earnings']
eps_units=['USD million','thousand shares','thousand shares','thousand shares','USD/share','USD/share']
annual_table('annual.eps',notes['annual.note.3']['quote'],eps_labels,eps_units,39,['FY2024','FY2023','FY2022'])
html_table('interim.eps',18,eps_labels,eps_units,['FY2025Q1','FY2024Q1'])
annual_table('annual.shares',notes['annual.note.10']['quote'],['Common stock'], 'thousand shares',47,['FY2024','FY2023','FY2022'])
rsu_labels=['Balance as of','RSUs granted','RSUs vested','RSUs canceled']
annual_table('annual.rsu',notes['annual.note.11']['quote'],rsu_labels,['thousand RSUs','USD/RSU grant-date fair value','USD million aggregate fair value, final row only'],48,'dated movements')
html_table('interim.rsu',24,rsu_labels,['thousand RSUs','USD/RSU grant-date fair value'],'dated quarter movements')
comp_labels=['Share-based compensation expense','Income tax benefit related']
annual_table('annual.expense',notes['annual.note.11']['quote'],comp_labels,'USD million',48,['FY2024','FY2023','FY2022'])
html_table('interim.expense',25,comp_labels,'USD million',['FY2025Q1','FY2024Q1'])
eq_labels=['Total shareholders','Beginning balances','Ending balances','Common stock issued','Common stock withheld','Share-based compensation','Net income','Dividends and dividend equivalents declared','Common stock repurchased','Other comprehensive']
annual_table('annual.equity',support['annual.equity'],eq_labels,'USD million; final dividend row USD/share or RSU',35,['FY2024','FY2023','FY2022'])
html_table('interim.equity',15,eq_labels,'USD million; final dividend row USD/share or RSU',['FY2025Q1','FY2024Q1'])
cash_labels=['Share-based compensation expense','Payments for taxes related','Repurchases of common stock']
annual_table('annual.cash',support['annual.cash'],cash_labels,'USD million',36,['FY2024','FY2023','FY2022'])
html_table('interim.cash',16,cash_labels,'USD million',['FY2025Q1','FY2024Q1'])
purchase_labels=['Open market and privately negotiated purchases','Total']
annual_table('annual.purchases',support['annual.purchases'],purchase_labels,['thousand shares','USD/share','thousand programme shares; total row instead unused authority USD million'],22,'three source intervals')
html_table('interim.purchases',34,purchase_labels,['thousand shares','USD/share','thousand programme shares; total row instead unused authority USD million'],'three source intervals')

expected_rows={'annual.eps':6,'interim.eps':6,'annual.shares':4,'annual.rsu':13,'interim.rsu':5,'annual.expense':2,'interim.expense':2,'annual.equity':17,'interim.equity':16,'annual.cash':3,'interim.cash':3,'annual.purchases':4,'interim.purchases':4}
for key, n in expected_rows.items():
    check(key+' row population',len(tables[key]['rows'])==n, len(tables[key]['rows']))
def vals(key,label,occ=0):
    return [F(x) for x in [r for r in tables[key]['rows'] if r['label'].startswith(label)][occ]['values']]
def v(key,label,col=0,occ=0): return vals(key,label,occ)[col]
eps=[]
for key in ['annual','interim']:
    t=key+'.eps'
    for i,period in enumerate(tables[t]['columns']):
        income,basic,awards,diluted=[v(t,l,i) for l in eps_labels[:4]]
        check(period+' denominator bridge',basic+awards==diluted)
        row=dict(period=period,income_millions=int(income),basic_thousands=int(basic),dilution_thousands=int(awards),diluted_thousands=int(diluted))
        for kind,denom,label in [('basic',basic,'Basic earnings'),('diluted',diluted,'Diluted earnings')]:
            ratio=income*1000/denom;reported=v(t,label,i)
            envelope=[(income-F(1,2))*1000/(denom+F(1,2)),(income+F(1,2))*1000/(denom-F(1,2))]
            check(period+' '+kind+' EPS rounding',abs(ratio-reported)<F(1,200))
            check(period+' '+kind+' conditional source rounding overlap',envelope[0]<reported+F(1,200) and envelope[1]>reported-F(1,200))
            row[kind]=dict(exact_ratio=str(ratio),decimal=float(ratio),reported=str(reported),conditional_ratio_envelope=list(map(str,envelope)))
        eps.append(row)
for i,period in enumerate(tables['annual.shares']['columns']):
    s=[F(r['values'][i]) for r in tables['annual.shares']['rows']]
    check(period+' ordinary share bridge',sum(s[:3])==s[3])
for key in ['annual','interim']:
    rows=tables[key+'.rsu']['rows']
    for i in range(0,len(rows)-1,4):
        check(key+' RSU movement '+str(i),sum(F(r['values'][0]) for r in rows[i:i+4])==F(rows[i+4]['values'][0]))
    rows=tables[key+'.purchases']['rows']
    check(key+' monthly purchases total',sum(F(r['values'][0]) for r in rows[:3])==F(rows[3]['values'][0]))
    check(key+' programme quantities match purchased quantities',all(r['values'][0]==r['values'][2] for r in rows[:3]))
    eq=key+'.equity'
    for i in range(3 if key=='annual' else 2):
        capital=v(eq,'Beginning balances',i)+v(eq,'Common stock withheld',i)+v(eq,'Share-based compensation',i)+(v(eq,'Common stock issued',i) if key=='annual' else 0)
        retained=v(eq,'Beginning balances',i,1)+v(eq,'Net income',i)+v(eq,'Dividends and dividend equivalents declared',i)+v(eq,'Common stock withheld',i,1)+v(eq,'Common stock repurchased',i)
        oci=v(eq,'Beginning balances',i,2)+v(eq,'Other comprehensive',i)
        for n,x in enumerate([capital,retained,oci]):check(key+' monetary equity component '+str((i,n)),x==v(eq,'Ending balances',i,n))
        check(key+' total equity '+str(i),capital+retained+oci==v(eq,'Total shareholders’ equity, ending',i))
        check(key+' expense to cash-flow adjustment '+str(i),v(key+'.expense','Share-based compensation expense',i)==v(key+'.cash','Share-based compensation expense',i))

close=15040731;opening=15116786
check('quarter balance shares pinned', '15,040,731' in support['interim.balance'] and '15,116,786' in support['interim.balance'] and 'shares issued and outstanding' in support['interim.balance'])
quarter_purchases=int(v('interim.purchases','Total'))
quarter_other=close-opening+quarter_purchases
differences={}
for key in ['annual','interim']:
    eq=key+'.equity';cash=key+'.cash'
    values=dict(repurchases_equity=-int(v(eq,'Common stock repurchased')),repurchases_cash=-int(v(cash,'Repurchases of common stock')),
        withholding_equity=-int(v(eq,'Common stock withheld')+v(eq,'Common stock withheld',occ=1)),withholding_cash=-int(v(cash,'Payments for taxes related')),
        equity_compensation=int(v(eq,'Share-based compensation')),expense_compensation=int(v(key+'.expense','Share-based compensation expense')))
    values['repurchase_equity_minus_cash']=values['repurchases_equity']-values['repurchases_cash']
    values['withholding_equity_minus_cash']=values['withholding_equity']-values['withholding_cash']
    values['equity_compensation_minus_expense']=values['equity_compensation']-values['expense_compensation']
    differences[key]=values

# Exact conditional quantity model. Day d events apply for days d,...,363.
T=364;S0=int(v('annual.shares','Common stock outstanding, beginning'))*1000
issue=int(v('annual.shares','Common stock issued'))*1000
repurchase=-int(v('annual.shares','Common stock repurchased'))*1000
target=int(v('annual.eps','Weighted-average basic'))*1000
end=int(v('annual.shares','Common stock outstanding, ending'))*1000
check('FY2024 calendar length', (date(2024,9,29)-date(2023,10,1)).days==T and '2024 and 2022 spanned 52 weeks' in support['annual.calendar'])
q4fixed=[(290,-35697000),(322,-42910000),(350,-33653000)]
ranges=[(273,307),(308,335),(336,363)]
check('fixed events respect annual Item 5 intervals',all(a<=d<=b for (d,_),(a,b) in zip(q4fixed,ranges)))
q1target=int(v('interim.eps','Weighted-average basic',col=1))*1000
q1drop=S0-q1target
fixed=[(45,-q1drop),(46,-q1drop)]+q4fixed
initial=[[(182,issue),(189,-224118000),(190,-275254000)],[(91,issue),(177,-246481000),(178,-252891000)]]
rejected=[]
for events in initial:
    w=F(S0)+sum(F(q*(T-d),T) for d,q in events)
    check('screened aggregate-only witness fits annual targets '+str(events[0][0]),S0+sum(q for _,q in events)==end and w==target)
    rejected.append(dict(events=events,annual_fit=True,monthly_fit=False,verdict='Rejected for declared population: no disclosed fourth-quarter repurchases'))
witnesses=[]
for d_issue in [182,91]:
    rest=repurchase+sum(q for _,q in fixed)
    required=(S0-target)*T+issue*(T-d_issue)+sum(q*(T-d) for d,q in fixed)
    duration=required//rest;early=required-duration*rest
    d_early=T-duration-1;d_late=d_early+1
    events=sorted([(d_issue,issue),(d_early,-early),(d_late,-(rest-early))]+fixed)
    daily=[S0+sum(q for d,q in events if d<=day) for day in range(T)]
    weighted=F(S0)+sum(F(q*(T-d),T) for d,q in events)
    ident='H'+str(len(witnesses)+1)
    check(ident+' positive integer quantities and dates',all(isinstance(q,int) and q!=0 and 0<=d<T for d,q in events) and min(daily)>0)
    check(ident+' formula and independent daily sum',weighted==F(sum(daily),T)==target)
    check(ident+' FY2024Q1 comparative average',F(sum(daily[:91]),91)==q1target)
    check(ident+' closing and total repurchases',S0+sum(q for _,q in events)==end and -sum(q for _,q in events if q<0)==repurchase)
    for j,(a,b) in enumerate(ranges):check(ident+' monthly interval '+str(j),-sum(q for d,q in events if a<=d<=b and q<0)==-q4fixed[j][1])
    witnesses.append(dict(id=ident,events=[dict(elapsed_days=d,date=(date(2023,10,1)+timedelta(days=d)).isoformat(),change_shares=q) for d,q in events],
        closing_shares=end,weighted_average_shares=str(weighted),q1_weighted_average_shares=q1target,after_100_days=daily[100]))
check('witnesses differ at intermediate date',witnesses[0]['after_100_days']!=witnesses[1]['after_100_days'])

queries=[
 dict(id='Q1',question='Can closing shares replace the basic denominator?',answer='No: displayed-centre EPS is '+str(float(F(93736000,15116786)))+' rather than 6.11; use period-weighted shares.'),
 dict(id='Q2',question='Do the EPS tables add and reproduce the displayed ratios?',answer='Five basic-plus-award bridges and ten ratios checked, with explicit scale and conditional rounding.'),
 dict(id='Q3',question='Does an annual fit establish compatibility with all retained purchase disclosures?',answer='No: the two initial schedules fit annual totals/average but violate Item 5; rejected before manuscript promotion.'),
 dict(id='Q4',question='Do monthly totals plus annual and first-quarter weighted averages identify dates?',answer='No in the stated quantity model: H1/H2 fit those quantities and differ after 100 elapsed days; not complete monetary histories.'),
 dict(id='Q5',question='Does the interim note leave all net share movement unidentified?',answer=f'Item 2 narrows purchases to {quarter_purchases:,} thousand; opening/closing shares imply {quarter_other:,} thousand net other increases, without identifying their components.'),
 dict(id='Q6',question='Are vested RSUs, net issuance and incremental diluted shares equal?',answer='Different targets: gross award movement, net common-share issuance and period-dependent dilution; reported withholding is rounded and award populations differ.'),
 dict(id='Q7',question='Can purchases, equity charges or withholding amounts replace cash paid?',answer='No; monetary equity and cash rows differ; causes unallocated rather than assigned to fees, tax or unsettled trades.'),
 dict(id='Q8',question='Does unrecognised compensation divided by years supply an expense schedule?',answer='No: weighted periods and future award facts do not specify a constant allocation or cash liability.'),
 dict(id='Q9',question='Does repurchase authority establish an obligation?',answer='No: notes and programme footnotes explicitly deny minimum purchase obligations.'),
 dict(id='Q10',question='Does the anti-dilutive exclusion extend to every period?',answer='The approximately 24-million RSU exclusion is expressly FY2023; other periods remain separate.'),
]
note_keys=['annual.eps','annual.shares','annual.rsu','annual.expense','interim.eps','interim.rsu','interim.expense']
coverage=dict(notes=list(notes),note_units=len(units),dependencies=len(deps),note_numeric_cells=sum(len(r['values']) for k in note_keys for r in tables[k]['rows']),queries=len(queries),whole_apple_package='open',outstanding_exhibit_targets=40,publication_date_repairs=0)
save('source-claim-supplement.json',dict(plan='docs/plans/accounting-apple-eps-20261009.md',sources=prior['sources'],notes=notes,units=units,dependencies=deps,numeric_tables=tables,queries=queries,coverage=coverage,acceptance='Author preparation; independent/human acceptance pending'))
save('calculations.json',dict(eps=eps,quarter_shares=dict(opening_thousands=opening,closing_thousands=close,repurchased_thousands=quarter_purchases,net_other_increase_thousands=quarter_other),differences_millions=differences,quantity_model=dict(days=T,opening_shares=S0,net_issuance_shares=issue,repurchased_shares=repurchase,target_average_shares=target,closing_shares=end,convention='Changes after d elapsed days apply for 364-d days. Displayed centres exact only within this authored model; no other movements/splits. Net issuance grouped into one event; not an RSU vesting history.',rejected_initial_schedules=rejected,witnesses=witnesses,scope='Quantity constraints only; no probabilities, actual timing, price/journal fit or exhaustive history family')))
parts=['<html><body><h1>Derived retained interim filing view</h1><p>Text and DOM tables from the retained SEC HTML; not an original browser screenshot.</p>']
for ident in ['interim.note.3','interim.note.7','interim.note.8']:
    parts.append('<h2>'+ident+'</h2><p>'+html.escape(notes[ident]['quote']).replace('\n','<br>')+'</p>')
for ident in ['interim.equity','interim.cash','interim.purchases']:
    parts.append('<h2>'+ident+'</h2>'+str(soup.find_all('table')[tables[ident]['html_table_index']]))
parts.append('</body></html>')
(OUT/'sources/interim-eps-print.html').write_text('\n'.join(parts))
outputs={str(p.relative_to(ROOT)):sha(p) for p in [OUT/'source-claim-supplement.json',OUT/'calculations.json']+list((OUT/'sources').iterdir())}
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,output_hashes=outputs,checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),coverage=coverage,wall_seconds=time.monotonic()-START)
save('evidence-checks.json',report)
print(json.dumps({k:report[k] for k in ['passed','failed','coverage']}))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']]))
    raise SystemExit(1)
