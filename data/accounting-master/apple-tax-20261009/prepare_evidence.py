"""Read the bounded retained tax population and check its stated consequences."""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import html
import json
from pathlib import Path
import re
import time

from bs4 import BeautifulSoup
import fitz

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];START=time.monotonic()
if (OUT/'completion.json').exists():raise SystemExit('Closed unit')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda n,d:(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
norm=lambda s:re.sub(r'\s+','',s)
checks=[];inputs={}
def check(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
def read(p):inputs[str(p.relative_to(ROOT))]=sha(p);return json.loads(p.read_text())
prior=read(ROOT/'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json')
texts={}
for key in ['annual','interim']:
    src=prior['sources'][key]
    for pk,hk in [('original_path','original_sha256'),('extraction_path','extraction_sha256')]:
        p=ROOT/src[pk];inputs[src[pk]]=sha(p);check(key+' '+pk+' integrity',sha(p)==src[hk])
    texts[key]=(ROOT/src['extraction_path']).read_text()
note_src=next(n['source'] for n in prior['note_dispositions'] if n['note_id']=='annual.note.7')
note=texts['annual'][note_src['start']:note_src['end']]
check('full annual Note 7 pinned span',note==note_src['quote'])
spec=[
 ('heading','Note 7 –','Income-tax note identity','No numerical inference'),
 ('state_history','European Commission State Aid Decision','Issuer account of 2016 recovery, covered years and later legislative change','Not independent inspection of the judgment or tax law'),
 ('escrow','From time to time,','Adjusted recovery, interest, escrow gains and cash/securities split','Gross recovery, total escrow and unrestricted funding differ'),
 ('decision','The Company and Ireland appealed','Issuer account of appeal result and FY2024 charge with two offsets','Recognition is separate from later settlement; rounded narrative amounts'),
 ('provision','Provision for Income Taxes and Effective Tax Rate','Federal/state/foreign current and deferred components in three years','Current expense and deferred benefit are distinct; neither equals tax paid'),
 ('foreign_earnings','Foreign pretax earnings','Foreign pretax earnings in three years','Not the base for all consolidated current/foreign tax obligations'),
 ('rate_bridge','A reconciliation of the provision','Statutory expected amount, reconciling categories and effective rates','Period-specific explanation, not a future rate or legal rate for every entity'),
 ('deferred','Deferred Tax Assets and Liabilities','Gross DTA, valuation allowance, DTL and net position at two dates','Recognition/presentation and jurisdictional offset facts remain separate'),
 ('carryforwards','As of September 28, 2024, the Company had $5.1','Irish foreign-credit and California R&D carryforwards, indefinite terms and allowance','Indefinite carryforward does not establish recoverability'),
 ('uncertain','Uncertain Tax Positions','Gross unrecognized benefits versus the subset affecting the effective rate','Gross UTB is not an identified cash payable or expense'),
 ('utb_bridge','The aggregate change','Three-year gross-UTB movement table excluding interest and penalties','Keep signed categories and the excluded population; settlements row is a balance movement'),
 ('examinations','The Company is subject to taxation','Open jurisdictions/years and management possible next-year decrease of 5–13bn','Dated possibility statement, not a probability distribution, payment schedule or verified outcome'),
]
pos=[note.index(s[1]) for s in spec]+[len(note)];check('ordered exhaustive Note 7 partition',pos[0]==0 and pos==sorted(set(pos)))
units=[]
for i,(ident,marker,claim,limit) in enumerate(spec):
    a,b=pos[i:i+2];q=note[a:b]
    units.append(dict(id='annual.note.7.'+ident,source='annual',start=note_src['start']+a,end=note_src['start']+b,quote=q,span_sha256=hashlib.sha256(q.encode()).hexdigest(),interpretation=claim,limit=limit,status='Author reading; independent/human acceptance pending'))
check('all Note 7 characters retained',''.join(u['quote'] for u in units)==note)
(OUT/'sources/annual.note.7.txt').write_text(note)
deps=[]
def dep(key,ident,first,last,meaning,from_pos=0):
    t=texts[key];a=t.index(first,from_pos);b=t.index(last,a+len(first));q=t[a:b]
    row=dict(id=key+'.'+ident,source=key,start=a,end=b,quote=q,span_sha256=hashlib.sha256(q.encode()).hexdigest(),interpretation=meaning)
    deps.append(row);(OUT/'sources'/(row['id']+'.txt')).write_text(q);return q
dep('annual','policy','Income Taxes\nThe Company records certain','\n\nLeases','Certain foreign-minimum-tax DTA/DTL policy; not an entire tax recognition manual',texts['annual'].index('Note 1 –'))
dep('annual','escrow','    (2)    As of September 28, 2024','As of September 28, 2024, 86%','Note 4 restricted cash and securities, with comparative and designated purpose')
dep('annual','note.6','Note 6 –','Note 7 –','Three component tables; tax assets, both payable maturities and their surrounding classifications')
dep('annual','mda_tax','Provision for Income Taxes\n','Liquidity and Capital Resources','Annual rates and causal descriptions; not forecast rates')
dep('annual','mda_liquidity','The Company believes its balances of unrestricted cash','The Company’s material cash requirements','Management liquidity assessment and 140.8bn unrestricted total')
dep('annual','mda_repatriation','Deemed Repatriation Tax Payable','State Aid Decision Tax Payable','16.5bn payable, with 7.2bn expected within twelve months; distinct tax obligation')
dep('annual','mda_stateaid','State Aid Decision Tax Payable','Capital Return Program','Explicit 14.2bn EUR/15.8bn USD opening obligation and restricted settlement funds')
dep('annual','basis','The consolidated financial statements include the accounts of Apple Inc.','\n\nRevenue\n','Consolidated basis, estimates, reclassifications and fiscal calendar')
dep('interim','basis','The condensed consolidated financial statements include the accounts of Apple Inc.','Note 2 –','Interim basis and annual dependency; quarter follows FY2024')
dep('interim','escrow','(2)\nAs of December','As of December\xa028, 2024,\n85','Note 4 restricted cash/securities at both dates; no asset liquidation history')
dep('interim','mda_tax','Provision for Income Taxes\n','Liquidity and Capital Resources','Quarterly rates and qualitative foreign-currency explanations')
dep('interim','mda_stateaid','State Aid Decision Tax Payable','Capital Return Program','Quarter payment and remaining payable in EUR/USD, restricted funds and twelve-month expectation')
for key,heading in [('annual','CONSOLIDATED'),('interim','CONDENSED CONSOLIDATED')]:
    dep(key,'operations_context',heading+' STATEMENTS OF OPERATIONS',heading+' STATEMENTS OF COMPREHENSIVE','Only pretax income, tax expense and net income rows formalised')
    dep(key,'balance_context',heading+' BALANCE SHEETS',heading+' STATEMENTS OF SHAREHOLDERS','Only selected cash/securities and other asset/liability rows used')
    dep(key,'cashflow_context',heading+' STATEMENTS OF CASH FLOWS','Note 1 –','Only tax-paid supplemental row and context formalised; no allocation of all cash movements')
getdep=lambda ident:next(d['quote'] for d in deps if d['id']==ident)
getunit=lambda ident:next(u['quote'] for u in units if u['id'].endswith('.'+ident))
def amounts(t):
    vals=[]
    for s in re.findall(r'\(\s*\d[\d,]*(?:\.\d+)?\s*\)|\b\d[\d,]*(?:\.\d+)?\b|—',t):
        if s=='—':vals.append(0);continue
        v=F(re.sub(r'[(),\s]','',s));v=-v if s.startswith('(') else v
        vals.append(int(v) if v.denominator==1 else str(v))
    return vals
def annual_row(block,label,outlabel=None):
    line=next(l.strip() for l in block.splitlines() if re.match(re.escape(label)+r'\s+[$(\d—]',l.strip()))
    return dict(label=outlabel or label,literal=line,values=amounts(line[len(label):]))
def rows(block,labels):return [annual_row(block,l) for l in labels]
provision=[]
for part,nextpart in [('Federal:','State:'),('State:','Foreign:'),('Foreign:','Provision for income taxes')]:
    block=getunit('provision').split(part,1)[1].split(nextpart,1)[0]
    provision += [annual_row(block,l,part[:-1]+' '+l) for l in ['Current','Deferred','Total']]
provision += rows(getunit('provision'),['Provision for income taxes'])
rec_labels=['Computed expected tax','State taxes, net of federal effect','Impact of the State Aid Decision','Earnings of foreign subsidiaries','Research and development credit, net','Excess tax benefits from equity awards','Other','Provision for income taxes']
dta_labels=['Capitalized research and development','Tax credit carryforwards','Accrued liabilities and other reserves','Deferred revenue','Lease liabilities','Unrealized losses','Other','Total deferred tax assets','Less: Valuation allowance','Total deferred tax assets, net']
dtl_labels=['Depreciation','Right-of-use assets','Minimum tax on foreign earnings','Unrealized gains','Other','Total deferred tax liabilities']
dt=getunit('deferred');dta=dt.split('Deferred tax liabilities:',1)[0];dtl=dt.split('Deferred tax liabilities:',1)[1]
utb_labels=['Beginning balances','Increases related to tax positions taken during a prior year','Decreases related to tax positions taken during a prior year','Increases related to tax positions taken during the current year','Decreases related to settlements with taxing authorities','Decreases related to expiration of the statute of limitations','Ending balances']
tables={
 'provision':dict(columns=['FY2024','FY2023','FY2022'],rows=provision),
 'rate_bridge':dict(columns=['FY2024','FY2023','FY2022'],rows=rows(getunit('rate_bridge'),rec_labels)),
 'deferred':dict(columns=['2024-09-28','2023-09-30'],rows=[annual_row(dta,l,'DTA '+l) for l in dta_labels]+[annual_row(dtl,l,'DTL '+l) for l in dtl_labels]+rows(dtl,['Net deferred tax assets'])),
 'utb':dict(columns=['FY2024','FY2023','FY2022'],rows=rows(getunit('utb_bridge'),utb_labels))}
rates=annual_row(getunit('rate_bridge'),'Effective tax rate')
soup=BeautifulSoup((ROOT/prior['sources']['interim']['original_path']).read_bytes(),'html.parser')
findtable=lambda terms:next(t for t in soup.find_all('table') if all(x in t.get_text(' ',strip=True) for x in terms))
it=findtable(['42,584','Income before provision']);ct=findtable(['18,651','Cash paid for income taxes']);rt=findtable(['Statutory federal income tax rate','6,254']);bt=findtable(['344,085','Inventories'])
def html_row(tab,label):
    line=next(r.get_text(' ',strip=True) for r in tab.find_all('tr') if re.match(re.escape(label)+r'\s+[$(\d—]',r.get_text(' ',strip=True)))
    return dict(label=label,literal=line,values=amounts(line[len(label):]))
op_labels=['Income before provision for income taxes','Provision for income taxes','Net income']
support={
 'annual_operations':dict(columns=['FY2024','FY2023','FY2022'],rows=rows(getdep('annual.operations_context'),op_labels)),
 'interim_operations':dict(columns=['FY2025Q1','FY2024Q1'],rows=[html_row(it,l) for l in op_labels]),
 'annual_cash_tax':dict(columns=['FY2024','FY2023','FY2022'],rows=rows(getdep('annual.cashflow_context'),['Cash paid for income taxes, net'])),
 'interim_cash_tax':dict(columns=['FY2025Q1','FY2024Q1'],rows=[html_row(ct,'Cash paid for income taxes, net')]),
 'interim_rates':dict(columns=['FY2025Q1','FY2024Q1'],rows=[html_row(rt,l) for l in ['Provision for income taxes','Effective tax rate','Statutory federal income tax rate']])}
detail=getdep('annual.note.6')
for ident,title,end,labels in [
 ('assets','Other Non-Current Assets','Other Current Liabilities',['Deferred tax assets','Other non-current assets','Total other non-current assets']),
 ('current','Other Current Liabilities','Other Non-Current Liabilities',['Income taxes payable','Other current liabilities','Total other current liabilities']),
 ('noncurrent','Other Non-Current Liabilities',None,['Income taxes payable','Other non-current liabilities','Total other non-current liabilities'])]:
    block=detail.split(title,1)[1]
    if end:block=block.split(end,1)[0]
    support['annual_detail_'+ident]=dict(columns=['2024-09-28','2023-09-30'],rows=rows(block,labels))
alltables={**tables,**support}
values=lambda key,label:next(r['values'] for r in alltables[key]['rows'] if r['label']==label)
for key,t in alltables.items():check(key+' column counts',all(len(r['values'])==len(t['columns']) for r in t['rows']))
for i,year in enumerate(tables['provision']['columns']):
    for jurisdiction in ['Federal','State','Foreign']:
        check(year+' '+jurisdiction+' expense split',values('provision',jurisdiction+' Current')[i]+values('provision',jurisdiction+' Deferred')[i]==values('provision',jurisdiction+' Total')[i])
    check(year+' total tax',sum(values('provision',j+' Total')[i] for j in ['Federal','State','Foreign'])==values('provision','Provision for income taxes')[i])
    check(year+' statutory reconciliation',sum(r['values'][i] for r in tables['rate_bridge']['rows'][:-1])==values('provision','Provision for income taxes')[i])
    check(year+' UTB rollforward',sum(r['values'][i] for r in tables['utb']['rows'][:-1])==values('utb','Ending balances')[i])
    inc,tax,net=[r['values'][i] for r in support['annual_operations']['rows']]
    check(year+' income less tax',inc-tax==net)
    check(year+' tax matches statement',tax==values('provision','Provision for income taxes')[i])
    check(year+' 21 percent expected tax rounds',abs(F(21,100)*inc-values('rate_bridge','Computed expected tax')[i])<=F(1,2))
    check(year+' effective rate rounding',abs(F(tax*100,inc)-F(rates['values'][i]))<F(1,20))
for i,date in enumerate(tables['deferred']['columns']):
    d=values('deferred','DTA Total deferred tax assets')[i];va=values('deferred','DTA Less: Valuation allowance')[i];dn=values('deferred','DTA Total deferred tax assets, net')[i];l=values('deferred','DTL Total deferred tax liabilities')[i];net=values('deferred','Net deferred tax assets')[i]
    check(date+' gross DTA components',sum(values('deferred','DTA '+x)[i] for x in dta_labels[:7])==d)
    check(date+' allowance deduction',d+va==dn)
    check(date+' DTL components',sum(values('deferred','DTL '+x)[i] for x in dtl_labels[:5])==l)
    check(date+' net deferred position',dn-l==net)
    for k in ['assets','current','noncurrent']:
        v=[r['values'][i] for r in support['annual_detail_'+k]['rows']];check(date+' Note 6 '+k,sum(v[:-1])==v[-1])
for i,period in enumerate(support['interim_operations']['columns']):
    inc,tax,net=[r['values'][i] for r in support['interim_operations']['rows']]
    check(period+' income less tax',inc-tax==net)
    check(period+' tax repeated in MD&A',tax==values('interim_rates','Provision for income taxes')[i])
    check(period+' effective rate rounding',abs(F(tax*100,inc)-F(values('interim_rates','Effective tax rate')[i]))<F(1,20))
check('UTB adjacent annual balances',values('utb','Beginning balances')[:2]==values('utb','Ending balances')[1:])
pdf=fitz.open(ROOT/prior['sources']['annual']['original_path'])
for key,page in [('provision',43),('rate_bridge',43),('deferred',44),('utb',44),('annual_operations',32),('annual_cash_tax',36),('annual_detail_assets',42),('annual_detail_current',42),('annual_detail_noncurrent',42)]:
    original=norm(pdf[page-1].get_text())
    for r in alltables[key]['rows']:check(key+' original PDF '+r['label'],norm(r['literal']) in original)
check('entire Note 7 matches original pages',norm(note.replace('\f','')) in norm(''.join(pdf[p-1].get_text() for p in [42,43,44])))

# Explicitly mapped narrative amounts, retaining literal scale and source anchors.
narrative=[
 ('opening_eur',14200,'EUR',100,'annual.mda_stateaid','€14.2 billion'),
 ('opening_usd',15800,'USD',100,'annual.mda_stateaid','$15.8 billion'),
 ('payment_eur',11000,'EUR',100,'interim.mda_stateaid','€11.0\xa0billion'),
 ('payment_usd',11900,'USD',100,'interim.mda_stateaid','$11.9 billion'),
 ('remaining_eur',3300,'EUR',100,'interim.mda_stateaid','€3.3\xa0billion'),
 ('remaining_usd',3400,'USD',100,'interim.mda_stateaid','$3.4\xa0billion'),
 ('closing_restricted_cash',126,'USD',1,'interim.escrow','$\n126\nmillion'),
 ('closing_restricted_securities',3300,'USD',100,'interim.escrow','$\n3.3\nbillion'),
 ('opening_restricted_cash',2600,'USD',100,'annual.escrow','$2.6 billion'),
 ('opening_restricted_securities',13200,'USD',100,'annual.escrow','$13.2 billion'),
 ('rounded_charge',10200,'USD',100,'annual.note.7.decision','$10.2 billion'),
 ('foreign_tax_credit',4800,'USD',100,'annual.note.7.decision','$4.8 billion'),
 ('utb_offset',823,'USD',1,'annual.note.7.decision','$823 million'),
]
anchors={d['id']:d for d in deps}|{u['id']:u for u in units};mapped=[]
for ident,v,currency,quantum,anchor,literal in narrative:
    q=anchors[anchor]['quote'];check('narrative literal '+ident,literal in q)
    mapped.append(dict(id=ident,value_millions=v,currency=currency,display_quantum_millions=quantum,anchor=anchor,literal=literal))
nv={r['id']:r['value_millions'] for r in mapped}
current=sum(values('provision',j+' Current')[0] for j in ['Federal','State','Foreign'])
deferred=sum(values('provision',j+' Deferred')[0] for j in ['Federal','State','Foreign'])
tax=values('provision','Provision for income taxes')[0];cash=values('annual_cash_tax','Cash paid for income taxes, net')[0]
payables=[values('annual_detail_current','Income taxes payable')[i]+values('annual_detail_noncurrent','Income taxes payable')[i] for i in [0,1]]
netdta=values('deferred','Net deferred tax assets');change=netdta[0]-netdta[1]
charge=values('rate_bridge','Impact of the State Aid Decision')[0]
centre=nv['opening_usd']-nv['foreign_tax_credit']-nv['utb_offset']
check('current plus deferred equals expense',current+deferred==tax)
check('rounded charge agrees with detailed charge',abs(charge-nv['rounded_charge'])<=50)
charge_outer=[F(centre)-F(201,2),F(centre)+F(201,2)]
check('detailed charge is within rounded-component outer envelope',charge_outer[0]<=charge<=charge_outer[1])
movement={c:nv['remaining_'+c]+nv['payment_'+c]-nv['opening_'+c] for c in ['usd','eur']}
envelopes={c:[v-150,v+150] for c,v in movement.items()}
check('USD pure settlement rejected under conditional rounding',envelopes['usd'][1]<0)
check('EUR pure settlement remains rounding compatible',envelopes['eur'][0]<=0<=envelopes['eur'][1])
check('quarter restricted funds and obligation rounding compatible',abs(nv['closing_restricted_cash']+nv['closing_restricted_securities']-nv['remaining_usd'])<=F(201,2))
# Demonstrate settlement only, at carrying value, after a separate funding
# conversion if needed. This is not an estimate of the issuer's actual journal.
journal=[dict(account='tax payable',debit=11900,credit=0),dict(account='restricted cash',debit=0,credit=11900)]
check('conditional settlement journal balances',sum(x['debit'] for x in journal)==sum(x['credit'] for x in journal))
effect=dict(assets=-11900,liabilities=-11900,equity=0,current_period_expense=0)
check('conditional settlement preserves balance equation',effect['assets']==effect['liabilities']+effect['equity'])
check('opening restricted cash alone does not fund payment',nv['opening_restricted_cash']<nv['payment_usd'])
calc=dict(units='Millions with currencies explicitly tagged; displayed centres unless a conditional envelope is stated',
 annual_tax=dict(current_expense=current,deferred_expense=deferred,total_expense=tax,cash_paid_net=cash,expense_minus_cash=tax-cash,
   payable_opening=payables[1],payable_closing=payables[0],payable_change=payables[0]-payables[1],
   current_expense_minus_cash=current-cash,unallocated_payable_movement=payables[0]-payables[1]-(current-cash)),
 deferred=dict(net_opening=netdta[1],net_closing=netdta[0],net_change=change,profit_deferred_benefit=-deferred,
   unallocated_difference=change+deferred,asset_presentation=values('annual_detail_assets','Deferred tax assets'),
   asset_minus_net=[values('annual_detail_assets','Deferred tax assets')[i]-netdta[i] for i in [0,1]],
   limit='Presentation difference is not by itself authority for jurisdictional netting or a separately sourced liability line'),
 stateaid=dict(detailed_charge=charge,rounded_components_centre=centre,centre_difference=charge-centre,
   conditional_charge_outer=[str(v) for v in charge_outer],movement_residuals=movement,conditional_residual_envelopes=envelopes,
   closing_restricted_centres=nv['closing_restricted_cash']+nv['closing_restricted_securities'],remaining_obligation=nv['remaining_usd'],
   limit='USD residual is unallocated; EUR zero-compatibility is not proof of no other movement. Displayed conversion ratios are not a common verified exchange rate.'),
 quarter=dict(expense=values('interim_operations','Provision for income taxes')[0],cash_paid_net=values('interim_cash_tax','Cash paid for income taxes, net')[0],reported_stateaid_payment=nv['payment_usd']),
 conditional_settlement=dict(assumptions=['Payment equals liability carrying value at settlement','Sufficient restricted cash made available from escrow; preceding asset sales/transfers unspecified','No additional tax expense, FX gain/loss or transaction cost in this isolated posting'],journal=journal,statement_effect=effect),
 interpretation='No residual is an identified journal, no full issuer history is reconstructed, and no source conflict or probability distribution is established')
queries=[
 ('expense_cash','Does the annual expense equal cash paid?','No: 29,749 vs 26,102; current 32,780 plus deferred −3,031 gives expense.','Tax allocations and settlement history'),
 ('payables','Does current expense less cash reconstruct total tax payables?','No: change 11,579 vs 6,678 leaves unallocated 4,901 under the simple bridge.','FX, reclassification, vintage and scope of tax positions/payments'),
 ('deferred','Does the net DTA change equal the deferred benefit?','No: 1,951 vs 3,031 leaves −1,080.','OCI/equity/FX/acquisition and jurisdictional offset movements'),
 ('charge','Are the rounded State Aid narrative and 10,246 line incompatible?','No: detailed amount fits the conditional rounded-component envelope.','Unrounded components and issuer rounding rule'),
 ('settlement','Did the later payment create an equal new tax expense?','The report records a payment against the prior obligation; a conditional carrying-value settlement reduces assets/liability without a second expense.','Actual carrying value, funding conversion and gain/loss entries'),
 ('currency','Is the USD obligation reduction equal to the quarter payment?','At displayed centres it needs a −500 other-movement term; a common no-movement USD book fails even under conditional rounding.','Exact dated conversion, accruals, adjustments and settlement entries'),
 ('funds','Is all escrow cash or unrestricted liquidity?','No: annual 2,600 cash plus 13,200 securities; quarter 126 cash plus 3,300 securities, all restricted for the stated purpose.','Liquidation, transfers, valuations and exact balances'),
 ('utb','Is gross UTB or its possible decrease a cash forecast?','No: rollforward excludes interest/penalties; the rate-impact subset and the possible 5–13bn decrease have different targets.','Jurisdictional outcomes, timing, interest/penalties and payments'),
 ('carryforward','Does indefinite carryforward prove recoverability?','No: the issuer reports a valuation allowance on carryforwards and some other differences.','Taxable-profit, jurisdiction and recognition evidence'),
]
ledger=dict(plan='docs/plans/accounting-apple-tax-20261009.md',sources=prior['sources'],note=dict(id='annual.note.7',source=note_src),units=units,dependencies=deps,numeric_tables=tables,effective_rate_row=rates,support_tables=support,narrative_amounts=mapped,queries=[dict(id=i,question=q,supported_answer=a,missing_facts=m) for i,q,a,m in queries],coverage=dict(note_units=len(units),dependency_spans=len(deps),note_monetary_cells=sum(len(r['values']) for t in tables.values() for r in t['rows']),note_percentage_cells=3,whole_apple_package='open',outstanding_exhibit_targets=40,publication_date_repairs=0),acceptance='Author preparation only; independent/human acceptance pending')
save('source-claim-supplement.json',ledger);save('tax-bridges.json',calc)
# Readable derived view: exact retained passages, plus source DOM tables.
parts=['<h1>Retained interim tax disclosures — derived print view</h1>']
for ident in ['interim.escrow','interim.mda_tax','interim.mda_stateaid']:
    parts+=['<h2>'+ident+'</h2><p>'+html.escape(getdep(ident)).replace('\n',' ')+'</p>']
parts+=['<h2>Operating statement</h2>'+str(it),'<h2>Supplemental cash-flow disclosure (full table retained for context)</h2>'+str(ct)]
(OUT/'sources/interim-tax-print.html').write_text('<html><head><meta charset="utf-8"></head><body>'+''.join(parts)+'</body></html>')
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,output_hashes={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in ['source-claim-supplement.json','tax-bridges.json']},checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),wall_seconds=time.monotonic()-START)
save('evidence-checks.json',report)
print(json.dumps(dict(passed=report['passed'],failed=report['failed'],coverage=ledger['coverage'],calculation=calc)))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']]));raise SystemExit(1)
