"""Record individually rendered pages319–324 and exact joint settlements."""
from hashlib import sha256
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0313-0318.json').read_text());j=json.loads((D/prior['inventory']).read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[];paths=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
c('H1 first-period cash',-2000-1082,-3082)
c('H2 first-period cash',-1000-2082,-3082)
c('independent minima fabricate cash',-2000-2082,-4082)
c('fabricated amount differs',-4082==-3082,False)
for branch,expense,capital in [('H1',2000,1082),('H2',1000,2082)]:
 for timing,e1,c1 in [('both_first',expense,capital),('capital_later',expense,0),('expense_later',0,capital)]:
  first=-e1-c1;second=-(expense-e1)-(capital-c1)
  expected={('H1','both_first'):-3082,('H2','both_first'):-3082,('H1','capital_later'):-2000,('H2','capital_later'):-1000,('H1','expense_later'):-1082,('H2','expense_later'):-2082}[(branch,timing)]
  c(branch+'/'+timing+'/first period',first,expected)
  c(branch+'/'+timing+'/eventual cash',first+second,-3082)
  c(branch+'/'+timing+'/liability settlements',e1+c1+(expense-e1)+(capital-c1),3082)
  paths.append(dict(branch=branch,timing=timing,operating_first=-e1,investing_first=-c1,total_first=first,total_second=second,eventual=-3082,probability=None))
c('all six paths retained',len(paths),6)
c('later Americas profit',167045-89587-9802,67656)
c('supported page offset',165-163,2)
c('wrong target same offset',158-156,2)
c('target difference not offset error',165-158,163-156)
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf'])
for n in range(319,325):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
with (D/'arithmetic-0319-0324.json').open('x') as stream:json.dump(dict(count=len(checks),checks=checks,paths=paths,scope='Displayed conditional settlement/segment/navigation arithmetic only; source facts not newly certified'),stream,indent=2)
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0319-0324',pages=list(range(319,325)),entry_state=prior['exit_state'],
 exit_state='The joint settlement example preserves both branch and payment period despite equal eventual totals. Source-located answers and later comparative detail have named evidence views; unresolved publication or actor clocks stay unresolved. Chapter29 defines immutable assertions with source, context, amount, meaning, timing and review fields, separates semantic mapping from measurement conversion and changing legal/reporting perimeters, and distinguishes document, semantic and simulation coverage. Continue the cross-reference work-list procedure after its four outcomes: resolved, duplicate, unavailable or ambiguous.',
 observations=[
 dict(pages=[319],finding='H1 and H2 settle different operating/investing pairs but each totals-3082; independently combining marginal minima invents-4082. Deferring one payment changes first-period liquidity. Later expense detail and corrected navigation belong to separately named source views.',disposition='Exact six-path checks preserve branch and payment period, with no fabricated opening cash or probability. The two-page JPMorgan print/PDF offsets agree at both targets, so an offset change cannot repair the seven-page target difference. The prose keeps amounts, timing, source facts and as-of knowledge separate.'),
 dict(pages=[320],finding='Chapter28 concludes that a navigation correction can revise selected pages/search coverage without erasing unrelated literal source facts, and a JPMorgan review proposal supplies no Apple constraint or posting permission.',disposition='The short page is the chapter ending, not missing text. The final paragraph connects the implementation appendix while preserving issuer separation; no additional equation or source authority claim is introduced.'),
 dict(pages=[321],finding='Chapter29 moves from the cases to immutable assertions and separate derived records. A complete source-ingestion inventory is weaker than a complete financial model; unresolved note commitments, auditor qualifications and management forecasts retain their meanings.',disposition='The distinction between source coverage and economic completeness follows the preceding partial-answer example. The field table starts at the page bottom and continues with repeated headers on322; no truncation is observed.'),
 dict(pages=[322],finding='Observation fields include context, lexical/numeric amount, proposed meaning, multiple clocks and reliability/review separate from history probability. Qualitative substantially-all does not set fixed fraction1. Concept equivalence, aggregation, reclassification and measurement transformation differ.',disposition='The table continuation is readable. Proposed numerical thresholds remain analyst assumptions. Jurisdiction/basis conversion and tax versus accounting measurements are presented as separate derivations, not dictionary relabelling or new current-rule conclusions.'),
 dict(pages=[323],finding='Economic validity, report period, publication/access and database time remain separate. Historical query views retain corrections/conflicts and require compatible periods/basis/perimeter/units/vintage for quarter derivation. Company ownership, reporting control and exposure boundaries differ.',disposition='Calendar half-open example is explicit; later restatements are not backfilled. The source citation to bitemporal work is retained without new technical re-certification. Specification-language supports is read as design intent, not proof of runtime completion. Consolidation plugs do not become recovered transactions.'),
 dict(pages=[324],finding='Gross events, maturity/reset dates, nonbalance obligations, currency roles, cohorts and strategic choices require more state than net statements. The importer inventories packages/roots before interpretation; document, semantic and simulation denominators stay separate.',disposition='A percentage of acquired source units is not a percentage of financial meaning; semantic inventory itself can be incomplete. The work-list stopping condition names unresolved and resource limits rather than assuming exhaustive closure. Page ends midway through unavailable/ambiguous outcome treatment, carried explicitly into the next entry.')],
 equations_reviewed=['319 joint settlement table and timing variants'],equation_judgments=[dict(labels=['319 settlement table'],role='conditional dated liability cash settlement',verdict='Correct under supplied expense q2000, capital payables1082/2082 and sufficient unrestricted funding; joint pairs total-3082, mixed minima-4082 unsupported. No new profit/equity effects under stated no incremental tax/FX/interest assumption.')],
 arithmetic_artifact='arithmetic-0319-0324.json',source_claims_reviewed=[],render_binding='render-bindings-0319-0324.json',independent_reader='pending',human_acceptance='pending')
with (D/'main-0319-0324.json').open('x') as stream:json.dump(packet,stream,indent=2);stream.write(chr(10))
with (H/'inventory-before-0324.json').open('x') as stream:json.dump(j,stream,indent=2);stream.write(chr(10))
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks))))

