"""Record the next actually read segment and independent local arithmetic."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0265-0270.json').read_text())
j=json.loads((D/prior['inventory']).read_text())
v=next(v for v in j['volumes'] if v['name']==prior['volume'])
pdf=ROOT/v['pdf']; assert sha256(pdf.read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def check(name, actual, expected):
    checks.append(dict(name=name,passed=actual==expected,actual=str(actual),expected=str(expected)))
check('opening assets',Q(60)+20+30+100-20,Q(190))
check('opening claims and equity',Q(20)+100+50+20,Q(190))
check('28.1 collections',Q(20)+260-35,Q(245))
check('28.2 purchases',Q(20)-30+165,Q(155))
check('28.3 payments',Q(20)+155-30,Q(145))
check('annual pretax income',Q(260)-165-42-11-5,Q(37))
check('annual profit',Q(37)*(1-Q(1,5)),Q('29.6'))
check('annual equity',Q(70)+Q('29.6')-9,Q('90.6'))
check('direct operating cash',Q(245)-145-42-5-Q('7.4'),Q('45.6'))
check('indirect operating cash',Q('29.6')+11-15+10+10,Q('45.6'))
check('cash movement',Q('45.6')-22-9,Q('14.6'))
check('closing cash',Q(60)+Q('14.6'),Q('74.6'))
check('June assets',Q(65)+20+25+85+2,Q(197))
check('June claims and equity',Q(25)+100+50+22,Q(197))
check('December assets',Q('74.6')+35+20+91,Q('220.6'))
check('December claims and equity',Q(30)+100+50+Q('40.6'),Q('220.6'))
check('original-to-corrected profit',Q(14)-10*(1-Q(1,5)),Q(6))
check('corrected equity',Q(70)+6-4,Q(72))
check('corrected second-half revenue',Q(260)-110,Q(150))
check('incompatible subtraction arithmetic only',Q(260)-120,Q(140))
check('next purchases units',Q(30)+8-4,Q(34))
check('next purchases cost',Q(34)*5,Q(170))
check('collections',Q(300)*Q(9,10)+10,Q(280))
check('next receivables',Q(35)+300-280,Q(55))
check('next payables',Q(30)+170-160,Q(40))
check('next depreciation',Q(10)+Q(10,5)+Q(12,12),Q(13))
for alpha in [Q(0),Q(1)]:
    interest=7-2*alpha; pretax=Q(300)-150-50-13-interest
    tax=pretax/5; profit=pretax-tax
    ocf=Q(280)-160-50-interest-tax
    cash=Q('74.6')+ocf-20-8
    equity=Q('90.6')+profit-8
    check('profit alpha='+str(alpha),profit,64+Q(8,5)*alpha)
    check('cash alpha='+str(alpha),cash,Q('93.6')+Q(8,5)*alpha)
    check('equity alpha='+str(alpha),equity,Q('146.6')+Q(8,5)*alpha)
    check('balance alpha='+str(alpha),cash+55+40+98,40+100+equity)
for rate, delta in [(Q(7,100),Q(2)),(Q(9,100),Q(4))]:
    check('28.4 interest slope rate='+str(rate),100*rate-5,delta)
    check('after-tax cash sensitivity rate='+str(rate),delta*Q(4,5),Q('1.6') if delta==2 else Q('3.2'))
check('purchased inventory units',Q(6)+14,Q(20))
check('purchased inventory value',Q(20)*5,Q(100))
check('delivered remaining inventory',Q(20)-15,Q(5))
assert all(c['passed'] for c in checks)
with (D/'arithmetic-0271-0276.json').open('x') as f:
    json.dump(dict(checks=checks,count=len(checks),scope='Independent local exact arithmetic; no new authority or forecast evidence'),f,indent=2);f.write('\n')
doc=fitz.open(pdf)
for n in range(271,277):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
r=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0271-0276',
    pages=list(range(271,277)),entry_state=prior['exit_state'],
    exit_state='Northstar identifies selected annual working-capital movements only under its explicit no-writeoff/no-acquisition scope, while debt composition remains a joint continuous family. Interim corrections change publication and ingestion views. The 2025 calculation is archival conditional on a corrected opening learned in March, not an investor forecast available in January. Whole event/state histories, actual source meaning and unresolved branches must survive every report.',
    observations=[
        dict(pages=[271],finding='The demonstrator must link three reporting dates, restatement and fixed/floating ambiguity to journals and statements. Synthetic and public cases have different evidence roles; forecast accuracy is explicitly deferred.',disposition='Retain the acceptance distinction. Sparse closing page is a chapter-end layout choice, not missing content or a mathematical defect.'),
        dict(pages=[272,273],finding='Northstar declares homogeneous goods, explicit units, absent sectors and half-year aggregation before supplying opening balances and movements. Delivery control, claim recognition, inventory cost, asset service dates and simplified tax are economically explained before inversion.',disposition='Retain the synthetic exclusions and source package. Opening assets190 and equity70 reconcile. Half-year ordering is a feasible aggregate history, not recovered invoice timing.'),
        dict(pages=[273],finding='Equations28.1–28.3 define C/P/S after specifying no writeoffs, acquisitions or currency effects; substitution yields collections245, purchases155 and supplier payments145. The immediately following debt relation preserves every mixture rather than mistaking one solver witness for identification.',disposition='All three equations and substitutions checked. Their uniqueness is explicitly conditional on the model. Keep financial dependence and missing real populations distinct.'),
        dict(pages=[274],finding='The opening/June/December statement table, annual profit, cash and equity bridges reconcile. Original revenue120 becomes110 after a correction; system ingestion can lag public availability, so an archive-based public query and an earlier system view differ.',disposition='Local statement and correction arithmetic checked. The annual-minus-interim140 is numerically valid but semantically incompatible across the stipulated revision groups; retain the required compatibility rule.'),
        dict(pages=[275],finding='All-fixed/all-floating future tables share the same alpha across cash, profit and equity; scenario drivers, asset service timing, tax and no new borrowing are stated. A marginal minimum cash paired with maximum equity has no supported joint company state.',disposition='Recalculated both endpoint profits/cash/equity and balance sheets; no forecast calibration is inferred. The explicit later x=1-alpha mapping prevents coordinate drift.'),
        dict(pages=[276],finding='Twenty-two proposed state/journal steps retain a common historical parent and future opening. Equation28.4 changes the floating-rate slope from2 at7% to4 at9%. The text then identifies the corrected March opening as unavailable for a January investor forecast and distinguishes missing values, unsupported tax and unquantified source language.',disposition='Rate and after-tax sensitivities checked exactly. The stated archival interpretation and no-publication-as-posting rule are clear. No new source authority is asserted; all six pages are legible.')],
    equations_reviewed=['28.1 receivables bridge','28.2 inventory bridge','28.3 payables bridge','28.4 floating-share interest relation'],
    equation_judgments=[dict(labels=['28.1','28.2','28.3'],role='accounting stock-flow identities under supplied exclusions',
        domain='same-year currency amounts; C collections, P purchases, S payments',
        interpretation='Annual flows are identified only after excluding other changes.',verdict='correct; substitutions245/155/145 checked'),
        dict(labels=['28.4'],role='exact supplied-rate scenario relation',domain='x floating share in[0,1], principal100, annual r',
        interpretation='Rate changes alter the debt-type exposure slope; after-tax effect uses stipulated20% tax.',verdict='correct under the supplied model; no predictive validation')],
    arithmetic_artifact='arithmetic-0271-0276.json',source_claims_reviewed=[],render_binding='render-bindings-0271-0276.json',
    independent_reader='pending',human_acceptance='pending')
with (D/'main-0271-0276.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps(dict(segment=r['id'],arithmetic_checks=len(checks))))
