"""Record the actually rendered/read sector close and historical Apple example."""
from fractions import Fraction as Q
from hashlib import sha256
from datetime import date
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0277-0282.json').read_text())
j=json.loads((D/prior['inventory']).read_text())
v=next(x for x in j['volumes'] if x['name']==prior['volume'])
pdf=ROOT/v['pdf'];assert sha256(pdf.read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(name,actual,expected):
    checks.append(dict(name=name,passed=actual==expected,actual=str(actual),expected=str(expected)))
c('alternative recovery terminal equity',Q(724)-85+74+34,Q(747))
c('parent opening equity',Q(500)+80+80-6,Q(654))
c('group opening cash',Q(500)+300+200-20,Q(980))
c('group opening liabilities',Q(200)+100+6-20,Q(286))
c('group opening equity',Q(980)-286,Q(694))
c('28.13 first loan carry',Q(100)*Q('1.1')-55,Q(55))
c('28.14 final loan carry',Q(55)*Q('1.1')-Q('60.5'),Q(0))
c('loan principal receipts',Q(50)+52,Q(102))
c('lifetime loan income',Q(5)+Q('8.5')+2,Q('15.5'))
c('insurance first liability',Q(100)+10-55,Q(55))
c('insurance final liability',Q(55)-5-50,Q(0))
c('28.15 first guarantee',max(Q(4),Q(7)),Q(7))
c('28.15 second guarantee',max(Q(2),Q(3)),Q(3))
c('first guarantee profit',Q(2)-(7-4),Q(-1))
c('second guarantee profit',Q(2)-((3-2)-(7-4)),Q(4))
c('bank first cash',Q(300)-102+2+55-2,Q(253))
c('bank second cash',Q(253)+Q('60.5')-Q('1.1'),Q('312.4'))
c('bank first equity',Q(253)+55-200,Q(108))
c('bank second equity',Q('312.4')-200,Q('112.4'))
c('insurer first equity',Q(150)+1-55,Q(96))
c('insurer second cash',Q(150)-45-1,Q(104))
c('parent second tax',Q(4-1)/5,Q('0.6'))
c('parent second profit',Q(4)-Q('0.6')-Q('0.2'),Q('3.2'))
c('28.16 bank OCI first',Q(100)*Q('0.2')+8*Q('0.1'),Q('20.8'))
c('28.16 insurer OCI first',Q(100)*Q('0.2')-4*Q('0.1'),Q('19.6'))
c('group profit first',Q(8-4)*Q('1.1')-Q('0.8'),Q('3.6'))
c('ownership NCI reduction',Q(108)*Q('1.2')/10,Q('12.96'))
c('ownership parent equity reduction',Q(15)-Q('12.96'),Q('2.04'))
c('28.17 NCI first',Q(40)+Q('0.88')+Q('8.08')-Q('12.96'),Q(36))
c('28.18 parent equity first',Q(654)+Q('3.6')-Q('0.88')+Q('40.4')-Q('8.08')-Q('2.04'),Q(687))
c('independent equity bridge first',Q(694)+Q('3.6')+Q('40.4')-15,Q(723))
c('bank OCI second',Q(108)*Q('0.1')+Q('4.4')*Q('0.05'),Q('11.02'))
c('insurer OCI second',Q(96)*Q('0.1')+8*Q('0.05'),Q(10))
c('group profit second',Q('5.5')+10+Q('3.2'),Q('18.7'))
c('NCI second profit',Q('5.5')/10+Q(10)/5,Q('2.55'))
c('NCI second OCI',Q('11.02')/10+Q(10)/5,Q('3.102'))
c('NCI closing',Q(36)+Q('2.55')+Q('3.102'),Q('41.652'))
c('parent closing',Q(687)+Q('18.7')-Q('2.55')+Q('21.02')-Q('3.102'),Q('721.068'))
c('group cash first',Q(485)+(Q(253)+150-20)*Q('1.2'),Q('944.6'))
c('group assets first',Q('944.6')+66+Q('1.4'),Q(1012))
c('group liabilities first',(Q(200)+55-20)*Q('1.2')+7,Q(289))
c('group cash second',Q('484.4')+(Q('312.4')+104-20)*Q('1.3'),Q('999.72'))
c('group liabilities second',(Q(200)-20)*Q('1.3')+3,Q(237))
c('group equity second',Q('999.72')-237,Q('762.72'))
c('28.19 first CFO',Q(-100)+(Q(55)-2-50)*Q('1.1'),Q('-96.7'))
c('first bank cash FX',Q(300)*Q('0.2')-100*Q('0.2')+53*Q('0.1'),Q('45.3'))
c('first insurer cash FX',Q(200)*Q('0.2')-50*Q('0.1'),Q(35))
c('first group cash FX',Q('45.3')+35-4,Q('76.3'))
c('28.20 first cash bridge',Q(980)-Q('96.7')-15+Q('76.3'),Q('944.6'))
c('second CFO',(Q('60.5')-Q('1.1')-45-1)*Q('1.25')-Q('0.6'),Q('16.15'))
c('second bank cash FX',Q(253)*Q('0.1')+(Q('60.5')-Q('1.1'))*Q('0.05'),Q('28.27'))
c('second insurer cash FX',Q(150)*Q('0.1')-46*Q('0.05'),Q('12.7'))
c('second group cash FX',Q('28.27')+Q('12.7')-2,Q('38.97'))
c('second cash bridge',Q('944.6')+Q('16.15')+Q('38.97'),Q('999.72'))
c('annual debt carry',Q(97341)-321-358,Q(96662))
c('annual debt components',Q(10912)+85750,Q(96662))
c('interim debt components',Q(10848)+83956,Q(94804))
c('indicative unrestricted remainder',Q(29943)-2600,Q(27343))
c('debt movement residual',Q(96662)-1009-94804,Q(849))
c('interim cash movement',Q(29935)+9792-39371,Q(356))
c('interim cash bridge',Q(29943)+356,Q(30299))
c('euro annual coupon',Q(1250)*Q('0.00875'),Q('10.9375'))
c('euro final scheduled payment',Q(1250)+Q('10.9375'),Q('1260.9375'))
c('May maturity weekday',date(2025,5,24).weekday(),5)
c('November maturity weekday',date(2025,11,15).weekday(),5)
c('conditional stress',Q('0.02')*Q(13,52)*14575,Q('72.875'))
c('conditional cash',Q(30299)-Q('72.875'),Q('30226.125'))
c('conditional assets',Q(344085)-Q('72.875'),Q('344012.125'))
c('conditional equity',Q(66758)-Q('72.875'),Q('66685.125'))
c('conditional balance',Q('344012.125')-277327,Q('66685.125'))
c('annual revenue',Q(294866)+96169,Q(391035))
c('annual gross margin',Q(391035)-185233-25119,Q(180683))
c('annual operating income',Q(180683)-31370-26097,Q(123216))
c('annual net income',Q(123216)+269-29749,Q(93736))
assert all(x['passed'] for x in checks),[x for x in checks if not x['passed']]
with (D/'arithmetic-0283-0288.json').open('x') as f:
    json.dump(dict(checks=checks,count=len(checks),scope='Exact manuscript-example arithmetic; external-source authority not newly verified'),f,indent=2);f.write('\n')
doc=fitz.open(pdf)
for n in range(283,289):
    assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
r=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0283-0288',pages=list(range(283,289)),
 entry_state=prior['exit_state'],
 exit_state='The sector close distinguishes legal taxpayers, dated ownership and cash FX from translation OCI. Historical Apple reported totals constrain measurements but do not identify legal instruments, spendable cash, settlement dates or exact floating exposure. The conditional13-week stress preserves statement effects. The next section starts connecting annual operations, equity and cash through the single net-income amount93736; the continuation must finish that argument.',
 observations=[
 dict(pages=[283],finding='Alternative supported-recovery recognition changes intermediate equity and profit but reaches the same final747; missing evidence remains unresolved. The sector example supplies separate books, currencies, ownership, dates and an identified internal deposit before its group opening.',disposition='Opening and terminal arithmetic checked. Retain separate taxpayer and offset premises; source applicability is not newly checked.'),
 dict(pages=[283,284],finding='Loan principal, coupons and fee differ from EIR income. Insurance release is not another payment. External guarantee measurement uses the higher of unamortized initial amount and allowance. Legal tax losses do not pool taxpayers or create cash refunds.',disposition='Loan, guarantee, tax and legal balances check. ECL, recovery support and scope remain supplied premises.'),
 dict(pages=[285],finding='Equation28.16 derives OCI from translated closing equity less translated opening equity and profit. The10% bank purchase follows first-period results, removing12.96 NCI for15 cash and changing only later attribution.',disposition='Derivation, NCI timing, parent equity and independent group bridge check. Dates and quantities are explained before use.'),
 dict(pages=[285,286],finding='Cash FX preserves dated cash origins and eliminates the internal deposit effect. It differs from OCI because OCI includes noncash net assets. Constant-FX and no-purchase comparisons isolate the mechanisms.',disposition='Cash944.6/999.72 and equity762.72 reconcile. This reading does not execute every sector refusal control or establish general implementation correctness.'),
 dict(pages=[286,287],finding='Historical Apple discussion distinguishes principal/carrying/fair value, annual/interim, consolidated/issuer and rounded/exact quantities. The849 debt residual remains unidentified. Restricted escrow and fiscal maturity buckets affect liquidity and timing separately.',disposition='Printed arithmetic checks. The recovery summary wrote investing inflow7992; the actual manuscript correctly prints9792 and reconciles356. The summary is corrected here, with no manuscript defect inferred. No external-source reading is claimed.'),
 dict(pages=[287,288],finding='Euro scheduled payments remain conditional on holdings and indenture terms; weekend settlement is unresolved. The72.875 stress explicitly assumes effective exposure and frozen statements. Annual net income starts a five-statement argument that continues on the next page.',disposition='Payments, weekend dates, stress postings and income arithmetic check. Pages are legible without clipping. Preserve the historical-source and conditional-exposure limits; no new authority or forecast claim.')],
 equations_reviewed=['28.13','28.14','28.15','28.16','28.17','28.18','28.19','28.20','28.9 unnumbered debt/cash/stress relations'],
 equation_judgments=[
 dict(labels=['28.13','28.14','28.15'],role='supplied loan and guarantee measurements',verdict='correct local calculation; input validity not newly certified'),
 dict(labels=['28.16'],role='translation identity without capital flows',verdict='correct expansion of(E+p)rc-Er0-pre under stated assumptions'),
 dict(labels=['28.17','28.18','28.19','28.20'],role='dated ownership and cash reconciliation',verdict='correct under supplied rates, ownership order and classifications'),
 dict(labels=['28.9'],role='reported-amount arithmetic and conditional stress',verdict='correct; unknown exposure, debt movements and settlement dependencies preserved')],
 arithmetic_artifact='arithmetic-0283-0288.json',source_claims_reviewed=[],render_binding='render-bindings-0283-0288.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0283-0288.json').open('x') as f:
    json.dump(r,f,indent=2);f.write('\n')
print(json.dumps(dict(segment=r['id'],arithmetic_checks=len(checks))))
