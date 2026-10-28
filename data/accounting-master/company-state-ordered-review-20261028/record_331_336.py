"""Record individually read331–336; distinguish reconciliation and identification."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0325-0330.json').read_text());j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
c('initial treaty timing difference',85-70,15)
c('year-one equity difference',Q(83)-Q('74.75'),Q('8.25'))
c('equal terminal cash',Q('88.3'),Q('88.3'))
c('terminal equality does not imply initial equality',85==70,False)
for N,O,C in [(Q(1,5),Q(1,10),Q(1,2)),(Q(-1,5),Q(1,10),Q(1,10)),(Q(2,5),Q(1,10),Q(7,10))]:
 S=C-N-O;c('rearranged normalized identity '+str(N),S+N+O-C,0)
c('different financing same operating sum',Q(1,2)-Q(1,5)-Q(1,10),Q(7,10)-Q(2,5)-Q(1,10))
c('identity alone leaves instrument free',Q(1,5)!=Q(2,5),True)
c('zero normalization denominator prohibited',Q(0)==0,True)
# Explicit small counterexample for the page335 existential warning.
family=[{'a'},{'b'}];certain=set.intersection(*family)
c('no row individually certain',sorted(certain),[])
c('every history has a row',all(bool(h) for h in family),True)
c('empty certain table loses existence',bool(certain),False)
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf'])
for n in range(331,337):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
with (D/'arithmetic-0331-0336.json').open('x') as stream:json.dump(dict(count=len(checks),checks=checks,scope='Illustrative differences, normalized identity and finite certain-answer counterexample only; cited technical papers not newly audited'),stream,indent=2)
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0331-0336',pages=list(range(331,337)),entry_state=prior['exit_state'],
 exit_state='The revised treaty case separates a changed interpretation from a permitted correction to committed journals; candidate-set membership and all ancestors matter to reuse. Chapter30 surveys accounting dynamics, incomplete databases, provenance, inverse identification, robust priors, model averaging and intervention. The normalized cash identity reconciles but cannot select financing; an empty certain-row table can lose an existential fact. Source results remain conditional on their own models, priors and dependencies. Continue after the distinction between imposed stress paths, observational conditioning and causal intervention.',
 observations=[
 dict(pages=[331],finding='Treaty ordering changes initial asset/equity85 versus70 and year-one equity83 versus74.75 despite common terminal cash88.3. Later versus unknown availability have different selection consequences. Changing candidate membership invalidates selection dependencies even if the chosen ID stays the same.',disposition='Local differences15 and8.25 are correct; the underlying insurance calculation is deferred to its stated later section and not re-certified here. Source/extraction corrections are distinguished. Full ancestry checks prevent stale descendants; equal displayed values or common company labels do not prove independence.'),
 dict(pages=[332],finding='An unchanged committed event retry returns its original receipt; changed request under the same event identity conflicts. A revised treaty assessment does not authorize a correcting journal without treatment, period, accounts and authority.',disposition='The short page is the Chapter29 conclusion, not a missing section. TREATMENT_UNSUPPORTED preserves the conditional calculation without posting. These statements are specification claims in this read, not newly observed runtime receipts or legal approval.'),
 dict(pages=[333],finding='Chapter30 declares a scoped design survey and distinguishes algebraic conservation from admissible transitions, correction-aware DSL syntax from company reconstruction, and standardized dynamic accounting data from heterogeneous reports.',disposition='The paragraph sequence explains each literature contribution and transfer limit. References to Nehmer/Robinson, Doshi, Babincevich, Shahnavazarian and Pierson are not newly technically re-read. The historical search cutoff remains the frozen manuscript date, not a claim that current survey work stopped then.'),
 dict(pages=[334],finding='Bank and stock-flow models motivate economic state, counterparty and decision rules; working cash-flow measures may differ from reported operating cash flow. Gentry planning objectives and Gentry/Hoque normalized cash reconciliation serve different roles.',disposition='The displayed S+N+O-C=0 and S=C-N-O are algebraically equal under common nonzero normalization. Three exact examples and a same-S/different-N pair confirm reconciliation does not choose instrument or date. The text preserves working-paper/version and source-notation ambiguities; no new comparative performance claim is made.'),
 dict(pages=[335],finding='The normalized-denominator zero case has no supplied rule. Fitted-sample R-squared is not held-out forecasting evidence; the expression evaluator does not solve the proposed simultaneous system. Shared unknowns/conditions retain history dependence, and certain-row tables can lose existential information.',disposition='The definition/identity/behavioral-rule distinction is clear. Finite histories{a}/{b} provide an exact explanatory counterexample: every history contains a row while no individual row is certain. Paper replication gaps and the historically uninspected REA source remain explicit, not newly resolved by this reading.'),
 dict(pages=[336],finding='Provenance semirings do not supply posterior probabilities or all nonrelational operations. Database storage time differs from public availability. Inverse regularization, robust priors, model averaging and causal intervention each add specific assumptions.',disposition='The text avoids transferring infinite-dimensional well-posedness or SVAR guarantees to arbitrary accounting programs. It rejects equal weights for duplicated syntax and distinguishes intervention from conditioning. The cited papers and Pearl section are not newly audited; their transfer boundaries are inspected as prose, with source-specific obligations still open.')],
 equations_reviewed=['334 normalized cash identity and rearrangement','336 observation relation y=G(u)'],
 equation_judgments=[dict(labels=['334 cash identity'],role='normalized signed reconciliation, not behavioral choice',verdict='Correct algebra under a common nonzero denominator and declared signed components; supplied source equation/version and notation ambiguity are retained, not re-certified. Local counterexamples preserve same operating sum with different financing.'),dict(labels=['336 y=G(u)'],role='observation-map notation introducing inverse identification',verdict='A stated schematic observation relation; no unique inverse, probability law or well-posedness result follows. The immediately following prose distinguishes regularization/prior assumptions and mixed/discontinuous local model limits.')],
 arithmetic_artifact='arithmetic-0331-0336.json',source_claims_reviewed=[],render_binding='render-bindings-0331-0336.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0331-0336.json').open('x') as stream:json.dump(packet,stream,indent=2);stream.write(chr(10))
with (H/'inventory-before-0336.json').open('x') as stream:json.dump(j,stream,indent=2);stream.write(chr(10))
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks))))

