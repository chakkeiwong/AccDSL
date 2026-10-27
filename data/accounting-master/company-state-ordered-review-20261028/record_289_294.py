"""Record actual pages289–294 and exact local arithmetic, without source promotion."""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import json,fitz
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0283-0288.json').read_text());j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
for n,a,b in [
 ('annual derivative OCI',-832-1337,-2169),('annual debt security OCI',5850+204,6054),('annual total OCI',395-2169+6054,4280),
 ('annual comprehensive income',93736+4280,98016),('annual accumulated OCI',-11452+4280,-7172),
 ('other equity movements',1423+12034-3993-1612-15218-95846,-103212),('annual equity bridge',62146+98016-103212,56950),
 ('annual capital',73812+1423+12034-3993,83276),('annual retained earnings',-214+93736-1612-15218-95846,-19154),
 ('annual closing equity components',83276-19154-7172,56950),('annual assets movement',364980-352583,12397),
 ('annual liabilities movement',308030-290437,17593),('annual equity movement',12397-17593,-5196),
 ('annual noncash adjustments',11445+11688-2266,20867),('annual working adjustments',-3788-1356-1046-11731+6020+15552,3651),
 ('annual CFO',93736+20867+3651,118254),('annual investing',-48656+51211+11135-9447-1308,2935),
 ('annual financing',3960-5441-15234-94949-9958-361,-121983),('annual cash movement',118254+2935-121983,-794),
 ('annual cash close',30737-794,29943),('opening cash population difference',30737-29965,772),('BS cash decrease',29965-29943,22),
 ('annual receivable residual',3902-3788,114),('annual inventory residual',955-1046,-91),('annual payable residual',6349-6020,329),
 ('annual repurchase difference',95846-94949,897),('annual withholding total',3993+1612,5605),('annual withholding residual',5605-5441,164),
 ('annual compensation difference',12034-11688,346),('annual dividend difference',15234-15218,16),
 ('quarter revenue',97960+26340,124300),('quarter operating income',124300-66025-15443,42832),
 ('quarter net income',42832-248-6254,36330),('quarter OCI',-625+2435-1427,383),('quarter comprehensive income',36330+383,36713),
 ('quarter other equity',3383-1891-1102-3819-23476,-26905),('quarter equity bridge',56950+36713-26905,66758),
 ('quarter assets',364980-20895,344085),('quarter liabilities',308030-30703,277327),('quarter equity change',-20895+30703,9808),
 ('quarter equity component change',7933+1492+383,9808),('quarter noncash adjustments',3080+3286-2009,4357),
 ('quarter working adjustments',3597+3166+215+939-6671-11998,-10752),('quarter CFO',36330+4357-10752,29935),
 ('quarter cash movement',29935+9792-39371,356),('quarter closing cash',29943+356,30299),
 ('combined comprehensive income',98016+36713,134729),('combined other equity',-103212-26905,-130117),
 ('combined CFO',118254+29935,148189),('combined CFI',2935+9792,12727),('combined CFF',-121983-39371,-161354),
 ('combined equity bridge',62146+134729-130117,66758),('combined cash bridge',30737+148189+12727-161354,30299),
 ('quarter payable residual',-7050+6671,-379),('lease gross payments',13518+1272,14790),('lease imputed interest',1984+376,2360),
 ('lease recognized liabilities',11534+896,12430),('operating lease reconciliation',13518-1984,11534),('finance lease reconciliation',1272-376,896),
 ('total lease reconciliation',14790-2360,12430),('ROU assets',10234+1069,11303),('current lease liabilities',1488+144,1632),
 ('current gross payment distinction',1991-1632,359),('uncommenced lease total',14790+849,15639)]:c(n,Q(a),Q(b))
c('deferred revenue residual',Q('13.2')-Q('12.8')+Q('3.7'),Q('4.1'))
c('rounding lower envelope',Q('13.15')-Q('12.85')+Q('3.65'),Q('3.95'))
c('rounding upper envelope',Q('13.25')-Q('12.75')+Q('3.75'),Q('4.25'))
for A,Rn,other in [('4.1','0','120.6'),('5.1','1','119.6')]:
 c('deferred close A='+A,Q('12.8')+Q(A)-Q('3.7')-Q(Rn),Q('13.2'))
 c('revenue sum A='+A,Q('3.7')+Q(Rn)+Q(other),Q('124.3'))
c('cash settled inflow',Q('120.6')+Q('4.1'),Q('124.7'))
c('receivable alternative asset change',Q('120.6')+Q('4.1'),Q('124.3')+Q('0.4'))
c('December recognition expectation',Q('13.2')*Q('.64'),Q('8.448'))
c('September recognition expectation',Q('12.8')*Q('.64'),Q('8.192'))
c('recognition bucket percentages',Q(64+25+9+2),Q(100))
c('15.639 within rounded15.6 envelope',Q('15.55')<=Q('15.639')<=Q('15.65'),True)
assert all(x['passed'] for x in checks),[x for x in checks if not x['passed']]
doc=fitz.open(ROOT/v['pdf'])
for n in range(289,295):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
with (D/'arithmetic-0289-0294.json').open('x') as f:json.dump(dict(checks=checks,count=len(checks),scope='Exact printed examples; external source authority not newly verified'),f,indent=2);f.write(chr(10))
r=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0289-0294',pages=list(range(289,295)),entry_state=prior['exit_state'],
 exit_state='Annual and interim income, equity and cash reconcile without identifying their underlying transactions. Deferred-revenue additions, releases, collection and dated recognition expectations remain distinct; two aggregate histories are not actual issuer contracts. Lease gross payments, discounted liabilities, current classification, ROU assets and uncommenced commitments also differ. The lease discussion now reaches the reported3.1% discount rate; continue its limitations and the remaining contractual payment details.',
 observations=[
 dict(pages=[289],finding='Annual net income appears in different bridges but is not added repeatedly. OCI flows into its accumulated balance; capital, retained earnings and AOCI reconcile separately. CFO retains each reported adjustment instead of replacing it with balance-sheet changes.',disposition='Income/equity/net-asset/cash arithmetic checked. Reported components and residual transactions are kept separate. Dense full page remains legible.'),
 dict(pages=[290],finding='Opening cash-flow population exceeds balance-sheet cash by772; it is not relabelled as the closing escrow. Equity repurchases, withholding, compensation and dividends differ from cash flows. The following quarter starts from annual stocks, not the prior-year comparative flows.',disposition='Arithmetic and time windows check. Source dash remains a source token; numerical reconciliation does not create an issuer-reported zero. Local prose clearly explains the change of period.'),
 dict(pages=[291],finding='Quarterly and combined15-month equity/cash bridges use common endpoints. Falling assets do not imply a loss. The text excludes summing EPS/weighted averages and says separately compatible notes need a compatible joint history. Revenue allocation introduces service cohorts before recognition timing.',disposition='All stated bridge totals check. Annual/interim and current/prior comparisons stay separate. Contract/cohort completeness remains unproved; source authority not newly checked.'),
 dict(pages=[292],finding='Principal/agent presentation, returns, tax remittances, product/geographic splits and timing prevent revenue from identifying gross collections. Equation28.21 derives net deferred movement4.1, not gross additions; its conditional rounded envelope is3.95–4.25.',disposition='Symbols, sign convention, units and rounding assumptions precede interpretation. Identity and bounds check. A heading uses unidentified to describe missing components, consistent with the argument.'),
 dict(pages=[293],finding='Two histories share ending deferred revenue13.2 and revenue124.3 but differ in new deferrals. Cash settlement versus a receivable produces different collections with the same asset increase. Recognition horizon percentages are expectations about dated balances, not history probabilities or collection dates.',disposition='Both histories and8.448/8.192 products check. Synthetic scope and omitted costs/taxes are explicit; no probability or actual issuer cash estimate is inferred. Table and captions are readable.'),
 dict(pages=[294],finding='Lease gross payments14790 less imputed interest2360 gives liability12430; ROU assets and current buckets answer different questions. Uncommenced849 produces a rounded-compatible15639 total but not a contract reconciliation or recognized liability increment.',disposition='Lease table arithmetic checks. Dated annual/interim warning and transition to commitments are clear. The weighted-average discount-rate qualification continues on the next page; do not close that argument here.')],
 equations_reviewed=['28.21','28.10 unnumbered annual/interim statement bridges','28.11 conditional recognition products','28.12 lease reconciliation'],
 equation_judgments=[dict(labels=['28.21'],role='deferred-revenue reconciliation identity',verdict='correct under stated signed movements; observations identify net movement only'),
 dict(labels=['28.10'],role='reported statement arithmetic and cumulative flow bridges',verdict='correct local sums; no underlying transaction identification'),
 dict(labels=['28.11'],role='conditional illustrative history and dated expectations',verdict='correct arithmetic; scope and rounding limits stated'),
 dict(labels=['28.12'],role='gross-payment versus discounted-liability measurement',verdict='correct table; future dates and valuation not identified')],
 arithmetic_artifact='arithmetic-0289-0294.json',source_claims_reviewed=[],render_binding='render-bindings-0289-0294.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0289-0294.json').open('x') as f:json.dump(r,f,indent=2);f.write(chr(10))
with (HERE/'inventory-before-0294.json').open('x') as f:json.dump(j,f,indent=2);f.write(chr(10))
print(json.dumps(dict(segment=r['id'],arithmetic_checks=len(checks))))

