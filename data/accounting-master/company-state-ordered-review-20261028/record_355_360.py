"""Actual ordered reading355–360 with local rational arithmetic and finding."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json,fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0349-0354.json').read_text());j=json.loads((D/prior['inventory']).read_text())
v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
def pv(r):return Q(121)/(1+r)**2
c('two-year positive-payment exact10percent',pv(Q(1,10)),Q(100))
c('fee changes residual at old root',pv(Q(1,10))-98,Q(2))
c('fee-adjusted root bracket lower',pv(Q(11,100))>98,True)
c('fee-adjusted root bracket upper',pv(Q(12,100))<98,True)
for r in [Q(-1,2),Q(0),Q(1,10),Q(1)]:
 c('positive-payment derivative at'+str(r),-Q(242)/(1+r)**3<0,True)
for r in [Q(1,10),Q(1,5)]:
 c('mixed-sign distinct root'+str(r),-100+Q(230)/(1+r)-Q(132)/(1+r)**2,Q(0))
c('half-year effective factor',Q(11,10)**2,Q(121,100))
c('half-year interest',100*(Q(11,10)-1),Q(10))
c('simple prorating changes contract',100*Q(21,100)*Q(1,2),Q(21,2))
c('irrational factor lower bracket',Q(1048,1000)**2<Q(11,10),True)
c('irrational factor upper bracket',Q(1049,1000)**2>Q(11,10),True)
c('rounding enclosure crosses half-cent',Q(10049,10000)<Q(201,200)<Q(10051,10000),True)
mass=[Q(1,3)*Q(3,4),Q(2,3)];z=sum(mass)
c('Bayes normalizer',z,Q(11,12));c('Bayes first mass',mass[0]/z,Q(3,11));c('Bayes second mass',mass[1]/z,Q(8,11))
c('unresolved mass retained',1-mass[0]/z,Q(8,11))
c('duplicate likelihood changes mass',Q(3,16)/(Q(3,16)+Q(2,3)),Q(9,41))
c('duplicate not idempotent fresh evidence',Q(9,41)!=Q(3,11),True)
precision=Q(1,4)+1;variance=1/precision;mean=variance*2
c('Gaussian precision',precision,Q(5,4));c('Gaussian variance',variance,Q(4,5));c('Gaussian mean',mean,Q(8,5))
c('conditional cash mean',100+10*mean,Q(116));c('conditional cash variance',100*variance,Q(80))
precision2=precision+1;v2=1/precision2;m2=v2*4
c('independent second precision',precision2,Q(9,4));c('independent second variance',v2,Q(4,9));c('independent second mean',m2,Q(16,9))
for x in [Q(-2),Q(0),Q(8,5),Q(3)]:
 c('Gaussian square completion at'+str(x),x*x/4+(2-x)**2,precision*(x-mean)**2+Q(4,5))
c('flat likelihood preserves prior odds',(Q(1,3)*Q(1,7))/(Q(2,3)*Q(1,7)),Q(1,2))
c('unidentified-share lower point mass',5+2*Q(0),Q(5));c('unidentified-share upper point mass',5+2*Q(1),Q(7))
c('conditioning observes U1',2*1+1,3)
intervention=[2*1+u for u in [0,1]]
c('intervention outcomes',intervention,[2,3]);c('intervention expectation',sum(intervention,Q(0))/2,Q(5,2))
c('conditioning intervention differ',Q(3)!=Q(5,2),True)
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf']);renders=[]
for n in range(355,361):
 assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
 renders.append(dict(page=n,sha256=sha256((D/'rendered-main'/f'{n:04}.png').read_bytes()).hexdigest()))
finding=dict(id='READ-0358-0360-01',pages=[358,359,360],source='chapters/06-language.tex',section='33.1',
 status='confirmed_author_navigation_issue_successor_repair_pending',
 question='Which current language construct does the reader use to turn a reported balance into a constrained, executable company path?',
 evidence='After one substantive opening paragraph, pages358–359 enumerate successive appendix extensions A.54.17–23, A.10–19, A.3–9 and A.20–26 before showing a local declaration or a running source-to-execution example. Page360 returns to compiler and identity distinctions but still leaves operational reconstruction to the appendices.',
 consequence='A prepared reader can state important limits, but must chase many implementation references to reconstruct how the current language composes a company model. The preceding precision/inference chapter does not teach these new language forms.',
 proposed_repair='In the post-diagnosis successor, organize33.1 around one sourced balance, an unresolved contract alternative and a conditional operation. Introduce each declaration where it changes that example, then move the chronological extension inventory to a compact reference subsection. Preserve every interface limitation, state/schema distinction, citation and exact appendix anchor.',
 boundary='Author diagnosis only, not human acceptance. Frozen baseline and selected/provisional releases stay unchanged; this record is not a completed prose repair.')
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0355-0360',pages=list(range(355,361)),entry_state=prior['exit_state'],
 exit_state='Positive-payment effective rates have a negative derivative on the stated domain, while mixed-sign cash flows can have multiple roots; fee, day fraction and rounding rules change the quantity queried. Bayesian and Gaussian updates require a supplied law and genuinely new evidence, and unresolved execution retains its mass. A supplied causal model distinguishes conditioning from intervention and does not grant managers future information. Chapter33 now distinguishes disclosures, possible histories, selected methods, source identity and semantic identity, but its current-profile overview relies on long appendix-reference sequences; a specific navigation repair remains pending. The reader reaches the first Money<C> type row; subsequent type definitions and portable language contracts continue after360.',
 observations=[
 dict(pages=[355],finding='The derivative completes the positive-payment rate argument. Fee2 changes the two-year rate; half-year21percent gives interest10, while simple prorating gives10.5. Rounding enclosures precede Bayes and duplicate-information semantics.',disposition='Signs and exact examples check. Domain/positive-payment premises carry from354; the bracket procedure keeps unknown signs unresolved. Bayes numerator/normalizer and retained8/11 failure mass are explicit. No clipped display or symbol is observed.'),
 dict(pages=[356],finding='The Gaussian example completes the square, adds precisions, gives variance4/5 and mean8/5, then distinguishes an independent second observation from duplicate data. Flat likelihood leaves an unidentified debt share governed by its prior.',disposition='The scalar square completion and cash moments116/80 check independently. Measurement error is explicitly a model premise, not rounding. The page is dense but defines symbols before using them. Stuart and Giacomini–Kitagawa references are retained source anchors, not newly certified by this reading.'),
 dict(pages=[357],finding='The supplied X=U,Y=2X+U model gives observed-X1 outcome3 versus intervention outcomes2/3 with mean2.5. Stress, observation and structural intervention remain different questions.',disposition='The finite example checks exactly; the manuscript states required structural equations/disturbance law and does not infer causal identification from filings. Permitted actor information stays separate from scheduler foresight. Large lower whitespace closes the chapter without clipping.'),
 dict(pages=[358],finding='The language chapter starts with useful distinctions among disclosures, possible histories, assumptions and applicable methods, then shifts into successive appendix-extension summaries.',disposition='The first paragraph supplies a sound reader purpose. The following long paragraph introduces many profiles, schemas and appendix numbers without a local declaration; READ-0358-0360-01 records the resulting navigation burden for successor repair.'),
 dict(pages=[359],finding='The overview catalogs source-constrained states, finite history families, operations, carried claims, method composition and shared-book tax successors.',disposition='The distinction between common caller and compatible book is substantive and matches the inspected refinancing integration limit. Repeated appendix jumps make the procedure difficult to reconstruct locally. This is a reader-navigation issue, not proof that the referenced interfaces are absent or wrong.'),
 dict(pages=[360],finding='Historical Core0, current portable methods, structural compilation, source/program digests and semantic identity are distinguished. The type table starts with Money<C>.',disposition='Whitespace-changing source versus unchanged lowered semantics is clearly explained. The text disclaims whole-company grammar/compiler completeness. The first table row is readable; remaining rows continue next page and are not pre-accepted. The profile-overview repair remains open.')],
 equations_reviewed=['355 effective-rate derivative','355 two-year fee and half-year accumulation','355 Bayes rule and finite normalizer','356 Gaussian quadratic expansion','356 precision/mean equations and scalar examples','356 conditional-prior bounds','357 elementary structural equations'],
 equation_judgments=[
 dict(labels=['effective-rate derivative'],role='local uniqueness argument',verdict='Positive payments/times and r>-1 imply strictly negative derivative; a certified sign-changing bracket contains one root. Mixed-sign counterexample retains two distinct roots1/10 and1/5.'),
 dict(labels=['fee and half-year accumulation'],role='contract/numerical target distinctions',verdict='Payment121 at two years over proceeds100 gives10percent; proceeds98 shifts the root into(.11,.12). Effective21percent over half a year gives factor1.1; linear prorating is a different contract. Rational enclosures cross rounding cells as stated.'),
 dict(labels=['Bayes rule'],role='finite conditional probability definition',verdict='A positive normalizer11/12 produces3/11 and8/11. Squaring a reused likelihood instead gives9/41 for the first history, demonstrating changed evidence rather than an idempotent condition. Zero evidence probability remains unsupported conditioning.'),
 dict(labels=['Gaussian quadratic expansion','precision and mean'],role='local conjugate-model derivation',verdict='Positive-definite covariances and independent Gaussian observation error are explicit. Scalar square completion and moments reproduce precision5/4,mean8/5,variance4/5; the independent second update gives16/9 and4/9. Reusing the same observation is wrong for the stated information.'),
 dict(labels=['conditional-prior bounds'],role='local unidentified-share deduction',verdict='With a constant likelihood, prior odds stay unchanged. Point masses at0/1 attain expected5+2x endpoints5/7; no general asymptotic theorem is transferred.'),
 dict(labels=['elementary structural equations'],role='supplied causal counterexample',verdict='Conditioning X1 fixes U1 and Y3. Replacing only X preserves the original Bernoulli-U law and gives mean2.5. This checks the illustration, not empirical identification or the external source theorem.')],
 arithmetic_artifact='arithmetic-0355-0360.json',source_claims_reviewed=[],render_binding='render-bindings-0355-0360.json',findings=[finding],independent_reader='pending',human_acceptance='pending')
for path,obj in [(D/'arithmetic-0355-0360.json',dict(count=len(checks),checks=checks,scope='Local rational examples; external source results not newly certified')),(D/'main-0355-0360.json',packet),(H/'inventory-before-0360.json',j),(D/'render-bindings-0355-0360.json',dict(pdf=v['pdf'],pdf_sha256=v['pdf_sha256'],scale=1.5,pages=renders)),(H/'finding-0358-0360.json',finding)]:
 with path.open('x') as f:json.dump(obj,f,indent=2);f.write(chr(10))
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks),unresolved_findings=1)))
