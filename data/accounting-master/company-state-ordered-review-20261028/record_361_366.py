"""Ordered page361–366 diagnosis; exact examples do not certify a compiler."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json,fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0355-0360.json').read_text());j=json.loads((D/prior['inventory']).read_text())
v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(name,a,b):checks.append(dict(name=name,passed=a==b,actual=str(a),expected=str(b)))
c('decimal2.50 exact',Q('2.50'),Q(5,2));c('zero normalized',str(Q(0,7)),'0')
for x in [Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)]:
 alpha=1-x
 c('shared debt partition/'+str(x),100*alpha+100*(1-alpha),100)
 c('portable interest/'+str(x),100*((1-x)/20+Q(7,100)*x),5+2*x)
 c('fixed versus floating share/'+str(x),100*(alpha/20+(1-alpha)*Q(7,100)),5+2*x)
 c('nine percent assumption/'+str(x),100*((1-x)/20+Q(9,100)*x),5+4*x)
 c('original no shock/'+str(x),100*(alpha/20+(1-alpha)/20),5)
c('fixed floating bounds',[5+2*x for x in [Q(0),Q(1)]],[Q(5),Q(7)])
c('changed upper endpoint',5+4*Q(1),Q(9))
for charge in [Q(0),Q(5),Q(6),Q(7)]:
 c('interest debit-credit balance/'+str(charge),charge-charge,0)
 c('one-year simple/'+str(charge),100*(charge/100)*1,charge)
# Exact local illustrations of the prose, not a test of the portable codec.
c('escaped versus literal decoded unicode',json.loads('"'+chr(92)+'u00e9"'),chr(233))
c('composed decomposed stay distinct',chr(233)=='e'+chr(769),False)
parent={Q(0),Q(1,2),Q(1)};child={a for a in parent if a<=Q(1,2)}
c('child intersection preserves parent',child<=parent,True)
c('endpoint labels do not exhaust family',Q(1,2) in parent-{Q(0),Q(1)},True)
c('conjunction conflicting assertion',child & {Q(1)},set())
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf']);renders=[]
for n in range(361,367):
 assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
 renders.append(dict(page=n,sha256=sha256((D/'rendered-main'/f'{n:04}.png').read_bytes()).hexdigest()))
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0361-0366',pages=list(range(361,367)),entry_state=prior['exit_state'],
 exit_state='The language type table distinguishes contextual money, shared unknowns, structural choices, probability laws and missingness. Portable records have precise rational/Unicode/dependency identity rules separate from raw evidence and financial admission. The current profile still has narrower text authoring than whole-company scope. The synthetic debt listing uses one shared fixed fraction alpha; x=1-alpha preserves the portable floating-share family, interest5–7 and the intermediate6. A same-date interest-payment rule proposes a balanced batch under explicit rounding, while overrides, unresolved applicability, alternative constraints, evidence revision and package migrations preserve separate meanings. Chapter33 ends with versioned IR and source/recognition boundaries; the next chapter must explain how a supported program executes without conflating compiler and solver.',
 observations=[
 dict(pages=[361],finding='The continuing table defines quantity, rate/calendar, account owner, observation, shared symbol, unweighted choice, probability law and measurement. Prose distinguishes exact decimal literals, tagged missingness and contextual aggregation.',disposition='Type roles are intelligible to the accounting implementer; NotApplicable stays distinct from unknown and zero. The dense reference table is readable with no clipping, and rate/calendar refinements are explained beneath it. This is specification reading, not proof of runtime conformance.'),
 dict(pages=[362],finding='The portable record section motivates interoperable identity, specifies six record fields and typed dependency closure, then defines canonical rational/JSON encoding and a schema-separated digest.',disposition='The digest is a representation definition with components introduced locally; it does not establish financial equivalence. Escaped versus literal Unicode and composed versus decomposed strings have distinct stated roles. The page is dense implementation reference but connects details to identity and source preservation. No visible clipping or missing equation symbols.'),
 dict(pages=[363],finding='The proposed whole-company profile has explicitly broader domain than its matched debt text frontend. Compiler stages, expanded bilinear expressions and retained unresolved inputs precede the matched debt formula.',disposition='The alpha/x substitution and5+2x examples check exactly, including the9percent endpoint change. The common language is explicitly unfinished. Several appendix references continue the earlier overview burden, but the local compiler input/result descriptions and following worked listing improve the route; they do not retrospectively close READ-0358-0360-01.'),
 dict(pages=[364],finding='Two readable source listings construct a shared fixed/floating debt family from exact100, give named endpoint alternatives and distinguish the continuous parent family from a weighted mixture.',disposition='The source is explicitly a shortened historical demonstration with no IFRS authority. Shared alpha preserves principal100 and interest7-2alpha; endpoints are not exhaustive. Code boxes fit the page. Later useful examples do not repair the earlier abrupt profile inventory.'),
 dict(pages=[365],finding='The same-date InterestPaid rule separates simple interest, declared half-even rounding, nonnegative scope and a balanced proposed batch. Override maxima, conflicts and symbolic applicability remain explicit before alternative inheritance.',disposition='Accrual/payment timing is stated before code; the debit/credit signs balance. Negative interest needs a different rule. Applicable-rule ambiguity remains a conflict rather than file-order priority. These are clear specification conditions; the reading does not test a general dispatcher. No clipped code line observed.'),
 dict(pages=[366],finding='A shared treatment variable links liability classification and periodic payments; conjunction, source correction and posterior reweighting are distinct. Packages and IR versions preserve mandatory rules and original payloads.',disposition='The chapter closes with meaningful semantic/version boundaries and no implicit last-loaded override. IR node enumeration is reference material. Large lower whitespace closes the chapter; no lost continuation or malformed symbol is visible. Independent implementation and reader acceptance remain open.')],
 equations_reviewed=['362 portable record digest','363 floating share substitution and interest expression','364 shared principal partition and rate-shock family','365 simple-interest balanced posting'],
 equation_judgments=[
 dict(labels=['portable record digest'],role='supporting representation definition',verdict='Schema-specific prefix, NUL separator and canonical bytes define content identity after local encoding rules. No probabilistic, economic or cryptographic-security theorem is asserted or newly checked; raw evidence retains a separate digest.'),
 dict(labels=['floating share substitution','conditional interest'],role='mechanism-bearing debt-family identity',verdict='x=1-alpha preserves fixed/floating principal100 and one-year simple interest5+2x. Five exact fractions verify the algebra, endpoints and interior6; changing floating7percent to9percent gives5+4x. These are supplied assumptions, not market rates.'),
 dict(labels=['shared principal partition','rate-shock family'],role='mechanism-bearing source-to-constraint example',verdict='The same alpha must occur in both components. Their sum is100 for the full interval; two named branches do not exhaust it or supply a prior. Local finite point checks support the elementary identity, whose algebra holds for every alpha.'),
 dict(labels=['simple-interest balanced posting'],role='recognition-rule illustration',verdict='Under same-date accrual/payment and nonnegative rounded charge, expense debit and cash credit sum to zero. Simple year-fraction calculation and rounding are declared premises; balance alone proves neither accounting eligibility nor completeness.')],
 arithmetic_artifact='arithmetic-0361-0366.json',source_claims_reviewed=[],render_binding='render-bindings-0361-0366.json',findings=[],carried_unresolved_findings=['READ-0358-0360-01'],independent_reader='pending',human_acceptance='pending')
for path,obj in [(D/'arithmetic-0361-0366.json',dict(count=len(checks),checks=checks,scope='Local exact debt and semantic illustrations; no codec/compiler or imported theorem certification')),(D/'main-0361-0366.json',packet),(H/'inventory-before-0366.json',j),(D/'render-bindings-0361-0366.json',dict(pdf=v['pdf'],pdf_sha256=v['pdf_sha256'],scale=1.5,pages=renders))]:
 with path.open('x') as stream:json.dump(obj,stream,indent=2);stream.write(chr(10))
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks),new_findings=0,carried_unresolved=['READ-0358-0360-01'])))
