"""Joined group-close and tax-carry segment, actually read in order."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0271-0276.json').read_text())
j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
pdf=ROOT/v['pdf'];assert sha256(pdf.read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(name,actual,expected):checks.append(dict(name=name,passed=actual==expected,actual=str(actual),expected=str(expected)))
c('parent opening assets',Q(500)+60+100+16+80+10,Q(766))
c('parent opening equity',Q(766)-40-100-4,Q(622))
c('group opening assets',Q(766)+100-80,Q(786))
c('group opening equity',Q(786)-144,Q(642))
c('bond cash split',Q(90)+10,Q(100))
c('estimated recovery asset',2*(Q(12)-3-1),Q(16))
c('returned inventory',min(2*(Q(12)-2),Q(20)),Q(20))
c('return net expense',Q(8)-(20-16),Q(4))
c('return taxable reduction',Q(40)-20+8,Q(28))
c('temporary difference',Q(28)-4,Q(24))
c('opening tax reversal',Q(10)-4,Q(6))
c('28.5 internal profit', (Q(140)-60)*(1-Q(2,5)),Q(48))
c('legal remaining inventory',Q(140)*Q(3,5),Q(84))
c('group remaining inventory',Q(60)*Q(3,5),Q(36))
c('cost elimination',Q(140)-48,Q(92))
c('inventory deferred asset',Q(48)/4,Q(12))
c('parent pretax H1',Q(80)-4-10-10,Q(56))
c('parent taxable H1',Q(56)-24,Q(32))
c('parent after tax H1',Q(56)-8-6,Q(42))
c('subsidiary after tax H1',(Q(84)-56)*Q(3,4),Q(21))
c('28.6 group H1',Q(42)+21-48+12,Q(27))
c('H1 NCI',Q(21)/5,Q('4.2'))
c('H1 assets',Q(511)+56+90+12,Q(669))
c('H1 group equity',Q('644.8')+Q('24.2'),Q(669))
c('28.7 NCI reduction',-(Q(9,10)-Q(8,10))*121,Q('-12.1'))
c('28.8 parent equity reduction',-(Q(20)-Q('12.1')),Q('-7.9'))
c('28.9 group H2',Q(10)-Q('2.5')+42-Q('10.5')+48-12,Q(75))
c('annual NCI',Q('4.2')+Q('31.5')/10,Q('7.35'))
c('annual parent profit',Q(102)-Q('7.35'),Q('94.65'))
c('28.10 parent closing equity',Q(622)+Q('94.65')-Q('7.9'),Q('708.75'))
c('28.11 closing NCI',Q(20)+Q('7.35')-Q('12.1'),Q('15.25'))
c('group closing equity',Q('708.75')+Q('15.25'),Q(724))
c('28.12 closing cash',Q(600)+(250-96)-(90+20),Q(644))
c('full-year profit',Q(136)-28-6,Q(102))
c('short-period parent loss',Q(20)-110-10,Q(-100))
c('short-period asset',Q(40)/4,Q(10))
c('short-period group equity',Q(574)+70+10-5,Q(649))
c('short-period loss',Q(-90)+15,Q(-75))
c('short-period parent EPS',(Q(-90)+Q(9,10)*15)/10,Q('-7.65'))
c('rate remeasurement benefit',Q(40)*(Q(3,10)-Q(1,4)),Q(2))
c('second-period deferred expense',Q(-2)+12-9,Q(1))
c('second-period parent profit',Q(60)-1,Q(59))
c('second-period group equity',Q(669)+50+9-6,Q(722))
c('second-period parent EPS',(Q(59)+Q(9,10)*14)/10,Q('7.16'))
c('final deferred expense',Q(20)*Q(3,10)+Q(10)*Q(3,10),Q(9))
c('final parent profit',Q(20)-9,Q(11))
c('final group profit',Q(11)+14,Q(25))
c('final parent EPS',(Q(11)+Q(9,10)*14)/10,Q('2.36'))
c('three-period cash bridge',Q(644)+240-150-17,Q(717))
c('three-period equity bridge',Q(724)+240-150-17-50,Q(747))
c('final group assets',Q(717)+30,Q(747))
c('final parent owners equity',Q(600)+10+Q('125.35')-Q('7.9'),Q('727.45'))
c('final NCI',Q(747)-Q('727.45'),Q('19.55'))
assert all(x['passed'] for x in checks)
with (D/'arithmetic-0277-0282.json').open('x') as f:json.dump(dict(checks=checks,count=len(checks),scope='Exact manuscript-example arithmetic only'),f,indent=2);f.write('\n')
doc=fitz.open(pdf)
for n in range(277,283):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
r=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0277-0282',pages=list(range(277,283)),
 entry_state=prior['exit_state'],exit_state='The joined parent/subsidiary close preserves shared cash, legal-book history, intragroup margin and tax, and dated NCI changes. Cash redemption separates prior accrued interest from principal without a new expense. Carrying balances into a short period and two later years keeps loss quantity, tax rate, expiry and support distinct; later estimates do not overwrite earlier reports or annualize a short-period result.',
 observations=[
 dict(pages=[277],finding='Exact retry after an uncertain acknowledgement precedes fresh-head comparison but follows original input/authorization validation. Distinct evidence, search progress and posting receipts have different owners. The joined example supplies two legal entities,80% ownership, cash/opening balances and a deliberately narrow tax law before calculations.',disposition='Preserve retry identity and no-durability inference. Opening parent/group balances check; historical regulatory source claims remain unreviewed in this read.'),
 dict(pages=[278],finding='Bond redemption separates90 original principal from10 previously accrued interest. The return example separates recovery asset16, inventory20, cash refunds40, handling8 and net expense4. Tax reduction28 versus book expense4 explains the deferred reversal6.',disposition='Exact arithmetic checked. The passage prevents current expense from being inferred from cash paid and avoids counting handling twice.'),
 dict(pages=[278,279],finding='Equation28.5 identifies residual intragroup margin48; Figure28.1 visually separates internal140 from external84. The group eliminates legal revenue/cost and recognizes a stipulated tax asset12. Downstream profit attribution remains with parent owners; NCI receives its share of subsidiary legal profit.',disposition='All margin, tax and H1 totals checked. The diagram is legible and contributes the legal/group boundary. No source applicability is newly certified.'),
 dict(pages=[279,280],finding='The1July purchase changes NCI carrying equity by12.1 and parent equity by7.9 without goodwill or gain. H1 profit keeps the old20% NCI share; H2 uses10%. Later sale releases48 margin and12 tax, producing75 H2 group profit and closing equity724.',disposition='Equations28.7–28.12 and annual cash/profit/NCI bridges check. The table distinguishes period flows from closing stocks and separately removes internal receipts/payments.'),
 dict(pages=[281],finding='The common-state implementation requires an uninterrupted receipt chain and recalculates consolidation from legal balances rather than adding the June adjustment twice. Carry closes income without earning profit again. The six-month loss recognizes a deferred asset only for the supported40 of loss100.',disposition='Retain explicit source/recognition premises, the no-cross-sector claim and short-period warning. Group assets/liabilities/equity649 and parent EPS-7.65 check.'),
 dict(pages=[282],finding='Tax-rate change remeasures supported loss40 before utilization; the decomposition-2+12-9=1 preserves rate benefit, consumed asset and newly supported loss. Final loss expiry consumes the remaining asset while the unused tax right expires. Later reports preserve earlier comparative estimates.',disposition='All local carry, EPS, cash717 and final equity747 calculations check. The six-page slice is readable without clipping. No new substantive defect found; general tax law and actual recovery evidence remain separate.')],
 equations_reviewed=['28.5 residual internal margin','28.6 H1 group profit','28.7–28.8 ownership transfer','28.9 H2 group profit','28.10–28.11 closing owner equity','28.12 cash bridge','28.7.6 unnumbered tax-carry identities'],
 equation_judgments=[dict(labels=['28.5'],role='exact supplied-lot relation',verdict='correct; s external-sold fraction and T/C legal/original cost are defined'),
 dict(labels=['28.6','28.7','28.8','28.9','28.10','28.11','28.12'],role='accounting reconciliation under supplied ownership/tax/classification',verdict='correct local arithmetic; source authority not newly inspected'),
 dict(labels=['28.7.6 tax carry'],role='rate/quantity/expiry accounting decomposition',verdict='correct with supplied recovery evidence and dated tax laws; no backdated restatement')],
 arithmetic_artifact='arithmetic-0277-0282.json',source_claims_reviewed=[],render_binding='render-bindings-0277-0282.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0277-0282.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps(dict(segment=r['id'],arithmetic_checks=len(checks))))
