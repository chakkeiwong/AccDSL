"""Record the six pages actually inspected; no source acceptance inferred."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / 'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior = json.loads((D / 'main-0259-0264.json').read_text())
inventory = json.loads((D / prior['inventory']).read_text())
volume = next(v for v in inventory['volumes'] if v['name'] == prior['volume'])
pdf = ROOT / volume['pdf']
assert sha256(pdf.read_bytes()).hexdigest() == volume['pdf_sha256']
checks = []
def check(name, actual, expected):
    checks.append(dict(name=name, passed=actual == expected, actual=str(actual), expected=str(expected)))
check('creditor assessed net loan', Q(100)-30, Q(70))
check('assessed creditor assets and equity', Q(30)+70, Q(130)-30)
check('zero allowance disposal loss', Q(70)-100, Q(-30))
check('allowance30 share60 disposal loss', Q(60)-(100-30), Q(-10))
check('allowance30 share60 total loss', Q(-30)-10, Q(-40))
check('zero allowance share100 disposal', Q(100)-100, Q(0))
check('zero allowance share120 disposal', Q(120)-100, Q(20))
check('component inventory', Q(80)+20+5+3, Q(108))
check('separate components', Q(108)-80, Q(28))
for alpha in [Q(0),Q(1,2),Q(1)]:
    check('27.1 alpha='+str(alpha), 100*(Q(1,20)*alpha+Q(7,100)*(1-alpha)), 7-2*alpha)
    check('complementary coordinate alpha='+str(alpha), 7-2*alpha, 5+2*(1-alpha))
assert all(c['passed'] for c in checks)
arithmetic = dict(pages=[265,266,268,269], checks=checks, count=len(checks),
    scope='Exact local arithmetic only; cited accounting authority not newly inspected')
with (D/'arithmetic-0265-0270.json').open('x') as stream:
    json.dump(arithmetic,stream,indent=2);stream.write('\n')
doc=fitz.open(pdf)
for n in range(265,271):
    assert sha256(doc[n-1].get_text().encode()).hexdigest()==volume['pages'][n-1]['text_sha256']
segment=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=volume['pdf_sha256'],
    id='main-0265-0270',pages=list(range(265,271)),entry_state=prior['exit_state'],
    exit_state='Creditor impairment and disposal remain separate even when final totals coincide. Acquisition consideration is only one part of a supplied exchange partition. Part II restates the inverse-accounting product decision: equal historical journals can hide a continuous family of contract terms, which yields scenario ranges without probabilities. The ten acceptance requirements distinguish evidence, histories, meanings, joint ambiguity and accounting from implementation choices; design acceptance and delivered software remain separate.',
    observations=[
        dict(pages=[265],finding='The creditor example begins from an explicitly measured amortised-cost loan and separately supplied loss allowance. Allowance30 and shares70 give impairment loss30 with no disposal loss; allowance0 with the same shares gives disposal loss30 instead. Intermediate history, not the common total, identifies the two mechanisms.',disposition='Retain full impairment/disposal sequence and supplied FVTPL/no-control/no-significant-influence premises. Exact local amounts checked; AASB paragraph applicability not freshly validated.'),
        dict(pages=[266],finding='The acquisition example partitions80 consideration,20 debt settlement,5 costs and3 other transaction, totaling108. The difference28 is explicitly not a goodwill residual. The discussion correctly stops before inferring a loan-specific allocation or constructing a complete group worksheet.',disposition='Retain scope and unresolved allocation. Heading wraps awkwardly at ex-change and the page has large lower whitespace, but text is legible; optional typography refinement after full diagnosis, not a substantive accounting correction.'),
        dict(pages=[267,268],finding='The Part II divider visibly shifts from worked models to product/implementation design. Chapter27 motivates unobserved activities behind reported aggregates, then distinguishes evidence-backed history, compatible states and conditional simulations before proposing the typed language.',disposition='The renewed borrowing example repeats an earlier case but serves a new implementation-purpose transition. Do not treat repeated explanation as an automatic defect. Divider is intentional; no clipping.'),
        dict(pages=[268,269],finding='The borrowing journal records principal100 and interest5 under either debt type. Equation27.1 defines alpha as fixed share and produces7-2alpha; the following paragraph explicitly reconciles Chapter1 floating-share notation by complementing the coordinate. Feasible ranges are separated from probability laws.',disposition='Exact equation and complementary-coordinate identities checked at endpoints and midpoint, with general linear algebra explicit. The previous-page assumptions supply full-year rates/no fees/no default. No hidden probability or empirical calibration is introduced.'),
        dict(pages=[269,270],finding='The intended users and full workflow make traceability and later revision comparison concrete. The requirements table preserves source context, distinct clocks, joint ambiguity, balanced journals, economics, conditional results and reproducibility. The paragraph treats Python/storage/parser choices separately from acceptance requirements.',disposition='Retain separation of design acceptance, software delivery and forecast validation. Dense table is legible. Initial nonfinancial scope is framed as implementation staging, with bank/insurer representability required from the outset; compare later sector claims before final acceptance.')],
    equations_reviewed=['27.1: supplied annual interest as a function of fixed debt share'],
    equation_judgments=[dict(label='27.1',role='exact local model relation',domain='0<=alpha<=1; debt100 currency units; annual fixed5%/floating7%',
        interpretation='Increasing fixed share reduces scenario interest from7 to5.',
        source='Supplied debt example; no imported empirical result',timing='One complete following year under immediate reset',
        transition='Equal historical journals motivate latent contract state and a feasible range rather than a probability distribution.',
        verdict='correct under explicit premises; later equation reuse not checked in this segment')],
    arithmetic_artifact='arithmetic-0265-0270.json',source_claims_reviewed=[],
    render_binding='render-bindings-0265-0270.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0265-0270.json').open('x') as stream:
    json.dump(segment,stream,indent=2);stream.write('\n')
print(json.dumps(dict(authored_segment=segment['id'],arithmetic_checks=len(checks),pdf_unchanged=True)))
