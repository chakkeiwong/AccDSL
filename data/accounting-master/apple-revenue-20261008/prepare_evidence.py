"""Inspect retained revenue notes and check limited documentary consequences."""
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
if (OUT/"completion.json").exists():raise SystemExit("Closed unit")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save=lambda n,d:(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
checks=[];inputs={}


def check(name,passed,detail=None):
    checks.append(dict(name=name,passed=bool(passed),detail=detail))


def norm(t):return re.sub(r"\s+","",t).replace("®","")


prior_path=ROOT/"docs/design/cases/apple/continuation-20261007/case-supplement-v1.json"
prior=json.loads(prior_path.read_text());inputs[str(prior_path.relative_to(ROOT))]=sha(prior_path)
texts={}
for key in ["annual","interim"]:
    src=prior["sources"][key]
    for pkey,hkey in [("original_path","original_sha256"),("extraction_path","extraction_sha256")]:
        p=ROOT/src[pkey];inputs[src[pkey]]=sha(p);check(key+" "+pkey+" integrity",sha(p)==src[hkey])
    texts[key]=(ROOT/src["extraction_path"]).read_text()

# Every character of each retained note span is assigned to one unit. This is
# a declared coverage population, not a machine certification of interpretation.
annual_specs=[
 ("heading","Note 2 – Revenue","heading","Revenue note identity; no substantive financial claim","None","No numeric consequence"),
 ("control","The Company recognizes revenue at the amount","policy","Recognise expected entitlement when control transfers; most Products transfer on shipment, Services over delivery; collection follows shortly, with no quantified lag","Contract-specific control/payment terms","Revenue timing differs from receipts; do not turn generally or short period into a universal date"),
 ("reductions","The Company records reductions to Products net sales","estimate","Returns, price protection and incentives reduce Products net sales using expectations/history","Return and incentive estimates, settlement/refund terms","Reported Products is net; revenue alone does not identify units shipped or refund cash"),
 ("ssp","For arrangements with multiple performance obligations","allocation","Allocate across distinct promises by relative SSP; observable prices preferred, otherwise entity estimates with stated factors","Contract promises, observable/estimated SSP and allocation inputs","Cannot infer the bundled-service share or standalone prices from product sales totals"),
 ("bundles","The Company has identified the performance obligations regularly","policy","iPhone/Mac/iPad include delivered hardware/software plus future product-related services; discounts use relative SSP; service portion released straight-line over estimated period","Allocation and cohort service life; do not apply to every service contract","Preserve hardware delivery and service cohorts separately; change in estimated service period affects recognition path"),
 ("unbilled","For certain long-term service arrangements","unquantified_obligation","Certain undelivered services carry no current right to bill; related consideration entirely relates to undelivered services, not recognised or quantified here","Affected contracts and amount","Unknown consideration is not zero and is not identified by the deferred-revenue balance"),
 ("gross_net","For the sale of third-party products","presentation","Gross revenue where control obtained; App Store third-party applications net commission only, per source control assessment","Transaction populations and gross billed/commission amounts","Do not count gross customer billings as Apple revenue or infer billings from commissions"),
 ("product_table","Net sales disaggregated by significant products and services","numeric_table","Five product/service rows partition reported total in each of three fiscal-year columns","No product-by-region joint table supplied here","Sum rows within a column; do not add segment totals to this partition"),
 ("bundle_in_services","(1)   Services net sales include","classification","Services net sales already includes amortisation of deferred bundled-service value","Amount of that component","Do not add it again to total revenue or classify all product cash as current Products revenue"),
 ("opening_release","Total net sales include $7.7 billion","cohort_flow","2024/2023/2022 revenue from respective opening deferred balances is 7.7/8.2/7.5 billion; included in total net sales","New-origin releases and other movements","Opening-cohort release is not all revenue released from deferred revenue during a period"),
 ("segment_qualification","The Company’s proportion of net sales","dimension_qualification","Source mix generally similar by segment except moderately higher iPhone proportion in Greater China","Exact joint product/region amounts","Do not infer a proportional product-by-region matrix from two marginal tables"),
 ("balance_expectation","As of September 28, 2024 and September 30, 2023","balance_and_expectation","Total deferred revenue 12.8/12.1 billion at named dates; expected realisation of 2024 balance 64/25/9/2 percent in four elapsed-time buckets","Cohorts, exact timing, estimates, future additions and collection status","Rounded dated recognition expectation is not total future revenue, a probability law or cash schedule"),
]
interim_specs=[
 ("heading","Note 2 –","heading","Interim revenue note identity","None","No numeric consequence"),
 ("product_table","Net sales disaggregated by significant products and services","numeric_table","Five rows partition total revenue for quarters ended 28 Dec 2024 and 30 Dec 2023","Joint product/region values absent","Compare like fiscal-quarter populations; no annual-minus-next-quarter subtraction"),
 ("opening_release","Total net sales include $","cohort_flow","3.7/3.5 billion from respective opening deferred balances is included in quarter revenue","New-origin releases and other movements","3.7 constrains opening cohort only; missing movement terms remain unidentified"),
 ("segment_qualification","The Company’s proportion of net sales","dimension_qualification","Generally consistent source mix, except higher iPhone proportion in Greater China","Exact joint matrix","Do not allocate segment totals mechanically by overall product shares"),
 ("balance_expectation","As of December","balance_and_expectation","13.2/12.8 billion total deferred revenue; December expectation 64/25/9/2, separately dated from September","New contracts, revisions and collection status","Equal percentage vectors do not prove unchanged cohorts, cash dates or a stationary recognition process"),
]
units=[];notes={}
for key,specs in [("annual",annual_specs),("interim",interim_specs)]:
    old=next(n["source"] for n in prior["note_dispositions"] if n["note_id"]==key+".note.2")
    full=texts[key];note=full[old["start"]:old["end"]]
    check(key+" note source span intact",note==old["quote"])
    positions=[note.index(spec[1]) for spec in specs]
    check(key+" unit order and full coverage",positions[0]==0 and positions==sorted(set(positions)))
    positions.append(len(note));rebuilt=""
    for i,spec in enumerate(specs):
        ident,marker,kind,claim,unknown,consequence=spec;start,end=positions[i:i+2];quote=note[start:end];rebuilt+=quote
        units.append(dict(id=key+".revenue."+ident,source=key,kind=kind,source_start=old["start"]+start,source_end=old["start"]+end,
                     offset_unit="Unicode code points in pinned extraction",quote=quote,span_sha256=hashlib.sha256(quote.encode()).hexdigest(),
                     interpretation=claim,missing_facts=unknown,query_consequence=consequence,
                     status="author_interpretation; human admission pending",dependencies=["annual.note.1","annual.note.13"] if key=="annual" else ["interim.note.1","annual.note.2","interim.note.10"]))
    check(key+" segmented text exactly reconstructs full retained Note 2",rebuilt==note)
    (OUT/"sources"/(key+"-note2.txt")).write_text(note)
    notes[key]=dict(source=old,unit_ids=[u["id"] for u in units if u["source"]==key],coverage="All characters assigned; includes heading, tables and footer. Interpretations are bounded author work")

annual_note=notes["annual"]["source"]["quote"];interim_note=notes["interim"]["source"]["quote"]
annual_table=next(u["quote"] for u in units if u["id"]=="annual.revenue.product_table")
labels=["iPhone","Mac","iPad","Wearables, Home and Accessories","Services","Total net sales"]
tables={"annual":{},"interim":{}}
for label in labels:
    line=next(l for l in annual_table.splitlines() if l.strip().startswith(label))
    vals=[int(v.replace(",","")) for v in re.findall(r"\d{1,3}(?:,\d{3})+",line)]
    check("annual three columns "+label,len(vals)==3)
    tables["annual"][label]=vals
soup=BeautifulSoup((ROOT/prior["sources"]["interim"]["original_path"]).read_bytes(),"html.parser")
table=next(t for t in soup.find_all("table") if "69,138" in t.get_text() and "Change" not in t.get_text())
for label in labels:
    tr=next(r for r in table.find_all("tr") if r.get_text(' ',strip=True).startswith(label))
    vals=[int(v.replace(",","")) for v in re.findall(r"\d{1,3}(?:,\d{3})+",tr.get_text(' ',strip=True))]
    check("interim two columns "+label,len(vals)==2)
    tables["interim"][label]=vals
for key,years in [("annual",["FY2024","FY2023","FY2022"]),("interim",["FY2025Q1","FY2024Q1"])]:
    for i,year in enumerate(years):
        check("product partition "+year,sum(tables[key][l][i] for l in labels[:-1])==tables[key]["Total net sales"][i])
        check("numeric cells in extracted note "+year,all(str(tables[key][l][i]).replace(",","") in norm(notes[key]["source"]["quote"]).replace(",","") for l in labels))

ann_pdf=fitz.open(ROOT/prior["sources"]["annual"]["original_path"])
for i,(label,vals) in enumerate(tables["annual"].items()):
    check("annual row original PDF "+label,all(f"{v:,}" in ann_pdf[37].get_text() for v in vals))
statement_table=next(t for t in soup.find_all("table") if 'Deferred revenue' in t.get_text() and '8,461' in t.get_text())
tr=next(r for r in statement_table.find_all('tr') if r.get_text(' ',strip=True).startswith('Deferred revenue'))
currents=[int(v.replace(',','')) for v in re.findall(r"\d{1,3}(?:,\d{3})+",tr.get_text(' ',strip=True))]
check("current deferred balances and total are distinct",currents==[8461,8249] and 'Current liabilities:' in statement_table.get_text())
check("annual current balance agrees with interim comparative",'8,249' in ann_pdf[33].get_text())

dependency_specs=[
 ("annual","basis","The consolidated financial statements include the accounts of Apple Inc.","\n\nRevenue\n","Consolidated U.S.-GAAP context and fiscal 52/53-week calendar; do not replace with calendar year"),
 ("annual","taxes","The Company records revenue net of taxes collected","\n\nShare-Based Compensation","Tax amounts remitted to governments are not net sales; revenue does not establish gross customer cash"),
 ("annual","segment","The Company manages its business primarily on a geographic basis.","\fThe following table shows information by reportable segment","Geographic scope and general customer-location attribution; product and geographic tables are overlapping views, not additive sales"),
 ("interim","basis","The condensed consolidated financial statements include the accounts of Apple Inc.","Note 2 –","Interim statements are unaudited, refer to annual notes, use U.S. GAAP and fiscal weeks"),
]
dependencies=[]
for src,ident,start,end,meaning in dependency_specs:
    text=texts[src];s=text.index(start);e=text.index(end,s);quote=text[s:e]
    dependencies.append(dict(id=src+'.'+ident,source=src,start=s,end=e,quote=quote,interpretation=meaning))
# Read geographic revenue tables only as a cross-reference check, not full segment-note formalisation.
seg_annual=texts['annual'].split('The following table shows information by reportable segment for 2024',1)[1].split('A reconciliation',1)[0]
seg_rows=[]
for line in seg_annual.splitlines():
    if 'Net sales' in line:seg_rows.append([int(v.replace(',','')) for v in re.findall(r'\d{1,3}(?:,\d{3})+',line)])
seg_interim=next(t for t in soup.find_all('table') if '52,648' in t.get_text() and 'Operating income' in t.get_text())
qseg=[]
for r in seg_interim.find_all('tr'):
    if r.get_text(' ',strip=True).startswith('Net sales'):qseg.append([int(v.replace(',','')) for v in re.findall(r'\d{1,3}(?:,\d{3})+',r.get_text())])
check('five geographic rows per table',len(seg_rows)==len(qseg)==5)
for key,rows in [('annual',seg_rows),('interim',qseg)]:
    check(key+' geographic sums equal product totals',[sum(x[i] for x in rows) for i in range(len(rows[0]))]==tables[key]['Total net sales'])

def require(text,phrase,name):check(name,norm(phrase) in norm(text))
require(annual_note,'total deferred revenue of $12.8 billion and $12.1 billion','annual total balances anchored')
require(interim_note,'total deferred revenue of $13.2 billion and $12.8 billion','interim total balances anchored')
require(interim_note,'$3.7 billion of revenue recognized','opening-cohort release anchored')
require(interim_note,'64% of total deferred revenue to be realized in less than a year, 25% within one-to-two years, 9% within two-to-three years and 2% in greater than three years','dated percentage scope anchored')
require(annual_note,'does not disclose amounts, related to these undelivered services','unquantified service amount anchored')
require(annual_note,'only the commission it retains','net-commission boundary anchored')

opening,closing,opening_release=F('12.8'),F('13.2'),F('3.7')
residual=closing-opening+opening_release
half_unit=F('0.05');lower=(closing-half_unit)-(opening+half_unit)+(opening_release-half_unit);upper=(closing+half_unit)-(opening-half_unit)+(opening_release+half_unit)
check('residual is net new deferrals less new releases plus other movements',residual==F('4.1'))
check('conditional rounding envelope',lower==F('3.95') and upper==F('4.25'))
weights=[F(64,100),F(25,100),F(9,100),F(2,100)]
check('recognition buckets partition percentage total',sum(weights)==1)
buckets=[]
for date,balance in [('2024-09-28',opening),('2024-12-28',closing)]:
    vals=[balance*w for w in weights]
    check('display-centre bucket sum '+date,sum(vals)==balance)
    buckets.append(dict(as_of=date,reported_total_billion=str(balance),percentages=[64,25,9,2],indicative_amounts_billion=[str(v) for v in vals],
                  labels=['less than a year','one-to-two years','two-to-three years','greater than three years'],
                  meaning='Issuer expectation for recognition of that dated balance, not probability weights, future total revenue or cash due dates'))
witnesses=[]
revenue=F(tables['interim']['Total net sales'][0],1000)
for ident,new_release in [('H1',F(0)),('H2',F(1))]:
    addition=residual+new_release;other_revenue=revenue-opening_release-new_release
    check(ident+' same deferred balance',opening+addition-opening_release-new_release==closing)
    check(ident+' same total revenue',opening_release+new_release+other_revenue==revenue)
    check(ident+' nonnegative new-origin outstanding',addition-new_release>=0)
    for collection_mode in ['cash','receivable']:
        cash=other_revenue+(addition if collection_mode=='cash' else 0)
        receivable=addition if collection_mode=='receivable' else F(0)
        check(ident+' revenue-side journal invariant '+collection_mode,cash+receivable==(closing-opening)+revenue)
        witnesses.append(dict(history=ident,consideration_on_new_deferral=collection_mode,new_deferrals_billion=str(addition),new_origin_release_billion=str(new_release),
             opening_release_billion=str(opening_release),other_recognised_revenue_billion=str(other_revenue),closing_deferred_billion=str(closing),
             conditional_revenue_side_cash_increase_billion=str(cash),conditional_receivable_increase_billion=str(receivable),
             scope='Author-constructed revenue/deferred-balance subsystem only; other recognised revenue assumed cash-settled; no costs/tax/FX/refunds/other movements. Not a fit to every Apple statement or actual contracts.'))

queries=[
 dict(id='total_vs_current',question='What deferred revenue did Apple report at 28 December 2024?',result={'total_USD_billion_rounded':'13.2','current_USD_million':8461},consequence='Select concept and precision; never substitute current for total'),
 dict(id='cash_from_residual',question='Did Apple collect 4.1 billion of new advances?',result='not_identified',consequence='4.1 is A minus new-origin release plus other movements at displayed centres; no collection fact follows'),
 dict(id='opening_release',question='Is 3.7 billion all quarterly deferred-revenue recognition?',result='not_identified',consequence='Only opening-balance origin is specified; preserve unknown new-origin release'),
 dict(id='recognition_expectation',question='How much of December deferred revenue is expected in less than a year?',result='Indicative 8.448 billion from rounded inputs',consequence='Expectation, not fixed cash due or all future revenue; retain December anchor and unknown intra-bucket timing'),
 dict(id='unbilled_consideration',question='What is the value of the excluded long-term undelivered services?',result='unquantified',consequence='Keep obligation/amount unknown; do not substitute zero or total deferred revenue'),
 dict(id='product_region',question='Can Greater China iPhone revenue be obtained by multiplying total iPhone share by segment revenue?',result='not_identified',consequence='Two marginal tables plus qualitative exception do not identify the joint amount'),
 dict(id='appstore_gross',question='Does Services revenue measure customer gross App Store spending?',result='wrong_target',consequence='Source describes retained net commission for these transactions; gross billings require separate facts'),
 dict(id='invalid_time_subtraction',question='Can FY2024 revenue minus FY2025Q1 revenue give FY2024 last nine months?',result='incompatible_periods',consequence='The December 2024 quarter begins after the September 2024 year end'),
]
save('source-claim-supplement.json',dict(sources={k:prior['sources'][k] for k in ['annual','interim']},notes=notes,units=units,dependencies=dependencies,
     selected_segment_revenue_rows=dict(annual=seg_rows,interim=qseg),coverage=dict(annual_note_units=len(annual_specs),interim_note_units=len(interim_specs),
     full_character_partition=True,semantic_review='bounded author interpretation; human admission pending',whole_apple_package='open',outstanding_exhibit_targets=40),
     source_boundary='Issuer accounting assertions, not independent ASC authority or compliance judgement'))
save('revenue-history.json',dict(tables_USD_million=tables,current_deferred_USD_million=dict(dec2024=currents[0],sep2024=currents[1]),
     identity='D1 = D0 + A - R_open - R_new + M; M is signed other movements, not an inferred journal',
     point_inputs_USD_billion=dict(D0='12.8',D1='13.2',R_open='3.7'),residual_USD_billion=str(residual),
     rounding=dict(status='conditional sensitivity, not reported issuer rounding policy',assumption='Each total/release rounded to nearest 0.1 billion; closed outer envelopes avoid an unverified tie rule',envelope_USD_billion=[str(lower),str(upper)]),
     expectations=buckets,witnesses=witnesses,queries=queries,
     evidence_classes=dict(reported='Source tables, note amounts/policies and dated expectations',derived='Sums, residual and conditional precision envelope',authored='Two movement histories with cash/receivable alternatives; no weighting'),
     execution='Deterministic document arithmetic only; no production/runtime implementation'))
outputs={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in ['source-claim-supplement.json','revenue-history.json']}
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,output_hashes=outputs,
            checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),wall_seconds=time.monotonic()-START)
save('evidence-checks.json',report)
print(json.dumps(dict(passed=report['passed'],failed=report['failed'],note_units=len(units),numeric_cells=sum(len(v) for t in tables.values() for v in t.values()),queries=len(queries),witnesses=len(witnesses))))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']],ensure_ascii=False));raise SystemExit(1)
