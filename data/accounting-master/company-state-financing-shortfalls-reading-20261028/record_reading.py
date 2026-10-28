"""Record full primary draft reading and explicit import vetoes once."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json,subprocess
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;R=ROOT/'docs/design/research/company-state-program-20261028';SID='N-WHITED-SHORTFALLS-20080520'
def rel(p):return str(p.relative_to(ROOT))
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
assert json.loads((H/'convention-attempt-01/verification.json').read_text())['passed']
b=H/'ledgers-before';b.mkdir(exist_ok=False);L={}
for n in ['source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omitted-paper-risk','search-log']:
 p=R/(n+'.json');(b/p.name).write_bytes(p.read_bytes());L[n]=json.loads(p.read_text())
source=dict(id=SID,title='Whited, What Can Cash Shortfalls and Windfalls Tell Us About Finance Constraints?',
 doi='10.1007/978-3-7908-2131-4_1',path=rel(H/'sources/shortfalls-author-20080520.pdf'),sha256=sha(H/'sources/shortfalls-author-20080520.pdf'),
 version='20May2008 author draft; published chapter equivalence unresolved',classification='RETRACTED_OR_QUARANTINED',
 quarantine_reason='Local literal model contradictions and missing empirical-results support; not a retraction finding',
 reading_status='All26 pages, sections1–5, equations1–11, two footnotes, references and five figures read; no appendix',
 visually_inspected_physical_pages=[8,11,12,13,14,19,22,23,24,25,26],
 publication_integrity='Crossref/author title agree; publisher supplies preview only; metadata dates disagree; OpenAlex not retracted28October; bounded correction query no explicit notice',
 allowed_claims='Describe retained draft and exact local mismatch; use research questions as leads only',
 forbidden_claims='Validated primary model, empirical evidence, theorem validity, published-version errors, unrestricted-cash interpretation or default calibration',
 official_code='Not located/audited on inspected author/publication routes',continuation_note=rel(R/'pension-funding-and-identification.md'))
assert not any(x['id']==SID for x in L['source-support']['sources']);L['source-support']['sources'].append(source);dump(H/'source.json',source)
L['citation-venue']['rows'].append(dict(id=SID,citation_count=9,citation_source='OpenAlex W2198095829',access_date='2026-10-28',venue='The Economics of Imperfect Markets, chapter17–32',venue_metric=None,venue_metric_source='Not obtained; not acceptance evidence',note='Published chapter metadata does not establish author-draft equivalence or correctness.'))
for title,anchor,action in [
 ('Rauh2006, Investment and Financing Constraints: Evidence from the Funding of Corporate Pension Plans','sections1–2,4','Read original institutional rule, identification, estimates and response'),
 ('Chava/Roberts, How Does Financing Impact Investment? The Role of Debt Covenants','section1','Inspect covenant threshold and alternative mechanism'),
 ('Erickson/Whited2000, Measurement Error and the Relationship Between Investment and q','sections1,2,4','Read measurement-error theory and evidence'),
 ('Van der Klaauw2002;Heckman/Robb1985;Thistlethwaite/Campbell1960','section2','Read identification/continuity/control-function conditions'),
 ('Stokey/Lucas1989, Recursive Methods in Economic Dynamics, Theorems9.6/9.8','section3','Check cited hypotheses against fixed cost, penalty and stated feasible set'),
 ('Gomes2001;Hennessy/Whited2005,2007;Cooper/Haltiwanger2006','sections3–4','Read numerical method, calibration and real/financial adjustment competitors'),
 ('Rotemberg/Woodford1992,1999;Tauchen1986','section4.1','Check parameter mapping and discretization before reuse'),
 ('Blanchard/Lopez-de-Silanes/Shleifer1994;Lamont1997','section1','Compare other cash-shock settings and identification')]:
 L['backward-snowball']['rows'].append(dict(seed=SID,candidate=title,anchor=anchor,classification='DIRECT_METHOD',action=action,status='lead_not_technical_support'))
for f,order in [('forward-cited.json','cited_by_count:desc'),('forward-recent.json','publication_date:desc')]:
 d=json.loads((H/'sources'/f).read_text())
 for x in d['results']:L['forward-snowball']['rows'].append(dict(seed=SID,source_file=rel(H/'sources'/f),query_date='2026-10-28',query_order=order,matched_population=d['meta']['count'],title=x['title'],openalex_id=x['id'],doi=x.get('doi'),date=x.get('publication_date'),citation_count=x.get('cited_by_count'),classification='COMPETITOR',screening_level='Metadata only; overlapping queries',disposition='Inspect primary text before use'))
L['forward-snowball']['rows'].append(dict(seed=SID,title='Threshold Events and Identification: A Study of Cash Shortfalls',doi='10.1111/j.1540-6261.2012.01742.x',source_file=rel(H/'sources/correction-crossref.json'),classification='DIRECT_METHOD',screening_level='Related title; exact version/successor relation not established',disposition='Read published primary and compare; do not inherit draft claims'))
for ident,claim,anchor in [
 ('SHORTFALLS-LIMIT-SIGN','The printed right-minus-left contrast equals minus alpha under its w=1[s<=0].','physical8;convention-attempt-01'),
 ('SHORTFALLS-REWARD','Equation9 reward omits D from equation8 e=G-D under unchanged definitions.','physical12;convention-attempt-01'),
 ('SHORTFALLS-LABOR','The printed labor exponent-.525 contradicts assumed positive marginal product and negative own curvature.','physical11/13;convention-attempt-01'),
 ('SHORTFALLS-EMPIRICAL-GAP','The full retained draft contains no empirical sample/estimation section supporting its real-firm conclusion.','physical7 roadmap;18–19 conclusion;full26-page inventory'),
 ('SHORTFALLS-CONDITIONAL-NORMALITY','Conditional normality alone does not imply linear conditional mean; N(s squared,1) is a counterexample.','physical9;local definition'),
 ('SHORTFALLS-CASH-POPULATION','Figure5 caption calls the cash-panel quantity pension assets; unrestricted cash is not established.','physical26;section3')]:
 L['claim-support']['rows'].append(dict(id=ident,source_id=SID,claim=claim,anchor=anchor,limits='Diagnostic of retained draft; quarantined from model/empirical support; no published-version or author-code verdict',support_class='PROJECT_DERIVATION'))
for ident,candidate,reason,action in [
 ('OR-SHORTFALLS-PUBLISHED','Published chapter and official code','Author draft has material contradictions; publisher returns subscription preview','Obtain public legitimate technical version/code; retain draft quarantine'),
 ('OR-SHORTFALLS-PRIMARY','Rauh2006;later threshold paper;What Gives? studies','Disputed empirical interpretation requires both original and later methods/results','Inspect data, identification, uncertainty and mechanisms before use'),
 ('OR-SHORTFALLS-THEOREMS','Stokey/Lucas cited existence/unique-policy results','Fixed costs/threshold and calibration conflicts prevent unexamined theorem transfer','Inspect source hypotheses and feasible-set conditions')]:
 L['omitted-paper-risk']['rows'].append(dict(id=ident,candidate=candidate,reason=reason,disposition=action,task='S06/S02',acceptable_for_final_survey=False))
L['search-log']['rows'].append(dict(date='2026-10-28',task='S06/S02',queries=['Whited shortfalls title/correction','OpenAlex chapter/top5/recent5','author accepted-papers and linked PDF','Debt Dynamics author/JSTOR/SSRN'],outcome='26-page primary draft obtained; publisher200 is HTML preview; corrections query has no explicit notice in5 results; Debt JSTOR challenge and trusted SSRN403. Guessed.org failed; retained canonical.com succeeds.',evidence=rel(H/'query-log.json')))
for n,d in L.items():dump(R/(n+'.json'),d)
dump(H/'query-log.json',dict(date='2026-10-28',source_routes=['https://www.toniwhited.com/accepted-papers','https://www.toniwhited.com/s/shortfalls.pdf','https://link.springer.com/content/pdf/10.1007/978-3-7908-2131-4_1.pdf'],outcomes=['Author page/PDF200','Publisher200 HTML subscription preview, no PDF','Debt JSTOR200 client challenge','Debt SSRN DNS then trusted403','Initial guessed whited.org DNS failure normally/trusted; corrected from canonical stored page'],scope='Bounded discovery and metadata; no control bypass or absence claim',files=[dict(path=rel(p),sha256=sha(p)) for p in (H/'sources').iterdir() if p.is_file()]))
p=ROOT/'data/accounting-master/unified-program-20261028/program.json';d=json.loads(p.read_text());old=deepcopy(d);dump(H/'program-before.json',old)
for t in d['tasks']:
 if t['id'] in ['S06','S02']:
  assert t['status']=='in_progress';t['evidence'].extend([rel(H/'result.md'),source['continuation_note']])
  t['remaining'].append('Whited20May2008 literal draft quarantined after source audit; published/code and original/related threshold study comparison required')
  if t['id']=='S06':t['next_action']='Continue direct primary cash/debt and maturity models, Rauh and related threshold study; preserve retained draft equation-import vetoes until published/code comparison resolves them.'
for a,b in zip(old['tasks'],d['tasks']):
 for k in ['id','status','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
dump(p,d)
entry='''
## Primary financing draft reviewed — 28 October2026

The26-page Whited20May2008 pension-shortfalls draft is fully read.15 exact
checks confirm literal treatment-sign, reward and labor-calibration mismatches;
its real-firm conclusion lacks the corresponding empirical section. This
version is quarantined from model/empirical import. Published/code comparison
and Rauh/related threshold work remain open. Source denial does not halt
other ready work. Result: company-state-financing-shortfalls-reading-20261028/result.md
under data/accounting-master. All six survey ledgers retain the findings.

S06/S02 remain in_progress. The40-task criteria/dependencies and original
acceptance/failure populations persist. Main reading300/831; resume301.
Releases remain not_ready; E3 deferred. Continue independent ready work.

'''
for n in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
for n,k in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
 p=ROOT/n;d=json.loads(p.read_text());d[k]['shortfalls_primary_review_20261028']=dict(result=rel(H/'result.md'),checks=15,model_import='quarantined',program_complete=False);dump(p,d)
files=[p for p in H.rglob('*') if p.is_file() and 'ledgers-before' not in p.parts and p.name!='manifest.json']
dump(H/'manifest.json',dict(date='2026-10-28',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),plan='docs/plans/company-state-financing-shortfalls-reading-20261028.md',result=rel(H/'result.md'),cpu_gpu='CPU-only document and Fraction; no GPU import',seeds='N/A deterministic',wall_time='Interactive reading; no runtime claim',files=[dict(path=rel(p),sha256=sha(p)) for p in files]+[dict(path=source['continuation_note'],sha256=sha(ROOT/source['continuation_note']))]))
print(json.dumps(dict(read_pages=26,exact_checks=15,model_import='quarantined',task_statuses_preserved=True)))

