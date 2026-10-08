"""Read bounded retained asset disclosures and test scoped reconstruction claims."""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import time

from bs4 import BeautifulSoup
import fitz

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
START=time.monotonic()
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

specs={
 'annual.note.5':[
  ('heading','Note 5 –','Note identity; no financial claim','No numeric consequence','None'),
  ('table','The following table shows','Gross cost by three asset classes, accumulated depreciation and net amount at two fiscal dates','Retain gross/contra/net measurement and date; a balance movement is not additions or depreciation','Purchases, disposals, noncash additions, FX/reclassifications, impairments and cohorts'),
  ('expense','Depreciation expense on property','PP&E depreciation expense 8.2/8.5/8.7 billion in FY2024/23/22','Preserve expense scope and tenths-of-billion precision; do not replace with total D&A','Unrounded expense, class allocation and any other movement in accumulated depreciation'),
 ],
 'interim.note.5':[
  ('heading','Note 5 –','Interim statement-detail note identity','No numeric consequence','None'),
  ('context','The following tables show','Consolidated details at December 28 and September 28, 2024, in millions','Dates are stocks, not quarterly flows; September is the annual comparative','Independent historical availability remains unverified here'),
  ('inventory','Inventories','Components/finished goods sum to inventory at two dates','Keep product stage dimension; total does not reveal quantities, prices, purchases or lot age','Transfers, production cost, sales/consumption, write-downs, ownership and FX'),
  ('ppe','Property, Plant and Equipment, Net','Gross PP&E less accumulated depreciation equals net at two dates','Changes in gross and contra balances are net movements, not all acquisitions/depreciation','Asset entries/exits, component lives, residuals and settlement histories'),
 ]}
units=[];notes={}
for note_id,rows in specs.items():
    src=next(n['source'] for n in prior['note_dispositions'] if n['note_id']==note_id)
    key=note_id.split('.')[0];note=texts[key][src['start']:src['end']]
    check(note_id+' original retained span',note==src['quote'])
    pos=[note.index(r[1]) for r in rows];check(note_id+' ordered full span',pos[0]==0 and pos==sorted(set(pos)))
    pos.append(len(note));rebuilt=''
    for i,(ident,marker,claim,consequence,missing) in enumerate(rows):
        a,b=pos[i:i+2];quote=note[a:b];rebuilt+=quote
        units.append(dict(id=note_id+'.'+ident,source=key,start=src['start']+a,end=src['start']+b,
            quote=quote,span_sha256=hashlib.sha256(quote.encode()).hexdigest(),interpretation=claim,
            query_consequence=consequence,missing_facts=missing,status='Author interpretation; independent/human acceptance pending'))
    check(note_id+' complete character partition',rebuilt==note)
    notes[note_id]=dict(source=src,unit_ids=[u['id'] for u in units if u['id'].startswith(note_id+'.')])
    (OUT/'sources'/(note_id+'.txt')).write_text(note)

deps=[]
dep_specs=[
 ('annual','fifo','Inventories\nInventories are measured','\n\nProperty, Plant','Reported FIFO is not a lot-quantity, age, ownership or write-down history'),
 ('annual','straight_line','Property, Plant and Equipment\nDepreciation on','\n\nDerivative Instruments','Reported straight-line policy does not establish useful lives, residual values or available-for-use dates'),
 ('annual','basis','The consolidated financial statements include the accounts of Apple Inc.','\n\nRevenue\n','Consolidated basis, estimates/reclassifications and fiscal 52/53-week calendar; FY2024 precedes December quarter'),
 ('interim','basis','The condensed consolidated financial statements include the accounts of Apple Inc.','Note 2 –','Unaudited consolidated interim, annual-policy reference, estimates and fiscal calendar'),
 ('annual','balance_context','CONSOLIDATED BALANCE SHEETS','CONSOLIDATED STATEMENTS OF SHAREHOLDERS','Table context; only inventory and net PP&E rows formalised in this unit'),
 ('annual','cashflow_context','CONSOLIDATED STATEMENTS OF CASH FLOWS','Note 1 – Summary','Table context; selected operating reconciliation rows and capital-payment row, not every financing transaction'),
 ('interim','balance_context','CONDENSED CONSOLIDATED BALANCE SHEETS','CONDENSED CONSOLIDATED STATEMENTS OF SHAREHOLDERS','Table context; only inventory and net PP&E rows formalised'),
 ('interim','cashflow_context','CONDENSED CONSOLIDATED STATEMENTS OF CASH FLOWS','Note 1 –','Table context; selected operating reconciliation and capital-payment rows only'),
]
for key,ident,first,last,meaning in dep_specs:
    t=texts[key];a=t.index(first);b=t.index(last,a);quote=t[a:b]
    deps.append(dict(id=key+'.'+ident,source=key,start=a,end=b,quote=quote,span_sha256=hashlib.sha256(quote.encode()).hexdigest(),interpretation=meaning))
    (OUT/'sources'/(key+'.'+ident+'.txt')).write_text(quote)
lease_prior_path=ROOT/'data/accounting-master/apple-commitments-20261008/source-claim-supplement.json'
lease_prior=read(lease_prior_path)
for ident in ['annual.note.8.cash_noncash','annual.note.8.assets_liabilities']:
    u=next(u for u in lease_prior['units'] if u['id']==ident)
    check(ident+' dependency remains source-bound',texts['annual'][u['source_start']:u['source_end']]==u['quote'])
    deps.append(dict(id=ident,source='annual',start=u['source_start'],end=u['source_end'],quote=u['quote'],
        span_sha256=u['span_sha256'],prior_ledger=str(lease_prior_path.relative_to(ROOT)),
        interpretation='Noncash ROU additions are across lease classes; only the finance ROU class is mapped to PP&E. Do not add the full 1.0bn to PP&E additions or cash capex'))

def amounts(t):
    out=[]
    for s in re.findall(r'\(\s*\d[\d,]*(?:\.\d+)?\s*\)|\b\d[\d,]*(?:\.\d+)?\b',t):
        negative=s.startswith('(');v=F(re.sub(r'[(),\s]','',s));out.append(-v if negative else v)
    return [int(v) if v.denominator==1 else str(v) for v in out]
def annual_row(block,label):
    lines=[s.strip() for s in block.splitlines()]
    line=next(s for s in lines if re.match(re.escape(label)+r'\s+[$(\d—]',s))
    return dict(label=label,literal=line,values=amounts(line[len(label):]))
def html_row(table,label):
    rows=[r.get_text(' ',strip=True) for r in table.find_all('tr')]
    row=next(s for s in rows if re.match(re.escape(label)+r'\s+[$(\d—]',s))
    return dict(label=label,literal=row,values=amounts(row[len(label):]))
soup=BeautifulSoup((ROOT/prior['sources']['interim']['original_path']).read_bytes(),'html.parser')
find_table=lambda terms:next(t for t in soup.find_all('table') if all(x in t.get_text(' ',strip=True) for x in terms))
it=find_table(['Components','4,119']);pt=find_table(['Gross property, plant and equipment','120,615'])
bt=find_table(['344,085','Inventories']);ct=find_table(['29,935','3,080'])
ann_note=notes['annual.note.5']['source']['quote']
table_labels=['Land and buildings','Machinery, equipment and internal-use software','Leasehold improvements','Gross property, plant and equipment','Accumulated depreciation','Total property, plant and equipment, net']
tables={
 'annual_ppe':dict(columns=['2024-09-28','2023-09-30'],rows=[annual_row(ann_note,l) for l in table_labels]),
 'interim_inventory':dict(columns=['2024-12-28','2024-09-28'],rows=[html_row(it,l) for l in ['Components','Finished goods','Total inventories']]),
 'interim_ppe':dict(columns=['2024-12-28','2024-09-28'],rows=[html_row(pt,l) for l in table_labels[3:]])}
check('all note monetary cells counted',sum(len(r['values']) for t in tables.values() for r in t['rows'])==24)
for key,tab in tables.items():
    for r in tab['rows']:check(key+' two columns '+r['label'],len(r['values'])==2)
    for i,date in enumerate(tab['columns']):
        vs=[r['values'][i] for r in tab['rows']]
        if key=='annual_ppe':check('annual gross component sum '+date,sum(vs[:3])==vs[3]);check('annual gross plus contra equals net '+date,vs[3]+vs[4]==vs[5])
        elif key=='interim_inventory':check('inventory component sum '+date,sum(vs[:2])==vs[2])
        else:check('interim gross plus contra equals net '+date,vs[0]+vs[1]==vs[2])
ann_balance=next(d['quote'] for d in deps if d['id']=='annual.balance_context')
ann_cf=next(d['quote'] for d in deps if d['id']=='annual.cashflow_context')
op=ann_cf.split('Operating activities:',1)[1].split('Investing activities:',1)[0]
ops=['Net income','Depreciation and amortization','Share-based compensation expense','Other','Accounts receivable, net','Vendor non-trade receivables','Inventories','Other current and non-current assets','Accounts payable','Other current and non-current liabilities','Cash generated by operating activities']
support={
 'annual_balance':dict(columns=['2024-09-28','2023-09-30'],rows=[annual_row(ann_balance,l) for l in ['Inventories','Property, plant and equipment, net']]),
 'interim_balance':dict(columns=['2024-12-28','2024-09-28'],rows=[html_row(bt,l) for l in ['Inventories','Property, plant and equipment, net']]),
 'annual_operating_cash':dict(columns=['FY2024','FY2023','FY2022'],rows=[annual_row(op,l) for l in ops]),
 'interim_operating_cash':dict(columns=['FY2025Q1','FY2024Q1'],rows=[html_row(ct,l) for l in ops]),
 'annual_capital_payment':dict(columns=['FY2024','FY2023','FY2022'],rows=[annual_row(ann_cf,'Payments for acquisition of property, plant and equipment')]),
 'interim_capital_payment':dict(columns=['FY2025Q1','FY2024Q1'],rows=[html_row(ct,'Payments for acquisition of property, plant and equipment')])}
for key,t in support.items():
    check(key+' column counts',all(len(r['values'])==len(t['columns']) for r in t['rows']))
    if 'operating_cash' in key:
        for i,col in enumerate(t['columns']):check(key+' net income and adjustments sum '+col,sum(r['values'][i] for r in t['rows'][:-1])==t['rows'][-1]['values'][i])
alltables={**tables,**support}
get=lambda key,label:next(r['values'] for r in alltables[key]['rows'] if r['label']==label)
annual_net=get('annual_ppe',table_labels[-1]);quarter_net=get('interim_ppe',table_labels[-1])
check('annual net PPE equals balance sheet',annual_net==get('annual_balance','Property, plant and equipment, net'))
check('interim inventory equals balance sheet',get('interim_inventory','Total inventories')==get('interim_balance','Inventories'))
check('interim net PPE equals balance sheet',quarter_net==get('interim_balance','Property, plant and equipment, net'))
for label in table_labels[3:]:check('September PPE repeated comparative '+label,get('annual_ppe',label)[0]==get('interim_ppe',label)[1])
check('September inventory repeated comparative',get('interim_inventory','Total inventories')[1]==get('annual_balance','Inventories')[0])

pdf=fitz.open(ROOT/prior['sources']['annual']['original_path'])
for key,page in [('annual_ppe',42),('annual_balance',34),('annual_operating_cash',36),('annual_capital_payment',36)]:
    text=pdf[page-1].get_text()
    for r in alltables[key]['rows']:check(key+' original PDF '+r['label'],all(f'{abs(v):,}' in text for v in r['values']))
expense_line=next(l.strip() for l in ann_note.splitlines() if l.startswith('Depreciation expense'))
expense_literals=re.findall(r'\$(\d+\.\d+) billion',expense_line)
check('PP&E-specific depreciation values and units',expense_literals==['8.2','8.5','8.7'] and norm(expense_line) in norm(pdf[41].get_text()))
ppe_depreciation=[int(F(s)*1000) for s in expense_literals]
check('PP&E depreciation differs from broad D&A',get('annual_operating_cash','Depreciation and amortization')[0]==11445 and ppe_depreciation[0]==8200)

# Original DOM tables are retained. The print view is derived, not a browser screenshot.
html='<html><head><meta charset="utf-8"></head><body><h1>Retained interim asset and cash-flow tables — derived print view</h1>'+''.join('<h2>'+label+'</h2>'+str(t) for label,t in [('Inventory note',it),('PP&E note',pt),('Balance sheet',bt),('Cash-flow statement',ct)])+'</body></html>'
(OUT/'sources/interim-tables-print.html').write_text(html)

inventory=[]
for period,opening,closing,cf in [
 ('FY2024',get('annual_balance','Inventories')[1],get('annual_balance','Inventories')[0],get('annual_operating_cash','Inventories')[0]),
 ('FY2025Q1',get('interim_inventory','Total inventories')[1],get('interim_inventory','Total inventories')[0],get('interim_operating_cash','Inventories')[0])]:
    delta=closing-opening;residual=cf+delta
    inventory.append(dict(period=period,opening=opening,closing=closing,delta=delta,indirect_cash_adjustment=cf,residual= residual,
        residual_meaning='Reported adjustment minus negative stock change; cause unallocated, not a journal or direct cash measure'))
check('annual inventory difference and unallocated residual',inventory[0]['delta']==955 and inventory[0]['residual']==-91)
check('quarter inventory difference and unallocated residual',inventory[1]['delta']==-375 and inventory[1]['residual']==-160)
check('quarter inventory classes offset',get('interim_inventory','Components')[0]-get('interim_inventory','Components')[1]==-835 and get('interim_inventory','Finished goods')[0]-get('interim_inventory','Finished goods')[1]==460)

g1,g0=get('annual_ppe','Gross property, plant and equipment')
minus_b1,minus_b0=get('annual_ppe','Accumulated depreciation');b0,b1=-minus_b0,-minus_b1
d=ppe_depreciation[0];cash=-get('annual_capital_payment','Payments for acquisition of property, plant and equipment')[0]
delta_g=g1-g0;delta_b=b1-b0
naive_retired=cash-delta_g;removed=d-delta_b;gap=removed-naive_retired
check('annual gross contra net changes',delta_g==4529 and delta_b==2564 and delta_g-delta_b==1965)
check('shortcut fails nonnegative retired carrying amount',naive_retired==4918 and removed==5636 and removed>naive_retired)
check('shortcut gap also follows directly from net assets',gap==718==d-cash+(annual_net[0]-annual_net[1]))
lower=F(d)-50-(F(cash)+F(1,2))+(F(annual_net[0])-F(1,2))-(F(annual_net[1])+F(1,2))
upper=F(d)+50-(F(cash)-F(1,2))+(F(annual_net[0])+F(1,2))-(F(annual_net[1])-F(1,2))
check('conditional nearest-rounding gap remains positive',lower==F('666.5') and upper==F('769.5') and lower>0)
quarter=dict(gross_change=get('interim_ppe','Gross property, plant and equipment')[0]-get('interim_ppe','Gross property, plant and equipment')[1],
    accumulated_change=-get('interim_ppe','Accumulated depreciation')[0]+get('interim_ppe','Accumulated depreciation')[1],
    net_change=quarter_net[0]-quarter_net[1],cash_capital_payment=-get('interim_capital_payment','Payments for acquisition of property, plant and equipment')[0],
    broad_depreciation_amortisation=get('interim_operating_cash','Depreciation and amortization')[0],ppe_depreciation='Not separately disclosed in the inspected interim Note 5')
check('quarter net gross and contra agree',quarter['gross_change']==1487 and quarter['accumulated_change']==1098 and quarter['net_change']==389)

histories=[]
for ident,retired in [('H1',6000),('H2',7000)]:
    added=delta_g+retired;unpaid=added-cash;loss=retired-removed
    entries=[
      dict(event='retire_at_open',postings=[dict(account='accumulated_depreciation',debit=removed,credit=0),dict(account='retirement_loss',debit=loss,credit=0),dict(account='ppe_cost',debit=0,credit=retired)]),
      dict(event='depreciate_survivors',postings=[dict(account='depreciation_expense',debit=d,credit=0),dict(account='accumulated_depreciation',debit=0,credit=d)]),
      dict(event='acquire_at_year_end',postings=[dict(account='ppe_cost',debit=added,credit=0),dict(account='cash',debit=0,credit=cash),dict(account='capital_payable',debit=0,credit=unpaid)])]
    for e in entries:check(ident+' balanced '+e['event'],sum(p['debit'] for p in e['postings'])==sum(p['credit'] for p in e['postings']) and all(p['debit']>=0 and p['credit']>=0 for p in e['postings']))
    check(ident+' nonnegative asset carrying amounts',0<=removed<=retired<=g0 and b0>=removed and g0-retired-(b0-removed)>=d and unpaid>=0)
    # A feasible allocation also preserves all three reported gross asset classes.
    class_open=[r['values'][1] for r in tables['annual_ppe']['rows'][:3]]
    class_close=[r['values'][0] for r in tables['annual_ppe']['rows'][:3]]
    class_retired=[0,retired,0];class_added=[y-x+r for x,y,r in zip(class_open,class_close,class_retired)]
    check(ident+' gross classes can match',all(v>=0 for v in class_added) and sum(class_added)==added)
    balances={}
    for e in entries:
        for p in e['postings']:balances[p['account']]=balances.get(p['account'],0)+p['debit']-p['credit']
    end_g=g0+balances['ppe_cost'];end_b=b0-balances['accumulated_depreciation']
    delta_net=balances['ppe_cost']+balances['accumulated_depreciation'];delta_assets=delta_net+balances['cash']
    profit=-(balances['depreciation_expense']+balances['retirement_loss']);delta_liability=-balances['capital_payable']
    check(ident+' selected gross contra cash and expense reproduced',end_g==g1 and end_b==b1 and balances['cash']==-cash and balances['depreciation_expense']==d)
    check(ident+' incremental balance sheet reconciles',delta_assets==delta_liability+profit and delta_net==1965)
    histories.append(dict(id=ident,gross_additions=added,gross_retired=retired,accumulated_removed=removed,retired_carrying_loss=loss,unpaid_additions=unpaid,
        cash_paid=cash,expense=d,class_additions=class_added,journals=entries,statement_effects=dict(net_ppe=delta_net,cash=-cash,assets=delta_assets,liabilities=delta_liability,profit=profit,equity=profit,investing_cash=-cash),
        scope='Selected asset subsystem and gross classes only; not every Apple statement/lease/cohort constraint'))
check('repair histories differ but preserve selected endpoints',histories[0]['gross_additions']==10529 and histories[1]['gross_additions']==11529 and histories[0]['unpaid_additions']==1082 and histories[1]['unpaid_additions']==2082)
calcs=dict(units='USD millions',inventory=inventory,quarter_ppe=quarter,
    annual_shortcut=dict(gross_change=delta_g,accumulated_change=delta_b,cash_as_additions=cash,ppe_depreciation_point=d,required_gross_retired=naive_retired,required_accumulated_removed=removed,impossible_excess=gap,
        verdict='Infeasible under the conjunction: cash equals additions, displayed PP&E expense exact, only additions/depreciation/retirements; not an issuer error finding'),
    rounding=dict(gap_outer_envelope=[str(lower),str(upper)],assumption='Each million display rounded to nearest million and 8.2 billion to nearest 0.1 billion; unverified issuer policy, tie rule unknown',verdict='This conditional envelope remains strictly positive'),
    histories=histories,assumptions=['Displayed source centres used as exact illustrative inputs','Retire at beginning, depreciate surviving assets, acquire at year end; no other PP&E movements',
        'Cash payments all for current additions, no opening capital payables, no disposal proceeds; additional purchases unpaid',
        'All depreciation treated as expense in this subsystem; tax, OCI and owner flows omitted; no probability weights'],
    unknowns=['Causes of inventory cash-adjustment differences','Actual capital accrual/noncash/FX/reclassification/retirement histories','Asset and lot quantity, life, residual value and impairment memory','Full operative ASC applicability and actual company accounting admission'])
queries=[
 ('Q1','Inventory composition and dates','Return components/finished goods and both dated totals; no lot quantities inferred'),
 ('Q2','Inventory cash interpretation','Return indirect adjustment +215 and balance change -375 separately; residual -160 remains unallocated'),
 ('Q3','Annual PPE reconciliation','Gross and contra changes 4529/2564 give net1965; depreciation-specific8200 has coarse precision and differs from D&A11445'),
 ('Q4','Capital-payment shortcut','Reject the joint minimal book because accumulated depreciation removed5636 exceeds gross retired4918; no unique omitted cause follows'),
 ('Q5','Conditional repair','Retain both unpaid-addition histories and their journals/statement effects as authored witnesses, no actual transaction assertion'),
 ('Q6','Quarterly depreciation','Return gross/contra/net movements1487/1098/389 and cash2940/D&A3080; no PP&E-only quarter expense identified'),
 ('Q7','Lease overlap','Finance ROU belongs to PP&E, operating ROU to other noncurrent assets; full noncash ROU1.0bn is not all PP&E or cash capex'),
 ('Q8','Future cost and cash','Require lot/cohort, life, impairment, ownership and settlement facts; FIFO/straight-line alone do not identify forecasts')]
ledger=dict(plan='docs/plans/accounting-apple-assets-20261008.md',sources=prior['sources'],notes=notes,units=units,dependencies=deps,numeric_tables=tables,support_tables=support,
    ppe_depreciation=dict(literal=expense_line,values_millions=ppe_depreciation,display_quantum_millions=100,years=[2024,2023,2022]),
    queries=[dict(id=i,question=q,answer=a) for i,q,a in queries],
    coverage=dict(note_units=len(units),dependency_spans=len(deps),note_monetary_cells=24,whole_apple_package='open',outstanding_exhibit_targets=40,publication_date_repairs=0),
    acceptance=dict(author_interpretation='provisional',independent_reader='pending',human_acceptance='pending',full_readiness='not_ready'))
save('source-claim-supplement.json',ledger);save('asset-history.json',calcs)
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,
    output_hashes={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in ['source-claim-supplement.json','asset-history.json']},checks=checks,
    passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),wall_seconds=time.monotonic()-START)
save('evidence-checks.json',report)
print(json.dumps(dict(passed=report['passed'],failed=report['failed'],note_units=len(units),dependency_spans=len(deps),queries=len(queries))))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']]))
    raise SystemExit(1)
