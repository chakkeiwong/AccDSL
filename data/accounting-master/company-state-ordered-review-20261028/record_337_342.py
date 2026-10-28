"""Record actual individual-page reading of337–342, without source promotion."""
from datetime import datetime
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
prior=json.loads((D/'main-0331-0336.json').read_text());I=D/prior['inventory'];j=json.loads(I.read_text());v=next(x for x in j['volumes'] if x['name']==prior['volume'])
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
checks=[]
def c(n,a,b):checks.append(dict(name=n,passed=a==b,actual=str(a),expected=str(b)))
hours=Q(int((datetime(2027,1,6,9)-datetime(2027,1,4,11)).total_seconds()),3600)
c('stated interval hours',hours,46)
c('whole elapsed days',hours//24,1)
c('calendar date days',(datetime(2027,1,6).date()-datetime(2027,1,4).date()).days,2)
c('conditional day-count interest factor',Q(2,365)/Q(1,365),2)
c('two-loan assumed decomposition',60+40,100)
c('different decomposition also reconciles',70+30,100)
c('aggregate does not identify component',60==70,False)
assert all(x['passed'] for x in checks)
doc=fitz.open(ROOT/v['pdf'])
for n in range(337,343):assert sha256(doc[n-1].get_text().encode()).hexdigest()==v['pages'][n-1]['text_sha256']
packet=dict(inventory=prior['inventory'],volume=prior['volume'],pdf_sha256=v['pdf_sha256'],id='main-0337-0342',pages=list(range(337,343)),entry_state=prior['exit_state'],
 exit_state='The survey ends by separating language semantics, contract events, extraction, exact constraints and optional inference from actual accounting admission. The ACTUS46-hour example exposes day-count/version choices; extraction scores retain their supplied-text population. Chapter31 starts with one typed IR shared by human, extractor, library and textual frontends. Borrowing100 may be decomposed into assumed60/40 without reporting those as disclosed facts. The typed schema/SQL/Python baseline remains a serious competitor, and the textual frontend must demonstrate value through common conformance cases. Continue into the concrete architecture after this reversible frontend decision.',
 observations=[
 dict(pages=[337],finding='Language/compiler correctness and contract event semantics do not establish accounting rule correctness. Empty/conflict results differ from evidence branches. The retained ACTUS versions and timestamp conventions are explicitly unresolved;46 elapsed hours give one complete day versus two calendar days.',disposition='The local time arithmetic and factor2 check pass. These are stated retained-edition findings, not newly audited software versions. Contract meaning, valuation and accounting presentation are separated. Dense but readable page; the source path fits. Candidate search bounds remain distinct from completeness.'),
 dict(pages=[338],finding='The extraction discussion separates table detection, structure and text association. TableFormer reported TEDS95.4/90.1/93.6 is scoped to cropped PDF tables with supplied text, while QA and RAG benchmarks do not demand complete conditional company histories.',disposition='Scores are quoted manuscript claims, not recomputed or newly verified against papers in this reading. The actual prose specifies Tables2/4 and supplementary Section2, distinguishes structure-only/content metrics and does not promote scores to accounting accuracy. The recent-competitor wording is frozen historical context; current survey remains incomplete.'),
 dict(pages=[339],finding='Bounded exact arithmetic and optional probabilistic inference solve different questions. Unsupported formulas retain diagnostics; accounting identities are not replaced by likelihood penalties, and sampler completion does not show that all interpretations were explored.',disposition='Two short paragraphs finish this subtopic with ample whitespace. No missing text or clipped content. The statement is a design boundary, not evidence of runtime coverage, sampler validity or a new theorem. Referenced source sections are not newly technically audited.'),
 dict(pages=[340],finding='The literature synthesis identifies the unresolved chain from disclosures through histories, economic events and accounting to reports. It explicitly leaves originality and empirical advantage unestablished and points to comparative acceptance work.',disposition='The brief chapter conclusion supplies the reason architecture follows: connecting contributions without collapsing their distinct meanings. It is not a survey-completion claim or evidence that Chapter40 acceptance has passed. The short page is a deliberate chapter boundary.'),
 dict(pages=[341],finding='Figure31.1 presents evidence, typed history, compatible alternatives, scenario execution and reports in order. Several authoring frontends produce common IR. The borrowing100 example distinguishes an assumed60/40 loan decomposition from a reported disclosure.',disposition='The diagram is legible with visible connectors and caption, and the paragraph gives its concrete epistemic consequence.60+40 and70+30 both equal100, demonstrating aggregate nonidentification without inventing actual loan facts. No numbered mathematical display occurs; the figure is architecture, not a proof of implementation.'),
 dict(pages=[342],finding='Typed schema/SQL/Python is the strongest explicit baseline; the table assigns scoped roles to XBRL, ledgers, graphs, rules, probabilistic programs, spreadsheets and the DSL. Common conformance cases and frontend value, rather than notation alone, motivate the staged choice.',disposition='The eight-row comparison fits one page without clipping and follows the shared-IR diagram. Benefits and costs are stated rather than claiming inherent DSL superiority. The common tests and representative authoring comparison are future acceptance obligations, not established by this reading.')],
 equations_reviewed=['337 inline elapsed-day/calendar-day calculation','341 inline borrowing100 decomposition'],
 equation_judgments=[dict(labels=['337 day count'],role='conditional timing arithmetic under two explicitly different conventions',verdict='Correct46-hour/one-whole-day/two-calendar-day arithmetic and factor2 under common nonzero simple-interest factors. No contract convention or matched ACTUS edition is admitted.'),dict(labels=['341 borrowing100'],role='illustrative aggregate-versus-component distinction',verdict='Correct60+40=100, also70+30=100; aggregate equality does not identify loan components. Not a source fact or completeness statement.')],
 arithmetic_artifact='arithmetic-0337-0342.json',source_claims_reviewed=[],render_binding='render-bindings-0337-0342.json',independent_reader='pending',human_acceptance='pending')
for path,obj in [(D/'arithmetic-0337-0342.json',dict(count=len(checks),checks=checks,scope='Local timing/decomposition arithmetic only; no new paper/source validation')),(D/'main-0337-0342.json',packet),(H/'inventory-before-0342.json',j)]:
 with path.open('x') as fh:json.dump(obj,fh,indent=2);fh.write('\n')
print(json.dumps(dict(segment=packet['id'],arithmetic_checks=len(checks))))
