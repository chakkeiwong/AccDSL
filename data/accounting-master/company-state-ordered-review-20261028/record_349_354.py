"""Ordered individual reading349–354 and exact local arithmetic controls."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0343-0348.json').read_text());j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
def rounded(x):
 sign=-1 if x<0 else 1;x=abs(x)*100;return sign*Q((x+Q(1,2)).numerator//(x+Q(1,2)).denominator,100)
w=Q(3,5);mean=w*5+(1-w)*7
c('illustrative fixed/floating mean',mean,Q(29,5))
points=[(Q(4),w/2),(Q(6),w/2),(Q(5),(1-w)/2),(Q(9),(1-w)/2)]
variance=sum(m*(x-mean)**2 for x,m in points)
c('total variance local finite control',variance,w*1+(1-w)*4+w*(1-w)*(5-7)**2)
c('total variance value',variance,Q(79,25))
c('posterior fixed unnormalized',Q(3,5)*Q(1,5),Q(3,25))
c('posterior floating unnormalized',Q(2,5)*Q(4,5),Q(8,25))
c('posterior normalizer',Q(3,25)+Q(8,25),Q(11,25))
c('posterior fixed',Q(3,25)/Q(11,25),Q(3,11))
c('posterior floating',Q(8,25)/Q(11,25),Q(8,11))
c('known mass not whole mass',Q(3,5)<1,True)
c('failed branch retains complement',1-Q(3,5),Q(2,5))
low=Q(199,2);high=Q(201,2)
c('rounded lower interest',low*Q(1,20),Q(199,40))
c('rounded upper supremum',high*Q(7,100),Q(1407,200))
c('all-floating low total',low*Q(7,100),Q(1393,200))
c('historic interest lower within interval',Q(9,2)<=Q(1,20)*low<Q(11,2),True)
c('historic upper total still below interest cap',Q(1,20)*high<Q(11,2),True)
c('cent-grid maximum',Q(10049,100)*Q(7,100),Q(70343,10000))
c('real-only value omitted by cent maximum',Q(70343,10000)<Q(70346,10000)<Q(1407,200),True)
c('display count',703-498+1,206)
witnesses=[]
for cents in range(498,704):
 x=Q(cents,100)
 if x<=Q(1393,200):floating=(x-Q(199,40))/Q(1,50);fixed=low-floating
 else:fixed=Q(0);floating=x/Q(7,100)
 okay=fixed>=0 and floating>=0 and low<=fixed+floating<high and Q(9,2)<=Q(1,20)*(fixed+floating)<Q(11,2)
 c('display witness/'+str(cents),okay,True)
 c('exact image witness/'+str(cents),Q(1,20)*fixed+Q(7,100)*floating,x)
 witnesses.append(dict(display=str(x),fixed=str(fixed),floating=str(floating)))
c('raw lower rounds4.98',rounded(Q(199,40)),Q(249,50))
c('excluded raw upper would round7.04',rounded(Q(1407,200)),Q(176,25))
c('cent-grid maximum rounds7.03',rounded(Q(70343,10000)),Q(703,100))
c('negative included upper rounds-4.98',rounded(-Q(199,40)),Q(-249,50))
c('negative excluded lower would round-7.04',rounded(-Q(1407,200)),Q(-176,25))
c('open unit interval can display1',rounded(Q(199,200)),Q(1))
c('lower tie enclosure rounds1.00',rounded(Q(10049,10000)),Q(1))
c('upper tie enclosure rounds1.01',rounded(Q(10051,10000)),Q(101,100))
c('round each then add',rounded(Q(1,200))+rounded(Q(1,200)),Q(1,50))
c('add then round',rounded(Q(1,200)+Q(1,200)),Q(1,100))
c('treaty posterior normalizer',Q(1,3)*Q(3,4)+Q(2,3),Q(11,12))
c('treaty posterior timely',Q(1,4)/Q(11,12),Q(3,11))
c('treaty posterior late',Q(2,3)/Q(11,12),Q(8,11))
c('treaty mixed equity',Q(3,11)*83+Q(8,11)*Q(299,4),Q(77))
c('known contribution not complete mean',Q(3,11)*83==77,False)
c('same terminal cash distinct prior equities',Q('88.3')==Q('88.3') and 85!=70 and Q(83)!=Q('74.75'),True)
c('one-payment rate root',Q(110)/(1+Q(1,10))-100,Q(0))
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf']);renders=[]
for n in range(349,355):
 assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
 renders.append(dict(page=n,sha256=sha256((D/'rendered-main'/f'{n:04}.png').read_bytes()).hexdigest()))
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0349-0354',pages=list(range(349,355)),entry_state=prior['exit_state'],
 exit_state='The chapter separates permitted-information policies, event generation, accounting and state transitions before propagating history-indexed laws. Optional mixtures require a declared measure; variance and uncertain-weight bounds do not arise from unweighted histories. Rounded debt can be expressed linearly in principal amounts with an attained4.975 lower endpoint and unattained7.035 supremum. Explicit construction templates and additive grouping preserve scoped completeness limits. Real outputs, rounded displays and cent-grid inputs remain different queries; identical terminal cash does not erase prior treaty or credit memory. Conditional mass remains attached to unresolved execution. The next section introduces financial-method precision through a positive-payment effective-rate equation, whose uniqueness/domain reasoning continues after354.',
 observations=[
 dict(pages=[349],finding='Equations32.4–32.7 stage policy, generator, accounting and transition; valuation information is date-limited. Equations32.8–32.9 distinguish a family of conditional laws from a measurable mixture under a supplied history measure.',disposition='The mechanism terms are defined before the displays and default gives a concrete interpretation. Policy notation includes full state while prose requires permitted information; implementation must enforce that restriction, as in the separately retained observation checks. The mixture requires kernel measurability explicitly. No complete event-method or actual-probability admission follows.'),
 dict(pages=[350],finding='Weights are not solver counts, duplicated statement evidence is disallowed, and equality constraints require suitable measure treatment. The fixed/floating example motivates total variance; uncertain measure bounds and query-relative equivalence follow.',disposition='The total-variance cross term is explained and the finite local control reproduces it. Exact equivalence is scoped to the declared laws, outputs, scenarios and horizon; policy/observation changes still require the stronger dynamic check elsewhere. Sample extrema are correctly inner exploration, and interval enclosures need not be attained. All displays fit.'),
 dict(pages=[351],finding='Principal amounts F,V replace a bilinear unknown share times total. Equation32.11 preserves rounded half-open debt and interest intervals; the lower interest4.975 is attained while upper7.035 is not. Template construction then names scope, slots, shared symbols and unfinished cells.',disposition='The reformulation introduces its positive-total domain and distinguishes fixed from unknown share restrictions. Endpoint arithmetic and exact witnesses agree. Rational, integer-cent and numerical domains remain separate; unsupported theory and timeout do not become infeasibility. The construction completeness qualification continues visibly onto352.'),
 dict(pages=[352],finding='A witness and complete scoped search remain weaker than actual-history coverage. Safe grouping requires shared terms and additive transition/reporting maps. The finite prior0.6/0.4 and likelihood0.2/0.8 example yields posterior3/11 and8/11.',disposition='Examples of nonadditive covenants, guarantees and impairments constrain the grouping claim. Changed horizon/scenario/rule/output invalidates approval. The probability example explicitly treats weights as hypothetical and distinguishes source evidence from extraction scores. Independent rational normalization checks pass; source or implementation completeness is not inferred.'),
 dict(pages=[353],finding='Unsupported execution retains probability mass. The exact real interest image is half-open[4.975,7.035), while cent-rounded displays run4.98–7.03 and integer-cent principal has maximum7.0343. Signed images and rounding ties retain endpoint meaning.',disposition='The page is dense but legible; consecutive examples distinguish output rounding from input quantization before using them. All206 displayed values have checked feasible principal witnesses. Boundary/sign/tie calculations agree. The last sentence deliberately continues on354, and no upper raw endpoint is misreported as attained.'),
 dict(pages=[354],finding='Rounding order changes0.005+0.005 from0.01 to0.02. Equal cash88.3 from different treaty histories is not reusable full state. Posterior weights3/11 and8/11 retain unresolved mass; the complete equity mean is77. The positive-payment rate equation opens the precision section.',disposition='Cash/equity/treaty values are explicitly supplied and their source derivation is cross-referenced to38.6, not newly certified here. Arithmetic and partial-contribution distinctions check. The positive-rate domain r>-1 is visible before the display; existence/uniqueness reasoning continues next page and is not pre-accepted. Monospace refusal labels are actual interface results, and no clipping is observed.')],
 equations_reviewed=['349 equations32.4–32.9','350 fixed/floating mixture','350 equation32.10','350 lower/upper probability bounds','350 scoped law equivalence','351 equation32.11','352 additive transition relation','353 real interest image and witness formulas','354 conditional mean77','354 effective annual rate equation'],
 equation_judgments=[
 dict(labels=['32.4–32.7'],role='reference event and information architecture',verdict='Distinct policy/event/accounting/transition roles and date-limited expectations are explicit; full-state policy notation remains subject to admitted-information restriction, not permission to expose hidden state.'),
 dict(labels=['32.8–32.9'],role='family and mixture definitions',verdict='Kernel measurability and a supplied measure are stated; a family of laws is distinct from a single predictive distribution. Finite weighted controls verify only the local illustrations.'),
 dict(labels=['32.10'],role='local total-variance derivation',verdict='Finite second moment and the zero conditional residual mean remove the cross term. Checked finite example gives79/25 from within-plus-between components.'),
 dict(labels=['lower/upper probability bounds','scoped law equivalence'],role='query definitions and bounded interpretation',verdict='Bounds depend on an admissible measure class; allowing all point masses gives extrema of the kernel. Equivalence is for declared conditional laws and scenarios, not a license to drop information for changed policies.'),
 dict(labels=['32.11'],role='affine constraint reformulation',verdict='Principal amounts preserve the rounded domain without unknown-variable products. Positive-total equivalence and zero-total share undefinedness are stated. Exact lower/supremum and206 display witnesses pass.'),
 dict(labels=['additive transition relation'],role='conditional sufficient grouping argument',verdict='Additivity under every admitted driver and additive reporting permit an induction. The adjacent text excludes thresholds, netting, nonlinear guarantees and lot-specific impairment.'),
 dict(labels=['real interest image and witness formulas'],role='domain/rounding counterexamples',verdict='The two intervals cover the exact half-open image. Witness formulas give feasible principals for every cent display; cent-grid maximum, signed endpoints and rounding order are distinct and checked.'),
 dict(labels=['conditional mean77'],role='finite mixture arithmetic',verdict='Normalizer11/12 and posterior3/11,8/11 give77 from83 and74.75. A known weighted contribution alone is not the mean; rejected accounting is not a third probability atom.'),
 dict(labels=['effective annual rate equation'],role='financial-method definition',verdict='Positive payments/times/price and r>-1 are declared. One-payment rational root is checked; general monotonicity/existence and later numerical treatment await the following page.')],
 arithmetic_artifact='arithmetic-0349-0354.json',source_claims_reviewed=[],render_binding='render-bindings-0349-0354.json',independent_reader='pending',human_acceptance='pending')
for path,obj in [(D/'arithmetic-0349-0354.json',dict(count=len(checks),checks=checks,witnesses=witnesses,scope='Local rational/finite arithmetic; imported source results not newly certified')),(D/'main-0349-0354.json',packet),(H/'inventory-before-0354.json',j),(D/'render-bindings-0349-0354.json',dict(pdf=v['pdf'],pdf_sha256=v['pdf_sha256'],scale=1.5,pages=renders))]:
 with path.open('x') as f:json.dump(obj,f,indent=2);f.write(chr(10))
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks))))
