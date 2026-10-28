"""Record individually read pages325–330 with exact illustrative checks."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0319-0324.json').read_text());j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
c('geography total',180+80,260);c('channel total',200+60,260)
c('double counting both margins',180+80+200+60,520)
for x in [120,180]:
 table=[[x,180-x],[200-x,x-120]]
 c(str(x)+'/rows',[sum(row) for row in table],[180,80])
 c(str(x)+'/columns',[table[0][i]+table[1][i] for i in [0,1]],[200,60])
 c(str(x)+'/nonnegative',all(n>=0 for row in table for n in row),True)
c('distinct cross cells possible',120!=180,True)
c('annual plus interim notes',13+10,23)
c('nearest rounding lower in millions',Q(100)-Q(1,2),Q(199,2))
c('nearest rounding upper in millions',Q(100)+Q(1,2),Q(201,2))
c('positive truncation lower',100,100);c('positive truncation exclusive upper',100+1,101)
c('99.75 fits nearest',Q(199,2)<=Q(399,4)<=Q(201,2),True)
c('99.75 outside truncation',100<=Q(399,4)<101,False)
c('100.75 fits truncation',100<=Q(403,4)<101,True)
c('100.75 outside nearest',Q(199,2)<=Q(403,4)<=Q(201,2),False)
c('compatible revised second half',260-110,150)
c('incompatible original half arithmetic',260-120,140)
c('vintage-induced difference',150-140,10)
c('reference target print/PDF offsets',[158-156,165-163],[2,2])
def temporal(cutoff,start,end):return 'excluded' if cutoff<start else 'unresolved' if cutoff<end else 'supported_date'
for cutoff,expected in [(-1,'excluded'),(0,'unresolved'),(Q(1,2),'unresolved'),(1,'supported_date')]:
 c('date-only cutoff '+str(cutoff),temporal(cutoff,0,1),expected)
for cutoff,public,possessed,accepted in [(3,True,False,False),(5,True,True,False),(6,True,True,True)]:
 c('authored day'+str(cutoff)+'/three clocks',[cutoff>=2,cutoff>=5,cutoff>=6],[public,possessed,accepted])
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf'])
for n in range(325,331):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
with (D/'arithmetic-0325-0330.json').open('x') as stream:json.dump(dict(count=len(checks),checks=checks,scope='Conditional illustrative partitions, rounding, vintage and timing; actual source facts and authority not newly certified'),stream,indent=2)
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0325-0330',pages=list(range(325,331)),entry_state=prior['exit_state'],
 exit_state='Source mappings preserve partition, context and measurement meaning; literal transcription can correctly preserve a wrong navigation direction while a separately reviewed interpretation rejects it. Disclosure coverage, rounding assumptions and source availability versus system possession remain distinct. Revised half-year110 with annual260 gives150; original120 would mix vintages. The bank example preserves original commitment risk and separates public availability January2, ingestion January5 and reading acceptance January6. Continue the consequences of revised facts for bank and insurance histories without treating these authored dates as historical evidence.',
 observations=[
 dict(pages=[325],finding='Unresolved incorporated references remain obligations. Narrative qualifiers distinguish coupon type from total exposure, authority from mandatory action and contingent guarantee exposure from present liability. Mapping relationships preserve basis and population; geography180+80 and channel200+60 each describe260.',disposition='The concrete partition example motivates disjoint/exhaustive sumOver. Adding both partitions produces520 and is invalid; two feasible joint tables prove the marginals do not identify geography-by-channel cells. Next-midnight use is a conservative date-only eligibility rule, not a recovered publication instant.'),
 dict(pages=[326],finding='Revision scope does not silently update every note or accounting basis. FIFO and straight-line policy statements do not supply lots, useful lives or impairment facts. Extraction, translation, model admission and accounting eligibility answer distinct questions; a source statement can be faithfully copied and wrong.',disposition='The four-stage distinction is connected to specific inventory and depreciation unknowns. Retained Apple and ASBE passages are cited historical evidence, not newly checked legal authority. Unknowns are not replaced by thresholds or a single approved flag. The wrong-reference section begins with two competing literal directions.'),
 dict(pages=[327],finding='JPMorgan target pages differ by seven while both physical/printed mappings have offset two. Navigation repair preserves the literal156 statement, supports target163, and invalidates dependent search/coverage while unrelated financial amounts may remain reusable.',disposition='Page-specific source and navigation claims are not conflated with financial misstatement. The text states the156 target is wrong relative to the auditor-location question without pretending both alternatives remain admissible after refutation. Cache invalidation includes negative search results and annotated displays; no generic delete-all implication.'),
 dict(pages=[328],finding='The reference case is an author source inspection and proposed review sequence, not observed human/software acceptance. Retained-unit, assertion-review and query-exposure coverage have different populations. The rounding section introduces display100 in millions and an explicitly assumed nearest-rounding enclosure.',disposition='13 annual plus10 interim notes gives23; reported inventories are historical counts, not current completion. Source-package obligations can remain open after downloaded units finish. Scale and issuer rounding are separate; the conservative closed half-unit interval is conditional on a nearest-rounding model and unknown tie rule.'),
 dict(pages=[329],finding='Positive truncation gives100 to101 exclusive, unlike nearest rounding99.5 to100.5. Unknown issuer rounding supplies no automatic half-unit bound. Public availability, system possession and accepted reading use different cutoffs; date-only metadata represents an interval between named-zone midnights.',disposition='Exact contrasting99.75/100.75 examples check the interval distinction. Figure29.1 clearly separates exclusion, unresolved instant and date-supported eligibility; it does not add a delay to known timestamps or assume all days last24 hours. Missing timezone remains unresolved. Formula line continues from328 without lost symbols.'),
 dict(pages=[330],finding='Revision selection operates after availability filtering. Revised half-year110 with annual260 yields150; subtracting original120 gives140 with incompatible vintage. A constructed commitment-risk example and publication/ingestion/review dates distinguish recovered history from receipt time.',disposition='The numerical half-year arithmetic is correct and its admissibility condition explicit. Absence of qualifying financial conflicts in the bounded search is not absence in the corpus. The bank allowance4/equity16 statement points to later assumptions and is not newly derived here; AASB authority and actual historical byte availability are not newly certified.')],
 equations_reviewed=['328 nearest-rounding compatibility enclosure','329 positive truncation interval','329 Figure29.1 cutoff intervals','330 compatible and mixed-vintage half-year differences'],
 equation_judgments=[dict(labels=['328 nearest rounding','329 truncation'],role='conditional compatibility constraints in displayed units',verdict='Correct for explicit positive scale and admitted rounding/truncation models; unknown tie rule justifies conservative closed enclosure, truncation positive-domain upper endpoint is excluded. Literal precision alone does not select either model.'),dict(labels=['329 Figure29.1'],role='date-only publication uncertainty and cutoff eligibility',verdict='Correct conservative interval logic: before local-midnight start excluded, inside interval unresolved, at/after next-midnight end date-supported, with byte linkage and named timezone separately required.'),dict(labels=['330 half-year'],role='same-vintage period difference',verdict='260-110=150 is correct under compatible periods/basis/perimeter and revised vintage;260-120=140 is arithmetically correct but wrong for the specified revised-history query.')],
 arithmetic_artifact='arithmetic-0325-0330.json',source_claims_reviewed=[],render_binding='render-bindings-0325-0330.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0325-0330.json').open('x') as stream:json.dump(packet,stream,indent=2);stream.write(chr(10))
with (H/'inventory-before-0330.json').open('x') as stream:json.dump(j,stream,indent=2);stream.write(chr(10))
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks))))

