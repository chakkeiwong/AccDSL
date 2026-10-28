"""Ordered individual reading343–348 with exact local mathematical controls."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0337-0342.json').read_text());j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
low,high=Q(100)-Q(1,2),Q(100)+Q(1,2)
c('rounding lower',low,Q('99.5'));c('rounding upper',high,Q('100.5'))
c('half-open includes lower',low<=Q('99.5')<high,True)
c('half-open excludes upper',low<=Q('100.5')<high,False)
family=[{('A',100)},{('B',100)}]
c('certain tuples empty',len(set.intersection(*family)),0)
c('union aggregate wrong',sum(x[1] for x in set.union(*family)),200)
c('each history total',sorted({sum(x[1] for x in h) for h in family}),[100])
c('certain existence',all(bool(h) for h in family),True)
c('not certain A',all(('A',100) in h for h in family),False)
c('empty history changes existence',all(bool(h) for h in family+[set()]),False)
for z,delta in [((60,40),(10,-10)),((20,80),(-5,5))]:
 c('null vector '+str(delta),sum(delta),0)
 c('same aggregation '+str(z),sum(x+y for x,y in zip(z,delta)),sum(z))
c('receivable path1',20+50-40-5+0,25)
c('receivable path2',20+50-45-0+0,25)
balances=[Q(20),Q(-20),Q(0),Q(0)]
for i,journal in enumerate([[Q(100),Q(-100),0,0],[Q(-40),Q(40),0,0],[0,0,Q(6),Q(-6)]]):
 c('journal balance'+str(i),sum(journal),0)
 balances=[a+b for a,b in zip(balances,journal)]
 c('inductive book balance'+str(i),sum(balances),0)
c('decimal rational',Q('12.34'),Q(1234,100))
c('unknown-or-negation local three-valued arithmetic',max(Q(1,2),1-Q(1,2)),Q(1,2))
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf'])
for n in range(343,349):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0343-0348',pages=list(range(343,349)),entry_state=prior['exit_state'],
 exit_state='The architecture keeps source inspection, licensing, adapter outputs and actual integration separate. Chapter32 defines history compatibility relative to context, precision and model scope; empty or singleton families do not establish false filings or real-history identification. The payable100 example separates certain existence and totals from individually certain creditor rows. Source theorems require information-order, genericity and representation conditions, while undecided evaluation does not establish opposing histories. Null-space ambiguity and unknown contract terms coexist. Balanced signed journals preserve a one-currency bookkeeping invariant, and reports additionally require movements, economic state and reporting rules. Continue after the separation of functional-currency books from group translation.',
 observations=[
 dict(pages=[343],finding='The component catalogue explicitly describes selected official interfaces and licences archived on2 October2026, without executed integration or performance evidence. The table covers ingestion, ledgers, rules, contracts, valuation and tax-rule references with separate roles.',disposition='The long table is readable and continues with a repeated header. Repository status/licence text is historical surveyed evidence, not freshly verified current software or legal advice. Candidate/optional status and missing corporate-tax coverage are visible; no adapter adoption is inferred.'),
 dict(pages=[344],finding='The remaining component rows separate exact solving, analytics and optional inference. Licence compatibility is unresolved for concrete combinations. XBRL context/decimals remain part of facts. Contract and valuation adapters return typed results rather than directly posting.',disposition='The table closes cleanly before the responsibilities section. Ownership of uncertainty, provenance and accounting rules is explicit, and performance is subordinate to common semantic cases. No current licence or runtime guarantee is supplied by this author read.'),
 dict(pages=[345],finding='Equation32.1 defines compatible histories using the model scope, joint constraints and context-specific reporting intervals. Rounding endpoints require a tie convention; unknown precision has no automatic tolerance. Empty, singleton and larger sets have different model-relative interpretations.',disposition='Symbols and contexts are introduced before the display and outcomes immediately explained. The half-open interval includes99.5 and excludes100.5 for displayed100/unit1 under the declared convention. The closed unknown-tie enclosure is cross-referenced. No assumption of actual-model completeness or a true singleton is made.'),
 dict(pages=[346],finding='Payable100 to A or B makes existence and total certain while creditor identity varies. Certain-row intersection is empty and union wrongly totals200. Answer-family, certain-tuples and Boolean-certainty displays state different query meanings.',disposition='The example precedes all three local definitions, which specify nonempty family and total deterministic query. Exact finite controls reproduce the distinctions and the effect of adding an empty history. Source Libkin results remain separately cited; this local example neither proves finite symbolic representation nor licenses merging histories for later queries.'),
 dict(pages=[347],finding='Information-order preservation is not presented as sufficient alone: genericity and representation conditions are also required. The three-valued example can be undecided even when every completion says yes. The following null-space derivation introduces fixed mappings, dimensions and a nonzero null vector.',disposition='Source theorem/equation anchors and transfer limits are explicit; primary papers are not newly re-read here. The local1/2 calculation is illustrative, not a re-proof of the evaluator theorem. The bottom-page linear equation is legible and its feasible-constraint qualification continues on348. No timeout is promoted to evidence of two opposing histories.'),
 dict(pages=[348],finding='Null-space alternatives remain subject to all other constraints; receivables aggregation does not identify collections when other movements are unknown. Contract-reset ambiguity can remain after movement recovery. Equations32.2/32.3 separate signed-book conservation from economic correctness and reporting rules.',disposition='Exact examples preserve report totals under distinct movement vectors and receivable paths. The induction correctly uses balanced opening and balanced journals. Profit closing is excluded from cash flows and double counting. Single functional currency and separate share/foreign units are explicit. Displays and prose fit; no local repair is confirmed.')],
 equations_reviewed=['345 equation32.1','346 answer family/certain tuples/Boolean certainty','347 A(z+v)=Az+Av=y','348 receivables bridge','348 equation32.2','348 equation32.3'],
 equation_judgments=[
 dict(labels=['32.1'],role='local definition of scoped compatible histories',verdict='Well-scoped definition with observation contexts, justified intervals and joint constraints introduced; no statistical or real-history completeness theorem asserted.'),
 dict(labels=['answer family','certain tuples','Boolean certainty'],role='distinct query definitions',verdict='Finite payable100 example and empty-history control verify the local logic. Omitted certain rows do not imply absence; history links are required even when query outputs coincide.'),
 dict(labels=['A(z+v)=Az+Av=y'],role='linear nonidentification derivation',verdict='Correct by linearity with Av=0; the next page retains remaining constraints. Two rational null-vector controls pass; contract unknowns are a separate source of ambiguity.'),
 dict(labels=['receivables bridge'],role='classified movement identity',verdict='Signs match opening plus credit sales minus collections/write-offs plus other classified movements. Two explicit paths give25 with different collections; no inferred real events.'),
 dict(labels=['32.2'],role='bookkeeping conservation invariant and transition',verdict='Correct induction from balanced opening and journals in one functional currency. Three journal controls pass; economic classification and authority do not follow from balance.'),
 dict(labels=['32.3'],role='reporting-function definition',verdict='Inputs include end balances, period journals, economic state, basis/perimeter and interval. It is a declared interface, not an implemented completeness theorem; cash categories require more than end cash.')],
 arithmetic_artifact='arithmetic-0343-0348.json',source_claims_reviewed=[],render_binding='render-bindings-0343-0348.json',independent_reader='pending',human_acceptance='pending')
for path,obj in [(D/'arithmetic-0343-0348.json',dict(count=len(checks),checks=checks,scope='Local rational/set controls only; imported theorems/licences not newly audited')),(D/'main-0343-0348.json',packet),(H/'inventory-before-0348.json',j)]:
 with path.open('x') as fh:json.dump(obj,fh,indent=2);fh.write('\n')
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks))))
