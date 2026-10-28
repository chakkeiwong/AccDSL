"""Record rendered reading313–318 after individual image inspection."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0307-0312.json').read_text());j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
c('annual comprehensive income',93736+4280,98016)
c('annual closing equity',364980-308030,56950)
c('cash population difference',30737-29965,772)
c('H1 gross additions funded',9447+1082,10529)
c('H1 retirement loss',6000-5636,364)
c('H2 additions',10529+1000,11529)
c('H2 retirements',6000+1000,7000)
c('H2 retirement loss',7000-5636,1364)
c('H2 capital payable',1082+1000,2082)
c('H1 net property movement',10529-6000-8200+5636,1965)
c('H2 net property movement',11529-7000-8200+5636,1965)
c('extra liabilities offset',1000-1000,0)
c('expense and loss offset',-1000+1364-364,0)
for a in [Q(0),Q(1,2),Q(1)]:
 other=1000+a*(-1000);liabilities=(1-a)*(-1000)
 c('other adjustment alpha'+str(a),other,1000*(1-a))
 c('liability adjustment alpha'+str(a),liabilities,-1000*(1-a))
 c('total operating cash difference alpha'+str(a),other+liabilities,0)
c('alpha1 displayed rows both vanish', (1000+Q(1)*(-1000),(1-Q(1))*(-1000)),(0,0))
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf'])
for n in range(313,319):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
with (D/'arithmetic-0313-0318.json').open('x') as stream:json.dump(dict(count=len(checks),checks=checks,scope='Displayed arithmetic and exact conditional equations only; no new source/rule certification'),stream,indent=2)
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0313-0318',pages=list(range(313,319)),entry_state=prior['exit_state'],
 exit_state='Disruption, product replacement, supplier capacity, defective stock and continuing service rights require distinct dated resources and obligations. The combined source-token query can finish while actual whole-company histories remain unresolved. Two conditional asset histories share annual rows after an independently assumed expense-liability offset and alpha-dependent cash-flow allocation; future liabilities can still differ. Continue the next consequence of matching annual rows without collapsing these conditional histories into an exhaustive real-company family.',
 observations=[
 dict(pages=[313],finding='Trade restrictions and disasters have separate exposure, response and recovery dates. Demand loss and component interruption need different product-level response models; supplier requirements and insurance do not identify loss probabilities or payment dates.',disposition='The page completes the prior unfinished restriction discussion. Recovery capacity, deliveries, spending and settlement remain separate; the prose is legible with no clipped text or confirmed local defect. No current event or legal finding is re-certified.'),
 dict(pages=[314],finding='Product replacement can lower revenue or margins, and requires customer acceptance, component compatibility and capacity. Development, announcement, production, shipment, bundled service and cash collection cannot share one launch timestamp.',disposition='The argument progresses from restored supply to whether it produces the desired product. Inventory cohorts and committed purchases supply relevant memory; no substitution fraction, write-down probability or source-inferred scenario is invented.'),
 dict(pages=[315],finding='A supply agreement does not establish supplier capacity, renewal or performance; multiple suppliers may share a shortage. Restoring a source and switching source have different compatibility, term and delivery prerequisites. Delivery does not itself establish a safe functioning product.',disposition='The section shift introduces the next necessary condition after availability. A final citation continues on316 and is intact. The distinction between production, assembly and delivery avoids counting one improvement as all three.'),
 dict(pages=[316],finding='Delivered, acceptable and repaired units differ. Defects can produce several expense/obligation types; supplier recovery is a separate claim. Obsolete stock, cancellation obligations and long-lived impairment require distinct facts. Typical150-day manufacturing commitments do not redefine all reported obligations.',disposition='Two equal inventory totals can support different responses because quality, compatibility and contracts differ. The text treats FIFO as a reported cost-flow method, not proof of recoverability. Source wording and present accounting authority are not newly validated.'),
 dict(pages=[317],finding='Service access depends on intellectual-property/content rights, developer support, data and payment conditions beyond physical capacity. The connected answer distinguishes source-located statement readings from actual company-history completeness.',disposition='Annual93736+4280=98016 and assets364980 minus liabilities308030=equity56950 check exactly. The units warning prevents adding shares or per-share values to monetary totals. The last sentence continues inventory detail on318.'),
 dict(pages=[318],finding='A source-query completion is different from identifying the actual whole-company family. Reported dash and cash-population difference772 are not new transactions. H1/H2 property paths share net property but differ in capital payable and retirement loss; an explicitly independent expense-liability premise offsets those differences.',disposition='23 exact checks preserve funding, loss, property and equity arithmetic. Equations28.25/28.26 sum to zero for every alpha;0,1/2,1 controls verify. Alpha is a reporting allocation, not history probability. The offset assumptions and unresolved absolute feasible remainder are explicit, so matched rows do not establish an actual two-member family.')],
 equations_reviewed=['28.25','28.26'],equation_judgments=[dict(labels=['28.25','28.26'],role='conditional difference in two indirect operating-cash-flow rows',verdict='Correct under the expressly supplied expense-liability and shared-row assumptions:1000(1-alpha) and-1000(1-alpha) cancel. Alpha1 gives both rows zero; no probability or actual family conclusion.')],
 arithmetic_artifact='arithmetic-0313-0318.json',source_claims_reviewed=[],render_binding='render-bindings-0313-0318.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0313-0318.json').open('x') as stream:json.dump(packet,stream,indent=2);stream.write(chr(10))
with (H/'inventory-before-0318.json').open('x') as stream:json.dump(j,stream,indent=2);stream.write(chr(10))
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks))))

